# -*- coding: utf-8 -*-
"""各主要地点的可重复随机事件池。"""
import random

from systems import ui
from systems.time_system import period_name


def _event(event_id, location, title, text, effects=None, periods=None, cooldown=4, once=False,
           min_chapter=1, chain=None, stage=0):
    return {
        "id": event_id,
        "location": location,
        "title": title,
        "text": text,
        "effects": effects or {},
        "periods": periods,
        "cooldown": cooldown,
        "once": once,
        "min_chapter": min_chapter,
        "chain": chain,
        "stage": stage,
    }


EVENTS = [
    _event("home_milk", "naruto_home", "过期牛奶", "你顺手清理了冰箱，终于让这间小公寓像个真正的家。", {"belonging": 1}),
    _event("home_dream", "naruto_home", "前世的梦", "夜色里，一些前世的记忆浮上心头。你记下了一个可能改变未来的细节。", {"fate": 1}, periods=("夜晚",), cooldown=8),
    _event("academy_cleanup", "ninja_academy", "放学后的教室", "你帮伊鲁卡收拾了教室，听他讲了一会儿学生们的趣事。", {"belonging": 1}, periods=("黄昏", "夜晚")),
    _event("academy_notes", "ninja_academy", "基础课笔记", "一本遗落的课堂笔记里，有不少被你忽略过的基础。", {"exp": 18}),
    _event("office_errand", "hokage_office", "火影的跑腿任务", "你帮忙送了一摞文件，也顺便熟悉了村子的运作方式。", {"village_trust": 1}),
    _event("office_intel", "hokage_office", "被风吹起的情报", "桌角的情报露出一行关键地名，你不动声色地记在了心里。", {"fate": 1}, cooldown=9),
    _event("ichiraku_extra", "ichiraku", "手打大叔的加量", "「今天修行很辛苦吧？」大叔笑着多放了一勺叉烧。", {"heal": 0.25, "belonging": 1}),
    _event("ichiraku_rumor", "ichiraku", "拉面摊的闲谈", "客人们的闲谈里夹着村子最新的传闻，真假参半，却也值得留心。", {"village_trust": 1}),
    _event("training_marks", "training_ground_7", "木桩上的新痕", "你沿着卡卡西留下的攻击痕迹反推动作，对力道有了新理解。", {"exp": 25}),
    _event("training_team", "training_ground_7", "临时对练", "路过的同期生陪你拆了几招，一个人的忍道也可以有很多同行者。", {"trust": 1, "exp": 15}),
    _event("hospital_supplies", "konoha_hospital", "药品搬运", "你帮护士把新到的药品搬进仓库，得到了一份谢礼。", {"item": ("回复丹", 1), "village_trust": 1}),
    _event("hospital_rooftop", "konoha_hospital", "天台的风", "短暂的安静让你重新理清了查克拉的流动。", {"chakra": 0.3}),
    _event("rock_sunrise", "hokage_rock", "火影岩日出", "晨光从四代目的石像后升起，照亮整座村子。", {"fate": 1, "belonging": 1}, periods=("清晨",), cooldown=7),
    _event("rock_graffiti", "hokage_rock", "被擦掉的涂鸦", "看着当年涂鸦留下的淡淡印记，你忍不住笑了。", {"belonging": 1}),
    _event("uchiha_cat", "uchiha_ruins", "族地里的野猫", "一只黑猫从团扇族徽下钻出来，安静地陪你坐了一会儿。", {"belonging": 1}),
    _event("uchiha_shuriken", "uchiha_ruins", "生锈的手里剑", "墙角还留着宇智波少年们练习过的痕迹，你照着角度试了几次。", {"exp": 22}),
    _event("forest_herbs", "konoha_forest", "林间药草", "树根旁长着一小片药草，叶片上还挂着露水。", {"item": ("药草", 1)}),
    _event("forest_tracks", "konoha_forest", "陌生脚印", "你在泥地上发现了不属于村民的脚印，一路追踪并排除了隐患。", {"exp": 25, "village_trust": 1}),
    _event("gate_caravan", "konoha_gate", "远方商队", "一支风尘仆仆的商队进入木叶，带来了忍界各地的新闻。", {"fate": 1}),
    _event("gate_guard", "konoha_gate", "代班守门", "你帮神月出云和钢子铁盯了一会儿大门，认出了几张可疑面孔。", {"village_trust": 2}),
    _event("death_forest_shed", "forest_of_death", "蜇蜕的巨蛇皮", "林地里留着一段巨大蛇蜕，你从齿痕判断出它的攻击方式。", {"exp": 35}),
    _event("death_forest_cache", "forest_of_death", "考生的补给袋", "树洞里卡着一只陈年补给袋，里面的军粮丸居然还能用。", {"item": ("军粮丸", 1)}),
    _event("tougen_petals", "tougen_gate", "命线花雨", "门后的花瓣随命线飘来，轻轻落在掌心。", {"fate": 1}, cooldown=7),
    _event("tougen_echo", "tougen_gate", "桃源的回声", "你听见契约之树深处传来模糊的笑声，像是有人在等你回家。", {"belonging": 2}),
    _event("suna_market", "suna_village", "砂隐集市", "风之国的香料和忍具摆满长街，摊主坚持送你一份特产。", {"item": ("查克拉丸", 1)}, min_chapter=7),
    _event("suna_children", "suna_village", "追随风影的孩子们", "几个孩子缠着你讲我爱罗的故事，眼里满是憧憬。", {"belonging": 1, "fate": 1}, min_chapter=7),
    _event("myoboku_oil", "myoboku", "自然能量油", "深作仙人让你在石像前静坐，查克拉流动逐渐平稳。", {"chakra": 0.4, "exp": 30}, min_chapter=9),
    _event("myoboku_feast", "myoboku", "虫子大餐", "志麻仙人端出了一盘「营养丰富」的料理。你闭着眼吃完了。", {"heal": 0.35}, min_chapter=9),
    _event("front_patrol", "war_front", "战后巡逻", "你带着小队清理了一处白绝残留的地穴。", {"exp": 45, "village_trust": 1}, min_chapter=10),
    _event("front_letters", "war_front", "未寄出的家书", "一封封没来得及寄出的信被整齐收好。你决定将它们送回家人手中。", {"belonging": 2, "fate": 1}, min_chapter=10, once=True),
]

# 每个地点一条三阶段连续见闻。完成前一阶段后，后续阶段才会进入事件池。
CHAIN_DEFS = (
    ("home_letters", "naruto_home", 1, (
        ("门缝里的旧信", "门缝深处卡着一封多年前的匿名信：生日快乐，鸣人。字迹刻意藏起来了。", {"belonging": 1}, None),
        ("寻找写信的人", "你按纸张和墨水追到忍校旧仓库，发现那是伊鲁卡尚未成为老师时写下的。", {"trust": 2}, ("黄昏", "夜晚")),
        ("今年的回信", "你没有追问，只在今年生日写了一封回信塞进伊鲁卡家门缝：我收到了。", {"fate": 2, "ryo": 120}, None),
    )),
    ("academy_dropout", "ninja_academy", 1, (
        ("空着的座位", "教室最后一排连续三天空着。伊鲁卡说，那孩子觉得自己永远学不会分身术。", {"exp": 20}, None),
        ("河堤上的学生", "你在河堤找到他，没有讲大道理，只演示了自己当年最糟糕的一次分身。", {"belonging": 1}, ("黄昏",)),
        ("并不标准的分身", "孩子做出了歪歪扭扭却能站住的分身。全班第一次为不完美的忍术鼓掌。", {"village_trust": 3, "ryo": 150}, None),
    )),
    ("office_missing_file", "hokage_office", 2, (
        ("少了一页的档案", "波之国商路档案被整齐撕去一页，缺口比凌乱本身更可疑。", {"fate": 1}, None),
        ("墨迹的去向", "你在废纸焚化炉找到同批封印墨，线索指向一名替商人销案的旧官员。", {"item": ("封印墨", 1)}, ("夜晚",)),
        ("重新写下的名字", "被抹掉的遇难者重新回到档案。纲手让涉事者用余生偿还每一笔赔款。", {"village_trust": 4, "reputation": ("konoha", 5), "ryo": 250}, None),
    )),
    ("ichiraku_veteran", "ichiraku", 2, (
        ("只点清汤的老人", "一名退役忍者每晚只点最便宜的清汤，却总把叉烧钱压在空碗下。", {"belonging": 1}, ("夜晚",)),
        ("没有领到的抚恤", "老人并非贫穷，而是在替一名档案遗失的队友保存那份抚恤金。", {"fate": 1}, None),
        ("两碗豚骨拉面", "档案补齐那天，手打端上两碗拉面。老人把其中一碗放在身旁空位，终于动了筷子。", {"belonging": 3, "ryo": 100}, ("黄昏", "夜晚")),
    )),
    ("training_bell", "training_ground_7", 2, (
        ("第三只铃铛", "木桩下埋着一只生锈的第三只铃铛，背面刻着朔茂的名字。", {"exp": 25}, None),
        ("卡卡西没有说完的话", "卡卡西承认这是父亲留给他的考题：队伍有三人，为什么只有两只铃铛?", {"trust": 2}, ("黄昏",)),
        ("铃声属于整支队伍", "你们把第三只铃铛挂回木桩。风吹过时，三只铃铛第一次同时响起。", {"fate": 2, "party_bond": 3}, None),
    )),
    ("hospital_unknown", "konoha_hospital", 3, (
        ("没有姓名的伤员", "病历只有编号，没有姓名。老人醒来后也拒绝说自己来自哪个村子。", {"item": ("药草", 1)}, None),
        ("旧雾隐护额", "清洗衣物时露出被划掉的雾隐护额。他曾是血雾时代逃亡的医疗忍者。", {"exp": 30}, ("夜晚",)),
        ("新的医疗班讲师", "纲手没有追究旧身份，只问他愿不愿意把救人的本事教给下一代。", {"village_trust": 3, "reputation": ("konoha", 4), "ryo": 220}, None),
    )),
    ("rock_graffiti_chain", "hokage_rock", 2, (
        ("新的涂鸦犯", "四代目石像脸上多了两撇胡须。守卫气得跳脚，你却看懂了那份孤独。", {"belonging": 1}, None),
        ("躲在阴影里的孩子", "你在夜里抓到涂鸦的战争孤儿。他说，只有搞破坏时大人才肯看他。", {"fate": 1}, ("夜晚",)),
        ("被允许留下的画", "你们洗掉胡须，在石壁角落画下一群牵手的小人。纲手看见后没有让人擦。", {"belonging": 2, "village_trust": 2}, None),
    )),
    ("uchiha_lamps", "uchiha_ruins", 3, (
        ("熄灭的石灯", "族地道路两侧的石灯早已熄灭，灯座下却压着尚未腐烂的灯芯。", {"item": ("封印墨", 1)}, None),
        ("佐助记得点灯顺序", "佐助沉默地从最里面点起。那是宇智波迎接远行者回家的旧规矩。", {"party_bond": 2}, ("黄昏", "夜晚")),
        ("不再只为亡者", "最后一盏灯亮起时，佐助把备用灯芯交给你：下次有人回来，你来点。", {"fate": 2, "reputation": ("konoha", 4)}, None),
    )),
    ("forest_poachers", "konoha_forest", 2, (
        ("被切断的捕兽绳", "树间布着不属于忍者的钢索，目标不是野兽，而是通灵兽幼崽。", {"exp": 25}, None),
        ("买家的暗号", "钢索上的刻痕指向地下忍具商。对方正在收购具有查克拉的兽骨。", {"item": ("兽骨", 1)}, ("夜晚",)),
        ("重新开放的兽径", "偷猎网被全部拆除。几只小兽远远看着你，没有立刻逃走。", {"reputation": ("konoha", 5), "ryo": 280, "party_bond": 2}, None),
    )),
    ("gate_refugees", "konoha_gate", 5, (
        ("没有通行证的一家人", "来自小国的一家人被拦在门外，他们的村子刚被流浪忍者烧毁。", {"belonging": 1}, None),
        ("担保人的名字", "高层不愿承担风险。你把自己的名字写进担保栏，卡卡西随后签在第二行。", {"village_trust": 2}, ("白昼",)),
        ("木叶的新木匠", "数日后，父亲修好了大门边所有漏雨的岗亭。通行证上写着：木叶居民。", {"reputation": ("konoha", 6), "ryo": 200, "item": ("木材", 2)}, None),
    )),
    ("death_seal", "forest_of_death", 3, (
        ("松动的旧封印", "第44演习场地下传来不自然的查克拉脉动，大蛇丸留下的术式仍在呼吸。", {"exp": 35}, None),
        ("咒印培养槽", "封印深处是一排废弃培养槽，其中一只还残留着微弱心跳。", {"item": ("查克拉晶片", 1)}, ("夜晚",)),
        ("让实验到此为止", "你与队友毁掉术式，把最后的实验体送往医院。森林的虫鸣重新连成一片。", {"fate": 2, "reputation": ("konoha", 6), "party_bond": 3}, None),
    )),
    ("tougen_sprout", "tougen_gate", 3, (
        ("没有颜色的嫩芽", "门边长出一株灰白嫩芽，既不属于现实，也不属于桃源。", {"fate": 1}, None),
        ("九道不同的养分", "契约者们各留下少量查克拉。嫩芽的叶脉逐渐染上九种颜色。", {"party_bond": 2}, None),
        ("会在两界开放的花", "花朵同时在门内门外绽放。第一次，桃源的温暖主动抵达了现实。", {"fate": 3, "belonging": 3, "item": ("自然结晶", 1)}, None),
    )),
    ("suna_well", "suna_village", 7, (
        ("变苦的井水", "砂隐东区的井水突然发苦，孩子们提着空桶排成长队。", {"exp": 35}, None),
        ("埋在沙下的旧管道", "管道被战争时期的起爆黏土污染。必须在不引爆它的情况下逐段清理。", {"item": ("铁砂", 2)}, ("清晨", "白昼")),
        ("沙漠重新出水", "第一股清水冲开砂砾时，我爱罗亲手把它分给排队最末的孩子。", {"reputation": ("suna", 7), "ryo": 350, "party_bond": 2}, None),
    )),
    ("myoboku_tadpole", "myoboku", 9, (
        ("迷路的小蝌蚪", "一只尚不会说话的小蛤蟆沿错误的瀑布漂进了危险石林。", {"exp": 30}, None),
        ("自然能量的路标", "你不能靠气味追踪，只能分辨每块岩石上极细微的自然能量差异。", {"chakra": 0.3}, None),
        ("蛤蟆一族的乳名", "小蛤蟆被安全送回。深作告诉你它的乳名，意味着妙木山把你当成真正的家人。", {"item": ("自然结晶", 2), "fate": 2, "party_bond": 2}, None),
    )),
    ("front_memorial", "war_front", 10, (
        ("散落的护额", "焦土上散落着五种护额，已经分不清它们原本属于哪支部队。", {"belonging": 1}, None),
        ("共同的名字册", "幸存者决定不再按村子分类，而按最后并肩作战的小队记录名字。", {"fate": 1}, ("黄昏",)),
        ("没有村界的慰灵碑", "五种金属熔成同一块碑。碑上第一行写着：他们为彼此而战。", {"reputation": ("alliance", 8), "ryo": 400, "item": ("查克拉晶片", 2)}, None),
    )),
)

for chain_id, location, min_chapter, stages in CHAIN_DEFS:
    for stage, (title, text, effects, periods) in enumerate(stages):
        EVENTS.append(_event(
            f"chain_{chain_id}_{stage + 1}", location, title, text, effects,
            periods=periods, cooldown=2, once=True, min_chapter=min_chapter,
            chain=chain_id, stage=stage,
        ))


def _eligible(state, event):
    if event["location"] != state.location or state.chapter < event["min_chapter"]:
        return False
    if event["periods"] and period_name(state) not in event["periods"]:
        return False
    if event.get("chain") and state.world_event_chains.get(event["chain"], 0) != event["stage"]:
        return False
    count = state.random_event_history.get(event["id"], 0)
    if event["once"] and count:
        return False
    last_seen = state.random_event_last_seen.get(event["id"], -9999)
    return state.actions_taken - last_seen >= event["cooldown"]


def _apply_effects(state, effects):
    if effects.get("fate"):
        state.gain_fate(effects["fate"], "地点见闻")
    if effects.get("exp"):
        state.gain_exp(effects["exp"])
    if effects.get("trust"):
        state.add_trust(effects["trust"])
    if effects.get("village_trust"):
        state.add_village_trust(effects["village_trust"])
    if effects.get("belonging"):
        state.belonging += effects["belonging"]
        ui.slow_print(f"♥ 归属感 +{effects['belonging']} [当前: {state.belonging}]")
    if effects.get("item"):
        state.add_item(*effects["item"], cap=99)
    if effects.get("ryo"):
        state.gain_ryo(effects["ryo"], "地点事件")
    if effects.get("reputation"):
        from systems import factions
        factions.add_reputation(state, *effects["reputation"], reason="地点事件")
    if effects.get("party_bond"):
        from systems import party
        party.gain_teammate_exp(state, state.selected_party, 0, bond=effects["party_bond"])
    if effects.get("heal"):
        amount = max(1, int(state.player["max_hp"] * effects["heal"]))
        state.player["hp"] = min(state.player["max_hp"], state.player["hp"] + amount)
        ui.slow_print(f"※ 生命恢复 {amount} 点。")
    if effects.get("chakra"):
        amount = max(1, int(state.player["max_chakra"] * effects["chakra"]))
        state.player["chakra"] = min(state.player["max_chakra"], state.player["chakra"] + amount)
        ui.slow_print(f"※ 查克拉恢复 {amount} 点。")


def trigger_random_event(state, force=False):
    """尝试触发当前地点事件；主动观察时 force=True。"""
    candidates = [event for event in EVENTS if _eligible(state, event)]
    if not candidates:
        if force:
            ui.slow_print("你在附近走了走，此刻没有发现新鲜事。")
        return False
    if not force and random.random() >= 0.3:
        return False
    if force:
        chain_candidates = [event for event in candidates if event.get("chain")]
        unseen = [event for event in candidates if not state.random_event_history.get(event["id"])]
        event = random.choice(chain_candidates or unseen or candidates)
    else:
        event = random.choice(candidates)
    ui.title(f"地点见闻: {event['title']}")
    ui.story(event["text"])
    state.random_event_history[event["id"]] = state.random_event_history.get(event["id"], 0) + 1
    state.random_event_last_seen[event["id"]] = state.actions_taken
    if event.get("chain"):
        state.world_event_chains[event["chain"]] = event["stage"] + 1
    _apply_effects(state, event["effects"])
    return True
