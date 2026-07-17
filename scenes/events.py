# -*- coding: utf-8 -*-
"""地点事件调度:根据游戏进度决定各地点触发的剧情与可用行动。"""
from scenes import chapter_01, chapter_02, chapter_03, rin_arc
from systems import ui


def on_enter(state):
    """进入地点时自动触发的事件。"""
    loc = state.location
    f = state.flags

    if loc == "ninja_academy" and f["intro_done"] and not f["team7_assigned"]:
        chapter_01.assignment_day(state)
    elif loc == "training_ground_7" and f["team7_assigned"] and not state.quests["team7_restart"]["completed"]:
        if f["talked_sasuke"] and f["talked_sakura"]:
            chapter_01.arrive_training_ground(state)
        else:
            ui.slow_print("(先回忍者学校找佐助和小樱聊聊吧。)")
    elif loc == "uchiha_ruins":
        if state.chapter < 2:
            ui.slow_print("(佐助的身影在远处一闪而过。他的剧情,将随章节推进展开。)")
    elif loc == "konoha_hospital":
        if not f["rin_photo_seen"] and state.chapter >= 2:
            ui.slow_print("(走廊尽头的公告栏上,那张泛黄的老照片,似乎在等你驻足。)")
    elif loc == "naruto_home":
        if state.chapter >= 6 and f["tsunade_done"] and not f["sasuke_arc_done"]:
            ui.slow_print("(夜风有些不安分。今晚睡觉前,最好把该做的准备都做完——存档、修炼、契约。)")
    elif loc == "konoha_gate":
        if state.chapter >= 5 and not f["tsunade_done"]:
            ui.slow_print("(自来也倚在大门边冲你招手:「小鬼,行李收拾好了没?」)")
        elif f["main_complete"] and not f["shippuden_started"]:
            ui.slow_print("(自来也的身影出现在门外的官道上——三年之约,随时可以启程。)")
        elif state.chapter >= 10 and f["pain_done"] and not f["war_done"]:
            ui.slow_print("(一只铁之国的信鹰掠过大门上空。五影会谈的召集令,已经在路上了。)")
    elif loc == "suna_village":
        if f["shippuden_started"] and not f["kazekage_done"]:
            ui.slow_print("(村口的守卫神色慌张——砂隐村的上空,似乎还残留着爆炸的烟痕。)")
    elif loc == "myoboku":
        if state.chapter >= 9 and not f["sage_training_done"]:
            ui.slow_print("(深作老仙人蹲在巨大的蘑菇伞下,朝你点了点烟杆。)")


def _academy_actions(state, actions):
    flags = state.flags
    if flags["team7_assigned"] and not state.quests["team7_restart"]["completed"]:
        if not flags["talked_sasuke"]:
            actions.append(("找佐助说话", chapter_01.talk_sasuke))
        if not flags["talked_sakura"]:
            actions.append(("找小樱说话", chapter_01.talk_sakura))


def _training_ground_actions(state, actions):
    if state.quests["team7_restart"]["completed"] and not state.flags["bell_test_completed"]:
        actions.append(("【主线】开始铃铛测试", chapter_02.bell_test))


def _home_actions(state, actions):
    flags = state.flags
    if flags["bell_test_completed"] and not flags["tougen_unlocked"]:
        actions.append(("【主线】上床睡觉 (触发重要剧情)", chapter_03.tougen_awakening))
    elif state.chapter >= 6 and flags["tsunade_done"] and not flags["sasuke_arc_done"]:
        actions.append(("【主线·终章】就寝 (今夜,命运将走到岔路口)", _final_night))
    if state.chapter >= 9 and flags["sage_training_done"] and not flags["pain_done"]:
        actions.append(("【主线】就寝 (雨云正在逼近木叶——)", _start_pain))


def _hokage_office_actions(state, actions):
    flags = state.flags
    if state.chapter == 2 and not flags["wave_done"]:
        actions.append(("【主线】接取护送任务 (波之国篇)", _start_wave))
    if state.chapter >= 3 and not flags["chunin_done"]:
        actions.append(("【主线】报名中忍考试 (中忍考试篇→木叶崩溃篇)", _start_chunin))
    if flags["kazekage_done"] and not flags["akatsuki_done"]:
        actions.append(("【主线】十班的紧急任务 (晓之阴影篇)", _start_akatsuki))
    actions.append((ui.Choice("拜访火影", ("actions", "visit")), _visit_hokage))


def _gate_actions(state, actions):
    flags = state.flags
    if state.chapter >= 5 and not flags["tsunade_done"]:
        actions.append(("【主线】与自来也出发 (寻找纲手篇)", _start_tsunade))
    if flags["main_complete"] and not flags["shippuden_started"]:
        actions.append(("【疾风传】与自来也踏上三年修行之旅", _start_timeskip))
    if state.chapter >= 10 and flags["pain_done"] and not flags["war_done"]:
        actions.append(("【主线·大结局】响应五影会谈召集 (第四次忍界大战)", _start_war))
    if flags["main_complete"]:
        actions.append(("眺望村外的道路", _gate_view))


def _hospital_actions(state, actions):
    flags = state.flags
    if state.chapter >= 2 and not flags["rin_photo_seen"]:
        actions.append(("查看走廊尽头的老照片", rin_arc.hospital_photo))
    if flags["rin_contacted"] and not flags["rin_kakashi_hint"]:
        actions.append(("【剧情】替琳,给卡卡西带一句话", rin_arc.rin_kakashi_hint))
    if flags["wave_done"] and not state.quests["herb_gathering"]["completed"]:
        handler = rin_arc.herb_quest_turn_in if flags["herb_quest_active"] else rin_arc.herb_quest_start
        label = "上交药草 (需要3株)" if flags["herb_quest_active"] else "接受护士长的采药委托 (日常)"
        actions.append((label, handler))
    if state.chapter in (3, 4) and not flags["sakura_hospital_c3"] and state.relations["sakura"]["medical"] >= 5:
        actions.append(("【剧情】长椅上的小樱", rin_arc.sakura_hospital))
    if state.chapter >= 5 and flags["tsunade_returned"] and not flags["sakura_hospital_c5"]:
        actions.append(("【剧情】医疗班的见习生", rin_arc.sakura_hospital))
    if flags["akatsuki_done"] and state.contracts["tsunade"]["unlocked"] and not flags["shizune_contracted"]:
        actions.append(("【剧情】账房里的静音", _shizune_bond))


def _uchiha_actions(state, actions):
    flags = state.flags
    if state.chapter in (3, 4) and flags["wave_done"] and not flags["sasuke_talk_c3"]:
        actions.append(("【剧情】族地门口的佐助", _sasuke_talk_c3))
    elif state.chapter == 5 and flags["crush_done"] and not flags["sasuke_talk_c4"]:
        actions.append(("【剧情】屋顶上的背影", _sasuke_talk_c4))
    elif state.chapter >= 6 and not flags["sasuke_arc_done"] and not flags["sasuke_talk_c5"]:
        actions.append(("【剧情】黄昏的训练场邀约", _sasuke_talk_c5))


def _suna_actions(state, actions):
    if state.flags["shippuden_started"] and not state.flags["kazekage_done"]:
        actions.append(("【主线】驰援砂隐 (风影夺还篇)", _start_kazekage))
    elif state.flags["kazekage_done"]:
        actions.append(("拜访风影办公室", _suna_visit))


def _myoboku_actions(state, actions):
    if state.chapter >= 9 and not state.flags["sage_training_done"]:
        actions.append(("【主线】拜入蛤蟆仙人座下 (仙术修行)", _start_sage))


LOCATION_ACTION_BUILDERS = {
    "ninja_academy": _academy_actions,
    "training_ground_7": _training_ground_actions,
    "naruto_home": _home_actions,
    "hokage_office": _hokage_office_actions,
    "konoha_gate": _gate_actions,
    "hokage_rock": lambda state, actions: actions.append(("眺望村子", _hokage_rock_view)),
    "konoha_hospital": _hospital_actions,
    "uchiha_ruins": _uchiha_actions,
    "suna_village": _suna_actions,
    "myoboku": _myoboku_actions,
}


def get_location_actions(state):
    """返回当前地点的可选剧情行动 [(标签, handler)]。"""
    actions = []
    builder = LOCATION_ACTION_BUILDERS.get(state.location)
    if builder:
        builder(state, actions)
    if state.flags["shippuden_started"]:
        from scenes import romance
        actions.extend(romance.get_romance_actions(state, state.location))
    return actions


# ── 主线入口 ─────────────────────────────────

def _start_wave(state):
    from scenes import wave_country
    wave_country.start(state)


def _start_chunin(state):
    from scenes import chunin_exam
    chunin_exam.start(state)


def _start_tsunade(state):
    from scenes import tsunade_search
    tsunade_search.start(state)


def _final_night(state):
    from scenes import sasuke_retrieval
    sasuke_retrieval.night_event(state)


def _start_timeskip(state):
    from scenes import kazekage_rescue
    kazekage_rescue.depart(state)


def _start_kazekage(state):
    from scenes import kazekage_rescue
    kazekage_rescue._rescue(state)


def _suna_visit(state):
    from scenes import kazekage_rescue
    kazekage_rescue.suna_visit(state)


def _start_akatsuki(state):
    from scenes import akatsuki_shadow
    akatsuki_shadow.start(state)


def _start_sage(state):
    from scenes import akatsuki_shadow
    akatsuki_shadow.sage_training(state)


def _shizune_bond(state):
    from scenes import akatsuki_shadow
    akatsuki_shadow.shizune_bond(state)


def _start_pain(state):
    from scenes import pain_assault
    pain_assault.start(state)


def _start_war(state):
    from scenes import fourth_war
    fourth_war.start(state)


# ── 火影办公室 ────────────────────────────────

def _visit_hokage(state):
    f = state.flags
    if f["tsunade_returned"]:
        from scenes import tsunade_search
        tsunade_search.visit_tsunade(state)
        return
    if f["crush_done"] and f["hiruzen_saved"]:
        ui.story("""
病榻上的三代火影气色好了不少,正偷偷抽烟斗,
见鸣人进来,慌忙藏到枕头底下。

「咳、咳咳!是鸣人啊。」

「纲手奶奶说了,再抽没收。」鸣人绷着脸伸出手。

老人苦着脸交出烟斗,忽然又笑了:「臭小子……
 能被你这样管着,真好啊。」
""")
        state.belonging += 2
        ui.slow_print(f"※ 归属感 +2 [当前: {state.belonging}]")
        return
    if f["crush_done"] and not f["hiruzen_saved"]:
        ui.story("""
办公室里,三代的烟斗静静躺在灵位前,一尘不染。

鸣人添了一炷香,站了很久。

「爷爷,村子今天也很和平。」他轻声汇报,
 像老人还坐在那堆文件后面一样,
「等我。你身后那块石头上,很快就会有我的脸了。」
""")
        state.belonging += 1
        ui.slow_print(f"※ 归属感 +1 [当前: {state.belonging}]")
        return
    if state.kakashi_suspicion >= 100:
        ui.story("""
「鸣人,坐吧。」三代放下烟斗,目光深邃。

「卡卡西向我汇报了一些……有趣的事。」

(卡卡西怀疑值过高,三代开始单独关注你。慎重行事。)
""")
        state.add_backlash(1, "高层的注视")
    else:
        ui.story("""
「哦,是鸣人啊。」三代火影从文件堆里抬起头,慈祥地笑了。

「怎么样,和卡卡西他们相处得还好吗?」

「好得很!爷爷,等着吧,我很快就会把你身后那块石头上
 刻上我的脸的!」

三代大笑:「哈哈哈,那老头子我可要拭目以待了。」

(望着老人温暖的笑容,鸣人的心却揪了一下——
 那场即将到来的战斗……这一次,绝不会让悲剧重演。)
""")
        state.belonging += 1


# ── 火影岩 ──────────────────────────────────

def _hokage_rock_view(state):
    ui.story("""
风从山顶掠过。整个木叶村在脚下铺展开来。

鸣人在四代目的石像头顶坐下——前世,他无数次坐在这里。

「爸爸,妈妈已经找到了。」他轻声说,
「接下来,一个都不会少。」

(内心平静了下来。)
""")
    p = state.player
    p["chakra"] = min(p["max_chakra"], p["chakra"] + 30)
    ui.slow_print("※ 查克拉恢复 30 点。")
    if state.flags["chapter1_end"] and not state.flags["rasengan_learned"]:
        ui.story("""
指尖,查克拉不自觉地开始旋转。

前世刻进骨髓的感觉,顺着风回来了。
虽然身体还跟不上记忆,但一颗歪歪扭扭的螺旋丸,
已经能在掌心勉强成形。

★ 习得技能【不完全螺旋丸】!
(注意:在他人面前使用会大幅增加暴露度与怀疑值。)
""")
        state.flags["rasengan_learned"] = True
        state.learn_skill("rasengan_incomplete")


# ── 木叶大门 ─────────────────────────────────

def _gate_view(state):
    ui.story("""
大门外,官道笔直地伸向远方的地平线。

三年后,自来也会带你走上这条路;赤云会从这条路来;
战争、和解、以及新的时代,都在这条路的尽头。

但今天,门内飘着一乐拉面的香气,桃源的命线
在心口暖暖发亮。

——来日方长。先回家吃饭。
""")
    state.belonging += 1
    ui.slow_print(f"※ 归属感 +1 [当前: {state.belonging}]")


# ── 佐助关系事件 ──────────────────────────────

def _sasuke_talk_c3(state):
    ui.title("剧情: 族地门口的佐助")
    ui.story("""
宇智波族地的门口,佐助正在拆信——雪白的信纸,
边角绘着细小的冰晶纹路。

「白寄来的?」鸣人凑过去。

「……嗯。」佐助飞快把信塞进怀里,别过脸,
「问我写轮眼开了几个勾玉。烦人。」

(嘴上嫌弃,信纸却叠得整整齐齐。)

「喂,鸣人。」沉默半晌,佐助忽然开口,
「波之国的桥上……你为什么护着我?
 明明,变强的是我,被保护的也是我。」
""")
    idx = ui.choose("你回答——", [
        "「同伴互相挡刀,不需要理由。」",
        "「因为我见过失去你的样子。不想再见第二次。」",
    ])
    if idx == 0:
        ui.story("""
「……哼。」佐助踢开脚边的石子,「下次换我挡。
 记住了,吊车尾,下次换我。」

他转身回了族地。夕阳把两个人的影子,拉得很长。
""")
        state.add_rel("sasuke", "trust", 6)
        state.add_rel("sasuke", "team_bond", 5)
    else:
        ui.story("""
佐助猛地回头,黑瞳锐利如刀:「什么意思?」

「字面意思。」鸣人迎着他的目光,没有躲,
「我这个人,做过很多很后悔的梦。梦里的你,
 走进了再也回不来的黑暗里。——所以这一世,
 做梦都别想甩开我。」

「……神经病。」佐助丢下三个字走了。

但走出十几步,他的脚步,慢了下来。
""")
        state.add_rel("sasuke", "trust", 8)
        state.add_rel("sasuke", "isolation", -8)
        state.exposure += 3
    state.flags["sasuke_talk_c3"] = True
    ui.pause()


def _sasuke_talk_c4(state):
    ui.title("剧情: 屋顶上的背影")
    ui.story("""
族地最高的屋顶上,佐助盘膝而坐,望着木叶崩溃后
仍在重建的街区。

「上来。」他头也不回。

鸣人在他旁边坐下。两个人谁都没说话,
看着夕阳一点点沉进火影岩的轮廓里。

「入侵那天,」佐助忽然开口,「你先是拦了我爱罗,
 又冲进了天台结界。每一步,都像早就知道会发生什么。」

他转过头,写轮眼静静旋转:「我不问你怎么知道的。
 我只问一句——鼬的事,你也『知道』吗?」
""")
    idx = ui.choose("你——", [
        "沉默三秒,然后说:「知道一部分。但现在告诉你,只会害了你。」",
        "「与其想那个,不如想想怎么变强。来,切磋一场!」(岔开话题)",
    ])
    if idx == 0:
        ui.story("""
空气凝固了很久。

「『害了我』……」佐助一字一字地咀嚼着,拳头攥紧,
 又缓缓松开,「好。我记住这句话了。
 等你觉得『不会害我』的那天——一个字,都不许少。」

「一言为定。」

(信任与焦灼同时生长。真相的倒计时,开始走动了。)
""")
        state.add_rel("sasuke", "trust", 10)
        state.add_rel("sasuke", "revenge", -5)
    else:
        ui.story("""
「……无聊。」

佐助起身就走,下屋檐前又停住:

「明早六点,训练场。敢迟到就绝交。」

(第二天的切磋,两人从日出打到日落。
 有些话拳头说不清,但拳头能记住温度。)
""")
        state.add_rel("sasuke", "team_bond", 8)
        state.add_rel("sasuke", "isolation", -5)
        state.player["attack"] += 1
        ui.slow_print("※ 与佐助的切磋让攻击 +1!")
    state.flags["sasuke_talk_c4"] = True
    ui.pause()


def _sasuke_talk_c5(state):
    ui.title("剧情: 黄昏的邀约")
    ui.story("""
第七训练场。三根木桩的影子被夕阳拉到最长。

佐助抱臂靠在中间那根木桩上——当年鸣人被绑过的那根。

「小樱进了医疗班,你拜了三忍当师父。」他望着河面,
 语气听不出情绪,「第七班里,好像只有我,
 还站在原地。」

「胡说。」鸣人捡起一块石头打了个水漂,
「写轮眼三勾玉、体术全班第一、还学会了给白回信——
 进步可大了。」

「……最后那个算什么进步。」

「算!交朋友是天底下最难的忍术!」

佐助被噎得沉默了半天,忽然低声笑了一下。
真的笑了一下。
""")
    idx = ui.choose("趁着气氛,你——", [
        "认真地说:「不管接下来发生什么,第七班永远有你的位置。」",
        "提议:「明天叫上小樱和卡卡西老师,四个人吃一乐!我请!」",
    ])
    if idx == 0:
        ui.story("""
佐助看了他很久。

「……知道了。」他推开木桩往回走,声音散在风里,
「啰嗦。」

(但那三个字,他听进去了。种进心里的东西,
 会在最黑的夜里发光。)
""")
        state.add_rel("sasuke", "trust", 8)
        state.add_rel("sasuke", "team_bond", 8)
    else:
        ui.story("""
第二天中午,一乐拉面的柜台前挤满了第七班。

卡卡西照例迟到、照例找借口、照例被小樱吼;
佐助被大叔多送的溏心蛋弄得不知所措;
鸣人吃到第三碗,钱包见了底,被迫写欠条。

很普通的一顿饭。普通得,让人想永远记住。
""")
        state.add_rel("sasuke", "team_bond", 10)
        state.add_rel("sasuke", "isolation", -10)
        state.add_rel("sakura", "trust", 5)
        state.belonging += 3
        ui.slow_print(f"※ 归属感 +3 [当前: {state.belonging}]")
    state.flags["sasuke_talk_c5"] = True
    ui.pause()
