# -*- coding: utf-8 -*-
"""寻找纲手篇:自来也同行、旅馆的黑袍、螺旋丸师承、纲手的绝望与救赎。

设计文档 §11 第六章:说服纲手回村、学习螺旋丸、解锁医疗支援、桃源医疗室。
"""
from systems import battle, contract, quest, ui


def start(state):
    if state.player["level"] < 10:
        ui.story("""
「喂喂,就你现在这小身板,跟老子出远门?」
自来也捏了捏鸣人的胳膊,撇嘴。

(推荐等级 Lv.10。死亡森林是不错的修炼场。)
""")
        if ui.choose("现在出发吗?", ["再修炼一阵 (推荐)", "现在就出发!"]) == 0:
            return
    _departure(state)
    _itachi_inn(state)
    _rasengan_training(state)
    _tsunade_meeting(state)
    _kabuto_battle(state)
    _return_home(state)


def _departure(state):
    ui.title("剧情: 出发·寻找纲手")
    if state.flags["hiruzen_saved"]:
        ui.story("""
木叶大门。自来也把一份盖着火影印的委任状
拍在鸣人脑门上。

「老猴子的原话:『我这身老骨头撑不了几年了,
 木叶需要纲手——医疗班需要她,火影楼,迟早也需要她。』」

「所以,咱们爷俩这趟,是去把那个赌鬼请回家。」
自来也扛起行囊,咧嘴一笑,「顺便,修行。」
""")
    else:
        ui.story("""
木叶大门。晨雾未散,村子的伤口还在冒烟。

「五代目火影候选,纲手。」自来也望着远方,难得没有嬉笑,
「我的老队友,这个忍界最好的医疗忍者,
 以及——赌得最烂的赌鬼。」

「走吧,小鬼。把她找回来,木叶才能真正止血。」
""")
    ui.pause()


def _itachi_inn(state):
    ui.title("剧情: 旅馆·黑袍红云")
    ui.story("""
温泉街的旅馆。自来也被艳遇(幻术)勾走了。

鸣人盘腿坐在房间里,数着心跳。

——来了。

叩、叩。

敲门声很轻。门外立着两道黑袍红云:
一人面若寒潭,写轮眼静如深渊;
一人形似鲛鱼,背负巨刀,獠牙外露。

宇智波鼬。干柿鬼鲛。

「鸣人君,」鼬的声音听不出温度,「请跟我们走一趟。」
""")
    can_gamble = state.fate_points >= 2
    can_divert = state.player["sense"] >= 18
    opts = ["拖时间,等自来也回来 (前世的走向——佐助会赶到,并被击溃)"]
    if can_gamble:
        opts.append("赌命!凑近鼬,压低声音说出「不该知道的事」(消耗2命运点,豪赌)")
    if can_divert:
        opts.append("早有布置:影分身已引开赶来的佐助 (避免兄弟相残)")
    idx = ui.choose("面对晓,你——", opts)
    label = opts[idx]

    if label.startswith("赌命"):
        state.spend_fate(2, "在深渊边缘递出情报")
        ui.story("""
鸣人朝前一步——近得能看清鼬眼中三枚勾玉的转动。

他用只有两人能听见的音量,极轻、极稳地说:

「月之眼计划。带土。还有,团藏拿走的那只眼睛。」

「——我知道你在守护什么,宇智波鼬。」

深渊般的写轮眼,产生了一丝真正的波动。
""")
        ui.pause()
        ok = state.player["spirit"] >= 35 or state.contracts["kushina"]["contract_level"] >= 4
        if ok:
            ui.story("""
月读的世界只展开了一瞬——赤红的月亮刚刚升起,
一条金色的命线便横在了鸣人的意识之前,
温暖而不容置疑,像一位母亲张开的手臂。

鼬收回了幻术。这位灭族之夜后从未失态的男人,
沉默了足足十秒。

「……鬼鲛,撤。」

「哈?鼬,任务——」

「目标有自来也贴身护卫,强取不智。撤。」

转身的最后一刻,鼬的唇形无声地动了动。
读出来是四个字:

——『佐助,拜托。』
""")
            state.flags["itachi_knows"] = True
            state.gain_fate(2, "在深渊里,点了一盏灯")
        else:
            ui.story("""
月读的世界展开了一瞬——赤红的月亮下,鸣人单膝跪地,
冷汗如浆。幻术只扫过记忆的边缘便收了回去,
可那份精神冲击依然让他眼前发黑。

「有趣的孩子。」鼬的声音依旧平静,
「但知道得太多,会活不长。——鬼鲛,撤。」

(他没有否认。也没有杀你。这本身,就是答案。)
""")
            state.flags["itachi_knows"] = True
            state.player["hp"] = max(1, int(state.player["max_hp"] * 0.5))
            state.gain_fate(1, "赌赢了一半")
        ui.story("""
黑袍消失在走廊尽头,与赶来的自来也擦身而错。

而佐助,直到半个时辰后才追至旅馆——扑了个空。
他攥着拳头站在空房间里,青筋暴起,却终究,
没有遭遇那双足以碾碎他心志的眼睛。
""")
        state.add_rel("sasuke", "revenge", 8)
        state.add_rel("sasuke", "isolation", 5)
    elif label.startswith("早有布置"):
        ui.story("""
——三小时前,鸣人的影分身便扮作旅馆伙计,
给一路狂奔而来的佐助递了封「卡卡西急件」,
把他支去了完全相反的方向。

此刻,面对两道黑袍,鸣人反而笑了:

「二位找我?不巧,我师父马上回来。
 三忍对二晓,今天这架,打不起来吧?」

鬼鲛的巨刀刚抬到一半,走廊尽头已传来自来也的脚步声
与蛤蟆油爆开的湿响。

「……撤。」鼬淡淡道。转身时,那双写轮眼在鸣人脸上
停了半秒——像是在重新估量什么。

(佐助没有出现在这条走廊。月读的悲剧,无声地绕开了。)
""")
        state.gain_fate(2, "一封假信,救了一颗心")
        state.add_rel("sasuke", "revenge", 3)
    else:
        ui.story("""
「我哥……在哪?!」

最坏的脚步声还是来了。佐助喘着粗气堵住走廊,
千鸟在他掌心嘶鸣成一片。

之后的一切,快得像一场噩梦:千鸟被单手捏碎,
手腕被拧断,然后——月读。

七十二小时的灭族之夜,在三秒内灌进佐助的意识。

自来也赶回时,晓已远遁,只剩昏迷的佐助
和攥紧到出血的鸣人的拳头。
""")
        state.flags["sasuke_hospitalized"] = True
        state.add_rel("sasuke", "revenge", 15)
        state.add_rel("sasuke", "isolation", 10)
        state.add_rel("sasuke", "trust", -5)
        ui.slow_print("(佐助被送回木叶医院。心魔,更深了。)")
    ui.pause()


def _rasengan_training(state):
    ui.title("剧情: 师承·螺旋丸")
    ui.story("""
旅途继续。某夜,自来也买来一袋水球。

「看好了,小鬼。四代目火影的遗产——螺旋丸。
 第一步,转破水球……」
""")
    if state.flags["rasengan_learned"]:
        ui.story("""
啪。啪。啪。

水球、皮球、气球,三步连破。总耗时,一炷香。

自来也叼着的烟斗「吧嗒」掉在地上。

「……小鬼,你老实交代,」他把鸣人拎到眼前,
「这术,你是不是早就会了?」

「有、有天赋不行吗!」

「天赋?」老头眯起眼,盯着他看了半晌,忽然叹了口气,
把一只大手按在他的金毛脑袋上,揉得乱七八糟。

「行。天赋。」他说,「从今天起,这术是为师亲传的。
 以后谁问起,你就这么答——省得那些老家伙嚼舌根。」

(不完全螺旋丸 → 螺旋丸!从此名正言顺,再无暴露之忧。)
""")
        state.gain_fate(1, "师承之名,落定")
    else:
        ui.story("""
七天。水球、皮球、气球。

掌心磨破了三层皮,查克拉耗干了无数次,
第七天黄昏,一颗完整的螺旋丸终于在掌心轰然成型,
把河边的岩石钻出了一个漂亮的螺旋坑。

「哦哦——!」自来也抚掌大笑,「不愧是那两口子的种!」

★ 查克拉控制 +2!
""")
        state.player["chakra_control"] += 2
    if "rasengan_incomplete" in state.player["skills"]:
        state.player["skills"].remove("rasengan_incomplete")
    state.learn_skill("rasengan")
    state.flags["rasengan_official"] = True
    state.flags["rasengan_learned"] = True
    ui.slow_print("★ 习得正式的【螺旋丸】!(桃源可继续研究「性质变化」强化)")
    ui.pause()


def _tsunade_meeting(state):
    ui.title("剧情: 绳树街的赌鬼")
    ui.story("""
绳树街,酒馆。

找了大半个月的人,就趴在那儿——金发束成双马尾,
额间菱形印记,面前空酒壶排成一排。

传说中的医忍,纲手。以及她身后抱着小猪的静音。

「自来也?」纲手抬起眼皮,「稀客。……那个金毛小鬼是?」

谈话进行得很糟。听到「回木叶」三个字,纲手嗤笑出声;
""")
    if state.flags["hiruzen_saved"]:
        ui.slow_print("听到「老师需要你执掌医疗部」,她把酒杯捏得咯咯响;")
    else:
        ui.slow_print("听到「五代目火影」,她把酒杯直接捏成了粉末;")
    ui.story("""
「火影?」她冷笑,眼底是深不见底的疲惫,
「那是只有蠢货才会去做的工作。断,绳树,
 还有我爱过的男人——全都死在那两个字上。」

「生命,是赌桌上最没价值的筹码。谁赌谁输。」

鸣人「腾」地站了起来。
""")
    bond = 0
    picks = []
    for round_no in range(2):
        remain = [t for t in ["dream", "hokage", "medic"] if t not in picks]
        labels = {
            "dream": "说「断」与「绳树」——「他们的梦想没死,我捡起来了」",
            "hokage": "说火影之名——「那不是职位,是守护所有人的觉悟」",
            "medic": "说医疗忍者体系——「一个能让『断』们不再牺牲的构想」",
        }
        idx = ui.choose(f"(第{round_no+1}句) 你对纲手说——", [labels[t] for t in remain])
        topic = remain[idx]
        picks.append(topic)
        if topic == "dream":
            bond += 1
            ui.story("""
「断哥想当火影,是为了让村子认可他;绳树哥想当火影,
 是因为他崇拜你,想守护你!」

纲手霍然抬头:「你怎么知道绳树的——」

「因为怀着同样梦想的人,隔着多少年都能听见彼此!」
鸣人指着自己胸口,「他们的梦没死!它现在在这儿,
 在我这儿!你要连他们的梦一起埋掉吗?!」

酒馆死一样地静。纲手垂着眼,指节发白。
""")
        elif topic == "hokage":
            bond += 1
            ui.story("""
「火影不是职位!」鸣人一巴掌拍在桌上,
「是有人愿意站在所有人前面挨刀的觉悟!
 初代是你爷爷!你比谁都清楚这一点!

 你可以骂它蠢,可以逃——但不许你,
 坐在这里嘲笑那些为它死掉的人!!」

「你——!!」纲手拍案而起,额角青筋直跳。
两人隔桌对瞪,鼻尖几乎撞上。

(静音在旁边吓得直哆嗦。自来也却在偷笑。)
""")
        else:
            bond += 1
            ui.story("""
「我一直在想,」鸣人掰着手指,「为什么每个小队
 不能标配一名医疗忍者?为什么医院不能开设战地医疗科?
 为什么全忍界最强的医女,要在这里喂酒壶?

 建立那套体系,能让千千万万个『断』活着回家——
 而全世界只有一个人办得到。」

纲手的酒杯,停在了半空。

「……这套话,谁教你的?」

「未来。」鸣人认真地说。她当成了玩笑,可执杯的手,
 却久久没有放下。
""")
    ui.pause()
    ui.story("""
「……有意思的小鬼。」纲手忽然伸出一根手指,
「会螺旋丸?好。打个赌——一周之内,你要是能让
 这术再上一层楼,这条项链归你。」

她拈起颈间的碧色宝石——初代火影的项链。

「要是不能,你的钱包归我,还得承认火影是蠢货的工作。」

「一言为定!!」
""")
    state.flags["tsunade_bond"] = bond
    ui.slow_print(f"※ 与纲手的心结,解开了几分 (羁绊 {bond}/3)")
    ui.pause()


def _kabuto_battle(state):
    ui.title("剧情: 决战·药师兜")
    ui.story("""
一周之期的清晨,纲手没在旅馆。

「上钩了。」自来也脸色铁青——酒里被下了散功药,
「大蛇丸约了她。用『复活断和绳树』做筹码,
 换她医好那双手臂!」

旷野之上,对峙已经开始:纲手立在原地,浑身发抖——
不是因为大蛇丸,而是因为溅上衣角的血。

多年的血液恐惧症。传说的医忍,此刻连拳头都握不住。

「纲手大人的心,由我来守。」药师兜推了推眼镜,
 查克拉手术刀嗡嗡作响,「至于你们——顺便清理掉。」
""")
    allies = [{"name": "自来也(散功)", "power": 25, "element": "fire",
               "move": "强撑着以蛤蟆油火弹掩护", "act_rate": 0.5}]

    def win_condition(st, player, enemy, turn, log):
        if turn == 3 and not log.get("tsunade_break"):
            log["tsunade_break"] = True
            ui.story("""
兜的手术刀擦过鸣人的胸口,血花溅起——

几步之外,纲手瞳孔剧震。发抖的、蜷缩的、
被血冻住十几年的身体里,忽然撞进一个画面:

刚才,那个小鬼中刀前吼的是什么?

「离、纲、手、奶、奶、远、点——!!」

……这个蠢小鬼。和绳树,和断,和那个人,
一模一样的蠢。

「————啊啊啊,够了!!」

大地轰然炸裂!纲手一脚踏碎战场,拳风掀翻了兜,
额间印记绽开,「都给老娘,退,下!!」

血还沾在她脸上。她不再抖了。
""")
            ui.slow_print("⇒ 纲手参战!她的医疗支援将守护你!")
            allies.append({"name": "纲手", "power": 40, "element": "taijutsu",
                           "move": "怪力轰碎地面", "can_heal": True, "act_rate": 0.8})
            return None
        return None

    result = battle.battle(
        state, "kabuto",
        special_rules={"win_condition": win_condition, "no_escape": True,
                       "allies": allies},
        intro="「让我看看,写在你身体里的『情报』。」兜的镜片闪着冷光。")
    if result == "lose":
        ui.story("""
意识模糊的最后,一双带着菱形印记的手接住了他,
碧绿的医疗查克拉温柔地裹住全身——

「睡吧,小鬼。」纲手的声音又稳又暖,
「接下来,是大人的战场。」

(通灵三方大战的地动山摇里,你昏睡了过去。
 醒来时,大蛇丸已败走,而纲手正守在床边。)
""")
        state.player["hp"] = state.player["max_hp"] // 2
    else:
        ui.story("""
「螺旋丸——!!」

风之旋涡正中兜的腹部,把他钻飞出去十几丈,
撞穿了两块巨岩才停下来。

大蛇丸看看废掉的心腹,又看看自己枯萎的双臂,
再看看怒发冲冠的纲手与拄刀而立的自来也——

「啧。今天的账,先记下。」

蛇影遁地而走。旷野上只剩风声,和纲手
似怒似笑的一声:「小鬼,过来,包扎!」
""")
    ui.pause()
    ui.story("""
当夜,篝火边。纲手把初代的项链,轻轻挂上了鸣人的脖子。

「赌,是你赢了。」她凝视着那块碧色宝石,目光穿过它,
 望向很多年前,「这石头克死过两个戴它的人。
 但不知道为什么……我觉得你小子,能镇得住它。」

「那当然!」鸣人攥住项链,咧嘴大笑,
「我可是要当火影的男人!」

「哈,口气不小——」纲手屈指,朝他额头轻轻一弹,
 指尖停在他的发间,揉了揉,

「——赌你能赢,鸣人。」
""")
    state.flags["tsunade_bond"] = min(3, state.flags["tsunade_bond"] + 1)
    state.gain_fate(2, "赢下了传说医忍的赌局")
    ui.pause()


def _return_home(state):
    ui.title("剧情: 归村")
    if state.flags["hiruzen_saved"]:
        ui.story("""
木叶大门。三代火影亲自拄杖相迎。

「老师。」纲手在老人面前站定,千言万语,
 最后只化作一句,「……我回来了。」

「回来就好。」老人笑出满脸沟壑,「医疗部,交给你了。
 至于火影这顶帽子嘛——老夫再替你焐两年。」

木叶医疗部部长·纲手,走马上任。
医院的走廊里,从此多了一个雷厉风行的身影,
和一群闻风丧胆又干劲十足的医疗班学员。
""")
    else:
        ui.story("""
木叶大门。长老与守卫列队相迎。

纲手在门前驻足,望着火影岩上四张石刻的面孔,
以及旁边尚未动工的、属于第五张的位置。

「真是,」她低声骂了一句,「蠢到家的工作。」

然后,她大步走进了村门。

数日后,火影岩上开凿的锤声响起——
五代目火影·纲手,就任。
""")
    quest.complete_quest(state, "tsunade_search")

    # 桃源医疗室 & 契约者共鸣
    if not state.has_building("medical_room"):
        state.tougen_buildings.append("medical_room")
        ui.story("""
当晚的桃源,琳围着新落成的医疗室转了一圈又一圈,
眼睛亮得像星星。

「病床!无影灯!还有整面墙的药柜!」她攥着鸣人的袖子,
「这是照着纲手大人的战地医疗构想建的吧?!
 鸣人,以后你受一次伤,我就在这里给你修一次!
 ——啊不对,最好还是别受伤!」

★ 桃源【医疗室】落成!(每次进入桃源获得回复丹)
""")
    contract.grant_level(state, "rin",
                         max(3, state.contracts["rin"]["contract_level"]),
                         "医者之魂,共鸣加深")
    if state.relations["sakura"]["medical"] >= 15:
        ui.story("""
更让人高兴的是——递到医疗班报名表最上面的那份,
署名「春野樱」。

「查克拉控制,十年一遇。」纲手翻着她的档案,挑眉,
「行,这徒弟,老娘收了。」

(小樱的医疗之路,比原本的命运提前了整整一年。)
""")
        state.add_rel("sakura", "confidence", 10)
        state.add_rel("sakura", "responsibility", 8)

    # 桃源邀请
    if state.flags["tsunade_bond"] >= 2:
        _tougen_invitation(state)
    else:
        ui.slow_print("(与纲手的羁绊尚浅。今后可以在火影办公室拜访她,慢慢积累信任。)")

    state.flags["tsunade_done"] = True
    state.flags["tsunade_returned"] = True
    state.chapter = 6
    ui.story("""
═══════════════════════════

        寻找纲手篇 · 完

═══════════════════════════

(村子恢复了元气。但命运的下一个漩涡,已经在酝酿——
 · 佐助的心结,需要尽快去化解 (宇智波族地遗址/医院)
 · 桃源的契约之树,或许能迎来第三条命线
 · 当一切准备就绪,回家睡一觉……某个夜晚,即将到来
 · 记得存档!)
""")
    ui.pause()


def _tougen_invitation(state):
    ui.title("剧情: 第三条命线的方向")
    ui.story("""
琳听说了旅途的经过,托着腮想了想,忽然说:

「纲手大人……她其实,是玖辛奈阿姨的远亲哦。
 同是漩涡血脉——初代夫人漩涡水户大人,是她的祖母。」

红枫林里,玖辛奈也点头:

『嗯。论辈分,她还是我半个前辈。这忍界上,
 能让那个女人真心软下来的东西不多了——
 家人,算一个。』

她看向鸣人,目光温柔而郑重:

『鸣人,如果你信得过她——把桃源给她看吧。
 让她知道,她在这个世上,还有家。』

(契约之树中,纲手的命线已经开始泛光。
 当好感、信任、安全感与命运共鸣足够时,
 就可以在【契约之树】缔结第三契约。)
""")
    c = state.contracts["tsunade"]
    bond = state.flags["tsunade_bond"]
    c["affection"] = 60 + bond * 5
    c["trust"] = 70 + bond * 5
    c["safety"] = 70 + bond * 5
    c["fate_resonance"] = 50 + bond * 10
    c["note"] = "命线已开始泛光。在火影办公室拜访她可加深羁绊。"
    state.flags["tsunade_tougen_invited"] = True
    ui.slow_print(f"※ 纲手: 好感{c['affection']} 信任{c['trust']} 安全感{c['safety']} 共鸣{c['fate_resonance']}")
    ui.pause()


def visit_tsunade(state):
    """火影办公室/医院:拜访纲手,加深羁绊 (可重复)。"""
    import random
    c = state.contracts["tsunade"]
    if c["unlocked"]:
        ui.story("""
「哟,来了。」纲手头也不抬地批着文件,
 顺手把一碟茶点往鸣人那边推了推。

命线微微发亮。有些陪伴,不需要言语。
""")
        state.belonging += 1
        ui.slow_print(f"※ 归属感 +1 [当前: {state.belonging}]")
        ui.pause()
        return
    ui.story(random.choice([
        """
「无聊。」纲手把一摞文件拍在桌上,「陪老娘下一盘将棋。」

一个时辰后,鸣人被杀得片甲不留,却赖着不肯认输,
非要「再来最后一把」——第七次。

「噗。」纲手终于绷不住笑了,「跟绳树一个德行。」
""",
        """
医疗部的午后。鸣人抱着一摞卷宗跑前跑后,
帮着分拣药品、安抚哭闹的小病号。

纲手倚在门口看了很久。

「喂,小鬼,」她忽然说,「你身上……有种让人
 想相信『明天』的味道。真讨厌。」

嘴上说着讨厌,嘴角却是弯的。
""",
        """
「项链,还好好戴着?」

「当然!」鸣人扯出领口的碧色宝石晃了晃,亮闪闪的。

纲手看着那块石头在少年胸前发光,而少年活蹦乱跳、
中气十足——一直堵在心口十几年的什么东西,
好像又化开了一点。
""",
    ]))
    for key in ("affection", "trust", "safety"):
        c[key] = min(100, c[key] + 5)
    c["fate_resonance"] = min(100, c["fate_resonance"] + 5)
    state.belonging += 1
    ui.slow_print(f"※ 纲手: 好感{c['affection']} 信任{c['trust']} 安全感{c['safety']} 共鸣{c['fate_resonance']}")
    from systems.contract import can_contract
    if can_contract(c):
        ui.slow_print("(纲手的心防已经放下。去桃源的【契约之树】,缔结第三契约吧!)")
    ui.pause()
