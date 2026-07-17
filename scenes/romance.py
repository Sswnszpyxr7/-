# -*- coding: utf-8 -*-
"""恋爱线:小樱/雏田/纲手/小南/琳。

疾风传开启(shippuden_started),前置各自契约。
两段约会事件积累「心动值」,大战完结(war_done)后
在专属地点告白定情——единственный恋人制,定情后其余命线温柔收束为家人。
"""
from systems import ui

NAMES = {"sakura": "小樱", "hinata": "雏田", "tsunade": "纲手",
         "konan": "小南", "rin": "琳"}

# 告白地点提示 (id -> 地点名)
CONFESS_SPOT = {"sakura": "木叶医院", "hinata": "第七训练场", "tsunade": "火影办公室",
                "konan": "木叶大门", "rin": "桃源"}


def _ready(state, who):
    """恋爱线开启条件:疾风传 + 契约已缔结。"""
    return state.flags["shippuden_started"] and state.contracts[who]["unlocked"]


def can_confess(state, who):
    """告白条件:大战完结、心动≥50、尚未定情。"""
    return (state.flags["war_done"] and state.romance.get(who, 0) >= 50
            and not state.flags["lover"])


def get_romance_actions(state, loc):
    """返回当前地点的恋爱事件 [(标签, handler)]。"""
    f = state.flags
    acts = []
    if loc == "konoha_hospital" and _ready(state, "sakura"):
        if not f["rom_sakura_1"]:
            acts.append(("【心动】加班的医疗班 (小樱)", sakura_date_1))
        elif f["rom_sakura_2"] and can_confess(state, "sakura"):
            acts.append(("【告白】医院天台的晚霞 (小樱)", sakura_confess))
    if loc == "ichiraku":
        if _ready(state, "sakura") and f["rom_sakura_1"] and not f["rom_sakura_2"]:
            acts.append(("【心动】两碗拉面 (小樱)", sakura_date_2))
        if _ready(state, "tsunade") and f["rom_tsunade_1"] and not f["rom_tsunade_2"]:
            acts.append(("【心动】不赌牌的夜晚 (纲手)", tsunade_date_2))
    if loc == "training_ground_7" and _ready(state, "hinata"):
        if f["hinata_contracted"] and not f["rom_hinata_1"]:
            acts.append(("【心动】月下的组手 (雏田)", hinata_date_1))
        elif f["rom_hinata_2"] and can_confess(state, "hinata"):
            acts.append(("【告白】三根木桩的约定 (雏田)", hinata_confess))
    if loc == "hokage_rock" and _ready(state, "hinata") and f["rom_hinata_1"] and not f["rom_hinata_2"]:
        acts.append(("【心动】火影岩上的两个人 (雏田)", hinata_date_2))
    if loc == "hokage_office" and _ready(state, "tsunade"):
        if not f["rom_tsunade_1"]:
            acts.append(("【心动】深夜的办公室 (纲手)", tsunade_date_1))
        elif f["rom_tsunade_2"] and can_confess(state, "tsunade"):
            acts.append(("【告白】火影帽下的答案 (纲手)", tsunade_confess))
    if loc == "konoha_gate" and _ready(state, "konan"):
        if state.flags["pain_done"] and not f["rom_konan_1"]:
            acts.append(("【心动】雨之国的来客 (小南)", konan_date_1))
        elif f["rom_konan_1"] and not f["rom_konan_2"]:
            acts.append(("【心动】纸伞下 (小南)", konan_date_2))
        elif f["rom_konan_2"] and can_confess(state, "konan"):
            acts.append(("【告白】第一万零一朵纸花 (小南)", konan_confess))
    return acts


def get_tougen_romance_actions(state):
    """桃源内的琳恋爱事件。"""
    f = state.flags
    acts = []
    if _ready(state, "rin"):
        if not f["rom_rin_1"]:
            acts.append(("【心动】星空湖的夜钓 (琳)", rin_date_1))
        elif not f["rom_rin_2"]:
            acts.append(("【心动】一起做药丸 (琳)", rin_date_2))
        elif can_confess(state, "rin"):
            acts.append(("【告白】药草田的花开了 (琳)", rin_confess))
    return acts


# ══════════════════ 小樱 ══════════════════

def sakura_date_1(state):
    ui.title("心动: 加班的医疗班")
    ui.story("""
深夜的木叶医院,只有三楼还亮着一盏灯。

小樱趴在值班室的桌上睡着了,手边摊着写了一半的病历,
发梢垂进墨水瓶旁边,呼吸轻轻的。

你把带来的饭盒放到桌角,想给她披件外套——

「唔……影分身,查克拉输出再压低半成……」她说着梦话,
 眉头还皱着,连梦里都在给人治伤。

外套刚披上肩,她惊醒了,看清是你,脸一下子红了:
「鸣、鸣人?!几点了——你看到我流口水了吗?!」

「没有。」(看到了。)

「……饭盒是给我的?」她打开,是一乐大叔特制的
 蔬菜多多拉面,还温着。她小口小口吃着,忽然说:
「喂。下次,别只在我加班的时候来啊。」
""")
    state.flags["rom_sakura_1"] = True
    state.add_romance("sakura", 25)
    state.belonging += 1
    ui.pause()


def sakura_date_2(state):
    ui.title("心动: 两碗拉面")
    ui.story("""
「今天我请客。」小樱在一乐的柜台前坐下,把钱包
拍在台面上,「庆祝医疗班考核全员通过。」

两碗拉面,你一碗她一碗。她学着你的样子先喝汤,
烫得直吐舌头,又不肯认输地继续喝。

「以前啊,」她忽然说,「我总觉得来一乐吃面,
 是你和佐助君他们的事。我就……不算在里面。」

「现在呢?」

「现在?」她把最后一颗溏心蛋夹到你碗里,理直气壮,
「现在这里的位置是我的。谁来都不让。」

大叔在灶台后面憋笑憋得肩膀直抖。
""")
    state.flags["rom_sakura_2"] = True
    state.add_romance("sakura", 30)
    state.add_rel("sakura", "trust", 5)
    ui.pause()


def sakura_confess(state):
    ui.title("告白: 医院天台的晚霞")
    ui.story("""
战后的医院天台。晚霞把整个木叶染成蜜色。

小樱靠着栏杆,白大褂被风吹起一角。听见脚步声,
她没有回头:「我就知道你会来。」

「小樱。」你走到她身边,「有句话,想了很久。」

「……嗯。」

「从铃铛测试那天起,你就一直在。追我打的是你,
 给我包扎的是你,在沙漠里跟我并排跪着救人的,
 也是你。」你深吸一口气,「我喜欢你。不是同伴的那种——
 是想一辈子,把后背交给你的那种。」

晚霞烧得正艳。她转过身来,眼睛比晚霞还亮,
抬手作势要打,落下来却轻轻攥住了你的衣角。

「笨蛋。」她说,声音哽咽,「医疗忍者的守则第一条,
 是活着回来——从今往后,你的『回来』,都归我管了。」
""")
    _seal_love(state, "sakura")


# ══════════════════ 雏田 ══════════════════

def hinata_date_1(state):
    ui.title("心动: 月下的组手")
    ui.story("""
第七训练场。月色正好,雏田如约而至。

「契约之后,白眼能看见你查克拉的『颜色』了。」她轻声说,
「今晚……让我看看仙人模式的金色,好吗?」

组手开始。柔拳的掌影与你的体术在月光下交错,
她的动作越来越流畅,像一支终于敢跳完的舞。

一个失衡——你伸手扶住她的手腕,两个人都顿住了。

「……心跳,」她小声说,耳尖通红,「白眼,连心跳都看得见的。
 鸣人君现在,心跳很快。」

「彼此彼此。」你也红了脸。

月亮躲进云里,像是很识趣。
""")
    state.flags["rom_hinata_1"] = True
    state.add_romance("hinata", 25)
    state.belonging += 1
    ui.pause()


def hinata_date_2(state):
    ui.title("心动: 火影岩上的两个人")
    ui.story("""
「这里是我的秘密基地。」你带雏田爬上四代目的石像头顶,
「前世……很小的时候,难过了就来这里。」

雏田在你身边坐下,把带来的便当摊开——玉子烧
摆成了螺旋丸的形状,一看就练习过很多次。

「那时候的鸣人君,一个人坐在这里,在想什么呢?」

「在想,什么时候才会有人找我一起吃饭。」

她安静了一会儿,然后把便当往中间推了推,
声音很轻,却清清楚楚:

「以后每一顿,我都找你。」

夕阳落进远山。整个木叶在脚下亮起灯火,
像谁把星空铺在了地上。
""")
    state.flags["rom_hinata_2"] = True
    state.add_romance("hinata", 30)
    state.belonging += 2
    ui.pause()


def hinata_confess(state):
    ui.title("告白: 三根木桩的约定")
    ui.story("""
战后的第七训练场。三根木桩静静立在河边,
中间那根上,新刻了一个小小的九瓣花印。

「雏田。」你站在木桩前,转身面对她,
「佩恩那一战,你说『哪里都不去,就在你身边』。
 战争结束了——这句话,还算数吗?」

她怔住了,白色的瞳仁里月光轻轻晃动。

「我喜欢你,雏田。」你一字一句,不再让任何迟钝
 耽误任何等待,「从你把伤药塞给我的那天,从你在
 佩恩面前挡在我身前的那天——不,或许更早。
 这一世重来一次,我不想再错过你。」

眼泪毫无预兆地涌出来。她一边哭一边笑,
一步一步走过来,把额头轻轻抵在你的胸口——
心口的九瓣花印记,暖得像一个小小的太阳。

「算数。」她说,「一辈子,都算数。」
""")
    _seal_love(state, "hinata")


# ══════════════════ 纲手 ══════════════════

def tsunade_date_1(state):
    ui.title("心动: 深夜的办公室")
    ui.story("""
火影办公室的灯,又亮到了后半夜。

你端着一乐的外卖推门进去,纲手头也不抬:
「静音,我说了这摞批完就——」抬头,「……是你啊,小鬼。」

「静音姐被我支去休息了。」你把面放到文件山的
 唯一空隙里,「火影大人,该吃饭了。」

她瞪了你半天,到底还是拿起了筷子。吃到一半,
忽然说:「绳树以前,也这样给我送过面。」

「那我明天还送。」

「……哼。」她别过脸去,耳根却红了,
「明天,记得多要一份叉烧。」
""")
    state.flags["rom_tsunade_1"] = True
    state.add_romance("tsunade", 25)
    state.belonging += 1
    ui.pause()


def tsunade_date_2(state):
    ui.title("心动: 不赌牌的夜晚")
    ui.story("""
一乐的帘子外飘着小雨。纲手难得没有处理公务,
和你并肩坐在柜台前,面前摆着清酒。

「陪老娘玩两把?」她掏出扑克,又自己收了回去,
「算了。跟你赌,老娘的手气会好——那才是凶兆。」

你们就那么喝着聊着。聊绳树,聊断,聊自来也
年轻时的糗事,聊着聊着她笑出了眼泪。

「小鬼。」雨停的时候,她忽然说,「你知道吗,
 遇见你之前,老娘赌了半辈子,就想输光所有,
 好有借口离这个伤心的村子远远的。」

「现在呢?」

她把杯里的酒一饮而尽,笑得像卸下了千斤:

「现在啊——舍不得走喽。」
""")
    state.flags["rom_tsunade_2"] = True
    state.add_romance("tsunade", 30)
    state.belonging += 2
    ui.pause()


def tsunade_confess(state):
    ui.title("告白: 火影帽下的答案")
    ui.story("""
战后的火影办公室。夕阳从火影岩的方向照进来,
把「五代目」的帽子镀了一层金边。

「纲手。」你把门关上,认真地站到桌前。

她批文件的手停了。这些年,你从没这样叫过她——
不是奶奶,不是纲手姐,不是火影大人。

「我知道这很任性。你失去过绳树,失去过断,
 你说过不想再把心交给会死在你前面的男人。」

你摊开手掌,命线的金光静静流转:

「所以我用九命一系向你保证——我死不了。
 有九条命线拴着,有整个家拽着,我哪里都去不了。
 纲手,我喜欢你。让我陪你,把往后每一把都赢回来。」

好久,好久。她站起身,绕过桌子,屈指在你额头
轻轻一弹——然后顺势,把你拉进了怀里。

「这一把,」她的声音闷闷的,带着笑也带着泪,
「老娘,梭哈了。」
""")
    _seal_love(state, "tsunade")


# ══════════════════ 小南 ══════════════════

def konan_date_1(state):
    ui.title("心动: 雨之国的来客")
    ui.story("""
木叶大门的守卫来报:有位「蓝头发的大姐姐」找你。

小南站在门外的官道上,肩头落着旅尘,怀里抱着
一束用纸折的花——每一朵都是不同的折法。

「雨隐的重建,告一段落了。」她说,「来看看
 命线另一头的……家。」

你带她走遍木叶:一乐拉面、火影岩、重建后的街道。
她话不多,却把每一处都看得很仔细。

「弥彦说过,想亲眼看看和平的村子长什么样子。」
临走时,她把纸花束留给你,轻声说,
「今天,我替他看到了。……下次,为我自己再来一次。」
""")
    state.flags["rom_konan_1"] = True
    state.add_romance("konan", 25)
    state.belonging += 1
    ui.pause()


def konan_date_2(state):
    ui.title("心动: 纸伞下")
    ui.story("""
她真的又来了。这一次,木叶下着雨。

「雨隐的人,不怕雨。」小南在门口撑开一把纸伞——
 用她的忍术折的,雨点落在上面,竟不濡湿,
「但今天,想试试『躲雨』是什么感觉。」

一把伞,两个人,沿着护城河慢慢走。

「长门走后,我以为我这一生,就是守着雨之国,
 守着他们两个的墓,守到最后一张纸化掉。」

雨声淅沥。她侧过头看你,琥珀色的眼睛里,
有什么东西正在解冻:

「是你那条命线,一直暖暖的,像谁在那头
 攥着不肯放。……鸣人,人的心,原来是折不坏的。」
""")
    state.flags["rom_konan_2"] = True
    state.add_romance("konan", 30)
    state.belonging += 2
    ui.pause()


def konan_confess(state):
    ui.title("告白: 第一万零一朵纸花")
    ui.story("""
战后。小南再一次出现在木叶大门,这次,
她的行囊比以往任何一次都大。

「雨隐的新政议会,今天正式接管了村务。」她望着你,
「我这个『天使』,终于可以退休了。」

「那接下来,去哪?」

「不知道。」她第一次露出近乎茫然的神情,
「守了半生的东西,忽然不需要我守了。」

「那就换一个守法。」你上前一步,从怀里取出
 那朵她很久以前折的向日葵——被你压在护额里,
 边角都磨圆了,「小南。我数过,你给弥彦和长门
 折了一万朵纸花。第一万零一朵——能不能,为我们折?」

「『我们』……?」

「嗯。为你和我。」

纸花从她的指间散开,漫天飞舞,像一场白色的樱吹雪。
她走进你张开的手臂里,声音轻得像纸落地:

「这一朵,要折得很慢很慢。……要折,一辈子。」
""")
    _seal_love(state, "konan")


# ══════════════════ 琳 ══════════════════

def rin_date_1(state):
    ui.title("心动: 星空湖的夜钓")
    ui.story("""
桃源的星空湖边,琳不知从哪翻出两根钓竿。

「带土以前总吹牛说会钓鱼,结果一条都没钓到过。」
她把鱼饵挂好,递给你一根,「来,陪我验证一下,
 是鱼的问题,还是宇智波的问题。」

一个时辰过去,两个人一条都没钓到。

「……结论:是鱼的问题。」她一本正经地宣布,
你们对视一眼,一起笑倒在草地上。

星空湖把整条银河都盛在水里。她躺在草地上,
忽然说:「鸣人,谢谢你。把我从海底捞上来的时候,
 我以为等着我的是审判——结果是钓鱼。」

「桃源的规矩。」你说,「回家的人,只需要休息。」
""")
    state.flags["rom_rin_1"] = True
    state.add_romance("rin", 25)
    state.belonging += 1
    ui.pause()


def rin_date_2(state):
    ui.title("心动: 一起做药丸")
    ui.story("""
药草田边的工坊里,琳系着围裙,郑重其事:

「今天,传授你野原家秘制兵粮丸的做法。
 学不会,不许吃晚饭。」

结果你把药材配比记错了三次,把药碾打翻了一次,
最后揉出来的药丸,形状可疑地像只青蛙。

「噗——」琳绷不住了,笑得直不起腰,
「你、你这个……哈哈哈哈,文太看了要绝交的!」

「那这颗给你。」你把「青蛙」塞进她手心。

她捧着那颗歪歪扭扭的药丸看了很久,忽然低下头,
声音软软的:

「……舍不得吃了,怎么办。」

窗外的药草田,花开得正好。
""")
    state.flags["rom_rin_2"] = True
    state.add_romance("rin", 30)
    state.belonging += 2
    ui.pause()


def rin_confess(state):
    ui.title("告白: 药草田的花开了")
    ui.story("""
战争结束后的桃源,药草田开出了从未见过的花——
淡紫色的小花,一直蔓延到星空湖边。

「这花叫什么?」琳蹲在田埂上,眼睛亮晶晶的。

「不知道。桃源自己长的。」你在她身边蹲下,
「大地母亲说,桃源的景色,随住在这里的人的心变化。」

「那这片花,是谁的心?」

「我的。」

她转过头来。你迎着她的目光,把想了很久的话说完:

「琳姐。你是第二条命线,是桃源的药香,是把带土
 从黑暗里牵回来的那双手。这一世我救回了很多人,
 但只有你——是我每次推开桃源的门,第一眼想找的人。」

风吹过药草田,淡紫色的花浪一直涌到天边。

她笑了,眼泪却先掉下来。她伸出手,轻轻碰了碰
你心口的印记——第二条命线,亮得像一颗小星星。

「我死过一次,」她说,「所以我最知道,『活着』
 最好的用法,就是和喜欢的人,把每一天过满。

 ——鸣人,我也是。第一眼想找的,也是你。」
""")
    _seal_love(state, "rin")


# ══════════════════ 定情 ══════════════════

def _seal_love(state, who):
    """定情:记录恋人,其余命线温柔收束。"""
    state.flags["lover"] = who
    state.romance[who] = 100
    name = NAMES[who]
    state.gain_fate(3, "命运唯一的答案")
    state.belonging += 5
    ui.slow_print(f"※ 归属感 +5 [当前: {state.belonging}]")
    ui.banner(f"❀ 定情: {name} ❀")
    ui.story(f"""
当夜,桃源的契约之树下,九条命线一齐轻轻亮了一下——
像整个家,都在为这个答案眨眼睛。

玖辛奈笑着抹眼泪,说要开始准备「那个仪式」;
其余的命线依旧温暖,只是从此,各自安放:
是家人,是战友,是这一世不散的羁绊。

而属于{name}的那一条,从今往后,
是牵在手心里的,唯一的红线。
""")
    ui.pause()


def romance_status(state):
    """查看心动值(供状态页调用)。"""
    lover = state.flags.get("lover", "")
    if lover:
        return f"  ❀ 恋人: {NAMES.get(lover, lover)}"
    lines = [f"{NAMES[k]} {v}" for k, v in state.romance.items() if v > 0]
    return ("  ❀ 心动: " + " | ".join(lines)) if lines else ""
