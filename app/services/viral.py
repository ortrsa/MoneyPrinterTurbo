"""
短视频"病毒式"叠加层：卡拉OK 逐词高亮字幕、事实计数器和进度条。

设计取舍
--------
1. 字幕通过生成 ASS 文件、再由 ffmpeg/libass 一次性烧录，而不是像
   `video.py` 那样为每段文字创建 MoviePy `TextClip`。原因是逐词高亮需要
   在同一行内使用多种颜色，MoviePy 的 `TextClip` 只支持整段单色；用 ASS
   的 `\\1c` 内联覆盖既能做到，也不需要在 Python 侧逐帧渲染上百个片段。
2. 每个词生成一条 Dialogue：文本是整个词块，但只有当前词被染色。相邻
   Dialogue 的时间区间不重叠，所以任意时刻画面上只有一行字幕、一个高亮词。
3. 进度条用 ASS 绘图模式（`\\p1`）画矩形，再用 `\\t` 动画化 `\\clip` 做
   平滑填充，全片只需一条 Dialogue，避免生成成百上千条 tick 事件。

这套叠加层是"后处理"：先让既有流水线产出成片，再把 ASS 烧上去。这样
不需要改动 `video.py` 的合成逻辑，失败时也只影响叠加层而非整个任务。
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass

from loguru import logger

# 研究结论：高亮略微提前于发声更跟得上阅读节奏（读比听快）。
DEFAULT_LEAD_SECONDS = 0.06
# 每屏词数。字幕研究给出的舒适阅读速度上限约 160-200 WPM，短视频里
# 每屏 3 个词配合逐词高亮可以在不超过该上限的前提下保持"跳动"观感。
DEFAULT_WORDS_PER_CAPTION = 3


@dataclass
class WordTiming:
    """一个词及其在音频中的起止时间（秒）。"""

    word: str
    start: float
    end: float


@dataclass
class FactSegment:
    """一条事实在成片中的时间区间，用于计数器与进度条。"""

    index: int
    start: float
    end: float


def transcribe_word_timings(
    audio_file: str,
    model_size: str = "base.en",
    device: str = "cpu",
    compute_type: str = "int8",
) -> list[WordTiming]:
    """
    用 faster-whisper 取逐词时间轴。

    项目使用的 Gemini / OpenAI 这类 TTS 不返回词边界，而 Edge TTS 的
    WordBoundary 依赖 WebSocket，在受限网络里不可用。因此这里统一从生成好的
    音频里反解时间轴：脚本内容我们本来就知道，只缺时间。

    `base.en` 在 CPU 上对几十秒的英文旁白只需几秒，精度足够做字幕对齐；
    需要更高精度时可传入更大的模型。
    """
    from faster_whisper import WhisperModel

    logger.info(f"transcribing word timings: model={model_size}, device={device}")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments, _info = model.transcribe(
        audio_file, word_timestamps=True, vad_filter=True
    )

    words: list[WordTiming] = []
    for segment in segments:
        for word in segment.words or []:
            text = _clean_whisper_word(word.word)
            if not text:
                continue
            words.append(WordTiming(word=text, start=float(word.start), end=float(word.end)))

    logger.info(f"word timings: {len(words)} words")
    return words


# Whisper 会把非语音内容写成 `[Music]`、`[BLANK_AUDIO]` 这类标注，偶尔还会在
# 正常词后面粘上 `…]` 之类的残缺括号。这些内容一旦进入字幕就会直接显示在画面上
# （例如 "These…] six bizarre"），因此在进入时间轴前先清掉。
_ANNOTATION_CHARS = "[]()<>♪…"


def _clean_whisper_word(raw: str) -> str:
    """去掉 Whisper 的非语音标注残留，返回可安全显示的词；整词是标注时返回空串。"""
    text = (raw or "").strip()
    if not text:
        return ""
    # 整词就是一条标注（`[Music]`、`(laughs)`）时直接丢弃
    if text.startswith(("[", "(")) and text.endswith(("]", ")")):
        return ""
    cleaned = text.strip(_ANNOTATION_CHARS).strip()
    # 清理后只剩标点说明这个 token 没有实际内容
    if not any(ch.isalnum() for ch in cleaned):
        return ""
    return cleaned


def align_script_to_words(
    script_text: str, words: list[WordTiming]
) -> list[WordTiming]:
    """
    用脚本原文替换 Whisper 的转写文本，只保留 Whisper 的时间信息。

    字幕显示的文字必须来自我们自己写的脚本，而不是语音识别结果：脚本是权威
    文本，Whisper 只是用来"找时间"的。这样可以同时消除三类问题：
    1. 非语音标注残留（`These…]`）；
    2. 识别错误导致画面上出现错字；
    3. 数字/缩写写法不一致（脚本 "seventy-five"，识别成 "75"）。

    对齐不上的脚本词按相邻锚点线性插值，保证每个词都有时间且顺序单调。
    """
    import difflib

    display_tokens = [token for token in (script_text or "").split() if token.strip()]
    if not display_tokens or not words:
        return words

    script_norm = [_normalize_token(t) for t in display_tokens]
    whisper_norm = [_normalize_token(w.word) for w in words]

    matcher = difflib.SequenceMatcher(a=script_norm, b=whisper_norm, autojunk=False)
    matched: dict[int, int] = {}  # 脚本词索引 -> whisper 词索引
    for a_start, b_start, size in matcher.get_matching_blocks():
        for offset in range(size):
            matched[a_start + offset] = b_start + offset

    aligned: list[WordTiming] = []
    for i, token in enumerate(display_tokens):
        if i in matched:
            source = words[matched[i]]
            aligned.append(WordTiming(word=token, start=source.start, end=source.end))
        else:
            aligned.append(WordTiming(word=token, start=-1.0, end=-1.0))

    # 为未匹配的词插值：在前后两个已知锚点之间平均分配时间
    total_end = words[-1].end
    gap_start = 0
    while gap_start < len(aligned):
        if aligned[gap_start].start >= 0:
            gap_start += 1
            continue
        gap_end = gap_start
        while gap_end < len(aligned) and aligned[gap_end].start < 0:
            gap_end += 1

        left = aligned[gap_start - 1].end if gap_start > 0 else 0.0
        right = aligned[gap_end].start if gap_end < len(aligned) else total_end
        if right < left:
            right = left
        count = gap_end - gap_start
        step = (right - left) / count if count else 0.0
        for offset in range(count):
            start = left + step * offset
            aligned[gap_start + offset].start = start
            aligned[gap_start + offset].end = start + step
        gap_start = gap_end

    logger.info(
        f"aligned script to audio: {len(aligned)} display words "
        f"({len(matched)} matched, {len(aligned) - len(matched)} interpolated)"
    )
    return aligned


def _normalize_token(text: str) -> str:
    """比对用的归一化：只保留字母数字并转小写。"""
    return "".join(ch for ch in text.lower() if ch.isalnum())


def align_facts_to_words(
    fact_texts: list[str],
    words: list[WordTiming],
    total_duration: float | None = None,
) -> list[FactSegment]:
    """
    把"每条事实的文本"对齐到 Whisper 返回的词序列，得到每条事实的时间区间。

    我们知道脚本原文，缺的只是时间；而 Whisper 的转写与原文可能有个别出入
    （数字写法、连字符、口语化缩写等）。因此这里用 `difflib` 做序列对齐，
    而不是简单按词数切分——后者只要有一处增删就会让后续所有边界整体错位。

    对齐不上的位置回退到按词数比例估算，保证始终能返回可用的区间。
    """
    import difflib

    script_tokens: list[str] = []
    token_owner: list[int] = []  # 每个脚本 token 属于第几条事实
    for index, text in enumerate(fact_texts):
        for raw in text.split():
            token = _normalize_token(raw)
            if token:
                script_tokens.append(token)
                token_owner.append(index)

    whisper_tokens = [_normalize_token(w.word) for w in words]
    duration = total_duration or (words[-1].end if words else 0.0)

    if not script_tokens or not whisper_tokens:
        # 没有可对齐的内容时，均分时间轴，至少让计数器能正常推进
        count = max(1, len(fact_texts))
        return [
            FactSegment(
                index=i + 1,
                start=duration * i / count,
                end=duration * (i + 1) / count,
            )
            for i in range(count)
        ]

    # whisper 词索引 -> 事实序号
    owner_by_whisper: dict[int, int] = {}
    matcher = difflib.SequenceMatcher(a=script_tokens, b=whisper_tokens, autojunk=False)
    for a_start, b_start, size in matcher.get_matching_blocks():
        for offset in range(size):
            owner_by_whisper[b_start + offset] = token_owner[a_start + offset]

    # 未匹配上的词沿用前一个已知归属，避免中间出现空洞
    last_owner = 0
    resolved: list[int] = []
    for i in range(len(whisper_tokens)):
        last_owner = owner_by_whisper.get(i, last_owner)
        resolved.append(last_owner)

    # 必须为每一段输入都返回一个区间，且保持原有顺序：调用方会按位置切片
    # （例如去掉开头的钩子和结尾的收尾语），一旦这里跳过了没匹配上的段落，
    # 后面所有段落都会整体错位，计数器就会少数一条。
    segments: list[FactSegment] = []
    for index in range(len(fact_texts)):
        member_positions = [i for i, owner in enumerate(resolved) if owner == index]
        if member_positions:
            start = words[member_positions[0]].start
            end = words[member_positions[-1]].end
        else:
            # 没有任何词归到这一段：退化成零长度区间，稍后由邻接修正接管
            previous_end = segments[-1].end if segments else 0.0
            start = end = previous_end
        segments.append(FactSegment(index=index + 1, start=start, end=end))

    # 让相邻区间首尾相接，计数器就不会在事实之间闪断
    for i in range(len(segments) - 1):
        segments[i].end = max(segments[i].start, segments[i + 1].start)
    if segments and duration:
        segments[-1].end = max(segments[-1].end, duration)
    return segments


def _ass_time(seconds: float) -> str:
    """秒 -> ASS 时间戳 `H:MM:SS.cc`（厘秒精度）。"""
    seconds = max(0.0, float(seconds))
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:  # 四舍五入进位，避免出现 `.100`
        centis = 0
        secs += 1
        if secs >= 60:
            secs = 0
            minutes += 1
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def _ass_color(hex_color: str) -> str:
    """`#RRGGBB` -> ASS 的 `&HBBGGRR&`（注意 ASS 用 BGR 而非 RGB）。"""
    value = hex_color.lstrip("#")
    if len(value) != 6:
        raise ValueError(f"expected #RRGGBB color, got: {hex_color}")
    r, g, b = value[0:2], value[2:4], value[4:6]
    return f"&H{b}{g}{r}&".upper()


def _escape_ass_text(text: str) -> str:
    """转义 ASS 里有特殊含义的字符，避免正文被当成覆盖标签解析。"""
    return text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")


def group_words_into_captions(
    words: list[WordTiming],
    words_per_caption: int = DEFAULT_WORDS_PER_CAPTION,
    boundaries: list[float] | None = None,
) -> list[list[WordTiming]]:
    """
    把逐词时间轴切成每屏若干词的块。

    `boundaries` 是"硬切点"（通常是每条事实的开始时间）。跨越切点的词不会
    被分到同一块里，否则一屏字幕会同时出现上一条和下一条事实的内容。
    """
    words_per_caption = max(1, int(words_per_caption))
    boundaries = sorted(boundaries or [])

    def boundary_index(t: float) -> int:
        # 该时间点落在第几个事实区间，用于判断是否需要断块
        index = 0
        for i, boundary in enumerate(boundaries):
            if t >= boundary - 1e-6:
                index = i
        return index

    chunks: list[list[WordTiming]] = []
    current: list[WordTiming] = []
    current_segment: int | None = None

    for word in words:
        segment = boundary_index(word.start) if boundaries else 0
        if current and (len(current) >= words_per_caption or segment != current_segment):
            chunks.append(current)
            current = []
        if not current:
            current_segment = segment
        current.append(word)

    if current:
        chunks.append(current)
    return chunks


def _caption_events(
    chunks: list[list[WordTiming]],
    style: str,
    highlight_color: str,
    lead_seconds: float,
    total_duration: float,
) -> list[str]:
    """
    为每个词生成一条 Dialogue：整块文字照常显示，仅当前词换色。

    这是"周围词保持白色、当前词高亮"的标准做法。用 `\\1c` 内联覆盖当前词，
    再用 `\\r` 复位回样式默认色，因此不需要为每种配色单独定义样式。
    """
    highlight = _ass_color(highlight_color)
    events: list[str] = []

    for chunk_index, chunk in enumerate(chunks):
        # 每块的首词都会提前 lead_seconds 出现（读字比听字快）。如果上一块
        # 的末词仍按自己的 word.end 收尾，这一提前量就会让两块在同一个
        # \pos 上重叠约 lead_seconds，画面上表现为两行字叠印在一起。
        # 因此把本块的结束时间夹到下一块出现的那一刻：既消除叠字，
        # 也顺带填掉块间静音时的空白闪烁。
        if chunk_index + 1 < len(chunks):
            chunk_limit = max(0.0, chunks[chunk_index + 1][0].start - lead_seconds)
        else:
            chunk_limit = total_duration

        for i, word in enumerate(chunk):
            start = max(0.0, word.start - lead_seconds)
            # 高亮持续到下一个词开始，避免词间静音时字幕闪烁回全白
            if i + 1 < len(chunk):
                end = max(start, chunk[i + 1].start - lead_seconds)
            else:
                end = max(start, min(chunk_limit, total_duration))
            if end <= start:
                continue

            parts = []
            for j, other in enumerate(chunk):
                text = _escape_ass_text(other.word)
                if j == i:
                    parts.append(f"{{\\1c{highlight}}}{text}{{\\r}}")
                else:
                    parts.append(text)
            line = " ".join(parts)
            events.append(
                f"Dialogue: 0,{_ass_time(start)},{_ass_time(end)},{style},,0,0,0,,{line}"
            )
    return events


def _counter_events(facts: list[FactSegment], total: int, style: str) -> list[str]:
    """每条事实期间显示 `3/6` 计数器。"""
    events = []
    for fact in facts:
        if fact.end <= fact.start:
            continue
        text = f"{fact.index}/{total}"
        events.append(
            f"Dialogue: 0,{_ass_time(fact.start)},{_ass_time(fact.end)},{style},,0,0,0,,{text}"
        )
    return events


def _progress_bar_events(
    duration: float,
    video_width: int,
    bar_y: int,
    bar_height: int,
    margin_x: int,
    track_style: str,
    fill_style: str,
) -> list[str]:
    """
    进度条：一条底色轨道 + 一条用 `\\clip` 动画揭示的填充条。

    填充用 `\\t` 把裁剪矩形的右边界从左侧推到右侧，libass 会逐帧插值，
    因此整条进度条只需两条 Dialogue，而不是每隔几帧生成一条事件。
    """
    x1 = margin_x
    x2 = max(margin_x + 1, video_width - margin_x)
    y1 = bar_y
    y2 = bar_y + bar_height
    width = x2 - x1

    # ASS 绘图：以 \pos 为原点画一个矩形
    rect = f"{{\\p1}}m 0 0 l {width} 0 l {width} {bar_height} l 0 {bar_height}{{\\p0}}"
    end = _ass_time(duration)

    track = (
        f"Dialogue: 0,{_ass_time(0)},{end},{track_style},,0,0,0,,"
        f"{{\\pos({x1},{y1})}}{rect}"
    )
    fill = (
        f"Dialogue: 0,{_ass_time(0)},{end},{fill_style},,0,0,0,,"
        f"{{\\pos({x1},{y1})\\clip({x1},{y1},{x1},{y2})"
        f"\\t(0,{int(duration * 1000)},\\clip({x1},{y1},{x2},{y2}))}}{rect}"
    )
    return [track, fill]


def build_ass(
    words: list[WordTiming],
    duration: float,
    video_width: int = 1080,
    video_height: int = 1920,
    facts: list[FactSegment] | None = None,
    font_name: str = "Anton",
    font_size: int | None = None,
    base_color: str = "#FFFFFF",
    highlight_color: str = "#FFE500",
    outline_color: str = "#000000",
    counter_color: str = "#FFFFFF",
    bar_color: str = "#FFE500",
    words_per_caption: int = DEFAULT_WORDS_PER_CAPTION,
    lead_seconds: float = DEFAULT_LEAD_SECONDS,
    caption_y_frac: float = 0.5,
    show_counter: bool = True,
    show_progress_bar: bool = True,
) -> str:
    """
    生成完整 ASS 文件内容。

    `PlayResX/PlayResY` 必须与最终视频分辨率一致，否则 libass 会按比例缩放
    字号、描边和边距，导致字幕大小和位置都不对——这是 ASS 烧录最常见的坑。
    """
    # 字号取画面高度的一个比例：短视频字幕常见区间约为画面高度的 5%-8%
    if font_size is None:
        font_size = int(video_height * 0.062)
    outline = max(2, int(font_size * 0.09))
    shadow = max(0, int(font_size * 0.04))

    counter_size = int(font_size * 0.55)
    margin_x = int(video_width * 0.07)
    bar_height = max(6, int(video_height * 0.006))
    bar_y = int(video_height * 0.055)
    counter_y = bar_y + bar_height + int(counter_size * 0.9)
    caption_y = int(video_height * caption_y_frac)

    styles = [
        # 逐词高亮字幕：\an5 表示以中心点定位，配合 \pos 精确居中
        f"Style: Cap,{font_name},{font_size},{_ass_color(base_color)},{_ass_color(highlight_color)},"
        f"{_ass_color(outline_color)},&H00000000&,-1,0,0,0,100,100,0,0,1,{outline},{shadow},5,"
        f"{margin_x},{margin_x},0,1",
        f"Style: Counter,{font_name},{counter_size},{_ass_color(counter_color)},{_ass_color(counter_color)},"
        f"{_ass_color(outline_color)},&H00000000&,-1,0,0,0,100,100,0,0,1,{max(2, outline // 2)},0,5,"
        f"{margin_x},{margin_x},0,1",
        # 进度条轨道用半透明白（alpha 前缀 A0），填充用不透明高亮色
        f"Style: BarTrack,{font_name},{counter_size},&HA0FFFFFF,&HA0FFFFFF,&HA0FFFFFF,&HA0FFFFFF,"
        f"0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
        f"Style: BarFill,{font_name},{counter_size},{_ass_color(bar_color)},{_ass_color(bar_color)},"
        f"{_ass_color(bar_color)},{_ass_color(bar_color)},0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
    ]

    boundaries = [fact.start for fact in facts] if facts else None
    chunks = group_words_into_captions(
        words, words_per_caption=words_per_caption, boundaries=boundaries
    )

    events: list[str] = []
    if show_progress_bar and duration > 0:
        events += _progress_bar_events(
            duration=duration,
            video_width=video_width,
            bar_y=bar_y,
            bar_height=bar_height,
            margin_x=margin_x,
            track_style="BarTrack",
            fill_style="BarFill",
        )
    if show_counter and facts:
        events += _counter_events(facts, total=len(facts), style="Counter")

    caption_events = _caption_events(
        chunks,
        style="Cap",
        highlight_color=highlight_color,
        lead_seconds=lead_seconds,
        total_duration=duration,
    )
    # 字幕统一用 \pos 居中；写在事件里而不是样式里，方便逐条微调位置
    caption_events = [
        event.replace(",,0,0,0,,", f",,0,0,0,,{{\\pos({video_width // 2},{caption_y})}}", 1)
        for event in caption_events
    ]
    # 计数器同样显式定位到顶部
    events = [
        event.replace(
            ",,0,0,0,,", f",,0,0,0,,{{\\pos({video_width // 2},{counter_y})}}", 1
        )
        if event.startswith("Dialogue") and ",Counter," in event
        else event
        for event in events
    ]
    events += caption_events

    header = "\n".join(
        [
            "[Script Info]",
            "ScriptType: v4.00+",
            f"PlayResX: {video_width}",
            f"PlayResY: {video_height}",
            "WrapStyle: 2",
            "ScaledBorderAndShadow: yes",
            "YCbCr Matrix: TV.709",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
            "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
            "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            *styles,
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        ]
    )
    return header + "\n" + "\n".join(events) + "\n"


def _ffmpeg_executable() -> str:
    """优先使用项目自带的 imageio-ffmpeg 二进制，回退到 PATH 上的 ffmpeg。"""
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        found = shutil.which("ffmpeg")
        if not found:
            raise RuntimeError("ffmpeg not found; install it or add it to PATH")
        return found


def burn_overlay(
    video_in: str,
    ass_file: str,
    video_out: str,
    fonts_dir: str | None = None,
    crf: int = 20,
    # 这是成片的最后一次编码，但 `veryfast` 在同样 CRF 下与 `medium` 的
    # 观感差异对短视频来说可以忽略，编码时间却只有约 40%。
    preset: str = "veryfast",
) -> str:
    """
    把 ASS 叠加层烧进视频。音频直接 `copy`，不重新编码，避免二次损伤。

    `fontsdir` 只是"追加"字体搜索路径，样式里的 `Fontname` 仍必须写字体的
    内部家族名（例如 Anton-Regular.ttf 的家族名是 `Anton`），否则 libass
    会回退到默认字体。
    """
    ffmpeg = _ffmpeg_executable()
    # ffmpeg 的 filter 参数里 `:` 和 `\` 需要转义，Windows 路径尤其容易踩坑
    escaped = ass_file.replace("\\", "/").replace(":", "\\:")
    subtitle_filter = f"ass=filename='{escaped}'"
    if fonts_dir:
        escaped_fonts = fonts_dir.replace("\\", "/").replace(":", "\\:")
        subtitle_filter += f":fontsdir='{escaped_fonts}'"

    command = [
        ffmpeg,
        "-y",
        "-i", video_in,
        "-vf", subtitle_filter,
        "-c:v", "libx264",
        "-crf", str(crf),
        "-preset", preset,
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-loglevel", "error",
        video_out,
    ]
    logger.info(f"burning viral overlay: {os.path.basename(video_out)}")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        tail = (result.stderr or "").strip().splitlines()[-15:]
        raise RuntimeError(
            "failed to burn subtitle overlay: " + " | ".join(tail)
        )
    if not os.path.exists(video_out) or os.path.getsize(video_out) == 0:
        raise RuntimeError(f"overlay burn produced no output: {video_out}")
    return video_out
