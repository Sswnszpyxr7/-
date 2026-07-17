# -*- coding: utf-8 -*-
"""命运系统：命运点、命运反噬、命运回廊。"""
from systems import ui

BACKLASH_DESC = {
    0: "命运之河平稳流淌。",
    1: "小事件开始偏移原本的轨迹。",
    2: "敌人变得警觉，暗处有目光注视着木叶。",
    3: "命运的湍流加剧，战斗将更加艰难。",
    4: "剧情正在提前爆发，未来变得模糊。",
    5: "关键人物的死亡风险正在增加！",
    6: "世界线正在强制修正——命运在反抗你！",
}


def _fate_events(state):
    """命运回廊的光门列表: (标题, 提示/结果, 已定格?)。"""
    f = state.flags
    events = []

    if f["wave_done"]:
        if f["haku_alive"] and f["zabuza_alive"]:
            outcome = "雾散了。冰镜的少年与斩首刀的鬼，正走在通往木叶的路上。——完美改写"
        elif f["haku_alive"]:
            outcome = "雪落在大桥上。少年活了下来，替那个男人看着往后的世界。——半改写"
        else:
            outcome = "雪落满桥。两条命运沉入了雾中，一如原本的轨迹。"
        events.append(("波之国任务", outcome, True))
    else:
        events.append(("波之国任务", "雾中的桥，雪落之时，冰镜中映出两条即将消逝的生命……", False))

    if f["chunin_done"]:
        outcome = ("白蛇的毒牙没能刻下印记。可它的目光,转向了另一个更有趣的容器……"
                   if f["curse_avoided"] else
                   "咒印烙上了复仇者的脖颈。黑暗的种子已经埋下，能否发芽,取决于羁绊。")
        events.append(("中忍考试", outcome, True))
    elif state.chapter >= 3:
        events.append(("中忍考试", "草叶之下藏着白蛇，死亡森林里，咒印将烙上复仇者的脖颈……", False))

    if f["crush_done"]:
        outcome = ("烟斗的青烟仍在办公室里飘着。猿飞老师活了下来——命运第一次真正低头。"
                   if f["hiruzen_saved"] else
                   "旗帜低垂,细雨落满黑衣。三代火影的意志,由活着的人继承下去。")
        events.append(("木叶崩溃计划", outcome, True))
    elif state.chapter >= 3:
        events.append(("木叶崩溃计划", "沙与音的联军踏破城墙，猿与蛇在屋顶上做最后的对决……", False))

    if f["sasuke_arc_done"]:
        ending = f.get("sasuke_ending", 1)
        outcome = {
            1: "终结谷的水面,只剩一枚划伤的护额。他走向了蛇的巢穴。",
            2: "「三年。」少年留下约定离去。命运的丝线,并未完全断裂。",
            3: "他回到了村子。暗部的影子在他身后,但同伴的手一直伸着。",
            4: "两个少年在终结谷的石像上并肩而坐。改写命运的同盟,就此结成。",
        }[ending]
        events.append(("佐助离村", outcome, True))
    elif state.chapter >= 3:
        events.append(("佐助离村", "终结谷的瀑布轰鸣，两个少年的拳头即将相撞……", False))

    if state.chapter >= 5 and not f["shippuden_started"]:
        events.append(("晓之暗流", "赤云黑袍在黎明前移动。他们的目标,是所有的『尾』……", False))
    if f["main_complete"] and not f["shippuden_started"]:
        events.append(("红云与轮回", "三年后。带着轮回之瞳的「神」将从天而降。而那时的你,不再是一个人。", False))

    # ── 疾风传 ──
    if f["shippuden_started"]:
        if f["kazekage_done"]:
            if f["chiyo_alive"] and f["gaara_saved"]:
                outcome = "沙海的黎明。少年风影睁开眼时,老傀儡师就坐在他床边打盹。两条命,都留下了。——完美改写"
            elif f["gaara_saved"]:
                outcome = "我爱罗在万人的注视中醒来。而那双托起他的苍老的手,永远垂落在沙丘上。"
            else:
                outcome = "沙暴过后,风影的旗帜降了半旗。"
            events.append(("风影夺还", outcome, True))
        else:
            events.append(("风影夺还", "赤云掠过沙海,白色的巨鸟叼走了红发的少年风影……", False))

    if state.chapter >= 8:
        if f["akatsuki_done"]:
            parts = []
            parts.append("烟灰缸里的烟还燃着——阿斯玛活着回了家。" if f["asuma_saved"]
                         else "十班的少年们,在雨里接过了老师的将棋。")
            parts.append("雨之国的水声里,白发的身影仍在写他的书。——命线未断"
                         if f["jiraiya_saved"] else
                         "雨落满孤城。遗言化作暗号,刻在蛤蟆的背上。")
            events.append(("晓之阴影", " ".join(parts), True))
        else:
            events.append(("晓之阴影", "不死的镰刀正逼近十班;而雨之国深处,你师父的师父将孤身赴死……", False))

    if state.chapter >= 9:
        if f["pain_done"]:
            outcome = ("神俯下身,听见了「答案」。轮回之瞳选择了相信,纸之天使折起了新的花。——命运低头"
                       if f["nagato_redeemed"] else
                       "村子从瓦砾中重建。轮回天生的代价,由雨之国的亡魂偿还。")
            events.append(("天降之神", outcome, True))
        else:
            events.append(("天降之神", "六具躯体自雨云中降下,「神罗天征」将把木叶夷为平地……", False))

    if state.chapter >= 9 and f["pain_done"]:
        if f["war_done"]:
            outcome = ("红月碎裂。九条命线在黎明的天空下同时亮起——这一世,谁都没有被留在梦里。——九命同归"
                       if f["true_end"] else
                       "战争结束了。旗帜与墓碑一同立在焦土上。")
            events.append(("红月之战", outcome, True))
        else:
            events.append(("红月之战", "五影的旗帜将并立于铁之国。而月亮的背面,面具正在碎裂……", False))

    return events


def show_fate_corridor(state):
    ui.title("命运回廊")
    ui.story("""
长廊两侧漂浮着一扇扇朦胧的光门，
每一扇门后，都是一段尚未到来、或已被亲手定格的命运。
""")
    print(f"  ◆ 命运点 {state.fate_points}")
    print(f"  ▼ 命运反噬 Lv.{state.backlash} —— {BACKLASH_DESC[state.backlash]}")
    ui.line()

    events = _fate_events(state)
    free_peek = state.has_building("corridor_ext")
    opts = []
    for name, _, fixed in events:
        if fixed:
            opts.append(f"回望「{name}」——已定格的命运")
        else:
            opts.append(f"窥视「{name}」的命运碎片" + ("" if free_peek else " (消耗 1 命运点)"))
    if state.backlash > 0:
        opts.append("以命运点安抚命运之流 (消耗 2 命运点，反噬 -1)")
    idx = ui.choose("", opts, allow_cancel=True)
    if idx < 0:
        return
    if state.backlash > 0 and idx == len(events):
        if state.fate_points >= 2:
            state.fate_points -= 2
            state.backlash -= 1
            ui.slow_print("金色的命线轻轻抚平了命运之河的波澜……反噬等级降低了。")
        else:
            ui.slow_print("命运点不足。")
        return
    name, hint, fixed = events[idx]
    if fixed:
        ui.slow_print(f"你将手贴上「{name}」的光门。门中的景象已经安静地定格——")
        ui.slow_print(f"『{hint}』")
        ui.pause()
        return
    if not free_peek:
        if state.fate_points < 1:
            ui.slow_print("命运点不足，光门纹丝不动。")
            return
        state.fate_points -= 1
    ui.slow_print(f"你将手贴上「{name}」的光门——")
    ui.slow_print(f"『{hint}』")
    if free_peek:
        ui.slow_print("(扩建后的命运回廊中，命运的低语变得清晰而免费。)")
    else:
        ui.slow_print("(这些朦胧的预示，将在未来章节中成为改写命运的钥匙。)")
    ui.pause()
