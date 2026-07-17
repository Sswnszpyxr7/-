# -*- coding: utf-8 -*-
"""自由队伍选择与队友协战数据。"""
from systems import ui

MAX_PARTY_SIZE = 2
MAX_TEAMMATE_LEVEL = 20

TEAMMATES = {
    "sasuke": ("宇智波佐助", "lightning", "以千鸟突入敌阵", False),
    "sakura": ("春野樱", "taijutsu", "以怪力重拳轰击", True),
    "kakashi": ("旗木卡卡西", "lightning", "以雷切精准突袭", False),
    "hinata": ("日向雏田", "taijutsu", "以柔拳封锁经络", True),
    "gaara": ("我爱罗", "earth", "揀起沙浪压制敌人", False),
    "tsunade": ("纲手", "taijutsu", "以怪力砸裂地面", True),
    "konan": ("小南", "wind", "操纵纸翼切开敌阵", False),
    "obito": ("宇智波带土", "fire", "从神威空间发起奇袭", False),
}

TEAMMATE_ROUTES = {
    "sasuke": (
        {"id": "storm", "name": "雷火强袭", "description": "提高攻击和破势，奥义为麒麟落雷",
         "power_mult": 1.18, "act_bonus": 0.03, "ability": "damage_break", "ability_name": "麒麟·落雷"},
        {"id": "sharingan", "name": "写轮眼控场", "description": "提高出手率，奥义可封印敌方行动",
         "power_mult": 1.02, "act_bonus": 0.08, "ability": "seal", "ability_name": "幻术·写轮眼"},
    ),
    "sakura": (
        {"id": "strength", "name": "百豪怪力", "description": "大幅提高伤害，奥义重创破势",
         "power_mult": 1.25, "act_bonus": 0.02, "ability": "damage_break", "ability_name": "樱花冲·地裂"},
        {"id": "medic", "name": "战地医疗", "description": "强化治疗判断，奥义群体回春",
         "power_mult": 0.92, "act_bonus": 0.05, "can_heal": True, "ability": "heal", "ability_name": "掌仙术·回春"},
    ),
    "kakashi": (
        {"id": "raikiri", "name": "雷切处决", "description": "高伤害处决路线，擅长击破残血目标",
         "power_mult": 1.22, "act_bonus": 0.03, "ability": "execute", "ability_name": "雷切·双穿光"},
        {"id": "tactician", "name": "写轮眼军师", "description": "提高行动率，奥义打断并封印敌人",
         "power_mult": 0.98, "act_bonus": 0.1, "ability": "seal", "ability_name": "写轮眼·战术复制"},
    ),
    "hinata": (
        {"id": "lion", "name": "双狮点穴", "description": "削减敌人查克拉并破坏经络",
         "power_mult": 1.12, "act_bonus": 0.05, "ability": "chakra_drain", "ability_name": "柔步双狮拳"},
        {"id": "guardian", "name": "白眼守护", "description": "侦察危险并治疗掩护队伍",
         "power_mult": 0.9, "act_bonus": 0.08, "can_heal": True, "ability": "guard", "ability_name": "八卦·守护领域"},
    ),
    "gaara": (
        {"id": "coffin", "name": "砂瀑压制", "description": "强化群体压制和破势",
         "power_mult": 1.2, "act_bonus": 0.02, "ability": "damage_break", "ability_name": "砂瀑大葬"},
        {"id": "shield", "name": "绝对防御", "description": "主动为鸣人构筑砂之护盾",
         "power_mult": 0.94, "act_bonus": 0.06, "ability": "guard", "ability_name": "砂之绝对防御"},
    ),
    "tsunade": (
        {"id": "heaven_kick", "name": "怪力破阵", "description": "正面击碎敌方架势",
         "power_mult": 1.28, "act_bonus": 0.01, "ability": "damage_break", "ability_name": "痛天脚·崩岳"},
        {"id": "creation", "name": "创造再生", "description": "强化治疗并提供一次濒死保护",
         "power_mult": 0.9, "act_bonus": 0.05, "can_heal": True, "ability": "revive", "ability_name": "忍法·创造再生"},
    ),
    "konan": (
        {"id": "shikigami", "name": "式纸之舞", "description": "纸海切割并封锁敌人",
         "power_mult": 1.15, "act_bonus": 0.06, "ability": "seal", "ability_name": "式纸之舞·白牢"},
        {"id": "angel", "name": "天使庇护", "description": "纸翼为全队治疗并减伤",
         "power_mult": 0.92, "act_bonus": 0.08, "can_heal": True, "ability": "guard", "ability_name": "天使纸翼"},
    ),
    "obito": (
        {"id": "kamui", "name": "神威奇袭", "description": "无视部分防御发动空间突袭",
         "power_mult": 1.2, "act_bonus": 0.07, "ability": "execute", "ability_name": "神威·空间断层"},
        {"id": "redemption", "name": "赎罪守护", "description": "以神威转移伤害并恢复队伍",
         "power_mult": 0.95, "act_bonus": 0.08, "can_heal": True, "ability": "guard", "ability_name": "神威·彼岸守护"},
    ),
}

BOND_EVENTS = {
    "sasuke": ("佐助第一次主动说：下一次任务，算我一个。", "写轮眼不再只盯着仇人，也开始寻找你的破绽。", "终结谷的风里，佐助把后背完整交给了你。"),
    "sakura": ("小樱把你的名字写进了优先救治名单。", "她不再等待谁保护，而是与你并肩站上最前排。", "第七班的医疗卷轴上，多了一句：谁都不许少。"),
    "kakashi": ("卡卡西把亲热天堂合上，认真看完了你的训练。", "他开始在战术图上把你标成可以独当一面的箭头。", "老师与学生的界线淡了，你们成为能托付性命的同僚。"),
    "hinata": ("雏田第一次没有跟在身后，而是走在你身边。", "白眼的视野里，你的每一个死角都有她守着。", "她握住你的手：这一次，我们一起面对所有目光。"),
    "gaara": ("我爱罗寄来第一封没有公文格式的短信。", "沙子会在你遇险前自行抬起，仿佛记住了你的查克拉。", "两位人柱力不再谈孤独，只谈下一代会看见怎样的世界。"),
    "tsunade": ("纲手把一张赌桌筹码塞给你：活着回来再还。", "她开始用下一任火影的标准批评你，也用家人的方式替你疗伤。", "百豪印的生命力跨过命线：老娘准你输，没准你死。"),
    "konan": ("一只纸鹤每天准时送来雨隐的晴雨。", "千万张纸记住了你的查克拉，不会再误伤你的影分身。", "小南把最后一朵只属于弥彦的纸花，也分给了你一半。"),
    "obito": ("带土别扭地纠正了你一次神威落点。", "他开始用自己的眼睛守望现实，而不是寻找梦境。", "神威空间里出现一扇回桃源的门，那是他给自己留下的归路。"),
}

BOND_THRESHOLDS = (10, 30, 60)


def _is_available(state, teammate_id):
    flags = state.flags
    if teammate_id == "sasuke":
        return flags["team7_assigned"] and (
            not flags["sasuke_arc_done"] or flags["sasuke_ending"] >= 3 or flags["war_done"]
        )
    if teammate_id == "sakura":
        return flags["team7_assigned"]
    if teammate_id == "kakashi":
        return flags["bell_test_completed"]
    if teammate_id == "hinata":
        return flags["chunin_done"]
    if teammate_id == "gaara":
        return flags["gaara_redeemed"]
    if teammate_id == "tsunade":
        return flags["tsunade_returned"]
    if teammate_id == "konan":
        return flags["konan_contracted"]
    if teammate_id == "obito":
        return flags["obito_redeemed"]
    return False


def available_teammates(state):
    return [teammate_id for teammate_id in TEAMMATES if _is_available(state, teammate_id)]


def normalize_party(state):
    available = set(available_teammates(state))
    state.selected_party = [teammate_id for teammate_id in state.selected_party if teammate_id in available][
        :MAX_PARTY_SIZE
    ]
    return state.selected_party


def _default_progress(state):
    return {"level": max(1, min(MAX_TEAMMATE_LEVEL, state.player["level"] - 2)), "exp": 0, "bond": 0}


def normalize_progress(state):
    """补齐并清洗队友成长数据，兼容没有该字段的旧存档。"""
    for teammate_id in TEAMMATES:
        saved = state.teammate_progress.get(teammate_id)
        if not isinstance(saved, dict):
            saved = _default_progress(state)
            state.teammate_progress[teammate_id] = saved
        saved["level"] = max(1, min(MAX_TEAMMATE_LEVEL, int(saved.get("level", 1))))
        saved["exp"] = max(0, int(saved.get("exp", 0)))
        saved["bond"] = max(0, min(100, int(saved.get("bond", 0))))
        routes = {route["id"] for route in TEAMMATE_ROUTES[teammate_id]}
        saved["route"] = saved.get("route", "") if saved.get("route") in routes else ""
        saved["milestones"] = [
            threshold for threshold in saved.get("milestones", [])
            if threshold in BOND_THRESHOLDS
        ]
    valid_combos = {}
    for combo_id, saved in state.combo_mastery.items():
        if not isinstance(saved, dict):
            continue
        uses = max(0, int(saved.get("uses", saved.get("exp", 0))))
        valid_combos[combo_id] = {"uses": uses, "level": combo_level_for_uses(uses)}
    state.combo_mastery = valid_combos
    return state.teammate_progress


def exp_to_next(level):
    return 45 + level * 25


def gain_teammate_exp(state, teammate_ids, amount, bond=1):
    """给予实际出战队友经验，返回发生升级的队友 id。"""
    normalize_progress(state)
    leveled = []
    for teammate_id in dict.fromkeys(teammate_ids):
        if teammate_id not in TEAMMATES:
            continue
        progress = state.teammate_progress[teammate_id]
        if progress["level"] < MAX_TEAMMATE_LEVEL:
            progress["exp"] += max(0, int(amount))
        progress["bond"] = min(100, progress["bond"] + max(0, int(bond)))
        for event_index, threshold in enumerate(BOND_THRESHOLDS):
            if progress["bond"] >= threshold and threshold not in progress["milestones"]:
                progress["milestones"].append(threshold)
                ui.title(f"队友羁绊：{TEAMMATES[teammate_id][0]} · {threshold}")
                ui.story(BOND_EVENTS[teammate_id][event_index])
        while progress["level"] < MAX_TEAMMATE_LEVEL and progress["exp"] >= exp_to_next(progress["level"]):
            progress["exp"] -= exp_to_next(progress["level"])
            progress["level"] += 1
            leveled.append(teammate_id)
            ui.slow_print(
                f"★ 队友成长！{TEAMMATES[teammate_id][0]}达到 Lv.{progress['level']}。"
            )
        if progress["level"] >= MAX_TEAMMATE_LEVEL:
            progress["exp"] = 0
    return leveled


def combo_level_for_uses(uses):
    if uses >= 8:
        return 3
    if uses >= 3:
        return 2
    return 1


def combo_stats(state, combo_id, base_cost):
    """联合技熟练度修正：升阶后减耗，并提升伤害/治疗/持续时间。"""
    normalize_progress(state)
    data = state.combo_mastery.setdefault(combo_id, {"uses": 0, "level": 1})
    level = combo_level_for_uses(data["uses"])
    data["level"] = level
    return {
        "level": level,
        "cost": max(0, int(base_cost) - (level - 1) * 5),
        "power_mult": 1.0 + (level - 1) * 0.18,
        "heal_mult": 1.0 + (level - 1) * 0.15,
        "bonus_turns": level - 1,
    }


def gain_combo_mastery(state, combo_id):
    normalize_progress(state)
    data = state.combo_mastery.setdefault(combo_id, {"uses": 0, "level": 1})
    old_level = combo_level_for_uses(data["uses"])
    data["uses"] += 1
    data["level"] = combo_level_for_uses(data["uses"])
    if data["level"] > old_level:
        ui.slow_print(f"★ 联合技强化！熟练度提升至 {data['level']} 阶。")
    return data["level"]


def party_summary(state):
    normalize_party(state)
    return "、".join(TEAMMATES[teammate_id][0] for teammate_id in state.selected_party) or "(单独行动)"


def _route(teammate_id, route_id):
    return next(
        (route for route in TEAMMATE_ROUTES[teammate_id] if route["id"] == route_id),
        None,
    )


def growth_menu(state):
    available = available_teammates(state)
    normalize_progress(state)
    if not available:
        ui.slow_print("当前还没有可以培养的队友。")
        return
    while True:
        options = [ui.Choice("返回", ("actions", "retreat"))]
        for teammate_id in available:
            progress = state.teammate_progress[teammate_id]
            route = _route(teammate_id, progress["route"])
            options.append(ui.Choice(
                f"{TEAMMATES[teammate_id][0]} Lv.{progress['level']}",
                ("portraits", teammate_id),
                f"羁绊 {progress['bond']} · {route['name'] if route else '未选择路线'}",
            ))
        index = ui.choose("队友培养：选择成长路线（可在非战斗时调整）", options)
        if index == 0:
            return
        teammate_id = available[index - 1]
        routes = TEAMMATE_ROUTES[teammate_id]
        route_index = ui.choose(
            f"{TEAMMATES[teammate_id][0]}的成长路线",
            [
                ui.Choice(route["name"], ("portraits", teammate_id), route["description"])
                for route in routes
            ],
            allow_cancel=True,
        )
        if route_index >= 0:
            state.teammate_progress[teammate_id]["route"] = routes[route_index]["id"]
            ui.slow_print(
                f"★ {TEAMMATES[teammate_id][0]}选择路线【{routes[route_index]['name']}】。"
            )


def configure_party(state):
    available = available_teammates(state)
    normalize_party(state)
    if not available:
        ui.slow_print("当前还没有可自由邀请的队友。")
        return
    while True:
        options = [ui.Choice(
            "完成组队",
            ("actions", "ally_order"),
            f"已选择 {len(state.selected_party)}/{MAX_PARTY_SIZE}",
        )]
        for teammate_id in available:
            marker = "◉" if teammate_id in state.selected_party else "○"
            normalize_progress(state)
            progress = state.teammate_progress[teammate_id]
            options.append(ui.Choice(
                f"{marker} {TEAMMATES[teammate_id][0]}",
                ("portraits", teammate_id),
                f"Lv.{progress['level']} · 羁绊 {progress['bond']}",
            ))
        index = ui.choose("选择一至两名同行者", options)
        if index == 0:
            return
        teammate_id = available[index - 1]
        if teammate_id in state.selected_party:
            state.selected_party.remove(teammate_id)
        elif len(state.selected_party) >= MAX_PARTY_SIZE:
            ui.slow_print("队伍已满，最多选择两名队友。")
        else:
            state.selected_party.append(teammate_id)


def combat_allies(state):
    normalize_party(state)
    normalize_progress(state)
    result = []
    for teammate_id in state.selected_party:
        name, element, move, can_heal = TEAMMATES[teammate_id]
        progress = state.teammate_progress[teammate_id]
        level = progress["level"]
        bond_bonus = progress["bond"] // 10
        route = _route(teammate_id, progress["route"])
        power_mult = route.get("power_mult", 1.0) if route else 1.0
        act_bonus = route.get("act_bonus", 0.0) if route else 0.0
        result.append(
            {
                "id": f"party_{teammate_id}",
                "teammate_id": teammate_id,
                "name": name,
                "power": int((20 + level * 3 + bond_bonus) * power_mult),
                "element": element,
                "move": move,
                "can_heal": route.get("can_heal", can_heal) if route else can_heal,
                "act_rate": min(
                    0.98, 0.72 + level * 0.008 + progress["bond"] * 0.001 + act_bonus
                ),
                "route": route,
            }
        )
    return result


def active_ability_available(allies, log):
    used = log.setdefault("ally_abilities_used", set())
    return any(ally.get("teammate_id") and ally.get("route") and ally["teammate_id"] not in used
               for ally in allies)


def use_active_ability(state, player, enemy, log, allies):
    """发动一次所选队友路线奥义；每名队友每场战斗限一次。"""
    from systems import battle

    used = log.setdefault("ally_abilities_used", set())
    candidates = [
        ally for ally in allies
        if ally.get("teammate_id") and ally.get("route") and ally["teammate_id"] not in used
    ]
    if not candidates:
        ui.slow_print("当前队伍没有尚可发动的队友奥义。")
        return False
    index = ui.choose(
        "发动哪一位队友的路线奥义?",
        [f"{ally['name']}【{ally['route']['ability_name']}】" for ally in candidates],
        allow_cancel=True,
    )
    if index < 0:
        return False
    ally = candidates[index]
    route = ally["route"]
    effect = route["ability"]
    progress = state.teammate_progress[ally["teammate_id"]]
    strength = 1.0 + progress["bond"] / 200
    ui.slow_print(f"⇒ {ally['name']}发动奥义【{route['ability_name']}】！")
    if effect in ("damage_break", "execute", "seal", "chakra_drain"):
        multiplier = 2.0 if effect != "execute" else (2.8 if enemy["hp"] < enemy["max_hp"] * 0.4 else 2.2)
        damage = max(1, int(ally["power"] * multiplier * strength - enemy["defense"] * 0.35))
        enemy["hp"] -= damage
        ui.slow_print(f"  对 {enemy['name']}造成 {damage} 点伤害！")
        if effect == "damage_break":
            battle._apply_break(enemy, max(25, damage // 2), log, route["ability_name"])
        elif effect == "seal":
            battle.add_status(enemy, "sealed", 2)
        elif effect == "chakra_drain":
            drain = min(enemy["chakra"], 45 + progress["level"] * 2)
            enemy["chakra"] -= drain
            battle.add_status(enemy, "chakra_disorder", 2)
            ui.slow_print(f"  敌人查克拉流失 {drain} 点。")
    elif effect == "heal":
        healing = int(player["max_hp"] * min(0.65, 0.35 + progress["bond"] / 300))
        player["hp"] = min(player["max_hp"], player["hp"] + healing)
        player["status"] = [status for status in player.get("status", [])
                            if status["id"] not in ("poison", "burn", "bleed")]
        ui.slow_print(f"  恢复 {healing} 点生命并解除持续伤害。")
    elif effect == "guard":
        battle.add_status(player, "defense_up", 3)
        battle.add_status(player, "evade_up", 2)
        healing = int(player["max_hp"] * 0.18 * strength)
        player["hp"] = min(player["max_hp"], player["hp"] + healing)
        ui.slow_print(f"  构筑守护领域并恢复 {healing} 点生命。")
    elif effect == "revive":
        player["hp"] = min(player["max_hp"], player["hp"] + int(player["max_hp"] * 0.5))
        player["status"] = []
        log["undying"] = True
        ui.slow_print("  生命大幅恢复、异常全消，并获得一次濒死保护。")
    used.add(ally["teammate_id"])
    return True


def merge_allies(story_allies, selected_allies):
    result = list(story_allies)
    names = {ally.get("name") for ally in result}
    for ally in selected_allies:
        if ally.get("name") not in names:
            result.append(ally)
            names.add(ally.get("name"))
    return result
