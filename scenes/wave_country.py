# -*- coding: utf-8 -*-
"""波之国篇:护送达兹纳、再不斩、白——以及第一次真正的命运改写。

设计文档 §11 第三章:
  结局1 原剧情(白与再不斩死) / 结局2 半改写(白活) / 结局3 完美改写(双双存活)
"""
from scenes import rin_arc
from systems import battle, quest, ui


def start(state):
    if state.player["level"] < 4:
        ui.story("""
「C级护送任务……唔。」三代火影看了看鸣人,又看了看委托单。

(推荐等级 Lv.4。当前实力接下这个任务会相当勉强——
 可以先去木叶森林或训练场磨炼一下再来。)
""")
        if ui.choose("仍然要接取任务吗?", ["再准备准备 (推荐)", "现在就出发!"]) == 0:
            return
    _mission_briefing(state)
    _demon_brothers_event(state)
    _zabuza_first_battle(state)
    _training_interlude(state)
    _haku_meeting(state)
    _bridge_battle(state)
    _fate_crossroads(state)
    _epilogue(state)


def _mission_briefing(state):
    ui.title("剧情: C级任务·护送")
    ui.story("""
「第七班,你们的第一个村外任务——C级,护送。」

三代火影话音刚落,办公室的门就被推开了。
一个抱着酒瓶的老头晃了进来,酒气熏天。

「啥啊,就这几个小鬼?尤其那个最矮的,一脸蠢相,
 真的是忍者吗?」

「你说谁蠢——!」鸣人条件反射地跳脚,吼到一半却顿住了。

达兹纳。波之国的筑桥师。

这个嘴硬心软的老头背后,是加藤的垄断、白与再不斩的雪、
还有那座后来以自己名字命名的大桥。

——来了。第一场真正的命运之战。
""")
    idx = ui.choose("出发前,你——", [
        "私下提醒卡卡西:「我总觉得这单委托没那么简单,说不定有埋伏。」",
        "什么都不说,暗中戒备 (不引起怀疑)",
    ])
    if idx == 0:
        ui.story("""
卡卡西翻书的手停了停。

「哦?理由呢?」

「直觉!超强的直觉!」鸣人拍着胸口,
「而且那大叔的手一直在抖,不像只是喝多了——更像是害怕。」

独眼深深看了他两秒。「……记下了。」

(卡卡西提高了警惕。但他看你的眼神,也多了些别的东西。)
""")
        state.exposure += 3
        state.add_suspicion(5)
        state.runtime_flags["wave_prepared"] = True
    else:
        ui.story("""
鸣人揣着手跟在队伍最后,像前世一样和佐助拌着嘴。

只有握紧的指节暴露着:他在等。等那滩不该出现的水洼。
""")
        state.runtime_flags["wave_prepared"] = False
    ui.pause()


def _demon_brothers_event(state):
    ui.title("剧情: 水洼杀机")
    ui.story("""
出村半日,晴空万里的土路中央,躺着一滩水洼。

好多天没下雨了。
""")
    if state.runtime_flags.get("wave_prepared"):
        idx = ui.choose("鬼兄弟即将暴起。你——", [
            "抢先出手!苦无直钉水洼 (先发制人)",
            "按兵不动,配合卡卡西的「假死」诱敌",
        ])
    else:
        idx = ui.choose("鬼兄弟即将暴起。你——", [
            "抢先出手!苦无直钉水洼 (先发制人)",
            "按兵不动,配合卡卡西的「假死」诱敌",
        ])
    if idx == 0:
        ui.story("""
「哈啊——!」

苦无破空,直直钉进水洼中心!两道黑影狼狈窜出,
铁爪锁链哗啦作响——伏击,变成了遭遇战!

「臭小鬼!!」
""")
        result = battle.battle(state, "demon_brothers",
                               special_rules={"no_escape": True, "environment": "mist"},
                               intro="鬼兄弟的锁链在半空张开,毒爪泛着幽光!")
        if result == "lose":
            ui.story("""
锁链缠身的瞬间——银光一闪,卡卡西已经把两人反绑在树上。

「好了,交给我吧。」他把鸣人从地上拎起来,
「先出手是好判断,就是本事还差点儿。」
""")
        else:
            state.add_trust(3)
            state.gain_fate(1, "先发制人,无人受伤")
    else:
        ui.story("""
锁链绞碎了「卡卡西」的身体——木屑纷飞。替身术。

两道黑影转向达兹纳,却见鸣人早已横在老人身前,
佐助的手里剑同时钉住了锁链,小樱护住了侧翼!

下一瞬,卡卡西从树上悠然现身,双手各拎起一个鬼兄弟。

「配合不错嘛,你们三个。」

(前世这里,鸣人吓得动弹不得,还中了毒爪。
 这一世——第七班无人受伤。)
""")
        state.add_trust(5)
        state.gain_fate(1, "改写了自己的怯懦")
        state.add_rel("sasuke", "team_bond", 5)
    ui.pause()
    ui.story("""
审讯过后,达兹纳终于说了实话:黑心财阀加藤买凶杀他,
任务实际是 B 级往上。

「继续,还是回村?」卡卡西问三个下忍。

「继续!」×3

三道声音,整整齐齐。达兹纳偷偷抹了把眼睛。
""")
    ui.pause()


def _zabuza_first_battle(state):
    ui.title("剧情: 雾隐之鬼")
    ui.story("""
波之国的湖面,雾气毫无征兆地浓了起来。

「都趴下!!」

卡卡西一声暴喝,巨大的斩首刀贴着头皮呼啸而过,
深深斩进树干!

刀背上,立着一个绷带蒙面的男人。

「难怪鬼兄弟搞不定——写轮眼的卡卡西。」

桃地再不斩。雾隐之鬼。
""")
    ui.pause()
    ui.story("""
战斗爆发。水面之上,卡卡西与再不斩杀得难分难解——
可雾太浓了,一个恍神,卡卡西竟被困进了水牢!

「保护达兹纳,快跑!你们不是他的对手!」

前世,鸣人和佐助用「风魔手里剑连携」赌命破了水牢。
这一世,鸣人的嘴角微微一扬。

「佐助!」他把背包一甩,「老规矩——道具课代表,配合我!」

「谁跟你有『老规矩』……」佐助接住背包,却已心领神会。
""")
    def win_condition(st, player, enemy, turn, log):
        if enemy["hp"] <= enemy["max_hp"] * 0.55:
            return "interrupted"
        if turn >= 7:
            return "interrupted"
        return None

    allies = [
        {"name": "宇智波佐助", "power": 30, "element": "fire", "move": "掷出风魔手里剑并接以豪火球"},
        {"name": "春野樱", "power": 10, "element": "taijutsu", "move": "投掷苦无牵制",
         "can_heal": True, "act_rate": 0.5},
    ]
    result = battle.battle(
        state, "zabuza_first",
        special_rules={"win_condition": win_condition, "no_escape": True,
                       "allies": allies, "max_turns": 8, "timeout_result": "interrupted",
                       "objective_text": "将再不斩逼退，解救水牢中的卡卡西",
                       "environment": "mist"},
        intro="「水分身之术。」雾中,再不斩的杀意如有实质地压了过来!")

    if result in ("interrupted", "win"):
        ui.story("""
影分身群从三个方向同时扑出,风魔手里剑在水雾中变向——
再不斩被迫撤手,水牢应声而碎!

重获自由的卡卡西眼中写轮眼流转:「做得好!剩下的交给我。」

水龙对撞,巨浪滔天。就在卡卡西即将终结战斗的刹那——

咻!咻!

两枚千本精准地刺入再不斩的脖颈。他直挺挺栽倒。

雾的另一头,一个戴着雾隐猎忍面具的少年悄然现身,
朝这边微微欠身:

「感谢诸位。我追捕此人已经很久了。」
""")
        if result == "interrupted":
            state.gain_exp(160)
        state.add_trust(5)
        state.add_rel("sasuke", "trust", 5)
    else:
        ui.story("""
鸣人被水浪狠狠拍飞的瞬间,卡卡西怒喝一声,
硬生生以蛮力破开水牢,挡在众人身前。

两大上忍再度交手,难分胜负——直到两枚千本
突兀地刺入再不斩脖颈,「猎忍」少年现身收走了尸体。
""")
        state.player["hp"] = max(state.player["hp"], state.player["max_hp"] // 3)

    idx = ui.choose("「猎忍」抱起再不斩即将离开。你——", [
        "沉默。等他走后再提醒卡卡西「假死」的可能 (稳妥)",
        "当场戳穿:「等等!千本刺脖子,那是假死!」(果断但显眼)",
    ])
    if idx == 0:
        ui.story("""
少年消失在雾中后,鸣人才开口:

「卡卡西老师……猎忍不是应该当场处理尸体吗?
 而且千本那种东西,刺准了穴位,是可以制造假死的吧?」

卡卡西的独眼眯了起来。

「……我也在想同一件事。」他望向雾深处,
「一周。再不斩一周后就会回来。我们抓紧特训。」
""")
        state.add_trust(3)
    else:
        ui.story("""
「哦?」面具少年的脚步停了半拍。

雾陡然一浓——再回神时,人与「尸体」都消失了。

「……鸣人,你怎么知道假死?」卡卡西的声音很平静,
平静得让人后颈发凉。

「书、书上看的!医疗手册!」

(打草惊蛇了。但备战的时间,也确实争取到了。)
""")
        state.add_suspicion(10)
        state.exposure += 5
    ui.pause()


def _training_interlude(state):
    ui.title("剧情: 爬树与备战")
    ui.story("""
达兹纳家暂住的一周,卡卡西拄着拐杖,教了三人「爬树」——
查克拉集中脚底,只用双脚走上树干。

前世的鸣人为这一步摔了几十次。
这一世的他,得装着摔上几次,再「恍然大悟」。
""")
    idx = ui.choose("这一周的特训重点放在——", [
        "查克拉控制:老老实实爬树 (查克拉控制+2)",
        "和佐助较劲:比谁先登顶 (佐助羁绊提升)",
        "拉上小樱加练:她的控制力是天才级的 (小樱成长)",
    ])
    if idx == 0:
        state.player["chakra_control"] += 2
        state.player["max_chakra"] += 10
        ui.story("""
一周之后,鸣人「终于」稳稳站上了树冠。
指尖的查克拉,比重生以来任何时候都要听话。

※ 查克拉控制 +2,查克拉上限 +10。
""")
    elif idx == 1:
        state.player["chakra_control"] += 1
        state.add_rel("sasuke", "trust", 6)
        state.add_rel("sasuke", "team_bond", 8)
        state.add_rel("sasuke", "isolation", -5)
        ui.story("""
「喂,吊车尾,你到哪个记号了?」
「比你高一拳!」
「做梦,那是我的记号!」

两个少年在月光下的树干上你追我赶,摔了就爬,爬了再摔。
最后并排躺在树冠间喘气时,佐助忽然说:

「……你这家伙,到底还藏了多少东西。」

「多着呢。」鸣人望着星星,「以后慢慢给你看。」
""")
    else:
        state.add_rel("sakura", "confidence", 8)
        state.add_rel("sakura", "medical", 5)
        state.add_rel("sakura", "trust", 6)
        ui.story("""
「小樱,你第一次就登顶了,查克拉一点都没浪费——
 教教我们呗,课代表!」

被两个男生围着请教的小樱,先是慌,再是窘,
最后腰杆一点点挺直了。

「真、真拿你们没办法!看好了,要领是——」

(自信的种子,在异国的月光下抽了芽。)
""")
    ui.pause()


def _haku_meeting(state):
    ui.title("剧情: 林中的少年")
    ui.story("""
清晨的树林,鸣人练到脱力,仰面睡在草地上。

再睁眼时,一张清秀的脸正低头看着他——粉色和服的「少女」
提着药篮,在他身边采着草药。

「再睡下去会感冒的哦。」

白。

前世,就是在这里。同样的晨光,同样的药香,
同样的这句——
""")
    ui.pause()
    ui.story("""
「你有想要守护的、重要的人吗?」

白微笑着问出了那个问题。

「人真正变强,是在拥有想要守护的东西的时候。」
""")
    idx = ui.choose("面对白,你——", [
        "如实回答:「有。很多。这次一个都不会失去。」",
        "反问:「你呢?你想守护的人——值得你去死吗?」",
        "把心里话全说出来:「白,雾散之后,和再不斩一起来木叶吧。」",
    ])
    bond = state.flags["haku_bond"]
    if idx == 0:
        bond = max(bond, 1)
        ui.story("""
白眨了眨眼,笑意更深了些。

「是么。那你一定会变得很强。」

他提起药篮起身,走出几步,又回头:

「对了——我是男孩子哦。」

(熟悉的对话,熟悉的告别。但这一次,鸣人在他背影里
 看到的不是「敌人」,而是一个同样想守护什么的孩子。)
""")
    elif idx == 1:
        bond = max(bond, 2)
        ui.story("""
白采药的手,几不可察地停了。

「……值得。」他垂着眼答,「我是他的武器。武器的价值,
 就是为主人而碎。」

「胡说。」鸣人坐起来,直直地盯着他,
「武器不会挑药草,不会怕别人感冒,更不会笑。
 白,你不是武器。你只是……太久没人把你当人了。」

晨光里,少年的睫毛轻轻颤了很久。

「……你怎么知道,我的名字?」

「猜的。」鸣人咧嘴一笑,心跳如鼓。

白凝视他半晌,轻轻笑了:「真是奇怪的人。」
""")
        state.exposure += 3
    else:
        bond = max(bond, 3)
        ui.story("""
白的瞳孔猛地收缩。杀意瞬间凝聚——又在触及鸣人
毫无防备的笑脸时,一寸寸散去。

「……你知道我是谁。」

「知道。雪一样的血继限界,千本,还有把你从雪地里
 捡回来的那个人。」鸣人盘腿坐正,认真得像在起誓,
「我还知道,加藤那种人渣,根本不打算付钱——他会背叛。

 所以,别为那种局赔上你和再不斩先生的命。
 等桥修完,来木叶。担保人我来找,再不斩先生的刀,
 木叶用得上;你的温柔,更用得上。」

风穿过树林,吹了很久。

「……我会,转告他。」白抱起药篮,声音很轻,
「虽然他多半会笑着骂一句『天真』。」

「天真才好。」鸣人冲他背影喊,「忍者的世界,
 就是缺天真!」
""")
        state.gain_fate(1, "向命运递出的邀请函")
        state.exposure += 5
    state.flags["haku_bond"] = bond
    ui.slow_print(f"※ 与白的羁绊: {bond}/3")
    ui.pause()


def _bridge_battle(state):
    # 大桥决战前有一周休整，避免此前探索伤势直接带入连续阶段战。
    state.player["hp"] = max(state.player["hp"], int(state.player["max_hp"] * 0.75))
    state.player["chakra"] = max(
        state.player["chakra"], int(state.player["max_chakra"] * 0.75)
    )
    ui.title("剧情: 大桥决战")
    ui.story("""
一周之期,如约而至。

清晨的大桥浓雾弥漫,达兹纳的工人横七竖八地倒着(昏迷)。
雾中,再不斩的杀意与卡卡西的写轮眼再次对上。

而鸣人与佐助面前,冰晶铺天盖地升起——
魔镜冰晶,千本如雨的绝对领域。

「上次没能分出胜负。」面具后传来白的声音,
带着一丝不易察觉的歉意,「这次,请务必全力以赴。」
""")
    def win_condition(st, player, enemy, turn, log):
        # 第3回合: 冰镜齐射事件——前世佐助濒死的节点
        if turn == 3 and not log.get("shield_event"):
            log["shield_event"] = True
            ui.story("""
!!!

所有冰镜同时亮起——千本从每个角度倾泻而下,
而佐助,正下意识地朝鸣人这边扑来,要替他挡!

前世的画面轰然重叠:满身千本的佐助,垂下的手——
""")
            c = ui.choose("电光石火之间,你——", [
                "反手把佐助护在身下!(自己承受,佐助无伤)",
                "拼速度!拽着佐助一起闪出弹幕!(需要足够的速度)",
            ])
            if c == 0:
                dmg = int(player["max_hp"] * 0.3)
                player["hp"] = max(1, player["hp"] - dmg)
                ui.story(f"""
千本扎进后背的剧痛里,鸣人把佐助死死压在身下。

「你疯了吗吊车尾——!」

「你才疯了,」鸣人咧开血迹斑斑的笑,「想替我挡?
 那种事,这辈子都不许再做。」

佐助瞳孔剧震——那双黑眼睛深处,两枚勾玉悄然转生。

(受到 {dmg} 点伤害。佐助以「活着的眼睛」开启了写轮眼。)
""")
                state.add_rel("sasuke", "trust", 15)
                state.add_rel("sasuke", "revenge", -8)
                state.add_rel("sasuke", "isolation", -10)
                st.gain_fate(2, "改写了冰镜中的悲剧")
            else:
                if player["speed"] >= 26:
                    ui.story("""
「抓稳了!」

鸣人拽住佐助的领口,以极限速度在千本雨的缝隙间
连闪三步——堪堪擦着弹幕滚出了冰镜领域边缘!

「你、你这速度……」佐助又惊又怒又后怕。

「特训的成果!」鸣人抹掉脸颊的血线,咧嘴一笑。

(无人重伤。佐助在生死一瞬中开启了写轮眼。)
""")
                    state.add_rel("sasuke", "trust", 10)
                    state.add_rel("sasuke", "team_bond", 5)
                    st.gain_fate(2, "改写了冰镜中的悲剧")
                else:
                    dmg = int(player["max_hp"] * 0.2)
                    player["hp"] = max(1, player["hp"] - dmg)
                    ui.story(f"""
速度还是差了半步!

千本擦着两人的身体钉进桥面,佐助的肩头中了三针,
闷哼着单膝跪地——但要害,全都避开了。

「可恶……」佐助撑刀而起,双眼赤红——写轮眼,开了。

(受到 {dmg} 点伤害,佐助轻伤。比前世,好了太多。)
""")
                    state.add_rel("sasuke", "trust", 6)
                    st.gain_fate(1, "至少,没有人倒下")
            return None
        return None

    allies = [{"name": "宇智波佐助(写轮眼)", "power": 34, "element": "fire",
               "move": "以初开的写轮眼捕捉冰镜轨迹,豪火球轰出"}]
    result = battle.multi_stage_boss_battle(state, [
        {
            "name": "魔镜冰晶",
            "enemy_id": "haku_bridge",
            "intro": "冰镜之间,白的身影快得只剩残像。千本,来了!",
            "special_rules": {
                "win_condition": win_condition, "no_escape": True, "allies": allies,
                "objective_text": "撑过冰镜攻势，并击碎冰镜阵眼",
                "environment": "mist", "enemy_mods": {"hp": -140},
            },
        },
        {
            "name": "冰镜与鬼人水分身",
            "enemy_ids": [
                {"enemy_id": "haku_bridge", "enemy_name": "白·冰镜本体",
                 "enemy_mods": {"hp": -180}},
                {"enemy_id": "zabuza_first", "enemy_name": "再不斩·水分身",
                 "enemy_skills": ["decapitating_blade", "water_clone"],
                 "enemy_mods": {"hp": -220, "attack": -10}},
            ],
            "transition": "冰镜碎裂的同时，再不斩的水分身越过卡卡西战线。真正的决战变成了二对二。",
            "transition_heal": 0.25,
            "special_rules": {
                "no_escape": True, "allies": allies,
                "objective_text": "击破白的本体与再不斩的水分身",
                "environment": "mist",
            },
        },
    ])
    if result == "lose":
        ui.story("""
千本封住四肢的刹那,一股赤红的查克拉自动涌出体表,
硬生生震碎了半面冰镜——白借机收了手。

「呼……呼……」鸣人单膝跪地,勉强撑住。

(战败了。但白的千本,始终避开着要害——他不想杀人。)
""")
        state.player["hp"] = max(state.player["hp"], int(state.player["max_hp"] * 0.3))
    else:
        ui.story("""
最后一记正拳轰碎面具——白仰面倒在碎冰之间,
清秀的脸上带着解脱般的平静。

「打输了呢。……果然,是你这样的人啊。」
""")
    ui.pause()


def _fate_crossroads(state):
    ui.title("命运节点: 雪落之时")
    ui.story("""
雾,正在散。

另一头的战局已到终章——卡卡西的手中雷光炸响,千鸟的
鸟鸣声刺穿雾气,直取查克拉耗尽的再不斩!

白的身体猛地一颤。

「对不起。」他挣扎着撑起身,朝那边踉跄扑去,
「我还有……最后一点用处——」

前世的画面轰然袭来:贯胸的雷刃、漫天的雪、
再不斩含泪的道别、还有桥头小小的两座坟。

心口的九瓣印记,烫得像火。

『孩子,』地球母亲的声音在血液里低语,
『命运的岔路就在眼前。要伸手吗?——伸手,是有代价的。』
""")
    opts = ["就这样目送。有些命运,或许不该由我改写……(原剧情结局)"]
    can_half = state.fate_points >= 2
    can_perfect = state.fate_points >= 4 and state.flags["haku_bond"] >= 2
    if can_half:
        opts.append("燃烧命运点,拦下白!(消耗2命运点——至少,救下这个孩子)")
    if can_perfect:
        opts.append("燃烧命运点,两个都救!(消耗4命运点+白的羁绊——挑战完美改写)")
    idx = ui.choose("", opts)

    if idx == 0:
        _ending_canon(state)
    elif idx == 1 and can_half:
        _ending_half(state)
    else:
        _ending_perfect(state)


def _ending_canon(state):
    ui.story("""
鸣人的手,伸到一半,停住了。

白化作一道白影扑进雷光——噗嗤。

雪,毫无预兆地落了下来。

之后的一切,和记忆里一模一样:加藤的背叛,再不斩
口衔苦无的最后冲锋,桥头并排的两座新坟,
和那句「忍者,也是人」。

鸣人在坟前站了很久很久。

「……对不起。」他攥紧拳头,指甲掐进掌心,
「下一个。下一个,我一定救。」
""")
    state.flags["haku_alive"] = False
    state.flags["zabuza_alive"] = False
    state.gain_fate(2, "铭记了雪之国度的教训")
    state.belonging -= 2
    ui.slow_print("※ 归属感 -2。(有些重量,只能背着走。)")
    ui.pause()


def _ending_half(state):
    if not state.spend_fate(2, "拦下扑向死亡的白"):
        _ending_canon(state)
        return
    ui.story("""
「白ーーー!!」

金色的命线自心口炸开,鸣人的身影快得超越了自己的极限——
在白扑进雷光的前一瞬,狠狠将他撞离了轨道!

千鸟贯穿了再不斩的肩胛。卡卡西及时偏转的一击,
没能致命——但紧接着,加藤带着数百佣兵出现在桥头,
撕毁契约,乱箭齐发。

再不斩笑了。他口衔苦无,拖着废掉的双臂
杀进人海,砍下了加藤的头颅,也耗尽了自己最后的血。

「白……活下去。这是命令,不是……请求……」

雪落满桥。这一次,坟只有一座。

白跪在坟前,一夜白霜。天亮时,他朝鸣人深深一拜:

「这条命是你抢回来的。请告诉我——我该怎么活?」

「先活着。」鸣人握住他冰凉的手,「然后,来木叶找我。」
""")
    state.flags["haku_alive"] = True
    state.flags["zabuza_alive"] = False
    state.add_backlash(1, "命运的轨道被强行扳动")
    state.gain_fate(1, "从死神手里抢回一条命")
    ui.pause()


def _ending_perfect(state):
    if not state.spend_fate(4, "同时改写两条命运"):
        _ending_canon(state)
        return
    ui.story("""
「白!站住——加藤要背叛了!!」

鸣人一声暴喝,声音撕开浓雾:

「卡卡西老师,住手!桥头三百佣兵,雇主是加藤!
 他从头就没打算付钱,他要连再不斩一起黑吃黑!!」

千鸟的雷光,在离再不斩胸口一寸处硬生生偏出——
几乎同时,桥头传来加藤阴恻恻的嗤笑和佣兵的鼓噪。

「哟,鬼人先生,被打得挺惨啊?正好,省了尾款——」

全场寂静了一瞬。

再不斩缓缓直起身,绷带下渗出压抑不住的笑:

「小鬼,」他看着鸣人,「你从哪儿知道的,不重要。
 重要的是——白,我们的雇佣关系,到此为止。」

「现在开始,是私人恩怨。」
""")
    ui.pause()
    ui.story("""
那一战,后来被波之国的孩子们讲了很多年:

雾隐之鬼一刀断潮,写轮眼的火龙焚天,黄毛小子的
影分身漫山遍野,连粉头发的姑娘都撂倒了三个佣兵。

加藤的头颅落进海里时,雪停了,雾散了,
太阳从云缝里洒下来,照亮整座大桥。

——无人死亡。

「喂,小鬼。」撤离前,再不斩单手拎起鸣人,与他平视,
「白说,你请我们去木叶?」

「嗯!担保人我来找!」

「哈。」鬼人把他扔给白接住,扛起大刀走向桥的那头,
「等桥修完。要是敢放老子鸽子——」

「木叶的大门永远开着!」

白站在原地,朝鸣人露出一个真正的、少年人的笑:

「那么——木叶见,鸣人。」
""")
    state.flags["haku_alive"] = True
    state.flags["zabuza_alive"] = True
    state.add_backlash(2, "两条命运同时改写,世界线剧烈震荡")
    state.gain_fate(3, "完美改写:雪之国度无人死去")
    state.add_trust(5)
    state.add_suspicion(10)
    ui.slow_print("※ 卡卡西对你「未卜先知」的疑心加深了——改命,总有代价。")
    ui.pause()


def _epilogue(state):
    ui.title("剧情: 大桥落成")
    ui.story("""
数日后,大桥落成。

「桥的名字想好了!」伊那利挺着小胸脯宣布,
「就叫——鸣人大桥!」

「哈?!以、以我命名?!」

「因为是你告诉我的啊,」小男孩笑得眼睛弯弯,
「英雄是存在的。」

渡船离岸,波之国的人群挥手的影子越来越小。
""")
    if state.flags["haku_alive"] and state.flags["zabuza_alive"]:
        ui.slow_print("(雾的深处,一高一矮两道身影立在桥塔顶端,朝渡船遥遥举了举手。)")
    elif state.flags["haku_alive"]:
        ui.slow_print("(桥头的坟前,白色的身影放下一束新采的药草,朝渡船深深鞠躬。)")
    quest.complete_quest(state, "wave_mission")
    state.add_rel("sakura", "responsibility", 5)
    state.add_rel("sasuke", "isolation", -5)
    ui.pause()

    # 海雾中的残光 → 琳剧情线
    rin_arc.sea_mist(state)

    state.flags["wave_done"] = True
    state.chapter = 3
    ui.story("""
═══════════════════════════

        波之国篇 · 完

═══════════════════════════

(回到木叶后:
 · 去桃源查看「药草田的微光」,唤醒那缕温柔的残念
 · 木叶医院有新的剧情与日常任务
 · 在火影办公室报名【中忍考试】,开启下一章
 · 记得存档!)
""")
    ui.pause()
