# -*- coding: utf-8 -*-
"""地图探索系统：移动、地点事件、随机战斗。"""
import random

from systems import (
    battle,
    collection,
    crafting,
    equipment,
    factions,
    loadout,
    new_game_plus,
    party,
    skill_mastery,
    time_system,
    tougen,
    ui,
    visual_assets,
    wanted,
    world_events,
)


def show_location(state):
    loc = state.maps[state.location]
    ui.title(f"当前位置: {loc['name']} | {time_system.time_label(state)}")
    ui.slow_print(loc["description"])


def location_actions(state):
    """返回当前地点可用的额外行动 [(标签, 处理函数)]。"""
    from scenes import events
    return events.get_location_actions(state)


def _exit_allowed(state, dest):
    """部分地点需要剧情解锁。"""
    if dest == "forest_of_death":
        return state.flags["chunin_done"]
    if dest == "suna_village":
        return state.flags["shippuden_started"]
    if dest == "myoboku":
        return state.chapter >= 9
    if dest == "war_front":
        return state.flags["war_done"]
    return True


def explore_menu(state):
    """地点行动菜单，返回 True 表示继续主循环。"""
    loc = state.maps[state.location]
    actions = []

    for label, handler in location_actions(state):
        actions.append((label, handler))

    if loc["id"] == "tougen_gate":
        actions.append((ui.Choice("进入桃源", ("actions", "travel")), lambda s: tougen.enter_tougen(s)))
    if loc.get("can_rest") and loc["id"] != "tougen_gate":
        actions.append((ui.Choice("休息", ("actions", "rest"), "恢复部分生命和查克拉"), do_rest))
    if loc["id"] == "naruto_home":
        actions.append((ui.Choice("保存游戏", ("actions", "save"), "将当前进度写入存档"), do_save))
    if loc.get("can_train"):
        actions.append((ui.Choice("锻炼", ("actions", "train"), "与假想敌切磋"), do_train))
    if loc.get("random_battle"):
        actions.append((ui.Choice("深入探索", ("actions", "explore"), "可能遭遇战斗"), do_wander))
    if loc["id"] in crafting.LOCATION_MATERIALS:
        actions.append((ui.Choice("采集素材", ("actions", "gather"), "用于锻造与炼药"), do_gather))
    actions.append((ui.Choice("观察四周", ("actions", "observe"), "寻找地点见闻"), do_local_explore))

    actions.append((ui.Choice("移动到其他地点", ("actions", "travel")), do_move))
    actions.append((ui.Choice("查看状态", ("actions", "status")), show_status))
    actions.append((ui.Choice("查看任务", ("actions", "quests")), None))  # 特殊处理
    actions.append((ui.Choice("道具/菜单", ("actions", "item")), None))

    labels = [a[0] for a in actions]
    idx = ui.choose("要做什么?", labels)
    option, handler = actions[idx]
    label = ui.choice_label(option)
    if label == "查看任务":
        from systems import quest
        quest.show_quests(state)
    elif label == "道具/菜单":
        return system_menu(state)
    elif handler:
        handler(state)
    return True


def do_save(state):
    """鸣人家的直接存档入口。"""
    from systems import save
    save.save_menu(state)


def do_move(state):
    loc = state.maps[state.location]
    exits = [state.maps[e] for e in loc["exits"]
             if e in state.maps and _exit_allowed(state, e)]
    choices = []
    for destination in exits:
        illustration_id = visual_assets.illustration_for_location(destination["id"])
        asset = ("illustrations", illustration_id) if illustration_id else ("actions", "travel")
        choices.append(ui.Choice(destination["name"], asset))
    idx = ui.choose("前往哪里?", choices, allow_cancel=True)
    if idx < 0:
        return
    state.location = exits[idx]["id"]
    time_system.advance_time(state)
    show_location(state)
    # 触发地点进入事件
    from scenes import events
    events.on_enter(state)
    world_events.trigger_random_event(state)


def do_rest(state):
    p = state.player
    p["hp"] = min(p["max_hp"], p["hp"] + p["max_hp"] // 2)
    p["chakra"] = min(p["max_chakra"], p["chakra"] + p["max_chakra"] // 2)
    loc = state.maps[state.location]
    if loc["id"] == "ichiraku":
        ui.slow_print("一大碗热腾腾的豚骨拉面下肚，连心都暖了起来。")
        state.belonging += 1
    else:
        ui.slow_print("你好好休息了一会儿。")
    ui.slow_print("※ 恢复了一半生命与查克拉。")
    time_system.advance_time(state)


def do_train(state):
    ui.slow_print("你对着训练木桩开始挥拳——")
    result = battle.battle(state, "training_dummy")
    if result == "win":
        ui.slow_print("(基础的锻炼让身体逐渐找回前世的感觉。)")
    time_system.advance_time(state)


def do_wander(state):
    time_system.advance_time(state)
    loc = state.maps[state.location]
    # 找猫任务彩蛋
    if (loc["id"] == "konoha_forest"
            and not state.flags["cat_found"]
            and not state.quests["find_cat_tora"]["completed"]
            and state.quests["bell_test"]["completed"]
            and random.random() < 0.4):
        from systems import quest
        ui.story("""
草丛里传来窸窸窣窣的声音——一只系着红色蝴蝶结的猫窜了出来！
是大名夫人的宠物猫「虎」！

前世不知抓过多少次，鸣人对它的路数了如指掌。
你一个箭步绕到它逃跑路线的必经之处，稳稳把它抱了个正着。

「喵嗷——」猫在怀里徒劳地挣扎。
""")
        state.flags["cat_found"] = True
        quest.complete_quest(state, "find_cat_tora")
        return
    # 采药 (医院日常任务)
    if (state.flags["herb_quest_active"]
            and not state.quests["herb_gathering"]["completed"]
            and random.random() < 0.45):
        state.add_item("药草", 1)
        factions.record_progress(state, "gather", "药草", 1)
        n = state.inventory.get("药草", 0)
        ui.slow_print(f"你按护士长画的图谱找到了一株药草。(当前持有: {n} 株，凑齐 3 株后送回医院)")
        return
    if random.random() < 0.65:
        enemy_id = random.choice(loc.get("battle_pool", ["forest_wolf"]))
        result = battle.battle(state, enemy_id, special_rules={"allow_elite": True})
        if result == "lose":
            ui.story("""
眼前一黑……

醒来时，你发现自己躺在附近的草地上，浑身疼痛。
(战败了。回去休整一下吧。)
""")
            state.player["hp"] = max(1, state.player["max_hp"] // 4)
    else:
        cache_key = f"wander_cache:{loc['id']}"
        if not state.consume_daily_use(cache_key, limit=1):
            ui.slow_print("你沿着今天搜索过的路线又走了一遍，只找到一些空掉的补给袋。")
            return
        found = random.choice(["军粮丸", "回复丹", "查克拉丸"])
        state.add_item(found, 1, cap=9)
        ui.slow_print(f"你在林间搜寻了一番，找到了一枚【{found}】。（本地点今日补给已取）")


def do_local_explore(state):
    time_system.advance_time(state)
    factions.record_progress(state, "patrol", state.location, 1)
    world_events.trigger_random_event(state, force=True)


def do_gather(state):
    key = f"gather:{state.location}"
    if not state.consume_daily_use(key, limit=3):
        ui.slow_print("这片区域今天可采的素材已经不多了，明天再来吧。（每日最多采集 3 次）")
        return
    time_system.advance_time(state)
    crafting.gather_material(state)


def show_status(state):
    p = state.player
    ui.title("鸣人状态")
    print(f"  Lv.{p['level']}  经验 {p['exp']}/{state.exp_to_next()}")
    print(f"  时间 {time_system.time_label(state)} | 已行动 {state.actions_taken} 次")
    print(f"  {ui.stat_line('生命  ', p['hp'], p['max_hp'])}")
    print(f"  {ui.stat_line('查克拉', p['chakra'], p['max_chakra'])}")
    print(f"  攻击 {p['attack']} | 防御 {p['defense']} | 速度 {p['speed']} | 精神 {p['spirit']}")
    print(f"  感知 {p['sense']} | 查克拉控制 {p['chakra_control']} | 封印术 {p['seal_art']} | 命运力 {p['fate_power']}")
    ui.line()
    print("  ◆ 命运")
    print(f"  命运点 {state.fate_points} | 命运反噬 Lv.{state.backlash} | 暴露度 {state.exposure} | 九尾波动 {state.kyubi_flux}")
    print(f"  资金 {state.ryo} 两")
    print(f"  第七班信任 {state.team7_trust} | 卡卡西怀疑值 {state.kakashi_suspicion} | 归属感 {state.belonging}")
    ui.line()
    print("  ♥ 羁绊")
    sa = state.relations["sasuke"]
    sk = state.relations["sakura"]
    print(f"  [佐助] 信任 {sa['trust']} | 复仇执念 {sa['revenge']} | 咒印侵蚀 {sa['curse']}")
    print(f"         羁绊 {sa['team_bond']} | 孤立感 {sa['isolation']}")
    print(f"  [小樱] 自信 {sk['confidence']} | 医疗兴趣 {sk['medical']} | 信任 {sk['trust']}")
    print(f"         执念 {sk['sasuke_obsession']} | 责任感 {sk['responsibility']}")
    contracts = [c for c in state.contracts.values() if c["unlocked"]]
    if contracts:
        info = "、".join(f"{c['name']} Lv.{c['contract_level']}" for c in contracts)
        print(f"  契约: {info}")
    from scenes import romance
    rom_line = romance.romance_status(state)
    if rom_line:
        print(rom_line)
    ui.line()
    print("  ※ 技能与行囊")
    learned = [state.skills_db[s]["name"] for s in p["skills"] if s in state.skills_db]
    print(f"  已掌握: {'、'.join(learned)}")
    print(f"  已装备: {loadout.summary(state)}")
    print(f"  忍具: {equipment.summary(state)}")
    print(f"  同行者: {party.party_summary(state)}")
    party.normalize_progress(state)
    if state.selected_party:
        growth = "、".join(
            f"{party.TEAMMATES[tid][0]} Lv.{state.teammate_progress[tid]['level']}"
            f"/羁绊{state.teammate_progress[tid]['bond']}"
            f"/{next((route['name'] for route in party.TEAMMATE_ROUTES[tid] if route['id'] == state.teammate_progress[tid].get('route')), '未定路线')}"
            for tid in state.selected_party
        )
        print(f"  队友成长: {growth}")
    reputations = "、".join(
        f"{data['name']} {state.faction_reputation[fid]}({factions.reputation_rank(state.faction_reputation[fid])})"
        for fid, data in factions.FACTIONS.items() if data["unlock"](state)
    )
    print(f"  阵营声望: {reputations}")
    if state.new_game_plus:
        print(f"  新周目 +{state.new_game_plus} | 修正: {new_game_plus.modifier_summary(state)}")
    inv = "、".join(f"{k}×{v}" for k, v in state.inventory.items() if v > 0) or "无"
    print(f"  道具: {inv}")
    ui.line()
    ui.pause()


def system_menu(state):
    from systems import save
    idx = ui.choose(
        "系统菜单:",
        [
            ui.Choice("使用道具", ("actions", "item")),
            ui.Choice("战斗配置", ("actions", "loadout")),
            ui.Choice("动态委托/阵营声望", ("actions", "faction")),
            ui.Choice("忍具工坊/炼药", ("actions", "workshop")),
            ui.Choice("通缉榜", ("actions", "wanted")),
            ui.Choice("收藏馆", ("actions", "collection")),
            ui.Choice("新周目挑战", ("actions", "new_cycle")),
            ui.Choice("保存游戏", ("actions", "save")),
            ui.Choice("读取游戏", ("actions", "load")),
            ui.Choice("退出游戏", ("actions", "retreat")),
        ],
        allow_cancel=True,
    )
    if idx == 0:
        battle.use_item(state, state.player)
    elif idx == 1:
        _combat_setup_menu(state)
    elif idx == 2:
        factions.show_board(state)
    elif idx == 3:
        crafting.workshop_menu(state)
    elif idx == 4:
        wanted.show_wanted_board(state)
    elif idx == 5:
        collection.show_collection(state)
    elif idx == 6:
        new_game_plus.menu(state)
    elif idx == 7:
        save.save_menu(state)
    elif idx == 8:
        if save.load_menu(state):
            show_location(state)
    elif idx == 9:
        if ui.choose("确定退出? 当前进度将自动保存到存档 3。", ["取消", "退出"]) == 1:
            return False
    return True


def _combat_setup_menu(state):
    while True:
        index = ui.choose(
            "战斗配置",
            [
                ui.Choice("返回", ("actions", "retreat")),
                ui.Choice("技能装备", ("actions", "loadout"), loadout.summary(state)),
                ui.Choice("忍术强化", ("actions", "train"), skill_mastery.summary(state)),
                ui.Choice("忍具装备", ("actions", "workshop"), equipment.summary(state)),
                ui.Choice("同行者", ("actions", "ally_order"), party.party_summary(state)),
                ui.Choice("队友培养", ("actions", "ally_ultimate"), "路线与羁绊"),
            ],
        )
        if index == 0:
            return
        if index == 1:
            loadout.configure_loadout(state)
        elif index == 2:
            skill_mastery.configure_mastery(state)
        elif index == 3:
            equipment.configure_equipment(state)
        elif index == 4:
            party.configure_party(state)
        elif index == 5:
            party.growth_menu(state)
