# -*- coding: utf-8 -*-
"""九命一系契约系统。"""
from systems import ui

CONTRACT_LEVELS = {
    0: ("未契约", "尚未缔结契约"),
    1: ("初契", "可感知彼此生命状态"),
    2: ("同心", "可共享少量生命力"),
    3: ("牵命", "可借用一项基础天赋"),
    4: ("共鸣", "解锁支援技能强化"),
    5: ("命桥", "可在战斗中发动联合技能"),
    6: ("归心", "可进入【桃源】长时间休养"),
    7: ("命织", "可干涉小型命运事件"),
    8: ("一系", "可共同抵御死亡命运"),
    9: ("九命同归", "解锁终极命运改写技能"),
}


BOND_NAMES = {"affection": "好感", "trust": "信任",
              "safety": "安全感", "fate_resonance": "命运共鸣"}

TRIAL_LEVELS = {
    3: ("牵命·理解试炼", "理解对方最想守住的事物"),
    5: ("命桥·协同试炼", "在命线幻境中完成一次并肩战斗"),
    8: ("一系·抗死试炼", "共同承受最接近死亡的命运压力"),
    9: ("九命同归·归命试炼", "以完整羁绊回答最终誓言"),
}

TRIAL_THEMES = {
    "kushina": {"symbol": "赤色锁链", "truth": "让孩子拥有可以回去的家",
                "fear": "再次只能隔着封印看孩子独自长大", "oath": "母子不再被死亡分开"},
    "rin": {"symbol": "掌心医疗光", "truth": "让每个逞强的人都能平安回来",
            "fear": "自己的死亡再次成为别人坠入黑暗的理由", "oath": "温柔不再以牺牲自己为代价"},
    "tsunade": {"symbol": "百豪之印", "truth": "让下一代不必重复失去",
                "fear": "赌上的人又一次倒在自己面前", "oath": "这一次所有筹码都活着离场"},
    "sakura": {"symbol": "樱色拳风", "truth": "成为能保护同伴而非只被保护的人",
               "fear": "伸出的手永远赶不上离去的背影", "oath": "第七班三个人一个都不少"},
    "shizune": {"symbol": "银针与药香", "truth": "让照顾所有人的人也被人照顾",
                "fear": "忙着救人时忘记自己同样值得活下去", "oath": "安稳日子不再只是短暂停留"},
    "hinata": {"symbol": "白眼柔光", "truth": "走在所爱之人身边而不是身后",
               "fear": "勇气永远只差最后一步", "oath": "无论多少目光都一起向前"},
    "konan": {"symbol": "不会沉的纸花", "truth": "让和平从口号变成可以生活的日常",
              "fear": "最后一张纸也只能用来写同伴的讣告", "oath": "纸花从此只传平安"},
    "mei": {"symbol": "雾中的熔光", "truth": "彻底结束血雾留给下一代的诅咒",
            "fear": "改革只换来另一种更体面的暴力", "oath": "雾散之后仍敢把后背交给他人"},
    "gaia": {"symbol": "大地的心跳", "truth": "托住每一个疲惫却仍想前行的孩子",
             "fear": "土地再次只长坟墓不长花", "oath": "九条命线都拥有落脚之地"},
}

TRIAL_ENEMIES = {
    "kushina": "training_dummy", "rin": "training_dummy", "tsunade": "rogue_genin",
    "sakura": "training_dummy", "shizune": "rogue_genin", "hinata": "training_dummy",
    "konan": "akatsuki_pawn", "mei": "akatsuki_pawn", "gaia": "white_zetsu",
}


def add_bond(state, cid, gains):
    """契约四维加值(封顶100),打印实际变化。gains: {key: n}。"""
    c = state.contracts[cid]
    parts = []
    for key, n in gains.items():
        old = c[key]
        c[key] = max(0, min(100, old + n))
        if c[key] != old:
            parts.append(f"{BOND_NAMES[key]} +{c[key] - old}")
    if parts:
        ui.slow_print(f"♥ {c['name']}·{' '.join(parts)}"
                      f" [{c['affection']}/{c['trust']}/{c['safety']}/{c['fate_resonance']}]")
    else:
        ui.slow_print(f"♥ {c['name']}的羁绊已然圆满,无需更多言语。")


def can_contract(target):
    """契约判定：好感≥70 信任≥80 安全感≥80 命运共鸣≥60。"""
    return (target["affection"] >= 70 and target["trust"] >= 80
            and target["safety"] >= 80 and target["fate_resonance"] >= 60)


def level_up_cost(state, level):
    """提升到 level+1 级所需命运点。契约之树·深化可降低消耗。"""
    cost = (level + 1) * 2
    if state.has_building("tree_boost"):
        cost = max(2, cost - 2)
    return cost


def grant_level(state, cid, target_level, reason=""):
    """剧情赠予契约等级(只升不降)。"""
    c = state.contracts[cid]
    if not c["unlocked"] or c["contract_level"] >= target_level:
        return
    c["contract_level"] = target_level
    name, desc = CONTRACT_LEVELS[target_level]
    tail = f"({reason})" if reason else ""
    ui.slow_print(f"★ 命线共鸣加深！{c['name']} 契约等级提升至 {target_level}【{name}】{tail}")
    ui.slow_print(f"   {desc}")


def trial_key(cid, target_level):
    return f"{cid}_{target_level}"


def trial_completed(state, cid, target_level):
    return trial_key(cid, target_level) in state.contract_trials


def run_trial(state, c, target_level):
    """执行关键契约等级前置试炼，成功后记录但不直接升级。"""
    if target_level not in TRIAL_LEVELS or trial_completed(state, c["id"], target_level):
        return True
    theme = TRIAL_THEMES[c["id"]]
    title, goal = TRIAL_LEVELS[target_level]
    ui.title(f"契约试炼：{c['name']} · {title}")
    ui.slow_print(f"◎ {goal}")

    success = False
    if target_level == 3:
        ui.story(
            f"命线化作【{theme['symbol']}】，将一段没有说出口的愿望放在你面前。\n"
            f"这不是力量测试。你必须真正理解 {c['name']}。"
        )
        answer = ui.choose("这条命线真正想守住的是——", [
            theme["truth"], "获得足以压倒所有敌人的力量", "让过去的一切像从未发生过",
        ])
        success = answer == 0
    elif target_level == 5:
        from systems import battle

        ui.story(
            f"【{theme['symbol']}】在桃源中展开一座命线幻境。"
            f"只有把彼此的节奏当作自己的呼吸，才能击碎出口。"
        )
        level = state.player["level"]
        result = battle.battle(
            state, TRIAL_ENEMIES[c["id"]],
            special_rules={
                "no_escape": True, "defer_rewards": True, "enemy_name": f"命线幻影·{c['name']}",
                "enemy_mods": {"hp": level * 10, "attack": max(0, level // 2)},
                "objective_text": f"与{c['name']}心意同步，击碎命线幻影",
            },
            intro=f"{c['name']}的查克拉沿命线与你并肩。此战不能只靠一个人。",
        )
        success = result == "win"
    elif target_level == 8:
        from systems import battle

        ui.story(
            f"命线让你看见 {c['name']} 最深的恐惧：{theme['fear']}。\n"
            "你不能击败死亡，只能证明在死亡逼近时仍不会松手。"
        )
        result = battle.battle(
            state, TRIAL_ENEMIES[c["id"]],
            special_rules={
                "no_escape": True, "defer_rewards": True,
                "enemy_name": f"死亡命运·{c['name']}",
                "enemy_mods": {"attack": max(8, state.player["level"])},
                "objective": {"type": "survive", "turns": 3, "result": "survived"},
                "objective_text": "与命线共同承受三回合死亡压力",
            },
        )
        success = result == "survived"
    else:
        minimum = min(c["affection"], c["trust"], c["safety"], c["fate_resonance"])
        if minimum < 80:
            ui.slow_print(f"四项契约羁绊至少需要 80；当前最低为 {minimum}。")
            return False
        ui.story(
            f"契约之树询问最后一个问题。{c['name']}没有看树，只看着你。\n"
            f"你们共同给出的誓言是：{theme['oath']}。"
        )
        answer = ui.choose("是否愿意让这份誓言承担真实世界的重量?", ["愿意", "还需要时间"])
        success = answer == 0

    if success:
        state.contract_trials.append(trial_key(c["id"], target_level))
        state.gain_fate(1, f"{c['name']}契约试炼")
        ui.slow_print(f"★ 试炼通过！已获得提升至契约 Lv.{target_level} 的资格。")
    else:
        ui.slow_print("试炼尚未通过。命线没有断，它会等待你再次尝试。")
    return success


def _level_perk(state, c):
    """契约升级的属性成长。"""
    p = state.player
    lv = c["contract_level"]
    if lv == 2:
        p["max_hp"] += 20
        p["hp"] += 20
        ui.slow_print("※ 生命共鸣加深，鸣人生命上限 +20！")
    elif lv == 3:
        if c["id"] == "kushina":
            p["seal_art"] += 5
            ui.slow_print("※ 借用玖辛奈的封印术理解力，封印术 +5！")
        elif c["id"] == "rin":
            p["sense"] += 5
            ui.slow_print("※ 借用琳的医疗感知，感知 +5！")
        elif c["id"] == "tsunade":
            p["chakra_control"] += 3
            p["max_hp"] += 15
            ui.slow_print("※ 借用纲手的查克拉精密操控，查克拉控制 +3、生命上限 +15！")
        elif c["id"] == "sakura":
            p["attack"] += 3
            p["chakra_control"] += 2
            ui.slow_print("※ 借用小樱的怪力要诀与查克拉精算，攻击 +3、查克拉控制 +2！")
        elif c["id"] == "shizune":
            p["chakra_control"] += 3
            p["sense"] += 2
            ui.slow_print("※ 借用静音的医疗精密度，查克拉控制 +3、感知 +2！")
        elif c["id"] == "hinata":
            p["sense"] += 4
            p["speed"] += 2
            ui.slow_print("※ 借用雏田的白眼感知与柔步，感知 +4、速度 +2！")
        elif c["id"] == "konan":
            p["speed"] += 4
            ui.slow_print("※ 借用小南的纸翼轻盈，速度 +4！")
        elif c["id"] == "mei":
            p["attack"] += 3
            p["max_chakra"] += 15
            ui.slow_print("※ 借用照美冥的血继强度，攻击 +3、查克拉上限 +15！")
        else:
            p["fate_power"] += 2
            ui.slow_print("※ 命线深处传来古老的力量，命运力 +2！")
    elif lv == 4:
        ui.slow_print(f"※ 【{c['support_skill_name']}】的支援效果得到强化！")
    elif lv == 5:
        ui.slow_print("※ 解锁羁绊联合技！(战斗中通过「契约支援」发动)")
    elif lv == 6:
        p["max_chakra"] += 30
        p["chakra"] += 30
        ui.slow_print("※ 命线归心，查克拉上限 +30！")
    elif lv == 7:
        state.gain_fate(2, "命织·命运的丝线开始听从你")
    elif lv == 8:
        ui.slow_print("※ 【一系】达成——濒死时，契约者们将共同抵御死亡命运(消耗2命运点)！")
    elif lv == 9:
        p["max_hp"] += 50
        p["hp"] += 50
        p["fate_power"] += 5
        ui.slow_print("※ 【九命同归】！生命上限 +50，命运力 +5。命运改写的终极权柄已然在握。")


def show_contract_menu(state):
    ui.title("九命一系 · 契约之树")
    ui.story("""
巨大的契约之树在桃源中央静静伫立，
九条淡金色的命线自树心延伸，一部分已经亮起温暖的光。
""")
    while True:
        contracts = list(state.contracts.values())
        opts = []
        for c in contracts:
            lv_name, _ = CONTRACT_LEVELS[c["contract_level"]]
            status = f"契约等级 {c['contract_level']}【{lv_name}】" if c["unlocked"] else "未觉醒"
            opts.append(f"{c['name']} - {status}")
        opts.append("查看契约等级一览")
        idx = ui.choose(f"(持有命运点: {state.fate_points})", opts, allow_cancel=True)
        if idx < 0:
            return
        if idx == len(contracts):
            ui.line()
            for lv, (name, desc) in CONTRACT_LEVELS.items():
                if lv > 0:
                    print(f"  {lv}【{name}】{desc}")
            ui.pause()
            continue
        inspect_contract(state, contracts[idx])


def inspect_contract(state, c):
    ui.line()
    lv = c["contract_level"]
    lv_name, lv_desc = CONTRACT_LEVELS[lv]
    print(f"  {c['name']} 「{c['title']}」")
    print(f"  契约等级: {lv}【{lv_name}】- {lv_desc}")
    print(f"  好感 {c['affection']} | 信任 {c['trust']} | 安全感 {c['safety']} | 命运共鸣 {c['fate_resonance']}")
    print(f"  支援技能: {c['support_skill_name']} - {c['support_desc']}")
    print(f"  {c['note']}")
    ui.line()
    if not c["unlocked"]:
        if c["id"] == "tsunade" and state.flags.get("tsunade_tougen_invited") and can_contract(c):
            _tsunade_ceremony(state, c)
            return
        ui.slow_print("这条命线尚未觉醒。命运会在剧情中指引你。")
        ui.pause()
        return
    if lv >= 9:
        ui.slow_print("这条命线已抵达【九命同归】的境界。")
        ui.pause()
        return
    target_level = lv + 1
    if target_level in TRIAL_LEVELS and not trial_completed(state, c["id"], target_level):
        title, _ = TRIAL_LEVELS[target_level]
        if ui.choose(f"提升至 Lv.{target_level} 前需完成【{title}】", ["开始试炼", "稍后再说"]) == 0:
            run_trial(state, c, target_level)
        ui.pause()
        return
    cost = level_up_cost(state, lv)
    if ui.choose(f"消耗 {cost} 命运点，提升契约等级?", ["提升", "算了"]) == 0:
        if state.fate_points < cost:
            ui.slow_print("命运点不足。")
        else:
            state.fate_points -= cost
            c["contract_level"] += 1
            new_name, new_desc = CONTRACT_LEVELS[c["contract_level"]]
            ui.slow_print(f"★ 契约之树上，属于 {c['name']} 的命线亮起了新的光辉！")
            ui.slow_print(f"★ 契约等级提升至 {c['contract_level']}【{new_name}】: {new_desc}")
            _level_perk(state, c)
    ui.pause()


def _tsunade_ceremony(state, c):
    """纲手的契约仪式——首位通过正规判定缔结的非固定契约者。"""
    ui.story("""
契约之树的第三条命线，正微微震颤着，泛出淡金色的微光。

树影里传来熟悉的、带着酒气的轻笑。

「喂，小鬼。」纲手抱着手臂走出来，望着头顶的星空湖，
「这地方……比我这些年住过的任何赌场旅馆都让人安心。」

「所谓九命一系——是要我这种赌输了一辈子的女人，
 把最后的筹码押在你身上?」

鸣人摇头，认真地说:

「不是押在我身上。是我们互相把命交给对方保管。
 奶奶……不对，纲手姐。这个契约里没有输家。」

「……哈，嘴上功夫见长啊。」

她伸出手指，屈指在鸣人额头轻轻一弹——
和那一天，赌约达成时一模一样。

『行。老娘这条命，第三次——押你赢。』
""")
    c["unlocked"] = True
    c["contract_level"] = 1
    c["location"] = "konoha"
    c["note"] = "第三位契约者。传说中的医忍，如今守护着木叶，也守护着这个家。"
    state.gain_fate(3, "第三契约·传说的医忍")
    ui.slow_print("★ 纲手契约达成!契约等级 1【初契】")
    ui.slow_print("★ 战斗中可呼唤契约支援【百豪之守】")
    ui.pause()
