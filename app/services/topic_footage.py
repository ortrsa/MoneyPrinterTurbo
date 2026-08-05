"""
按"每段口播各自的主题"去取素材，并把素材精确铺进该段的时间窗。

默认管线的做法是：把一整条视频的搜索词合成一个池子，下载一堆片段后按
`max_clip_duration` 顺序切开拼满音频时长。结果是画面和当下在讲的那条事实
完全无关——第 3 条讲"声音克隆"，画面却还停在第 1 条的素材上。

这里换一种做法：
1. 先只生成音频，用 whisper 反解出每一段（钩子 / 每条事实 / 结尾）的
   起止时间。时间窗必须来自真实音频，估算的字数时长对不齐。
2. 每一段单独出搜索词、单独下载素材。
3. 每一段的素材只铺在这一段的时间窗里，边界与口播边界对齐。

这样"第 N 条事实"的画面一定落在第 N 条被念出来的那几秒里。
"""

from __future__ import annotations

import os
import random
from dataclasses import dataclass, field

from loguru import logger
from moviepy import AudioFileClip, ColorClip, CompositeVideoClip, VideoFileClip, concatenate_videoclips

from app.models.schema import VideoAspect
from app.services import material
from app.utils import utils

# 单个镜头的目标时长。研究里"Isolate 阶段"用 1-1.5 秒的快切来制造密度，
# 但facts 类视频每条事实本身只有 6-9 秒，切太碎会让观众来不及看清画面在讲什么。
# 3 秒左右是密度和可读性的折中：一条事实通常能分到 2-3 个镜头。
DEFAULT_TARGET_CUT_SECONDS = 3.0

# 低于这个长度的镜头看起来像是"闪了一下"的故障，而不是有意的快切。
MIN_CUT_SECONDS = 1.2

# 每个搜索词最多下载几个候选。取太多会拖慢整集生成，取太少则同一段里
# 容易重复用到同一个素材。
MAX_CLIPS_PER_TERM = 3


@dataclass
class SegmentPlan:
    """一段口播 + 它自己的搜索词 + 它在成片里的时间窗。"""

    index: int
    text: str
    start: float
    end: float
    terms: list[str] = field(default_factory=list)

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)


def plan_cuts(
    window: float,
    target_cut: float = DEFAULT_TARGET_CUT_SECONDS,
    min_cut: float = MIN_CUT_SECONDS,
) -> list[float]:
    """
    把一段时间窗切成若干等长镜头，总长严格等于 ``window``。

    等分而不是"按上限切、剩下的当尾巴"，是为了避免出现不足一秒的碎片镜头
    （这正是之前成片里被指出的问题）。因为是等分，最后一个镜头不会比其他
    镜头短，也就不存在尾巴过短的情况。
    """
    if window <= 0:
        return []
    if window <= min_cut:
        # 窗口本身就很短（例如很短的结尾句），不再细分，整段用一个镜头。
        return [window]

    count = max(1, round(window / target_cut))
    # 等分后若单个镜头短于下限，就减少镜头数，直到满足下限为止。
    while count > 1 and window / count < min_cut:
        count -= 1
    return [window / count] * count


def _fit_clip(clip, video_width: int, video_height: int):
    """把素材缩放/居中到目标分辨率，比例不一致时用黑底补边。"""
    clip_w, clip_h = clip.size
    if clip_w == video_width and clip_h == video_height:
        return clip

    clip_ratio = clip_w / clip_h
    video_ratio = video_width / video_height
    if clip_ratio == video_ratio:
        return clip.resized(new_size=(video_width, video_height))

    if clip_ratio > video_ratio:
        scale_factor = video_width / clip_w
    else:
        scale_factor = video_height / clip_h
    new_width = int(clip_w * scale_factor)
    new_height = int(clip_h * scale_factor)

    background = ColorClip(
        size=(video_width, video_height), color=(0, 0, 0)
    ).with_duration(clip.duration)
    resized = clip.resized(new_size=(new_width, new_height)).with_position("center")
    return CompositeVideoClip([background, resized])


def download_segment_materials(
    plan: SegmentPlan,
    task_id: str,
    video_aspect: VideoAspect = VideoAspect.portrait,
    source: str = "pexels",
    max_clips_per_term: int = MAX_CLIPS_PER_TERM,
    seen_urls: set[str] | None = None,
) -> list[str]:
    """
    只为这一段下载素材，返回本地文件路径列表。

    ``seen_urls`` 由调用方跨段共享：不同段的搜索词经常会命中同一批热门素材
    （例如多条 AI 事实都会搜到同一个"打字的手"），不做全局去重的话，
    同一个画面会在一条视频里重复出现好几次。

    但全局去重不能凌驾于"画面要对得上口播"之上。相邻两段讲的是同一个主体
    时（钩子和第 1 条事实都在讲袋熊），前一段会把该主体的素材取光，后一段
    再去重就只能落到它那两个更宽泛的备用词上——于是"袋熊的肠道"这句话配的
    是一只鹰。宁可两段出现相似的袋熊镜头，也不能配错动物，所以第一个词
    （即该段的主体）不参与去重。
    """
    search_videos = material.search_videos_pexels
    if source == "pixabay":
        search_videos = material.search_videos_pixabay
    elif source == "coverr":
        search_videos = material.search_videos_coverr

    material_directory = utils.task_dir(task_id)
    paths: list[str] = []
    if seen_urls is None:
        seen_urls = set()

    for term_index, term in enumerate(plan.terms):
        primary = term_index == 0
        # minimum_duration 传 1：这里的镜头长度由时间窗决定，短素材同样可用，
        # 按 max_clip_duration 过滤会把很多贴题的短素材白白筛掉。
        items = search_videos(
            search_term=term, minimum_duration=1, video_aspect=video_aspect
        )
        logger.info(f"segment {plan.index}: found {len(items)} clips for '{term}'")
        taken = 0
        for item in items:
            if taken >= max_clips_per_term:
                break
            if item.url in seen_urls and not primary:
                continue
            seen_urls.add(item.url)
            try:
                saved = material.save_video(
                    video_url=item.url, save_dir=material_directory
                )
            except Exception as exc:
                logger.error(f"segment {plan.index}: download failed: {exc}")
                continue
            if saved:
                paths.append(saved)
                taken += 1

    logger.info(f"segment {plan.index}: {len(paths)} clips downloaded")
    return paths


def _build_override_clips(
    plan: SegmentPlan,
    clip_paths: list[str],
    video_width: int,
    video_height: int,
    stack,
) -> list:
    """把"人工指定的本地素材"铺满这一段，作为一个连续镜头而不是多个快切。

    和 `_build_segment_clips` 的两点关键差别，都是因为这里的素材是为这一段
    专门准备的（目前的来源是 AI 生成的补位镜头，见 docs/skill/ai-footage-fill）：

    1. **不切碎**。库存素材要切成 3 秒左右的快切是因为一条素材本身和这句话
       只是"大致相关"，快切能提高信息密度。而专门生成的镜头本来就是照着这
       句话拍的，把一个连续 8 秒镜头切成三段再各自随机取偏移，只会得到同一
       个镜头的三次跳切，看起来像穿帮。
    2. **从第 0 秒开始，不随机取偏移**。这类素材的首帧是先单独画好、单独审过
       的——随机偏移会把这个唯一被审过的画面直接扔掉。
    """
    if plan.duration <= 0 or not clip_paths:
        return []

    share = plan.duration / len(clip_paths)
    built = []
    for path in clip_paths:
        try:
            source = stack.enter_context(VideoFileClip(path))
        except Exception as exc:
            logger.error(f"segment {plan.index}: cannot open override {path}: {exc}")
            continue

        available = source.duration or 0.0
        if available <= 0:
            continue

        if available >= share:
            piece = source.subclipped(0, share)
        else:
            # 素材比时间窗短：整段放慢铺满，而不是留黑或者回头去补库存素材，
            # 后者会让这一段一半是生成画面一半是库存画面，风格直接撕开。
            piece = source.with_speed_scaled(final_duration=share)
        built.append(_fit_clip(piece, video_width, video_height))

    if built:
        logger.info(
            f"segment {plan.index}: using {len(built)} override clip(s), "
            f"continuous, no stock footage downloaded"
        )
    return built


def _build_segment_clips(
    plan: SegmentPlan,
    clip_paths: list[str],
    video_width: int,
    video_height: int,
    stack,
    rng: random.Random,
) -> list:
    """把这一段的时间窗铺满，返回已缩放好的 MoviePy 片段列表。"""
    cuts = plan_cuts(plan.duration)
    if not cuts:
        return []
    if not clip_paths:
        # 该段一个素材都没搜到时用黑底占位。宁可黑屏也不要错位复用别段素材，
        # 否则"画面对得上口播"这个前提就被破坏了。
        logger.warning(f"segment {plan.index}: no materials, using black filler")
        return [ColorClip(size=(video_width, video_height), color=(0, 0, 0)).with_duration(plan.duration)]

    built = []
    # 素材不够镜头数时循环复用，但每次从不同起点截取，避免看起来是同一个画面。
    for cut_index, cut_duration in enumerate(cuts):
        path = clip_paths[cut_index % len(clip_paths)]
        try:
            source = stack.enter_context(VideoFileClip(path))
        except Exception as exc:
            logger.error(f"segment {plan.index}: cannot open {path}: {exc}")
            continue

        available = source.duration or 0.0
        if available <= 0:
            continue

        if available <= cut_duration:
            # 素材比镜头短：整段用掉，再放慢到正好铺满，避免出现黑帧缝隙。
            piece = source.with_speed_scaled(final_duration=cut_duration)
        else:
            max_offset = available - cut_duration
            offset = rng.uniform(0, max_offset) if max_offset > 0 else 0.0
            piece = source.subclipped(offset, offset + cut_duration)

        built.append(_fit_clip(piece, video_width, video_height))

    return built


def build_synced_footage(
    plans: list[SegmentPlan],
    audio_file: str,
    output_path: str,
    task_id: str,
    video_aspect: VideoAspect = VideoAspect.portrait,
    source: str = "pexels",
    threads: int = 2,
    seed: int | None = None,
    clip_overrides: dict[int, list[str]] | None = None,
) -> str:
    """
    按段取材并合成底片（含旁白音轨，不含字幕叠加层）。

    每一段的画面严格落在该段口播的时间窗内，所以"第 N 条事实"讲到时，
    屏幕上就是第 N 条对应的画面。

    ``clip_overrides``：段序号 -> 本地视频路径列表。命中的段完全跳过图库下载，
    直接用给定的文件（见 `_build_override_clips`）。这是给"图库确实没有这个东西"
    的段落留的逃生口——绝种动物、特定年代的场景、物理上不存在的画面——这些段
    再怎么换搜索词也只会返回泛泛的填充素材，或者干脆和旁白自相矛盾。
    整集仍然以图库素材为主，这里只补个别段。
    """
    aspect = VideoAspect(video_aspect)
    video_width, video_height = aspect.to_resolution()
    rng = random.Random(seed)

    from contextlib import ExitStack

    with ExitStack() as stack:
        ordered_clips = []
        # 跨段共享，避免同一个素材在不同事实里重复出现
        seen_urls: set[str] = set()
        overrides = clip_overrides or {}
        for plan in plans:
            override_paths = overrides.get(plan.index)
            if override_paths:
                segment_clips = _build_override_clips(
                    plan,
                    override_paths,
                    video_width=video_width,
                    video_height=video_height,
                    stack=stack,
                )
            else:
                clip_paths = download_segment_materials(
                    plan,
                    task_id=task_id,
                    video_aspect=aspect,
                    source=source,
                    seen_urls=seen_urls,
                )
                segment_clips = _build_segment_clips(
                    plan,
                    clip_paths,
                    video_width=video_width,
                    video_height=video_height,
                    stack=stack,
                    rng=rng,
                )
            logger.info(
                f"segment {plan.index}: {plan.start:.2f}s-{plan.end:.2f}s "
                f"({plan.duration:.2f}s) -> {len(segment_clips)} cuts"
            )
            ordered_clips.extend(segment_clips)

        if not ordered_clips:
            raise RuntimeError("no footage could be built for any segment")

        video = concatenate_videoclips(ordered_clips)
        narration = stack.enter_context(AudioFileClip(audio_file))
        # 画面总长按时间窗铺出来，理论上等于音频长度；这里再夹一次，
        # 防止浮点累积误差导致结尾多出/少掉几帧。
        video = video.subclipped(0, min(video.duration, narration.duration))
        video = video.with_audio(narration)

        out_dir = os.path.dirname(output_path) or "."
        os.makedirs(out_dir, exist_ok=True)
        video.write_videofile(
            output_path,
            fps=30,
            codec="libx264",
            audio_codec="aac",
            threads=threads,
            preset="veryfast",
            logger=None,
            # MoviePy 的临时音频文件默认落在当前工作目录，也就是仓库根目录，
            # 每渲染一集就往仓库里扔一个 TEMP_MPY_*.mp4。显式指定到任务目录，
            # 让中间产物和成片待在一起。
            temp_audiofile=os.path.join(out_dir, "temp-audio.m4a"),
        )

    logger.success(f"synced footage written: {output_path}")
    return output_path
