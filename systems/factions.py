# -*- coding: utf-8 -*-
"""按世界日刷新的动态委托与阵营声望。"""
import copy
import random

from systems import ui


FACTIONS = {
    "konoha": {"name": "木叶隐村", "unlock": lambda s: True},
    "suna": {"name": "砂隐村", "unlock": lambda s: s.flags.get("shippuden_started", False)},
    "alliance": {"name": "忍者联军", "unlock": lambda s: s.flags.get("summit_done", False)},
}

REPUTATION_RANKS = (
    (0, "陌生"), (20, "友善"), (50, "信赖"), (90, "尊敬"), (140, "英雄"),
)

# progress_event/target 与 record_progress 对应。委托会按章节过滤并随机抽取。
TEMPLATES = (
    {"key": "konoha_patrol", "faction": "konoha", "name": "村外巡逻",
     "event": "patrol", "target": "konoha_forest", "required": 2,
     "objective": "在木叶森林完成 2 次巡查", "chapter": 1, "rep": 8, "exp": 45},
    {"key": "konoha_hunt", "faction": "konoha", "name": "清剿林间威胁",
     "event": "defeat", "target": "any", "required": 3,
     "objective": "在探索中击败任意敌人 3 名", "chapter": 1, "rep": 10, "exp": 60},
    {"key": "konoha_herbs", "faction": "konoha", "name": "医疗班药材征集",
     "event": "gather", "target": "药草", "required": 3,
     "objective": "采集药草 3 株", "chapter": 2, "rep": 9, "exp": 55},
    {"key": "konoha_gate", "faction": "konoha", "name": "大门警戒轮值",
     "event": "patrol", "target": "konoha_gate", "required": 2,
     "objective": "在木叶大门完成 2 次警戒", "chapter": 2, "rep": 8, "exp": 55},
    {"key": "konoha_rogue", "faction": "konoha", "name": "越境忍者追缉",
     "event": "defeat", "target": "rogue_genin", "required": 2,
     "objective": "击败越境的迷途下忍 2 名", "chapter": 2, "rep": 11, "exp": 75},
    {"key": "konoha_venom", "faction": "konoha", "name": "毒物样本",
     "event": "gather", "target": "毒囊", "required": 2,
     "objective": "为医院收集毒囊 2 份", "chapter": 3, "rep": 10, "exp": 70},
    {"key": "konoha_ruins", "faction": "konoha", "name": "族地夜巡",
     "event": "patrol", "target": "uchiha_ruins", "required": 2,
     "objective": "在宇智波族地遗址巡查 2 次", "chapter": 5, "rep": 12, "exp": 85},
    {"key": "suna_iron", "faction": "suna", "name": "砂铁补给",
     "event": "gather", "target": "铁砂", "required": 2,
     "objective": "收集铁砂 2 份", "chapter": 7, "rep": 10, "exp": 80},
    {"key": "suna_hunt", "faction": "suna", "name": "风之国商路护卫",
     "event": "defeat", "target": "any", "required": 4,
     "objective": "击退沿途敌人 4 名", "chapter": 7, "rep": 12, "exp": 90},
    {"key": "suna_patrol", "faction": "suna", "name": "风影塔巡防",
     "event": "patrol", "target": "suna_village", "required": 2,
     "objective": "在砂隐村完成 2 次巡防", "chapter": 7, "rep": 9, "exp": 75},
    {"key": "suna_bones", "faction": "suna", "name": "傀儡关节材料",
     "event": "gather", "target": "兽骨", "required": 3,
     "objective": "为傀儡班收集兽骨 3 份", "chapter": 7, "rep": 10, "exp": 80},
    {"key": "suna_clay", "faction": "suna", "name": "起爆黏土清理",
     "event": "gather", "target": "起爆黏土", "required": 2,
     "objective": "回收晓遗留的起爆黏土 2 份", "chapter": 8, "rep": 12, "exp": 95},
    {"key": "suna_elite", "faction": "suna", "name": "沙海强敌",
     "event": "defeat", "target": "any", "required": 5,
     "objective": "在高危区域击败敌人 5 名", "chapter": 8, "rep": 14, "exp": 110},
    {"key": "suna_medical", "faction": "suna", "name": "千代的药方",
     "event": "gather", "target": "药草", "required": 4,
     "objective": "按千代留下的药方采集药草 4 株", "chapter": 8, "rep": 11, "exp": 90},
    {"key": "alliance_front", "faction": "alliance", "name": "前线肃清",
     "event": "defeat", "target": "any", "required": 5,
     "objective": "击败前线敌人 5 名", "chapter": 10, "rep": 15, "exp": 120},
    {"key": "alliance_crystal", "faction": "alliance", "name": "封印班补给",
     "event": "gather", "target": "查克拉晶片", "required": 3,
     "objective": "收集查克拉晶片 3 枚", "chapter": 10, "rep": 14, "exp": 110},
    {"key": "alliance_patrol", "faction": "alliance", "name": "前线换防",
     "event": "patrol", "target": "war_front", "required": 3,
     "objective": "在联军前线完成 3 次换防巡查", "chapter": 10, "rep": 13, "exp": 105},
    {"key": "alliance_zetsu", "faction": "alliance", "name": "白绝残党",
     "event": "defeat", "target": "white_zetsu", "required": 3,
     "objective": "识破并击败白绝残党 3 名", "chapter": 10, "rep": 16, "exp": 130},
    {"key": "alliance_iron", "faction": "alliance", "name": "工事修复",
     "event": "gather", "target": "铁砂", "required": 4,
     "objective": "为工兵部队收集铁砂 4 份", "chapter": 10, "rep": 13, "exp": 110},
    {"key": "alliance_clay", "faction": "alliance", "name": "爆破班库存",
     "event": "gather", "target": "起爆黏土", "required": 3,
     "objective": "向联军爆破班提交起爆黏土 3 份", "chapter": 10, "rep": 15, "exp": 125},
    {"key": "alliance_veteran", "faction": "alliance", "name": "战场清道夫",
     "event": "defeat", "target": "any", "required": 7,
     "objective": "清除任意战场威胁 7 名", "chapter": 10, "rep": 18, "exp": 160},
)

FACTION_CHAINS = {
    "konoha": (
        {"id": "konoha_oath_1", "name": "没有名字的巡逻路", "rep_required": 0,
         "event": "patrol", "target": "konoha_forest", "required": 2,
         "objective": "沿鸣人童年常走的林路巡查两次", "rep": 12, "exp": 80,
         "intro": "伊鲁卡把旧巡逻图交给你：真正的火之意志，先从没人看见的小路开始。",
         "completion": "你补好了褪色的路标。第二天，忍校孩子沿着它平安回了家。"},
        {"id": "konoha_oath_2", "name": "医院窗下的名单", "rep_required": 15,
         "event": "gather", "target": "药草", "required": 4,
         "objective": "为战后病房收集 4 株药草", "rep": 14, "exp": 95,
         "intro": "静音递来一张没有忍者姓名、只有家属人数的名单。每一株药都有人等。",
         "completion": "药香在病房散开，名单上的墨迹被一行行划去。"},
        {"id": "konoha_oath_3", "name": "根部留下的影子", "rep_required": 35,
         "event": "defeat", "target": "any", "required": 4,
         "objective": "清除藏在村外的根部遗留据点守卫", "rep": 16, "exp": 120,
         "intro": "卡卡西找到一座没有编号的地下入口。有些黑暗不会随旧时代自动消失。",
         "completion": "最后一张没有姓名的任务卷轴在火里卷曲。木叶少了一间不见天日的牢房。"},
        {"id": "konoha_oath_4", "name": "宇智波最后的灯", "rep_required": 65,
         "event": "patrol", "target": "uchiha_ruins", "required": 3,
         "objective": "连续守护宇智波族地遗址 3 次", "rep": 18, "exp": 145,
         "intro": "佐助没有请求你同行，只在族地门前留下一盏灯。你知道那就是邀请。",
         "completion": "第三夜结束时，废墟里第一次亮起不为悼亡、只为归家的灯。"},
        {"id": "konoha_oath_5", "name": "火影岩下的回答", "rep_required": 100,
         "event": "defeat", "target": "any", "required": 6,
         "objective": "完成六次村外高危威胁处置", "rep": 24, "exp": 200,
         "intro": "纲手把火影直属委任状拍在桌上：不是因为你会赢，而是因为村民相信你会回来。",
         "completion": "任务报告没有伤亡一栏。火影岩下，有孩子开始模仿你的护额系法。"},
    ),
    "suna": (
        {"id": "suna_oath_1", "name": "沙中第一口井", "rep_required": 0,
         "event": "gather", "target": "铁砂", "required": 3,
         "objective": "收集 3 份铁砂修复商路水井", "rep": 12, "exp": 90,
         "intro": "我爱罗说，沙漠里一口能出水的井，比一场胜仗更像奇迹。",
         "completion": "清水涌出时，商队没有欢呼，只安静地排起长队。那份安静比欢呼更重。"},
        {"id": "suna_oath_2", "name": "没有线的傀儡", "rep_required": 15,
         "event": "gather", "target": "兽骨", "required": 4,
         "objective": "为孤儿工坊收集 4 份傀儡关节材料", "rep": 14, "exp": 105,
         "intro": "勘九郎在教战争孤儿制作玩具傀儡。这一次，查克拉线不用于杀人。",
         "completion": "第一只木鸟歪歪扭扭飞过屋顶，孩子们追着它跑了半条街。"},
        {"id": "suna_oath_3", "name": "赤砂之后", "rep_required": 35,
         "event": "defeat", "target": "any", "required": 4,
         "objective": "击退盗取禁忌傀儡术的流浪忍者", "rep": 16, "exp": 130,
         "intro": "蝎留下的卷轴在黑市出现。千代的名字不该再被装进新的杀人机器。",
         "completion": "禁术卷轴被封入风影塔。勘九郎只留下其中关于义肢的三页。"},
        {"id": "suna_oath_4", "name": "风影不在的三天", "rep_required": 65,
         "event": "patrol", "target": "suna_village", "required": 3,
         "objective": "在我爱罗出访期间守卫砂隐 3 次", "rep": 18, "exp": 155,
         "intro": "我爱罗第一次把整座村子的后背交给外村忍者。长老们都在看。",
         "completion": "三天无事。长老院的任务评价只有两个字：可信。"},
        {"id": "suna_oath_5", "name": "沙海共同防线", "rep_required": 100,
         "event": "defeat", "target": "any", "required": 7,
         "objective": "与砂忍共同清除七处跨境威胁", "rep": 24, "exp": 215,
         "intro": "边界地图上不再画木叶与砂隐的分界，只画需要共同守住的水源和村镇。",
         "completion": "联合巡逻队换下两面旗，升起一面画着叶与沙的新旗。"},
    ),
    "alliance": (
        {"id": "alliance_oath_1", "name": "不同护额的同一班", "rep_required": 0,
         "event": "patrol", "target": "war_front", "required": 2,
         "objective": "带领混编小队完成两次前线巡查", "rep": 12, "exp": 110,
         "intro": "五个村子的年轻忍者第一次被编进同一个班。没人知道该听谁的口令。",
         "completion": "归营时，他们喊的是同一个报数节拍。"},
        {"id": "alliance_oath_2", "name": "白绝识别课", "rep_required": 15,
         "event": "defeat", "target": "white_zetsu", "required": 3,
         "objective": "识破并击败 3 名伪装白绝", "rep": 14, "exp": 135,
         "intro": "真正可靠的识别方式不是暗号，而是记得同伴那些无法复制的小习惯。",
         "completion": "三次伪装都被识破。混编小队开始真正记住彼此。"},
        {"id": "alliance_oath_3", "name": "无国籍的医疗帐", "rep_required": 35,
         "event": "gather", "target": "药草", "required": 5,
         "objective": "为不区分村籍的医疗帐收集 5 株药草", "rep": 16, "exp": 150,
         "intro": "医疗帐入口摘掉了五村标志。躺进去的人只有一种身份：伤员。",
         "completion": "最后一份药分给了曾经的敌村忍者，没有人提出异议。"},
        {"id": "alliance_oath_4", "name": "陨石坑里的名字", "rep_required": 65,
         "event": "gather", "target": "查克拉晶片", "required": 5,
         "objective": "回收 5 枚查克拉晶片修复慰灵碑", "rep": 18, "exp": 175,
         "intro": "陨石抹平了墓碑，却抹不掉应该被记住的名字。",
         "completion": "五种文字被刻在同一块碑上。风吹过时，纸花同时响起。"},
        {"id": "alliance_oath_5", "name": "战争之后的第一战", "rep_required": 100,
         "event": "defeat", "target": "any", "required": 8,
         "objective": "阻止八次试图重燃五国冲突的袭击", "rep": 24, "exp": 240,
         "intro": "有人认为联盟会随战争结束而解散。你要证明和平也值得共同作战。",
         "completion": "最后一处烽火被踩灭。联军没有解散，而是改名为五国共同防卫队。"},
    ),
}

RANK_REWARDS = {
    "konoha": {
        20: {"items": {"回复丹": 2}, "label": "医疗班定期补给"},
        50: {"gear": "will_of_fire_charm", "label": "火之意志护符"},
        90: {"stats": {"spirit": 5, "max_hp": 30}, "label": "木叶上忍认可"},
        140: {"fate": 5, "label": "木叶英雄"},
    },
    "suna": {
        20: {"items": {"铁砂": 4}, "label": "砂隐工坊配给"},
        50: {"gear": "suna_guard_mail", "label": "砂之守护甲"},
        90: {"stats": {"defense": 5, "max_chakra": 25}, "label": "风影亲卫认可"},
        140: {"fate": 5, "label": "砂海英雄"},
    },
    "alliance": {
        20: {"items": {"查克拉晶片": 4}, "label": "联军封印班配给"},
        50: {"gear": "alliance_chakra_blade", "label": "联军查克拉刃"},
        90: {"stats": {"attack": 5, "speed": 5}, "label": "联军总队长认可"},
        140: {"fate": 6, "label": "忍界共同英雄"},
    },
}

MAX_ACTIVE = 3
BOARD_SIZE = 3


def reputation_rank(points):
    rank = REPUTATION_RANKS[0][1]
    for threshold, name in REPUTATION_RANKS:
        if points < threshold:
            break
        rank = name
    return rank


def normalize_state(state):
    for faction_id in FACTIONS:
        state.faction_reputation[faction_id] = max(
            0, int(state.faction_reputation.get(faction_id, 0))
        )
    valid = {}
    for quest_id, quest in state.dynamic_quests.items():
        if not isinstance(quest, dict) or quest.get("faction") not in FACTIONS:
            continue
        normalized = copy.deepcopy(quest)
        normalized["progress"] = max(0, int(normalized.get("progress", 0)))
        normalized["required"] = max(1, int(normalized.get("required", 1)))
        normalized.setdefault("status", "offered")
        valid[quest_id] = normalized
    state.dynamic_quests = valid
    valid_story_ids = {quest["id"] for chain in FACTION_CHAINS.values() for quest in chain}
    state.faction_story = {
        quest_id: {
            "status": data.get("status", "active"),
            "progress": max(0, int(data.get("progress", 0))),
        }
        for quest_id, data in state.faction_story.items()
        if quest_id in valid_story_ids and isinstance(data, dict)
    }
    state.faction_rank_rewards = list(dict.fromkeys(state.faction_rank_rewards))
    return valid


def _story_spec(quest_id):
    return next(
        (quest for chain in FACTION_CHAINS.values() for quest in chain if quest["id"] == quest_id),
        None,
    )


def available_story_quests(state):
    """每个已解锁阵营最多展示一条当前手工任务链。"""
    normalize_state(state)
    result = []
    for faction_id, chain in FACTION_CHAINS.items():
        if not FACTIONS[faction_id]["unlock"](state):
            continue
        for index, quest in enumerate(chain):
            saved = state.faction_story.get(quest["id"])
            if saved and saved.get("status") == "completed":
                continue
            previous_done = index == 0 or state.faction_story.get(
                chain[index - 1]["id"], {}
            ).get("status") == "completed"
            if previous_done and state.faction_reputation[faction_id] >= quest["rep_required"]:
                item = copy.deepcopy(quest)
                item["faction"] = faction_id
                item["status"] = saved.get("status", "offered") if saved else "offered"
                item["progress"] = saved.get("progress", 0) if saved else 0
                result.append(item)
            break
    return result


def accept_story_quest(state, quest_id):
    quest = next((item for item in available_story_quests(state) if item["id"] == quest_id), None)
    if not quest or quest["status"] != "offered":
        return False
    if any(data.get("status") == "active" for data in state.faction_story.values()):
        ui.slow_print("同时只能推进一条阵营故事任务。")
        return False
    state.faction_story[quest_id] = {"status": "active", "progress": 0}
    ui.title(f"阵营任务：{quest['name']}")
    ui.story(quest["intro"])
    ui.slow_print(f"◎ 目标：{quest['objective']}")
    return True


def _grant_rank_rewards(state, faction_id):
    from systems import equipment

    points = state.faction_reputation[faction_id]
    for threshold, reward in RANK_REWARDS[faction_id].items():
        reward_id = f"{faction_id}_{threshold}"
        if points < threshold or reward_id in state.faction_rank_rewards:
            continue
        state.faction_rank_rewards.append(reward_id)
        ui.slow_print(
            f"★ {FACTIONS[faction_id]['name']}声望奖励【{reward['label']}】"
        )
        for item, count in reward.get("items", {}).items():
            state.add_item(item, count, cap=99)
        if reward.get("gear"):
            equipment.grant(state, reward["gear"])
        for stat, amount in reward.get("stats", {}).items():
            state.player[stat] += amount
            if stat == "max_hp":
                state.player["hp"] += amount
            if stat == "max_chakra":
                state.player["chakra"] += amount
            ui.slow_print(f"※ {stat} +{amount}")
        if reward.get("fate"):
            state.gain_fate(reward["fate"], reward["label"])


def reputation_perks(state, faction_id):
    points = state.faction_reputation.get(faction_id, 0)
    perks = []
    if points >= 20:
        perks.append("定期补给")
    if points >= 50:
        perks.append("阵营专属忍具")
    if points >= 90:
        perks.append("精英认可属性")
    if points >= 140:
        perks.append("英雄命运奖励")
    return "、".join(perks) or "尚未解锁"


def available_templates(state):
    return [
        template for template in TEMPLATES
        if state.chapter >= template["chapter"] and FACTIONS[template["faction"]]["unlock"](state)
    ]


def refresh_board(state, force=False, rng=None):
    """新的一天生成新委托；已接取委托不会被刷新掉。"""
    normalize_state(state)
    if not force and state.last_dynamic_refresh_day == state.world_day:
        return list(state.dynamic_quests.values())
    state.dynamic_quests = {
        quest_id: quest for quest_id, quest in state.dynamic_quests.items()
        if quest.get("status") == "active"
    }
    randomizer = rng or random
    templates = available_templates(state)
    randomizer.shuffle(templates)
    offered = 0
    for template in templates:
        if offered >= BOARD_SIZE:
            break
        state.dynamic_quest_serial += 1
        quest_id = f"dq_{state.world_day}_{state.dynamic_quest_serial}"
        quest = copy.deepcopy(template)
        quest.update({"id": quest_id, "progress": 0, "status": "offered", "day": state.world_day})
        state.dynamic_quests[quest_id] = quest
        offered += 1
    state.last_dynamic_refresh_day = state.world_day
    return list(state.dynamic_quests.values())


def accept_quest(state, quest_id):
    refresh_board(state)
    quest = state.dynamic_quests.get(quest_id)
    if not quest or quest.get("status") != "offered":
        return False
    active = sum(q.get("status") == "active" for q in state.dynamic_quests.values())
    if active >= MAX_ACTIVE:
        ui.slow_print(f"同时最多承接 {MAX_ACTIVE} 项动态委托。")
        return False
    quest["status"] = "active"
    ui.slow_print(f"★ 已承接动态委托：【{quest['name']}】")
    return True


def add_reputation(state, faction_id, amount, reason=""):
    if faction_id not in FACTIONS:
        return 0
    before = state.faction_reputation.get(faction_id, 0)
    old_rank = reputation_rank(before)
    after = max(0, before + int(amount))
    state.faction_reputation[faction_id] = after
    sign = "+" if amount >= 0 else ""
    tail = f"（{reason}）" if reason else ""
    ui.slow_print(f"♜ {FACTIONS[faction_id]['name']}声望 {sign}{amount}{tail} [当前: {after}]")
    new_rank = reputation_rank(after)
    if new_rank != old_rank:
        ui.slow_print(f"★ 阵营关系提升至【{new_rank}】！")
    _grant_rank_rewards(state, faction_id)
    return after


def complete_quest(state, quest_id):
    quest = state.dynamic_quests.get(quest_id)
    if not quest or quest.get("status") != "active":
        return False
    quest["status"] = "completed"
    ui.slow_print(f"★ 动态委托完成：【{quest['name']}】")
    state.gain_exp(quest.get("exp", 0))
    state.gain_ryo(max(80, quest.get("exp", 0) * 2), "动态委托")
    state.gain_fate(1, "动态委托")
    add_reputation(state, quest["faction"], quest.get("rep", 0), quest["name"])
    return True


def record_progress(state, event, target="any", count=1):
    """记录战斗、采集或巡逻事件，返回刚完成的委托 id。"""
    refresh_board(state)
    completed = []
    for quest_id, quest in list(state.dynamic_quests.items()):
        if quest.get("status") != "active" or quest.get("event") != event:
            continue
        if quest.get("target", "any") not in ("any", target):
            continue
        quest["progress"] = min(quest["required"], quest.get("progress", 0) + max(0, count))
        ui.slow_print(
            f"※ 委托进度【{quest['name']}】{quest['progress']}/{quest['required']}"
        )
        if quest["progress"] >= quest["required"] and complete_quest(state, quest_id):
            completed.append(quest_id)
    for quest_id, saved in list(state.faction_story.items()):
        if saved.get("status") != "active":
            continue
        quest = _story_spec(quest_id)
        if not quest or quest["event"] != event or quest.get("target", "any") not in ("any", target):
            continue
        saved["progress"] = min(quest["required"], saved.get("progress", 0) + max(0, count))
        ui.slow_print(f"※ 阵营任务【{quest['name']}】{saved['progress']}/{quest['required']}")
        if saved["progress"] >= quest["required"]:
            saved["status"] = "completed"
            faction_id = next(fid for fid, chain in FACTION_CHAINS.items() if quest in chain)
            ui.title(f"阵营任务完成：{quest['name']}")
            ui.story(quest["completion"])
            state.gain_exp(quest["exp"])
            state.gain_ryo(quest["exp"] * 3, "阵营故事任务")
            state.gain_fate(2, "阵营故事任务")
            add_reputation(state, faction_id, quest["rep"], quest["name"])
            completed.append(quest_id)
    return completed


def show_board(state):
    refresh_board(state)
    for faction_id in FACTIONS:
        if FACTIONS[faction_id]["unlock"](state):
            _grant_rank_rewards(state, faction_id)
    while True:
        quests = [q for q in state.dynamic_quests.values() if q.get("status") != "completed"]
        story_quests = available_story_quests(state)
        rep = " | ".join(
            f"{data['name']} {state.faction_reputation[fid]}·{reputation_rank(state.faction_reputation[fid])}"
            for fid, data in FACTIONS.items() if data["unlock"](state)
        )
        options = [
            ui.Choice("返回", ("actions", "retreat")),
            ui.Choice("查看阵营阶位奖励", ("actions", "faction")),
        ]
        entries = [("return", None), ("rewards", None)]
        for quest in story_quests:
            marker = "◆进行中" if quest["status"] == "active" else "◇故事"
            faction = FACTIONS[quest["faction"]]["name"]
            asset_id = {"gather": "gather", "defeat": "attack", "patrol": "observe"}.get(
                quest["event"], "quests"
            )
            options.append(ui.Choice(
                f"{marker} [{faction}] {quest['name']}",
                ("actions", asset_id),
                quest["objective"],
                f"{quest['progress']}/{quest['required']}",
            ))
            entries.append(("story", quest))
        for quest in quests:
            marker = "▶" if quest["status"] == "active" else "○"
            faction = FACTIONS[quest["faction"]]["name"]
            asset_id = {"gather": "gather", "defeat": "attack", "patrol": "observe"}.get(
                quest["event"], "quests"
            )
            options.append(ui.Choice(
                f"{marker} [{faction}] {quest['name']}",
                ("actions", asset_id),
                quest["objective"],
                f"{quest['progress']}/{quest['required']}",
            ))
            entries.append(("dynamic", quest))
        index = ui.choose(f"动态委托板 | {rep}", options)
        kind, quest = entries[index]
        if kind == "return":
            return
        if kind == "rewards":
            ui.line()
            for faction_id, data in FACTIONS.items():
                if data["unlock"](state):
                    points = state.faction_reputation[faction_id]
                    ui.slow_print(
                        f"{data['name']}：{points}·{reputation_rank(points)} | "
                        f"已解锁：{reputation_perks(state, faction_id)}"
                    )
            continue
        if kind == "story" and quest["status"] == "offered":
            accept_story_quest(state, quest["id"])
        elif kind == "dynamic" and quest["status"] == "offered":
            accept_quest(state, quest["id"])
        else:
            ui.slow_print("该委托正在进行中。")
