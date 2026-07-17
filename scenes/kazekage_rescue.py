# -*- coding: utf-8 -*-
"""疾风传·序 + 风影夺还篇:三年修行、砂隐驰援、蝎与迪达拉、千代的命运。"""
from systems import battle, quest, ui


def depart(state):
    """木叶大门:与自来也踏上三年修行之旅(疾风传开幕)。"""
    p = state.player
    if p["level"] < 16:
        idx = ui.choose(
            f"自来也倚在大门边打量你:「小鬼,三年可不是郊游。」(当前 Lv.{p['level']},建议 Lv.16+)",
            ["再准备准备 (推荐)", "现在就出发!"])
        if idx == 0:
            ui.slow_print("「不急。把该结的契约结了,该修的术修了,随时来找我。」")
            return

    ui.title("疾风传·序章: 三年之约")
    ui.story("""
出发前夜，你在桃源摆了一桌饯行宴。

玖辛奈往你包里塞了第五张封印符，琳把亲手做的药丸
按「苦→不苦」的顺序排好，纲手灌了三杯酒之后
终于承认「那个老色鬼教东西还是有两下子的」。

『三年。』玖辛奈替你理了理领口，像每一个送孩子远行的母亲，
『别忘了写信——桃源的门,在哪里都能打开。』
""")
    ui.pause()

    if state.flags["sasuke_ending"] == 4:
        ui.story("""
大门口，除了背着行囊的自来也，还站着另一个身影。

「吊车尾的，」佐助抱着手臂，别过脸，「三年后，比比谁走得更远。」

改命同盟的两人击了一次拳。这一次的离别，不是逃离，是约定。
""")
        state.add_rel("sasuke", "trust", 5)
    elif state.flags["sasuke_ending"] == 2:
        ui.story("""
你在大门的门柱上，发现了一道新刻的划痕——
和终结谷那天，他护额上的那道，一模一样。

(约定还在。三年后，两条路会再次交汇。)
""")
    ui.pause()

    ui.title("剧情: 三年修行")
    ui.story("""
三年，说长不长，说短不短。

自来也带着你走遍了火之国的边境:在瀑布下打坐，
在雪原里追踪，在温泉镇……帮他挡了无数个巴掌。

桃源的门始终开着。玖辛奈的封印课、琳的医疗课、
纲手隔空批改的查克拉控制作业——这三年，你不是一个人在修行。
""")
    ui.pause()
    idx = ui.choose("三年间，你把修行的重心放在——", [
        "体术与实战 (攻击/防御大幅成长)",
        "查克拉与忍术 (查克拉与控制大幅成长)",
        "封印与感知 (封印术/感知大幅成长)",
    ])
    # 三年成长:相当于+3级的底子,再加侧重加成
    p["level"] += 3
    p["max_hp"] += 45
    p["max_chakra"] += 36
    p["attack"] += 9
    p["defense"] += 6
    p["speed"] += 6
    p["spirit"] += 6
    if idx == 0:
        p["attack"] += 6
        p["defense"] += 4
        ui.slow_print("※ 拳头替你记住了每一课。攻击 +15、防御 +10 (含基础成长)。")
    elif idx == 1:
        p["max_chakra"] += 30
        p["chakra_control"] += 5
        ui.slow_print("※ 查克拉如海。查克拉上限 +66、查克拉控制 +5 (含基础成长)。")
    else:
        p["seal_art"] += 5
        p["sense"] += 5
        ui.slow_print("※ 纹路与气息皆入掌心。封印术 +5、感知 +5 (含基础成长)。")
    p["hp"] = p["max_hp"]
    p["chakra"] = p["max_chakra"]
    ui.slow_print(f"★ 三年归来!鸣人 Lv.{p['level']},全属性大幅成长,状态全满。")
    state.flags["shippuden_started"] = True
    quest.complete_quest(state, "timeskip_training")
    ui.pause()

    ui.story("""
再次站上木叶大门的土路时，风里有熟悉的拉面香。

「哟，回来啦。」卡卡西从檐上跳下来，手里还捏着新刊《亲热天堂》——
下一秒书被没收了。小樱叉着腰站在他身后，医疗手套在阳光下发亮。

「鸣人!你长高了!」

三年不见，每个人都往前走了很远。而命运,也没有停下脚步——
""")
    ui.pause()
    ui.story("""
一只信鹰尖啸着俯冲进村，鹰哨是砂隐的加急频率。

『木叶收信:砂隐村遭「晓」袭击。
 风影我爱罗——被带走了。』

前世的记忆轰然对位。风影夺还战，开始了。
""")
    state.gain_fate(1, "命运的钟声再次敲响")
    ui.pause()
    _rescue(state)


def _rescue(state):
    ui.title("风影夺还篇: 驰援砂隐")
    ui.story("""
卡卡西班全速奔驰三天，赭黄色的岩壁终于出现在地平线上。

砂隐村内一片狼藉。勘九郎躺在病床上，肤色青黑——
蝎的剧毒，前世要等小樱赶到才有解。

「让开。」小樱挽起袖子，「配药需要人手，鸣人，去按住他。」

三个时辰后，毒解了。医疗班的走廊里，一位白发盘髻的
老婆婆盯着卡卡西看了半晌，突然暴起——

「木叶白牙!!为我儿报仇——」

(千代婆婆。前世也是这一幕。)
""")
    ui.pause()
    idx = ui.choose("千代婆婆扑向卡卡西,你——", [
        "按原剧情让卡卡西挨这一下 (然后看她自己认错)",
        "上前一步替卡卡西挡下,认真自我介绍",
    ])
    if idx == 0:
        ui.story("""
「婆婆,白牙前辈早就过世了,这位是他儿子。」

「……哦。认错人了。」千代婆婆收手收得毫无心理负担,
全场砂隐忍者一起扶额。

(这个装傻的老太太,前世用命换回了我爱罗。这一世——)
""")
    else:
        ui.story("""
你侧身挡在两人之间，抱拳一礼:

「漩涡鸣人，我爱罗的朋友。婆婆，带路吧——
 我们去把你们的风影，抢回来。」

千代婆婆眯起浑浊的眼睛打量你，半晌，嗤笑一声:
「口气不小,小鬼。老婆子倒要亲眼看看。」
""")
        state.gain_fate(1, "向命运递出的名帖")
    ui.pause()
    _sasori_battle(state)


def _sasori_battle(state):
    ui.title("剧情: 洞窟前的红砂")
    ui.story("""
追踪两日，晓的巢穴出现在河之国的断崖下。
巨石封门，封印结界在小樱的怪力与四方牵制下轰然碎裂。

洞窟深处，佝偻的傀儡「响尾」缓缓抬头，外壳寸寸剥落——
里面走出一张永远年轻的脸。

「千代婆婆,好久不见。」赤砂之蝎轻声说,
「正好。我collection里,还缺一具漩涡一族。」

千代婆婆的十指间，查克拉丝无声绷紧:
「孙儿的错,由奶奶来收拾。小鬼们,借你们的命一用!」
""")
    allies = [
        {"name": "千代", "power": 32, "element": "taijutsu",
         "move": "操纵父母傀儡夹击", "act_rate": 0.8},
        {"name": "小樱", "power": 30, "element": "taijutsu",
         "move": "怪力粉碎傀儡", "can_heal": True, "act_rate": 0.6},
    ]
    result = battle.multi_stage_boss_battle(state, [
        {
            "name": "绯流琥·毒尾",
            "enemy_id": "sasori",
            "intro": "佝偻的绯流琥甩开钢铁蝎尾，毒针封死洞窟每一条退路。",
            "special_rules": {
                "no_escape": True, "allies": allies,
                "enemy_name": "蝎·绯流琥", "enemy_skills": ["puppet_barrage", "poison_mist"],
                "enemy_mods": {"hp": -400}, "objective_text": "击碎绯流琥外壳",
            },
        },
        {
            "name": "三代风影·铁砂界法",
            "enemy_id": "sasori",
            "transition": "绯流琥轰然崩碎，三代风影傀儡从卷轴中升起，铁砂将洞顶染成黑色。",
            "transition_heal": 0.15,
            "special_rules": {
                "no_escape": True, "allies": allies, "enemy_name": "蝎·三代风影傀儡",
                "enemy_skills": ["iron_sand_wave", "puppet_barrage"],
                "enemy_mods": {"hp": -300}, "objective_text": "突破铁砂并破坏风影傀儡",
            },
        },
        {
            "name": "赤秘技·百机操演",
            "enemy_id": "sasori",
            "transition": "蝎扯开晓袍，胸口再生核亮起。上百具红衣傀儡从洞窟穹顶倾泻而下。",
            "transition_heal": 0.15,
            "special_rules": {
                "no_escape": True, "allies": allies, "enemy_name": "赤砂之蝎·本体核心",
                "enemy_skills": ["puppet_barrage", "poison_mist", "iron_sand_wave"],
                "enemy_mods": {"hp": -320}, "objective_text": "穿过百机操演，击碎唯一的再生核",
            },
        },
    ], intro="铁砂在半空凝成棘林。这是傀儡师的巅峰对决,而你是那枚最不讲理的变数。")
    if result == "win":
        ui.story("""
最后一具傀儡的核心被螺旋丸洞穿。蝎跪在他亲手做的
「父亲」与「母亲」傀儡之间，像终于回到了等待了几十年的怀抱。

「……真慢啊,奶奶。」

千代婆婆闭上眼。再睁开时，她朝你们摆摆手:
「愣着干什么。迪达拉那个小混蛋,带着我爱罗往西边去了。」
""")
        state.add_rel("sakura", "confidence", 8)
        state.gain_fate(2, "傀儡师的谢幕")
    else:
        ui.story("""
毒雾漫过视野的最后一刻，千代婆婆的查克拉丝拽着所有人
撤出了洞窟。蝎没有追——他望着「父母」傀儡，出了神。

「小鬼,欠老婆子一条命。」

(战败了。但追击还要继续——)
""")
        state.player["hp"] = max(1, state.player["max_hp"] // 3)
    ui.pause()
    _deidara_battle(state)


def _deidara_battle(state):
    ui.title("剧情: 白鸟与夕阳")
    ui.story("""
断崖之上，白色巨鸟驮着一具红发的身体腾空而起。

「哟,九尾。」迪达拉坐在鸟首,居高临下地笑,
「一尾已经拔完了。想要?来追啊——嗯!」

我爱罗闭着眼，随鸟身轻轻晃动，像一枚被丢弃的空壳。

胸口的九命印记烫得发疼。前世你也是这样追着这只鸟,
追到指甲抠进掌心。这一世——

「卡卡西老师!」
「知道了。」写轮眼的万花筒纹路缓缓旋转,「压低他的高度,交给我。」
""")
    result = battle.battle(state, "deidara", special_rules={
        "no_escape": True,
        "allies": [
            {"name": "卡卡西", "power": 36, "element": "lightning",
             "move": "以神威撕裂粘土", "act_rate": 0.75},
        ],
        "environment": "desert",
    }, intro="起爆粘土如雨点般落下。艺术家的表演,该谢幕了。")
    if result == "win":
        ui.story("""
巨鸟在神威的漩涡中失去半边翅膀，你踏着影分身搭成的
阶梯跃上高空，一把抱住我爱罗坠落的身体。

迪达拉断了一条手臂，狼狈遁走。追,还是先顾我爱罗——
没有任何犹豫。你抱着那具轻得不像话的身体,落回沙丘。
""")
        state.gain_fate(2, "从赤云手中夺回的重量")
    else:
        ui.story("""
爆炸的气浪把你掀翻在沙丘上。但迪达拉的巨鸟也被雷切
削断了尾羽——他咂咂嘴,把我爱罗的身体丢了下来:

「拿去,嗯。反正『抽取』已经完成了——剩下的是空壳。」

你连滚带爬地冲过去,接住了那具冰冷的身体。
""")
        state.player["hp"] = max(1, state.player["max_hp"] // 3)
    ui.pause()
    _gaara_fate(state)


def _gaara_fate(state):
    ui.title("命运节点: 沙海的天平")
    ui.story("""
夕阳把沙丘染成血色。我爱罗躺在中央，没有呼吸。

一尾被拔离的人柱力，前世如此，这一世依然。

千代婆婆缓缓跪坐在他身边，十指结印——你认得这个印。
【转生术】。以命换命的禁术。

『孩子,』地球母亲的声音在心底响起,
『天平的两端各放着一条命。你可以旁观命运,
 也可以把你们的命线,也压上去。』
""")
    opts = ["按原轨迹:让千代婆婆完成她选择的谢幕 (我爱罗复活,千代逝去)"]
    can_rewrite = state.fate_points >= 3
    if can_rewrite:
        opts.append("以九命一系辅助转生术 (消耗3命运点:两条命,都留下)")
    else:
        opts.append("[命运点不足3] 命线黯淡,无力干涉")
    idx = ui.choose("", opts)

    if idx == 1 and can_rewrite and state.spend_fate(3, "把两条命都从天平上抱下来"):
        ui.story("""
「婆婆,等等!」你在她身边跪下,九瓣花印记亮起,
「转生术缺的是『生命力』,对吧?——用我的!」

金色的命线自你心口涌出,缠上她枯瘦的手腕。桃源的方向,
玖辛奈、琳、纲手的力量顺着命线一齐灌来,像春水汇入干涸的河。

「还有我!」小樱在另一侧跪下,双手覆上千代婆婆的手背,
翠绿的医疗查克拉稳稳汇入,「生命力的『输出通道』交给我——
 婆婆,您只管施术!」

千代婆婆愣住了。掌心之下,我爱罗的胸口开始起伏,
而她自己的生命,一丝一毫都没有流失。

「这是……什么术?」
「不是术。」你笑得眼睛发酸,「是『家人』。」
""")
        state.flags["gaara_saved"] = True
        state.flags["chiyo_alive"] = True
        state.add_rel("sakura", "confidence", 10)
        state.add_backlash(1, "命运的天平被强行扶正")
        state.gain_fate(2, "沙海的黎明")
        ui.pause()
        _sakura_contract(state)
    else:
        ui.story("""
淡蓝色的光从千代婆婆掌心流进我爱罗的胸口。

「……我这一生,尽是错处。」她的声音越来越轻,
「把未来托给你们这些孩子——是老婆子唯一做对的事。」

我爱罗睁开眼时,千代婆婆的手,永远垂落在沙丘上。

万千砂隐忍者跪满沙丘。你握紧拳头,指甲抠进掌心——
这一世,还是没能……不,不一样了。至少我爱罗看见了,
自己被多少人需要着。
""")
        state.flags["gaara_saved"] = True
        state.flags["chiyo_alive"] = False
        state.gain_fate(2, "被托付的未来")
        state.belonging += 2
        ui.pause()
        _sakura_contract(state)
    ui.pause()
    _epilogue(state)


def _sakura_contract(state):
    ui.title("契约: 樱色的手")
    ui.story("""
当夜，砂隐村的灯火渐次熄灭。你在客舍的檐下坐着,
听见身后传来熟悉的脚步声。

「果然在这里。」小樱在你身边坐下,膝上抱着医疗包,
沙漠的夜风吹起她的短发。
""")
    if state.flags["chiyo_alive"]:
        ui.story("""
「今天那个……命线的术。」她盯着自己的掌心,轻声说,
「查克拉顺着它流过去的时候,我『看见』了。
 玖辛奈阿姨、琳前辈、师父——还有一个暖得像春天的地方。」

「那是桃源。」你说,「我们的家。」

「『我们』。」她重复了一遍这个词,忽然笑了,
 眼眶却红了,「从忍者学校到现在,你一直在往前跑。
 波之国、中忍考试、终结谷……我总觉得自己在后面追。

 但今天,在婆婆的转生术上,我们的查克拉是并排的。
 第一次,并排的。」
""")
    else:
        ui.story("""
「婆婆的手垂下去的时候,」她盯着自己的掌心,轻声说,
「我就在旁边。医疗忍者的手,却什么都做不了。

 可你不一样。你心口那个印记亮起来的时候,我『看见』了——
 玖辛奈阿姨、琳前辈、师父,还有一个暖得像春天的地方。
 如果……如果当时我也在那些命线里,是不是,
 就能多分一份生命力给婆婆?」

「小樱……」

「不是自责。」她摇摇头,抬起眼,目光亮得惊人,
「是不想再站在『来不及』的那一边了。一次都不想。」
""")
    ui.pause()
    ui.story("""
她伸出手,掌心向上,摊在你面前——
那双手,既砸得碎岩石,也缝得好伤口。

「鸣人。把那条命线,也分我一条吧。」

小樱的眼睛在沙漠的星空下亮得惊人:

「不是被保护的位置。是并肩的位置——
 你冲在前面的时候,背后的伤,全部由我来治;
 你倒下的时候,把你捶醒的人,也必须是我。」

你握住那只手。九瓣花印记亮起,樱色的命线
如春水般漫开,与赤、碧、青三色缠在一起。

『契约成立。……哭什么啊笨蛋,又不是生离死别!』
『你、你才哭了呢!』

(两个人都哭了。沙漠的夜风,温柔得像桃源的风。)
""")
    c = state.contracts["sakura"]
    c["unlocked"] = True
    c["contract_level"] = 1
    c["affection"] = 82
    c["trust"] = 88
    c["safety"] = 85
    c["fate_resonance"] = 75
    c["location"] = "konoha"
    c["note"] = "第四位契约者。第七班的同伴,从并肩的这一天起,再也不是追赶背影的人。"
    state.flags["sakura_contracted"] = True
    state.add_rel("sakura", "trust", 10)
    state.add_rel("sakura", "sasuke_obsession", -10)
    state.gain_fate(2, "第四契约·并肩之樱")
    ui.slow_print("★ 小樱契约达成!契约等级 1【初契】")
    ui.slow_print("★ 战斗中可呼唤契约支援【怪力回春】")
    ui.pause()


def _epilogue(state):
    ui.title("剧情: 风影的道谢")
    ui.story("""
临行那天，我爱罗送到村口。风卷着沙,他的话依然不多。

「鸣人。」他伸出手,「上一次,是你把我从『只有自己』的
 世界里拉出来。这一次,是你把我从死亡里拉回来。」

「朋友之间,不用记这些。」你握住那只手。

「要记。」我爱罗认真地摇头,砂隐风影的目光沉静如渊,
「因为下一次——换我护你。」
""")
    if state.flags["chiyo_alive"]:
        ui.slow_print("(千代婆婆挥挥手:「滚吧滚吧,老婆子还欠你一条命——改天拿傀儡手艺还!」)")
    state.flags["gaara_redeemed"] = True  # 疾风传的羁绊延续
    state.flags["kazekage_done"] = True
    quest.complete_quest(state, "kazekage_rescue")
    state.add_trust(5)
    state.belonging += 5
    ui.slow_print(f"※ 归属感 +5 [当前: {state.belonging}]")
    state.chapter = 8
    ui.banner("风影夺还篇 · 完")
    ui.story("""
(下一步指引:
 · 火影办公室有新的主线「晓之阴影」——十班的命运正在逼近
 · 砂隐村已在地图开放,可以随时拜访我爱罗
 · 桃源的契约之树上,小樱的命线等着深化
 · 记得存档!)
""")
    ui.pause()


def suna_visit(state):
    """砂隐村日常:拜访我爱罗(与千代)。"""
    ui.title("剧情: 风影办公室的茶")
    if state.flags["chiyo_alive"]:
        ui.story("""
风影办公室里，我爱罗批文件，千代婆婆蹲在窗台上修傀儡,
一老一少谁也不说话，却意外地和谐。

「鸣人。」我爱罗推来一盏茶,「坐。」

「小鬼,来得正好,」千代婆婆头也不抬,「搭把手,上弦。」

一下午就这么过去了。临走时,我爱罗在门口说:
「随时欢迎。这里……也是你的村子。」
""")
    else:
        ui.story("""
风影办公室的窗台上，摆着一具小小的傀儡——
千代婆婆生前最后修好的那具。

「她说过,砂隐的未来托给我了。」我爱罗望着傀儡,
「所以我打算,让砂隐成为第一个和木叶缔结永久同盟的村子。」

「她会看到的。」你说。

「嗯。」风影少见地,轻轻笑了一下。
""")
    state.belonging += 2
    ui.slow_print(f"※ 归属感 +2 [当前: {state.belonging}]")
    ui.pause()
