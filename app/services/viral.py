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

    `condition_on_previous_text=False` 是必须的，不是可选优化：默认值为
    True 时，Whisper 会把已经转录的文本喂回去作为下一段的上下文，遇到某些
    音频（这里是旁白里出现了两次 "hearts"）会诱发重复幻觉——实测中模型在
    第一次识别到 "hearts" 后卡住，把接下来三十秒的音频全部转录成同一个词
    重复几十遍，导致 30 秒的时间轴被压缩成几乎为零，下游对齐把后面几条
    事实全部推到同一个时间点。这不是偶发的音频质量问题，是 Whisper 这个
    参数在特定重复词模式下的已知失败模式；关掉上下文条件后同一段音频转录
    完全正常。
    """
    from faster_whisper import WhisperModel

    logger.info(f"transcribing word timings: model={model_size}, device={device}")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments, _info = model.transcribe(
        audio_file,
        word_timestamps=True,
        vad_filter=True,
        condition_on_previous_text=False,
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


def _counter_events(
    facts: list[FactSegment], total: int, style: str, mode: str = "progress"
) -> list[str]:
    """
    每条事实期间显示计数器。

    `mode="progress"` → `3/6`，表示"看到哪儿了"。
    `mode="countdown"` → `#4`，表示"排名第几"，用于倒数排行榜格式：
    第一条讲的是第 6 名，最后一条才是第 1 名。观众看到 `#2` 就知道
    真正的爆点还没出来，这比进度条更直接地制造"再撑一条"的动机。
    """
    events = []
    for fact in facts:
        if fact.end <= fact.start:
            continue
        if mode == "countdown":
            # fact.index 是 1..N 的口播顺序，倒数榜里它对应的名次是反过来的
            text = f"#{total - fact.index + 1}"
        else:
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
    counter_mode: str = "progress",
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
        events += _counter_events(
            facts, total=len(facts), style="Counter", mode=counter_mode
        )

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


# 旁白必须始终压过音乐。这个值是量出来的，不是猜的：resource/songs 里的曲子
# 实测约 -20.0 LUFS，而成片旁白约 -20.5 LUFS——两者响度几乎相同，所以"凭感觉
# 取个小数"会直接把音乐调没（0.08 换算下来是 -22dB，音乐落到 -42 LUFS 左右，
# 在手机上完全听不见）。0.12 ≈ -18.4dB，让音乐稳定坐在人声下方约 18dB：
# 说话时是垫底的氛围，句子之间的空隙里才浮上来。
#
# 换新曲库时要重新量一次（`ffmpeg -i <file> -af ebur128 -f null -`），
# 这个数字只对当前这批 -20 LUFS 的曲子成立。
DEFAULT_BGM_VOLUME = 0.12

# 结尾留出的淡出时间。硬切到静音会让最后一句 CTA 显得像是视频卡住了。
DEFAULT_BGM_FADE_SECONDS = 2.0


def probe_duration(media_file: str) -> float:
    """读取媒体文件时长（秒）。取不到时返回 0.0，由调用方决定怎么兜底。"""
    ffmpeg = _ffmpeg_executable()
    result = subprocess.run(
        [ffmpeg, "-i", media_file], capture_output=True, text=True
    )
    # ffmpeg 没有 -show_format，时长只能从 stderr 的 "Duration: HH:MM:SS.ss" 里取；
    # 这里不额外依赖 ffprobe，因为 imageio-ffmpeg 只保证带 ffmpeg 二进制。
    for line in (result.stderr or "").splitlines():
        line = line.strip()
        if not line.startswith("Duration:"):
            continue
        stamp = line.split("Duration:", 1)[1].split(",", 1)[0].strip()
        try:
            hours, minutes, seconds = stamp.split(":")
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        except ValueError:
            return 0.0
    return 0.0


def mix_background_music(
    video_in: str,
    video_out: str,
    bgm_file: str,
    volume: float = DEFAULT_BGM_VOLUME,
    fade_seconds: float = DEFAULT_BGM_FADE_SECONDS,
) -> str:
    """
    在成片里垫一层背景音乐，**视频流直接 copy**，只重编码音频。

    放在 `burn_overlay` 之后单独跑一趟，而不是塞进 `build_synced_footage`：
    这一趟不碰视频流，几秒就结束，音量调错了可以从上一步的产物重来，不用
    重新渲染整集。混在渲染里就没有这个退路了。

    `amix` 默认会把各路输入按数量归一化（两路输入各降到一半），那样旁白会
    平白小掉 6dB——所以显式 `normalize=0`，音乐已经在前面按 `volume` 压过了。
    `duration=first` 让成片长度跟着旁白走，音乐长出来的部分直接截掉。
    """
    if not os.path.isfile(bgm_file):
        raise RuntimeError(f"background music file not found: {bgm_file}")

    ffmpeg = _ffmpeg_executable()
    duration = probe_duration(video_in)
    fade_start = max(0.0, duration - fade_seconds)

    bgm_chain = f"volume={volume},afade=t=in:st=0:d=0.8"
    if duration > 0:
        bgm_chain += f",afade=t=out:st={fade_start:.2f}:d={fade_seconds:g}"
    filter_complex = (
        f"[1:a]{bgm_chain}[bg];"
        f"[0:a][bg]amix=inputs=2:duration=first:normalize=0[out]"
    )

    command = [
        ffmpeg,
        "-y",
        "-i", video_in,
        "-i", bgm_file,
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[out]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-loglevel", "error",
        video_out,
    ]
    logger.info(
        f"mixing background music at {volume:g}: {os.path.basename(bgm_file)}"
    )
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        tail = (result.stderr or "").strip().splitlines()[-15:]
        raise RuntimeError("failed to mix background music: " + " | ".join(tail))
    if not os.path.exists(video_out) or os.path.getsize(video_out) == 0:
        raise RuntimeError(f"bgm mix produced no output: {video_out}")
    return video_out


# 转场音效的音量。比音乐高不少——音乐是持续垫底的，而音效是零点几秒的一下，
# 同样的响度感受下瞬态可以放得更响。0.35 实测能听见但不抢词。
DEFAULT_SFX_VOLUME = 0.35


def add_transition_sfx(
    video_in: str,
    video_out: str,
    sfx_file: str,
    timestamps: list[float],
    volume: float = DEFAULT_SFX_VOLUME,
) -> str:
    """
    在给定时间点上叠一层转场音效，视频流 copy，只重编码音频。

    `timestamps` 是每条事实的起点（`fact_timings` 里的 start）。音效落在
    切换的那一刻，用来标记"上一条讲完了"。第 0 秒不放——片头第一帧就"嗖"
    一声，听起来像播放器出错，而不是转场。

    做法是把音效用 `asplit` 复制 N 份，各自 `adelay` 到自己的时间点，再和
    原音轨一起 `amix`。`normalize=0` 的理由和背景音乐那边一样：默认的归一化
    会按输入路数把人声一起压小，路数越多压得越狠，这里有七八路，不关掉的话
    旁白会直接小一半以上。
    """
    if not os.path.isfile(sfx_file):
        raise RuntimeError(f"transition sfx file not found: {sfx_file}")

    # 0 秒和重复的时间点都去掉：前者是片头不是转场，后者会在同一位置叠出
    # 双倍音量的一声
    points = sorted({round(t, 3) for t in timestamps if t > 0.05})
    if not points:
        raise RuntimeError("no usable transition timestamps")

    ffmpeg = _ffmpeg_executable()
    labels = [f"s{i}" for i in range(len(points))]
    parts = [f"[1:a]asplit={len(points)}" + "".join(f"[r{i}]" for i in range(len(points)))]
    for i, (point, label) in enumerate(zip(points, labels)):
        ms = int(point * 1000)
        parts.append(f"[r{i}]volume={volume},adelay={ms}|{ms}[{label}]")
    mix_inputs = "[0:a]" + "".join(f"[{label}]" for label in labels)
    parts.append(
        f"{mix_inputs}amix=inputs={len(points) + 1}:duration=first:normalize=0[out]"
    )
    filter_complex = ";".join(parts)

    command = [
        ffmpeg,
        "-y",
        "-i", video_in,
        "-i", sfx_file,
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[out]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-loglevel", "error",
        video_out,
    ]
    logger.info(
        f"adding {len(points)} transition sfx at {volume:g}: "
        f"{os.path.basename(sfx_file)}"
    )
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        tail = (result.stderr or "").strip().splitlines()[-15:]
        raise RuntimeError("failed to add transition sfx: " + " | ".join(tail))
    if not os.path.exists(video_out) or os.path.getsize(video_out) == 0:
        raise RuntimeError(f"sfx pass produced no output: {video_out}")
    return video_out


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
