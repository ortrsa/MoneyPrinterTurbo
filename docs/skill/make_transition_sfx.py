#!/usr/bin/env python3
"""
合成转场音效，因为图库里一个都没有。

频道到 2026-08-07 为止的成片只有一条人声轨，`shorts_growth_guide.md` Rank 4
把"没有任何音效"列为一个便宜的缺口。Pexels 只供图像素材，仓库里的
`resource/songs/` 是三分钟的完整曲子、不是音效，所以这个文件用 numpy 直接
合成，不引入新依赖、也不用去找版权不明的音效包。

合成而不是下载还有一个好处：转场音必须和这个频道的节奏对得上（每条事实
之间约 8 秒切一次），长度和包络可以直接调参，而不是迁就一个现成文件。

用法::

    uv run --with numpy python docs/skill/make_transition_sfx.py

产物写进 `resource/sfx/`，是 git 跟踪的普通素材文件。
"""

from __future__ import annotations

import argparse
import sys
import wave
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SAMPLE_RATE = 44100


def _write_wav(path: Path, samples, sample_rate: int = SAMPLE_RATE) -> None:
    import numpy as np

    path.parent.mkdir(parents=True, exist_ok=True)
    # 留 3dB 余量：音效之后还要和人声、音乐相加，压到满刻度会削顶
    peak = float(np.abs(samples).max()) or 1.0
    scaled = (samples / peak) * 0.707
    pcm = (scaled * 32767).astype("<i2")
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(pcm.tobytes())


def make_whoosh(
    duration: float = 0.45,
    f_start: float = 300.0,
    f_end: float = 5000.0,
    sample_rate: int = SAMPLE_RATE,
    seed: int = 20260807,
):
    """
    扫频白噪声，做成"嗖"的一声转场。

    做法是在频域上给每一帧噪声套一个高斯带通，带通中心频率沿时间从
    `f_start` 扫到 `f_end`，再用重叠相加拼回时域。比在时域上串一堆固定
    截止频率的 ffmpeg 滤波器更可控——ffmpeg 的 `lowpass/bandpass` 的
    截止频率不接受随时间变化的表达式，想扫频得自己切段再拼，反而更绕。

    `f_start > f_end` 合法——扫频公式是指数插值，方向反过来就是下降扫频，
    听感上是完全不同的"落"而不是"起"，用来做变体音色而不是只调时长/音域。

    `seed` 默认固定，所以不传参数时和这个文件历史上生成的 `whoosh.wav`
    逐字节一致；生成变体音效时每个变体传不同的 seed，否则不同 duration/
    频率参数下噪声底噪的相关性会让几个变体听起来像同一个声音的音量差异，
    而不是真正不同的音色。
    """
    import numpy as np

    n = int(duration * sample_rate)
    frame = 1024
    hop = frame // 4
    # 两端各多合成一帧再裁掉。不留这个余量的话，首尾样本只被一两个窗覆盖，
    # 重叠相加的归一化分母极小，除完会把边缘放大成一个尖峰——实测第一帧
    # 直接冲到满幅，听上去就是一声"啪"，正好是转场音最不该有的东西。
    pad = frame
    total = n + 2 * pad
    rng = np.random.default_rng(seed)
    noise = rng.standard_normal(total)

    window = np.hanning(frame)
    out = np.zeros(total + frame)
    norm = np.zeros(total + frame)
    freqs = np.fft.rfftfreq(frame, 1 / sample_rate)

    for start in range(0, total, hop):
        chunk = np.zeros(frame)
        piece = noise[start : start + frame]
        chunk[: len(piece)] = piece
        spectrum = np.fft.rfft(chunk * window)

        # 这一帧在**裁剪后**那段里的位置 → 带通中心频率
        # （指数扫频，听感上才是线性的）
        pos = min(1.0, max(0.0, (start - pad) / max(1, n - 1)))
        centre = f_start * (f_end / f_start) ** pos
        # 带宽跟着中心频率走，保持恒定的音程宽度而不是恒定 Hz 宽度
        width = centre * 0.6
        mask = np.exp(-0.5 * ((freqs - centre) / width) ** 2)

        out[start : start + frame] += np.fft.irfft(spectrum * mask, n=frame) * window
        norm[start : start + frame] += window**2

    out = (out / np.maximum(norm, 1e-9))[pad : pad + n]

    # 包络必须跟着扫频走，不能用"快起快落"。第一版用了 exp(-3.2t)：实测振幅
    # 在 46ms 就冲到峰值，而那时扫频才走到 474Hz，等扫到 5kHz 时音量只剩个
    # 位数——听感上是一声低闷的"噗"，不是上扬的"嗖"。
    # 改成峰值落在中段的钟形包络，让最响的部分正好对上扫频的中高段。
    # 两端不到 10% 而不是硬切 0，避免边界爆音。
    t = np.linspace(0, 1, n)
    envelope = np.exp(-(((t - 0.45) / 0.28) ** 2))
    return out * envelope


def make_impact(
    duration: float = 0.35, freq: float = 62.0, sample_rate: int = SAMPLE_RATE
):
    """低频"咚"，给需要落点感而不是流动感的转场备用。"""
    import numpy as np

    n = int(duration * sample_rate)
    t = np.arange(n) / sample_rate
    # 音高快速下滑是"击打"听感的来源，固定频率听起来只是一个低音符
    sweep = freq * np.exp(-5.0 * t)
    phase = 2 * np.pi * np.cumsum(sweep) / sample_rate
    body = np.sin(phase) * np.exp(-9.0 * t)
    click = np.random.default_rng(7).standard_normal(n) * np.exp(-120.0 * t) * 0.25
    return body + click


# 转场音效池，2026-08-08 加入——owner 反馈"每次都是同一个声音，听着很假，
# 而且经常和画面对不上"。单一 whoosh.wav 的问题有两层：(1) 每一次转场都是
# 逐字节相同的文件，听多了确实机械；(2) `add_transition_sfx` 把音效整段
# 放在切点*之后*，声音只属于新镜头，不横跨切点，所以听感上是"贴了一个音效"
# 而不是"这一下把上一镜头带进下一镜头"。这里只解决第(1)层——生成一组扫频
# 参数各不相同、其中一条方向相反（下降扫频，听感上是"落"不是"起"）的变体，
# 而不是同一参数抖一下随机数；第(2)层（跨切点摆放）在 `viral.py` 里改。
#
# 每个变体给不同的 seed，否则 duration/频率变了、底噪的随机种子仍然一样，
# 几个"变体"听起来只是同一段噪声的滤波器差异，不是真正不同的音色。
TRANSITION_VARIANTS: dict[str, dict] = {
    "transition_1.wav": dict(duration=0.45, f_start=300.0, f_end=5000.0, seed=20260807),
    "transition_2.wav": dict(duration=0.55, f_start=220.0, f_end=3200.0, seed=20260808),
    "transition_3.wav": dict(duration=0.35, f_start=450.0, f_end=6500.0, seed=20260809),
    "transition_4.wav": dict(duration=0.50, f_start=4200.0, f_end=350.0, seed=20260810),
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=PROJECT_ROOT / "resource" / "sfx")
    parser.add_argument(
        "--variants-dir",
        type=Path,
        default=PROJECT_ROOT / "resource" / "sfx" / "transitions",
        help="转场音效池的输出目录，默认 resource/sfx/transitions/。",
    )
    args = parser.parse_args(argv)

    try:
        import numpy  # noqa: F401
    except ImportError:
        print("needs numpy: uv run --with numpy python docs/skill/make_transition_sfx.py")
        return 1

    made = []
    for name, samples in (
        ("whoosh.wav", make_whoosh()),
        ("impact.wav", make_impact()),
    ):
        path = args.out_dir / name
        _write_wav(path, samples)
        made.append(path)

    for name, params in TRANSITION_VARIANTS.items():
        path = args.variants_dir / name
        _write_wav(path, make_whoosh(**params))
        made.append(path)

    print("wrote:")
    for p in made:
        print(f"  {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
