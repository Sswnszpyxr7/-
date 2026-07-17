# -*- coding: utf-8 -*-
"""任务系统。"""
from systems import ui

TYPE_NAMES = {"main": "主线", "special": "特殊", "daily": "日常", "side": "支线"}


def quest_available(state, quest):
    if quest["completed"]:
        return False
    return all(state.quests.get(r, {}).get("completed") for r in quest["requirements"])


def show_quests(state):
    ui.title("任务列表")
    active = [q for q in state.quests.values() if not q["completed"] and quest_available(state, q)]
    done = [q for q in state.quests.values() if q["completed"]]
    for q in active:
        print(f"  ▶ {q['name']} ({TYPE_NAMES.get(q['type'], q['type'])}/{q['rank']})")
        for obj in q["objectives"]:
            print(f"      - {obj}")
    for q in done:
        print(f"  ✔ {q['name']} ({TYPE_NAMES.get(q['type'], q['type'])}/{q['rank']})")
    from systems import factions

    factions.refresh_board(state)
    dynamic = [q for q in state.dynamic_quests.values() if q.get("status") == "active"]
    for q in dynamic:
        faction = factions.FACTIONS[q["faction"]]["name"]
        print(f"  ◆ {q['name']} (动态/{faction})")
        print(f"      - {q['objective']} [{q['progress']}/{q['required']}]")
    faction_story = [q for q in factions.available_story_quests(state) if q["status"] == "active"]
    for q in faction_story:
        faction = factions.FACTIONS[q["faction"]]["name"]
        print(f"  ◈ {q['name']} (阵营故事/{faction})")
        print(f"      - {q['objective']} [{q['progress']}/{q['required']}]")
    if not active and not done and not dynamic and not faction_story:
        print("  暂无任务。")
    ui.line()
    ui.pause()


STAT_NAMES = {
    "chakra_control": "查克拉控制", "seal_art": "封印术", "attack": "攻击",
    "defense": "防御", "speed": "速度", "spirit": "精神", "sense": "感知",
}


def complete_quest(state, quest_id):
    q = state.quests.get(quest_id)
    if not q or q["completed"]:
        return
    q["completed"] = True
    ui.line()
    ui.slow_print(f"★ 任务完成:【{q['name']}】")
    r = q["rewards"]
    if r.get("exp"):
        state.gain_exp(r["exp"])
    if r.get("fate_points"):
        state.gain_fate(r["fate_points"], "任务奖励")
    if r.get("team7_trust"):
        state.add_trust(r["team7_trust"])
    for stat, cname in STAT_NAMES.items():
        if r.get(stat):
            state.player[stat] += r[stat]
            ui.slow_print(f"※ {cname} +{r[stat]}")
    if r.get("seal_art_exp"):
        state.player["seal_art"] += 3
        ui.slow_print("※ 封印术 +3 (封印深处的领悟)")
    if r.get("kushina_contract"):
        c = state.contracts["kushina"]
        c["fate_resonance"] = min(100, c["fate_resonance"] + r["kushina_contract"])
        ui.slow_print(f"※ 玖辛奈命运共鸣 +{r['kushina_contract']}")
    for key, val in r.items():
        if key.startswith("item_"):
            state.add_item(key[5:], val)
    ui.line()
