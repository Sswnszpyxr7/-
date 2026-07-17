# -*- coding: utf-8 -*-
"""技能装备栏。"""
from systems import ui

MAX_EQUIPPED_SKILLS = 6


def normalize_loadout(state):
    learned = [skill_id for skill_id in state.player.get("skills", []) if skill_id in state.skills_db]
    equipped = [skill_id for skill_id in state.equipped_skills if skill_id in learned]
    if not equipped:
        equipped = learned[:MAX_EQUIPPED_SKILLS]
    if "basic_taijutsu" in learned and "basic_taijutsu" not in equipped:
        if len(equipped) >= MAX_EQUIPPED_SKILLS:
            equipped[-1] = "basic_taijutsu"
        else:
            equipped.append("basic_taijutsu")
    state.equipped_skills = list(dict.fromkeys(equipped))[:MAX_EQUIPPED_SKILLS]
    return state.equipped_skills


def equipped_skill_ids(state):
    return normalize_loadout(state)


def summary(state):
    ids = equipped_skill_ids(state)
    return "、".join(state.skills_db[skill_id]["name"] for skill_id in ids) or "(未装备)"


def configure_loadout(state):
    """交互式选择最多六个战斗技能。"""
    normalize_loadout(state)
    learned = [skill_id for skill_id in state.player.get("skills", []) if skill_id in state.skills_db]
    while True:
        options = [f"完成配置 ({len(state.equipped_skills)}/{MAX_EQUIPPED_SKILLS})"]
        for skill_id in learned:
            skill = state.skills_db[skill_id]
            marker = "◉" if skill_id in state.equipped_skills else "○"
            options.append(
                f"{marker} {skill['name']} | 威力{skill['power']} 查克拉{skill['chakra_cost']}"
            )
        index = ui.choose("技能装备栏：选择技能进行装备/卸下", options)
        if index == 0:
            return
        skill_id = learned[index - 1]
        if skill_id in state.equipped_skills:
            if skill_id == "basic_taijutsu":
                ui.slow_print("基础体术是保底技能，不能卸下。")
            elif len(state.equipped_skills) <= 1:
                ui.slow_print("至少需要装备一个技能。")
            else:
                state.equipped_skills.remove(skill_id)
        elif len(state.equipped_skills) >= MAX_EQUIPPED_SKILLS:
            ui.slow_print(f"技能栏已满，最多装备 {MAX_EQUIPPED_SKILLS} 个技能。")
        else:
            state.equipped_skills.append(skill_id)
