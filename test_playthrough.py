# -*- coding: utf-8 -*-
"""自动化冒烟测试:模拟输入跑通全部主线(第一部+疾风传+真结局)。

用法: python test_playthrough.py
"""
import builtins
import atexit
import os
import random
import shutil
import sys
import tempfile

os.environ["NL_FAST"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

random.seed(42)

from scenes import chapter_01, chapter_02, chapter_03, events, rin_arc
from systems import battle, contract, fate, save, tougen, ui
from systems.state import GameState

# 始终使用临时存档目录，避免覆盖/删除玩家的 save_01.json。
TEST_SAVE_DIR = tempfile.mkdtemp(prefix="nine_lives_playthrough_")
save.set_save_dir(TEST_SAVE_DIR)
atexit.register(shutil.rmtree, TEST_SAVE_DIR, ignore_errors=True)

# ── 输入桩 ──────────────────────────────
def fake_input(prompt=""):
    print(f"{prompt}<enter>")
    return "1"


builtins.input = fake_input

# ── 剧本路由:按(匹配串, 选项串)依次消费;否则走默认策略 ──
SCRIPT = []
_skill_pick = {"n": 0}


def routed_choose(prompt, options, allow_cancel=False):
    _ = allow_cancel
    text = prompt or ""
    for i, (match, pick) in enumerate(SCRIPT):
        if match in text or any(match in o for o in options):
            SCRIPT.pop(i)
            for j, o in enumerate(options):
                if pick in o:
                    print(f"[choose] {text[:18]} -> {o[:30]}")
                    return j
            break
    # 默认策略
    for j, o in enumerate(options):
        if o.startswith("以言语共鸣"):
            return j
    if options and all("威力" in o for o in options):  # 技能菜单: 螺旋丸/体术交替,防查克拉耗尽死循环
        _skill_pick["n"] += 1
        if _skill_pick["n"] % 2 == 0:
            for j, o in enumerate(options):
                if o.startswith("螺旋丸"):
                    return j
        return 0
    for j, o in enumerate(options):
        if o == "忍术/体术":
            return j
    return 0


ui.choose = routed_choose
battle.ui.choose = routed_choose


def cheat(state, level, extra_def=10):
    """把鸣人调整到指定等级的合理属性(冒烟测试用)。"""
    p = state.player
    p["level"] = level
    p["max_hp"] = 120 + 15 * level
    p["max_chakra"] = 150 + 12 * level
    p["attack"] = 18 + 3 * level
    p["defense"] = 16 + 2 * level + extra_def
    p["speed"] = 14 + 2 * level
    p["spirit"] = 22 + 2 * level
    p["hp"] = p["max_hp"]
    p["chakra"] = p["max_chakra"]


state = GameState()

print("\n===== 1. 开场 =====")
chapter_01.intro(state)
assert state.flags["intro_done"]

print("\n===== 2. 分班日 =====")
state.location = "ninja_academy"
SCRIPT.append(("伊鲁卡走上讲台", "主动向佐助"))
chapter_01.assignment_day(state)
assert state.flags["team7_assigned"]
assert state.fate_points >= 1

print("\n===== 3. 对话佐助/小樱 =====")
chapter_01.talk_sasuke(state)
chapter_01.talk_sakura(state)
assert state.flags["talked_sasuke"] and state.flags["talked_sakura"]

print("\n===== 4. 抵达训练场 =====")
state.location = "training_ground_7"
chapter_01.arrive_training_ground(state)
assert state.quests["team7_restart"]["completed"]

print("\n===== 5. 铃铛测试 =====")
chapter_02.bell_test(state)
assert state.flags["bell_test_completed"]
assert state.quests["bell_test"]["completed"]

print("\n===== 6. 桃源觉醒 + 玖辛奈契约 =====")
chapter_03.tougen_awakening(state)
assert state.flags["tougen_unlocked"] and state.flags["kushina_contacted"]
assert state.contracts["kushina"]["unlocked"]
assert state.contracts["kushina"]["contract_level"] == 1
assert state.chapter == 2

print("\n===== 7. 桃源: 休息/修炼/契约升级 =====")
tougen.rest(state)
assert state.player["hp"] == state.player["max_hp"]
tougen.train(state)
state.fate_points = 10
SCRIPT.append(("消耗", "提升"))
contract.inspect_contract(state, state.contracts["kushina"])
assert state.contracts["kushina"]["contract_level"] == 2
assert state.player["max_hp"] > 120  # lv2 同心: 生命上限+20

print("\n===== 8. 命运回廊 =====")
fate.show_fate_corridor(state)

print("\n===== 9. 契约支援战斗 =====")
cheat(state, 4)
SCRIPT.append(("你的行动", "契约支援"))
result = battle.battle(state, "forest_wolf")
print("battle result:", result)
assert result in ("win", "lose")

print("\n===== 10. 存档/读档 =====")
save.save_game(state, 1)
state2 = GameState()
assert save.load_game(state2, 1)
assert state2.flags["tougen_unlocked"]
assert state2.contracts["kushina"]["contract_level"] == 2
assert state2.relations["sasuke"]["trust"] == state.relations["sasuke"]["trust"]

print("\n===== 11. 事件调度器 =====")
state2.location = "hokage_office"
acts = events.get_location_actions(state2)
assert any("波之国" in a[0] for a in acts), "第二章应有波之国任务入口"
state2.location = "hokage_rock"
for _label, h in events.get_location_actions(state2):
    h(state2)
assert state2.flags["rasengan_learned"]

print("\n===== 12. 数据完整性 =====")
for eid, e in state.enemies_db.items():
    for sk in e["skills"]:
        assert sk in state.skills_db, f"{eid} missing skill {sk}"
for sk in state.player["skills"]:
    assert sk in state.skills_db, f"player missing skill {sk}"
for rid in tougen.RESEARCH:
    assert callable(tougen.RESEARCH[rid]["check"])
for bid in tougen.BUILDINGS:
    assert callable(tougen.BUILDINGS[bid]["check"])

print("\n===== 13. 波之国篇 (完美改写) =====")
from scenes import wave_country
cheat(state, 7)
state.fate_points = 12
state.location = "hokage_office"
SCRIPT.append(("面对白", "来木叶吧"))
SCRIPT.append(("两个都救", "两个都救"))
wave_country.start(state)
assert state.flags["wave_done"]
assert state.flags["haku_alive"] and state.flags["zabuza_alive"], "完美改写: 白与再不斩均存活"
assert state.flags["rin_light_found"]
assert state.quests["wave_mission"]["completed"]
assert state.quests["mist_remnant"]["completed"]
assert state.chapter == 3
SCRIPT.clear()

print("\n===== 14. 琳契约 + 医院支线 =====")
rin_arc.herb_garden_awakening(state)
assert state.contracts["rin"]["unlocked"]
assert state.contracts["rin"]["contract_level"] == 1
assert state.contracts["kushina"]["contract_level"] >= 2
assert state.quests["rin_contract"]["completed"]
rin_arc.hospital_photo(state)
assert state.flags["rin_photo_seen"]
rin_arc.rin_kakashi_hint(state)
assert state.flags["rin_kakashi_hint"]
rin_arc.sakura_hospital(state)  # 第三章: 长椅上的小樱
assert state.relations["sakura"]["medical"] >= 15
state.flags["herb_quest_active"] = True
state.add_item("药草", 3)
rin_arc.herb_quest_turn_in(state)
assert state.quests["herb_gathering"]["completed"]

print("\n===== 15. 忍术研究 + 桃源建设 =====")
for rid in ("multi_clone", "seal_array", "yang_heal"):
    state.research_done.append(rid)
    tougen._apply_research(state, rid)
assert "multi_shadow_clone" in state.player["skills"]
assert "simple_seal_array" in state.player["skills"]
assert "yang_heal" in state.player["skills"]
state.tougen_buildings += ["hot_spring", "medical_room", "herb_field", "tree_boost"]
assert contract.level_up_cost(state, 4) == 8  # (4+1)*2-2

print("\n===== 16. 中忍考试篇 → 木叶崩溃篇 (连续剧情) =====")
from scenes import chunin_exam
cheat(state, 13)
state.player["seal_art"] = max(state.player["seal_art"], 16)
state.fate_points += 10
state.contracts["kushina"]["contract_level"] = 5
state.contracts["rin"]["contract_level"] = 5
SCRIPT.append(("报名之后", "进言"))
SCRIPT.append(("千钧一发", "硬撼"))
SCRIPT.append(("拦在担架前", "拦在担架前"))
SCRIPT.append(("撞进结界", "撞进结界"))
# 我爱罗战前四场连战无回血点,第一回合先呼唤琳的联合技满血恢复
SCRIPT.append(("以言语共鸣", "契约支援"))
SCRIPT.append(("呼唤谁的力量", "温柔归命"))
chunin_exam.start(state)
assert state.flags["chunin_done"]
assert state.flags["warned_hokage"]
assert state.flags["curse_avoided"] and state.relations["sasuke"]["curse"] == 0
assert state.flags["gaara_bond"] >= 1
assert state.quests["chunin_exam"]["completed"]
assert state.flags["crush_done"]
assert state.flags["hiruzen_saved"], "命运改写: 三代火影存活"
assert state.flags["gaara_redeemed"], "我爱罗被感化"
assert state.quests["konoha_crush"]["completed"]
assert state.chapter == 5
SCRIPT.clear()

print("\n===== 17. 羁绊联合技 =====")
cheat(state, 13)
SCRIPT.append(("你的行动", "契约支援"))
SCRIPT.append(("呼唤谁的力量", "赤阳封命阵"))
result = battle.battle(state, "giant_snake")
print("combo battle result:", result)
assert result in ("win", "lose")
SCRIPT.clear()

print("\n===== 18. 寻找纲手篇 =====")
from scenes import tsunade_search
cheat(state, 16)
state.fate_points += 8
SCRIPT.append(("面对晓", "赌命"))
tsunade_search.start(state)
assert state.flags["tsunade_done"] and state.flags["tsunade_returned"]
assert state.flags["itachi_knows"]
assert state.flags["rasengan_official"]
assert "rasengan" in state.player["skills"]
assert "rasengan_incomplete" not in state.player["skills"]
assert state.has_building("medical_room")
assert state.flags["tsunade_tougen_invited"]
assert state.chapter == 6
assert state.quests["tsunade_search"]["completed"]
SCRIPT.clear()

print("\n===== 19. 纲手契约(第三契约) =====")
tsunade_search.visit_tsunade(state)
c = state.contracts["tsunade"]
assert contract.can_contract(c), f"纲手契约条件应满足: {c['affection']}/{c['trust']}/{c['safety']}/{c['fate_resonance']}"
contract.inspect_contract(state, c)
assert c["unlocked"] and c["contract_level"] == 1

print("\n===== 20. 章节间关系事件 =====")
rin_arc.sakura_hospital(state)  # 第五章: 医疗班见习生
state.location = "uchiha_ruins"
acts = events.get_location_actions(state)
assert acts, "第六章宇智波遗址应有剧情"
acts[0][1](state)
assert state.flags["sasuke_talk_c5"]

print("\n===== 21. 终结谷 (改命同盟结局) =====")
from scenes import sasuke_retrieval
cheat(state, 20)
state.fate_points += 8
state.relations["sasuke"].update({"trust": 65, "revenge": 60, "curse": 0})
state.relations["sakura"]["confidence"] = 50
sasuke_retrieval.night_event(state)
assert state.flags["sasuke_arc_done"]
assert state.flags["sasuke_ending"] == 4, f"应达成改命同盟结局, 实际 {state.flags['sasuke_ending']}"
assert state.flags["main_complete"]
assert state.chapter == 7
assert state.quests["valley_of_the_end"]["completed"]

print("\n===== 22. 尾声系统检查 =====")
fate.show_fate_corridor(state)   # 已定格的命运回望
import main as main_mod
hint = main_mod.chapter_hint(state)
assert "疾风传" in hint, f"第一部完结提示应指向疾风传: {hint}"
save.save_game(state, 1)
state3 = GameState()
assert save.load_game(state3, 1)
assert state3.flags["sasuke_ending"] == 4
assert state3.has_building("medical_room")
assert state3.contracts["tsunade"]["unlocked"]
assert "rasenshuriken" in state3.skills_db

print("\n===== 23. 疾风传·三年之约 + 风影夺还 =====")
from scenes import kazekage_rescue
cheat(state, 20)
state.fate_points = 15
SCRIPT.append(("修行的重心", "体术与实战"))
SCRIPT.append(("千代婆婆扑向卡卡西", "替卡卡西挡下"))
SCRIPT.append(("辅助转生术", "辅助转生术"))
kazekage_rescue.depart(state)
assert state.flags["shippuden_started"]
assert state.quests["timeskip_training"]["completed"]
assert state.flags["kazekage_done"]
assert state.flags["gaara_saved"], "命运改写: 我爱罗未死"
assert state.flags["chiyo_alive"], "命运改写: 千代存活"
assert state.contracts["sakura"]["unlocked"], "第四契约: 小樱"
assert state.quests["kazekage_rescue"]["completed"]
assert state.chapter == 8
SCRIPT.clear()

print("\n===== 24. 疾风传·晓之阴影 (阿斯玛/自来也改命 + 红契约) =====")
from scenes import akatsuki_shadow
cheat(state, 24)
state.fate_points = 15
akatsuki_shadow.start(state)
assert state.flags["akatsuki_done"]
assert state.flags["asuma_saved"], "命运改写: 阿斯玛存活"
assert state.flags["jiraiya_saved"], "命运改写: 自来也不再孤身赴死"
assert state.flags["pain_intel"] >= 3
assert state.flags["hinata_contracted"] and state.contracts["hinata"]["unlocked"]
assert state.quests["akatsuki_shadow"]["completed"]
assert state.chapter == 9
SCRIPT.clear()

print("\n===== 25. 疾风传·妙木山修行 + 静音契约 =====")
akatsuki_shadow.sage_training(state)
assert state.flags["sage_training_done"]
assert "sage_mode" in state.player["skills"]
assert "frog_kata" in state.player["skills"]
assert state.quests["sage_training"]["completed"]
akatsuki_shadow.shizune_bond(state)
assert state.flags["shizune_contracted"] and state.contracts["shizune"]["unlocked"]

print("\n===== 26. 疾风传·佩恩袭村 (长门/小南) =====")
from scenes import pain_assault
cheat(state, 28)
state.fate_points = 15
SCRIPT.append(("暴雨将至", "疏散"))
SCRIPT.append(("雏田", "影分身"))
pain_assault.start(state)
assert state.flags["pain_done"]
assert state.flags["village_evacuated"], "命运改写: 提前疏散"
assert state.flags["hinata_guarded"], "命运改写: 雏田未重伤"
assert state.flags["nagato_redeemed"], "长门转意"
assert state.flags["konan_contracted"] and state.contracts["konan"]["unlocked"]
assert state.quests["pain_assault"]["completed"]
assert state.chapter == 10
SCRIPT.clear()

print("\n===== 27. 疾风传·第四次忍界大战 (真结局) =====")
from scenes import fourth_war
cheat(state, 32)
state.fate_points = 20
# 契约等级拉满到6+,确保「九命同归」条件(>=6名契约者)可验证
for cid in ("kushina", "rin", "tsunade", "sakura", "shizune", "hinata", "konan"):
    state.contracts[cid]["contract_level"] = max(
        state.contracts[cid]["contract_level"], 6)
fourth_war.start(state)
assert state.flags["war_done"]
assert state.flags["summit_done"]
assert state.flags["kurama_friend"], "与九喇嘛和解"
assert "kurama_mode" in state.player["skills"]
assert state.flags["obito_redeemed"], "带土被琳唤回"
assert state.flags["mei_contracted"] and state.contracts["mei"]["unlocked"]
assert state.contracts["gaia"]["unlocked"], "第九契约: 大地母亲"
assert state.flags["infinite_tsukuyomi_stopped"], "无限月读被阻止"
assert state.flags["true_end"], (
    "真结局条件: nagato+obito+asuma+gaara+jiraiya+chiyo 全改命 "
    f"({state.flags['nagato_redeemed']},{state.flags['obito_redeemed']},"
    f"{state.flags['asuma_saved']},{state.flags['gaara_saved']},"
    f"{state.flags['jiraiya_saved']},{state.flags['chiyo_alive']})")
assert state.quests["fourth_war"]["completed"]
assert state.chapter >= 11
SCRIPT.clear()

print("\n===== 28. 疾风传尾声: 回廊/闲话/联合技/存档 =====")
fate.show_fate_corridor(state)
tougen.chat(state)
hint = main_mod.chapter_hint(state)
assert "自由模式" in hint
# 九命同归联合技可用性
state.contracts["mei"]["contract_level"] = 9
for cid in ("kushina", "rin", "tsunade", "sakura", "shizune", "hinata"):
    state.contracts[cid]["contract_level"] = 9
combos = [k for k, _, _, _ in battle._combo_list(state)]
assert "combo_ninelives" in combos, f"九命同归联合技应解锁: {combos}"
save.save_game(state, 1)
state4 = GameState()
assert save.load_game(state4, 1)
assert state4.flags["true_end"]
assert state4.contracts["gaia"]["unlocked"]
assert state4.flags["war_done"]
print("\n===== 29. 恋爱线 (雏田·定情) =====")
from scenes import romance
# 疾风传+契约已满足;两段约会积累心动
state.location = "training_ground_7"
acts = romance.get_romance_actions(state, "training_ground_7")
assert any("月下的组手" in a[0] for a in acts), f"雏田约会1应可用: {[a[0] for a in acts]}"
romance.hinata_date_1(state)
assert state.flags["rom_hinata_1"] and state.romance["hinata"] >= 25
acts = romance.get_romance_actions(state, "hokage_rock")
assert any("火影岩上" in a[0] for a in acts), "雏田约会2应可用"
romance.hinata_date_2(state)
assert state.romance["hinata"] >= 50
# war_done 已达成 → 可告白
acts = romance.get_romance_actions(state, "training_ground_7")
assert any("告白" in a[0] for a in acts), "雏田告白应可用"
romance.hinata_confess(state)
assert state.flags["lover"] == "hinata"
assert state.romance["hinata"] == 100
# 定情后其他人不可再告白
state.romance["sakura"] = 100
state.flags["rom_sakura_1"] = state.flags["rom_sakura_2"] = True
acts = romance.get_romance_actions(state, "konoha_hospital")
assert not any("告白" in a[0] for a in acts), "单恋人制: 定情后不应再有告白入口"
# 其余四人约会事件入口存在性(用干净状态验证)
_s = GameState()
_s.flags["shippuden_started"] = True
_s.flags["pain_done"] = True
for cid in ("sakura", "tsunade", "konan", "rin"):
    _s.contracts[cid]["unlocked"] = True
assert any("小樱" in a[0] for a in romance.get_romance_actions(_s, "konoha_hospital"))
assert any("纲手" in a[0] for a in romance.get_romance_actions(_s, "hokage_office"))
assert any("小南" in a[0] for a in romance.get_romance_actions(_s, "konoha_gate"))
assert any("琳" in a[0] for a in romance.get_tougen_romance_actions(_s))
# 恋人闲话与状态页
assert "雏田" in romance.romance_status(state)
tougen.chat(state)
# 存档往返
save.save_game(state, 1)
state5 = GameState()
assert save.load_game(state5, 1)
assert state5.flags["lover"] == "hinata"
assert state5.romance["hinata"] == 100

print("\n===== 30. 契约互动 + 九命共鸣 =====")
from scenes import bonding
# add_bond 封顶
state.contracts["hinata"]["affection"] = 95
contract.add_bond(state, "hinata", {"affection": 20})
assert state.contracts["hinata"]["affection"] == 100
# 谈心(直调;routed_choose 默认选 0 → 第一位契约者)
_belong = state.belonging
bonding.heart_talk(state, set())
assert state.belonging > _belong
# 送礼:偏好道具命中
state.inventory["药草"] = 2
state.contracts["rin"]["affection"] = 90
SCRIPT.append(("送给谁", "野原琳"))
SCRIPT.append(("送什么", "药草"))
bonding.give_gift(state)
assert state.inventory["药草"] == 1
assert state.contracts["rin"]["affection"] == 98, state.contracts["rin"]["affection"]
# 融合技研究与实战
assert tougen.RESEARCH["ninelives_fusion"]["check"](state)
state.research_done.append("ninelives_fusion")
tougen._apply_research(state, "ninelives_fusion")
assert "ninelives_fusion" in state.player["skills"]
assert battle._fusion_power(state) > 100, battle._fusion_power(state)  # 终局态威力成长
state.equipped_skills = ["basic_taijutsu", "ninelives_fusion"]
state.player["hp"] = state.player["max_hp"]
state.player["chakra"] = state.player["max_chakra"]
SCRIPT.append(("你的行动", "忍术/体术"))
SCRIPT.append(("使用哪个技能", "九命共鸣"))
result = battle.battle(state, "forest_wolf")
assert result in ("win", "lose"), result
SCRIPT.clear()
# banner 冒烟(全角居中)
ui.banner("测试横幅")
# 存档往返:融合技随 player 序列化
save.save_game(state, 1)
state6 = GameState()
assert save.load_game(state6, 1)
assert "ninelives_fusion" in state6.player["skills"]
os.remove(os.path.join(TEST_SAVE_DIR, "save_01.json"))

print("\n" + "=" * 46)
print("ALL TESTS PASSED ✓ 全部主线(第一部~疾风传·真结局+恋爱线)跑通!")
