#!/usr/bin/env python3
"""
拉取 RBT Telegram 机器人自上次检查以来收到的新文本消息，标记为已读，
以 JSON 打印出来供 Routine/会话逐条处理（每条消息 = 一集新话题/新故事线索）。

已读状态存在 `storage/telegram_state.json`（storage/ 整体不进 git，运行时
状态放这里，不是配置，不该进仓库）。核心不变式：**先持久化 offset，
再返回结果** —— 万一后续的生成/渲染中途崩溃，宁可丢一条消息，也不能让
同一条消息被下一次检查重新拿到、重复生成一遍视频。

用法::

    uv run python docs/skill/check_telegram_inbox.py

    # 输出:
    # {"new_messages": [{"update_id": ..., "date": ..., "text": "bats"}, ...]}
    # 空数组说明没有新消息。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests
import toml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATE_FILE = PROJECT_ROOT / "storage" / "telegram_state.json"


def load_state(state_file: Path) -> dict:
    if state_file.is_file():
        return json.loads(state_file.read_text(encoding="utf-8"))
    return {"last_update_id": 0}


def save_state(state_file: Path, state: dict) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")


def load_telegram_config(root: Path) -> tuple[str, str]:
    cfg = toml.load(root / "config.toml")
    telegram = cfg.get("telegram", {})
    token = telegram.get("bot_token", "").strip()
    chat_id = telegram.get("chat_id", "").strip()
    if not token or not chat_id:
        raise RuntimeError("config.toml is missing [telegram] bot_token/chat_id")
    return token, chat_id


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--state-file", type=Path, default=STATE_FILE)
    args = parser.parse_args(argv)

    token, chat_id = load_telegram_config(args.root)
    state = load_state(args.state_file)
    # offset = 已确认到的最大 update_id + 1；Telegram 收到带 offset 的请求后
    # 会把更小的 update_id 标记为已确认，之后不会再返回它们。不传 offset
    # 会每次都拿到全部积压的未确认消息——这正是要避免的重复处理。
    offset = state["last_update_id"] + 1

    resp = requests.get(
        f"https://api.telegram.org/bot{token}/getUpdates",
        params={"offset": offset, "timeout": 0},
        timeout=30,
    )
    data = resp.json()
    if not data.get("ok"):
        print(json.dumps({"error": data}), file=sys.stderr)
        return 1

    updates = data["result"]
    max_id = state["last_update_id"]
    new_messages = []
    for u in updates:
        max_id = max(max_id, u["update_id"])
        msg = u.get("message")
        if not msg:
            continue
        # 只信任配置好的那个 chat_id 发来的消息——万一有别人找到这个 bot
        # 并发消息给它，不能让那条消息也触发一次渲染。
        if str(msg.get("chat", {}).get("id", "")) != str(chat_id):
            continue
        text = (msg.get("text") or "").strip()
        if not text or text.startswith("/"):
            continue
        new_messages.append(
            {"update_id": u["update_id"], "date": msg["date"], "text": text}
        )

    # 先落盘再返回结果：下游哪怕整个崩溃，这批 update_id 也已经确认过了，
    # 不会在下次检查时重新出现。
    state["last_update_id"] = max_id
    save_state(args.state_file, state)

    print(json.dumps({"new_messages": new_messages}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
