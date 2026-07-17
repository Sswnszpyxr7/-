# -*- coding: utf-8 -*-
"""疾风传·终章:第四次忍界大战——五影会谈、九喇嘛和解、带土与斑、九命同归。"""
from systems import battle, quest, ui


def start(state):
    """木叶大门触发(chapter>=10, pain_done)。全作大结局。"""
    if state.chapter < 10 or not state.flags["pain_done"] or state.flags["war_done"]:
        return
    _summit(state)
    _kurama(state)
    _war_opens(state)
    _mei_arc(state)
    _obito(state)
    _madara(state)
    _gaia_finale(state)
    _epilogue(state)


# ── 一、五影会谈 ────────────────────────────────

def _summit(state):
    ui.title("剧情: 五影会谈")
    ui.story("""
铁之国。三狼山的雪没过脚踝。

五张影之座椅围成半圆:纲手、我爱罗、照美冥、
大野木、艾。而你,作为「击退佩恩的英雄」与
「九尾人柱力」,破例列席。

「哦呀,」水影大人以指背支颐,琥珀色的眼睛弯起来,
「这就是那位鸣人君?比传闻里……嗯,顺眼多了。」

会谈进行到一半——天花板无声地扭曲了。

一个戴着螺旋面具的男人,从空间的漩涡中踱步而出。

「初次见面,五影。」他的声音隔着面具,平静得像在谈天气,
「我是宇智波斑。来向你们宣战——
 第四次忍界大战,以及,【无限月读】。」
""")
    ui.pause()
    ui.story("""
他说完想说的,身影便沉回漩涡,只留下满室死寂。

「无限月读……把所有人关进永远的梦。」纲手的指节捏得发白。

「所以,联军。」我爱罗环视五影,少年风影的声音稳如磐石,
「忍界五大国,第一次为了同一件事而战。」

散会后,照美冥在廊下叫住你。

「鸣人君。刚才那个面具男出现的时候,全场只有你,
 眼神里没有『恐惧』,只有『心疼』。」她审视着你,
「……你知道面具下面是谁,对吧?」

你没有否认。水影大人轻轻叹了口气:
「留着你的秘密。但战场上,别一个人扛。」
""")
    state.flags["summit_done"] = True
    state.gain_fate(2, "五影并立的誓言")
    ui.pause()


# ── 二、心之瀑布 ────────────────────────────────

def _kurama(state):
    ui.title("剧情: 心之瀑布")
    ui.story("""
开战前夜。桃源深处,新辟出的一片山林前。

你在契约之树下盘膝坐定,意识沉入封印空间。

铁栅之后,巨大的赤红身影睁开眼,九条尾巴
卷起腥风:『又来了,小鬼。这次想借多少?』

「不借。」你摇头,抬手解开了栅栏的封印锁。

九尾愣住了。连忙赶来的玖辛奈也愣住了——
随即,她笑着按住了想要阻拦的手。

「九喇嘛。」你叫出那个名字,「这一世,我不想
 『使用』你的力量。我想和你,并肩作战。」
""")
    ui.pause()
    ui.story("""
『……九喇嘛。』巨兽的瞳孔缩了缩,
『多少年了,没有人类叫过这个名字。』

玖辛奈走上前,赤红的长发在封印空间里轻轻浮动。

「那天晚上的事,我一直想向你道歉。」她深深低头,
「把你当成灾祸封印的,是我们。可你明明——
 也只是一个被仇恨推着走的,孤独的孩子。」

『你……』

「桃源里给你留了一片山。」你指向意识的深处——
契约之树的方向,九瓣花的印记正温暖地亮着,
「有山有水,没有栅栏。九喇嘛,回家吧。」

良久,巨兽发出一声像叹息又像笑的低吼。

『……真是,拿你们漩涡家的没办法。』

栅栏彻底崩解。赤红的查克拉不再灼人,
如朝阳般漫过全身——
""")
    state.flags["kurama_friend"] = True
    state.learn_skill("kurama_mode")
    state.learn_skill("bijuu_rasengan")
    state.kyubi_flux = 0
    ui.slow_print("★ 与九喇嘛真正和解!九尾波动彻底平息。")
    ui.slow_print("★ 习得【九喇嘛查克拉模式】【尾兽玉螺旋丸】!")
    state.gain_fate(3, "九喇嘛,拜托了!")
    ui.pause()


# ── 三、开战 ──────────────────────────────────

def _war_opens(state):
    ui.title("剧情: 开战")
    ui.story("""
忍界联军,四万人列阵于焦土之上。
五大国的旗帜,历史上第一次朝着同一个方向。

地面裂开了。白色的人形如蛆虫般涌出;
更远处,秽土转生的死者军团迈着不属于生者的步伐——

「全军——」我爱罗的沙之手掌托起指挥台,
「为了活着的人,也为了死去的人。开战!!」
""")
    result = battle.battle(state, "edo_jonin", special_rules={
        "no_escape": True,
        "allies": [
            {"name": "小樱", "power": 26, "element": "taijutsu",
             "move": "怪力轰开敌阵", "can_heal": True, "act_rate": 0.65},
            {"name": "我爱罗", "power": 28, "element": "earth",
             "move": "沙瀑大葬吞没纵队", "act_rate": 0.75},
        ],
        "environment": "war_front",
    }, intro="眼中布满裂纹的死者举起了刀——「拜托了,在我伤到同伴之前!」")
    if result == "win":
        ui.story("""
封印班一拥而上,白布与封印符缠住静止的死者。

「谢谢……」秽土的上忍在光中闭上眼,「木叶的少年。」
""")
    else:
        ui.story("""
死者的刀锋掠过肩头的瞬间,封印班及时赶到。
你踉跄着撑住膝盖——战争没有暂停键。
""")
        state.player["hp"] = max(1, state.player["max_hp"] // 3)
    ui.pause()

    # 宁次改命节点
    ui.title("命运节点: 日向的宿命")
    if state.flags["hinata_guarded"]:
        ui.story("""
战线中段,十尾的木刺如暴雨般泼下。

前世的这一刻,宁次用身体挡在了雏田身前。

——但这一世,雏田自佩恩之战后勤修不辍,
柔步双狮拳早已今非昔比。她侧身、旋掌、
以回天的弧线荡开了所有木刺,还顺手护住了身后的宁次。

「雏田大人……什么时候变得这么强了。」宁次怔怔道。

「因为有想守护的人哦,宁次哥哥。」

(日向的宿命,在这一世,由日向自己终结了。)
""")
        state.gain_fate(1, "日向的宿命,到此为止")
    else:
        ui.story("""
战线中段,十尾的木刺如暴雨般泼下,直取雏田——

前世的画面轰然重叠:宁次的白眼,穿胸的木刺,
「因为,被称为天才啊」……

「影分身之术!!」

九喇嘛模式的金色分身抢先一步,尾兽查克拉的手掌
将木刺尽数拍飞。宁次与雏田背靠背站定,毫发无伤。

「……欠你一次,鸣人。」宁次白眼一凛,重新扑入战团。

(不欠。这一世,谁都不许再替谁死。)
""")
        state.gain_fate(1, "日向的宿命,到此为止")
    ui.pause()


# ── 四、水影的熔光 ───────────────────────────────

def _mei_arc(state):
    ui.title("契约: 水影的熔光")
    ui.story("""
西线告急。你带着影分身军团驰援时,正看见
照美冥一人立于白绝纵队的正面。

「熔遁·熔怪之术。」

熔浆如瀑布般倾泻,白色的人形在赤红中成片消融。
强硬、precise、不留余地——这就是终结了「血雾之村」
时代的五代水影。

「哎呀,鸣人君。」她回头,额角带着汗,笑容依旧从容,
「来得正好。左边三百,右边五百——选哪边?」

「都要!」

金色的查克拉外衣与熔浆的赤光并肩推进。
半个时辰后,西线的白绝,一个不剩。
""")
    ui.pause()
    ui.story("""
战线间隙。照美冥靠着岩壁灌了口水,忽然开口:

「佩恩之战后,我调阅过木叶的战报。九条命线,
 把整个村子从死亡里捞回来的术……」

她望着你,琥珀色的眼睛里有一瞬间的怅然:

「血雾之村的时代,我亲手杀死了很多『必须杀』的人,
 才换来今天的雾隐。那时候我总想——如果有谁能把
 『守护』做得比『杀戮』更强,该多好。」

「现在有了。」她笑起来,伸出手,
「水影照美冥。守护温柔需要强硬,你两样都有——
 那就,再多一个人给你撑腰吧?」

你握住那只手。九瓣花印记亮起,第八条命线
如熔金般流淌成形。

『契约成立。……啊啦,这感觉,比婚戒实在多了。』
""")
    c = state.contracts["mei"]
    c["unlocked"] = True
    c["contract_level"] = 1
    c["affection"] = 78
    c["trust"] = 85
    c["safety"] = 82
    c["fate_resonance"] = 74
    c["location"] = "mist"
    c["note"] = "第八位契约者。五代水影,雾隐新时代的缔造者,桃源温泉的常客。"
    state.flags["mei_contracted"] = True
    state.gain_fate(2, "第八契约·熔光之影")
    ui.slow_print("★ 照美冥契约达成!契约等级 1【初契】")
    ui.slow_print("★ 战斗中可呼唤契约支援【熔遁掩护】")
    ui.pause()


# ── 五、面具之下 ────────────────────────────────

def _obito(state):
    ui.title("剧情: 战场的面具")
    ui.story("""
战争第二日。十尾复活的祭坛前,面具男终于亲自站上战场。

「无限月读,是唯一的救赎。」他张开双臂,
 神威的漩涡在身周明灭,「在梦里,死去的人会回来。
 失败者会成为英雄。这个地狱一样的现实——不再存在。」

「卡卡西老师,」你按住身边人的肩,低声道,
「等下别管我,配合我把他的面具,打下来。」
""")
    allies = [{"name": "卡卡西", "power": 34, "element": "lightning",
               "move": "雷切与神威同频斩落", "act_rate": 0.75}]
    result = battle.multi_stage_boss_battle(state, [
        {
            "name": "神威·虚化",
            "enemy_id": "obito_masked",
            "intro": "攻击一次次穿过虚化的身体。先由卡卡西标记两个空间的时间差。",
            "special_rules": {
                "no_escape": True, "allies": allies, "enemy_name": "面具男·神威虚化",
                "enemy_skills": ["kamui_strike", "uchiha_flame"],
                "enemy_mods": {"hp": -440}, "objective_text": "识破虚化周期，逼出实体化瞬间",
                "environment": "war_front",
            },
        },
        {
            "name": "人柱力锁链阵",
            "enemy_id": "obito_masked",
            "transition": "神威节奏被识破，带土扯动查克拉锁链。尾兽之力与木遁从祭坛四周一齐暴走。",
            "transition_heal": 0.25,
            "special_rules": {
                "no_escape": True, "allies": allies, "enemy_name": "带土·人柱力锁链阵",
                "enemy_skills": ["wood_dragon", "kamui_strike", "uchiha_flame"],
                "enemy_mods": {"hp": -390, "attack": -6},
                "objective_text": "斩断锁链，在实体化瞬间击碎面具",
                "environment": "war_front",
            },
        },
    ])
    if result != "win":
        state.player["hp"] = max(1, state.player["max_hp"] // 3)
        state.add_backlash(1, "神威的代价")
    ui.pause()

    ui.title("剧情: 面具之下")
    ui.story("""
尾兽玉螺旋丸与雷切的合击轰在面具上——
螺旋纹路的白色面具,寸寸碎裂。

碎片之后,是一张卡卡西再熟悉不过的脸。

「带土……!你还活着……?!」

「『宇智波带土』早就死了。」右脸带着旧伤的男人
面无表情,「死在神无毗桥,死在那个雪夜——
 死在琳的心脏,被雷切贯穿的那一刻。」
""")
    ui.pause()
    if state.contracts["rin"]["unlocked"]:
        ui.story("""
就在这时,你心口的九瓣花印记,自己亮了起来。

第二条命线——琳的命线,轻轻震颤着,像在恳求。

你闭上眼,松开了命线的闸门。

碧绿色的光在战场中央凝聚成形。短发的少女踏着光走出,
医疗背包还背在肩上,像随时准备给谁处理伤口。

「————琳?」

带土的声音,第一次碎了。

「带土。」琳走到他面前,仰起头,认真地看着他,
「我一直都在看着哦。从那个雪夜,到现在。」

「看着你把我的名字,变成毁掉世界的理由。」

「笨蛋带土——我什么时候,要过这样的守护?」
""")
        ui.pause()
        ui.story("""
「我……我只是想……」修罗一样的男人退了半步,
 像做错事的十三岁少年,「想要一个,你还活着的世界……」

「我活着。」琳握住他的手,把它按在自己的心口,
 命线的暖流顺着掌心涌过去,「在鸣人为我们建的家里,
 好好地活着。药草田、溪水、还有星空湖——
 带土,不用月读。回家就好。」

神威的漩涡,缓缓地、缓缓地停了。

那个背负了半个忍界之恶的男人跪倒在地,
像终于卸下了千斤的面具——嚎啕大哭。
""")
    else:
        ui.story("""
「带土前辈。」你走上前,「琳姐的事,我都知道。
 我还知道——她从来没有怪过任何人。」

你说了很久。说前世,说桃源,说那些被改写的命运。
说到最后,神威的漩涡缓缓停了。
""")
    state.flags["obito_redeemed"] = True
    state.gain_fate(3, "雪夜终于化了")
    ui.slow_print("★ 带土迷途知返!他撕下黑袍,转身面向斑的方向。")
    ui.pause()


# ── 六、最终决战 ────────────────────────────────

def _madara(state):
    ui.title("终章: 红月之战")
    ui.story("""
「……真是无聊的闹剧。」

苍老而威严的声音自天穹落下。秽土转生的宇智波斑
踏着陨石的碎片降临,完成体须佐能乎撕开云海——

「带土背叛,计划提前。也罢。」战国的亡灵俯瞰众生,
「就由我亲手,给这个世界降下永恒的梦。」

「舞吧,忍者们。这才配称为——战争。」
""")
    allies = []
    se = state.flags["sasuke_ending"]
    if se >= 2:
        allies.append({"name": "宇智波佐助", "power": 36, "element": "lightning",
                       "move": "千鸟贯穿了边狱的死角", "act_rate": 0.8})
    else:
        allies.append({"name": "终于折返的佐助", "power": 32, "element": "lightning",
                       "move": "千鸟撕开须佐的侧翼", "act_rate": 0.7})
    if state.flags["obito_redeemed"]:
        allies.append({"name": "带土", "power": 30, "element": "yin",
                       "move": "神威撕开了须佐的装甲", "act_rate": 0.75})
    allies.append({"name": "我爱罗", "power": 28, "element": "earth",
                   "move": "沙之大手缚住巨人的脚踝", "act_rate": 0.7})

    result = battle.multi_stage_boss_battle(state, [
        {
            "name": "完成体须佐能乎",
            "enemy_id": "madara_final",
            "intro": "仙人模式与九喇嘛模式重叠。第一目标不是斑，而是那具劈开山岳的蓝色巨人。",
            "special_rules": {
                "no_escape": True, "allies": allies[:3], "enemy_name": "斑·完成体须佐能乎",
                "enemy_skills": ["perfect_susanoo", "limbo_strike"],
                "enemy_mods": {"hp": -800}, "objective_text": "集中破势，击碎须佐能乎装甲",
                "environment": "war_front",
            },
        },
        {
            "name": "天碍震星",
            "enemy_id": "madara_final",
            "transition": "须佐装甲崩裂。斑仰头结印，两颗遮蔽天穹的陨石一前一后压向联军。",
            "transition_heal": 0.15,
            "special_rules": {
                "no_escape": True, "allies": allies[:3], "enemy_name": "斑·天碍震星",
                "enemy_skills": ["tengai_shinsei", "wood_dragon"],
                "enemy_mods": {"hp": -700}, "objective_text": "击碎第一颗陨石，并承受第二颗的冲击",
                "environment": "war_front",
            },
        },
        {
            "name": "轮墓·边狱",
            "enemy_id": "madara_final",
            "transition": "陨石在半空爆散，轮回眼的波纹却亮到极致。看不见的轮墓分身从四方逼近。",
            "transition_heal": 0.15,
            "special_rules": {
                "no_escape": True, "allies": allies[:3], "enemy_name": "宇智波斑·轮墓边狱",
                "enemy_skills": ["limbo_strike", "perfect_susanoo", "wood_dragon"],
                "enemy_mods": {"hp": -600}, "objective_text": "借仙术感知锁定轮墓，阻止无限月读",
                "environment": "war_front",
            },
        },
    ], intro="仙人模式与九喇嘛模式重叠,金色的光衣上浮现出仙术的纹路。\n这一战,是为了所有人的明天。")
    if result != "win":
        ui.story("""
须佐的太刀劈落的瞬间,九条命线同时亮起——
契约者们的生命力如洪流般涌入,将你从死亡线上拽了回来。

『还没结束!』『站起来,鸣人!』

你重新站起。而斑的秽土之躯,也已在联军
车轮战下裂纹遍布——
""")
        state.player["hp"] = max(1, int(state.player["max_hp"] * 0.4))
    ui.pause()

    ui.title("终章: 九命同归")
    ui.story("""
「够了。」

遍体鳞伤的斑仰头结印,轮回之瞳倒映着升起的红月——

「天盖震星。无限月读——落幕吧。」

天穹之上,陨石拖着赤红的尾焰坠落;红月的瞳术之光
开始漫过战场,联军的忍者一个接一个僵在原地——
""")
    high = [c for c in state.contracts.values() if c["unlocked"]]
    if len(high) >= 6:
        ui.story("""
——就在月光触及你的刹那,心口的九瓣花印记,
绽放出前所未有的光芒。

「九命一系·终式——」

九条命线冲天而起:赤发的封印锁链、碧绿的医疗辉光、
淡青的百豪纹路、盛放的樱色拳风、银白的毒针轨迹、
月白的柔拳掌影、纯白的千纸羽翼、金红的熔光洪流——
以及,大地本身的呼吸。

「九命同归!!」

金色的大网在天穹之上织成九瓣花的形状,
接住了坠落的陨石;命线的辉光逆流而上,
沿着月光的路径直贯红月——

轮回之瞳的图腾,在九命的光芒中寸寸碎裂。

无限月读,被扼杀在了成形的前一刻。

「……羁绊,吗。」斑望着天空中绽放的九瓣花,
 秽土之躯开始剥落,「柱间,你看到了吗。
 这个时代……或许,不需要神了。」

战国的亡灵含笑而逝。战争——结束了。
""")
        state.flags["infinite_tsukuyomi_stopped"] = True
        state.gain_fate(3, "九瓣花开,红月碎裂")
    else:
        ui.story("""
你拼尽全力将尾兽玉掷向红月,命线的光芒紧随其后——

瞳术的图腾在半空碎裂,但反噬的冲击也让所有命线
一齐黯淡下去。你单膝砸进焦土,嘴角淌血。

无限月读,终究是被止住了。只是这份代价——
命运会记在账上。

「……有趣的小鬼。」斑的秽土之躯在风中剥落,
「这个时代,交给你们了。」
""")
        state.flags["infinite_tsukuyomi_stopped"] = True
        state.add_backlash(2, "以血肉之躯撼动神明")
    ui.pause()


# ── 七、大地的声音 ───────────────────────────────

def _gaia_finale(state):
    ui.title("终章: 大地的声音")
    ui.story("""
战后的黎明。硝烟散尽,焦土之上,草芽以肉眼可见的
速度钻出地面——整个战场,正在苏醒。

你独自走在草芽之间,忽然,心底响起了那个声音。

时隔多年。温柔、古老、像大地本身。

『孩子。』

契约之树最深处,第九条命线缓缓显形——
它不指向任何一个人。它指向脚下的大地,
指向风,指向水,指向所有生命的循环。

『九年前,我给了你九道命线。』大地母亲的声音
 带着笑意,『现在,最后一条,来认领它的主人了。』

「最后一条命线……是你自己?」

『不。』风穿过草芽,像一声温柔的叹息,
『是「家」本身。孩子,你以为是我选中了你——
 其实,是你把孤独,一步一步活成了家。
 九命一系从来不是我赐予你的术。
 是你教会这片大地的,爱的形状。』
""")
    c = state.contracts["gaia"]
    c["unlocked"] = True
    c["contract_level"] = 1
    c["name"] = "大地母亲"
    c["location"] = "everywhere"
    c["note"] = "第九条命线。她一直都在——从赐术的那一天起,从生命诞生的那一天起。"
    state.gain_fate(3, "第九契约·大地之母")
    ui.slow_print("★ 第九契约达成!九条命线,至此圆满。")
    ui.slow_print("★ 战斗中可呼唤契约支援【大地之息】")
    ui.pause()


# ── 八、结局 ──────────────────────────────────

def _epilogue(state):
    f = state.flags
    true_end = (f["nagato_redeemed"] and f["obito_redeemed"] and f["asuma_saved"]
                and f["gaara_saved"] and f["jiraiya_saved"] and f["chiyo_alive"])
    if true_end:
        f["true_end"] = True
        ui.banner("九命同归 · 真结局")
        ui.story("""
战争结束的第七天,桃源。

契约之树下摆开了长长的宴席。玖辛奈和琳在灶间
争论拉面到底配不配蔬菜;纲手和照美冥拼酒拼到
第三坛;小樱和静音清点着战后的药材账目,
雏田给大家分她亲手做的点心;小南的纸鹤
在每个人头顶盘旋,大地母亲的风,拂过每一张笑脸。

村子里——

三代火影在火影岩顶钓鱼,被纲手抓包;
自来也的新书大卖,依然被玖辛奈追着打;
阿斯玛戒了烟,红抱着刚满月的女儿晒太阳;
白和再不斩开了间刀剑铺,生意兴隆;
千代婆婆的砂隐与我爱罗,成了木叶最铁的盟友;
长门和弥彦的墓前,雨之国的孩子放满了纸花;
带土在琳的药草田里除草,笨手笨脚,却笑得像十三岁;
佐助——他正站在你身边,嫌弃地看你第三碗拉面。

「喂,鸣人。」他忽然说,「这一世,算你赢了。」

「什么跟什么啊,」你笑起来,眼眶发热,
「明明是——大家一起赢的。」

九条命线在暮色里轻轻发亮,像九颗不会熄灭的星。

这一世,没有人被留在黑暗里。
这一世,所有的遗憾,都被温柔地改写。

因为家的意义,就是——谁都不许少。
""")
        state.gain_fate(3, "真结局·谁都不许少")
    else:
        ui.banner("改命者 · 结局")
        saved = []
        missed = []
        (saved if f["gaara_saved"] else missed).append("我爱罗")
        (saved if f["chiyo_alive"] else missed).append("千代")
        (saved if f["asuma_saved"] else missed).append("阿斯玛")
        (saved if f["jiraiya_saved"] else missed).append("自来也")
        (saved if f["nagato_redeemed"] else missed).append("长门")
        (saved if f["obito_redeemed"] else missed).append("带土")
        ui.story(f"""
战争结束了。焦土上立起了旗帜,也立起了墓碑。

这一世,你从命运手里抢回了:{('、'.join(saved)) or '——'}。
""")
        if missed:
            ui.story(f"""
但也有些名字,永远留在了风里:{('、'.join(missed))}。

命运的天平不会永远偏向勇者。也许在另一条世界线上,
另一个你,正把这些遗憾一一补全。

(提示: 达成全部六大改命,可解锁「九命同归·真结局」。)
""")
    ui.pause()

    state.flags["war_done"] = True
    state.chapter = 11
    quest.complete_quest(state, "fourth_war")
    state.gain_fate(6, "疾风传·完")
    state.belonging += 10
    state.add_village_trust(20)
    ui.banner("《九命一系:鸣人重生录》\n疾风传 · 全篇完")
    ui.story("""
(疾风传全部完结!自由模式:
 · 联军前线开放「深入探索」,可清剿白绝残党练级
 · 把九条命线全部提升至【九命同归】,解锁终极联合技
 · 补全剩余的忍术研究与桃源建设
 · 若未达成真结局,可读档改写更多命运
 · 感谢游玩!——「这一世,谁都不许少。」)
""")
    ui.pause()
