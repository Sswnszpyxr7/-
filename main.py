# -*- coding: utf-8 -*-
"""《九命一系:鸣人重生录》统一启动入口。

默认启动 GUI；使用 ``python main.py --cli`` 进入终端版。
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from systems import ui
from systems.runtime import chapter_hint, run_game, title_screen
from systems.state import GameState
from systems.validation import DataValidationError, validate_game_state

__all__ = ["chapter_hint", "title_screen", "run_cli", "run_gui", "cli_main", "main"]


def build_parser():
    parser = argparse.ArgumentParser(description="九命一系：鸣人重生录")
    parser.add_argument("--cli", action="store_true", help="使用终端界面")
    parser.add_argument("--fast", action="store_true", help="关闭终端逐字打印")
    parser.add_argument("--validate-data", action="store_true", help="校验数据后退出")
    return parser


def run_cli(fast=False):
    ui.configure_console()
    if fast:
        ui.set_fast_mode(True)
    return run_game(handle_keyboard_interrupt=True)


def run_gui():
    from gui import NineLivesGUI, enable_hidpi

    enable_hidpi()
    try:
        app = NineLivesGUI()
    except Exception as exc:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("启动失败", f"无法启动游戏:\n{exc}", parent=root)
        root.destroy()
        return None
    app.run()
    return app.state


def cli_main():
    """安装后的 ``nine-lives-cli`` 命令入口。"""
    return main(["--cli"])


def main(argv=None):
    ui.configure_console()
    args = build_parser().parse_args(argv)
    if args.validate_data:
        try:
            warnings = validate_game_state(GameState())
        except DataValidationError as exc:
            print(f"数据校验失败:\n{exc}", file=sys.stderr)
            return 1
        for warning in warnings:
            print(f"警告: {warning}")
        print("数据校验通过。")
        return 0
    if args.cli:
        run_cli(args.fast)
    else:
        run_gui()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
