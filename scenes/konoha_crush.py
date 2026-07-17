# -*- coding: utf-8 -*-
"""木叶崩溃篇:羽毛幻术、我爱罗暴走、天台结界——三代的生死节点。

设计文档 §11 第五章:击退大蛇丸、拯救三代、感化我爱罗、保护平民。
玖辛奈在此篇可能第一次实体化短暂现身。
"""
from systems import battle, contract, quest, ui


def invasion(state):
    _feathers(state)
    _gaara_pursuit(state)
    _rooftop_fate(state)
    _aftermath(state)


def _feathers(state):
    ui.title("剧情: 崩溃开始")
    ui.story("""
「解!」

羽毛落满肩头之前,鸣人的双手早已结好了印。
睡意如潮水漫过全场——又从他身周分开。

爆炸声接连响起。城墙方向,砂隐的巨蛇撞碎了工事;
看台上,伪装成观众的音忍暴起发难;
火影包厢中,「风影」挟持三代跃上天台,
四紫炎阵的紫色结界轰然升起!
""")
    if state.flags["warned_hokage"]:
        ui.story("""
但是——这一次,木叶没有慌乱。

「暗部,按预案行动!」「疏散组走三号线!」
「结界班,压制城墙缺口!」

早已加倍的巡逻与预案,让侵略者的第一波攻势
硬生生撞在了铁板上。

(你的进言,救下了此刻无数条命。)
""")
        state.gain_fate(2, "先见之明,化作了盾")
    if state.flags["haku_alive"] and state.flags["zabuza_alive"]:
        ui.story("""
战场的另一角,忽然腾起漫天冰雾——

「奉卡卡西先生担保状之约,前来助阵。」
白的冰镜封住了整条平民疏散街的入口,
再不斩的斩首大刀,把闯进来的音忍成片扫飞。

「喂喂,这就是木叶的危机?」鬼人咧嘴狞笑,
「比雾隐的政变,差远了!」

(波之国改写的命运,此刻回报了木叶。平民伤亡大幅降低。)
""")
        state.gain_fate(1, "昔日善因,今日善果")
    elif state.flags["haku_alive"]:
        ui.story("""
平民疏散的街口,一道白色身影悄然而立,
冰镜折射着火光,千本精准地放倒一个个音忍。

(白,来赴约了。)
""")
        state.gain_fate(1, "昔日善因,今日善果")
    ui.pause()


def _gaara_pursuit(state):
    ui.title("剧情: 追击我爱罗")
    ui.story("""
「鸣人,佐助,小樱——追击我爱罗!」卡卡西格开一刀,
头也不回,「他是砂隐的王牌,不能让他在村里暴走!」

森林里,追上的时候,我爱罗已经不对了——
半边身体膨胀成黄褐色的砂爪,眼白里全是杀意,
守鹤的纹路在皮肤上蔓延。

「漩涡,鸣人——!!」怪物盯住了他,嘴角咧到耳根,
「杀了你……我就能,确认自己活着!!」

佐助横到半途就被砂浪拍飞,撞在树干上咳血;
小樱护住昏迷的佐助,被砂爪钉在树上,不断收紧——!

「放开他们。」鸣人向前一步,声音低得可怕,
「你的对手,从头到尾,只有我。」
""")
    def extra_actions(log):
        return ["以言语共鸣 (向同类伸出手)"]

    def action_handler(label, st, player, enemy, log):
        if not label.startswith("以言语共鸣"):
            return False
        attempts = log.get("talk", 0) + 1
        log["talk"] = attempts
        ready = (enemy["hp"] <= enemy["max_hp"] * 0.55) or log.get("turn_now", 0) >= 5
        bond = st.flags["gaara_bond"]
        if ready and (bond >= 1 or attempts >= 3):
            log["gaara_reached"] = True
            return True
        ui.story("""
「我爱罗!听我说——孤独的滋味,我最清楚!」

「闭嘴闭嘴闭嘴!!」砂浪疯狂拍来,
「爱……只留给自己!其他人,全都去死!!」

(话,他听见了。但还不够——要么打进他心里,
 要么先打碎那层沙。)
""")
        dmg = max(1, int(enemy["attack"] * 0.5))
        player["hp"] -= dmg
        ui.slow_print(f"  被砂浪扫中,受到 {dmg} 点伤害!")
        return True

    def win_condition(st, player, enemy, turn, log):
        log["turn_now"] = turn
        if log.get("gaara_reached"):
            return "redeemed"
        return None

    result = battle.battle(
        state, "gaara_berserk",
        special_rules={"extra_actions": extra_actions, "action_handler": action_handler,
                       "win_condition": win_condition, "no_escape": True,
                       "objective_text": "压制守鹤化，并通过共鸣唤回我爱罗",
                       "environment": "desert"},
        intro="「沙瀑送葬——!!」铺天盖地的黄沙,遮蔽了天空!")

    if result == "redeemed":
        state.gain_exp(260)
    if result in ("redeemed", "win"):
        ui.story("""
沙,散了。

两个遍体鳞伤的少年并排躺在树根间,谁也动不了。
鸣人用下巴一点一点地,朝我爱罗的方向蹭。

「你、还要过来……为什么……」沙之少年的声音
第一次带上了恐惧之外的颤抖,「明明,那么痛——」

「因为我知道那种孤独。」鸣人喘着气,笑了,
「也因为,我现在有了很多很重要的人。
 为了守护重要的人,痛算什么。」

「……重要的,人。」

「嗯。你也会有的,我爱罗。从今天起,先算我一个。」

远处,手鞠和勘九郎赶到,如临大敌——
我爱罗却缓缓抬手,拦住了他们。

「……回家。」他说。顿了顿,又轻声补了一句,
「对不起。」

砂隐三姐弟消失在林海。风里,好像有什么坚硬的东西,
碎掉了一角。
""")
        state.flags["gaara_redeemed"] = True
        state.gain_fate(2, "把手伸进了沙漠")
        state.add_rel("sasuke", "trust", 5)
    else:
        ui.story("""
意识模糊的最后,一道白影与一道黑影赶到——
卡卡西与凯,联手逼退了失控的守鹤。

我爱罗被砂隐仓皇带走。鸣人躺在担架上,
望着天,拳头攥了又松。

(没能传达到……但那双空洞的眼睛里,
 确实有什么东西,晃了一下。)
""")
        state.flags["gaara_redeemed"] = False
        state.player["hp"] = max(state.player["hp"], state.player["max_hp"] // 4)
    ui.pause()


def _rooftop_fate(state):
    ui.title("命运节点: 紫焰之内")
    ui.story("""
处理完我爱罗,鸣人拖着伤体奔回村中——

火影楼天台,紫色的四紫炎阵仍未熄灭。

结界之内,三代火影僵直地立着,双手结着最后的印;
他身前,大蛇丸脸色惨白地嘶吼——尸鬼封尽的死神
已经显出虚影,正一寸寸拖拽着白蛇的双臂与灵魂!

前世的此刻,老人以命换臂,烟斗声从此绝于木叶。

心口的九瓣印记,烫得几乎烧穿胸膛。

『孩子,』地球母亲的声音响起,『这是一条沉重的命运。
 猿飞日斩自己选择了死亡——要逆着他的觉悟伸手,
 代价,比波之国大得多。』
""")
    cost = 5
    if state.flags["warned_hokage"]:
        cost -= 1
    kushina_ok = state.contracts["kushina"]["contract_level"] >= 3
    if kushina_ok:
        cost -= 1
    cost = max(2, cost)

    opts = [f"燃烧命运点,撞进结界救三代!(消耗{cost}命运点)"
            if state.fate_points >= cost else
            f"[命运点不足{cost}] 撞进结界救三代 (无法做到)",
            "尊重老人的觉悟,守住结界外的战场 (原剧情结局)"]
    idx = ui.choose("", opts)

    if idx == 0 and state.fate_points >= cost:
        state.spend_fate(cost, "逆命救人")
        ui.story("""
「影分身之术!!」

上百个鸣人同时扑向结界四角的音忍四人众——
不求破阵,只求一秒的动摇!

紫焰晃动的刹那,本体已经贴地窜入结界缺口!

「爷爷——住手!!那一式,不用把命搭进去!!」
""")
        if kushina_ok:
            contract.grant_level(state, "kushina",
                                 max(4, state.contracts["kushina"]["contract_level"]),
                                 "命线在生死场上淬炼")
            ui.story("""
心口的印记轰然炸开金光——

赤红色的长发在光中飞扬。漩涡玖辛奈的身影,
第一次,以近乎实体的姿态降临在现实的天台上!

『猿飞老师!』她双手结印,金色的锁链自虚空暴射而出,
『封印的收尾,交给我们母子!您只管——收手!!』

「玖辛奈?!」三代与大蛇丸同时失声。

死神的利刃悬停。玖辛奈的查克拉锁链与鸣人的简易封印阵
里应外合,狠狠绞住大蛇丸的双臂——

『漩涡流·双重封缚!!』

咔嚓。白蛇的双臂霎时枯萎成灰白色,惨叫着被属下拼死
拖出结界,遁入夜色。

死神的虚影,缓缓消散了。玖辛奈的身影化作点点金光,
没入鸣人心口前,朝三代眨了眨眼:

『老师,这孩子,以后拜托您多照看啦。』
""")
        else:
            ui.story("""
鸣人十指翻飞,简易封印阵在掌心展开,狠狠拍向
尸鬼封尽的术式边缘——以漩涡族的封印术强行「接管」收尾!

「小鬼,你疯了——」三代目眦欲裂。

「疯的是您!」鸣人嘶吼着,封印纹路顺着老人的手臂
逆流而上,截住了灵魂被抽离的路径,
「用命换他一双手,这买卖亏到家了!!」

金色纹路与死神之力剧烈拉锯——最终,「咔」的一声,
大蛇丸的双臂枯萎成灰,惨叫着被属下拖走;
而死神的虚影,在收走「双臂之魂」后,缓缓消散。
""")
        ui.pause()
        ui.story("""
紫焰散尽。天台上,三代火影瘫坐在地,大口喘着气——
活着。老人还活着。

「鸣人……」他望着眼前满身是伤的少年,又望望
自己完好的双手,老泪纵横,「你这孩子……
 你到底,还要让老头子我惊讶多少次……」

「至少到您看着我戴上火影帽为止!」

老人放声大笑,笑着笑着,哭了。
""")
        state.flags["hiruzen_saved"] = True
        state.add_backlash(2, "逆转了既定的死亡")
        state.gain_fate(2, "三代火影,存活!")
        state.add_suspicion(15)
        state.exposure += 10
    else:
        ui.story("""
鸣人的脚,在结界十步之外,钉住了。

结界之内,老人的目光越过大蛇丸,落在他身上——
那目光平静、温柔,带着不容置疑的托付。

『木叶的孩子们,拜托了。』

尸鬼封尽轰然完成。大蛇丸的双臂枯萎,惨叫遁走;
而三代火影猿飞日斩,含笑倒在了紫焰的中央。

雨,下了三天。

葬礼上,木叶白衣如雪。鸣人站在遗像前,
久久说不出话——直到伊鲁卡的手,轻轻按上他的肩。

「三代大人守护了村子,」老师的声音也在抖,
「现在,轮到活着的人了。」

(有些命运,重得连重生者也扛不动。
 但它的重量,会变成往前走的力气。)
""")
        state.flags["hiruzen_saved"] = False
        state.gain_fate(2, "继承了火之意志")
        state.belonging += 3
    ui.pause()


def _aftermath(state):
    ui.title("剧情: 崩溃之后")
    if state.flags["hiruzen_saved"]:
        ui.story("""
入侵被击退了。木叶伤痕累累,但屋顶的旗帜仍在。

病床上的三代火影签下的第一道手令,是全村重建;
第二道,是一封绝密召集令——

「老夫这把骨头,是借来的了。木叶需要新的血液。
 自来也,把纲手,给我找回来。」

而在村子的各个角落,人们口口相传着天台上那一幕:
金色锁链、赤红长发——

「漩涡的女人回来护村了。」老人们说着,红了眼眶。
""")
    else:
        ui.story("""
入侵被击退了。木叶伤痕累累,失去了它的火影。

灵堂的白布徐徐落下。长老会连夜议定:
必须尽快迎回五代目火影候选人——传说三忍之一,纲手。

「这差事,老子去。」自来也在灵前灌了一口酒,
 把杯子重重一放,「顺便,把某个胎记小鬼也捎上。
 老这么闷着,他会憋坏的。」
""")
    quest.complete_quest(state, "konoha_crush")
    state.flags["crush_done"] = True
    state.chapter = 5
    ui.pause()
    ui.story("""
═══════════════════════════

        木叶崩溃篇 · 完

═══════════════════════════

(休整之后:
 · 前往【木叶大门】,与自来也一同踏上寻找纲手之旅
 · 死亡森林已开放自由探索(高等级修炼地)
 · 桃源的忍术研究解锁了新的可能
 · 记得存档!)
""")
    ui.pause()
