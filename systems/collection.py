# -*- coding: utf-8 -*-
"""角色/敌人/技能图鉴、成就与结局收集。"""
from systems import ui


CHARACTERS = {
    "naruto": ("漩涡鸣人", "带着前世记忆重新踏上忍道的少年。"),
    "sasuke": ("宇智波佐助", "复仇与羁绊之间摇摆的宇智遗孤。"),
    "sakura": ("春野樱", "从普通少女成长为顶尖医疗忍者。"),
    "kakashi": ("旗木卡卡西", "第七班导师，在失去与守护之间前行。"),
    "kushina": ("漩涡玖辛奈", "鸣人的母亲，赤色命线的第一位守护者。"),
    "rin": ("野原琳", "一份本不该消失的温柔。"),
    "tsunade": ("纲手", "传说中的三忍与木叶第五代火影。"),
    "hinata": ("日向雏田", "安静外表下藏着从未动摇的勇气。"),
    "gaara": ("我爱罗", "从孤独的人柱力成长为被村子信赖的风影。"),
    "konan": ("小南", "将纸花与希望留给雨隐的天使。"),
    "obito": ("宇智波带土", "在理想、绝望与赎罪之间走了很远的人。"),
}


ACHIEVEMENTS = {
    "first_action": ("重生后的第一天", "推进一次世界时间", lambda s: s.actions_taken >= 1),
    "event_hunter": ("村子的倾听者", "触发 5 种地点见闻", lambda s: len(s.random_event_history) >= 5),
    "world_walker": ("足迹遍布", "触发 15 种地点见闻", lambda s: len(s.random_event_history) >= 15),
    "full_loadout": ("忍术师的工具箱", "装满六个技能槽", lambda s: len(s.equipped_skills) >= 6),
    "two_companions": ("我们一起上", "同时选择两名同行者", lambda s: len(s.selected_party) >= 2),
    "first_contract": ("命线之始", "缔结第一份契约", lambda s: any(c["unlocked"] for c in s.contracts.values())),
    "nine_contracts": ("九命一系", "解锁九名契约者", lambda s: sum(c["unlocked"] for c in s.contracts.values()) >= 9),
    "skill_scholar": ("忍术研究者", "掌握 10 个技能", lambda s: len(s.player.get("skills", [])) >= 10),
    "first_ending": ("命运的岔路", "收集第一个结局", lambda s: len(s.endings_seen) >= 1),
    "ending_collector": ("命运收藏家", "收集 5 个结局", lambda s: len(s.endings_seen) >= 5),
    "true_end": ("九命同归", "达成真结局", lambda s: s.flags["true_end"]),
}


ENDINGS = {
    "wave_canon": ("波之国·原定命运", lambda s: s.flags["wave_done"] and not s.flags["haku_alive"]),
    "wave_haku": ("波之国·白的新生", lambda s: s.flags["wave_done"] and s.flags["haku_alive"] and not s.flags["zabuza_alive"]),
    "wave_perfect": ("波之国·双生归途", lambda s: s.flags["wave_done"] and s.flags["haku_alive"] and s.flags["zabuza_alive"]),
    "sasuke_canon": ("终结谷·离村", lambda s: s.flags["sasuke_ending"] == 1),
    "sasuke_promise": ("终结谷·约定", lambda s: s.flags["sasuke_ending"] == 2),
    "sasuke_guarded": ("终结谷·监护下的木叶", lambda s: s.flags["sasuke_ending"] == 3),
    "sasuke_alliance": ("终结谷·改命同盟", lambda s: s.flags["sasuke_ending"] == 4),
    "war_standard": ("忍界大战·未尽的遗憾", lambda s: s.flags["war_done"] and not s.flags["true_end"]),
    "war_true": ("忍界大战·九命同归", lambda s: s.flags["true_end"]),
}


def _character_unlocked(state, character_id):
    if character_id in state.discovered_characters:
        return True
    flags = state.flags
    if character_id == "naruto":
        return True
    if character_id in ("sasuke", "sakura", "kakashi"):
        return flags["team7_assigned"]
    if character_id == "gaara":
        return flags["chunin_done"] or flags["gaara_redeemed"]
    if character_id == "obito":
        return flags["war_done"] or flags["obito_redeemed"]
    contract = state.contracts.get(character_id)
    return bool(contract and contract["unlocked"])


def sync_endings(state):
    for ending_id, (_, condition) in ENDINGS.items():
        if condition(state) and ending_id not in state.endings_seen:
            state.endings_seen.append(ending_id)


def evaluate_achievements(state, announce=False):
    sync_endings(state)
    for character_id in CHARACTERS:
        if _character_unlocked(state, character_id) and character_id not in state.discovered_characters:
            state.discovered_characters.append(character_id)
    for skill_id in state.player.get("skills", []):
        if skill_id in state.skills_db and skill_id not in state.discovered_skills:
            state.discovered_skills.append(skill_id)
    unlocked = []
    for achievement_id, (name, _, condition) in ACHIEVEMENTS.items():
        if achievement_id not in state.achievements and condition(state):
            state.achievements.append(achievement_id)
            unlocked.append(name)
    if announce:
        for name in unlocked:
            ui.slow_print(f"★ 成就解锁【{name}】")
    return unlocked


def refresh(state, announce=False):
    return evaluate_achievements(state, announce=announce)


def collection_sections(state):
    refresh(state)
    characters = []
    for character_id, (name, description) in CHARACTERS.items():
        unlocked = _character_unlocked(state, character_id)
        characters.append(f"{'[已解锁]' if unlocked else '[????]'} {name if unlocked else '未知角色'}"
                          + (f"\n  {description}" if unlocked else ""))
    characters.insert(0, f"进度: {len(state.discovered_characters)}/{len(CHARACTERS)}")

    enemies = []
    for enemy_id, enemy in state.enemies_db.items():
        unlocked = enemy_id in state.discovered_enemies
        enemies.append(f"{'[已遇见]' if unlocked else '[????]'} {enemy['name'] if unlocked else '未知敌人'}")
    enemies.insert(0, f"进度: {len(state.discovered_enemies)}/{len(state.enemies_db)}")

    known_skills = [skill_id for skill_id in state.discovered_skills if skill_id in state.skills_db]
    skills = [f"[已掌握] {state.skills_db[skill_id]['name']}" for skill_id in known_skills]
    skills.insert(0, f"已收录忍术: {len(known_skills)}")

    achievements = []
    for achievement_id, (name, description, _) in ACHIEVEMENTS.items():
        unlocked = achievement_id in state.achievements
        achievements.append(f"{'[★]' if unlocked else '[ ]'} {name}\n  {description}")
    achievements.insert(0, f"进度: {len(state.achievements)}/{len(ACHIEVEMENTS)}")

    endings = []
    for ending_id, (name, _) in ENDINGS.items():
        unlocked = ending_id in state.endings_seen
        endings.append(f"{'[已收集]' if unlocked else '[????]'} {name if unlocked else '未知结局'}")
    endings.insert(0, f"进度: {len(state.endings_seen)}/{len(ENDINGS)}")

    return {
        "角色图鉴": characters,
        "敌人图鉴": enemies,
        "忍术图鉴": skills or ["(尚未掌握忍术)"],
        "成就": achievements,
        "结局收集": endings,
    }


def show_collection(state):
    sections = collection_sections(state)
    names = list(sections)
    while True:
        index = ui.choose("收藏馆", names, allow_cancel=True)
        if index < 0:
            return
        name = names[index]
        ui.title(name)
        print("\n\n".join(sections[name]))
        ui.pause()
