# -*- coding: utf-8 -*-
"""《九命一系:鸣人重生录》图形界面外壳 (tkinter,零第三方依赖)。

复用终端版全部游戏逻辑,只替换输入输出层:
  - 游戏跑在工作线程里,stdout 重定向到消息队列 → 左侧剧情窗
  - ui.choose / ui.pause 被替换为"发选项给界面,阻塞等点击"
  - 右侧边栏实时展示 GameState (生命/查克拉/命运点/羁绊/道具等)

运行: python main.py   (或双击 启动图形界面.bat)
"""
import os
import queue
import re
import sys
import threading
import traceback
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk

from systems import (
    collection,
    equipment,
    factions,
    icon_assets,
    loadout,
    new_game_plus,
    party,
    progression_graphs,
    runtime,
    save,
    time_system,
    ui,
    visual_assets,
)
from systems.state import GameState

# ── 配色 ──────────────────────────────────────
BG      = "#14161c"
PANEL   = "#1d2129"
PANEL2  = "#262c38"
FG      = "#e8e2d2"
DIM     = "#8a8fa3"
ACCENT  = "#f79b2e"   # 木叶橙
HP_COL  = "#58c470"
CK_COL  = "#4aa3e8"
EXP_COL = "#d9a441"
BTN_BG  = "#2a303d"
BTN_HOV = "#3a4356"
WARN_COL = "#e05555"
MODAL_BACKDROP = "#0a0c12"
MODAL_CARD = "#1a1f2a"
MODAL_CARD_EDGE = "#3a4254"
MODAL_HEADER = "#222833"
PRIMARY_BTN = "#d8892a"
PRIMARY_BTN_HOV = "#f0a040"
PRIMARY_BTN_FG = "#1a1208"
DANGER_BTN = "#b04040"
DANGER_BTN_HOV = "#d05555"

GRAPH_STATUS_STYLE = {
    "complete": ("#173524", HP_COL, "完成"),
    "current": ("#46321c", ACCENT, "当前"),
    "route_good": ("#19354a", CK_COL, "本档改命"),
    "route_bad": ("#452127", WARN_COL, "本档路线"),
    "collected": ("#352945", "#b48ce8", "已收集"),
    "alternate": ("#252b36", "#626c80", "其他路线"),
    "waiting": ("#443a1c", EXP_COL, "待条件"),
    "love": ("#492437", "#e88cb0", "已定情"),
    "family": ("#292e38", DIM, "家人线"),
    "locked": ("#1a1e26", "#353c49", "未解锁"),
}

# 行首符号 → 剧情窗着色 tag (复用 state.py 的播报符号体系)
SYMBOL_TAGS = {
    "★": "gold", "※": "dim", "◆": "fate", "◇": "fate",
    "▼": "warn", "▲": "warn", "☄": "flux",
    "♥": "love", "❀": "love", "♦": "love", "♣": "green", "⇒": "ally",
}

LOG_FONT   = ("SimSun", 12)            # 等宽中文,状态条/分隔线不会错位
UI_FONT    = ("Microsoft YaHei UI", 10)
UI_BOLD    = ("Microsoft YaHei UI", 10, "bold")
BTN_FONT   = ("Microsoft YaHei UI", 11)
CHOICE_VIEW_HEIGHT = 210              # 固定行动视口，避免剧情页随选项出现/消失跳动
# 与 assets/illustrations、boss_cutins 统一规格 832×208（4:1）对齐，少动资源。
VISUAL_BANNER_HEIGHT = 208
ILLUSTRATION_ASSET_SIZE = (832, 208)

# UI 偏好：字号 / 快速文本 / 剧情滚动（写入存档目录 ui_prefs.json）
UI_PREFS_VERSION = 1
DEFAULT_UI_PREFS = {
    "version": UI_PREFS_VERSION,
    "font_scale": "medium",   # small | medium | large
    "fast_text": False,
    "scroll_speed": "normal",  # slow | normal | fast
    "battle_hud": "detailed",  # compact | detailed
}
FONT_SCALE_PRESETS = {
    "small": {"log": 11, "ui": 9, "btn": 10, "continue": 12, "label": "小"},
    "medium": {"log": 12, "ui": 10, "btn": 11, "continue": 14, "label": "中"},
    "large": {"log": 14, "ui": 12, "btn": 13, "continue": 16, "label": "大"},
}
SCROLL_SPEED_PRESETS = {
    "slow": {"pixels": 1, "label": "慢", "hint": "约 60 像素/秒"},
    "normal": {"pixels": 2, "label": "标准", "hint": "约 125 像素/秒"},
    "fast": {"pixels": 4, "label": "快", "hint": "约 250 像素/秒"},
}
BATTLE_HUD_PRESETS = {
    "compact": {"label": "精简", "hint": "仅生命与意图"},
    "detailed": {"label": "详细", "hint": "破势 / 查克拉 / 状态图标"},
}

# 统一视觉规范：内边距 / 边框 / 字号阶梯（P1 组件语言）
STYLE = {
    "pad_card": (12, 10),
    "pad_section": (10, 8),
    "pad_btn": (14, 8),
    "radius_edge": MODAL_CARD_EDGE,
    "title_size": 13,
    "section_size": 10,
    "caption_size": 8,
}


def _ui_prefs_path():
    return os.path.join(save.SAVE_DIR, "ui_prefs.json")


def load_ui_prefs():
    """从存档目录读取界面偏好；损坏或缺失时回退默认值。"""
    prefs = dict(DEFAULT_UI_PREFS)
    path = _ui_prefs_path()
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, dict):
                if data.get("font_scale") in FONT_SCALE_PRESETS:
                    prefs["font_scale"] = data["font_scale"]
                if isinstance(data.get("fast_text"), bool):
                    prefs["fast_text"] = data["fast_text"]
                if data.get("scroll_speed") in SCROLL_SPEED_PRESETS:
                    prefs["scroll_speed"] = data["scroll_speed"]
                if data.get("battle_hud") in BATTLE_HUD_PRESETS:
                    prefs["battle_hud"] = data["battle_hud"]
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass
    # 冒烟/批处理环境强制快速文本，避免拖慢自动化。
    if os.environ.get("NL_FAST") == "1":
        prefs["fast_text"] = True
    return prefs


def save_ui_prefs(prefs):
    """原子写入界面偏好。"""
    payload = {
        "version": UI_PREFS_VERSION,
        "font_scale": prefs.get("font_scale", "medium"),
        "fast_text": bool(prefs.get("fast_text", False)),
        "scroll_speed": prefs.get("scroll_speed", "normal"),
        "battle_hud": prefs.get("battle_hud", "detailed"),
    }
    if payload["font_scale"] not in FONT_SCALE_PRESETS:
        payload["font_scale"] = "medium"
    if payload["scroll_speed"] not in SCROLL_SPEED_PRESETS:
        payload["scroll_speed"] = "normal"
    if payload["battle_hud"] not in BATTLE_HUD_PRESETS:
        payload["battle_hud"] = "detailed"
    path = _ui_prefs_path()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    temp_path = f"{path}.tmp"
    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
    os.replace(temp_path, path)
    return payload


# ── P1 统一组件工厂 ──────────────────────────

def make_section_header(parent, title, *, bg=PANEL2, accent=ACCENT):
    """卡片内小节标题：左侧强调色竖条 + 标题文字。"""
    row = tk.Frame(parent, bg=bg)
    strip = tk.Frame(row, bg=accent, width=3)
    strip.pack(side="left", fill="y", padx=(0, 8))
    tk.Label(
        row, text=title, font=UI_BOLD, fg=accent, bg=bg, anchor="w",
    ).pack(side="left", fill="x", expand=True)
    return row


def make_card(parent, *, title=None, padx=None, pady=None, fill="x", expand=False):
    """标准内容卡片：深色底板 + 细边框。"""
    if padx is None:
        padx = STYLE["pad_card"][0]
    if pady is None:
        pady = STYLE["pad_card"][1]
    shell = tk.Frame(
        parent, bg=PANEL, highlightthickness=1,
        highlightbackground=STYLE["radius_edge"],
    )
    shell.pack(fill=fill, expand=expand, padx=6, pady=6)
    body = tk.Frame(shell, bg=PANEL, padx=padx, pady=pady)
    body.pack(fill="both", expand=True)
    if title:
        make_section_header(body, title, bg=PANEL).pack(fill="x", pady=(0, 8))
    return body


def make_action_button(parent, text, command, *, style="secondary", font=None, **kwargs):
    """统一按钮：primary / secondary / danger。"""
    if style == "primary":
        bg, hover, fg = PRIMARY_BTN, PRIMARY_BTN_HOV, PRIMARY_BTN_FG
    elif style == "danger":
        bg, hover, fg = DANGER_BTN, DANGER_BTN_HOV, FG
    else:
        bg, hover, fg = BTN_BG, BTN_HOV, FG
    button = tk.Button(
        parent,
        text=text,
        command=command,
        font=font or UI_BOLD,
        bg=bg,
        fg=fg,
        activebackground=hover,
        activeforeground=fg,
        relief="flat",
        cursor="hand2",
        padx=kwargs.pop("padx", STYLE["pad_btn"][0]),
        pady=kwargs.pop("pady", STYLE["pad_btn"][1]),
        **kwargs,
    )
    button.bind("<Enter>", lambda _e, target=button, color=hover: target.config(bg=color))
    button.bind("<Leave>", lambda _e, target=button, color=bg: target.config(bg=color))
    return button


def make_badge(parent, text, *, bg=ACCENT, fg="#1a1208"):
    return tk.Label(
        parent, text=f" {text} ", font=(UI_FONT[0], STYLE["caption_size"], "bold"),
        fg=fg, bg=bg, padx=8, pady=3,
    )


class GuiIO:
    """替代 sys.stdout:把游戏输出送进队列,由界面线程消费。"""

    def __init__(self, q):
        self.q = q

    def write(self, s):
        if s:
            self.q.put(("txt", s))

    def flush(self):
        pass


class GUIClosed(Exception):
    """用户关闭窗口时中断工作线程的正常信号。"""


CLOSE_SIGNAL = object()


class StatBar:
    """边栏里的一根数值条 (Canvas 绘制)。"""

    def __init__(self, parent, row, label, color):
        self.color = color
        tk.Label(parent, text=label, font=UI_FONT, fg=DIM, bg=PANEL,
                 anchor="w").grid(row=row, column=0, sticky="w", padx=(10, 4))
        self.canvas = tk.Canvas(parent, width=130, height=13, bg=PANEL2,
                                highlightthickness=0)
        self.canvas.grid(row=row, column=1, sticky="w", pady=2)
        self.text = tk.Label(parent, text="", font=UI_FONT, fg=FG, bg=PANEL,
                             anchor="w")
        self.text.grid(row=row, column=2, sticky="w", padx=(6, 10))

    def set(self, cur, mx, warn=False):
        mx = max(mx, 1)
        w = int(130 * max(0, min(cur, mx)) / mx)
        self.canvas.delete("all")
        if w > 0:
            color = WARN_COL if warn else self.color
            self.canvas.create_rectangle(0, 0, w, 13, fill=color, width=0)
        self.text.config(text=f"{cur}/{mx}")


class NineLivesGUI:
    def __init__(self):
        self.out_q = queue.Queue()   # 工作线程 → 界面
        self.ans_q = queue.Queue()   # 界面 → 工作线程
        self.waiting = None          # None | "choose" | "pause"
        self._options = []
        self._allow_cancel = False
        self._prompt = ""
        self.ended = False
        self.closed = False
        self._tick = 0
        self._at_line_start = True   # 剧情窗行首状态(用于按符号着色)
        self._cur_tag = None
        self._story_scroll_job = None
        self._original_stdout = sys.stdout
        self._original_choose = ui.choose
        self._original_pause = ui.pause
        self._original_line = ui.line
        self._original_visual_handler = ui.VISUAL_EVENT_HANDLER
        self._io_patched = False
        self._photo_cache = {}
        self._overlay_photos = []
        self._banner_photo = None
        self._portrait_photo = None
        self._current_portrait = None
        self._current_illustration = None
        self._speaker_name = "漩涡鸣人"
        self._last_location = None
        self._battle_visual = None
        self._reaction_token = 0
        self._modal_active = False
        self._modal_backdrop = None
        self._modal_result = None
        self._modal_waiter = None
        self._modal_primary_action = None
        self._modal_cancel_action = None
        self._closing_confirmed = False
        self.continue_panel = None
        self.continue_button = None
        self.settings_button = None
        self.hint_label = None
        self.fast_check = None
        self._settings_open = False
        self._settings_close = None
        self.side_lists = {}
        self.stat_vars = {}
        self.metric_rows = {}
        self.bag_canvas = None
        self.prefs = load_ui_prefs()
        self._apply_runtime_prefs()

        self.state = GameState()
        self._build_window()
        self._apply_font_prefs()
        self._patch_io()

        self.worker = threading.Thread(target=self._run_game, daemon=True)
        self.worker.start()
        if not self.closed:
            self.root.after(15, self._poll)

    # ── 窗口搭建 ──────────────────────────────

    def _build_window(self):
        self.root = tk.Tk()
        self.root.title("九命一系 · 鸣人重生录")
        self.root.geometry("1360x820")
        self.root.minsize(1040, 680)
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # 70/30 响应式双栏：解决宽屏下剧情区无限变宽、右栏仍只有 290px 的问题。
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=7, minsize=680, uniform="main_columns")
        self.root.grid_columnconfigure(1, weight=3, minsize=340, uniform="main_columns")
        left = tk.Frame(self.root, bg=BG)
        left.grid(row=0, column=0, sticky="nsew")
        side = tk.Frame(self.root, bg=PANEL, highlightthickness=1,
                        highlightbackground="#303746")
        side.grid(row=0, column=1, sticky="nsew")

        # 场景横幅 + 当前角色头像。高度与插图资源 832×208 对齐，避免上下黑边。
        self.visual_canvas = tk.Canvas(
            left,
            height=VISUAL_BANNER_HEIGHT,
            bg="#0d1118",
            highlightthickness=1,
            highlightbackground="#343b49",
        )
        self.visual_canvas.pack(fill="x", padx=(14, 10), pady=(14, 0))
        self.visual_canvas.bind("<Configure>", self._on_visual_resize)

        # 行动区紧贴场景，不会被持续刷新的剧情文本挤出首屏。
        act = tk.Frame(left, bg=PANEL, padx=10, pady=8)
        act.pack(fill="x", padx=(14, 10), pady=(8, 8))
        top_row = tk.Frame(act, bg=PANEL)
        top_row.pack(fill="x")
        self.hint_var = tk.StringVar(value="……")
        self.hint_label = tk.Label(
            top_row, textvariable=self.hint_var, font=UI_BOLD,
            fg=ACCENT, bg=PANEL, anchor="w",
        )
        self.hint_label.pack(side="left")
        self.fast_var = tk.BooleanVar(value=bool(self.prefs.get("fast_text")))
        self.fast_check = tk.Checkbutton(
            top_row, text="⚡ 快速文本", variable=self.fast_var,
            command=self._toggle_fast, font=UI_FONT, fg=DIM,
            bg=PANEL, activebackground=PANEL, activeforeground=FG,
            selectcolor=PANEL2,
        )
        self.fast_check.pack(side="right")
        self.settings_button = tk.Button(
            top_row,
            text="⚙ 设置",
            command=self._open_settings,
            font=UI_FONT,
            fg=FG,
            bg=BTN_BG,
            activebackground=BTN_HOV,
            activeforeground=FG,
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=2,
        )
        self.settings_button.pack(side="right", padx=(0, 8))
        self.choice_area = tk.Frame(act, bg=PANEL)
        self.choice_area.pack(fill="x", pady=(6, 0))
        self.choice_canvas = tk.Canvas(
            self.choice_area,
            height=CHOICE_VIEW_HEIGHT,
            bg=PANEL,
            highlightthickness=0,
        )
        self.choice_scroll = tk.Scrollbar(
            self.choice_area,
            orient="vertical",
            command=self.choice_canvas.yview,
        )
        self.choice_canvas.configure(yscrollcommand=self.choice_scroll.set)
        self.choice_canvas.pack(side="left", fill="x", expand=True)
        self.btn_frame = tk.Frame(self.choice_canvas, bg=PANEL)
        self._choice_window = self.choice_canvas.create_window(
            (0, 0), window=self.btn_frame, anchor="nw"
        )
        self.btn_frame.bind(
            "<Configure>",
            lambda _event: self.choice_canvas.configure(
                scrollregion=self.choice_canvas.bbox("all")
            ),
        )
        self.choice_canvas.bind(
            "<Configure>",
            lambda event: self.choice_canvas.itemconfigure(
                self._choice_window, width=event.width
            ),
        )
        self.choice_canvas.bind("<MouseWheel>", self._scroll_choices)
        self.choice_canvas.bind("<Button-4>", self._scroll_choices)
        self.choice_canvas.bind("<Button-5>", self._scroll_choices)
        self.btn_frame.bind("<MouseWheel>", self._scroll_choices)
        self.btn_frame.bind("<Button-4>", self._scroll_choices)
        self.btn_frame.bind("<Button-5>", self._scroll_choices)
        # 焦点在行动区时也能滚（技能卡抢焦点时很关键）。
        self.choice_area.bind("<MouseWheel>", self._scroll_choices)
        self.choice_area.bind("<Button-4>", self._scroll_choices)
        self.choice_area.bind("<Button-5>", self._scroll_choices)

        # 剧情文本窗独立滚动，新消息只影响这一区域。
        txt_frame = tk.Frame(left, bg=BG)
        txt_frame.pack(fill="both", expand=True, padx=(14, 10), pady=(0, 14))
        self.text = tk.Text(txt_frame, wrap="word", font=LOG_FONT, bg=BG,
                            fg=FG, insertbackground=FG, relief="flat",
                            padx=14, pady=10, state="disabled",
                            selectbackground=BTN_HOV)
        sb = tk.Scrollbar(txt_frame, command=self.text.yview,
                          troughcolor=BG, bg=PANEL2)
        self.text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)
        self.text.tag_configure("echo", foreground=ACCENT,
                                font=(LOG_FONT[0], LOG_FONT[1], "bold"))
        for name, col in (("gold", EXP_COL), ("dim", DIM), ("fate", "#b48ce8"),
                          ("warn", WARN_COL), ("flux", "#e07040"),
                          ("love", "#e88cb0"), ("green", HP_COL), ("ally", CK_COL)):
            self.text.tag_configure(name, foreground=col)

        # 键盘: 数字选选项,回车/空格继续；模态层占用 Enter/Esc
        self.root.bind("<Key>", self._on_key)
        self.root.bind("<Escape>", self._on_modal_escape)
        self.root.bind("<Return>", self._on_modal_return)
        self.root.bind("<KP_Enter>", self._on_modal_return)

        self._build_sidebar(side)
        self._set_visual(
            portrait_id="naruto",
            illustration_id=visual_assets.illustration_for_location(self.state.location),
            speaker_name="漩涡鸣人",
        )

    def _load_path_photo(self, path, max_dim=None):
        if not path:
            return None
        path = Path(path)
        key = (str(path), max_dim)
        if key in self._photo_cache:
            return self._photo_cache[key]
        if not path or not path.is_file():
            return None
        try:
            photo = tk.PhotoImage(file=str(path))
            if max_dim:
                factor = max(1, (max(photo.width(), photo.height()) + max_dim - 1) // max_dim)
                if factor > 1:
                    photo = photo.subsample(factor, factor)
        except tk.TclError:
            return None
        self._photo_cache[key] = photo
        return photo

    def _load_photo(self, kind, asset_id):
        path = (
            visual_assets.portrait_path(asset_id)
            if kind == "portrait"
            else visual_assets.illustration_path(asset_id)
        )
        return self._load_path_photo(path)

    def _set_visual(self, portrait_id=None, illustration_id=None, speaker_name=None):
        if portrait_id is not None:
            self._current_portrait = portrait_id
            self._portrait_photo = self._load_photo("portrait", portrait_id)
        if illustration_id is not None:
            self._current_illustration = illustration_id
            self._banner_photo = self._load_photo("illustration", illustration_id)
        if speaker_name:
            self._speaker_name = speaker_name
        self._redraw_visual()

    def _redraw_visual(self):
        if not hasattr(self, "visual_canvas"):
            return
        canvas = self.visual_canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 400)
        # 画布高度与插图资源 832×208 对齐，避免上下黑边。
        height = max(canvas.winfo_height(), VISUAL_BANNER_HEIGHT)
        canvas.create_rectangle(0, 0, width, height, fill="#0d1118", outline="")
        if self._banner_photo:
            # 贴顶水平居中：资源高=画布高时无上下空边。
            canvas.create_image(
                width // 2,
                0,
                anchor="n",
                image=self._banner_photo,
            )
        else:
            canvas.create_text(
                width // 2,
                height // 2,
                text="九命一系 · 鸣人重生录",
                fill=DIM,
                font=(UI_FONT[0], 16, "bold"),
            )
        self._draw_banner_vignette(canvas, width, height)

        # 左侧头像区：高度随 208 横幅收缩，仍容纳 176×176 头像。
        portrait_size = min(176, height - 24)
        portrait_top = 10
        portrait_bottom = portrait_top + portrait_size
        canvas.create_rectangle(0, 0, 220, height, fill="#10141c", outline="")
        canvas.create_rectangle(
            10, portrait_top - 2, 198, portrait_bottom + 2,
            fill="", outline=ACCENT, width=1,
        )
        canvas.create_rectangle(
            12, portrait_top, 196, portrait_bottom,
            fill=PANEL, outline="#2a3140", width=1,
        )
        if self._portrait_photo:
            canvas.create_image(
                104, portrait_top + portrait_size // 2, image=self._portrait_photo,
            )
        else:
            canvas.create_text(
                104, portrait_top + portrait_size // 2 - 6, text="忍", fill=DIM,
                font=(UI_FONT[0], 40, "bold"),
            )
        name_top = portrait_bottom - 32
        canvas.create_rectangle(12, name_top, 196, portrait_bottom, fill="#0e1219", outline="")
        canvas.create_rectangle(12, name_top, 16, portrait_bottom, fill=ACCENT, outline="")
        canvas.create_text(
            104,
            name_top + 16,
            text=self._speaker_name or "旁白",
            fill=FG,
            font=UI_BOLD,
            width=168,
        )
        self._draw_battle_overlay(canvas, width)

    def _draw_banner_vignette(self, canvas, width, height):
        """底部细压暗：资源已贴满高度，只做轻量 UI 融合。"""
        canvas.create_rectangle(0, height - 28, width, height, fill="#0e1118", outline="")
        canvas.create_rectangle(0, height - 12, width, height, fill="#0a0c12", outline="")

    def _draw_battle_overlay(self, canvas, width):
        if not self._battle_visual:
            return
        battle = self._battle_visual
        self._overlay_photos = []
        hud_mode = self.prefs.get("battle_hud", "detailed")
        compact = hud_mode == "compact"
        left, top = 232, 10
        panel_width = min(560, max(280, width - left - 14))
        # 横幅 208 高：收紧 HUD，避免溢出。
        panel_bottom = 108 if compact else 158
        canvas.create_rectangle(
            left,
            top,
            left + panel_width,
            panel_bottom,
            fill="#151922",
            outline=ACCENT if battle.get("boss") else "#596171",
            width=2 if battle.get("boss") else 1,
        )
        title = ("BOSS · " if battle.get("boss") else "") + battle.get("enemy_name", "战斗")
        canvas.create_text(
            left + 12,
            top + 10,
            text=title,
            fill=FG,
            font=UI_BOLD,
            anchor="nw",
        )
        mode_label = BATTLE_HUD_PRESETS.get(hud_mode, BATTLE_HUD_PRESETS["detailed"])["label"]
        canvas.create_text(
            left + panel_width - 10,
            top + 10,
            text=mode_label,
            fill=DIM,
            font=(UI_FONT[0], 7, "bold"),
            anchor="ne",
        )

        hp = battle.get("enemy_hp")
        max_hp = battle.get("enemy_max_hp")
        bar_left, bar_right = left + 12, left + panel_width - 12
        row_y = top + 34
        if hp is not None and max_hp:
            hp = max(0, hp)
            hp_ratio = max(0.0, min(1.0, hp / max_hp))
            canvas.create_text(bar_left, row_y, text="生命", fill=DIM,
                               font=(UI_FONT[0], 8, "bold"), anchor="nw")
            hp_left = bar_left + 34
            canvas.create_rectangle(hp_left, row_y + 1, bar_right, row_y + 13,
                                    fill="#252b36", outline="")
            canvas.create_rectangle(hp_left, row_y + 1,
                                    hp_left + int((bar_right - hp_left) * hp_ratio), row_y + 13,
                                    fill="#f06a5f" if hp_ratio <= 0.25 else "#c94b55", outline="")
            canvas.create_text(bar_right, row_y, text=f"{hp}/{max_hp}", fill=FG,
                               font=(UI_FONT[0], 8, "bold"), anchor="ne")
            row_y += 18

        # 精简模式：只再显示意图文字，跳过破势/查克拉/多图标。
        if compact:
            intent = battle.get("intent")
            if intent:
                intent_name = battle.get("intent_name") or icon_assets.INTENT_NAMES.get(intent, intent)
                canvas.create_text(
                    bar_left, row_y + 4,
                    text=f"意图  {intent_name}",
                    fill=ACCENT, font=UI_BOLD, anchor="nw",
                )
            reaction = battle.get("reaction")
            if reaction:
                canvas.create_text(
                    bar_right, row_y + 4,
                    text=icon_assets.REACTION_NAMES.get(reaction, reaction),
                    fill="#e8c8ff", font=(UI_FONT[0], 8, "bold"), anchor="ne",
                )
            return

        break_max = battle.get("break_max", 0)
        if break_max:
            break_value = max(0, battle.get("break_value", 0))
            break_ratio = max(0.0, min(1.0, break_value / break_max))
            canvas.create_text(
                bar_left,
                row_y,
                text="破势",
                fill=ACCENT,
                font=(UI_FONT[0], 8, "bold"),
                anchor="nw",
            )
            break_left = bar_left + 34
            canvas.create_rectangle(break_left, row_y + 1, bar_right, row_y + 13,
                                    fill="#252b36", outline="")
            canvas.create_rectangle(break_left, row_y + 1,
                                    break_left + int((bar_right - break_left) * break_ratio), row_y + 13,
                                    fill=ACCENT, outline="")
            canvas.create_text(bar_right, row_y, text=f"{break_value}/{break_max}", fill=FG,
                               font=(UI_FONT[0], 8, "bold"), anchor="ne")
            row_y += 18

        chakra = battle.get("enemy_chakra")
        max_chakra = battle.get("enemy_max_chakra")
        if chakra is not None and max_chakra:
            chakra = max(0, chakra)
            chakra_ratio = max(0.0, min(1.0, chakra / max_chakra))
            canvas.create_text(bar_left, row_y, text="查克拉", fill=CK_COL,
                               font=(UI_FONT[0], 8, "bold"), anchor="nw")
            chakra_left = bar_left + 46
            canvas.create_rectangle(chakra_left, row_y + 1, bar_right, row_y + 13,
                                    fill="#252b36", outline="")
            canvas.create_rectangle(chakra_left, row_y + 1,
                                    chakra_left + int((bar_right - chakra_left) * chakra_ratio), row_y + 13,
                                    fill=CK_COL, outline="")
            canvas.create_text(bar_right, row_y, text=f"{chakra}/{max_chakra}", fill=FG,
                               font=(UI_FONT[0], 8, "bold"), anchor="ne")
            row_y += 18

        icon_specs = []
        elements = battle.get("elements") or []
        if elements:
            icon_specs.append(("elements", elements[0], icon_assets.ELEMENT_NAMES.get(elements[0], elements[0])))
        intent = battle.get("intent")
        if intent:
            icon_specs.append(("intents", intent, battle.get("intent_name") or icon_assets.INTENT_NAMES[intent]))
        for affix in (battle.get("affixes") or [])[:2]:
            icon_specs.append(("affixes", affix, icon_assets.AFFIX_NAMES.get(affix, affix)))
        for status_id in (battle.get("enemy_status") or [])[:2]:
            icon_specs.append(("status", status_id, icon_assets.STATUS_NAMES.get(status_id, status_id)))
        for status_id in (battle.get("player_status") or [])[:2]:
            label = icon_assets.STATUS_NAMES.get(status_id, status_id)
            icon_specs.append(("status", status_id, f"我·{label}"))

        reaction = battle.get("reaction")
        available_slots = max(2, min(6, (panel_width - 18) // 59))
        normal_slots = available_slots - 1 if reaction else available_slots
        x = left + 14
        y = max(row_y + 4, top + 96)
        for category, asset_id, label in icon_specs[:normal_slots]:
            photo = self._load_path_photo(icon_assets.icon_path(category, asset_id), max_dim=34)
            if photo:
                self._overlay_photos.append(photo)
                canvas.create_image(x + 17, y + 17, image=photo)
            else:
                canvas.create_oval(x + 3, y + 3, x + 31, y + 31, outline=DIM)
                canvas.create_text(x + 17, y + 17, text="忍", fill=DIM, font=(UI_FONT[0], 8, "bold"))
            canvas.create_text(
                x + 17,
                y + 39,
                text=label[:7],
                fill=FG,
                font=(UI_FONT[0], 7),
                width=62,
            )
            x += 59

        if reaction:
            photo = self._load_path_photo(icon_assets.icon_path("reactions", reaction), max_dim=58)
            rx = left + panel_width - 45
            canvas.create_rectangle(rx - 31, y - 5, rx + 31, y + 57, fill="#16121a", outline="#b48ce8", width=2)
            if photo:
                self._overlay_photos.append(photo)
                canvas.create_image(rx, y + 18, image=photo)
            canvas.create_text(
                rx,
                y + 47,
                text=icon_assets.REACTION_NAMES.get(reaction, reaction),
                fill="#e8c8ff",
                font=(UI_FONT[0], 8, "bold"),
                width=90,
            )

    def _on_visual_resize(self, _event=None):
        self._redraw_visual()

    def _update_visual_from_text(self, text):
        if self._battle_visual and str(self._current_illustration).startswith("boss:"):
            return
        portrait_id, speaker_name = visual_assets.character_for_text(text)
        illustration_id = visual_assets.illustration_for_text(text)
        if portrait_id or illustration_id:
            self._set_visual(
                portrait_id=portrait_id,
                illustration_id=illustration_id,
                speaker_name=speaker_name,
            )

    def _queue_visual_event(self, event, payload):
        self.out_q.put(("visual", event, payload))

    def _handle_visual_event(self, event, payload):
        if event == "battle_start":
            self._battle_visual = dict(payload)
            enemy_id = payload.get("enemy_id")
            if payload.get("boss") and enemy_id in icon_assets.BOSS_META:
                name, portrait_id, _background, _accent, _secondary = icon_assets.BOSS_META[enemy_id]
                cutin = icon_assets.boss_cutin_path(enemy_id)
                if cutin.is_file():
                    self._current_illustration = f"boss:{enemy_id}"
                    self._banner_photo = self._load_path_photo(cutin)
                self._current_portrait = portrait_id
                self._portrait_photo = self._load_photo("portrait", portrait_id)
                self._speaker_name = name
            self._redraw_visual()
            return
        if event == "battle_update":
            if self._battle_visual is None:
                self._battle_visual = {}
            self._battle_visual.update(payload)
            self._redraw_visual()
            return
        if event == "status":
            if self._battle_visual is not None:
                key = "enemy_status" if payload.get("target") == self._battle_visual.get("enemy_name") else "player_status"
                statuses = list(self._battle_visual.get(key) or [])
                status_id = payload.get("status")
                if status_id and status_id not in statuses:
                    statuses.append(status_id)
                self._battle_visual[key] = statuses[-4:]
                self._redraw_visual()
            return
        if event == "reaction":
            if self._battle_visual is not None:
                self._reaction_token += 1
                token = self._reaction_token
                self._battle_visual["reaction"] = payload.get("reaction")
                self._redraw_visual()
                self.root.after(1800, lambda: self._clear_reaction(token))
            return
        if event == "battle_end":
            self._reaction_token += 1
            self._battle_visual = None
            self._set_visual(illustration_id=visual_assets.illustration_for_location(self.state.location))

    def _clear_reaction(self, token):
        if token != self._reaction_token or not self._battle_visual:
            return
        self._battle_visual.pop("reaction", None)
        self._redraw_visual()

    def _build_sidebar(self, side):
        from tkinter import ttk

        self.collection_button = tk.Button(
            side,
            text="◈ 图鉴·成就·结局收集",
            command=self._open_collection,
            font=UI_BOLD,
            fg=FG,
            bg=BTN_BG,
            activebackground=BTN_HOV,
            activeforeground=FG,
            relief="flat",
            cursor="hand2",
        )
        self.collection_button.pack(side="bottom", fill="x", padx=10, pady=(8, 8))

        # 首屏只固定放置战斗与导航必需信息。
        core = tk.Frame(side, bg=PANEL)
        core.pack(fill="x")
        self.sv = {}
        tk.Label(core, text="鸣 人", font=UI_BOLD, fg=ACCENT, bg=PANEL,
                 anchor="w").pack(fill="x", padx=10, pady=(10, 2))
        self.sv["head"] = tk.StringVar()
        tk.Label(core, textvariable=self.sv["head"], font=UI_BOLD, fg=FG,
                 bg=PANEL, anchor="w").pack(fill="x", padx=10)
        bars = tk.Frame(core, bg=PANEL)
        bars.pack(fill="x", pady=3)
        self.bar_hp = StatBar(bars, 0, "生命", HP_COL)
        self.bar_ck = StatBar(bars, 1, "查克拉", CK_COL)
        self.bar_xp = StatBar(bars, 2, "经验", EXP_COL)

        quick = tk.Frame(core, bg=PANEL2, padx=8, pady=6)
        quick.pack(fill="x", padx=8, pady=(3, 7))
        for column in range(2):
            quick.grid_columnconfigure(column, weight=1)
        for index, (key, label) in enumerate((("loc", "所在地"), ("time", "时间"),
                                               ("fate", "命运点"), ("party", "同行"))):
            box = tk.Frame(quick, bg=PANEL2)
            box.grid(row=index // 2, column=index % 2, sticky="ew", padx=3, pady=2)
            tk.Label(box, text=label, font=(UI_FONT[0], 8), fg=DIM, bg=PANEL2,
                     anchor="w").pack(fill="x")
            self.sv[key] = tk.StringVar()
            tk.Label(box, textvariable=self.sv[key], font=UI_BOLD, fg=FG, bg=PANEL2,
                     anchor="w", wraplength=120).pack(fill="x")

        style = ttk.Style(self.root)
        style.configure("Side.TNotebook", background=PANEL, borderwidth=0,
                        tabmargins=(0, 0, 0, 0))
        style.configure("Side.TNotebook.Tab", background=PANEL2, foreground=DIM,
                        padding=(14, 8), font=UI_BOLD, borderwidth=0)
        style.map("Side.TNotebook.Tab",
                  background=[("selected", BTN_BG), ("active", BTN_HOV)],
                  foreground=[("selected", ACCENT), ("active", FG)])
        notebook = ttk.Notebook(side, style="Side.TNotebook")
        notebook.pack(fill="both", expand=True, padx=8, pady=(2, 0))
        tabs = []
        for title in ("成长", "关系", "行囊"):
            tab = tk.Frame(notebook, bg=PANEL)
            notebook.add(tab, text=title)
            tabs.append(tab)

        scroll_body = tabs[0]
        sidebar_canvas = tk.Canvas(scroll_body, bg=PANEL, highlightthickness=0)
        sidebar_scroll = tk.Scrollbar(scroll_body, orient="vertical", command=sidebar_canvas.yview)
        sidebar_canvas.configure(yscrollcommand=sidebar_scroll.set)
        sidebar_scroll.pack(side="right", fill="y")
        sidebar_canvas.pack(side="left", fill="both", expand=True)
        content = tk.Frame(sidebar_canvas, bg=PANEL)
        content_window = sidebar_canvas.create_window((0, 0), window=content, anchor="nw")
        content.bind(
            "<Configure>",
            lambda _event: sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all")),
        )
        sidebar_canvas.bind(
            "<Configure>",
            lambda event: sidebar_canvas.itemconfigure(content_window, width=event.width),
        )
        sidebar_canvas.bind(
            "<MouseWheel>",
            lambda event: sidebar_canvas.yview_scroll(int(-event.delta / 120), "units"),
        )
        self.sidebar_canvas = sidebar_canvas
        self.side_lists = {}
        self.stat_vars = {}
        self.metric_rows = {}

        def section_card(parent, title):
            outer = tk.Frame(parent, bg=PANEL2, padx=10, pady=8)
            outer.pack(fill="x", padx=8, pady=(8, 0))
            tk.Label(
                outer, text=title, font=UI_BOLD, fg=ACCENT, bg=PANEL2, anchor="w",
            ).pack(fill="x", pady=(0, 6))
            return outer

        def plain_row(parent, key, label):
            frame = tk.Frame(parent, bg=PANEL2)
            frame.pack(fill="x", pady=2)
            tk.Label(
                frame, text=label, font=(UI_FONT[0], 9), fg=DIM, bg=PANEL2,
                width=8, anchor="nw",
            ).pack(side="left")
            self.sv[key] = tk.StringVar()
            tk.Label(
                frame, textvariable=self.sv[key], font=(UI_FONT[0], 9), fg=FG,
                bg=PANEL2, anchor="nw", justify="left", wraplength=245,
            ).pack(side="left", fill="x", expand=True)

        # ── 成长：四维格子 + 结构化列表 ──
        stats_card = section_card(content, "忍者素质")
        grid = tk.Frame(stats_card, bg=PANEL2)
        grid.pack(fill="x", pady=(0, 4))
        for column in range(2):
            grid.grid_columnconfigure(column, weight=1, uniform="stat_grid")
        for index, (key, label) in enumerate((
            ("attack", "攻击"),
            ("defense", "防御"),
            ("speed", "速度"),
            ("spirit", "精神"),
        )):
            cell = tk.Frame(grid, bg=BTN_BG, padx=8, pady=6)
            cell.grid(
                row=index // 2, column=index % 2,
                sticky="nsew", padx=3, pady=3,
            )
            tk.Label(
                cell, text=label, font=(UI_FONT[0], 8), fg=DIM, bg=BTN_BG, anchor="w",
            ).pack(fill="x")
            self.stat_vars[key] = tk.StringVar(value="—")
            tk.Label(
                cell, textvariable=self.stat_vars[key],
                font=(UI_FONT[0], 12, "bold"), fg=FG, bg=BTN_BG, anchor="w",
            ).pack(fill="x")
        plain_row(stats_card, "backlash", "风险")
        plain_row(stats_card, "flux", "九尾")

        journey_card = section_card(content, "旅程进度")
        plain_row(journey_card, "chapter", "主线")
        self.side_lists["reputation"] = self._make_side_list(
            journey_card, empty_text="(尚无解锁势力)",
        )
        plain_row(journey_card, "cycle", "周目")

        combat_card = section_card(content, "战斗准备")
        tk.Label(
            combat_card, text="队友", font=(UI_FONT[0], 8, "bold"),
            fg=DIM, bg=PANEL2, anchor="w",
        ).pack(fill="x", pady=(2, 0))
        self.side_lists["growth"] = self._make_side_list(
            combat_card, empty_text="(无同行队友)",
        )
        tk.Label(
            combat_card, text="忍术装备", font=(UI_FONT[0], 8, "bold"),
            fg=DIM, bg=PANEL2, anchor="w",
        ).pack(fill="x", pady=(6, 0))
        self.side_lists["loadout"] = self._make_side_list(
            combat_card, empty_text="(未装备)",
        )
        tk.Label(
            combat_card, text="忍具", font=(UI_FONT[0], 8, "bold"),
            fg=DIM, bg=PANEL2, anchor="w",
        ).pack(fill="x", pady=(6, 0))
        self.side_lists["gear"] = self._make_side_list(
            combat_card, empty_text="(未装备)",
        )

        # ── 关系：指标行（左名右值）──
        for key, title, fields in (
            ("trust", "第七班", (("trust", "信任"),)),
            ("suspicion", "怀疑 / 归属",
             (("kakashi", "卡卡西怀疑"), ("belonging", "归属感"))),
            ("sasuke", "佐助",
             (("trust", "信任"), ("revenge", "复仇"), ("curse", "咒印"))),
            ("sakura", "小樱",
             (("confidence", "自信"), ("trust", "信任"))),
        ):
            card = section_card(tabs[1], title)
            self.metric_rows[key] = self._make_metric_block(card, fields)

        # ── 行囊：契约 / 道具列表 + 资金 ──
        bag_scroll = tk.Canvas(tabs[2], bg=PANEL, highlightthickness=0)
        bag_bar = tk.Scrollbar(tabs[2], orient="vertical", command=bag_scroll.yview)
        bag_scroll.configure(yscrollcommand=bag_bar.set)
        bag_bar.pack(side="right", fill="y")
        bag_scroll.pack(side="left", fill="both", expand=True)
        bag_body = tk.Frame(bag_scroll, bg=PANEL)
        bag_window = bag_scroll.create_window((0, 0), window=bag_body, anchor="nw")
        bag_body.bind(
            "<Configure>",
            lambda _event: bag_scroll.configure(scrollregion=bag_scroll.bbox("all")),
        )
        bag_scroll.bind(
            "<Configure>",
            lambda event: bag_scroll.itemconfigure(bag_window, width=event.width),
        )
        bag_scroll.bind(
            "<MouseWheel>",
            lambda event: bag_scroll.yview_scroll(int(-event.delta / 120), "units"),
        )
        self.bag_canvas = bag_scroll

        contracts_card = section_card(bag_body, "契约")
        self.side_lists["contracts"] = self._make_side_list(
            contracts_card, empty_text="(尚无契约)",
        )
        items_card = section_card(bag_body, "道具")
        self.side_lists["items"] = self._make_side_list(
            items_card, empty_text="(空)",
        )
        money_card = section_card(bag_body, "资金")
        plain_row(money_card, "ryo", "两")

        # 兼容旧代码：保留占位 StringVar，避免遗漏引用崩溃
        for legacy_key in (
            "stats", "reputation", "growth", "loadout", "gear",
            "trust", "suspicion", "sasuke", "sakura", "contracts", "items",
        ):
            self.sv.setdefault(legacy_key, tk.StringVar())

    def _make_side_list(self, parent, empty_text="(无)"):
        """可刷新的名称/数值双列列表，内容签名不变时不重建。"""
        holder = tk.Frame(parent, bg=PANEL2)
        holder.pack(fill="x", pady=(2, 2))
        return {
            "frame": holder,
            "empty_text": empty_text,
            "signature": None,
        }

    def _make_metric_block(self, parent, fields):
        """关系类指标：每行 标签 + 数值。"""
        block = tk.Frame(parent, bg=PANEL2)
        block.pack(fill="x")
        vars_map = {}
        for key, label in fields:
            row = tk.Frame(block, bg=BTN_BG)
            row.pack(fill="x", pady=2)
            tk.Label(
                row, text=label, font=(UI_FONT[0], 9), fg=DIM, bg=BTN_BG,
                anchor="w", padx=8, pady=5,
            ).pack(side="left")
            var = tk.StringVar(value="—")
            vars_map[key] = var
            tk.Label(
                row, textvariable=var, font=(UI_FONT[0], 10, "bold"),
                fg=FG, bg=BTN_BG, anchor="e", padx=8, pady=5,
            ).pack(side="right")
        return vars_map

    def _set_side_list(self, list_key, rows):
        """rows: [(name, value), ...]；仅内容变化时重建子控件。"""
        panel = self.side_lists.get(list_key)
        if not panel:
            return
        normalized = []
        for entry in rows or ():
            if isinstance(entry, (list, tuple)) and len(entry) >= 2:
                normalized.append((str(entry[0]), str(entry[1])))
            else:
                normalized.append((str(entry), ""))
        signature = tuple(normalized) if normalized else (("__empty__", panel["empty_text"]),)
        if signature == panel["signature"]:
            return
        panel["signature"] = signature
        frame = panel["frame"]
        for child in frame.winfo_children():
            child.destroy()
        if not normalized:
            tk.Label(
                frame, text=panel["empty_text"], font=(UI_FONT[0], 9),
                fg=DIM, bg=PANEL2, anchor="w", padx=4, pady=4,
            ).pack(fill="x")
            return
        for index, (name, value) in enumerate(normalized):
            bg = BTN_BG if index % 2 == 0 else PANEL2
            row = tk.Frame(frame, bg=bg)
            row.pack(fill="x", pady=1)
            tk.Label(
                row, text=name, font=(UI_FONT[0], 9), fg=FG, bg=bg,
                anchor="w", padx=6, pady=4,
            ).pack(side="left", fill="x", expand=True)
            if value:
                tk.Label(
                    row, text=value, font=(UI_FONT[0], 9, "bold"), fg=ACCENT,
                    bg=bg, anchor="e", padx=6, pady=4,
                ).pack(side="right")

    # ── 输入输出接管 ──────────────────────────

    def _patch_io(self):
        sys.stdout = GuiIO(self.out_q)
        ui.choose = self._gui_choose
        ui.pause = self._gui_pause
        ui.VISUAL_EVENT_HANDLER = self._queue_visual_event
        # 装饰分隔线在窗口里最多 40 个全角字符,避免折行
        ui.line = lambda char="─", width=46: self._original_line(char, min(width, 40))
        self._io_patched = True

    def _restore_io(self):
        if not self._io_patched:
            return
        sys.stdout = self._original_stdout
        ui.choose = self._original_choose
        ui.pause = self._original_pause
        ui.line = self._original_line
        ui.VISUAL_EVENT_HANDLER = self._original_visual_handler
        self._io_patched = False

    # 以下两个函数运行在工作线程:发消息给界面,阻塞等回答
    def _gui_choose(self, prompt, options, allow_cancel=False):
        if prompt:
            ui.slow_print(prompt)
        self.out_q.put(("choose", prompt, list(options), allow_cancel))
        answer = self.ans_q.get()
        if answer is CLOSE_SIGNAL:
            raise GUIClosed
        return answer

    def _gui_pause(self, msg="(按回车继续)"):
        self.out_q.put(("pause", msg))
        if self.ans_q.get() is CLOSE_SIGNAL:
            raise GUIClosed

    def _run_game(self):
        """工作线程:运行终端与 GUI 共用的唯一游戏流程。"""
        try:
            runtime.run_game(self.state)
        except GUIClosed:
            pass
        except Exception:
            self.out_q.put(("txt", "\n[游戏内部发生错误]\n" + traceback.format_exc()))
        finally:
            self._restore_io()
            self.out_q.put(("end",))

    # ── 界面线程:消息循环 ──────────────────────

    def _poll(self):
        chunks = []
        try:
            while True:
                msg = self.out_q.get_nowait()
                kind = msg[0]
                if kind == "txt":
                    chunks.append(msg[1])
                    continue
                self._flush_text(chunks)
                if kind == "visual":
                    _, event, payload = msg
                    self._handle_visual_event(event, payload)
                elif kind == "choose":
                    _, self._prompt, self._options, self._allow_cancel = msg
                    self.waiting = "choose"
                    self._show_choices()
                    self._refresh_status()
                elif kind == "pause":
                    _, pause_message = msg if len(msg) > 1 else ("pause", "(按回车继续)")
                    self.waiting = "pause"
                    self._show_continue_prompt(pause_message)
                    self._refresh_status()
                elif kind == "end":
                    self.ended = True
                    self.waiting = None
                    self._clear_buttons()
                    self.hint_var.set("游戏已结束 —— 可直接关闭窗口")
                    self._refresh_status()
        except queue.Empty:
            pass
        self._flush_text(chunks)

        self._tick += 1
        if self._tick % 30 == 0:
            # 旁白播放期间也定期刷新边栏;此时工作线程可能正在改状态,
            # 瞬时不一致就跳过,下个节拍再刷 (等待输入时的刷新总是一致的)
            try:
                self._refresh_status()
            except Exception:
                pass
        if not self.closed:
            self.root.after(15, self._poll)

    def _flush_text(self, chunks, tag=None):
        if not chunks:
            return
        s = "".join(chunks)
        chunks.clear()
        self._update_visual_from_text(s)
        self.text.configure(state="normal")
        if tag:
            self.text.insert("end", s, tag)
        else:
            # 按行首符号自动着色;慢速模式一行会跨多次 flush,
            # 用 _at_line_start/_cur_tag 状态机保证判定只看行首首个非空白字符
            for piece in s.splitlines(keepends=True):
                if self._at_line_start:
                    head = piece.lstrip()[:1]
                    if head:  # 行首仍全是空白则保持待定
                        self._cur_tag = SYMBOL_TAGS.get(head)
                        self._at_line_start = False
                self.text.insert("end", piece, self._cur_tag or ())
                if piece.endswith("\n"):
                    self._at_line_start, self._cur_tag = True, None
        self.text.configure(state="disabled")
        # 不再瞬间跳到底。持续输出时只更新同一个滚动目标，由动画以稳定的
        # 阅读速度追随；输出停止后仍会走完最后一段，形成自动翻页的感觉。
        self._start_story_scroll()

    def _start_story_scroll(self):
        if self.closed or self._story_scroll_job is not None:
            return
        self._story_scroll_job = self.root.after(16, self._step_story_scroll)

    def _step_story_scroll(self):
        self._story_scroll_job = None
        if self.closed:
            return
        self.text.update_idletasks()
        _top, bottom = self.text.yview()
        if bottom >= 0.9995:
            return
        # 固定步长由偏好 scroll_speed 决定；距离再远也不分档加速，抵达末尾时依靠
        # Text 自身的滚动边界自然停下，避免最后一次强制贴底造成抖动。
        pixels = SCROLL_SPEED_PRESETS.get(
            self.prefs.get("scroll_speed", "normal"),
            SCROLL_SPEED_PRESETS["normal"],
        )["pixels"]
        self.text.yview_scroll(pixels, "pixels")
        self._story_scroll_job = self.root.after(16, self._step_story_scroll)

    # ── 选项按钮 ──────────────────────────────

    def _clear_buttons(self):
        for w in self.btn_frame.winfo_children():
            w.destroy()
        self.choice_canvas.yview_moveto(0)
        # 行动区保持固定高度。若在点击后折叠、下一轮再展开，下面的剧情
        # Text 会一次改变上百像素高度，看起来就像自动滚动突然翻了一页。
        self.choice_canvas.configure(
            height=CHOICE_VIEW_HEIGHT,
            scrollregion=(0, 0, 0, 0),
        )
        self.choice_scroll.pack_forget()
        self.continue_panel = None
        self.continue_button = None

    def _normalize_pause_message(self, message):
        """把终端式「(按回车继续)」整理成 GUI 可读提示。"""
        text = (message or "").strip()
        for wrapper in (("(", ")"), ("（", "）"), ("[", "]"), ("【", "】")):
            if text.startswith(wrapper[0]) and text.endswith(wrapper[1]):
                text = text[len(wrapper[0]):-len(wrapper[1])].strip()
        generic = {
            "",
            "按回车继续",
            "按 回车 继续",
            "回车继续",
            "press enter",
            "press enter to continue",
        }
        if text.lower() in generic or text in ("按回车继续", "回车继续"):
            return "阅读完毕后，点击下方按钮继续"
        return text

    def _show_continue_prompt(self, message="(按回车继续)"):
        """暂停态：大号主按钮，与行动选项列表视觉明显区分。"""
        self._clear_buttons()
        self._choice_columns = 1
        for column in range(2):
            self.btn_frame.grid_columnconfigure(
                column,
                weight=1 if column == 0 else 0,
                uniform="btn" if column == 0 else "",
            )

        prompt_text = self._normalize_pause_message(message)
        self.hint_var.set("▼ 剧情暂停 · 准备继续")

        shell = tk.Frame(self.btn_frame, bg=PANEL)
        shell.grid(row=0, column=0, sticky="ew", padx=6, pady=(10, 6))
        self.btn_frame.grid_columnconfigure(0, weight=1)

        # 左侧强调条 + 文案，模仿商业 AVG 的“等待输入”条。
        banner = tk.Frame(shell, bg=PANEL2, highlightthickness=1,
                          highlightbackground=MODAL_CARD_EDGE)
        banner.pack(fill="x", pady=(0, 12))
        accent_strip = tk.Frame(banner, bg=ACCENT, width=4)
        accent_strip.pack(side="left", fill="y")
        copy = tk.Frame(banner, bg=PANEL2)
        copy.pack(side="left", fill="both", expand=True, padx=14, pady=10)
        tk.Label(
            copy,
            text="剧情推进",
            font=(UI_FONT[0], 8, "bold"),
            fg=ACCENT,
            bg=PANEL2,
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            copy,
            text=prompt_text,
            font=UI_FONT,
            fg=FG,
            bg=PANEL2,
            anchor="w",
            justify="left",
            wraplength=560,
        ).pack(fill="x", pady=(2, 0))

        # 主 CTA：橙色大按钮，hover 提亮；与灰色行动按钮形成层级。
        continue_size = FONT_SCALE_PRESETS.get(
            self.prefs.get("font_scale", "medium"),
            FONT_SCALE_PRESETS["medium"],
        )["continue"]
        cta_wrap = tk.Frame(shell, bg=ACCENT, padx=2, pady=2)
        cta_wrap.pack(fill="x")
        continue_button = tk.Button(
            cta_wrap,
            text="▶  继续",
            command=self._continue,
            font=(UI_FONT[0], continue_size, "bold"),
            bg=PRIMARY_BTN,
            fg=PRIMARY_BTN_FG,
            activebackground=PRIMARY_BTN_HOV,
            activeforeground=PRIMARY_BTN_FG,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=24,
            pady=14,
        )
        continue_button.pack(fill="x")
        continue_button.bind(
            "<Enter>",
            lambda _event: continue_button.config(bg=PRIMARY_BTN_HOV),
        )
        continue_button.bind(
            "<Leave>",
            lambda _event: continue_button.config(bg=PRIMARY_BTN),
        )

        tk.Label(
            shell,
            text="快捷键：Enter  /  空格",
            font=(UI_FONT[0], 9),
            fg=DIM,
            bg=PANEL,
            anchor="center",
        ).pack(fill="x", pady=(10, 2))

        self.continue_panel = shell
        self.continue_button = continue_button
        self.root.after_idle(self._resize_choice_area)
        return continue_button

    def _choice_asset_path(self, category, asset_id):
        if category == "wanted":
            return icon_assets.wanted_path(asset_id, thumbnail=True)
        if category == "portraits":
            return visual_assets.portrait_path(asset_id)
        if category == "illustrations":
            return visual_assets.illustration_path(asset_id)
        return icon_assets.icon_path(category, asset_id)

    def _make_button(self, option, cmd, r, c, prefix=""):
        choice = ui.as_choice(option)
        label = prefix + choice.label
        if choice.badge:
            label += f"  [{choice.badge}]"
        asset = choice.asset or icon_assets.option_asset(choice.label)
        image = None
        if asset:
            category, asset_id = asset
            path = self._choice_asset_path(category, asset_id)
            max_dim = 68 if category == "wanted" else 44 if category == "illustrations" else 40
            image = self._load_path_photo(path, max_dim=max_dim)
        columns = getattr(self, "_choice_columns", 1)
        area_width = max(self.choice_canvas.winfo_width(), self.root.winfo_width() // 2)
        column_width = area_width // columns
        # Tk 的 compound 按钮不会可靠地按长文本撑高；按实际列宽换行，
        # 并且只在确有语义资源时显示图标，避免突兀的“+”占位块。
        wraplength = max(180, column_width - (72 if image else 30))
        button_options = {}
        if image is not None:
            button_options.update(image=image, compound="left")
        b = tk.Button(self.btn_frame, text=label, command=cmd, font=BTN_FONT,
                      bg=BTN_BG, fg=FG, activebackground=BTN_HOV,
                      activeforeground=FG, relief="flat", anchor="w",
                      padx=10, pady=8, cursor="hand2", wraplength=wraplength,
                      justify="left",
                      state="normal" if choice.enabled else "disabled",
                      **button_options)
        if image is not None:
            b.image = image
        b.bind("<Enter>", lambda e: b.config(bg=BTN_HOV))
        b.bind("<Leave>", lambda e: b.config(bg=BTN_BG))
        b.bind("<MouseWheel>", self._scroll_choices)
        b.grid(row=r, column=c, sticky="ew", padx=3, pady=3)
        if choice.detail:
            # 独立的“详情”点击区：主按钮仍可直接选择行动，说明按需弹出。
            info = tk.Button(
                self.btn_frame, text="详情", font=(UI_FONT[0], 8),
                bg=PANEL2, fg=DIM, activebackground=BTN_HOV,
                activeforeground=FG, relief="flat", cursor="hand2",
                command=lambda title=choice.label, detail=choice.detail:
                    self._show_choice_detail(title, detail),
            )
            info.place(in_=b, relx=1.0, rely=0.5, x=-8, anchor="e")
            info.bind("<MouseWheel>", self._scroll_choices)
        return b

    def _show_choice_detail(self, title, detail):
        """在不占用行动列表空间的前提下展示选项完整说明。"""
        self._modal_info(
            title=title or "行动详情",
            message=detail or "（暂无说明）",
            badge="详情",
            ok_label="知道了",
        )

    # ── 商业风模态浮层（替代系统 messagebox）──

    def _modal_info(self, title, message, badge="提示", ok_label="确定"):
        """信息弹层：阅读后点主按钮关闭。"""
        return self._show_game_modal(
            title=title,
            message=message,
            kind="info",
            badge=badge,
            buttons=(
                {"id": "ok", "label": ok_label, "style": "primary", "default": True},
            ),
        )

    def _modal_error(self, title, message, badge="错误", ok_label="知道了"):
        """错误弹层：强调色边框，阻塞至确认。"""
        return self._show_game_modal(
            title=title,
            message=message,
            kind="error",
            badge=badge,
            buttons=(
                {"id": "ok", "label": ok_label, "style": "danger", "default": True},
            ),
        )

    def _modal_confirm(
        self,
        title,
        message,
        *,
        badge="确认",
        yes_label="确定",
        no_label="取消",
        danger=False,
    ):
        """确认弹层：返回 True/False。Esc / 点遮罩 = 取消。"""
        result = self._show_game_modal(
            title=title,
            message=message,
            kind="danger" if danger else "confirm",
            badge=badge,
            buttons=(
                {"id": "no", "label": no_label, "style": "secondary", "cancel": True},
                {
                    "id": "yes",
                    "label": yes_label,
                    "style": "danger" if danger else "primary",
                    "default": True,
                },
            ),
            dismiss_id="no",
        )
        return result == "yes"

    def _show_game_modal(
        self,
        title,
        message,
        *,
        kind="info",
        badge="提示",
        buttons=None,
        dismiss_id="ok",
        max_body_height=280,
    ):
        """在主窗口上绘制全屏遮罩 + 居中卡片，阻塞直到用户选择。

        返回被点击按钮的 id；窗口已关闭时返回 dismiss_id。
        """
        if self.closed or not self.root.winfo_exists():
            return dismiss_id
        if self._modal_active:
            self._close_game_modal(self._modal_result if self._modal_result is not None else dismiss_id)

        buttons = list(buttons or (
            {"id": "ok", "label": "确定", "style": "primary", "default": True},
        ))
        accent = {
            "info": ACCENT,
            "confirm": ACCENT,
            "danger": WARN_COL,
            "error": WARN_COL,
        }.get(kind, ACCENT)

        self._modal_active = True
        self._modal_result = None
        self._modal_waiter = tk.StringVar(master=self.root, value="")
        self._modal_primary_action = None
        self._modal_cancel_action = dismiss_id

        backdrop = tk.Frame(self.root, bg=MODAL_BACKDROP, cursor="arrow")
        backdrop.place(x=0, y=0, relwidth=1, relheight=1)
        backdrop.lift()
        self._modal_backdrop = backdrop

        # 外层居中容器：用 place 把卡片钉在视口中央。
        shell = tk.Frame(backdrop, bg=MODAL_BACKDROP)
        shell.place(relx=0.5, rely=0.5, anchor="center")

        # 双层边框模拟商业 UI 卡片厚度。
        outer = tk.Frame(shell, bg=accent, padx=2, pady=2)
        outer.pack()
        card = tk.Frame(outer, bg=MODAL_CARD, padx=0, pady=0)
        card.pack()
        card.configure(highlightbackground=MODAL_CARD_EDGE, highlightthickness=1)

        header = tk.Frame(card, bg=MODAL_HEADER)
        header.pack(fill="x")
        badge_label = tk.Label(
            header,
            text=f" {badge} ",
            font=(UI_FONT[0], 8, "bold"),
            fg="#1a1208" if kind in ("info", "confirm") else FG,
            bg=accent,
            padx=8,
            pady=3,
        )
        badge_label.pack(side="left", padx=(16, 10), pady=14)
        tk.Label(
            header,
            text=title,
            font=(UI_FONT[0], 13, "bold"),
            fg=FG,
            bg=MODAL_HEADER,
            anchor="w",
        ).pack(side="left", fill="x", expand=True, padx=(0, 16), pady=14)

        accent_bar = tk.Frame(card, bg=accent, height=2)
        accent_bar.pack(fill="x")

        body_wrap = tk.Frame(card, bg=MODAL_CARD)
        body_wrap.pack(fill="both", expand=True, padx=20, pady=(16, 8))

        body_text = str(message).strip() or "（无内容）"
        # 长文用可滚动文本区；短文用标签，避免多余滚动条。
        if len(body_text) > 160 or body_text.count("\n") >= 4:
            text_frame = tk.Frame(body_wrap, bg=PANEL2, highlightthickness=1,
                                  highlightbackground=MODAL_CARD_EDGE)
            text_frame.pack(fill="both", expand=True)
            text_widget = tk.Text(
                text_frame,
                wrap="word",
                font=UI_FONT,
                bg=PANEL2,
                fg=FG,
                relief="flat",
                padx=12,
                pady=10,
                height=min(12, max(4, body_text.count("\n") + 3)),
                width=48,
                cursor="arrow",
            )
            scroll = tk.Scrollbar(text_frame, command=text_widget.yview,
                                  troughcolor=PANEL2, bg=BTN_BG)
            text_widget.configure(yscrollcommand=scroll.set)
            scroll.pack(side="right", fill="y")
            text_widget.pack(side="left", fill="both", expand=True)
            text_widget.insert("1.0", body_text)
            text_widget.configure(state="disabled")
            # 限制最大高度，避免小窗被撑破。
            text_widget.configure(height=min(14, max(5, max_body_height // 22)))
        else:
            tk.Label(
                body_wrap,
                text=body_text,
                font=UI_FONT,
                fg=FG,
                bg=MODAL_CARD,
                justify="left",
                anchor="w",
                wraplength=420,
            ).pack(fill="x")

        footer = tk.Frame(card, bg=MODAL_CARD)
        footer.pack(fill="x", padx=16, pady=(8, 16))

        hint = tk.Label(
            footer,
            text="Enter 确认 · Esc 关闭",
            font=(UI_FONT[0], 8),
            fg=DIM,
            bg=MODAL_CARD,
            anchor="w",
        )
        hint.pack(side="left", padx=(4, 8))

        btn_row = tk.Frame(footer, bg=MODAL_CARD)
        btn_row.pack(side="right")

        def finish(action_id):
            self._close_game_modal(action_id)

        for spec in buttons:
            style = spec.get("style", "secondary")
            if style == "primary":
                bg, hover, fg = PRIMARY_BTN, PRIMARY_BTN_HOV, PRIMARY_BTN_FG
            elif style == "danger":
                bg, hover, fg = DANGER_BTN, DANGER_BTN_HOV, FG
            else:
                bg, hover, fg = BTN_BG, BTN_HOV, FG
            action_id = spec["id"]
            button = tk.Button(
                btn_row,
                text=spec["label"],
                font=UI_BOLD,
                bg=bg,
                fg=fg,
                activebackground=hover,
                activeforeground=fg,
                relief="flat",
                padx=18,
                pady=8,
                cursor="hand2",
                command=lambda action=action_id: finish(action),
            )
            button.pack(side="left", padx=4)
            button.bind("<Enter>", lambda _e, target=button, color=hover: target.config(bg=color))
            button.bind("<Leave>", lambda _e, target=button, color=bg: target.config(bg=color))
            if spec.get("default"):
                self._modal_primary_action = action_id
            if spec.get("cancel"):
                self._modal_cancel_action = action_id

        if self._modal_primary_action is None and buttons:
            self._modal_primary_action = buttons[-1]["id"]
        if self._modal_cancel_action is None:
            self._modal_cancel_action = dismiss_id

        # 点遮罩空白处 = 取消/关闭（点卡片本身不关闭）。
        backdrop.bind("<Button-1>", lambda _e: finish(self._modal_cancel_action))
        for widget in (shell, outer, card, header, body_wrap, footer, btn_row):
            widget.bind("<Button-1>", lambda e: "break")

        try:
            self.root.wait_variable(self._modal_waiter)
        except tk.TclError:
            return dismiss_id

        result = self._modal_result
        if result is None or result == "":
            return dismiss_id
        return result

    def _close_game_modal(self, action_id="ok"):
        if not self._modal_active and self._modal_backdrop is None:
            return
        self._modal_result = action_id
        backdrop = self._modal_backdrop
        self._modal_backdrop = None
        self._modal_active = False
        self._modal_primary_action = None
        self._modal_cancel_action = None
        if backdrop is not None:
            try:
                backdrop.place_forget()
                backdrop.destroy()
            except tk.TclError:
                pass
        waiter = self._modal_waiter
        self._modal_waiter = None
        if waiter is not None:
            try:
                waiter.set(str(action_id))
            except tk.TclError:
                pass

    def _make_skill_button(self, option, cmd, r, c, prefix=""):
        """宝可梦式技能卡：技能名和属性在上，威力/消耗固定在下方。"""
        choice = ui.as_choice(option)
        power = re.search(r"威力\s*(\d+)", choice.label)
        cost = re.search(r"查克拉\s*(\d+)", choice.label)
        skill_name = choice.label.split(" (威力", 1)[0].strip()
        asset = choice.asset or icon_assets.option_asset(choice.label)
        skill_id = asset[1] if asset and asset[0] == "skills" else None
        skill = self.state.skills_db.get(skill_id, {})
        element_id = skill.get("element", "neutral")
        element = icon_assets.ELEMENT_NAMES.get(element_id, element_id or "无属性")
        colors = {
            "fire": "#b94b3e", "water": "#367cab", "wind": "#4a9b72",
            "lightning": "#aa8b32", "earth": "#8c6845", "yin": "#75549b",
            "yang": "#b67b35", "neutral": "#596171",
        }
        accent = colors.get(element_id, "#596171")
        enabled = choice.enabled and (not cost or int(cost.group(1)) <= self.state.player.get("chakra", 0))

        card = tk.Frame(self.btn_frame, bg=BTN_BG, highlightthickness=2,
                        highlightbackground=accent, cursor="hand2")
        card.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)
        top = tk.Frame(card, bg=BTN_BG)
        top.pack(fill="x", padx=9, pady=(7, 2))
        tk.Label(top, text=f"{prefix}{skill_name}", font=UI_BOLD,
                 fg=FG if enabled else DIM, bg=BTN_BG, anchor="w").pack(side="left", fill="x", expand=True)
        tk.Label(top, text=element, font=(UI_FONT[0], 8, "bold"), fg="#ffffff",
                 bg=accent, padx=6, pady=2).pack(side="right")
        stats = f"威力  {power.group(1) if power else '—'}        查克拉  {cost.group(1) if cost else '0'}"
        tk.Label(card, text=stats, font=(UI_FONT[0], 9, "bold"), fg=FG if enabled else DIM,
                 bg=PANEL2, anchor="w", padx=9, pady=4).pack(fill="x", padx=2, pady=(2, 2))
        description = choice.detail or skill.get("description", "")
        if description:
            tk.Label(card, text=description, font=(UI_FONT[0], 8), fg=DIM, bg=BTN_BG,
                     anchor="w", justify="left", wraplength=330).pack(fill="x", padx=9, pady=(2, 7))

        widgets = [card, *card.winfo_children()]
        widgets += [child for child in card.winfo_children() for child in child.winfo_children()]
        if enabled:
            for widget in widgets:
                widget.bind("<Button-1>", lambda _event: cmd())
                widget.bind("<Enter>", lambda _event, target=card: target.config(bg=BTN_HOV))
                widget.bind("<Leave>", lambda _event, target=card: target.config(bg=BTN_BG))
        # 技能卡内层 Label/Frame 必须各自绑定滚轮，否则 Windows 下事件不冒泡。
        self._bind_choice_wheel(card)
        return card

    def _bind_choice_wheel(self, widget):
        """递归绑定滚轮：覆盖技能卡、详情按钮等所有子控件。"""
        if widget is None:
            return
        try:
            widget.bind("<MouseWheel>", self._scroll_choices)
            widget.bind("<Button-4>", self._scroll_choices)  # Linux 上滚
            widget.bind("<Button-5>", self._scroll_choices)  # Linux 下滚
        except tk.TclError:
            return
        for child in widget.winfo_children():
            self._bind_choice_wheel(child)

    def _choice_content_overflows(self):
        """行动区内容是否超出固定视口高度。"""
        if not self.btn_frame.winfo_exists():
            return False
        self.btn_frame.update_idletasks()
        bbox = self.choice_canvas.bbox("all")
        if bbox:
            content_height = max(1, bbox[3] - bbox[1])
        else:
            content_height = max(1, self.btn_frame.winfo_reqheight())
        view_height = max(1, self.choice_canvas.winfo_height() or CHOICE_VIEW_HEIGHT)
        return content_height > view_height + 2

    def _scroll_choices(self, event):
        """滚动行动/技能列表。只要内容溢出即可滚，不依赖滚动条是否显示。"""
        if self.closed or not hasattr(self, "choice_canvas"):
            return
        if not self.choice_canvas.winfo_exists():
            return
        if not self._choice_content_overflows():
            return
        delta = getattr(event, "delta", 0) or 0
        if delta:
            # Windows / macOS：delta 为 ±120 的倍数
            steps = int(-delta / 120)
            if steps == 0:
                steps = -1 if delta > 0 else 1
            self.choice_canvas.yview_scroll(steps, "units")
        elif getattr(event, "num", None) == 4:
            self.choice_canvas.yview_scroll(-1, "units")
        elif getattr(event, "num", None) == 5:
            self.choice_canvas.yview_scroll(1, "units")
        return "break"

    def _resize_choice_area(self):
        if self.closed or not self.btn_frame.winfo_exists():
            return
        self.btn_frame.update_idletasks()
        content_height = max(1, self.btn_frame.winfo_reqheight())
        self.choice_canvas.configure(
            height=CHOICE_VIEW_HEIGHT,
            scrollregion=self.choice_canvas.bbox("all"),
        )
        if content_height > CHOICE_VIEW_HEIGHT:
            if not self.choice_scroll.winfo_manager():
                self.choice_scroll.pack(
                    side="right", fill="y", before=self.choice_canvas
                )
        else:
            self.choice_scroll.pack_forget()
        # 新建选项后补绑滚轮（含技能卡深层子控件）。
        self._bind_choice_wheel(self.btn_frame)
        self._bind_choice_wheel(self.choice_canvas)

    def _show_choices(self):
        self._clear_buttons()
        self.hint_var.set("▼ 选择行动 (可按数字键)")
        skill_mode = "使用哪个技能" in self._prompt
        # 详情不再参与布局计算；宽屏下普通行动和技能都使用双列。
        columns = 2 if self.root.winfo_width() >= 880 else 1
        self._choice_columns = columns
        for column in range(2):
            self.btn_frame.grid_columnconfigure(
                column,
                weight=1 if column < columns else 0,
                uniform="btn" if column < columns else "",
            )
        for i, opt in enumerate(self._options):
            maker = self._make_skill_button if skill_mode else self._make_button
            maker(opt, lambda i=i: self._answer(i),
                  i // columns, i % columns, prefix=f"{i + 1}. ")
        if self._allow_cancel:
            n = len(self._options)
            self._make_button("0. 返回", lambda: self._answer(-1),
                              n // columns, n % columns)
        self.root.after_idle(self._resize_choice_area)

    def _answer(self, idx):
        if self.waiting != "choose":
            return
        self.waiting = None
        self._clear_buttons()
        self.hint_var.set("……")
        label = "返回" if idx < 0 else ui.choice_text(self._options[idx])
        self._flush_text([f"\n　▸ {label}\n"], tag="echo")
        self.ans_q.put(idx)

    def _continue(self):
        if self.waiting != "pause":
            return
        self.waiting = None
        self._clear_buttons()
        self.hint_var.set("……")
        self.ans_q.put(None)

    def _on_key(self, event):
        # 模态浮层 / 设置面板打开时吞掉快捷键，避免误选行动或误继续剧情。
        if self._modal_active or self._settings_open:
            return "break"
        if self.waiting == "pause" and event.keysym in ("Return", "space", "KP_Enter"):
            self._continue()
            return "break"
        elif self.waiting == "choose" and event.char.isdigit():
            n = int(event.char)
            if n == 0 and self._allow_cancel:
                self._answer(-1)
            elif 1 <= n <= len(self._options):
                self._answer(n - 1)

    def _on_modal_escape(self, _event=None):
        if self._settings_open:
            if callable(self._settings_close):
                self._settings_close()
            return "break"
        if not self._modal_active:
            return
        self._close_game_modal(self._modal_cancel_action or "ok")
        return "break"

    def _on_modal_return(self, _event=None):
        if self._settings_open:
            return "break"
        if not self._modal_active:
            return
        self._close_game_modal(self._modal_primary_action or "ok")
        return "break"

    def _toggle_fast(self):
        fast = bool(self.fast_var.get())
        ui.SLOW_PRINT = not fast
        self.prefs["fast_text"] = fast
        try:
            save_ui_prefs(self.prefs)
        except OSError:
            pass

    def _apply_runtime_prefs(self):
        """应用不依赖控件树的偏好（启动早期调用）。"""
        ui.SLOW_PRINT = not bool(self.prefs.get("fast_text"))
        scale = self.prefs.get("font_scale", "medium")
        if scale not in FONT_SCALE_PRESETS:
            scale = "medium"
            self.prefs["font_scale"] = scale
        self._set_global_fonts(scale)

    def _set_global_fonts(self, scale):
        """更新模块级字体常量，供后续新建控件读取。"""
        global LOG_FONT, UI_FONT, UI_BOLD, BTN_FONT
        preset = FONT_SCALE_PRESETS.get(scale, FONT_SCALE_PRESETS["medium"])
        LOG_FONT = ("SimSun", preset["log"])
        UI_FONT = ("Microsoft YaHei UI", preset["ui"])
        UI_BOLD = ("Microsoft YaHei UI", preset["ui"], "bold")
        BTN_FONT = ("Microsoft YaHei UI", preset["btn"])

    def _apply_font_prefs(self):
        """把当前字号档位应用到已存在的主界面控件。"""
        scale = self.prefs.get("font_scale", "medium")
        self._set_global_fonts(scale)
        if not hasattr(self, "text") or self.text is None:
            return
        try:
            self.text.configure(font=LOG_FONT)
            self.text.tag_configure(
                "echo",
                foreground=ACCENT,
                font=(LOG_FONT[0], LOG_FONT[1], "bold"),
            )
            if self.hint_label is not None:
                self.hint_label.configure(font=UI_BOLD)
            if self.fast_check is not None:
                self.fast_check.configure(font=UI_FONT)
            if self.settings_button is not None:
                self.settings_button.configure(font=UI_FONT)
            if self.collection_button is not None:
                self.collection_button.configure(font=UI_BOLD)
            if self.continue_button is not None and self.continue_button.winfo_exists():
                preset = FONT_SCALE_PRESETS.get(scale, FONT_SCALE_PRESETS["medium"])
                self.continue_button.configure(
                    font=("Microsoft YaHei UI", preset["continue"], "bold"),
                )
            # 选项区若正在展示，按新字号重建，避免新旧字号混用。
            if self.waiting == "choose" and self._options:
                self._show_choices()
            elif self.waiting == "pause":
                self._show_continue_prompt("(按回车继续)")
        except tk.TclError:
            pass

    def _apply_ui_prefs(self, prefs, *, persist=True):
        """合并并应用偏好；persist 时写入磁盘。"""
        merged = dict(self.prefs)
        merged.update(prefs or {})
        if merged.get("font_scale") not in FONT_SCALE_PRESETS:
            merged["font_scale"] = "medium"
        if merged.get("scroll_speed") not in SCROLL_SPEED_PRESETS:
            merged["scroll_speed"] = "normal"
        merged["fast_text"] = bool(merged.get("fast_text"))
        # 自动化环境保持快速文本，避免设置面板把冒烟测拖慢。
        if os.environ.get("NL_FAST") == "1":
            merged["fast_text"] = True
        self.prefs = merged
        ui.SLOW_PRINT = not merged["fast_text"]
        if hasattr(self, "fast_var") and self.fast_var is not None:
            self.fast_var.set(merged["fast_text"])
        self._apply_font_prefs()
        if persist:
            try:
                save_ui_prefs(self.prefs)
            except OSError as exc:
                self._modal_error(
                    title="设置未能保存",
                    message=f"界面偏好已生效，但写入磁盘失败。\n\n{exc}",
                    badge="设置",
                )

    def _open_settings(self):
        """商业风设置面板：字号 / 快速文本 / 剧情滚动速度。"""
        if self.closed or self._modal_active or self._settings_open:
            return
        self._settings_open = True

        draft = {
            "font_scale": self.prefs.get("font_scale", "medium"),
            "fast_text": bool(self.prefs.get("fast_text")),
            "scroll_speed": self.prefs.get("scroll_speed", "normal"),
        }

        backdrop = tk.Frame(self.root, bg=MODAL_BACKDROP)
        backdrop.place(x=0, y=0, relwidth=1, relheight=1)
        backdrop.lift()

        shell = tk.Frame(backdrop, bg=MODAL_BACKDROP)
        shell.place(relx=0.5, rely=0.5, anchor="center")
        outer = tk.Frame(shell, bg=ACCENT, padx=2, pady=2)
        outer.pack()
        card = tk.Frame(outer, bg=MODAL_CARD)
        card.pack()
        card.configure(highlightbackground=MODAL_CARD_EDGE, highlightthickness=1)

        header = tk.Frame(card, bg=MODAL_HEADER)
        header.pack(fill="x")
        tk.Label(
            header, text=" 设置 ", font=(UI_FONT[0], 8, "bold"),
            fg="#1a1208", bg=ACCENT, padx=8, pady=3,
        ).pack(side="left", padx=(16, 10), pady=14)
        tk.Label(
            header, text="界面与阅读", font=(UI_FONT[0], 13, "bold"),
            fg=FG, bg=MODAL_HEADER, anchor="w",
        ).pack(side="left", fill="x", expand=True, padx=(0, 16), pady=14)
        tk.Frame(card, bg=ACCENT, height=2).pack(fill="x")

        body = tk.Frame(card, bg=MODAL_CARD, padx=22, pady=16)
        body.pack(fill="both", expand=True)

        font_var = tk.StringVar(value=draft["font_scale"])
        scroll_var = tk.StringVar(value=draft["scroll_speed"])
        fast_var = tk.BooleanVar(value=draft["fast_text"])

        def section(title):
            tk.Label(
                body, text=title, font=UI_BOLD, fg=ACCENT, bg=MODAL_CARD, anchor="w",
            ).pack(fill="x", pady=(8, 4))

        def radio_row(variable, options):
            row = tk.Frame(body, bg=PANEL2, padx=10, pady=8)
            row.pack(fill="x", pady=(0, 6))
            for value, label in options:
                tk.Radiobutton(
                    row,
                    text=label,
                    variable=variable,
                    value=value,
                    font=UI_FONT,
                    fg=FG,
                    bg=PANEL2,
                    activebackground=PANEL2,
                    activeforeground=FG,
                    selectcolor=BTN_BG,
                    anchor="w",
                    indicatoron=True,
                    highlightthickness=0,
                ).pack(side="left", padx=(0, 18))

        section("剧情字号")
        radio_row(font_var, [
            (key, FONT_SCALE_PRESETS[key]["label"])
            for key in ("small", "medium", "large")
        ])
        tk.Label(
            body,
            text="影响剧情文本与行动按钮字号。侧栏部分标签会在重启后完全对齐。",
            font=(UI_FONT[0], 8), fg=DIM, bg=MODAL_CARD, anchor="w", wraplength=420,
            justify="left",
        ).pack(fill="x", pady=(0, 6))

        section("文本速度")
        fast_row = tk.Frame(body, bg=PANEL2, padx=10, pady=8)
        fast_row.pack(fill="x", pady=(0, 6))
        tk.Checkbutton(
            fast_row,
            text="⚡ 快速文本（关闭逐字打印）",
            variable=fast_var,
            font=UI_FONT,
            fg=FG,
            bg=PANEL2,
            activebackground=PANEL2,
            activeforeground=FG,
            selectcolor=BTN_BG,
            anchor="w",
        ).pack(side="left")
        if os.environ.get("NL_FAST") == "1":
            tk.Label(
                body,
                text="当前由环境变量 NL_FAST 强制快速模式（测试用）。",
                font=(UI_FONT[0], 8), fg=EXP_COL, bg=MODAL_CARD, anchor="w",
            ).pack(fill="x", pady=(0, 6))

        section("剧情自动滚动")
        radio_row(scroll_var, [
            (key, f"{SCROLL_SPEED_PRESETS[key]['label']}  ·  {SCROLL_SPEED_PRESETS[key]['hint']}")
            for key in ("slow", "normal", "fast")
        ])

        footer = tk.Frame(card, bg=MODAL_CARD)
        footer.pack(fill="x", padx=16, pady=(4, 16))
        tk.Label(
            footer, text="设置立即生效，并记住到下次启动",
            font=(UI_FONT[0], 8), fg=DIM, bg=MODAL_CARD, anchor="w",
        ).pack(side="left", padx=(4, 8))
        btn_row = tk.Frame(footer, bg=MODAL_CARD)
        btn_row.pack(side="right")

        def close_settings():
            self._settings_open = False
            self._settings_close = None
            try:
                backdrop.place_forget()
                backdrop.destroy()
            except tk.TclError:
                pass

        def apply_and_close():
            self._apply_ui_prefs(
                {
                    "font_scale": font_var.get(),
                    "fast_text": bool(fast_var.get()),
                    "scroll_speed": scroll_var.get(),
                },
                persist=True,
            )
            close_settings()

        def make_btn(parent, label, style, command):
            if style == "primary":
                bg, hover, fg = PRIMARY_BTN, PRIMARY_BTN_HOV, PRIMARY_BTN_FG
            else:
                bg, hover, fg = BTN_BG, BTN_HOV, FG
            button = tk.Button(
                parent, text=label, command=command, font=UI_BOLD,
                bg=bg, fg=fg, activebackground=hover, activeforeground=fg,
                relief="flat", padx=16, pady=8, cursor="hand2",
            )
            button.pack(side="left", padx=4)
            button.bind("<Enter>", lambda _e, t=button, c=hover: t.config(bg=c))
            button.bind("<Leave>", lambda _e, t=button, c=bg: t.config(bg=c))
            return button

        make_btn(btn_row, "取消", "secondary", close_settings)
        make_btn(btn_row, "保存并应用", "primary", apply_and_close)

        # 点遮罩空白处关闭；点卡片不关闭。
        backdrop.bind("<Button-1>", lambda _e: close_settings())
        for widget in (shell, outer, card, header, body, footer, btn_row):
            widget.bind("<Button-1>", lambda e: "break")
        self._settings_close = close_settings
        return backdrop

    def _open_collection(self):
        from tkinter import ttk

        sections = collection.collection_sections(self.state)
        window = tk.Toplevel(self.root)
        window.title("忍界收藏馆")
        window.geometry("820x620")
        window.minsize(620, 420)
        window.configure(bg=BG)
        window.asset_photos = []
        notebook = ttk.Notebook(window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        tab_names = []
        for name, entries in sections.items():
            frame = tk.Frame(notebook, bg=BG)
            notebook.add(frame, text=name)
            tab_names.append(name)
            text = tk.Text(
                frame,
                wrap="word",
                font=UI_FONT,
                bg=BG,
                fg=FG,
                relief="flat",
                padx=14,
                pady=12,
            )
            scrollbar = tk.Scrollbar(frame, command=text.yview)
            text.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            text.pack(side="left", fill="both", expand=True)
            text.insert("1.0", "\n\n".join(entries))
            text.configure(state="disabled")
        story_canvas = self._add_graph_tab(
            notebook,
            "剧情分支图",
            progression_graphs.story_graph(self.state),
            self._draw_story_graph,
        )
        romance_canvas = self._add_graph_tab(
            notebook,
            "恋爱线阶段图",
            progression_graphs.romance_graph(self.state),
            self._draw_romance_graph,
        )
        tab_names.extend(("剧情分支图", "恋爱线阶段图"))
        self._add_visual_collection_tabs(notebook, window, tab_names)
        window.collection_tabs = tab_names
        window.story_graph_canvas = story_canvas
        window.romance_graph_canvas = romance_canvas

    def _add_visual_collection_tabs(self, notebook, window, tab_names):
        skills = []
        for skill_id, name in icon_assets.SKILL_NAMES.items():
            skill = self.state.skills_db.get(skill_id, {})
            unlocked = skill_id in self.state.discovered_skills
            element = icon_assets.ELEMENT_NAMES.get(skill.get("element"), skill.get("element", ""))
            skills.append(
                {
                    "title": name if unlocked else "未知技能",
                    "subtitle": f"{element} · {skill.get('type', '')}" if unlocked else "尚未收录",
                    "unlocked": unlocked,
                    "path": icon_assets.icon_path("skills", skill_id),
                }
            )
        contracts = []
        for contract_id, name in icon_assets.CONTRACT_NAMES.items():
            contract = self.state.contracts.get(contract_id, {})
            unlocked = bool(contract.get("unlocked"))
            contracts.append(
                {
                    "title": name if unlocked else "未觉醒命线",
                    "subtitle": (
                        f"契约 Lv.{contract.get('contract_level', 0)} · {contract.get('support_skill_name', '')}"
                        if unlocked else "契约之树仍沉睡"
                    ),
                    "unlocked": unlocked,
                    "path": icon_assets.icon_path("contracts", contract_id),
                }
            )
        achievements = []
        for achievement_id, (name, description, _condition) in collection.ACHIEVEMENTS.items():
            unlocked = achievement_id in self.state.achievements
            achievements.append(
                {
                    "title": name,
                    "subtitle": description if unlocked else "尚未达成",
                    "unlocked": unlocked,
                    "path": icon_assets.icon_path("achievements", achievement_id),
                }
            )
        endings = []
        for ending_id, (name, _condition) in collection.ENDINGS.items():
            unlocked = ending_id in self.state.endings_seen
            endings.append(
                {
                    "title": name if unlocked else "未知结局",
                    "subtitle": "已收集" if unlocked else "命运尚未抵达",
                    "unlocked": unlocked,
                    "path": icon_assets.icon_path("endings", ending_id),
                }
            )
        for name, entries in (
            ("技能图标", skills),
            ("契约徽章", contracts),
            ("成就徽章", achievements),
            ("结局徽章", endings),
        ):
            self._add_asset_grid_tab(notebook, name, entries, window)
            tab_names.append(name)

    def _add_asset_grid_tab(self, notebook, name, entries, photo_owner):
        frame = tk.Frame(notebook, bg=BG)
        notebook.add(frame, text=name)
        canvas = tk.Canvas(frame, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        body = tk.Frame(canvas, bg=BG)
        body_window = canvas.create_window((0, 0), window=body, anchor="nw")
        body.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(body_window, width=event.width))
        canvas.bind("<MouseWheel>", lambda event: canvas.yview_scroll(int(-event.delta / 120), "units"))
        columns = 4
        for column in range(columns):
            body.grid_columnconfigure(column, weight=1, uniform="asset_card")
        for index, entry in enumerate(entries):
            row, column = divmod(index, columns)
            card = tk.Frame(body, bg=PANEL, highlightthickness=1, highlightbackground=PANEL2)
            card.grid(row=row, column=column, sticky="nsew", padx=6, pady=6)
            path = entry["path"]
            photo = self._load_path_photo(path, max_dim=68) if entry["unlocked"] else None
            if photo:
                photo_owner.asset_photos.append(photo)
                tk.Label(card, image=photo, bg=PANEL).pack(pady=(9, 4))
            else:
                tk.Label(
                    card,
                    text="？",
                    font=(UI_FONT[0], 24, "bold"),
                    fg="#4e5667",
                    bg=PANEL2,
                    width=4,
                    height=2,
                ).pack(pady=(9, 4))
            tk.Label(
                card,
                text=entry["title"],
                font=UI_BOLD,
                fg=FG if entry["unlocked"] else DIM,
                bg=PANEL,
                wraplength=150,
                justify="center",
            ).pack(fill="x", padx=6)
            tk.Label(
                card,
                text=entry["subtitle"],
                font=(UI_FONT[0], 8),
                fg=DIM,
                bg=PANEL,
                wraplength=150,
                justify="center",
            ).pack(fill="x", padx=6, pady=(3, 9))
        return canvas

    def _add_graph_tab(self, notebook, name, graph, renderer):
        frame = tk.Frame(notebook, bg=BG)
        notebook.add(frame, text=name)
        tk.Label(
            frame,
            text=graph["summary"],
            font=UI_BOLD,
            fg=ACCENT,
            bg=PANEL,
            anchor="w",
            padx=12,
            pady=8,
        ).pack(fill="x")
        detail_var = tk.StringVar(value="点击节点查看条件与当前存档结果。")
        tk.Label(
            frame,
            textvariable=detail_var,
            font=UI_FONT,
            fg=FG,
            bg=PANEL2,
            anchor="w",
            justify="left",
            wraplength=740,
            padx=12,
            pady=7,
        ).pack(side="bottom", fill="x")
        body = tk.Frame(frame, bg=BG)
        body.pack(fill="both", expand=True)
        canvas = tk.Canvas(body, bg=BG, highlightthickness=0)
        vbar = tk.Scrollbar(body, orient="vertical", command=canvas.yview)
        hbar = tk.Scrollbar(body, orient="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        vbar.pack(side="right", fill="y")
        hbar.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(scrollregion=(0, 0, graph["width"], graph["height"]))
        canvas.bind("<MouseWheel>", lambda event: canvas.yview_scroll(int(-event.delta / 120), "units"))
        renderer(canvas, graph, detail_var)
        return canvas

    def _graph_node(self, canvas, node, detail_var):
        x, y = node["x"], node["y"]
        width, height = node["width"], node["height"]
        fill, outline, status_label = GRAPH_STATUS_STYLE[node["status"]]
        tag = f"graph_node_{id(node)}"
        canvas.create_rectangle(
            x,
            y,
            x + width,
            y + height,
            fill=fill,
            outline=outline,
            width=2,
            tags=(tag,),
        )
        canvas.create_text(
            x + 10,
            y + 9,
            text=node["title"],
            fill=FG,
            font=UI_BOLD,
            anchor="nw",
            width=width - 20,
            tags=(tag,),
        )
        canvas.create_text(
            x + 10,
            y + 32,
            text=node["detail"],
            fill=DIM,
            font=(UI_FONT[0], 8),
            anchor="nw",
            width=width - 20,
            tags=(tag,),
        )
        canvas.create_text(
            x + width - 7,
            y + height - 5,
            text=status_label,
            fill=outline,
            font=(UI_FONT[0], 7, "bold"),
            anchor="se",
            tags=(tag,),
        )
        message = f"{node['title']}：{node['detail']}　[{status_label}]"
        canvas.tag_bind(tag, "<Button-1>", lambda _event, value=message: detail_var.set(value))
        canvas.tag_bind(tag, "<Enter>", lambda _event: canvas.configure(cursor="hand2"))
        canvas.tag_bind(tag, "<Leave>", lambda _event: canvas.configure(cursor=""))

    def _graph_edge(self, canvas, source, target, branched=False):
        source_center_y = source["y"] + source["height"] / 2
        target_center_y = target["y"] + target["height"] / 2
        _, color, _ = GRAPH_STATUS_STYLE[target["status"]]
        if branched:
            source_right = source["x"] + source["width"]
            fork_x = source_right + 18
            bus_y = min(source["y"], target["y"]) - 13
            target_top_x = target["x"] + target["width"] / 2
            canvas.create_line(
                source_right,
                source_center_y,
                fork_x,
                source_center_y,
                fork_x,
                bus_y,
                target_top_x,
                bus_y,
                target_top_x,
                target["y"],
                fill=color,
                width=2,
                arrow="last",
                arrowshape=(8, 10, 4),
            )
            return
        if target["x"] > source["x"]:
            start = (source["x"] + source["width"], source_center_y)
            end = (target["x"], target_center_y)
        else:
            start = (source["x"] + source["width"] / 2, source["y"] + source["height"])
            end = (target["x"] + target["width"] / 2, target["y"])
        canvas.create_line(*start, *end, fill=color, width=2, arrow="last", arrowshape=(8, 10, 4))

    def _draw_story_graph(self, canvas, graph, detail_var):
        nodes = {node["id"]: node for node in graph["nodes"]}
        for source_id, target_id in graph["edges"]:
            source, target = nodes[source_id], nodes[target_id]
            self._graph_edge(canvas, source, target, branched=target["x"] > source["x"])
        for node in graph["nodes"]:
            self._graph_node(canvas, node, detail_var)

    def _draw_romance_graph(self, canvas, graph, detail_var):
        stage_width, stage_height = 195, 76
        for row_index, row in enumerate(graph["rows"]):
            y = 35 + row_index * 145
            if row_index:
                canvas.create_line(20, y - 18, graph["width"] - 25, y - 18, fill=PANEL2)
            name = f"❀ {row['name']}" if row["is_lover"] else row["name"]
            canvas.create_text(28, y + 13, text=name, fill=FG, font=(UI_FONT[0], 13, "bold"), anchor="nw")
            canvas.create_text(
                28,
                y + 45,
                text=f"心动 {row['heart']}/100",
                fill="#e88cb0" if row["heart"] >= 50 else DIM,
                font=UI_FONT,
                anchor="nw",
            )
            canvas.create_rectangle(28, y + 69, 148, y + 79, fill=PANEL2, outline="")
            heart_width = int(120 * min(100, max(0, row["heart"])) / 100)
            if heart_width:
                canvas.create_rectangle(28, y + 69, 28 + heart_width, y + 79, fill="#e88cb0", outline="")
            previous = None
            for stage_index, stage in enumerate(row["stages"]):
                x = 180 + stage_index * 225
                node = {
                    "id": f"{row['id']}_{stage_index}",
                    "title": stage["title"],
                    "detail": stage["detail"],
                    "x": x,
                    "y": y,
                    "width": stage_width,
                    "height": stage_height,
                    "status": stage["status"],
                }
                if previous:
                    self._graph_edge(canvas, previous, node)
                self._graph_node(canvas, node, detail_var)
                previous = node

    # ── 状态边栏 ──────────────────────────────

    def _refresh_status(self):
        st = self.state
        p = st.player
        self.sv["head"].set(f"Lv.{p['level']}　漩涡鸣人")
        self.bar_hp.set(p["hp"], p["max_hp"], warn=p["hp"] < p["max_hp"] * 0.25)
        self.bar_ck.set(p["chakra"], p["max_chakra"])
        self.bar_xp.set(p["exp"], st.exp_to_next())

        # 四维：2×2 格子
        if self.stat_vars:
            self.stat_vars["attack"].set(str(p.get("attack", 0)))
            self.stat_vars["defense"].set(str(p.get("defense", 0)))
            self.stat_vars["speed"].set(str(p.get("speed", 0)))
            self.stat_vars["spirit"].set(str(p.get("spirit", 0)))
        # 兼容旧 StringVar（若仍有引用）
        if "stats" in self.sv:
            self.sv["stats"].set(
                f"攻 {p['attack']}  防 {p['defense']}  "
                f"速 {p['speed']}  精神 {p['spirit']}"
            )

        self.sv["fate"].set(f"{st.fate_points}")
        self.sv["backlash"].set(f"反噬 Lv.{st.backlash}　暴露 {st.exposure}")
        self.sv["flux"].set(f"{st.kyubi_flux}")

        reputation_rows = [
            (data["name"], str(st.faction_reputation[fid]))
            for fid, data in factions.FACTIONS.items()
            if data["unlock"](st)
        ]
        self._set_side_list("reputation", reputation_rows)
        if "reputation" in self.sv:
            self.sv["reputation"].set(
                "、".join(f"{name}{value}" for name, value in reputation_rows) or "(无)"
            )

        # 关系指标
        metrics = self.metric_rows
        if "trust" in metrics and "trust" in metrics["trust"]:
            metrics["trust"]["trust"].set(str(st.team7_trust))
        if "suspicion" in metrics:
            metrics["suspicion"]["kakashi"].set(str(st.kakashi_suspicion))
            metrics["suspicion"]["belonging"].set(str(st.belonging))
        sa, sk = st.relations["sasuke"], st.relations["sakura"]
        if "sasuke" in metrics:
            metrics["sasuke"]["trust"].set(str(sa["trust"]))
            metrics["sasuke"]["revenge"].set(str(sa["revenge"]))
            metrics["sasuke"]["curse"].set(str(sa["curse"]))
        if "sakura" in metrics:
            metrics["sakura"]["confidence"].set(str(sk["confidence"]))
            metrics["sakura"]["trust"].set(str(sk["trust"]))
        if "trust" in self.sv:
            self.sv["trust"].set(f"信任 {st.team7_trust}")
        if "suspicion" in self.sv:
            self.sv["suspicion"].set(
                f"卡卡西 {st.kakashi_suspicion}　归属 {st.belonging}"
            )
        if "sasuke" in self.sv:
            self.sv["sasuke"].set(
                f"信任 {sa['trust']}  复仇 {sa['revenge']}  咒印 {sa['curse']}"
            )
        if "sakura" in self.sv:
            self.sv["sakura"].set(
                f"自信 {sk['confidence']}  信任 {sk['trust']}"
            )

        contract_rows = [
            (contract["name"], f"Lv.{contract['contract_level']}")
            for contract in st.contracts.values()
            if contract.get("unlocked")
        ]
        self._set_side_list("contracts", contract_rows)
        if "contracts" in self.sv:
            self.sv["contracts"].set(
                "、".join(f"{name} {level}" for name, level in contract_rows) or "(尚无)"
            )

        item_rows = [
            (str(item_name), f"×{count}")
            for item_name, count in st.inventory.items()
            if count > 0
        ]
        self._set_side_list("items", item_rows)
        if "items" in self.sv:
            self.sv["items"].set(
                "、".join(f"{name}{value}" for name, value in item_rows) or "(空)"
            )

        self.sv["ryo"].set(f"{st.ryo}")
        loc = st.maps.get(st.location, {})
        self.sv["loc"].set(loc.get("name", st.location))
        if st.location != self._last_location:
            self._last_location = st.location
            self._set_visual(
                illustration_id=visual_assets.illustration_for_location(st.location)
            )
        self.sv["time"].set(time_system.time_label(st))
        tail = " (主线完结)" if st.flags.get("main_complete") else ""
        self.sv["chapter"].set(f"第 {st.chapter} 章{tail}")
        self.sv["party"].set(party.party_summary(st))

        party.normalize_progress(st)
        growth_rows = []
        for teammate_id in st.selected_party:
            progress = st.teammate_progress[teammate_id]
            route_name = next(
                (
                    route["name"]
                    for route in party.TEAMMATE_ROUTES[teammate_id]
                    if route["id"] == progress.get("route")
                ),
                "未定",
            )
            growth_rows.append((
                party.TEAMMATES[teammate_id][0],
                f"Lv.{progress['level']} · {route_name}",
            ))
        self._set_side_list("growth", growth_rows)
        if "growth" in self.sv:
            self.sv["growth"].set(
                "、".join(f"{name} {detail}" for name, detail in growth_rows) or "(无)"
            )

        skill_rows = []
        for skill_id in loadout.equipped_skill_ids(st):
            skill = st.skills_db.get(skill_id, {})
            skill_rows.append((
                skill.get("name", skill_id),
                f"威力{skill.get('power', '—')} · 查克拉{skill.get('chakra_cost', 0)}",
            ))
        self._set_side_list("loadout", skill_rows)
        if "loadout" in self.sv:
            self.sv["loadout"].set(loadout.summary(st))

        equipment.normalize_equipment(st)
        gear_rows = []
        for slot in equipment.SLOTS:
            item_id = st.equipped_gear.get(slot)
            label = (
                equipment.equipment_label(st, item_id)
                if item_id in equipment.CATALOG
                else "未装备"
            )
            gear_rows.append((equipment.SLOT_NAMES.get(slot, slot), label))
        self._set_side_list("gear", gear_rows)
        if "gear" in self.sv:
            self.sv["gear"].set(equipment.summary(st))

        cycle = f"新周目 +{st.new_game_plus}" if st.new_game_plus else "初周目"
        if st.challenge_modifiers:
            cycle += f" | {new_game_plus.modifier_summary(st)}"
        self.sv["cycle"].set(cycle)

    # ── 关闭处理 ──────────────────────────────

    def _on_close(self):
        if self.closed:
            return
        # 已在退出确认流程中再次点关闭：视为取消，避免重入。
        if self._modal_active:
            self._close_game_modal(self._modal_cancel_action or "no")
            return
        if not self.ended and not self._closing_confirmed:
            confirmed = self._modal_confirm(
                title="退出游戏",
                message=(
                    "确定要离开忍界旅程吗？\n\n"
                    "当前进度将自动保存到「存档 3」。\n"
                    "可随时从标题画面读档继续。"
                ),
                badge="退出",
                yes_label="退出并保存",
                no_label="继续游戏",
                danger=True,
            )
            if not confirmed:
                return
            self._closing_confirmed = True
            try:
                save.save_game(self.state, 3, silent=True)
            except save.SaveError as exc:
                self._closing_confirmed = False
                self._modal_error(
                    title="存档失败",
                    message=f"无法写入自动存档，游戏暂未退出。\n\n{exc}",
                    badge="存档",
                    ok_label="返回游戏",
                )
                return
        self._force_close()

    def _force_close(self):
        """真正销毁窗口；可从退出确认成功路径或游戏已结束时调用。"""
        if self.closed:
            return
        self.closed = True
        if self._modal_active:
            self._close_game_modal("ok")
        if self.waiting in ("choose", "pause"):
            self.ans_q.put(CLOSE_SIGNAL)
        self._restore_io()
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def run(self):
        self.root.mainloop()


def enable_hidpi():
    """Windows 高分屏下让文字清晰。"""
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


if __name__ == "__main__":
    enable_hidpi()
    NineLivesGUI().run()
