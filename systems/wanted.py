# -*- coding: utf-8 -*-
"""可重复挑战的通缉榜。"""
import random

from systems import battle, equipment, ui


TARGETS = (
    {
        "id": "forest_alpha", "name": "森林狼王", "enemy": "forest_wolf", "chapter": 1,
        "description": "异常凶猛的狼群首领，擅长流血与咆哮。",
        "affixes": ("swift", "berserk"), "fate": 1, "item": "军粮丸", "gear": "",
    },
    {
        "id": "rogue_hunter", "name": "越境猎忍", "enemy": "rogue_genin", "chapter": 2,
        "description": "专门猎杀下忍的越境忍者，装备精良。",
        "affixes": ("armored", "venomous"), "fate": 1, "item": "回复丹", "gear": "hunter_blade",
    },
    {
        "id": "serpent_king", "name": "死亡森林蛇王", "enemy": "giant_snake", "chapter": 3,
        "description": "盘踞第44演习场深处的巨蛇。",
        "affixes": ("regenerative", "venomous"), "fate": 2, "item": "查克拉丸", "gear": "serpent_guard",
    },
    {
        "id": "red_cloud_agent", "name": "赤云密使", "enemy": "akatsuki_pawn", "chapter": 8,
        "description": "掌握多种属性忍术的晓组织外围精英。",
        "affixes": ("chakra", "armored"), "fate": 2, "item": "回复丹", "gear": "",
    },
    {
        "id": "zetsu_commander", "name": "白绝残党指挥体", "enemy": "white_zetsu", "chapter": 10,
        "description": "战后仍在活动的高密度白绝融合体。",
        "affixes": ("regenerative", "armored", "berserk"), "fate": 3, "item": "查克拉丸",
        "gear": "war_emblem",
    },
)


def available_targets(state):
    return [target for target in TARGETS if state.chapter >= target["chapter"]]


def show_wanted_board(state):
    targets = available_targets(state)
    if not targets:
        ui.slow_print("当前没有适合你等级的通缉目标。")
        return
    while True:
        options = []
        for target in targets:
            clears = state.wanted_records.get(target["id"], 0)
            marker = "★首胜" if clears == 0 else f"已讨伐 {clears} 次"
            options.append(f"{target['name']} | {marker} | {target['description']}")
        index = ui.choose("木叶通缉榜：精英目标会携带特殊词缀", options, allow_cancel=True)
        if index < 0:
            return
        target = targets[index]
        clears = state.wanted_records.get(target["id"], 0)
        affix_count = min(len(target["affixes"]), 1 + state.new_game_plus)
        affixes = random.sample(list(target["affixes"]), affix_count)
        result = battle.battle(
            state,
            target["enemy"],
            special_rules={
                "no_escape": True,
                "elite_affixes": affixes,
                "break_multiplier": 1.15,
                "objective_text": f"讨伐通缉目标【{target['name']}】",
            },
            intro=target["description"],
        )
        if result != "win":
            ui.slow_print("通缉任务失败。目标已经撤离，休整后可以再次挑战。")
            return
        state.wanted_records[target["id"]] = clears + 1
        if clears == 0:
            state.gain_fate(target["fate"], "通缉榜首胜")
            state.add_item(target["item"], 1)
            if target["gear"]:
                equipment.grant(state, target["gear"])
            ui.slow_print("★ 首次讨伐奖励已经发放。")
        else:
            state.add_item(target["item"], 1)
            ui.slow_print(f"※ 重复讨伐奖励：【{target['item']}】×1。")
        return
