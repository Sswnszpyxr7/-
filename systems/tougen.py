# -*- coding: utf-8 -*-
"""桃源：专属小世界。休息、修炼、契约之树、命运回廊、忍术研究、桃源建设。"""
import random

from systems import contract, fate, time_system, ui

SCENERY = [
    "花海在微风中起伏，粉白的花瓣飘向远方。",
    "清澈的溪流绕过小屋，水声潺潺。",
    "远处的雪山映着夕照，泛出温柔的金红色。",
    "星空湖倒映着漫天星辰，安静得像一个梦。",
    "枫叶小径铺满红叶，每一步都沙沙作响。",
    "月光草原上，萤火虫提着小小的灯笼飞舞。",
]

# 定情后,恋人在桃源的专属闲话 (id -> 语录列表)
LOVER_CHAT = {
    "sakura": [
        """
小樱正在药草田边捣药,看见你,很自然地朝旁边挪了挪,
把小板凳空出一半——现在这是「两个人的位置」。

「今天的药,不苦。」她把一颗药丸塞进你嘴里,
 趁你没反应过来,飞快地在你脸颊上亲了一下,
「……嗯,是甜的吧。」
""",
        """
「喂,把手给我。」小樱捏着你的手检查旧伤,
 指尖的医疗查克拉暖暖的,「嗯,恢复得不错。」

 检查完了,她却没松手。就那么牵着,
 假装看星空湖的水面,耳朵红红的。
""",
    ],
    "hinata": [
        """
月光草原上,雏田靠着你的肩膀,数星空湖里的星星。

「白眼能看两公里远,」她忽然小声说,
「但最近,总是不由自主地,只看身边一米。」
""",
        """
雏田给你织了一条围巾——红色的,针脚细密。

「我妈妈说过,给喜欢的人织围巾,冬天就会一直牵手。」
 她把围巾绕上你的脖子,打了个漂亮的结,
「木叶的冬天,快到了哦。」
""",
    ],
    "tsunade": [
        """
纲手把公文全丢给了静音,难得偷得浮生半日。

「陪老娘躺着。」她拍拍身边的草地,你依言躺下。
 云很慢,风很软。她的指尖绕着你的头发,
「……这种日子,赌上国库老娘也不换。」
""",
        """
「小鬼,过来。」纲手招招手,变戏法似的掏出两个杯子,
「今天教你喝酒。喝不过我,不许上桌。」

 三杯下肚你就晕了。迷糊间,有人把你的头
 轻轻搬到了柔软的膝盖上。

「笨蛋徒孙。」声音又好气又好笑,「慢慢练。
 反正——日子长着呢。」
""",
    ],
    "konan": [
        """
小南在桃源住下了。溪流边多了一座纸折的小亭子,
精巧得像神明的手笔。

「雨隐的雨,木叶的晴,桃源的星空。」她把一朵
 新折的花别在你的衣襟上,「我全都要。还有你。」
""",
        """
你睡午觉的时候,小南用纸给你折了一床「被子」——
千万张纸鳞叠成的,又轻又暖。

醒来时她坐在旁边看书,发梢别着你送的那朵纸向日葵。

「醒了?」她翻过一页,嘴角弯弯,
「继续睡。天塌下来,有纸接着。」
""",
    ],
    "rin": [
        """
琳把工坊的门牌换了——从「药草工坊」
换成了「琳与鸣人的药草工坊」。

「字是我写的,牌子是带土刻的。」她叉着腰,
 骄傲得像个孩子,「他刻完还哭了,说什么
 『琳终于有家了』——笨蛋带土,这里早就是家了。」
""",
        """
星空湖边,琳枕着你的手臂,看流星划过。

「许愿了吗?」你问。

「不用许了。」她把你的手臂抱得更紧了些,
 声音里全是笑意,「死过一次的人最清楚——
 现在这样,就是愿望本身啊。」
""",
    ],
}

# 疾风传新契约者的闲话 (id -> 语录列表)
EXTRA_CHAT = {
    "sakura": [
        """
药草田边支起了一张新的工作台。小樱正在捣药,
见你过来,头也不抬地把一碗药汤推过来:

「喝。别问什么味,问就是琳前辈的配方,我改良的。」

(比琳前辈的版本还苦。但她盯着看,你一饮而尽。)

「……嗯。」她满意地点头,耳根却有点红,
「下一锅,给你加蜂蜜。」
""",
        """
「说起来,真的不可思议。」小樱望着星空湖,轻声说,
「忍者学校那会儿,我满脑子都是佐助君,把你当跟屁虫。

 结果一路走到今天——把后背交给谁最放心,
 我的答案早就变了。」

她握起拳头,在你肩上不轻不重地捶了一下:
「所以你也一样。敢死在我前面,我就把你捶活过来。」
""",
    ],
    "shizune": [
        """
静音抱着一摞医案从医疗室出来，看见你，眼睛一亮:

「鸣人君，来得正好——啊，不是要抽血！别跑！
 是琳前辈新调的营养剂，你尝尝苦不苦……诶，真的不苦！」

(是甜的。桃源的药，连味道都是温柔的。)
""",
        """
「师父她啊，嘴上凶，昨晚却在这里念叨了你半宿。」
静音一边给毒针上油，一边小声说，

「所以，别让她担心。也……也别让我担心。
 我们家的弟弟，可就你一个。」
""",
    ],
    "hinata": [
        """
月光草原上,雏田正在练柔拳。见你来了,她收势,
双颊微红,却没有像从前那样躲开视线。

「鸣人君。……陪,陪我练一会儿好吗?
 白眼看得见查克拉的流向——你的仙术,还有三处淤堵。」

指尖相抵的瞬间,命线轻轻发烫。
月光落在两个人的影子上,把它们连在了一起。
""",
        """
「小时候,我总是躲在电线杆后面看你。」

雏田坐在溪边,把一小盒药膏放进你手里——
她亲手做的,治擦伤最灵。

「现在不一样了。」她抬起头,白色的瞳仁映着星空湖的光,
 认真得不像那个爱脸红的少女,
「现在,我就走在你旁边。哪里都不去。」
""",
    ],
    "konan": [
        """
溪边，小南把一张纸折成花，放进水里。纸花漂了很远都不散。

『在雨隐，纸沾了水就完了。』她轻声说，
『可在这里，连纸都可以不必坚强。』

她又折了一朵，递给你。这一朵，是向日葵。
""",
        """
『弥彦总说，痛过的人才懂温柔。长门信了一半，走岔了路。』

小南望着星空湖，蓝发上落着花瓣。

『而你把另一半补全了——温柔过的人，才有资格谈痛。
 这句话，我替他们两个，说给你听。』
""",
    ],
    "mei": [
        """
温泉边，照美冥披着浴衣挽起长发，朝你晃了晃杯子:

「五个村子的文山会海，都没这一池温泉解乏。
 小英雄，陪水影大人聊两句——放心，不催婚，聊你的。」

雾气袅袅，她笑得像一汪化开的熔岩，暖而不烫。
""",
        """
「血雾之村的时代，我亲手终结的。」照美冥的声音难得认真，

「所以我知道，『守护温柔』这四个字，背后要多硬的骨头。
 你的骨头够硬，心又软——这样的男人……啊不，这样的忍者，
 值得把后背交给他。」
""",
    ],
}

# ── 忍术研究 (设计文档 §28.1) ──────────────────────

RESEARCH = {
    "multi_clone": {
        "name": "多重影分身修炼法",
        "cost": 2,
        "desc": "习得【多重影分身之术】，且桃源修炼收益翻倍",
        "hint": "需要: Lv.4 以上",
        "check": lambda s: s.player["level"] >= 4,
    },
    "seal_array": {
        "name": "简易封印阵",
        "cost": 2,
        "desc": "习得封印系忍术【简易封印阵】",
        "hint": "需要: 封印术 ≥ 12",
        "check": lambda s: s.player["seal_art"] >= 12,
    },
    "yang_heal": {
        "name": "阳遁恢复术",
        "cost": 2,
        "desc": "习得自我治疗忍术【阳遁恢复术】",
        "hint": "需要: 查克拉控制 ≥ 14，或琳的指导",
        "check": lambda s: s.player["chakra_control"] >= 14 or s.contracts["rin"]["unlocked"],
    },
    "cloak": {
        "name": "九尾查克拉外衣",
        "cost": 3,
        "desc": "习得【九尾查克拉外衣】(使用会提高九尾波动)",
        "hint": "需要: 玖辛奈契约等级 ≥ 3，且完成波之国篇",
        "check": lambda s: s.contracts["kushina"]["contract_level"] >= 3 and s.chapter >= 3,
    },
    "rasengan_perfect": {
        "name": "风遁·螺旋丸 (性质变化)",
        "cost": 3,
        "desc": "为螺旋丸注入风之性质变化，威力提升 (螺旋丸威力+25)",
        "hint": "需要: 正式习得螺旋丸(寻找纲手篇)，查克拉控制 ≥ 16",
        "check": lambda s: s.flags["rasengan_official"] and s.player["chakra_control"] >= 16,
    },
    "rasenshuriken": {
        "name": "风遁·螺旋手里剑",
        "cost": 5,
        "desc": "习得终极自创禁术【风遁·螺旋手里剑】",
        "hint": "需要: 完成「风遁·螺旋丸」研究，查克拉控制 ≥ 20",
        "check": lambda s: s.has_research("rasengan_perfect") and s.player["chakra_control"] >= 20,
    },
    "sage_sense": {
        "name": "仙术基础感知",
        "cost": 3,
        "desc": "静坐感知自然能量，感知 +10、速度 +3",
        "hint": "需要: 第六章之后，精神 ≥ 40",
        "check": lambda s: s.chapter >= 5 and s.player["spirit"] >= 40,
    },
    "ninelives_fusion": {
        "name": "九命共鸣",
        "cost": 4,
        "desc": "习得融合忍术【九命共鸣】，威力与守护随契约成长",
        "hint": "需要: 已缔结契约 ≥ 3 人",
        "check": lambda s: sum(1 for c in s.contracts.values() if c.get("unlocked")) >= 3,
    },
}


def research_menu(state):
    ui.title("桃源 · 忍术研究")
    ui.story("""
书房里摊着写满笔记的卷轴。前世的记忆是最好的老师，
而桃源里的时间，安静得刚好适合钻研。
""")
    while True:
        keys = list(RESEARCH.keys())
        opts = []
        for k in keys:
            r = RESEARCH[k]
            if state.has_research(k):
                opts.append(f"[已完成] {r['name']}")
            elif r["check"](state):
                opts.append(f"[可研究] {r['name']} (命运点{r['cost']}) - {r['desc']}")
            else:
                opts.append(f"[未满足] {r['name']} - {r['hint']}")
        idx = ui.choose(f"(持有命运点: {state.fate_points})", opts, allow_cancel=True)
        if idx < 0:
            return
        key = keys[idx]
        r = RESEARCH[key]
        if state.has_research(key):
            ui.slow_print("这项研究已经完成了。")
            continue
        if not r["check"](state):
            ui.slow_print(f"条件尚未满足。{r['hint']}")
            continue
        if state.fate_points < r["cost"]:
            ui.slow_print("命运点不足。")
            continue
        state.fate_points -= r["cost"]
        state.research_done.append(key)
        _apply_research(state, key)
        ui.pause()


def _apply_research(state, key):
    p = state.player
    if key == "multi_clone":
        state.learn_skill("multi_shadow_clone")
        ui.story("""
数百个影分身在花海中同时扎起马步——桃源之内，没人会看到，
也没人会怀疑。禁术级的修炼法，从今天起就是日常。

★ 习得【多重影分身之术】！桃源修炼收益翻倍！
""")
    elif key == "seal_array":
        state.learn_skill("simple_seal_array")
        ui.story("""
在玖辛奈的远程指点下，你在研究间的地板上画出了
第一个能够自主运转的漩涡流封印阵。

『不错嘛。不愧是我儿子。』

★ 习得【简易封印阵】！对尾兽、咒印类敌人有奇效。
""")
    elif key == "yang_heal":
        state.learn_skill("yang_heal")
        if state.contracts["rin"]["unlocked"]:
            ui.story("""
「手要这样放，查克拉像溪水一样流过去——对，就是这样。」

琳手把手教了三个晚上。当掌心第一次泛起碧绿的光时，
她笑得比鸣人还开心。

★ 习得【阳遁恢复术】！
""")
        else:
            ui.story("""
以漩涡一族的生命力为引，你摸索出了粗糙但有效的
自我治疗之法。

★ 习得【阳遁恢复术】！
""")
    elif key == "cloak":
        state.learn_skill("nine_tails_cloak")
        ui.story("""
『借力可以，但记住——』玖辛奈神情少见地严肃，
『那孩子的力量是烈火。用它护人，别让它烧了你自己。』

★ 习得【九尾查克拉外衣】！攻击大幅提升。
(注意: 使用会提高九尾波动与暴露度。)
""")
    elif key == "rasengan_perfect":
        # 直接改技能库数值;读档时由 state.from_dict 依据 research_done 重放
        state.skills_db["rasengan"]["power"] = 120
        ui.story("""
螺旋丸中央，出现了一枚细小的、白色的风之刃。
四代目未竟的课题——性质变化的融合，迈出了第一步。

★ 螺旋丸威力提升至 120！
""")
    elif key == "rasenshuriken":
        state.learn_skill("rasenshuriken")
        ui.story("""
风声如手里剑的尖啸。掌心之上，白色的巨大风轮缓缓成形，
连桃源的花海都被吹伏了一片。

『这一世提前这么多年搞出这个……鸣人，你真是乱来。』
玖辛奈嘴上数落着，眼里全是骄傲。

★ 习得【风遁·螺旋手里剑】！
""")
    elif key == "sage_sense":
        p["sense"] += 10
        p["speed"] += 3
        ui.story("""
你在契约之树下静坐。呼吸放缓、心跳放缓，
渐渐地，整个桃源的风、水、光，都变成了「自己」的一部分。

蛤蟆仙人的修行，前世要在妙木山才能开始——
但「感知自然」这一步，桃源就是最好的道场。

★ 感知 +10、速度 +3！
""")
    elif key == "ninelives_fusion":
        state.learn_skill("ninelives_fusion")
        ui.story("""
契约之树下，你把手贴上树心。已经亮起的命线
一条条应声轻鸣，光顺着掌心涌进经络——

不是谁借你力量。是「家」本身，成为了忍术。

★ 习得【九命共鸣】！契约者越多、羁绊越深，它就越强。
""")


# ── 桃源建设 (设计文档 §28.2) ──────────────────────

BUILDINGS = {
    "cottage": {
        "name": "小屋·温居", "cost": 2,
        "desc": "闲坐时归属感翻倍，契约者的话也更多",
        "check": lambda s: True, "hint": "",
    },
    "medical_room": {
        "name": "医疗室", "cost": 3,
        "desc": "每日首次进入桃源获得 1 枚回复丹",
        "check": lambda s: s.contracts["rin"]["unlocked"] or s.flags["tsunade_done"],
        "hint": "需要: 琳的契约，或完成寻找纲手篇",
    },
    "seal_lab": {
        "name": "封印术研究间", "cost": 2,
        "desc": "封印术修炼收益 +1",
        "check": lambda s: s.flags["kushina_contacted"], "hint": "需要: 玖辛奈契约",
    },
    "courtyard": {
        "name": "修炼庭院·扩建", "cost": 2,
        "desc": "体术修炼收益 +1",
        "check": lambda s: True, "hint": "",
    },
    "hot_spring": {
        "name": "温泉", "cost": 2,
        "desc": "休息时精神舒缓，归属感 +1",
        "check": lambda s: True, "hint": "",
    },
    "herb_field": {
        "name": "药草田", "cost": 2,
        "desc": "每日首次进入桃源获得 1 株药草",
        "check": lambda s: s.contracts["rin"]["unlocked"], "hint": "需要: 琳的契约",
    },
    "tree_boost": {
        "name": "契约之树·深化", "cost": 4,
        "desc": "契约升级所需命运点 -2 (最低2)",
        "check": lambda s: True, "hint": "",
    },
    "corridor_ext": {
        "name": "命运回廊·扩建", "cost": 3,
        "desc": "窥视命运碎片不再消耗命运点",
        "check": lambda s: True, "hint": "",
    },
}


def build_menu(state):
    ui.title("桃源 · 建设")
    ui.story("""
桃源随心而变。只要命运之力足够，
这个家就能长出新的房间、新的田地、新的温柔。
""")
    while True:
        keys = list(BUILDINGS.keys())
        opts = []
        for k in keys:
            b = BUILDINGS[k]
            if state.has_building(k):
                opts.append(f"[已建成] {b['name']}")
            elif b["check"](state):
                opts.append(f"[可建造] {b['name']} (命运点{b['cost']}) - {b['desc']}")
            else:
                opts.append(f"[未满足] {b['name']} - {b['hint']}")
        idx = ui.choose(f"(持有命运点: {state.fate_points})", opts, allow_cancel=True)
        if idx < 0:
            return
        key = keys[idx]
        b = BUILDINGS[key]
        if state.has_building(key):
            ui.slow_print("这里已经建好了。")
            continue
        if not b["check"](state):
            ui.slow_print(f"条件尚未满足。{b['hint']}")
            continue
        if state.fate_points < b["cost"]:
            ui.slow_print("命运点不足。")
            continue
        state.fate_points -= b["cost"]
        state.tougen_buildings.append(key)
        ui.slow_print(f"★ 【{b['name']}】在温暖的金光中落成了！")
        ui.slow_print(f"   效果: {b['desc']}")
        ui.pause()


# ── 桃源主菜单 ──────────────────────────────────

def enter_tougen(state):
    if not state.flags["tougen_unlocked"]:
        ui.story("""
你站在心底那扇朦胧的门前。
门后传来温暖的气息，却还差一把钥匙。
(桃源尚未完全开启——继续推进剧情吧。)
""")
        ui.pause()
        return

    ui.title("桃 源")
    ui.slow_print(random.choice(SCENERY))
    if state.flags["kushina_contacted"]:
        ui.slow_print("小屋旁的红枫林沙沙作响——那是属于玖辛奈的颜色。")
    if state.contracts["rin"]["unlocked"]:
        ui.slow_print("药草田里药香浮动——那是属于琳的温柔。")
    elif state.flags["rin_light_found"]:
        ui.slow_print("(花海的一角，出现了一小片朦胧的药草田虚影，中央浮着一缕碧色微光……)")
    if state.contracts["sakura"]["unlocked"]:
        ui.slow_print("药草田边多了一张捣药的工作台，樱色的发绳系在台角——小樱的位置。")
    if state.contracts["hinata"]["unlocked"]:
        ui.slow_print("月光草原的边缘，薰衣草悄悄连成了一片——那是属于雏田的、安静的颜色。")
    if state.contracts["konan"]["unlocked"]:
        ui.slow_print("溪水上漂着永不濡湿的纸花，一路漂向星空湖。")
    if state.contracts["mei"]["unlocked"]:
        ui.slow_print("温泉的雾气里融进了一丝熔岩的暖意，连雪山的方向都变得柔和。")
    if state.contracts["gaia"]["unlocked"]:
        ui.slow_print("脚下的大地传来极缓、极安稳的搏动——第九条命线，与桃源同频呼吸。")

    # 建筑馈赠只在每日首次进入时结算，避免退出再进入反复领取。
    if state.consume_daily_use("tougen_supply", limit=1):
        if state.has_building("medical_room"):
            state.add_item("回复丹", 1, cap=5)
        if state.has_building("herb_field"):
            state.add_item("药草", 1, cap=5)

    talked = set()  # 本次进入桃源已谈心的契约者
    while True:
        opts = [
            ui.Choice("休息恢复", ("actions", "rest"), "生命/查克拉/负面状态全恢复"),
            ui.Choice("契约之树", ("actions", "contract_tree"), "查看/提升契约"),
            ui.Choice("命运回廊", ("actions", "fate_corridor"), "窥视未来/安抚反噬"),
            ui.Choice("修炼庭院", ("actions", "training_court"), "消耗时间提升属性"),
            ui.Choice("忍术研究", ("actions", "ninjutsu_research"), "以前世记忆开发新术"),
            ui.Choice("桃源建设", ("actions", "tougen_build"), "扩建这个家"),
            ui.Choice("在小屋里坐一会儿", ("actions", "rest")),
        ]
        if any(c.get("unlocked") for c in state.contracts.values()):
            opts.insert(1, ui.Choice("个别谈心", ("actions", "heart_talk"), "与契约者加深羁绊"))
            opts.insert(2, ui.Choice("送礼", ("actions", "gift"), "以心意浇灌命线"))
        extra = []
        if state.flags["rin_light_found"] and not state.flags["rin_contacted"]:
            extra.append("【剧情】走向药草田的微光")
        if state.kyubi_flux >= 50 and state.flags["kushina_contacted"]:
            extra.append("【剧情】和妈妈谈谈九尾的力量")
        # 琳的恋爱线
        from scenes import romance
        rom_acts = {label: handler
                    for label, handler in romance.get_tougen_romance_actions(state)}
        extra += list(rom_acts.keys())
        opts = extra + opts

        idx = ui.choose("在桃源做什么?", opts, allow_cancel=True)
        if idx < 0:
            ui.slow_print("你在心底轻轻关上桃源之门，回到现实。")
            return
        label = ui.choice_label(opts[idx])
        if label in rom_acts:
            rom_acts[label](state)
        elif label.startswith("【剧情】走向药草田"):
            from scenes import rin_arc
            rin_arc.herb_garden_awakening(state)
        elif label.startswith("【剧情】和妈妈谈谈"):
            _kyubi_calm(state)
        elif label.startswith("休息恢复"):
            rest(state)
        elif label.startswith("个别谈心"):
            from scenes import bonding
            bonding.heart_talk(state, talked)
        elif label.startswith("送礼"):
            from scenes import bonding
            bonding.give_gift(state)
        elif label.startswith("契约之树"):
            contract.show_contract_menu(state)
        elif label.startswith("命运回廊"):
            fate.show_fate_corridor(state)
        elif label.startswith("修炼庭院"):
            train(state)
        elif label.startswith("忍术研究"):
            research_menu(state)
        elif label.startswith("桃源建设"):
            build_menu(state)
        else:
            chat(state)


def rest(state):
    p = state.player
    p["hp"] = p["max_hp"]
    p["chakra"] = p["max_chakra"]
    p["status"] = []
    ui.story("""
你躺在小屋柔软的榻上，温暖的光透过窗子洒进来。
疲惫、伤痛、连同心里的阴霾，都被轻轻抚平了。
※ 生命、查克拉完全恢复，负面状态解除。
""")
    if state.has_building("hot_spring"):
        if state.consume_daily_use("tougen_hot_spring", limit=1):
            state.belonging += 1
            ui.slow_print("※ 温泉的热气舒缓了紧绷的神经。归属感 +1。（今日首次）")
    time_system.advance_time(state)
    ui.pause()


def train(state):
    session_cap = max(4, state.chapter * 2)
    if state.tougen_training_sessions >= session_cap:
        ui.slow_print(
            f"这一阶段能消化的桃源修炼已经饱和（{session_cap}/{session_cap}）。推进主线后再来吧。"
        )
        return
    if state.daily_uses("tougen_training") >= 1:
        ui.slow_print("今天的经络已经接近极限。桃源修炼每日只能获得一次属性成长。")
        return
    p = state.player
    mult = 2 if state.has_research("multi_clone") else 1
    seal_bonus = 1 if state.has_building("seal_lab") else 0
    tai_bonus = 1 if state.has_building("courtyard") else 0
    opts = [
        f"查克拉控制 (查克拉控制+{mult}，查克拉上限+{5*mult})",
        f"封印术 (封印术+{mult + seal_bonus})",
        f"体术 (攻击+{mult + tai_bonus})",
    ]
    if state.contracts["rin"]["unlocked"]:
        opts.append(f"医疗基础·琳指导 (精神+{mult}，查克拉控制+1)")
    prompt = "修炼什么?" + (" (多重影分身修炼法: 收益×2)" if mult == 2 else "")
    idx = ui.choose(prompt, opts, allow_cancel=True)
    if idx < 0:
        return
    state.consume_daily_use("tougen_training", limit=1)
    state.tougen_training_sessions += 1
    if idx == 0:
        p["chakra_control"] += mult
        p["max_chakra"] += 5 * mult
        ui.slow_print(f"※ 树叶在指尖稳稳漂浮。查克拉控制 → {p['chakra_control']}，查克拉上限 → {p['max_chakra']}")
    elif idx == 1:
        p["seal_art"] += mult + seal_bonus
        ui.slow_print(f"※ 你在研究间描摹漩涡一族的封印纹路。封印术 → {p['seal_art']}")
    elif idx == 2:
        p["attack"] += mult + tai_bonus
        ui.slow_print(f"※ 修炼庭院里拳风呼啸。攻击 → {p['attack']}")
    else:
        p["spirit"] += mult
        p["chakra_control"] += 1
        ui.slow_print(f"※ 琳握着你的手腕纠正查克拉输出。精神 → {p['spirit']}，查克拉控制 → {p['chakra_control']}")
    ui.slow_print("(桃源的修炼加成，让收获比外界更扎实。)")
    ui.slow_print(f"(本阶段桃源修炼：{state.tougen_training_sessions}/{session_cap})")
    time_system.advance_time(state)
    ui.pause()


def _kyubi_calm(state):
    ui.title("剧情: 烈火与安抚")
    if not state.flags["kyubi_calm_done"]:
        ui.story("""
「妈妈,」鸣人在红枫林里坐下,摊开手掌——
掌心之上,赤红色的查克拉正不安地明灭着。

「最近借它的力量,有点多了。」

玖辛奈的残影在枫叶间浮现。她没有说教,只是伸出手,
虚虚地覆在那团躁动的红光上。

『黄色闪光的封印,加上我漩涡玖辛奈的锁链,』
她微微一笑,『再加上你自己的心——三重保险,怕什么。』

『但是鸣人,记住:力量收不住的时候,就想想桃源。
 想想这里的每一个人。那就是你的锚。』

金色的命线缠上手腕,赤红的波动如潮水般退去。
""")
        state.player["seal_art"] += 2
        state.flags["kyubi_calm_done"] = True
        state.kyubi_flux = max(0, state.kyubi_flux - 40)
        ui.slow_print(f"※ 九尾波动大幅平息 [当前: {state.kyubi_flux}]，封印术 +2。")
    else:
        ui.story("""
红枫林里,玖辛奈的指尖再次覆上那团躁动的红光。

『又乱来了吧。』她轻轻点了点鸣人的额头,
『没关系。有几次,妈妈就安抚几次。』
""")
        state.kyubi_flux = max(0, state.kyubi_flux - 40)
        ui.slow_print(f"※ 九尾波动平息 [当前: {state.kyubi_flux}]。")
    ui.pause()


def chat(state):
    grants_reward = state.consume_daily_use("tougen_chat", limit=1)
    speakers = []
    if state.flags["kushina_contacted"]:
        speakers.append("kushina")
    if state.contracts["rin"]["unlocked"]:
        speakers.append("rin")
    if state.contracts["tsunade"]["unlocked"]:
        speakers.append("tsunade")
    for cid in ("sakura", "shizune", "hinata", "konan", "mei"):
        if state.contracts[cid]["unlocked"]:
            speakers.append(cid)

    if not speakers:
        ui.story("""
你独自坐在小屋里。屋子很温暖，却也很安静。

你知道，这里迟早会热闹起来的。

这一世，你不会再一个人了。
""")
        if grants_reward:
            state.belonging += 1
            ui.slow_print("※ 归属感 +1。（今日闲坐收益已领取）")
        else:
            ui.slow_print("(今天已经在小屋里好好休息过了，这次只享受片刻安静。)")
        ui.pause()
        return

    who = random.choice(speakers)
    lover = state.flags.get("lover", "")
    # 定情后,恋人有一半概率被抽中,使用专属语录
    if lover in speakers and lover in LOVER_CHAT and (who == lover or random.random() < 0.5):
        ui.story(random.choice(LOVER_CHAT[lover]))
        gain = 3 if state.has_building("cottage") else 2
        if grants_reward:
            state.belonging += gain
            ui.slow_print(f"※ 归属感 +{gain} [当前: {state.belonging}]（今日闲坐收益已领取）")
        else:
            ui.slow_print("(今日闲坐带来的归属感收益已经领取。)")
        ui.pause()
        return
    if who == "kushina":
        ui.story(random.choice([
            """
你坐在小屋的茶室里。茶香袅袅。

『……鸣人，要好好吃饭。别老是只吃拉面。』

『拉面要配蔬菜！听到没有！』

你笑着应了一声，眼眶有点热。
""",
            """
玖辛奈盘腿坐在廊下，绘声绘色地讲着当年的事——

『然后你爸那个笨蛋，约会迟到就算了，还把信物掉进了河里！
 气得我差点用锁链把他吊在火影岩上！』

红枫叶落了她一肩。这样的夜晚，前世的鸣人做梦都想要。
""",
            """
『来，把手伸出来。』玖辛奈虚虚握住你的手腕，
指尖描着经络，『封印术的第一课不是画纹路，是「听」。
 听查克拉自己想往哪里流。』

窗外星空湖的水声，和妈妈的声音混在一起。
""",
        ]))
    elif who == "rin":
        ui.story(random.choice([
            """
药草田边，琳挽着袖子分拣药草，见你过来便扬起笑:

「来得正好！尝尝这个——补血的药丸，我改良了配方，
 这次真的不苦了！……大概。」

(还是苦的。但你面不改色地咽了下去，她笑弯了眼。)
""",
            """
「卡卡西他……现在还总迟到吗？」琳望着溪水，轻声问。

「嗯。每次都说是在人生的道路上迷了路。」

「呵呵，那是带土的口头禅哦。」她笑着笑着，眼睛湿了，
「……谢谢你告诉我。谢谢你，还记得我们。」
""",
            """
琳把一枚亲手编的护身符塞进你手里，针脚歪歪扭扭。

「医疗忍者的守则第一条，是活着回来。
 做不到的话——」她板起脸，随即又忍不住笑场，
「做不到的话，就回桃源来，我给你补到做到为止。」
""",
        ]))
    else:
        ui.story(random.choice([
            """
纲手就着月光在廊下小酌，见你来了，弹了弹身边的地板。

「坐。……哼，这地方连酒都是甜的，没劲。」

嘴上抱怨着，她却一杯接一杯，眉间的川字
比在外面的任何时候都要浅。
""",
            """
「手伸出来。」纲手捏着你的手腕捻了捻，
「查克拉通路又练粗了。臭小子，悠着点，
 你的命现在可不只是你一个人的。」

说完她自己愣了愣，随即哼笑:「……这话还真是，这里的规矩。」
""",
        ]) if who == "tsunade" else random.choice(EXTRA_CHAT[who]))
    gain = 2 if state.has_building("cottage") else 1
    if who == "kushina":
        gain += 1
    if grants_reward:
        state.belonging += gain
        ui.slow_print(f"※ 归属感 +{gain} [当前: {state.belonging}]（今日闲坐收益已领取）")
    else:
        ui.slow_print("(今日闲坐带来的归属感收益已经领取。)")
    ui.pause()
