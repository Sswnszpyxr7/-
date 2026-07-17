# -*- coding: utf-8 -*-
"""佐助离村篇(终章):音忍四人众、终结谷——以及整个故事的大结局。

设计文档 §11 第七章,四种结局:
  1 佐助离村 / 2 暂时离村但留下约定 / 3 未离村(暗部监护) / 4 加入改命计划
"""
from systems import battle, quest, ui


def night_event(state):
    if state.flags["sasuke_hospitalized"] and not state.flags["spar_done"]:
        _hospital_rooftop(state)
    sa = state.relations["sasuke"]
    if sa["curse"] == 0 and sa["trust"] >= 55 and sa["revenge"] <= 45:
        _best_path(state)
    else:
        _sound_four_night(state)
    _grand_finale(state)


# ── 前置:医院天台 (鼬事件走了原剧情时) ──────────────

def _hospital_rooftop(state):
    ui.title("剧情: 天台的千鸟")
    ui.story("""
纲手的医疗术唤醒了月读昏迷中的佐助。
可醒来的佐助,眼神比昏迷时更暗。

医院天台。晾晒的床单在风里猎猎作响。

「鸣人。」佐助拦住来探望的他,声音哑得吓人,
「和我打一场。现在。」

那双写轮眼里烧着的东西,鸣人前世见过——
嫉妒、焦躁、被差距碾碎的自尊,和月读留下的无底黑暗。

(这一战避不开。但它不必以千鸟对螺旋丸、
 两败俱伤地收场。)
""")
    result = battle.battle(state, "sasuke_spar",
                           special_rules={"no_escape": True},
                           intro="佐助率先冲来,写轮眼的勾玉疯狂旋转!")
    if result == "win":
        ui.story("""
最后一记锁喉,鸣人把佐助按在水塔上——却在千钧一发处
收了力,只有风压掀飞了两人的护额。

「为什么收手!」佐助嘶吼。

「因为我们是同伴。」鸣人松开手,捡起两枚护额,
 把属于佐助的那枚拍回他胸口,
「记住这场败绩,佐助。然后记住——让你变强的路
 不止一条。最快的那条,通向的是地狱。」
""")
        state.add_rel("sasuke", "trust", 5)
        state.add_rel("sasuke", "revenge", 3)
    else:
        ui.story("""
千鸟与螺旋丸在半空相撞的前一瞬,两条白影分开了两人——
卡卡西一手一个,把两人钉在原地。

「够了。」他的独眼罕见地没有笑意。

佐助甩袖而去。天台上只剩风声,
和水塔上那个深不见底的千鸟凿痕。
""")
        state.add_rel("sasuke", "revenge", 5)
        state.add_rel("sasuke", "isolation", 5)
    state.flags["spar_done"] = True
    ui.pause()


# ── 最优路线:黑暗未曾扎根 ──────────────────────

def _best_path(state):
    ui.title("剧情: 月夜·屋顶的来客")
    ui.story("""
深夜。鸣人被窗外的气息弄醒——

屋顶上,佐助抱膝坐着,望着月亮。没有咒印的脖颈
在月光下干干净净。

「音隐的人来找过我。」他头也不回,
「四个,自称『音忍四人众』。说大蛇丸能给我力量,
 足以杀死鼬的力量。」

鸣人的心提到了嗓子眼:「……然后呢?」

「我把他们打发走了。」佐助转过头,写轮眼在夜色里
 亮得惊人,「力量的事,以后再说。今晚我来,
 是要一个答案——

 漩涡鸣人,你到底是谁?

 波之国、死亡森林、每一次,你都『恰好』知道
 接下来会发生什么。别拿『直觉』糊弄我。」
""")
    idx = ui.choose("面对佐助的逼问,你——", [
        "全盘托出:重生、前世、终结谷、以及鼬的真相 (需要足够的信任)",
        "半吐真言:「鼬的背后另有隐情,我在查。给我时间,给你真相。」",
    ])
    sa = state.relations["sasuke"]
    if idx == 0 and sa["trust"] >= 60:
        ui.story("""
鸣人在他身边坐下,深吸一口气——把一切都说了。

重生。前世。终结谷两败俱伤的诀别。大蛇丸的容器。
鼬的病。真相大白那天,佐助跪在尸体前的恸哭。
第四次忍界大战,并肩而战的最后时刻。

月亮走过半个天空。佐助一动不动地听完,
久久,久久没有说话。

「……荒谬。」他终于开口,声音干涩,
「可是,全都对得上。每一件,都对得上。」

他忽然抓住鸣人的衣领,眼眶通红:

「鼬他——我哥他,到底为什么?!」

「为了村子,为了你。」鸣人任他抓着,一字一句,
「所以这一世,我们不复仇——我们去『复原』。
 把真相挖出来,把设局的人挖出来,
 把你哥,从那条不归路上抢回来。」

「——加入我,佐助。这是比杀死鼬
 难一万倍的复仇。」
""")
        ui.pause()
        ui.story("""
佐助松开手,仰面躺倒在屋顶上,像卸掉了
背了八年的千斤重担。

「呵。」他望着月亮,极轻地笑了一声,
「吊车尾拯救世界……亏你说得出口。」

「信不信?」

「不信。」佐助闭上眼,「但是,赌了。」

他伸出拳头。鸣人笑着,用拳头撞了上去。

——黑暗降临之前,黎明先到了。
""")
        state.flags["sasuke_ending"] = 4
        state.gain_fate(3, "以真相为誓的同盟")
        state.add_rel("sasuke", "revenge", -20)
        state.add_rel("sasuke", "isolation", -20)
        state.add_rel("sasuke", "trust", 15)
        state.add_rel("sasuke", "team_bond", 15)
    else:
        ui.story("""
「鼬的事,背后另有隐情。」鸣人斟酌着字句,
「我在查。查到的那天,真相一个字不少,全给你。
 但在那之前——别把自己交给大蛇丸那种人。
 他要的不是给你力量,是你这具身体。」

佐助盯着他看了很久很久。

「……一年。」他站起身,月光把影子拉得很长,
「我给你一年。查不到,我就用我自己的方式。」

「一言为定。」

黑影跃下屋顶,消失在族地的方向。
——他留下了。带着悬而未决的约定,但留下了。
""")
        state.flags["sasuke_ending"] = 4 if sa["trust"] >= 70 else 3
        state.gain_fate(2, "拦在深渊前的约定")
        state.add_rel("sasuke", "revenge", -10)
        state.add_rel("sasuke", "trust", 8)
    quest.complete_quest(state, "valley_of_the_end")
    state.flags["sasuke_arc_done"] = True
    ui.pause()


# ── 原轨迹:夜逃与终结谷 ─────────────────────────

def _sound_four_night(state):
    ui.title("剧情: 离村之夜")
    ui.story("""
那个夜晚,还是来了。

音忍四人众的挑衅、咒印的诱惑、月读留下的黑洞、
以及「差距」带来的焦渴——种种黑暗在佐助心里
发酵成同一个决定。

深夜的街道,佐助背着行囊走向村门。
""")
    sk = state.relations["sakura"]
    if sk["confidence"] >= 45:
        ui.story("""
路灯下,小樱拦住了他。

但这一世的小樱,没有只是哭着说「带我走」。

「你要走,我拦不住。」她的声音在抖,眼泪在掉,
 拳头却攥得死紧,「所以我现在就去叫醒全村——
 鸣人、卡卡西老师、纲手师父!要恨就恨吧,佐助君,
 把你从黑暗里抢回来,是第七班的任务!!」

她转身狂奔。佐助来不及点她的昏穴,只能咬牙
加速冲向村门——

追击,比前世提前了整整四个时辰。
""")
        state.add_rel("sakura", "responsibility", 10)
    else:
        ui.story("""
路灯下,小樱哭着说尽了一切,换来一声「谢谢」
和颈后轻轻的一击。

清晨,她伏在长椅上被巡逻队发现时,
佐助已出村四个时辰。
""")
    ui.pause()
    ui.story("""
追击小队连夜集结:鹿丸、丁次、宁次、牙、李……

一路死战。音忍四人众与君麻吕,把木叶的少年们
一个个拦在血泊里——
""")
    if state.flags["gaara_redeemed"]:
        ui.story("""
——但在最危急的时刻,三道沙之旋风自侧翼杀到!

「木叶的诸位,」我爱罗的沙瀑吞没了君麻吕的骨刺,
 声音平静而坚定,「砂隐,前来还债。」

有沙之三姐弟压阵,追击小队无一人重伤。
所有的路障都被扫开——终结谷,只剩最后两个人的战场。
""")
        state.gain_fate(1, "沙漠的报恩")
    else:
        ui.story("""
少年们拼到最后一滴血,才勉强把路障逐一撕开。
(伤员已被医疗班接走——幸好,这一世的医疗班,
 有纲手坐镇。)

终结谷,只剩最后两个人的战场。
""")
    ui.pause()
    _valley_battle(state)


def _valley_battle(state):
    sa = state.relations["sasuke"]
    ui.title("剧情: 终结谷")
    ui.story("""
瀑布轰鸣。千仞峡谷两侧,初代火影与宇智波斑的石像
沉默对峙——如同此刻站在两尊石像头顶的两个少年。

「回去吧,鸣人。」佐助的声音混在水声里,
「我要去的地方,光照不进去。」

「那我就把光带过去。」鸣人扎稳马步,
「打赢我再走——第七班的规矩,吵架用拳头!」
""")
    if state.relations["sakura"]["medical"] >= 25:
        p = state.player
        p["hp"] = p["max_hp"]
        p["chakra"] = p["max_chakra"]
        state.add_item("军粮丸", 2)
        ui.slow_print("※ 出发前,小樱塞给你的应急药包发挥了作用——状态全恢复,军粮丸+2!")

    curse = sa["curse"]
    mods = {"hp": curse * 2, "max_hp": curse * 2, "attack": curse // 6}
    if curse >= 60:
        intro = "咒印二态!青黑色的皮肤上,手裂状的翼展开——「这就是,力量!」"
    elif curse > 0:
        intro = "咒印的黑纹爬上半边脸颊。佐助的杀气,比天台那次沉重十倍!"
    else:
        intro = "没有咒印,没有邪气——只有一双燃烧的写轮眼,和不肯回头的决心。"

    def extra_actions(log):
        return ["喊话 (用羁绊撼动他的决心)"]

    def action_handler(label, st, player, enemy, log):
        if not label.startswith("喊话"):
            return False
        n = log.get("waver", 0)
        lines = [
            "「一乐的拉面!说好下次我请客的,你还没吃!」",
            "「铃铛测试,冰镜,死亡森林——哪一次,我们不是背靠背?!」",
            "「你说过要斩断羁绊——可你下手的每一击,都避开了我的要害!!」",
        ]
        ui.slow_print(f"→ {lines[min(n, len(lines) - 1)]}")
        if st.relations["sasuke"]["trust"] >= 40:
            log["waver"] = n + 1
            enemy["attack"] = max(10, enemy["attack"] - 3)
            ui.slow_print("  佐助的攻击迟滞了一瞬——他在动摇!(敌方攻击下降)")
        else:
            ui.slow_print("  「闭嘴!!」回应你的只有更凶狠的千鸟。")
            dmg = max(1, int(enemy["attack"] * 0.4))
            player["hp"] -= dmg
            ui.slow_print(f"  受到 {dmg} 点伤害!")
        return True

    result = battle.battle(
        state, "sasuke_valley",
        special_rules={"no_escape": True, "enemy_mods": mods,
                       "extra_actions": extra_actions, "action_handler": action_handler},
        intro=intro)

    if result == "win":
        if sa["trust"] >= 60 and curse <= 45:
            _ending_alliance(state)
        else:
            _ending_guarded(state)
    else:
        if sa["trust"] >= 50:
            _ending_promise(state)
        else:
            _ending_canon(state)
    quest.complete_quest(state, "valley_of_the_end")
    state.flags["sasuke_arc_done"] = True
    ui.pause()


def _ending_alliance(state):
    """结局4: 加入改命计划。"""
    ui.story("""
两人仰面漂在谷底的水潭里,谁也爬不起来。

「……输了啊,我。」佐助望着天,忽然笑了,
 笑着笑着,眼角滑下水痕,分不清是瀑布还是别的,
「喂,鸣人。你每次都『恰好』知道未来……
 现在,把一切都告诉我。作为战败者的权利。」

鸣人也望着天,喘了很久,说:「好。」

于是,在终结谷的水声里,他把两世的故事,
从头讲到了尾——包括鼬的真相。

讲完时,朝阳正从峡谷的裂口照进来。

「……复仇,不急了。」佐助闭上眼,声音哑得厉害,
 却前所未有地平静,「先把真相连根挖出来。
 然后——把我哥抢回来。

 这份『改命计划』,算我一个。」

两只伤痕累累的拳头,在水面上,轻轻相碰。
""")
    state.flags["sasuke_ending"] = 4
    state.gain_fate(3, "终结谷的黎明")
    state.add_rel("sasuke", "revenge", -25)
    state.add_rel("sasuke", "isolation", -20)
    state.add_rel("sasuke", "trust", 15)


def _ending_guarded(state):
    """结局3: 带回木叶,暗部监护。"""
    ui.story("""
鸣人把昏迷的佐助背回了木叶。

裁定很快下来:私通叛忍未遂,念其未出国境、
且系咒印与幻术诱导——暗部监护观察一年,
禁足村内,查克拉限制器随身。
""")
    if state.flags["hiruzen_saved"]:
        ui.slow_print("(三代火影亲自压下了长老会的重罚提案:「孩子的路,要留有回头的余地。」)")
    ui.story("""
族地的门前,佐助背对着来探望的鸣人,半晌,
扔出一句:

「……别得意。是我大意了而已。」

「行行行,是你大意。」鸣人把一盒一乐外卖
 挂在他门把上,「下次大意前,先吃饱。」

门内很久没有动静。然后,外卖盒被一只手
 默默收了进去。

——他还在村子里。灯还亮着。这就够了。
""")
    state.flags["sasuke_ending"] = 3
    state.gain_fate(2, "把他留在了光里")
    state.add_rel("sasuke", "isolation", -10)
    state.add_rel("sasuke", "trust", 8)


def _ending_promise(state):
    """结局2: 暂时离村,留下约定。"""
    ui.story("""
最后一击,鸣人仰面倒进水潭。

佐助立在水面上,俯视着他,千鸟的余光在指尖明灭——
终究,缓缓熄灭了。

「为什么不补刀?」鸣人咳着水,咧嘴,「心软了?」

「闭嘴。」佐助转过身,背影融在瀑布的水雾里,
「三年。三年后,我会回来——验证你说过的每一句话。
 到那天,要是你敢变弱……」

「你放心!」鸣人朝那个背影嘶吼,声音劈了叉,
「三年后,把你拖回来的绳子,我现在就开始搓!!」

背影顿了顿。

风里,似乎飘回来极轻的一个字:

「……嗯。」
""")
    state.flags["sasuke_ending"] = 2
    state.gain_fate(2, "没有断掉的命线")
    state.add_rel("sasuke", "trust", 5)


def _ending_canon(state):
    """结局1: 原剧情离村。"""
    ui.story("""
雨,落了下来。

鸣人躺在谷底,望着那个越来越远的背影,
连抬手的力气都没有。

佐助在他身边驻足了一瞬。护额,轻轻落在他的手边——
中间一道深深的划痕,横贯木叶的标记。

脚步声,消失在雨里。

——和前世,一模一样的雨。

但攥紧护额的鸣人,眼里没有前世的茫然。

「跑吧。」他任雨水冲刷着脸,一字一字地说,
「三年也好,五年也罢——我两辈子都把你追回来了,
 不差这一次。等着,佐助。」
""")
    state.flags["sasuke_ending"] = 1
    state.gain_fate(2, "雨中立下的誓言")
    state.add_backlash(1, "命运暂时挣脱了掌心")


# ── 大结局 ─────────────────────────────────────

def _grand_finale(state):
    ending = state.flags["sasuke_ending"]
    if state.flags["itachi_knows"] and ending >= 3:
        ui.title("剧情: 乌鸦的回信")
        ui.story("""
数日后的清晨,鸣人的窗台上,落着一只乌鸦。

它脚上绑着一枚极小的纸卷,没有署名,只有一行
清瘦的字:

『弟弟的事,谢谢。
 「真相」的账,来日,由我亲自了结。
 ——在那之前,拜托了。』

乌鸦振翅而去,消失在黎明的天光里。

(在遥远的某处,那个背负一切的男人,
 第一次在计划里写下了「活下去」的选项。)
""")
        state.gain_fate(1, "深渊里的那盏灯,亮着")
        ui.pause()

    ui.title("终章: 桃源夜话")
    ui.story("""
入夜,桃源。

契约之树下摆开了长桌,玖辛奈「监工」,琳掌勺,
一桌子热气腾腾——红枫林飘着焰火,是妈妈的恶作剧;
药草田的萤火虫提着灯笼,绕着桌子飞。
""")
    if state.contracts["tsunade"]["unlocked"]:
        ui.slow_print("纲手拎着酒壶不请自来,被玖辛奈按头认了「前辈」,两人拼酒拼得惊天动地。")
    ui.story("""
「来,鸣人,」玖辛奈举起茶杯,眼睛亮晶晶的,
「说说看——这一世,你都改写了什么?」

鸣人挠着头,掰起手指:
""")
    f = state.flags
    lines = []
    if f["haku_alive"] and f["zabuza_alive"]:
        lines.append("「白和再不斩,活着。就住在村东头,白还在医疗班帮忙!」")
    elif f["haku_alive"]:
        lines.append("「白活下来了。他说要替再不斩,看看往后的世界。」")
    else:
        lines.append("「波之国……我记住了教训。桥头的两座坟,我每年都会去。」")
    if f["curse_avoided"]:
        lines.append("「佐助脖子上,干干净净——咒印,被我掀了桌!」")
    if f["hiruzen_saved"]:
        lines.append("「三代爷爷还活着!还答应看我戴上火影帽!」")
    else:
        lines.append("「三代爷爷……他把火之意志,交给我们了。」")
    if f["gaara_redeemed"]:
        lines.append("「我爱罗有朋友了。第一个,是我。」")
    lines.append({
        1: "「佐助他……暂时走了。但我搓绳子的手,一天都没停过。」",
        2: "「佐助留了约定。三年后,他会回来——回来验证我没吹牛。」",
        3: "「佐助还在村里。虽然嘴硬得要命,但外卖他都收了!」",
        4: "「佐助入伙了!改命计划,现在是两个人的了!」",
    }[ending])
    if state.contracts["rin"]["unlocked"]:
        lines.append("「还有琳姐回家了,妈妈也不再是一个人——」")
    for ln in lines:
        ui.slow_print(ln)
    ui.pause()
    ui.story("""
说到最后,鸣人的声音低了下去。

「……还有很多没做到的。晓还在动,大蛇丸还在,
 三年后,佩恩会来,战争会来——」

『鸣人。』

玖辛奈打断他。她伸出手,和琳的手、
以及所有契约者的手叠在一起,按在他的手背上。

『看看这张桌子。』她轻声说,『上一世的这个时候,
 你在哪里,身边有谁?』

鸣人怔住了。

上一世的这个夜晚——他一个人,在医院天花板下,
数着输给佐助的招式。

而现在,桃源的星空下,饭菜冒着热气,
每一条命线,都暖暖地亮着。

『改变命运啊,』妈妈笑起来,眼角有泪光,
『从来不是一场决战。是一顿一顿的饭,一次一次的
 「我在」。你已经做得,比谁都好了。』
""")
    ui.pause()
    state.flags["main_complete"] = True
    state.chapter = 7
    state.belonging += 10
    state.gain_fate(5, "第一部完结·命运的报偿")
    ui.story("""
═══════════════════════════════════

     《九命一系:鸣人重生录》

        第 一 部 · 全 篇 完

  「这一世,我不想再等到失去之后才明白珍惜。
   我要保护他们。
   也要让他们知道,我从来不是一个人。」

═══════════════════════════════════

        —— 下部预告 ——

 三年之后,赤云将至。带着轮回之瞳的「神」
 会从天而降;被扭曲的面具男,藏在月亮背后。

 但那时的漩涡鸣人,身后是九条命线、
 一座桃源、和一整个不再让他孤单的世界。

 (命运回廊里,新的光门已经亮起……)

═══════════════════════════════════

(主线全部完结!自由模式开启:
 · 继续修炼、提升契约至【九命同归】
 · 完成剩余的忍术研究与桃源建设
 · 死亡森林磨砺实力,备战「三年后」
 · 感谢游玩!)
""")
    ui.pause()
