# -*- coding: utf-8 -*-
"""核心忍术的二选一强化分支。"""
from systems import ui


BRANCHES = {
    "basic_taijutsu": (
        {"id": "combo", "name": "连击架势", "description": "威力提高15%，破势效率提高25%",
         "mods": {"power_mult": 1.15, "break_mult": 1.25}},
        {"id": "breaker", "name": "破绽追击", "description": "命中提高10%，破势效率提高60%",
         "mods": {"accuracy_delta": 10, "break_mult": 1.6}},
    ),
    "shadow_clone": (
        {"id": "guardian", "name": "守护分身", "description": "影分身护卫持续更久，并额外提升防御",
         "mods": {"status_turns": 3, "self_bonus": "defense_up"}},
        {"id": "assault", "name": "爆发分身", "description": "改为影分身围攻，造成伤害并强化破势",
         "mods": {"power_set": 38, "effect_set": None, "chakra_delta": 5, "break_mult": 1.35}},
    ),
    "rasengan": (
        {"id": "pierce", "name": "贯穿型", "description": "威力提高25%，但破势效率略降",
         "mods": {"power_mult": 1.25, "break_mult": 0.8}},
        {"id": "impact", "name": "破势型", "description": "威力降低10%，破势效率提高100%",
         "mods": {"power_mult": 0.9, "break_mult": 2.0}},
    ),
    "rasenshuriken": (
        {"id": "storm", "name": "扩散风暴", "description": "命中提高10%，元素反应伤害提高50%",
         "mods": {"accuracy_delta": 10, "reaction_mult": 1.5}},
        {"id": "sever", "name": "经络切断", "description": "威力提高15%，精神动摇触发率提高",
         "mods": {"power_mult": 1.15, "effect_chance": 0.85}},
    ),
    "simple_seal_array": (
        {"id": "lasting", "name": "久缚封印", "description": "封印触发率提高，持续时间延长",
         "mods": {"effect_chance": 0.9, "status_turns": 4}},
        {"id": "drain", "name": "吸能封阵", "description": "封印同时额外削减45点查克拉",
         "mods": {"target_chakra_drain": 45}},
    ),
}


def normalize_upgrades(state):
    learned = set(state.player.get("skills", []))
    state.skill_upgrades = {
        skill_id: branch_id
        for skill_id, branch_id in state.skill_upgrades.items()
        if skill_id in learned and any(branch["id"] == branch_id for branch in BRANCHES.get(skill_id, ()))
    }
    return state.skill_upgrades


def _branch(skill_id, branch_id):
    return next((branch for branch in BRANCHES.get(skill_id, ()) if branch["id"] == branch_id), None)


def apply_upgrade(state, skill):
    """返回应用当前分支后的技能副本。"""
    branch = _branch(skill["id"], state.skill_upgrades.get(skill["id"]))
    if not branch:
        return dict(skill)
    upgraded = dict(skill)
    mods = branch["mods"]
    if "power_set" in mods:
        upgraded["power"] = mods["power_set"]
    upgraded["power"] = max(0, int(upgraded["power"] * mods.get("power_mult", 1.0)))
    upgraded["chakra_cost"] = max(0, upgraded["chakra_cost"] + mods.get("chakra_delta", 0))
    upgraded["accuracy"] = min(100, upgraded["accuracy"] + mods.get("accuracy_delta", 0))
    if "effect_set" in mods:
        upgraded["effect"] = mods["effect_set"]
    for key in (
        "break_mult", "reaction_mult", "effect_chance", "status_turns", "self_bonus",
        "target_chakra_drain",
    ):
        if key in mods:
            upgraded[f"_{key}"] = mods[key]
    upgraded["_upgrade_name"] = branch["name"]
    upgraded["description"] = f"{upgraded['description']} [{branch['name']}：{branch['description']}]"
    return upgraded


def summary(state):
    normalize_upgrades(state)
    names = []
    for skill_id, branch_id in state.skill_upgrades.items():
        if skill_id not in state.skills_db:
            continue
        branch = _branch(skill_id, branch_id)
        if branch:
            names.append(f"{state.skills_db[skill_id]['name']}·{branch['name']}")
    return "、".join(names) or "(尚未选择)"


def configure_mastery(state):
    normalize_upgrades(state)
    eligible = [skill_id for skill_id in state.player.get("skills", []) if skill_id in BRANCHES]
    if not eligible:
        ui.slow_print("尚未掌握可强化的核心忍术。")
        return
    while True:
        options = ["完成强化配置"]
        for skill_id in eligible:
            skill = state.skills_db[skill_id]
            branch = _branch(skill_id, state.skill_upgrades.get(skill_id))
            options.append(f"{skill['name']} | {branch['name'] if branch else '未选择分支'}")
        index = ui.choose("忍术强化：每项核心忍术选择一个分支，可随时调整", options)
        if index == 0:
            return
        skill_id = eligible[index - 1]
        branches = BRANCHES[skill_id]
        branch_index = ui.choose(
            f"强化【{state.skills_db[skill_id]['name']}】",
            [
                f"{'◉' if state.skill_upgrades.get(skill_id) == branch['id'] else '○'} "
                f"{branch['name']} - {branch['description']}"
                for branch in branches
            ],
            allow_cancel=True,
        )
        if branch_index >= 0:
            state.skill_upgrades[skill_id] = branches[branch_index]["id"]
            ui.slow_print(
                f"★ 【{state.skills_db[skill_id]['name']}】切换为【{branches[branch_index]['name']}】。"
            )
