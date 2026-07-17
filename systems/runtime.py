# -*- coding: utf-8 -*-
"""终端与 GUI 共用的游戏运行流程。"""
from scenes import chapter_01
from systems import map as game_map
from systems import save, ui
from systems.state import GameState
from systems.validation import validate_game_state


PROGRESS_HINTS = (
    (lambda state: state.flags.get("war_done"), "疾风传已全部完结——自由模式:修满九命契约、重游忍界、备战前线余孽。"),
    (lambda state: state.flags.get("pain_done"), "前往【木叶大门】响应五影会谈召集,直面第四次忍界大战。"),
    (lambda state: state.flags.get("sage_training_done"), "回鸣人家就寝——雨云正在逼近木叶,佩恩要来了。"),
    (lambda state: state.flags.get("akatsuki_done"), "前往【妙木山】修行仙术;医院里静音的账房也值得一去。"),
    (lambda state: state.flags.get("kazekage_done"), "去【火影办公室】接十班的紧急任务,直面晓之阴影。"),
    (lambda state: state.flags.get("shippuden_started"), "前往【砂隐村】驰援——风影我爱罗被「晓」带走了。"),
    (lambda state: state.flags.get("main_complete"), "第一部完结。前往【木叶大门】与自来也踏上三年修行,开启疾风传。"),
    (lambda state: state.chapter >= 6, "终章在即:化解佐助的心结后,回鸣人家就寝,直面命运的岔路口。"),
    (lambda state: state.chapter >= 5, "前往【木叶大门】,与自来也一同踏上寻找纲手之旅。"),
    (lambda state: state.chapter >= 3, "去【火影办公室】报名中忍考试;医院与族地也有新剧情。"),
    (lambda state: state.chapter >= 2, "去【火影办公室】接取护送任务,开启波之国篇 (建议 Lv.4+)。"),
    (lambda state: not state.flags.get("team7_assigned"), "移动到「忍者学校」开始分班剧情。"),
    (lambda state: not state.flags.get("bell_test_completed"), "与佐助小樱对话后,去第七训练场进行铃铛测试。"),
)


def title_screen():
    print()
    ui.banner("九 命 一 系\n~ 鸣人重生录 ~\n\n文字冒险 RPG · 个人自用版")


def chapter_hint(state):
    """读档后的进度提示。"""
    for predicate, hint in PROGRESS_HINTS:
        if predicate(state):
            return hint
    return "回鸣人家睡觉,触发桃源觉醒。"


def prepare_game(state=None):
    """创建/验证状态，并完成新游戏或读档流程。"""
    state = state or GameState()
    save.load_profile(state)
    validate_game_state(state)
    title_screen()

    has_save = any(description for _, description in save.list_slots())
    options = ["新的旅程"] + (["继续旅程 (读档)"] if has_save else [])
    choice = ui.choose("", options)
    if choice == 1:
        if not save.load_menu(state):
            chapter_01.intro(state)
        ui.slow_print(f"\n(提示: {chapter_hint(state)})")
    else:
        chapter_01.intro(state)
        ui.slow_print("\n(提示: 移动到「忍者学校」开始分班剧情。)")
    game_map.show_location(state)
    return state


def run_game(state=None, handle_keyboard_interrupt=False):
    """运行共享的完整游戏流程，返回最终状态。"""
    state = prepare_game(state)
    running = True
    while running:
        try:
            running = game_map.explore_menu(state)
        except KeyboardInterrupt:
            if not handle_keyboard_interrupt:
                raise
            print()
            choice = ui.choose("要退出游戏吗?", ["继续游戏", "保存并退出"])
            if choice == 1:
                break

    try:
        save.save_game(state, 3, silent=True)
        ui.slow_print("(已自动保存到存档 3。)")
    except save.SaveError as exc:
        ui.slow_print(f"(自动存档失败: {exc})")
    ui.slow_print("下次再见,忍道之路仍在继续——")
    return state
