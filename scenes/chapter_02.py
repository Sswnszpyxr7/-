# -*- coding: utf-8 -*-
"""第二章:铃铛测试 —— 与卡卡西的战斗,团队合作机制。"""
from systems import battle, quest, ui


def bell_test(state):
    ui.title("剧情: 铃铛测试")
    ui.story("""
清晨的第七训练场。

「呦,各位早。」卡卡西迟到了整整三个小时,
举着那本《亲热天堂》慢悠悠地出现,
「路上遇到一只黑猫,所以绕了远路。」

「骗人!!」小樱怒吼。

卡卡西从口袋里掏出两只铃铛,叮铃作响。

「规则很简单——中午之前,从我手里抢到铃铛。
 抢不到的人,没有午饭,而且会被送回忍者学校。」

「铃铛只有两只哦。」

佐助的眼神冷了下来。小樱紧张地咽了口唾沫。

只有鸣人,平静地看着那两只铃铛。

——铃铛只有两只,但答案从来只有一个:团队合作。
""")
    ui.pause()
    idx = ui.choose("测试开始前,你——", [
        "悄悄告诉佐助和小樱:「这个测试的答案是三个人合作。」",
        "什么都不说,打算在战斗中用行动引导他们",
        "直接冲上去单挑卡卡西(按原剧情)",
    ])
    teamwork_seed = False
    if idx == 0:
        ui.story("""
趁卡卡西看书的间隙,鸣人压低声音:

「听我说——铃铛只有两只,是故意的。
 这个测试考的不是抢铃铛,是我们三个能不能配合。」

「你怎么知道?」小樱狐疑。

「上忍带队测试的淘汰率是66%,但第七班每年都存在。
 想想看,为什么偏偏是『两只铃铛给三个人』?」

佐助眯起眼,没说话——但战斗开始时,
他的站位,悄悄和鸣人形成了掎角之势。
""")
        teamwork_seed = True
        state.add_trust(5)
        state.exposure += 4
    elif idx == 1:
        ui.story("""
鸣人握紧拳头,没有多说。

有些事,说出来会显得奇怪。
但战斗中的一次援护、一声提醒,胜过千言万语。
""")
    else:
        ui.story("""
「我要正大光明地跟你决斗!」

鸣人像前世一样嗷嗷叫着冲了上去——
好吧,有些戏还是要演的,而且……他确实想试试,
现在的自己和这位老师之间还差多远。
""")
    ui.pause()

    # ── 战斗:特殊规则 ──
    def extra_actions(log):
        acts = []
        if not log["teamwork"]:
            acts.append("呼唤配合(向佐助和小樱发出信号)")
        acts.append("尝试抢夺铃铛")
        return acts

    def action_handler(label, st, player, enemy, log):
        if label.startswith("呼唤配合"):
            base = 0.45 + st.team7_trust * 0.02 + (0.3 if teamwork_seed else 0)
            import random
            if random.random() < base:
                log["teamwork"] = True
                ui.story("""
「佐助!左边!小樱,准备替身!」

千钧一发之际,佐助的火球从侧翼呼啸而至,
小樱的替身术为鸣人挡住了背后的偷袭!

三个人的动作第一次咬合在一起,像真正的忍者小队!
""")
                enemy["hp"] -= 60
                ui.slow_print("  卡卡西被打乱了节奏,受到 60 点伤害!")
                ui.slow_print("  (卡卡西的独眼里,闪过一丝真正的惊讶。)")
            else:
                ui.story("""
「佐助!配合我!」

「谁要跟你配合。」佐助独自冲了出去,被土遁拖入地下只剩一个脑袋。

(信任还不够……但你的呼喊,他们都听见了。)
""")
                st.add_trust(2)
            return True
        if label == "尝试抢夺铃铛":
            import random
            chance = 0.15 + (0.35 if log["teamwork"] else 0) + player["speed"] * 0.005
            if random.random() < chance:
                log["bell_grabbed"] = True
                ui.story("""
就是现在!

卡卡西的注意力被分散的一瞬间,鸣人矮身、突进、伸手——

叮铃。

清脆的铃铛声,在他掌心响起。
""")
            else:
                ui.slow_print("→ 你扑向铃铛,却被卡卡西轻巧地闪开了。「忍者的第一课:体术。」")
                dmg = max(1, int(enemy["attack"] * 0.6))
                player["hp"] -= dmg
                ui.slow_print(f"  被反击,受到 {dmg} 点伤害!")
            return True
        return False

    def win_condition(st, player, enemy, turn, log):
        if log.get("bell_grabbed"):
            return "bell"
        if log["teamwork"] and turn >= 4:
            return "teamwork"
        if enemy["hp"] <= enemy["max_hp"] * 0.55:
            return "impressed"
        return None

    result = battle.battle(
        state, "kakashi_bell_test",
        special_rules={
            "extra_actions": extra_actions,
            "action_handler": action_handler,
            "win_condition": win_condition,
            "objective_text": "夺取铃铛、完成团队配合，或迫使卡卡西认真应战",
            "no_escape": True,
            "max_turns": 10,
            "timeout_result": "survived",
        },
        intro="卡卡西合上书,把铃铛系在腰间。「那么——开始。」",
    )

    # ── 结算 ──
    ui.line("═")
    if result == "lose":
        ui.story("""
最后一击把鸣人掀翻在地。

「唔……」他挣扎着爬起来,却发现面前伸来一只手。

「体术、忍术都还差得远,」卡卡西把他拉起来,
「但你在战斗里一直在观察同伴的位置——这一点,合格了。」
""")
    elif result == "bell":
        ui.story("""
「哦?」卡卡西看着鸣人掌心的铃铛,独眼弯了起来。

「从我手里抢到铃铛的下忍,你是第一个。」

鸣人把铃铛抛给了佐助,又冲小樱眨眨眼:
「给你们。我嘛……大不了回学校再念一年。」

风掠过训练场。卡卡西静静看着这一幕,很久,很久。

「合格。」他说,「你们三个,全部合格。」
""")
        state.add_trust(10)
        state.gain_fate(2, "完美的铃铛测试")
    elif result == "teamwork":
        ui.story("""
中午的钟声响起。

三个人瘫倒在草地上,谁也没抢到铃铛。

「铃铛,一只都没抢到呢。」卡卡西俯视着他们,
「不过——最后那次三人配合,是谁的主意?」

佐助和小樱不约而同看向鸣人。

「忍者世界里,违反规则的人被称为废物。」
卡卡西的独眼弯成温柔的弧度,
「但是,不珍惜同伴的人,连废物都不如。」

「你们,合格了。」
""")
        state.add_trust(8)
        state.gain_fate(1, "唤醒了团队之魂")
    else:
        ui.story("""
「时间到。」卡卡西收起铃铛。

「虽然结果不完美——但你们每个人,都在战斗中
 有过保护同伴的瞬间。这就够了。」

「第七班,合格。」
""")
        state.add_trust(5)

    if state.kakashi_suspicion >= 50:
        ui.story("""
……解散后,卡卡西站在树梢上,若有所思地目送鸣人离开。

「那小子……」

(卡卡西怀疑值已经很高,他开始认真调查鸣人了。)
""")
        state.add_backlash(1, "过于醒目的表现")

    state.flags["bell_test_completed"] = True
    quest.complete_quest(state, "bell_test")
    ui.story("""
(第七班正式成立了。)

夜幕降临。回家的路上,鸣人只觉得眼皮越来越沉,
心口的九瓣印记,微微地发起热来……

(回鸣人家休息,将触发重要剧情。)
""")
    ui.pause()
