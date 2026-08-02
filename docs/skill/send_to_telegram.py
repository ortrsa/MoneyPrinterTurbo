#!/usr/bin/env python3
"""
把渲染完成的一集发到 Telegram：视频本体 + 标题/文案/置顶评论建议，
文案和置顶评论各拆成"标签"和"内容"两条消息，方便在手机上直接长按复制内容
那一条，不用先删掉前面的说明文字。

用法::

    uv run python docs/skill/send_to_telegram.py \
        --result-json storage/tasks/<id>/viral-result.json \
        --pinned-comment "Bet you're never looking at a margarita the same way again 🦇🍹 ..."

    # 或者不依赖 result json，手动传每个字段：
    uv run python docs/skill/send_to_telegram.py \
        --video storage/tasks/<id>/final-viral.mp4 \
        --title "Random But True Facts 10 👀" \
        --caption "..." \
        --hashtags "#batfacts,#animalfacts,#shorts" \
        --pinned-comment "..."

Bot token 和 chat_id 读取 `config.toml` 的 `[telegram]` 段，不接受命令行传入——
token 是敏感信息，不应该出现在 shell 历史或进程列表里。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests
import toml
from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parents[2]

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"

# shorts_growth_guide.md Rank 5: hashtags belong in the description, but only
# a handful — too many there reads as spammy. The full 9-12 tier-formula set
# (Rank 7) belongs in YouTube Studio's separate "Tags" field, not the caption.
CAPTION_HASHTAG_COUNT = 3

# 每个字段先发一条"标签"消息，再发一条"内容"消息——这样在手机上长按复制时,
# 只会选中要复制的正文，不会把 "title:" 这几个字也带进剪贴板。
LABELS = {
    "title": "title:",
    "caption": "caption:",
    "hashtags": "tags:",
    "pinned_comment": "pinned comment:",
}


def load_telegram_config(root: Path) -> tuple[str, str]:
    """从 `config.toml` 的 `[telegram]` 段读 bot_token 和 chat_id。"""
    config_path = root / "config.toml"
    if not config_path.is_file():
        raise RuntimeError(f"{config_path} not found")
    cfg = toml.load(config_path)
    telegram = cfg.get("telegram", {})
    token = telegram.get("bot_token", "").strip()
    chat_id = telegram.get("chat_id", "").strip()
    if not token or not chat_id:
        raise RuntimeError(
            "config.toml is missing [telegram] bot_token/chat_id. "
            "Create a bot via @BotFather, message it once, then read the "
            "chat_id from https://api.telegram.org/bot<token>/getUpdates"
        )
    return token, chat_id


def send_message(token: str, chat_id: str, text: str) -> dict:
    resp = requests.post(
        TELEGRAM_API.format(token=token, method="sendMessage"),
        data={"chat_id": chat_id, "text": text},
        timeout=30,
    )
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"sendMessage failed: {data}")
    return data


def send_video(token: str, chat_id: str, video_path: Path, caption: str = "") -> dict:
    with video_path.open("rb") as f:
        resp = requests.post(
            TELEGRAM_API.format(token=token, method="sendVideo"),
            data={"chat_id": chat_id, "caption": caption},
            files={"video": (video_path.name, f, "video/mp4")},
            timeout=300,
        )
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"sendVideo failed: {data}")
    return data


def send_labelled_field(token: str, chat_id: str, key: str, value: str) -> None:
    """先发标签消息，再发内容消息，两条都要发成功才算这个字段发完。"""
    if not value or not value.strip():
        logger.warning(f"skipping empty field: {key}")
        return
    send_message(token, chat_id, LABELS[key])
    send_message(token, chat_id, value.strip())
    logger.info(f"sent {key} ({len(value)} chars)")


def build_caption_with_hashtags(caption: str, hashtags: list[str]) -> str:
    """
    把 hashtags 接在文案末尾——但只取前 `CAPTION_HASHTAG_COUNT` 个。

    这是 YouTube 描述框的标准写法（SKILL.md 里也是这么说的：标签放描述末尾，
    不放标题），漏了这步等于 hashtags 白生成——上一次人工发送就漏了这个,
    所以这里把它做成脚本的默认行为而不是需要记住的步骤。

    完整的 9-12 个分层标签（post-specific/niche/broad）属于 YouTube Studio
    的 Tags 输入框，不属于描述——描述里塞 12 个 # 号看起来像垃圾信息。
    `hashtags` 列表已经按 tier 顺序排列（post-specific 在前），所以直接取
    前几个就是"当集专属"的标签，不是随手挑的。
    """
    caption = caption.rstrip()
    if not hashtags:
        return caption
    selected = hashtags[:CAPTION_HASHTAG_COUNT]
    tag_line = " ".join(h if h.startswith("#") else f"#{h}" for h in selected)
    return f"{caption}\n\n{tag_line}"


def format_tags_field(hashtags: list[str]) -> str:
    """
    把 hashtags 转成 YouTube "Tags" 输入框要的格式：纯词、逗号分隔、不带 #。

    Studio 的 Tags 字段和描述框里的 #hashtag 是两个不同的东西——Tags 是
    纯文本关键词，本身就不能带 # 号。同一组标签在这里要转成这个格式，
    在描述里保留 # 号（`build_caption_with_hashtags` 那份不变）。
    """
    return ", ".join(h.lstrip("#") for h in hashtags)


def send_upload_kit(
    token: str,
    chat_id: str,
    video: Path,
    title: str,
    caption: str,
    hashtags: list[str],
    pinned_comment: str | None,
) -> None:
    """
    发视频 + 四段各自"标签+内容"的字段。

    hashtags 出现两次，这是有意的，不是重复劳动：一次接在 caption 末尾
    （只取前 `CAPTION_HASHTAG_COUNT` 个，YouTube 描述框不适合塞满全部标签），
    一次是完整的 9-12 个，单独一条方便直接复制粘贴进 YouTube Studio 的
    Tags 输入框。只接在 caption 里、不单独发，第一次上线时就被指出漏了这个。
    """
    send_video(token, chat_id, video)
    send_labelled_field(token, chat_id, "title", title)
    send_labelled_field(
        token, chat_id, "caption", build_caption_with_hashtags(caption, hashtags)
    )
    send_labelled_field(token, chat_id, "hashtags", format_tags_field(hashtags))
    send_labelled_field(token, chat_id, "pinned_comment", pinned_comment or "")


def send_episode(
    result: dict,
    root: Path = PROJECT_ROOT,
    pinned_comment: str | None = None,
    video_path: Path | None = None,
) -> None:
    """
    供 viral_episode.py / story_episode.py 在渲染成功后直接调用（同进程内，
    不用再走一次 subprocess）。`result` 就是它们自己已经在内存里的那个
    result 字典，和写进 viral-result.json / story-result.json 的是同一份。

    发送失败只记警告，不抛异常——Telegram 投递是渲染之外的附加步骤，
    不应该让一次网络故障把一集已经渲染好的视频标记成失败。
    """
    try:
        token, chat_id = load_telegram_config(root)
    except RuntimeError as e:
        logger.warning(f"skipping Telegram delivery: {e}")
        return

    video = video_path or Path(result["video_file"])
    metadata = result.get("metadata", {})
    try:
        logger.info(f"sending video to Telegram: {video}")
        send_upload_kit(
            token,
            chat_id,
            video,
            title=metadata.get("title", ""),
            caption=metadata.get("caption", ""),
            hashtags=metadata.get("hashtags", []),
            pinned_comment=pinned_comment,
        )
        logger.success("upload kit delivered to Telegram")
    except Exception as e:
        logger.warning(f"Telegram delivery failed, video is still saved locally: {e}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--result-json",
        type=Path,
        default=None,
        help=(
            "viral_episode.py / story_episode.py 产出的 viral-result.json 或 "
            "story-result.json。提供它就自动取 video_file / metadata.title / "
            "metadata.caption / metadata.hashtags，--video/--title/--caption/"
            "--hashtags 只用来覆盖其中某一项。"
        ),
    )
    parser.add_argument("--video", type=Path, default=None)
    parser.add_argument("--title", default=None)
    parser.add_argument("--caption", default=None)
    parser.add_argument(
        "--hashtags",
        default=None,
        help="逗号分隔，例如 '#batfacts,#animalfacts,#shorts'",
    )
    parser.add_argument(
        "--pinned-comment",
        default=None,
        help=(
            "发布后建议置顶的评论文案。流水线目前不会自动生成这个字段——"
            "写好当集专属的一句（SKILL.md 第 10 条），手动传入。不传就跳过。"
        ),
    )
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args(argv)

    video_path = args.video
    title = args.title
    caption = args.caption
    hashtags: list[str] = (
        [h.strip() for h in args.hashtags.split(",") if h.strip()]
        if args.hashtags
        else []
    )

    if args.result_json:
        result = json.loads(args.result_json.read_text(encoding="utf-8"))
        video_path = video_path or Path(result["video_file"])
        metadata = result.get("metadata", {})
        title = title or metadata.get("title")
        caption = caption or metadata.get("caption")
        if not hashtags:
            hashtags = metadata.get("hashtags", [])

    if not video_path or not video_path.is_file():
        parser.error(f"video file not found: {video_path}")
    if not title:
        parser.error("no title (pass --title or --result-json)")
    if not caption:
        parser.error("no caption (pass --caption or --result-json)")

    token, chat_id = load_telegram_config(args.root)

    logger.info(f"sending video: {video_path}")
    send_upload_kit(
        token,
        chat_id,
        video_path,
        title=title,
        caption=caption,
        hashtags=hashtags,
        pinned_comment=args.pinned_comment,
    )

    logger.success("upload kit delivered to Telegram")
    return 0


if __name__ == "__main__":
    sys.exit(main())
