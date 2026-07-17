# -*- coding: utf-8 -*-
"""回合制战斗系统：属性克制、状态异常、影分身、队友协战、契约支援与联合技。"""
import copy
import random

from systems import collection, crafting, equipment, factions, loadout, party, skill_mastery, ui

# 属性克制表: 攻击属性 -> {被攻击属性: 倍率}
TYPE_CHART = {
    "fire":     {"wind": 1.5, "wood": 1.5, "water": 0.5, "earth": 0.5},
    "wind":     {"lightning": 1.5, "fire": 0.5},
    "lightning": {"water": 1.5, "earth": 1.5, "wind": 0.5},
    "water":    {"fire": 1.5, "earth": 1.5, "lightning": 0.5},
    "earth":    {"lightning": 1.5, "fire": 1.5, "water": 0.5},
    "wood":     {"water": 1.5, "earth": 1.5, "fire": 0.5, "lightning": 0.5},
    "yin":      {"yang": 0.5},
    "yang":     {"yin": 0.5},
    "seal":     {"tailed_beast": 2.0, "taijutsu": 0.5},
    "medical":  {},
    "taijutsu": {"genjutsu": 1.5, "seal": 0.5},
    "genjutsu": {"taijutsu": 1.5},
    "tailed_beast": {"seal": 0.5},
}

STATUS_NAMES = {
    "burn": "灼烧", "paralyze": "麻痹", "poison": "中毒", "confuse": "混乱",
    "bleed": "流血", "spirit_shake": "精神动摇", "defense_up": "防御提升",
    "evade_up": "闪避提升", "clone_guard": "影分身护卫", "sealed": "封印",
    "cloak": "九尾外衣", "attack_up": "攻击提升", "nine_shield": "九命守护",
    "fear": "恐惧", "chakra_disorder": "查克拉紊乱",
    "wet": "湿润",
}

ALLY_ORDER_NAMES = {
    "balanced": "均衡协战",
    "focus": "集中攻击",
    "guard": "掩护防御",
    "disrupt": "破势牵制",
}

POSITION_NAMES = {"front": "前排", "mid": "中排", "rear": "后排"}

ACTION_ASSETS = (
    ("忍术/体术", "attack"),
    ("队友指令", "ally_order"),
    ("队友奥义", "ally_ultimate"),
    ("调整站位", "position"),
    ("防御/反击", "guard"),
    ("道具", "item"),
    ("契约支援", "contract"),
    ("逃跑", "retreat"),
)


def _action_choice(label):
    if isinstance(label, ui.Choice):
        return label
    asset_id = next((asset for prefix, asset in ACTION_ASSETS if label.startswith(prefix)), None)
    return ui.Choice(label, ("actions", asset_id)) if asset_id else ui.Choice(label)

ENVIRONMENTS = {
    "neutral": {"name": "普通战场", "description": "无额外修正"},
    "forest": {"name": "茂密森林", "description": "火遁与风遁增强，灼烧更容易扩散"},
    "mist": {"name": "浓雾水域", "description": "水遁增强，火遁与非感知招式命中下降"},
    "desert": {"name": "风之国沙地", "description": "土遁增强，水遁威力略降"},
    "rain": {"name": "暴雨废墟", "description": "双方持续湿润，水遁与雷遁增强，火遁减弱"},
    "nature": {"name": "自然能量场", "description": "每回合恢复少量查克拉"},
    "war_front": {"name": "忍界大战前线", "description": "体术与土遁的破势效率提高"},
}

LOCATION_ENVIRONMENT = {
    "konoha_forest": "forest",
    "forest_of_death": "forest",
    "suna_village": "desert",
    "myoboku": "nature",
    "war_front": "war_front",
}

ELITE_AFFIXES = {
    "swift": ("迅捷", "速度提高30%"),
    "armored": ("重甲", "生命与防御提高25%"),
    "berserk": ("狂暴", "攻击提高30%，防御降低10%"),
    "chakra": ("查克拉充盈", "查克拉上限提高50%"),
    "regenerative": ("再生", "每回合恢复少量生命"),
    "venomous": ("剧毒", "攻击有概率附加中毒"),
}

CONTROL_EFFECTS = {
    "burn", "confuse", "bleed", "spirit_shake", "poison", "paralyze",
    "sealed", "fear", "chakra_disorder", "chakra_drain",
}


def type_multiplier(attack_element, defender_elements):
    mult = 1.0
    chart = TYPE_CHART.get(attack_element, {})
    for elem in defender_elements:
        mult *= chart.get(elem, 1.0)
    return mult


def calc_damage(attacker, defender, skill):
    """最终伤害 = 技能威力 × 攻击 ÷ 防御 × 克制倍率 × 浮动 × 状态修正"""
    power = skill["power"]
    if power <= 0:
        return 0
    atk = attacker["attack"]
    dfs = max(defender["defense"], 1)
    mult = type_multiplier(skill["element"], defender.get("elements", []))
    variance = random.uniform(0.85, 1.15)

    dmg = power * atk / dfs * mult * variance

    statuses = {s["id"] for s in attacker.get("status", [])}
    d_statuses = {s["id"] for s in defender.get("status", [])}
    if "burn" in statuses:
        dmg *= 0.8
    if "sealed" in statuses:
        dmg *= 0.7
    if "attack_up" in statuses:
        dmg *= 1.3
    if "defense_up" in d_statuses:
        dmg *= 0.7
    if "cloak" in d_statuses:
        dmg *= 0.85
    if "nine_shield" in d_statuses:
        dmg *= 0.5
    if "bleed" in d_statuses and skill["type"] == "taijutsu":
        dmg *= 1.25
    if "spirit_shake" in d_statuses and skill["type"] == "genjutsu":
        dmg *= 1.3

    # 九尾查克拉泄露：鸣人低血量时攻击提升
    if attacker.get("id") == "naruto" and attacker["hp"] < attacker["max_hp"] * 0.3:
        dmg *= 1.3
        ui.slow_print("  (鸣人体内涌出一丝赤红的查克拉——九尾查克拉泄露！)")

    return max(1, int(dmg))


def add_status(target, status_id, turns=3):
    if any(s["id"] == status_id for s in target.setdefault("status", [])):
        return
    target["status"].append({"id": status_id, "turns": turns})
    ui.emit_visual_event("status", status=status_id, target=target.get("name", ""))
    ui.slow_print(f"  {target['name']} 陷入了【{STATUS_NAMES.get(status_id, status_id)}】状态！")


def apply_turn_statuses(unit):
    """回合结束时结算状态。"""
    expired = []
    for s in unit.get("status", []):
        if s["id"] == "burn":
            loss = max(1, unit["max_hp"] // 16)
            unit["hp"] -= loss
            ui.slow_print(f"  {unit['name']} 因灼烧损失 {loss} 点生命。")
        elif s["id"] == "poison":
            loss = max(1, unit["max_hp"] // 12)
            unit["hp"] -= loss
            ui.slow_print(f"  {unit['name']} 因中毒损失 {loss} 点生命。")
        elif s["id"] == "bleed":
            loss = max(1, unit["max_hp"] // 20)
            unit["hp"] -= loss
            ui.slow_print(f"  {unit['name']} 因流血损失 {loss} 点生命。")
        s["turns"] -= 1
        if s["turns"] <= 0:
            expired.append(s)
    for s in expired:
        unit["status"].remove(s)
        ui.slow_print(f"  {unit['name']} 的【{STATUS_NAMES.get(s['id'], s['id'])}】状态解除了。")


def can_act(unit):
    statuses = {s["id"] for s in unit.get("status", [])}
    if "paralyze" in statuses and random.random() < 0.25:
        ui.slow_print(f"  {unit['name']} 因麻痹无法行动！")
        return False
    if "confuse" in statuses and random.random() < 0.4:
        self_dmg = max(1, unit["attack"] // 2)
        unit["hp"] -= self_dmg
        ui.slow_print(f"  {unit['name']} 陷入混乱，攻击了自己，损失 {self_dmg} 点生命！")
        return False
    return True


def hit_check(skill, defender):
    acc = skill["accuracy"]
    if any(s["id"] == "evade_up" for s in defender.get("status", [])):
        acc -= 25
    return random.randint(1, 100) <= acc


EFFECT_STATUS = {
    "burn": "burn", "confuse": "confuse", "bleed": "bleed",
    "spirit_shake": "spirit_shake", "poison": "poison",
    "paralyze": "paralyze", "sealed": "sealed",
    "fear": "fear", "chakra_disorder": "chakra_disorder",
}


def _has_status(unit, status_id):
    return any(s["id"] == status_id for s in unit.get("status", []))


def _remove_status(unit, status_id):
    unit["status"] = [status for status in unit.get("status", []) if status["id"] != status_id]


def _prepare_environment(state, rules):
    environment_id = rules.get("environment", LOCATION_ENVIRONMENT.get(state.location, "neutral"))
    environment = dict(ENVIRONMENTS.get(environment_id, ENVIRONMENTS["neutral"]))
    environment["id"] = environment_id if environment_id in ENVIRONMENTS else "neutral"
    return environment


def _environment_skill(skill, environment):
    adjusted = dict(skill)
    element = adjusted.get("element")
    environment_id = environment.get("id", "neutral")
    multiplier = 1.0
    if environment_id == "forest" and element in ("fire", "wind"):
        multiplier = 1.15 if element == "fire" else 1.1
    elif environment_id == "mist":
        if element == "water":
            multiplier = 1.15
        elif element == "fire":
            multiplier = 0.85
        if element not in ("water", "yin", "genjutsu"):
            adjusted["accuracy"] = max(40, adjusted["accuracy"] - 8)
    elif environment_id == "desert":
        multiplier = 1.15 if element == "earth" else 0.9 if element == "water" else 1.0
    elif environment_id == "rain":
        if element in ("water", "lightning"):
            multiplier = 1.15
        elif element == "fire":
            multiplier = 0.8
    adjusted["power"] = max(0, int(adjusted.get("power", 0) * multiplier))
    if environment_id == "war_front" and element in ("taijutsu", "earth"):
        adjusted["_break_mult"] = adjusted.get("_break_mult", 1.0) * 1.25
    return adjusted


def _position_skill(skill, user, context):
    adjusted = dict(skill)
    if not context or user.get("id") != "naruto":
        return adjusted
    position = context.get("player_position", "mid")
    skill_type = adjusted.get("type")
    multiplier = 1.0
    if position == "front":
        multiplier = 1.2 if skill_type == "taijutsu" else 0.95
        adjusted["_break_mult"] = adjusted.get("_break_mult", 1.0) * 1.2
    elif position == "rear":
        multiplier = 0.8 if skill_type == "taijutsu" else 1.1
    adjusted["power"] = max(0, int(adjusted.get("power", 0) * multiplier))
    return adjusted


def _apply_element_reaction(target, skill, result):
    if not result.get("hit") or result.get("damage", 0) <= 0:
        return
    element = skill.get("element")
    reaction_mult = skill.get("_reaction_mult", 1.0)
    if element == "water":
        if _has_status(target, "burn"):
            _remove_status(target, "burn")
            ui.emit_visual_event("reaction", reaction="douse", target=target.get("name", ""))
            ui.slow_print("  ◇ 水遁扑灭灼烧，蒸汽遮蔽了视野！")
        add_status(target, "wet", 2)
        return
    if element == "lightning" and _has_status(target, "wet"):
        _remove_status(target, "wet")
        extra = max(5, int(result["damage"] * 0.35 * reaction_mult))
        target["hp"] -= extra
        result["damage"] += extra
        add_status(target, "paralyze", 2)
        ui.emit_visual_event("reaction", reaction="electrocharged", target=target.get("name", ""))
        ui.slow_print(f"  ⚡【感电】湿润导电，额外造成 {extra} 点伤害并附加麻痹！")
    elif element == "fire" and _has_status(target, "wet"):
        _remove_status(target, "wet")
        extra = max(3, int(result["damage"] * 0.15 * reaction_mult))
        target["hp"] -= extra
        result["damage"] += extra
        ui.emit_visual_event("reaction", reaction="steam_burst", target=target.get("name", ""))
        ui.slow_print(f"  ♨【蒸汽爆发】冷热冲击额外造成 {extra} 点伤害！")
    elif element == "wind" and _has_status(target, "burn"):
        extra = max(4, int(result["damage"] * 0.3 * reaction_mult))
        target["hp"] -= extra
        result["damage"] += extra
        for status in target["status"]:
            if status["id"] == "burn":
                status["turns"] = max(status["turns"], 3)
        ui.emit_visual_event("reaction", reaction="fan_flame", target=target.get("name", ""))
        ui.slow_print(f"  🔥【风助火势】灼烧扩散，额外造成 {extra} 点伤害！")
    elif element == "earth" and _has_status(target, "wet"):
        add_status(target, "paralyze", 1)
        ui.emit_visual_event("reaction", reaction="mud_trap", target=target.get("name", ""))
        ui.slow_print("  ◆【泥沼】湿润地面被土遁搅成泥流，目标行动受限！")


def _environment_turn(environment, player, enemy, turn):
    environment_id = environment.get("id")
    if environment_id == "rain":
        if not _has_status(player, "wet"):
            add_status(player, "wet", 2)
        if not _has_status(enemy, "wet"):
            add_status(enemy, "wet", 2)
    elif environment_id == "nature" and turn > 1:
        recovered = max(3, player["max_chakra"] // 30)
        old_chakra = player["chakra"]
        player["chakra"] = min(player["max_chakra"], player["chakra"] + recovered)
        if player["chakra"] > old_chakra:
            ui.slow_print(f"  ◇ 自然能量汇入经络，恢复 {player['chakra'] - old_chakra} 点查克拉。")
    if "regenerative" in enemy.get("_elite_affixes", []) and enemy["hp"] < enemy["max_hp"]:
        heal = max(1, enemy["max_hp"] // 20)
        enemy["hp"] = min(enemy["max_hp"], enemy["hp"] + heal)
        ui.slow_print(f"  ⚠ 再生词缀恢复了 {enemy['name']} {heal} 点生命。")


def execute_skill(user, target, skill, state=None, context=None):
    """执行技能。"""
    cost = skill["chakra_cost"]
    if _has_status(user, "chakra_disorder") and cost > 0:
        cost = int(cost * 1.5)
        ui.slow_print(f"  ({user['name']} 的查克拉紊乱，消耗增加至 {cost}！)")
    if user["chakra"] < cost:
        ui.slow_print(f"  {user['name']} 查克拉不足，攻击失去了力道……")
        skill = {"id": "struggle", "name": "勉强挥拳", "type": "taijutsu",
                 "element": "taijutsu", "power": 15, "chakra_cost": 0, "accuracy": 90, "effect": None}
        cost = 0
    user["chakra"] -= cost

    result = {"hit": False, "damage": 0, "counter_success": False, "skill": skill}
    ui.slow_print(f"→ {user['name']} 使用了【{skill['name']}】！")

    if not hit_check(skill, target):
        ui.slow_print("  但是没有命中！")
        return result
    result["hit"] = True

    effect = skill.get("effect")

    # 自身增益/恢复类
    if effect == "defense_up":
        add_status(user, "defense_up", skill.get("_status_turns", 3))
    elif effect == "evade_up":
        add_status(user, "evade_up", skill.get("_status_turns", 2))
    elif effect == "clone_guard":
        add_status(user, "clone_guard", skill.get("_status_turns", 2))
    elif effect == "attack_up":
        add_status(user, "attack_up", 3)
    elif effect == "heal_self":
        heal = int(user["max_hp"] * 0.35)
        user["hp"] = min(user["max_hp"], user["hp"] + heal)
        ui.slow_print(f"  {user['name']} 恢复了 {heal} 点生命。")
    elif effect == "cloak":
        add_status(user, "attack_up", 3)
        add_status(user, "cloak", 3)
        ui.slow_print("  赤红色的查克拉如外衣般包裹全身，尾兽之力在血管里奔涌！")
        if state is not None and user.get("id") == "naruto":
            state.add_flux(10)
            state.exposure += 3
    elif effect == "sage_mode":
        add_status(user, "attack_up", 4)
        add_status(user, "evade_up", 3)
        heal = int(user["max_hp"] * 0.25)
        user["hp"] = min(user["max_hp"], user["hp"] + heal)
        ui.slow_print("  呼吸放缓——眼周浮现橙红色的隈取，天地的声音一齐涌进感知！")
        ui.slow_print(f"  ※ 仙人模式！攻击与闪避提升，恢复 {heal} 点生命。")
    elif effect == "kurama_mode":
        add_status(user, "attack_up", 4)
        add_status(user, "cloak", 4)
        heal = int(user["max_hp"] * 0.3)
        user["hp"] = min(user["max_hp"], user["hp"] + heal)
        ui.slow_print("  金色的查克拉如朝阳般点亮全身，九喇嘛的咆哮与心跳同频！")
        ui.slow_print(f"  ※ 九喇嘛模式！攻击大幅提升、伤害减免，恢复 {heal} 点生命。")
        if state is not None and user.get("id") == "naruto" and not state.flags.get("kurama_friend"):
            state.add_flux(8)
    elif effect == "fusion_resonance" and state is not None:
        # 九命共鸣:威力与附带效果随契约成长(不回写 skills_db)
        skill = dict(skill)
        skill["power"] = _fusion_power(state)
        _fusion_effects(state, user, target)

    # 伤害
    if skill["power"] > 0:
        dmg = calc_damage(user, target, skill)
        # 影分身护卫替目标承伤
        guard = next((s for s in target.get("status", []) if s["id"] == "clone_guard"), None)
        if guard:
            dmg = int(dmg * 0.5)
            target["status"].remove(guard)
            ui.slow_print(f"  {target['name']} 的影分身替他挡下了一半伤害！")
        guard_mode = target.get("_guard_mode")
        if guard_mode == "guard":
            dmg = max(1, int(dmg * 0.55))
            ui.slow_print(f"  {target['name']} 稳稳架住攻势，伤害大幅降低！")
        elif guard_mode == "counter":
            chance = max(0.45, min(0.85, 0.65 + (target.get("speed", 0) - user.get("speed", 0)) * 0.01))
            if random.random() < chance:
                dmg = max(1, int(dmg * 0.35))
                result["counter_success"] = True
                ui.slow_print(f"  {target['name']} 看穿攻击轨迹，精准卸开了大部分力道！")
            else:
                dmg = max(1, int(dmg * 1.1))
                ui.slow_print(f"  {target['name']} 反击时机判断失误，承受了更重的一击！")
        if target.get("_ally_guard"):
            dmg = max(1, int(dmg * 0.85))
            ui.slow_print("  队友的掩护又削弱了一部分伤害！")
        if context and target.get("id") == "naruto":
            target_position = context.get("player_position", "mid")
            if target_position == "front":
                dmg = max(1, int(dmg * 1.1))
            elif target_position == "rear":
                dmg = max(1, int(dmg * 0.9))
            gear_bonuses = context.get("gear_bonuses", {})
            dmg = max(1, int(dmg * gear_bonuses.get("incoming_mult", 1.0)))
            if guard_mode == "guard":
                dmg = max(1, int(dmg * gear_bonuses.get("guard_mult", 1.0)))
        target["hp"] -= dmg
        result["damage"] = dmg
        mult = type_multiplier(skill["element"], target.get("elements", []))
        note = ""
        if mult >= 2.0:
            note = " (效果绝佳!!)"
        elif mult > 1.0:
            note = " (效果不错!)"
        elif mult == 0:
            note = " (没有效果…)"
        elif mult < 1.0:
            note = " (效果不太好…)"
        ui.slow_print(f"  对 {target['name']} 造成 {dmg} 点伤害!{note}")

    # 目标异常类
    if effect in EFFECT_STATUS and random.random() < skill.get("_effect_chance", 0.6):
        add_status(target, EFFECT_STATUS[effect], skill.get("_status_turns", 3))
    elif effect == "chakra_drain":
        drain = min(target["chakra"], 35)
        target["chakra"] -= drain
        ui.slow_print(f"  {target['name']} 的经络被点封，查克拉流失 {drain} 点！")

    # 暴露风险(使用未来技能)
    if effect == "expose_risk" and state is not None:
        state.exposure += 5
        if target.get("id", "").startswith("kakashi"):
            state.add_suspicion(15)
    if skill.get("_self_bonus"):
        add_status(user, skill["_self_bonus"], 2)
    if skill.get("_target_chakra_drain"):
        drain = min(target["chakra"], skill["_target_chakra_drain"])
        target["chakra"] -= drain
        ui.slow_print(f"  ※ 强化封阵额外抽离 {drain} 点查克拉！")
    _apply_element_reaction(target, skill, result)
    return result


def _intent_kind(skill):
    if not skill:
        return None
    effect = skill.get("effect")
    if skill.get("power", 0) >= 90:
        return "fatal"
    if effect in CONTROL_EFFECTS:
        return "control"
    if skill.get("power", 0) <= 0:
        return "support"
    return "attack"


def _intent_description(skill):
    if not skill:
        return "破势中，本回合无法行动"
    kind_id = _intent_kind(skill)
    if kind_id == "fatal":
        kind = "☄ 致命攻击"
    elif kind_id == "control":
        kind = "◆ 控制招式"
    elif kind_id == "support":
        kind = "◇ 强化/恢复"
    else:
        kind = "▶ 直接攻击"
    return f"{kind}【{skill['name']}】"


def _objective_progress(rules, turn, log, enemy):
    objective = rules.get("objective")
    if not objective:
        return rules.get("objective_text", f"击败 {enemy['name']}")
    kind = objective.get("type", "defeat")
    if kind == "survive":
        return f"坚持 {objective['turns']} 回合（当前 {min(turn, objective['turns'])}/{objective['turns']}）"
    if kind == "break":
        return f"累计破势 {objective.get('count', 1)} 次（当前 {log.get('break_count', 0)}）"
    if kind == "capture":
        percent = int(objective.get("hp_ratio", 0.25) * 100)
        return f"将敌人生命压至 {percent}% 以下并完成破势"
    return objective.get("description", f"击败 {enemy['name']}")


def show_battle_status(player, enemy, turn, intent=None, rules=None, log=None):
    ui.line()
    print(f" 回合 {turn}")
    context = log or {}
    environment = context.get("environment", ENVIRONMENTS["neutral"])
    print(
        f" 战场: {environment['name']} | 鸣人站位: "
        f"{POSITION_NAMES.get(context.get('player_position', 'mid'), '中排')}"
    )
    p_warn = " ⚠危" if player["hp"] < player["max_hp"] * 0.25 else ""
    print(f" {player['name']:　<8} {ui.stat_line('HP', player['hp'], player['max_hp'])}{p_warn}")
    print(f" {'':　<8} {ui.stat_line('CK', player['chakra'], player['max_chakra'])}")
    p_status = " ".join(STATUS_NAMES.get(s['id'], s['id']) for s in player.get("status", []))
    if p_status:
        print(f" {'':　<8} 状态: {p_status}")
    print(f" {'─' * 17} VS {'─' * 17}")
    e_warn = " ⚠危" if enemy["hp"] < enemy["max_hp"] * 0.25 else ""
    print(f" {enemy['name']:　<8} {ui.stat_line('HP', enemy['hp'], enemy['max_hp'])}{e_warn}")
    if enemy.get("_elite_affixes"):
        affix_names = "、".join(ELITE_AFFIXES[affix][0] for affix in enemy["_elite_affixes"])
        print(f" {'':　<8} 精英词缀: {affix_names}")
    e_status = " ".join(STATUS_NAMES.get(s['id'], s['id']) for s in enemy.get("status", []))
    if e_status:
        print(f" {'':　<8} 状态: {e_status}")
    if enemy.get("max_break"):
        break_note = " 破势中" if enemy.get("broken") else ""
        print(f" {'':　<8} 破势 {enemy['break']}/{enemy['max_break']}{break_note}")
    print(f" 敌方意图: {_intent_description(intent)}")
    print(f" 战斗目标: {_objective_progress(rules or {}, turn, context, enemy)}")
    ui.line()


def _skill_break_damage(skill, result, enemy):
    if not result or not result.get("hit") or skill.get("power", 0) <= 0:
        return 0
    amount = skill.get("power", 0) * 0.42 + result.get("damage", 0) * 0.16
    if skill.get("type") == "taijutsu":
        amount *= 1.15
    if skill.get("effect") in CONTROL_EFFECTS:
        amount *= 1.35
    if type_multiplier(skill.get("element"), enemy.get("elements", [])) > 1:
        amount *= 1.2
    amount *= skill.get("_break_mult", 1.0)
    return max(4, int(amount))


def _apply_break(enemy, amount, log, source="攻击"):
    if amount <= 0 or not enemy.get("max_break") or enemy.get("broken"):
        return False
    old_value = enemy["break"]
    enemy["break"] = max(0, enemy["break"] - amount)
    ui.slow_print(f"  ※ {source}削减破势 {old_value - enemy['break']} 点。")
    if enemy["break"] > 0:
        return False
    enemy["broken"] = True
    log["break_count"] = log.get("break_count", 0) + 1
    ui.slow_print(f"★ {enemy['name']} 架势崩溃！下一次行动将被打断！")
    return True


def _resolve_counter(player, enemy, enemy_skill, result, log):
    if not result or not result.get("counter_success") or player["hp"] <= 0:
        return
    counter_damage = max(1, int(player["attack"] * 0.8 - enemy["defense"] * 0.2))
    enemy["hp"] -= counter_damage
    ui.slow_print(f"⇒ 精准反击！鸣人抓住【{enemy_skill['name']}】的空隙，造成 {counter_damage} 点伤害！")
    _apply_break(enemy, max(18, counter_damage // 2), log, "精准反击")


def _check_objective(rules, player, enemy, turn, log):
    objective = rules.get("objective")
    if not objective:
        return None
    kind = objective.get("type", "defeat")
    if kind == "survive" and turn > objective["turns"]:
        return objective.get("result", "survived")
    if kind == "break" and log.get("break_count", 0) >= objective.get("count", 1):
        return objective.get("result", "objective_complete")
    if kind == "capture":
        weak_enough = enemy["hp"] <= enemy["max_hp"] * objective.get("hp_ratio", 0.25)
        if weak_enough and log.get("break_count", 0) > 0:
            return objective.get("result", "captured")
    checker = objective.get("check")
    if checker:
        return checker(player, enemy, turn, log)
    return None


ITEM_EFFECTS = {
    "军粮丸": "恢复 40 生命、30 查克拉",
    "回复丹": "恢复 80 生命",
    "查克拉丸": "恢复 70 查克拉",
    "药草": "恢复 25 生命，解除中毒",
    "解毒丸": "解除中毒、灼烧、流血与麻痹",
    "复苏秘药": "恢复全部生命和查克拉，解除全部异常",
    "强效军粮丸": "恢复 90 生命、60 查克拉",
    "凝神丸": "恢复 100 查克拉并解除精神类异常",
}


def use_item(state, player):
    items = {k: v for k, v in state.inventory.items() if v > 0 and k in ITEM_EFFECTS}
    if not items:
        ui.slow_print("没有可用的道具。")
        return False
    names = list(items.keys())
    idx = ui.choose("使用哪个道具?", [f"{n} ×{c} ({ITEM_EFFECTS.get(n, '')})" for n, c in items.items()],
                    allow_cancel=True)
    if idx < 0:
        return False
    name = names[idx]
    state.inventory[name] -= 1
    heal_mult = equipment.combat_bonuses(state)["item_heal_mult"]
    if name == "军粮丸":
        heal = int(40 * heal_mult)
        player["hp"] = min(player["max_hp"], player["hp"] + heal)
        player["chakra"] = min(player["max_chakra"], player["chakra"] + 30)
        ui.slow_print(f"※ 嚼下军粮丸，恢复 {heal} 点生命、30 点查克拉。")
    elif name == "回复丹":
        heal = int(80 * heal_mult)
        player["hp"] = min(player["max_hp"], player["hp"] + heal)
        ui.slow_print(f"※ 服下回复丹，恢复 {heal} 点生命。")
    elif name == "查克拉丸":
        player["chakra"] = min(player["max_chakra"], player["chakra"] + 70)
        ui.slow_print("※ 吞下查克拉丸，恢复 70 点查克拉。")
    elif name == "药草":
        heal = int(25 * heal_mult)
        player["hp"] = min(player["max_hp"], player["hp"] + heal)
        player["status"] = [s for s in player.get("status", []) if s["id"] != "poison"]
        ui.slow_print(f"※ 嚼碎药草敷在伤口上，恢复 {heal} 点生命，中毒解除。")
    elif name == "解毒丸":
        player["status"] = [
            status for status in player.get("status", [])
            if status["id"] not in ("poison", "burn", "bleed", "paralyze")
        ]
        ui.slow_print("※ 服下解毒丸，中毒、灼烧、流血与麻痹全部解除。")
    elif name == "复苏秘药":
        player["hp"] = player["max_hp"]
        player["chakra"] = player["max_chakra"]
        player["status"] = []
        ui.slow_print("※ 复苏秘药化作暖流，生命与查克拉完全恢复，异常全消。")
    elif name == "强效军粮丸":
        heal = int(90 * heal_mult)
        player["hp"] = min(player["max_hp"], player["hp"] + heal)
        player["chakra"] = min(player["max_chakra"], player["chakra"] + 60)
        ui.slow_print(f"※ 强效军粮丸恢复 {heal} 点生命、60 点查克拉。")
    elif name == "凝神丸":
        player["chakra"] = min(player["max_chakra"], player["chakra"] + 100)
        player["status"] = [
            status for status in player.get("status", [])
            if status["id"] not in ("fear", "confuse", "spirit_shake", "chakra_disorder")
        ]
        ui.slow_print("※ 心神澄明，恢复 100 点查克拉并解除精神异常。")
    return True


def _fusion_power(state):
    """九命共鸣的运行时威力: 基础55 + Σ契约等级 + 四维均值加成。"""
    cs = [c for c in state.contracts.values() if c.get("unlocked")]
    if not cs:
        return 55
    lv_sum = sum(c["contract_level"] for c in cs)
    avg4 = sum(c["affection"] + c["trust"] + c["safety"] + c["fate_resonance"]
               for c in cs) / (4 * len(cs))
    return 55 + lv_sum + max(0, int((avg4 - 70) / 2))


def _fusion_effects(state, user, target):
    """九命共鸣的附带效果:每位已契约者的天赋各出一分力。"""
    cs = {c["id"] for c in state.contracts.values() if c.get("unlocked")}
    ui.slow_print(f"  {len(cs)} 条命线一齐亮起，与查克拉共鸣——")
    heal = 0
    ck = 0
    if "rin" in cs:
        heal += int(user["max_hp"] * 0.04)
    if "tsunade" in cs:
        heal += int(user["max_hp"] * 0.06)
    if "gaia" in cs:
        ck += int(user["max_chakra"] * 0.08)
    if "kushina" in cs or "konan" in cs:
        add_status(user, "defense_up", 2)
        ui.slow_print("  赤发的锁链与纸之羽翼环身护持，防御提升！")
    if "sakura" in cs:
        add_status(user, "attack_up", 2)
        ui.slow_print("  怪力的要诀灌入拳锋，攻击提升！")
    if "hinata" in cs:
        add_status(user, "evade_up", 2)
        ui.slow_print("  白眼的视野与柔步相合，闪避提升！")
    if "shizune" in cs:
        cured = [s for s in user.get("status", [])
                 if s["id"] in ("poison", "bleed", "burn")]
        if cured:
            user["status"] = [s for s in user["status"] if s not in cured]
            ui.slow_print("  静音的医毒手抚过经络，异常尽除。")
    if "mei" in cs:
        add_status(target, "burn", 2)
        ui.slow_print(f"  熔遁的余温缠上 {target['name']}，灼烧不止！")
    if heal:
        user["hp"] = min(user["max_hp"], user["hp"] + heal)
        ui.slow_print(f"  医疗系命线的暖流恢复 {heal} 点生命。")
    if ck:
        user["chakra"] = min(user["max_chakra"], user["chakra"] + ck)
        ui.slow_print(f"  大地之息补充 {ck} 点查克拉。")


def _combo_list(state):
    """返回当前可用的羁绊联合技 [(key, 名称, 描述, 查克拉)]。"""
    c = state.contracts
    combos = []

    def add_combo(key, name, description, base_cost):
        mastery = party.combo_stats(state, key, base_cost)
        rank = f"·强化{mastery['level']}阶" if mastery["level"] > 1 else ""
        combos.append((key, f"{name}{rank}", description, mastery["cost"]))

    if c["kushina"]["unlocked"] and c["kushina"]["contract_level"] >= 5:
        add_combo("combo_kushina", "赤阳封命阵 (鸣人+玖辛奈)",
                  "金红锁链封印敌人并恢复生命", 25)
    if c["rin"]["unlocked"] and c["rin"]["contract_level"] >= 5:
        add_combo("combo_rin", "温柔归命 (鸣人+琳)",
                  "生命完全恢复，解除全部异常", 25)
    if (c["kushina"]["unlocked"] and c["rin"]["unlocked"]
            and c["kushina"]["contract_level"] >= 5 and c["rin"]["contract_level"] >= 5):
        add_combo("combo_shield", "九命守护 (鸣人+双契约者)",
                  "命线护盾：3回合内受伤减半，并恢复生命", 30)
    if c["tsunade"]["unlocked"] and c["shizune"]["unlocked"] \
            and c["tsunade"]["contract_level"] >= 5 and c["shizune"]["contract_level"] >= 5:
        add_combo("combo_medic", "百豪医堂 (鸣人+纲手+静音)",
                  "师徒双医全力施为：完全恢复并附加再生护体", 30)
    if c["mei"]["unlocked"] and c["mei"]["contract_level"] >= 5:
        add_combo("combo_mei", "熔天焦土 (鸣人+照美冥)",
                  "螺旋丸与熔遁合流，重创敌人并致灼烧", 35)
    high = [x for x in c.values() if x["unlocked"] and x["contract_level"] >= 6]
    if len(high) >= 2:
        add_combo("combo_tougen", "桃源归心 (鸣人+全体契约者)",
                  "桃源之风拂过：大幅恢复生命查克拉，负面全消，攻击提升", 40)
    if len([x for x in c.values() if x["unlocked"] and x["contract_level"] >= 9]) >= 6:
        add_combo("combo_ninelives", "九命同归 (九条命线·终极)",
                  "九命齐鸣：完全恢复、九命守护、攻击大幅提升并重创敌人", 60)
    return combos


def contract_support(state, player, log, enemy=None):
    """契约支援与联合技。每项每场战斗限一次。"""
    used = log.setdefault("support_used", set())
    options = []   # (key, label, handler)

    for c in state.contracts.values():
        if not (c["unlocked"] and c["contract_level"] >= 1):
            continue
        key = f"sup_{c['id']}"
        if key in used:
            continue
        options.append((key, f"{c['name']}【{c['support_skill_name']}】- {c['support_desc']}", c))

    combos = []
    for key, name, desc, cost in _combo_list(state):
        if key not in used:
            combos.append((key, f"◆联合技◆ {name} - {desc} (查克拉{cost})", (key, cost)))
    options += combos

    if not options:
        if log.get("support_used"):
            ui.slow_print("契约者们的力量在这场战斗中已经用尽了——接下来，要靠自己。")
        else:
            ui.slow_print("尚无已缔结契约的支援者……心底只有一片安静的暖意。")
        return False

    idx = ui.choose("呼唤谁的力量? (每场战斗各限一次)", [o[1] for o in options], allow_cancel=True)
    if idx < 0:
        return False
    key, _, data = options[idx]

    # ── 基础支援 ──
    if key.startswith("sup_"):
        c = data
        lv = c["contract_level"]
        if c["id"] == "kushina":
            heal = 40 + 8 * lv
            player["hp"] = min(player["max_hp"], player["hp"] + heal)
            add_status(player, "defense_up", 3)
            ui.slow_print("一缕温暖的赤色查克拉缠绕上鸣人的身体——")
            ui.slow_print("『不要怕，妈妈在这里。』")
            ui.slow_print(f"※ 赤发守护！恢复 {heal} 点生命，防御提升！")
        elif c["id"] == "rin":
            heal = 45 + 8 * lv
            player["hp"] = min(player["max_hp"], player["hp"] + heal)
            player["status"] = [s for s in player.get("status", [])
                                if s["id"] not in ("poison", "bleed", "burn")]
            ui.slow_print("柔和的碧绿色光芒笼罩了伤口——")
            ui.slow_print("『别乱动，马上就好。……真是的，跟卡卡西一样爱逞强。』")
            ui.slow_print(f"※ 温柔医疗！恢复 {heal} 点生命，中毒、流血与灼烧解除。")
        elif c["id"] == "tsunade":
            heal = int(player["max_hp"] * 0.45)
            player["hp"] = min(player["max_hp"], player["hp"] + heal)
            player["status"] = [s for s in player.get("status", [])
                                if s["id"] in ("defense_up", "evade_up", "clone_guard",
                                               "attack_up", "cloak", "nine_shield")]
            log["undying"] = True
            log["undying_src"] = "tsunade"
            ui.slow_print("额间的印记透过命线传来磅礴的生命力——")
            ui.slow_print("『赌上这条项链，你小子今天死不了。』")
            ui.slow_print(f"※ 百豪之守！恢复 {heal} 点生命，异常解除，本场战斗将抵御一次致命伤！")
        elif c["id"] == "sakura":
            heal = 40 + 7 * lv
            player["hp"] = min(player["max_hp"], player["hp"] + heal)
            player["status"] = [s for s in player.get("status", [])
                                if s["id"] not in ("poison", "bleed", "burn")]
            ui.slow_print("翠绿的医疗查克拉裹住伤口,紧接着一道樱色的身影掠向敌阵——")
            ui.slow_print("『别愣着!伤我治,人你打——不许输啊,鸣人!』")
            ui.slow_print(f"※ 怪力回春！恢复 {heal} 点生命，中毒、流血与灼烧解除。")
            if enemy is not None:
                dmg = max(1, int((30 + 5 * lv) * random.uniform(0.8, 1.2)))
                enemy["hp"] -= dmg
                ui.slow_print(f"  百分百爱意的正拳轰进敌阵,造成 {dmg} 点伤害！")
        elif c["id"] == "shizune":
            heal = 40 + 7 * lv
            player["hp"] = min(player["max_hp"], player["hp"] + heal)
            player["status"] = [s for s in player.get("status", [])
                                if s["id"] not in ("poison", "bleed", "burn",
                                                   "paralyze", "confuse", "chakra_disorder")]
            ui.slow_print("熟练而轻柔的医疗查克拉抚过伤口——")
            ui.slow_print("『别动。……真是的，你和纲手大人一样不让人省心。』")
            ui.slow_print(f"※ 医毒净化！恢复 {heal} 点生命，大部分异常解除。")
            if enemy is not None:
                add_status(enemy, "poison", 3)
                ui.slow_print("  淬毒的针雨自命线中射出，刺入敌人的经络！")
        elif c["id"] == "hinata":
            player["status"] = [s for s in player.get("status", [])
                                if s["id"] not in ("spirit_shake", "confuse", "fear")]
            add_status(player, "evade_up", 3)
            ui.slow_print("温柔而坚定的白眼视野,顺着命线与你重合——")
            ui.slow_print("『鸣人君,左后方三点钟!……嗯,我看得见。全部,都看得见。』")
            ui.slow_print("※ 柔拳心眼！精神干扰解除，闪避提升！")
            if enemy is not None:
                drain = min(enemy["chakra"], 30)
                enemy["chakra"] -= drain
                add_status(enemy, "chakra_disorder", 3)
                ui.slow_print(f"  柔步双狮拳点封经络,敌人查克拉流失 {drain} 点并陷入紊乱！")
        elif c["id"] == "konan":
            heal = 35 + 6 * lv
            player["hp"] = min(player["max_hp"], player["hp"] + heal)
            add_status(player, "defense_up", 3)
            add_status(player, "evade_up", 2)
            ui.slow_print("千万张白纸自命线中涌出，折成羽翼与花，将你环抱——")
            ui.slow_print("『这是弥彦的梦，长门的心，和我的祈祷。』")
            ui.slow_print(f"※ 纸翼庇护！恢复 {heal} 点生命，防御与闪避提升！")
        elif c["id"] == "mei":
            ui.slow_print("命线尽头传来一声轻笑，天空落下灼热的雨——")
            ui.slow_print("『护着可爱的后辈，是水影的特权哦。』")
            if enemy is not None:
                dmg = calc_damage(
                    {"attack": 40 + 4 * lv, "status": [], "id": "mei",
                     "hp": 1, "max_hp": 1},
                    enemy,
                    {"power": 75, "element": "fire", "type": "ninjutsu"})
                enemy["hp"] -= dmg
                add_status(enemy, "burn", 3)
                ui.slow_print(f"  熔遁·熔怪之术！对敌人造成 {dmg} 点伤害并使其灼烧！")
            else:
                ui.slow_print("  熔浆在周身筑起了赤红的防线。")
        elif c["id"] == "gaia":
            player["hp"] = player["max_hp"]
            player["chakra"] = min(player["max_chakra"],
                                   player["chakra"] + int(player["max_chakra"] * 0.5))
            ui.slow_print("大地深处传来古老而温柔的搏动，与你的心跳渐渐重合——")
            ui.slow_print("『孩子，站稳。大地一直都在你的脚下。』")
            ui.slow_print("※ 大地之息！生命完全恢复，查克拉大幅恢复！")
        used.add(key)
        return True

    # ── 联合技 ──
    key, cost = data
    if player["chakra"] < cost:
        ui.slow_print("查克拉不足，无法引动联合技！")
        return False
    player["chakra"] -= cost
    base_costs = {
        "combo_kushina": 25, "combo_rin": 25, "combo_shield": 30,
        "combo_medic": 30, "combo_mei": 35, "combo_tougen": 40,
        "combo_ninelives": 60,
    }
    mastery = party.combo_stats(state, key, base_costs[key])
    power_mult = mastery["power_mult"]
    heal_mult = mastery["heal_mult"]
    bonus_turns = mastery["bonus_turns"]

    if key == "combo_kushina":
        ui.story("""
「九命一系——赤阳封命阵!!」

金色的命线自鸣人心口射出，玖辛奈的赤发之影在他身后展开，
无数漩涡纹路的锁链自虚空垂落，狠狠钉进大地！
""")
        if enemy is not None:
            dmg = calc_damage(
                {"attack": player["attack"] + state.player["seal_art"], "status": [], "id": "naruto",
                 "hp": player["hp"], "max_hp": player["max_hp"]},
                enemy,
                {"power": int(95 * power_mult), "element": "seal", "type": "seal"})
            enemy["hp"] -= dmg
            add_status(enemy, "sealed", 3)
            ui.slow_print(f"  封印锁链造成 {dmg} 点伤害，敌人的忍术被封印了！")
        heal = int(player["max_hp"] * 0.4 * heal_mult)
        player["hp"] = min(player["max_hp"], player["hp"] + heal)
        ui.slow_print(f"  赤阳的暖流涌入四肢百骸，恢复 {heal} 点生命！")
    elif key == "combo_rin":
        ui.story("""
「九命一系——温柔归命!!」

碧绿色的光如春水漫过全身。琳的身影在光中浮现，
双手结印，将鸣人体内所有的伤与痛，一寸寸抚平。

『没事了。全部，都没事了。』
""")
        player["hp"] = player["max_hp"]
        player["status"] = [s for s in player.get("status", [])
                            if s["id"] in ("defense_up", "evade_up", "clone_guard",
                                           "attack_up", "cloak", "nine_shield")]
        ui.slow_print("  ※ 生命完全恢复，所有负面状态解除！")
    elif key == "combo_shield":
        ui.story("""
「九命一系——九命守护!!」

赤与碧两道命线交织成网，在鸣人周身织出一层
流转着星光的守护结界。
""")
        add_status(player, "nine_shield", 3 + bonus_turns)
        heal = int(player["max_hp"] * 0.3 * heal_mult)
        player["hp"] = min(player["max_hp"], player["hp"] + heal)
        ui.slow_print(f"  ※ 3回合内受到的伤害减半，恢复 {heal} 点生命！")
    elif key == "combo_tougen":
        ui.story("""
「九命一系——桃源归心!!」

刹那间，战场仿佛与桃源重叠——花海的暖风、溪流的水声、
契约者们的气息一齐涌来，将疲惫与伤痛全部吹散。
""")
        player["hp"] = min(player["max_hp"], player["hp"] + int(player["max_hp"] * 0.6 * heal_mult))
        player["chakra"] = min(player["max_chakra"], player["chakra"] + int(player["max_chakra"] * 0.6 * heal_mult))
        player["status"] = [s for s in player.get("status", [])
                            if s["id"] in ("defense_up", "evade_up", "clone_guard",
                                           "attack_up", "cloak", "nine_shield")]
        add_status(player, "attack_up", 3 + bonus_turns)
        ui.slow_print("  ※ 生命与查克拉大幅恢复，负面全消，攻击提升！")
    elif key == "combo_medic":
        ui.story("""
「九命一系——百豪医堂!!」

淡青的百豪纹路与静音的医疗查克拉在命线上交汇，
两代医忍的全部技艺，在一瞬间涌入你的身体。

『站直了。』『马上就好!』
""")
        player["hp"] = player["max_hp"]
        player["status"] = [s for s in player.get("status", [])
                            if s["id"] in ("defense_up", "evade_up", "clone_guard",
                                           "attack_up", "cloak", "nine_shield")]
        add_status(player, "defense_up", 3 + bonus_turns)
        ui.slow_print("  ※ 生命完全恢复，异常全消，再生护体(防御提升)！")
    elif key == "combo_mei":
        ui.story("""
「九命一系——熔天焦土!!」

命线尽头，水影大人十指结印。熔浆自天倾泻,
与你掷出的螺旋丸在敌人头顶轰然合流——
""")
        if enemy is not None:
            dmg = calc_damage(
                {"attack": player["attack"] + 20, "status": [], "id": "naruto",
                 "hp": player["hp"], "max_hp": player["max_hp"]},
                enemy,
                {"power": int(110 * power_mult), "element": "fire", "type": "ninjutsu"})
            enemy["hp"] -= dmg
            add_status(enemy, "burn", 3)
            ui.slow_print(f"  熔天的洪流造成 {dmg} 点伤害，敌人陷入灼烧！")
    elif key == "combo_ninelives":
        ui.story("""
「九命一系·终式——九命同归!!」

九条命线同时亮起,九位家人的身影在金光中并肩而立。
花海、赤发、药香、酒气、傀儡线、毒针、红瞳、纸翼、熔光——
还有大地本身的呼吸。

『去吧,孩子。』『我们都在。』

这不是九个人的力量。是「家」的力量。
""")
        player["hp"] = player["max_hp"]
        player["chakra"] = player["max_chakra"]
        player["status"] = []
        add_status(player, "nine_shield", 4 + bonus_turns)
        add_status(player, "attack_up", 4 + bonus_turns)
        if enemy is not None:
            dmg = calc_damage(
                {"attack": player["attack"] + state.player["fate_power"] * 5, "status": [],
                 "id": "naruto", "hp": player["hp"], "max_hp": player["max_hp"]},
                enemy,
                {"power": int(150 * power_mult), "element": "seal", "type": "seal"})
            enemy["hp"] -= dmg
            add_status(enemy, "sealed", 4)
            ui.slow_print(f"  九命的金网将敌人牢牢缚住，造成 {dmg} 点伤害并封印其力量！")
        ui.slow_print("  ※ 完全恢复、九命守护、攻击大幅提升！")
    party.gain_combo_mastery(state, key)
    used.add(key)
    return True


def enemy_choose_skill(enemy, skills_db, player, turn):
    skills = [skills_db[s] for s in enemy["skills"] if s in skills_db]
    sealed = any(s["id"] == "sealed" for s in enemy.get("status", []))
    usable = [s for s in skills if s["chakra_cost"] <= enemy["chakra"]
              and (not sealed or s["chakra_cost"] == 0)]
    if _has_status(enemy, "fear"):
        usable = [s for s in usable if s["power"] <= 60]
    if not usable:
        return {"id": "struggle", "name": "挥拳", "type": "taijutsu", "element": "taijutsu",
                "power": 20, "chakra_cost": 0, "accuracy": 90, "effect": None}
    ai = enemy.get("ai", "aggressive")
    if ai == "passive":
        return usable[0]
    if ai == "bell_test":
        # 卡卡西: 血量高时游刃有余，低时认真起来
        if enemy["hp"] > enemy["max_hp"] * 0.7 and turn <= 2:
            support = [s for s in usable if s["power"] == 0]
            if support and random.random() < 0.5:
                return random.choice(support)
        return max(usable, key=lambda s: s["power"] * random.uniform(0.5, 1.5))
    if ai == "boss":
        # 低血量时倾向恢复/增益，其余时候智能选高威力
        if enemy["hp"] < enemy["max_hp"] * 0.4:
            recover = [s for s in usable if s.get("effect") in ("heal_self", "defense_up", "attack_up")]
            if recover and random.random() < 0.5:
                return random.choice(recover)
        return max(usable, key=lambda s: s["power"] * random.uniform(0.6, 1.4))
    return random.choice(usable)


def _configure_ally_order(log):
    options = [
        ui.Choice("均衡协战", ("actions", "ally_order"), "攻击、治疗和牵制自由判断"),
        ui.Choice("集中攻击", ("actions", "attack"), "提高出手率与伤害"),
        ui.Choice("掩护防御", ("actions", "guard"), "优先治疗并降低鸣人受到的伤害"),
        ui.Choice("破势牵制", ("actions", "position"), "降低直接伤害，大幅削减敌人破势槽"),
    ]
    orders = ("balanced", "focus", "guard", "disrupt")
    index = ui.choose("选择队友战术（不消耗本回合行动）", options, allow_cancel=True)
    if index < 0:
        return False
    log["ally_order"] = orders[index]
    ui.slow_print(f"⇒ 队友战术切换为【{ALLY_ORDER_NAMES[orders[index]]}】。")
    return True


def _change_position(log):
    positions = ("front", "mid", "rear")
    descriptions = (
        ui.Choice("前排", ("actions", "attack"), "体术威力与破势提高，但受到伤害增加10%"),
        ui.Choice("中排", ("actions", "position"), "攻防均衡，无额外修正"),
        ui.Choice("后排", ("actions", "guard"), "忍术威力提高10%、受到伤害降低10%，体术威力下降"),
    )
    index = ui.choose("选择站位（移动将消耗本回合行动）", list(descriptions), allow_cancel=True)
    if index < 0:
        return False
    new_position = positions[index]
    if new_position == log.get("player_position", "mid"):
        ui.slow_print("当前已经处于该站位。")
        return False
    log["player_position"] = new_position
    ui.slow_print(f"→ 鸣人移动到【{POSITION_NAMES[new_position]}】。")
    return True


def _allies_act(allies, player, enemy, state, log):
    """队友协战：每回合在鸣人行动后行动。"""
    order = log.get("ally_order", "balanced")
    if order == "guard":
        player["_ally_guard"] = True
        ui.slow_print("⇒ 队友收紧阵型，为鸣人构筑掩护防线！")
    for ally in allies:
        if enemy["hp"] <= 0:
            return
        if order == "guard" and ally.get("can_heal") and player["hp"] < player["max_hp"] * 0.9:
            heal = random.randint(28, 42)
            player["hp"] = min(player["max_hp"], player["hp"] + heal)
            ui.slow_print(f"⇒ {ally['name']}优先处理伤势，恢复 {heal} 点生命。")
            continue
        act_rate = ally.get("act_rate", 0.75)
        if order == "focus":
            act_rate = min(1.0, act_rate + 0.2)
        elif order == "disrupt":
            act_rate = min(1.0, act_rate + 0.1)
        elif order == "guard":
            act_rate *= 0.7
        if random.random() < act_rate:
            mult = type_multiplier(ally.get("element", "taijutsu"), enemy.get("elements", []))
            dmg = max(1, int(ally["power"] * random.uniform(0.75, 1.25) * mult))
            if order == "focus":
                dmg = int(dmg * 1.2)
            elif order == "disrupt":
                dmg = max(1, int(dmg * 0.7))
            gear_bonuses = log.get("gear_bonuses", {})
            dmg = max(1, int(dmg * gear_bonuses.get("ally_mult", 1.0)))
            enemy["hp"] -= dmg
            ui.slow_print(f"⇒ {ally['name']}{ally.get('move', '发起攻击')}！对 {enemy['name']} 造成 {dmg} 点伤害！")
            break_damage = max(4, dmg // 5)
            if order == "disrupt":
                break_damage = max(14, int(dmg * 0.8))
            break_damage = int(break_damage * gear_bonuses.get("break_mult", 1.0))
            _apply_break(enemy, break_damage, log, f"{ally['name']}的协战")
        elif ally.get("can_heal"):
            heal = random.randint(20, 35)
            player["hp"] = min(player["max_hp"], player["hp"] + heal)
            ui.slow_print(f"⇒ {ally['name']}掩护了鸣人并为他处理伤口，恢复 {heal} 点生命。")
        else:
            ui.slow_print(f"⇒ {ally['name']}牵制住了敌人的走位！")


def _death_check(state, player, log):
    """鸣人生命归零时的契约救赎判定。返回 True 表示战斗继续。"""
    if player["hp"] > 0:
        return True
    # 百豪之守：抵御一次致命伤
    if log.get("undying"):
        log["undying"] = False
        player["hp"] = max(1, int(player["max_hp"] * 0.3))
        ui.story("""
视野变黑的一瞬，额间闪过淡青色的印记之光——

『说了你今天死不了!』

百豪之力强行修复了致命伤！
""")
        return True
    # 九命一系·第八阶【一系】：共同抵御死亡命运
    if not log.get("ninelives_used"):
        high = [c for c in state.contracts.values()
                if c["unlocked"] and c["contract_level"] >= 8]
        if high and state.fate_points >= 2:
            log["ninelives_used"] = True
            state.spend_fate(2, "九命线共抗死亡")
            player["hp"] = max(1, int(player["max_hp"] * 0.35))
            names = "、".join(c["name"] for c in high)
            ui.story(f"""
心跳停止的刹那，九条命线同时亮起——

{names}的生命力顺着命线奔涌而来，
死亡的命运，被整个「家」的重量顶了回去!

【九命一系·一系】发动！鸣人重新站了起来！
""")
            return True
    return False


def _apply_elite_affixes(enemy, affixes):
    valid = [affix for affix in affixes if affix in ELITE_AFFIXES]
    for affix in valid:
        if affix == "swift":
            enemy["speed"] = int(enemy["speed"] * 1.3)
        elif affix == "armored":
            enemy["hp"] = int(enemy["hp"] * 1.25)
            enemy["max_hp"] = int(enemy["max_hp"] * 1.25)
            enemy["defense"] = int(enemy["defense"] * 1.25)
        elif affix == "berserk":
            enemy["attack"] = int(enemy["attack"] * 1.3)
            enemy["defense"] = max(1, int(enemy["defense"] * 0.9))
        elif affix == "chakra":
            enemy["chakra"] = int(enemy["chakra"] * 1.5)
            enemy["max_chakra"] = int(enemy["max_chakra"] * 1.5)
    enemy["_elite_affixes"] = valid
    if valid:
        enemy["exp_reward"] = int(enemy.get("exp_reward", 20) * (1 + 0.25 * len(valid)))


def _prepare_enemy(state, enemy_id, rules):
    enemy = copy.deepcopy(state.enemies_db[enemy_id])
    enemy["_source_id"] = enemy_id
    if rules.get("enemy_name"):
        enemy["name"] = rules["enemy_name"]
    if rules.get("enemy_skills"):
        enemy["skills"] = list(rules["enemy_skills"])
    if rules.get("enemy_elements"):
        enemy["elements"] = list(rules["enemy_elements"])
    enemy.setdefault("status", [])
    for stat, delta in (rules.get("enemy_mods") or {}).items():
        enemy[stat] = enemy.get(stat, 0) + delta
    if rules.get("phase_full_hp"):
        enemy["max_hp"] = max(1, enemy["hp"])
    enemy["max_hp"] = max(enemy["max_hp"], enemy["hp"])
    cycle_multiplier = 1 + state.new_game_plus * 0.08
    if "veteran_enemies" in state.challenge_modifiers:
        cycle_multiplier += 0.2
    if cycle_multiplier > 1:
        for stat in ("hp", "max_hp", "attack"):
            enemy[stat] = int(enemy[stat] * cycle_multiplier)
    if "fate_storm" in state.challenge_modifiers:
        enemy["attack"] = int(enemy["attack"] * 1.1)
        enemy["exp_reward"] = int(enemy.get("exp_reward", 20) * 1.25)
    if state.backlash >= 3 and enemy.get("ai") != "passive":
        multiplier = 1 + (state.backlash - 2) * 0.06
        for stat in ("hp", "max_hp", "attack"):
            enemy[stat] = int(enemy[stat] * multiplier)
        ui.slow_print(f"(命运反噬 Lv.{state.backlash}——命运的湍流让敌人变得更加凶险……)")
    affixes = list(rules.get("elite_affixes") or [])
    if rules.get("allow_elite") and not affixes:
        chance = 0.15 + state.new_game_plus * 0.05
        if "elite_world" in state.challenge_modifiers:
            chance += 0.35
        if random.random() < min(0.8, chance):
            count = 2 if state.new_game_plus >= 2 and random.random() < 0.35 else 1
            affixes = random.sample(list(ELITE_AFFIXES), count)
    _apply_elite_affixes(enemy, affixes)
    break_base = enemy.get("break_max", max(60, enemy.get("defense", 10) * 2 + enemy.get("level", 1) * 4))
    if "armored" in enemy.get("_elite_affixes", []):
        break_base = int(break_base * 1.25)
    if enemy.get("ai") == "boss":
        break_base = int(break_base * 1.3)
    break_base = int(break_base * rules.get("break_multiplier", 1.0))
    enemy["max_break"] = max(1, break_base)
    enemy["break"] = enemy["max_break"]
    enemy["broken"] = False
    return enemy


def _announce_battle(enemy, allies, intro, rules, environment):
    ui.title(f"战斗开始: VS {enemy['name']}")
    if intro:
        ui.story(intro)
    elif enemy.get("description"):
        ui.slow_print(enemy["description"])
    if enemy.get("_elite_affixes"):
        descriptions = "；".join(
            f"{ELITE_AFFIXES[affix][0]}：{ELITE_AFFIXES[affix][1]}"
            for affix in enemy["_elite_affixes"]
        )
        ui.slow_print(f"⚠ 精英词缀：{descriptions}")
    ui.slow_print(f"▣ 战场环境：【{environment['name']}】{environment['description']}")
    ui.slow_print(f"◎ 战斗目标：{_objective_progress(rules, 1, {}, enemy)}")
    for ally in allies:
        ui.slow_print(f"⇒ {ally['name']} 与你并肩而立！")


def _skill_action(state, player, enemy, log):
    skills = []
    gear_bonuses = log.get("gear_bonuses") or equipment.combat_bonuses(state)
    for skill_id in loadout.equipped_skill_ids(state):
        if skill_id not in state.skills_db:
            continue
        skill = skill_mastery.apply_upgrade(state, state.skills_db[skill_id])
        skill = equipment.apply_to_skill(skill, gear_bonuses)
        if "scarce_chakra" in state.challenge_modifiers:
            skill["chakra_cost"] = int(skill["chakra_cost"] * 1.2)
        skill = _environment_skill(skill, log.get("environment", ENVIRONMENTS["neutral"]))
        skill = _position_skill(skill, player, log)
        skills.append(skill)
    options = []
    for skill in skills:
        upgrade = f"·{skill['_upgrade_name']}" if skill.get("_upgrade_name") else ""
        options.append(
            f"{skill['name']}{upgrade} (威力{skill['power']}/查克拉{skill['chakra_cost']}) - "
            f"{skill['description']}"
        )
    index = ui.choose("使用哪个技能?", options, allow_cancel=True)
    if index < 0:
        return False
    skill = skills[index]
    if _has_status(player, "fear") and skill["power"] > 60:
        ui.slow_print("恐惧让高威力忍术无法凝聚成形！")
        return False
    if skill["chakra_cost"] > player["chakra"]:
        ui.slow_print("查克拉不足！")
        return False
    if can_act(player):
        result = execute_skill(player, enemy, skill, state, log)
        _apply_break(enemy, _skill_break_damage(skill, result, enemy), log, skill["name"])
        if skill.get("effect") == "expose_risk":
            log["used_future_skill"] = True
    return True


def _escape_action(player, enemy, rules):
    if rules.get("no_escape"):
        ui.slow_print("这场战斗无法逃避！")
        return False, None
    chance = 0.5 + (player["speed"] - enemy["speed"]) * 0.02
    if random.random() < chance:
        ui.slow_print("成功脱离了战斗！")
        return True, "escape"
    ui.slow_print("没能逃掉！")
    return True, None


def _player_action(state, player, enemy, rules, log, allies):
    """执行一次玩家行动，返回需立即结束战斗的结果或 None。"""
    while True:
        actions = ["忍术/体术", "防御/反击", "道具", "契约支援", "逃跑"]
        position = POSITION_NAMES.get(log.get("player_position", "mid"), "中排")
        actions.insert(1, f"调整站位 | {position}")
        if allies:
            order = ALLY_ORDER_NAMES.get(log.get("ally_order", "balanced"), "均衡协战")
            actions.insert(1, f"队友指令 | {order}")
            if party.active_ability_available(allies, log):
                actions.insert(2, "队友奥义 | 路线技能")
        if rules.get("extra_actions"):
            actions = rules["extra_actions"](log) + actions
        choices = [_action_choice(action) for action in actions]
        label = ui.choice_label(choices[ui.choose("你的行动:", choices)])
        if label == "忍术/体术" and _skill_action(state, player, enemy, log):
            return None
        if label.startswith("队友指令"):
            _configure_ally_order(log)
            continue
        if label.startswith("队友奥义"):
            if party.use_active_ability(state, player, enemy, log, allies):
                return None
            continue
        if label.startswith("调整站位"):
            if _change_position(log):
                return None
            continue
        if label == "防御/反击":
            guard_index = ui.choose(
                "选择防御方式",
                [
                    ui.Choice("稳固防御", ("actions", "guard"), "本回合减伤45%，并恢复少量查克拉"),
                    ui.Choice("精准反击", ("actions", "attack"), "成功时减伤65%、反击并削减破势；失败会增伤"),
                ],
                allow_cancel=True,
            )
            if guard_index < 0:
                continue
            if guard_index == 0:
                player["_guard_mode"] = "guard"
                recovered = max(5, player["max_chakra"] // 20)
                old_chakra = player["chakra"]
                player["chakra"] = min(player["max_chakra"], player["chakra"] + recovered)
                ui.slow_print(f"→ 鸣人稳住架势，恢复 {player['chakra'] - old_chakra} 点查克拉。")
            else:
                player["_guard_mode"] = "counter"
                ui.slow_print("→ 鸣人压低重心，等待敌人露出破绽。")
            return None
        if label == "道具" and use_item(state, player):
            return None
        if label == "契约支援" and contract_support(state, player, log, enemy):
            return None
        if label == "逃跑":
            acted, result = _escape_action(player, enemy, rules)
            if acted:
                return result
        elif label not in ("忍术/体术", "防御/反击", "道具", "契约支援") \
                and not label.startswith(("队友指令", "队友奥义", "调整站位")):
            handler = rules.get("action_handler")
            if handler and handler(label, state, player, enemy, log):
                return None


def _finish_battle(state, player, enemy, teammate_ids=None, defer_rewards=False):
    player.pop("_guard_mode", None)
    player.pop("_ally_guard", None)
    if player["hp"] <= 0:
        player["hp"] = 1
        collection.evaluate_achievements(state, announce=True)
        ui.emit_visual_event("battle_end", result="lose")
        return "lose"
    ui.line()
    ui.slow_print(f"★ 战斗胜利！击败了 {enemy['name']}！")
    if not defer_rewards:
        reward = enemy.get("exp_reward", 20)
        state.gain_exp(reward)
        state.gain_ryo(max(20, enemy.get("level", 1) * 18), "战斗报酬")
        party.gain_teammate_exp(state, teammate_ids or [], max(1, reward // 2))
        source_id = enemy.get("_source_id", enemy.get("id", "any"))
        factions.record_progress(state, "defeat", source_id, 1)
        crafting.award_battle_material(state, source_id)
    collection.evaluate_achievements(state, announce=True)
    ui.emit_visual_event("battle_end", result="win")
    return "win"


def _clean_battle_result(player, result):
    player.pop("_guard_mode", None)
    player.pop("_ally_guard", None)
    ui.emit_visual_event("battle_end", result=result)
    return result


def _battle_preparation(state, rules):
    if rules.get("skip_preparation"):
        return
    while True:
        options = [
            ui.Choice("开始战斗", ("actions", "battle_start")),
            ui.Choice("调整技能", ("actions", "loadout"), loadout.summary(state)),
            ui.Choice("忍术强化", ("actions", "train"), skill_mastery.summary(state)),
            ui.Choice("忍具装备", ("actions", "workshop"), equipment.summary(state)),
            ui.Choice("调整同行者", ("actions", "ally_order"), party.party_summary(state)),
            ui.Choice("队友培养", ("actions", "ally_ultimate"), "路线与羁绊"),
        ]
        index = ui.choose("战斗准备", options)
        if index == 0:
            return
        if index == 1:
            loadout.configure_loadout(state)
        elif index == 2:
            skill_mastery.configure_mastery(state)
        elif index == 3:
            equipment.configure_equipment(state)
        elif index == 4:
            party.configure_party(state)
        elif index == 5:
            party.growth_menu(state)


def battle(state, enemy_id, special_rules=None, intro=None):
    """
    主战斗循环。
    special_rules 可含:
      win_condition(state, player, enemy, turn, log) -> str|None
      extra_actions(log) -> [str]
      action_handler(label, state, player, enemy, log) -> bool
      allies: [{"name", "power", "element", "move", "can_heal", "act_rate"}]
      enemy_mods: {stat: +delta}
      objective: {type: survive|break|capture, ...}
      objective_text: 仅显示的目标说明
      break_multiplier: 敌人破势槽倍率
      no_escape / max_turns / timeout_result
    返回: "win" | "lose" | "escape" | 特殊结果字符串
    """
    player = state.player
    rules = special_rules or {}
    if not rules.get("preserve_player_status"):
        player["status"] = []
    player.pop("_guard_mode", None)
    player.pop("_ally_guard", None)
    log = {
        "teamwork": False,
        "used_future_skill": False,
        "break_count": 0,
        "ally_order": "balanced",
    }
    persistent = rules.get("persistent_resources")
    if persistent is not None:
        log["support_used"] = persistent.setdefault("support_used", set())
        log["ally_abilities_used"] = persistent.setdefault("ally_abilities_used", set())
    environment = _prepare_environment(state, rules)
    log["environment"] = environment
    log["player_position"] = rules.get("player_position", "mid")
    if enemy_id not in state.discovered_enemies:
        state.discovered_enemies.append(enemy_id)
    equipment.sync_unlocks(state)
    _battle_preparation(state, rules)
    log["gear_bonuses"] = equipment.combat_bonuses(state)
    enemy = _prepare_enemy(state, enemy_id, rules)
    story_allies = rules.get("allies") or []
    selected_allies = party.combat_allies(state) if rules.get("allow_party", True) else []
    allies = party.merge_allies(story_allies, selected_allies)
    ui.emit_visual_event(
        "battle_start",
        enemy_id=enemy_id,
        enemy_name=enemy["name"],
        boss=enemy.get("ai") == "boss",
        enemy_hp=enemy.get("hp", 0),
        enemy_max_hp=enemy.get("max_hp", enemy.get("hp", 0)),
        enemy_chakra=enemy.get("chakra", 0),
        enemy_max_chakra=enemy.get("max_chakra", enemy.get("chakra", 0)),
        break_value=enemy.get("break", 0),
        break_max=enemy.get("max_break", 0),
        elements=list(enemy.get("elements", [])),
        affixes=list(enemy.get("_elite_affixes", [])),
        environment=environment.get("id", "neutral"),
    )
    _announce_battle(enemy, allies, intro, rules, environment)

    turn = 1
    while player["hp"] > 0 and enemy["hp"] > 0:
        _environment_turn(environment, player, enemy, turn)
        # 特殊胜利条件检查(回合开始)
        if "win_condition" in rules:
            result = rules["win_condition"](state, player, enemy, turn, log)
            if result:
                return _clean_battle_result(player, result)
        objective_result = _check_objective(rules, player, enemy, turn, log)
        if objective_result:
            return _clean_battle_result(player, objective_result)

        enemy_intent = None if enemy.get("broken") else enemy_choose_skill(
            enemy, state.skills_db, player, turn
        )
        ui.emit_visual_event(
            "battle_update",
            enemy_hp=enemy.get("hp", 0),
            enemy_max_hp=enemy.get("max_hp", enemy.get("hp", 0)),
            enemy_chakra=enemy.get("chakra", 0),
            enemy_max_chakra=enemy.get("max_chakra", enemy.get("chakra", 0)),
            intent=_intent_kind(enemy_intent),
            intent_name=enemy_intent.get("name", "") if enemy_intent else "破势中",
            player_status=[status["id"] for status in player.get("status", [])],
            enemy_status=[status["id"] for status in enemy.get("status", [])],
            elements=list(enemy.get("elements", [])),
            affixes=list(enemy.get("_elite_affixes", [])),
            break_value=enemy.get("break", 0),
            break_max=enemy.get("max_break", 0),
        )
        show_battle_status(player, enemy, turn, enemy_intent, rules, log)

        action_result = _player_action(state, player, enemy, rules, log, allies)
        if action_result:
            return _clean_battle_result(player, action_result)

        # 队友协战
        if enemy["hp"] > 0 and allies:
            _allies_act(allies, player, enemy, state, log)

        objective_result = _check_objective(rules, player, enemy, turn, log)
        if objective_result:
            return _clean_battle_result(player, objective_result)

        if enemy["hp"] <= 0:
            break

        # 敌人行动
        if enemy.get("broken"):
            ui.slow_print(f"⇒ {enemy['name']}仍未恢复平衡，本回合行动被打断！")
            enemy["broken"] = False
            enemy["break"] = max(1, int(enemy["max_break"] * 0.55))
        elif can_act(enemy):
            skill = enemy_intent
            sealed = _has_status(enemy, "sealed")
            if not skill or skill["chakra_cost"] > enemy["chakra"] or (sealed and skill["chakra_cost"] > 0):
                ui.slow_print("  ※ 敌人的原定意图被打乱，临时改变了行动！")
                skill = enemy_choose_skill(enemy, state.skills_db, player, turn)
            skill = _environment_skill(skill, environment)
            skill_result = execute_skill(enemy, player, skill, state, log)
            if (
                "venomous" in enemy.get("_elite_affixes", [])
                and skill_result.get("damage", 0) > 0
                and random.random() < 0.35
            ):
                add_status(player, "poison", 3)
                ui.slow_print("  ⚠ 剧毒词缀将毒素注入了伤口！")
            _resolve_counter(player, enemy, skill, skill_result, log)
            if not _death_check(state, player, log):
                break

        player.pop("_guard_mode", None)
        player.pop("_ally_guard", None)

        apply_turn_statuses(player)
        apply_turn_statuses(enemy)
        if not _death_check(state, player, log):
            break
        turn += 1

        if rules.get("max_turns") and turn > rules["max_turns"]:
            if "timeout_result" in rules:
                return _clean_battle_result(player, rules["timeout_result"])
            break

    teammate_ids = [ally["teammate_id"] for ally in allies if ally.get("teammate_id")]
    return _finish_battle(
        state, player, enemy, teammate_ids, defer_rewards=rules.get("defer_rewards", False)
    )


def _finish_enemy_group(state, player, enemies, teammate_ids, defer_rewards=False):
    player.pop("_guard_mode", None)
    player.pop("_ally_guard", None)
    if player["hp"] <= 0:
        player["hp"] = 1
        collection.evaluate_achievements(state, announce=True)
        ui.emit_visual_event("battle_end", result="lose")
        return "lose"
    ui.line()
    names = "、".join(enemy["name"] for enemy in enemies)
    ui.slow_print(f"★ 战斗胜利！敌方小队【{names}】已全部击破！")
    if not defer_rewards:
        reward = sum(enemy.get("exp_reward", 20) for enemy in enemies)
        state.gain_exp(reward)
        state.gain_ryo(sum(max(15, enemy.get("level", 1) * 14) for enemy in enemies), "小队讨伐报酬")
        party.gain_teammate_exp(state, teammate_ids, max(1, reward // 2), bond=2)
        for enemy in enemies:
            source_id = enemy.get("_source_id", enemy.get("id", "any"))
            factions.record_progress(state, "defeat", source_id, 1)
            crafting.award_battle_material(state, source_id)
    collection.evaluate_achievements(state, announce=True)
    ui.emit_visual_event("battle_end", result="win")
    return "win"


def multi_target_battle(state, enemy_ids, special_rules=None, intro=None):
    """同场多目标战斗：玩家每回合可选目标，存活敌人会分别行动。"""
    enemy_specs = [
        {"enemy_id": enemy} if isinstance(enemy, str) else dict(enemy)
        for enemy in enemy_ids
    ]
    if not enemy_specs:
        raise ValueError("多目标战斗至少需要一个敌人")
    if len(enemy_specs) == 1 and set(enemy_specs[0]) == {"enemy_id"}:
        return battle(state, enemy_specs[0]["enemy_id"], special_rules=special_rules, intro=intro)
    missing = [
        spec["enemy_id"] for spec in enemy_specs if spec.get("enemy_id") not in state.enemies_db
    ]
    if missing:
        raise KeyError(f"不存在的敌人: {', '.join(missing)}")

    rules = dict(special_rules or {})
    player = state.player
    if not rules.get("preserve_player_status"):
        player["status"] = []
    player.pop("_guard_mode", None)
    player.pop("_ally_guard", None)
    log = {
        "teamwork": False,
        "used_future_skill": False,
        "break_count": 0,
        "ally_order": "balanced",
    }
    persistent = rules.get("persistent_resources")
    if persistent is not None:
        log["support_used"] = persistent.setdefault("support_used", set())
        log["ally_abilities_used"] = persistent.setdefault("ally_abilities_used", set())
    environment = _prepare_environment(state, rules)
    log["environment"] = environment
    log["player_position"] = rules.get("player_position", "mid")
    for enemy_id in [spec["enemy_id"] for spec in enemy_specs]:
        if enemy_id not in state.discovered_enemies:
            state.discovered_enemies.append(enemy_id)
    equipment.sync_unlocks(state)
    _battle_preparation(state, rules)
    log["gear_bonuses"] = equipment.combat_bonuses(state)
    enemies = []
    for spec in enemy_specs:
        enemy_rules = dict(rules)
        enemy_rules.update(spec.get("special_rules") or {})
        for key in ("enemy_name", "enemy_skills", "enemy_elements", "enemy_mods"):
            if key in spec:
                enemy_rules[key] = spec[key]
        enemies.append(_prepare_enemy(state, spec["enemy_id"], enemy_rules))
    story_allies = rules.get("allies") or []
    selected_allies = party.combat_allies(state) if rules.get("allow_party", True) else []
    allies = party.merge_allies(story_allies, selected_allies)
    teammate_ids = [ally["teammate_id"] for ally in allies if ally.get("teammate_id")]

    ui.emit_visual_event(
        "battle_start",
        enemy_id=rules.get("visual_id", "multi_target"),
        enemy_name=" / ".join(enemy["name"] for enemy in enemies),
        boss=any(enemy.get("ai") == "boss" for enemy in enemies),
        elements=sorted({element for enemy in enemies for element in enemy.get("elements", [])}),
        affixes=[],
        environment=environment.get("id", "neutral"),
        target_count=len(enemies),
    )
    ui.title("战斗开始: VS " + "、".join(enemy["name"] for enemy in enemies))
    if intro:
        ui.story(intro)
    ui.slow_print(f"▣ 战场环境：【{environment['name']}】{environment['description']}")
    ui.slow_print(f"◎ 战斗目标：击败全部 {len(enemies)} 个目标")
    for ally in allies:
        ui.slow_print(f"⇒ {ally['name']} 与你并肩而立！")

    turn = 1
    while player["hp"] > 0 and any(enemy["hp"] > 0 for enemy in enemies):
        living = [enemy for enemy in enemies if enemy["hp"] > 0]
        active = living[0]
        _environment_turn(environment, player, active, turn)
        living = [enemy for enemy in enemies if enemy["hp"] > 0]
        if not living:
            break
        if "win_condition" in rules:
            result = rules["win_condition"](state, player, living[0], turn, log)
            if result:
                return _clean_battle_result(player, result)
        if len(living) > 1:
            target_index = ui.choose(
                "选择本回合的攻击目标",
                [f"{enemy['name']} | HP {max(0, enemy['hp'])}/{enemy['max_hp']}" for enemy in living],
            )
            active = living[target_index]
        else:
            active = living[0]
        ui.slow_print(
            "敌方阵容：" + " | ".join(
                f"{enemy['name']} {max(0, enemy['hp'])}/{enemy['max_hp']}"
                for enemy in living
            )
        )
        intent = None if active.get("broken") else enemy_choose_skill(active, state.skills_db, player, turn)
        show_battle_status(
            player, active, turn, intent,
            {"objective_text": f"击败全部目标（剩余 {len(living)}/{len(enemies)}）"}, log,
        )
        action_result = _player_action(state, player, active, rules, log, allies)
        if action_result:
            return _clean_battle_result(player, action_result)
        if active["hp"] > 0 and allies:
            _allies_act(allies, player, active, state, log)

        for enemy in [unit for unit in enemies if unit["hp"] > 0]:
            if enemy.get("broken"):
                ui.slow_print(f"⇒ {enemy['name']}架势崩溃，本回合行动被打断！")
                enemy["broken"] = False
                enemy["break"] = max(1, int(enemy["max_break"] * 0.55))
                continue
            if not can_act(enemy):
                continue
            skill = enemy_choose_skill(enemy, state.skills_db, player, turn)
            if skill is None:
                continue
            skill = _environment_skill(skill, environment)
            skill_result = execute_skill(enemy, player, skill, state, log)
            if "venomous" in enemy.get("_elite_affixes", []) and skill_result.get("damage", 0) > 0:
                if random.random() < 0.35:
                    add_status(player, "poison", 3)
            _resolve_counter(player, enemy, skill, skill_result, log)
            if not _death_check(state, player, log):
                break
        player.pop("_guard_mode", None)
        player.pop("_ally_guard", None)
        apply_turn_statuses(player)
        for enemy in enemies:
            if enemy["hp"] > 0:
                apply_turn_statuses(enemy)
        if not _death_check(state, player, log):
            break
        turn += 1
        if rules.get("max_turns") and turn > rules["max_turns"]:
            if rules.get("timeout_result"):
                return _clean_battle_result(player, rules["timeout_result"])
            break
    return _finish_enemy_group(
        state, player, enemies, teammate_ids, defer_rewards=rules.get("defer_rewards", False)
    )


def multi_stage_boss_battle(state, phases, intro=None):
    """执行可配置的多阶段 Boss 战；生命与查克拉会跨阶段保留。"""
    phases = list(phases)
    if not phases:
        raise ValueError("多阶段 Boss 战至少需要一个阶段")
    if intro:
        ui.story(intro)
    total = len(phases)
    persistent_resources = {"support_used": set(), "ally_abilities_used": set()}
    for index, phase in enumerate(phases, start=1):
        ui.title(f"Boss 阶段 {index}/{total}：{phase.get('name', '未知形态')}")
        rules = dict(phase.get("special_rules") or {})
        if "visual_id" not in rules:
            visual_id = phase.get("visual_id") or phase.get("enemy_id")
            if not visual_id and phase.get("enemy_ids"):
                first_enemy = phase["enemy_ids"][0]
                visual_id = (
                    first_enemy.get("enemy_id") if isinstance(first_enemy, dict) else first_enemy
                )
            if visual_id:
                rules["visual_id"] = visual_id
        rules["persistent_resources"] = persistent_resources
        rules.setdefault("phase_full_hp", True)
        if index < total:
            rules["defer_rewards"] = True
        if index > 1:
            rules["skip_preparation"] = True
            rules["preserve_player_status"] = True
            recover_hp = int(state.player["max_hp"] * phase.get("transition_heal", 0))
            recover_chakra = int(state.player["max_chakra"] * phase.get("transition_chakra", 0))
            state.player["hp"] = min(state.player["max_hp"], state.player["hp"] + recover_hp)
            state.player["chakra"] = min(
                state.player["max_chakra"], state.player["chakra"] + recover_chakra
            )
        transition = phase.get("transition")
        if transition:
            if callable(transition):
                transition(state, index)
            else:
                ui.story(str(transition))
        if phase.get("enemy_ids"):
            result = multi_target_battle(
                state, phase["enemy_ids"], special_rules=rules, intro=phase.get("intro")
            )
        else:
            result = battle(
                state, phase["enemy_id"], special_rules=rules, intro=phase.get("intro")
            )
        if result != "win":
            return result
    ui.slow_print(f"★ 多阶段决战结束！你突破了全部 {total} 个阶段。")
    return "win"


# 简短别名，便于剧情脚本按语义调用。
multi_battle = multi_target_battle
boss_battle = multi_stage_boss_battle
