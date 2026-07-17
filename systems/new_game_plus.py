# -*- coding: utf-8 -*-
"""新周目继承与挑战修正。"""
import copy

from systems import ui
from systems.state import GameState


MODIFIERS = {
    "veteran_enemies": ("强敌世界", "敌人生命与攻击额外提高20%"),
    "scarce_chakra": ("查克拉匮乏", "所有技能查克拉消耗提高20%"),
    "elite_world": ("精英横行", "探索时精英敌人出现率显著提高"),
    "fate_storm": ("命运风暴", "敌人攻击提高10%，但经验奖励提高25%"),
}


def modifier_summary(state):
    if not state.challenge_modifiers:
        return "无"
    return "、".join(MODIFIERS[modifier][0] for modifier in state.challenge_modifiers if modifier in MODIFIERS)


def _select_modifiers():
    selected = []
    ids = list(MODIFIERS)
    while True:
        options = [ui.Choice(
            "确认选择",
            ("actions", "new_cycle"),
            f"已选择 {len(selected)}/2",
        )]
        for modifier in ids:
            name, description = MODIFIERS[modifier]
            marker = "◉" if modifier in selected else "○"
            options.append(ui.Choice(
                f"{marker} {name}",
                ("actions", "new_cycle"),
                description,
            ))
        index = ui.choose("选择最多两个新周目修正", options)
        if index == 0:
            return selected
        modifier = ids[index - 1]
        if modifier in selected:
            selected.remove(modifier)
        elif len(selected) >= 2:
            ui.slow_print("最多同时启用两个挑战修正。")
        else:
            selected.append(modifier)


def start_new_cycle(state, modifiers):
    """重置剧情并继承收藏、成长、强化和装备。"""
    preserved = {
        "player": copy.deepcopy(state.player),
        "inventory": copy.deepcopy(state.inventory),
        "ryo": state.ryo,
        "equipped_skills": list(state.equipped_skills),
        "skill_upgrades": dict(state.skill_upgrades),
        "owned_equipment": list(state.owned_equipment),
        "equipped_gear": dict(state.equipped_gear),
        "equipment_quality": dict(state.equipment_quality),
        "equipment_enhancements": dict(state.equipment_enhancements),
        "equipment_affixes": dict(state.equipment_affixes),
        "wanted_records": dict(state.wanted_records),
        "teammate_progress": copy.deepcopy(state.teammate_progress),
        "combo_mastery": copy.deepcopy(state.combo_mastery),
        "faction_reputation": dict(state.faction_reputation),
        "faction_rank_rewards": list(state.faction_rank_rewards),
        "contract_trials": list(state.contract_trials),
        "research_done": list(state.research_done),
        "discovered_characters": list(state.discovered_characters),
        "discovered_enemies": list(state.discovered_enemies),
        "discovered_skills": list(state.discovered_skills),
        "achievements": list(state.achievements),
        "endings_seen": list(state.endings_seen),
        "new_game_plus": state.new_game_plus + 1,
        "challenge_modifiers": list(modifiers),
    }
    fresh = GameState()
    fresh.player = preserved["player"]
    fresh.player["hp"] = fresh.player["max_hp"]
    fresh.player["chakra"] = fresh.player["max_chakra"]
    for key, value in preserved.items():
        if key != "player":
            setattr(fresh, key, value)
    fresh.fate_points = min(10, 2 + fresh.new_game_plus)
    state.__dict__.clear()
    state.__dict__.update(fresh.__dict__)

    from scenes import chapter_01
    from systems import equipment, loadout, map as game_map, skill_mastery

    equipment.normalize_equipment(state)
    loadout.normalize_loadout(state)
    skill_mastery.normalize_upgrades(state)
    ui.banner(f"新周目 +{state.new_game_plus}")
    ui.slow_print(f"挑战修正：{modifier_summary(state)}")
    chapter_01.intro(state)
    game_map.show_location(state)


def menu(state):
    if not state.flags["war_done"]:
        ui.slow_print("新周目将在完成忍界大战后开放。")
        return False
    modifiers = _select_modifiers()
    names = "、".join(MODIFIERS[modifier][0] for modifier in modifiers) or "无修正"
    confirm = ui.choose(
        f"开始新周目 +{state.new_game_plus + 1}？\n继承等级、忍术、收藏、强化与装备；剧情和契约重置。\n修正：{names}",
        [
            ui.Choice("取消", ("actions", "retreat")),
            ui.Choice("开始新周目", ("actions", "new_cycle")),
        ],
    )
    if confirm == 1:
        start_new_cycle(state, modifiers)
        return True
    return False
