# -*- coding: utf-8 -*-
"""文本界面工具：打印、选项、分隔线等。"""
from dataclasses import dataclass
import os
import sys
import time

# 是否启用逐字打印(测试时可关闭)
SLOW_PRINT = os.environ.get("NL_FAST") != "1"
CHAR_DELAY = 0.012
VISUAL_EVENT_HANDLER = None


@dataclass(frozen=True, eq=False)
class Choice:
    """可携带图标与辅助说明的选项；旧字符串选项仍然兼容。"""

    label: str
    asset: tuple[str, str] | None = None
    detail: str = ""
    badge: str = ""
    enabled: bool = True

    def __str__(self):
        return self.label

    def __getattr__(self, name):
        """兼容旧代码对选项直接调用 startswith/split 等字符串方法。"""
        return getattr(self.label, name)

    def __contains__(self, value):
        return value in self.label

    def __len__(self):
        return len(self.label)

    def __getitem__(self, key):
        return self.label[key]

    def __iter__(self):
        return iter(self.label)

    def __format__(self, spec):
        return format(self.label, spec)

    def __add__(self, other):
        return self.label + other

    def __radd__(self, other):
        return other + self.label

    def __eq__(self, other):
        if isinstance(other, Choice):
            return (
                self.label,
                self.asset,
                self.detail,
                self.badge,
                self.enabled,
            ) == (
                other.label,
                other.asset,
                other.detail,
                other.badge,
                other.enabled,
            )
        if isinstance(other, str):
            return self.label == other
        return NotImplemented

    def __hash__(self):
        return hash((self.label, self.asset, self.detail, self.badge, self.enabled))


def as_choice(option):
    return option if isinstance(option, Choice) else Choice(str(option))


def choice_label(option):
    return as_choice(option).label


def choice_text(option):
    choice = as_choice(option)
    suffix = f" [{choice.badge}]" if choice.badge else ""
    detail = f" — {choice.detail}" if choice.detail else ""
    return f"{choice.label}{suffix}{detail}"


def emit_visual_event(event, **payload):
    """向图形界面发送可选的战斗视觉事件；终端模式下静默忽略。"""
    if VISUAL_EVENT_HANDLER is None:
        return
    try:
        VISUAL_EVENT_HANDLER(event, payload)
    except Exception:
        # 视觉增强绝不能影响战斗流程。
        pass


def configure_console():
    """尽可能将 Windows 终端/管道设为 UTF-8，且不因特殊符号崩溃。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


def set_fast_mode(enabled=True):
    """运行时切换逐字打印。"""
    global SLOW_PRINT
    SLOW_PRINT = not enabled


def slow_print(text="", delay=None):
    """逐字打印文本，营造文字游戏氛围。"""
    if not SLOW_PRINT:
        print(text)
        return
    d = CHAR_DELAY if delay is None else delay
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(d)
    sys.stdout.write("\n")
    sys.stdout.flush()


def story(text):
    """打印剧情文本(逐行)。"""
    for line in text.strip("\n").split("\n"):
        slow_print(line.rstrip())


def line(char="─", width=46):
    print(char * width)


def _disp_width(text):
    """按东亚宽度计算显示列数(全角=2)。"""
    import unicodedata
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
               for ch in text)


def banner(text, char="═", width=40):
    """═ 三明治横幅,逐行按全角宽度居中。总宽 40 与 GUI 窗口一致。"""
    line(char, width)
    for row in text.strip("\n").split("\n"):
        pad = max(0, (width - _disp_width(row)) // 2) if row else 0
        slow_print(" " * pad + row)
    line(char, width)


def stat_line(label, cur, mx):
    """统一的 HP/CK 文本行: label + 状态条 + cur/mx。"""
    return f"{label} {bar(cur, mx)} {max(cur, 0)}/{mx}"


def title(text):
    line("═")
    print(f"  {text}")
    line("═")


def pause(msg="(按回车继续)"):
    try:
        input(msg)
    except EOFError:
        pass


def choose(prompt, options, allow_cancel=False):
    """显示选项并返回所选下标(0-based)；allow_cancel 时输入 0 返回 -1。"""
    print()
    if prompt:
        slow_print(prompt)
    w = 2 if len(options) >= 10 else 1
    for i, opt in enumerate(options, 1):
        print(f"  {i:>{w}}. {choice_text(opt)}")
    if allow_cancel:
        print(f"  {0:>{w}}. 返回")
    while True:
        try:
            raw = input("> ").strip()
        except EOFError:
            return -1 if allow_cancel else 0
        if allow_cancel and raw == "0":
            return -1
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return idx
        print("请输入有效编号。")


def bar(current, maximum, width=20, fill="█", empty="░"):
    """绘制状态条。"""
    maximum = max(maximum, 1)
    filled = int(width * max(current, 0) / maximum)
    filled = min(filled, width)
    return fill * filled + empty * (width - filled)
