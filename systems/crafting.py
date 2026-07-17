# -*- coding: utf-8 -*-
"""探索素材、忍具锻造与炼药。"""
import random

from systems import equipment, factions, icon_assets, ui


MATERIALS = {
    "木材", "铁砂", "查克拉晶片", "药草", "毒囊", "兽骨", "起爆黏土",
    "优质布", "封印墨", "自然结晶", "纸纤维",
}

LOCATION_MATERIALS = {
    "konoha_forest": (("木材", 4), ("药草", 4), ("兽骨", 2), ("优质布", 1)),
    "forest_of_death": (("药草", 3), ("毒囊", 3), ("兽骨", 2), ("查克拉晶片", 1), ("封印墨", 1)),
    "suna_village": (("铁砂", 5), ("兽骨", 2), ("起爆黏土", 1), ("优质布", 2)),
    "myoboku": (("药草", 4), ("自然结晶", 3), ("木材", 1), ("查克拉晶片", 2)),
    "war_front": (("铁砂", 3), ("查克拉晶片", 3), ("起爆黏土", 2), ("纸纤维", 2)),
}

ENEMY_DROPS = {
    "forest_wolf": ("兽骨", 0.65),
    "giant_snake": ("毒囊", 0.55),
    "training_dummy": ("木材", 0.2),
    "deidara": ("起爆黏土", 1.0),
    "sasori": ("毒囊", 1.0),
    "pain_deva": ("纸纤维", 0.8),
    "obito_masked": ("封印墨", 0.8),
    "madara_final": ("自然结晶", 1.0),
}

RECIPES = {
    "tempered_kunai": {"name": "锻造·百炼苦无组", "category": "forge",
                         "materials": {"铁砂": 3, "木材": 1}, "equipment": "tempered_kunai",
                         "unlock": lambda s: s.chapter >= 2},
    "chakra_mail": {"name": "锻造·查克拉锁甲", "category": "forge",
                     "materials": {"铁砂": 5, "查克拉晶片": 3}, "equipment": "chakra_mail",
                     "unlock": lambda s: s.flags.get("chunin_done", False)},
    "medic_charm": {"name": "锻造·医疗御守", "category": "forge",
                     "materials": {"药草": 4, "查克拉晶片": 2}, "equipment": "medic_charm",
                     "unlock": lambda s: s.flags.get("tsunade_done", False)},
    "healing_pill": {"name": "炼药·回复丹", "category": "alchemy",
                      "materials": {"药草": 2}, "item": "回复丹", "count": 1,
                      "unlock": lambda s: True},
    "chakra_pill": {"name": "炼药·查克拉丸", "category": "alchemy",
                     "materials": {"药草": 1, "查克拉晶片": 1}, "item": "查克拉丸", "count": 1,
                     "unlock": lambda s: s.chapter >= 2},
    "antidote": {"name": "炼药·解毒丸", "category": "alchemy",
                  "materials": {"药草": 1, "毒囊": 1}, "item": "解毒丸", "count": 2,
                  "unlock": lambda s: s.chapter >= 3},
    "revival_elixir": {"name": "炼药·复苏秘药", "category": "alchemy",
                        "materials": {"药草": 3, "查克拉晶片": 2, "毒囊": 1},
                        "item": "复苏秘药", "count": 1,
                        "unlock": lambda s: s.flags.get("tsunade_done", False)},
    "explosive_kunai": {"name": "锻造·爆裂苦无组", "category": "forge",
                         "materials": {"铁砂": 3, "起爆黏土": 2}, "equipment": "explosive_kunai",
                         "ryo": 450, "unlock": lambda s: s.chapter >= 3},
    "poison_senbon": {"name": "锻造·医毒千本匣", "category": "forge",
                       "materials": {"铁砂": 2, "毒囊": 3, "封印墨": 1}, "equipment": "poison_senbon",
                       "ryo": 550, "unlock": lambda s: s.flags.get("tsunade_done", False)},
    "puppet_blade": {"name": "锻造·傀儡机关刃", "category": "forge",
                      "materials": {"铁砂": 4, "兽骨": 3, "起爆黏土": 1}, "equipment": "puppet_blade",
                      "ryo": 650, "unlock": lambda s: s.flags.get("kazekage_done", False)},
    "sage_staff": {"name": "锻造·妙木仙杖", "category": "forge",
                    "materials": {"木材": 4, "自然结晶": 4, "封印墨": 2}, "equipment": "sage_staff",
                    "ryo": 850, "unlock": lambda s: s.flags.get("sage_training_done", False)},
    "paper_fan": {"name": "锻造·式纸战扇", "category": "forge",
                   "materials": {"纸纤维": 5, "铁砂": 2, "封印墨": 2}, "equipment": "paper_fan",
                   "ryo": 800, "unlock": lambda s: s.flags.get("konan_contracted", False)},
    "forest_cloak": {"name": "缝制·森行斗篷", "category": "forge",
                      "materials": {"优质布": 3, "木材": 2, "药草": 2}, "equipment": "forest_cloak",
                      "ryo": 350, "unlock": lambda s: s.chapter >= 2},
    "sandweave_armor": {"name": "锻造·砂织护甲", "category": "forge",
                         "materials": {"优质布": 4, "铁砂": 5}, "equipment": "sandweave_armor",
                         "ryo": 650, "unlock": lambda s: s.flags.get("shippuden_started", False)},
    "sage_robe": {"name": "缝制·仙术修行衣", "category": "forge",
                   "materials": {"优质布": 4, "自然结晶": 3, "药草": 2}, "equipment": "sage_robe",
                   "ryo": 800, "unlock": lambda s: s.flags.get("sage_training_done", False)},
    "paper_mantle": {"name": "缝制·纸翼披风", "category": "forge",
                      "materials": {"纸纤维": 6, "优质布": 3, "封印墨": 2}, "equipment": "paper_mantle",
                      "ryo": 850, "unlock": lambda s: s.flags.get("konan_contracted", False)},
    "war_plate": {"name": "锻造·联军复合甲", "category": "forge",
                  "materials": {"铁砂": 7, "查克拉晶片": 4, "优质布": 3}, "equipment": "war_plate",
                  "ryo": 1100, "unlock": lambda s: s.flags.get("summit_done", False)},
    "tracking_lens": {"name": "制作·感知目镜", "category": "forge",
                       "materials": {"查克拉晶片": 3, "铁砂": 2, "封印墨": 2}, "equipment": "tracking_lens",
                       "ryo": 500, "unlock": lambda s: s.chapter >= 5},
    "toxin_charm": {"name": "制作·百毒御守", "category": "forge",
                    "materials": {"毒囊": 3, "药草": 4, "封印墨": 1}, "equipment": "toxin_charm",
                    "ryo": 550, "unlock": lambda s: s.flags.get("tsunade_done", False)},
    "frog_charm": {"name": "制作·妙木蛙御守", "category": "forge",
                   "materials": {"自然结晶": 3, "木材": 2, "封印墨": 2}, "equipment": "frog_charm",
                   "ryo": 700, "unlock": lambda s: s.flags.get("sage_training_done", False)},
    "rain_amulet": {"name": "制作·雨隐纸花坠", "category": "forge",
                    "materials": {"纸纤维": 4, "查克拉晶片": 2, "封印墨": 2}, "equipment": "rain_amulet",
                    "ryo": 750, "unlock": lambda s: s.flags.get("pain_done", False)},
    "fate_compass": {"name": "制作·命运罗盘", "category": "forge",
                     "materials": {"自然结晶": 4, "查克拉晶片": 5, "封印墨": 3}, "equipment": "fate_compass",
                     "ryo": 1200, "unlock": lambda s: s.flags.get("war_done", False)},
    "strong_ration": {"name": "炼药·强效军粮丸", "category": "alchemy",
                      "materials": {"药草": 2, "兽骨": 1}, "item": "强效军粮丸", "count": 2,
                      "ryo": 120, "unlock": lambda s: s.chapter >= 2},
    "focus_pill": {"name": "炼药·凝神丸", "category": "alchemy",
                   "materials": {"药草": 2, "自然结晶": 1}, "item": "凝神丸", "count": 1,
                   "ryo": 180, "unlock": lambda s: s.flags.get("sage_training_done", False)},
}

SHOPS = {
    "konoha": {
        "locations": {"hokage_office", "konoha_hospital", "konoha_gate"},
        "faction": "konoha",
        "stock": {"药草": 45, "木材": 35, "优质布": 80, "封印墨": 100,
                  "军粮丸": 70, "回复丹": 140, "查克拉丸": 160},
    },
    "suna": {
        "locations": {"suna_village"}, "faction": "suna",
        "stock": {"铁砂": 55, "兽骨": 50, "优质布": 75, "起爆黏土": 130,
                  "军粮丸": 75, "查克拉丸": 150},
    },
    "alliance": {
        "locations": {"war_front"}, "faction": "alliance",
        "stock": {"铁砂": 50, "查克拉晶片": 130, "纸纤维": 100, "自然结晶": 180,
                  "回复丹": 120, "复苏秘药": 400},
    },
}


def material_summary(state):
    return "、".join(f"{name}×{state.inventory.get(name, 0)}" for name in sorted(MATERIALS))


def _weighted_choice(entries, rng):
    names = [name for name, _ in entries]
    weights = [weight for _, weight in entries]
    if hasattr(rng, "choices"):
        return rng.choices(names, weights=weights, k=1)[0]
    return random.choices(names, weights=weights, k=1)[0]


def gather_material(state, location_id=None, rng=None):
    location_id = location_id or state.location
    entries = LOCATION_MATERIALS.get(location_id)
    if not entries:
        ui.slow_print("这里没有适合采集的素材。")
        return None
    randomizer = rng or random
    material = _weighted_choice(entries, randomizer)
    amount = 2 if randomizer.random() < 0.2 else 1
    state.add_item(material, amount, cap=99)
    factions.record_progress(state, "gather", material, amount)
    ui.slow_print(f"※ 采集完成：{material}×{amount}。")
    return material


def award_battle_material(state, enemy_id, rng=None):
    randomizer = rng or random
    material, chance = ENEMY_DROPS.get(enemy_id, ("查克拉晶片", 0.12))
    if randomizer.random() >= chance:
        return None
    state.add_item(material, 1, cap=99)
    factions.record_progress(state, "gather", material, 1)
    return material


def can_craft(state, recipe_id):
    recipe = RECIPES.get(recipe_id)
    if not recipe or not recipe["unlock"](state):
        return False
    if recipe.get("equipment") in state.owned_equipment:
        return False
    return state.ryo >= recipe.get("ryo", 0) and all(
        state.inventory.get(name, 0) >= count for name, count in recipe["materials"].items()
    )


def _roll_quality(rng=None):
    roll = (rng or random).random()
    if roll < 0.03:
        return "legendary"
    if roll < 0.15:
        return "epic"
    if roll < 0.45:
        return "fine"
    return "common"


def craft(state, recipe_id, rng=None):
    recipe = RECIPES.get(recipe_id)
    if not recipe or not recipe["unlock"](state):
        return False
    if recipe.get("equipment") in state.owned_equipment:
        ui.slow_print("这件忍具已经锻造过了。")
        return False
    missing = {
        name: count - state.inventory.get(name, 0)
        for name, count in recipe["materials"].items()
        if state.inventory.get(name, 0) < count
    }
    if missing:
        ui.slow_print("素材不足：" + "、".join(f"{name}缺{count}" for name, count in missing.items()))
        return False
    if state.ryo < recipe.get("ryo", 0):
        ui.slow_print(f"资金不足：还需要 {recipe.get('ryo', 0) - state.ryo} 两。")
        return False
    for name, count in recipe["materials"].items():
        state.inventory[name] -= count
    if recipe.get("ryo"):
        state.spend_ryo(recipe["ryo"], "制作费用")
    if recipe.get("equipment"):
        quality = _roll_quality(rng)
        equipment.grant(state, recipe["equipment"], quality=quality)
        ui.slow_print(f"※ 成品品质：【{equipment.QUALITY_NAMES[quality]}】")
    else:
        state.add_item(recipe["item"], recipe.get("count", 1), cap=99)
    ui.slow_print(f"★ 制作完成：【{recipe['name']}】")
    return True


def _shop_for_location(state):
    return next(
        (shop for shop in SHOPS.values() if state.location in shop["locations"]),
        None,
    )


def _shop_discount(state, faction_id):
    rep = state.faction_reputation.get(faction_id, 0)
    if rep >= 140:
        return 0.2
    if rep >= 90:
        return 0.15
    if rep >= 50:
        return 0.1
    if rep >= 20:
        return 0.05
    return 0.0


def buy_item(state, name, base_price, faction_id, count=1):
    discount = _shop_discount(state, faction_id)
    price = max(1, int(base_price * count * (1 - discount)))
    if not state.spend_ryo(price, "商店购买"):
        ui.slow_print("两数不足。")
        return False
    state.add_item(name, count, cap=99)
    return True


def sell_item(state, name, base_price, count=1):
    if state.inventory.get(name, 0) < count:
        return False
    state.inventory[name] -= count
    state.gain_ryo(max(1, base_price * count // 2), "出售物资")
    return True


def shop_menu(state):
    shop = _shop_for_location(state)
    if not shop:
        ui.slow_print("当前位置没有开放的忍具商店。木叶办公室、医院、大门、砂隐和联军前线可交易。")
        return
    faction_id = shop["faction"]
    discount = int(_shop_discount(state, faction_id) * 100)
    while True:
        index = ui.choose(
            f"物资商店 | 持有 {state.ryo} 两 | 声望折扣 {discount}%",
            ["返回", "购买物资", "出售素材"],
        )
        if index == 0:
            return
        if index == 1:
            names = list(shop["stock"])
            item_index = ui.choose(
                "购买什么?",
                [f"{name} | {int(shop['stock'][name] * (1 - discount / 100))} 两" for name in names],
                allow_cancel=True,
            )
            if item_index >= 0:
                buy_item(state, names[item_index], shop["stock"][names[item_index]], faction_id)
        else:
            names = [name for name in MATERIALS if state.inventory.get(name, 0) > 0]
            if not names:
                ui.slow_print("没有可出售的素材。")
                continue
            item_index = ui.choose(
                "出售一份素材",
                [f"{name} ×{state.inventory[name]} | 售价 {shop['stock'].get(name, 60) // 2} 两" for name in names],
                allow_cancel=True,
            )
            if item_index >= 0:
                sell_item(state, names[item_index], shop["stock"].get(names[item_index], 60))


def upgrade_equipment(state, item_id):
    equipment.normalize_equipment(state)
    if item_id not in state.owned_equipment:
        return False
    level = state.equipment_enhancements.get(item_id, 0)
    if level >= 5:
        ui.slow_print("该忍具已强化至 +5。")
        return False
    iron_cost = level + 1
    crystal_cost = 1 if level >= 2 else 0
    ryo_cost = 180 * (level + 1)
    if state.inventory.get("铁砂", 0) < iron_cost or state.inventory.get("查克拉晶片", 0) < crystal_cost:
        ui.slow_print(f"强化需要铁砂×{iron_cost}、查克拉晶片×{crystal_cost}。")
        return False
    if not state.spend_ryo(ryo_cost, "忍具强化"):
        return False
    state.inventory["铁砂"] -= iron_cost
    state.inventory["查克拉晶片"] = state.inventory.get("查克拉晶片", 0) - crystal_cost
    state.equipment_enhancements[item_id] = level + 1
    ui.slow_print(f"★ {equipment.CATALOG[item_id]['name']}强化至 +{level + 1}！")
    return True


def refine_quality(state, item_id):
    quality = state.equipment_quality.get(item_id, "common")
    index = equipment.QUALITY_ORDER.index(quality)
    if index >= len(equipment.QUALITY_ORDER) - 1:
        ui.slow_print("该忍具已达到传说品质。")
        return False
    crystal_cost = 2 + index * 2
    ryo_cost = 400 + index * 350
    if state.inventory.get("自然结晶", 0) < crystal_cost:
        ui.slow_print(f"品质精炼需要自然结晶×{crystal_cost}。")
        return False
    if not state.spend_ryo(ryo_cost, "品质精炼"):
        return False
    state.inventory["自然结晶"] -= crystal_cost
    new_quality = equipment.QUALITY_ORDER[index + 1]
    state.equipment_quality[item_id] = new_quality
    ui.slow_print(f"★ 品质提升至【{equipment.QUALITY_NAMES[new_quality]}】！")
    return True


def reforge_affix(state, item_id, rng=None):
    if state.inventory.get("查克拉晶片", 0) < 2 or not state.spend_ryo(300, "词缀重铸"):
        ui.slow_print("重铸需要 300 两与查克拉晶片×2。")
        return False
    state.inventory["查克拉晶片"] -= 2
    affix_id = (rng or random).choice(list(equipment.AFFIXES))
    state.equipment_affixes[item_id] = affix_id
    ui.slow_print(f"★ 获得词缀【{equipment.AFFIXES[affix_id]['name']}】！")
    return True


def dismantle_equipment(state, item_id):
    if item_id not in state.owned_equipment or item_id in ("kunai_kit", "genin_vest"):
        return False
    if item_id in state.equipped_gear.values():
        ui.slow_print("请先卸下该忍具。")
        return False
    recipe = next((recipe for recipe in RECIPES.values() if recipe.get("equipment") == item_id), None)
    returned = recipe.get("materials", {"铁砂": 2}) if recipe else {"铁砂": 2}
    for name, count in returned.items():
        state.add_item(name, max(1, count // 2), cap=99)
    state.gain_ryo(100 + state.equipment_enhancements.get(item_id, 0) * 80, "拆解回收")
    state.owned_equipment.remove(item_id)
    state.equipment_quality.pop(item_id, None)
    state.equipment_enhancements.pop(item_id, None)
    state.equipment_affixes.pop(item_id, None)
    ui.slow_print(f"※ 已拆解【{equipment.CATALOG[item_id]['name']}】。")
    return True


def equipment_workbench(state):
    equipment.normalize_equipment(state)
    while True:
        options = ["返回"] + [equipment.equipment_label(state, item_id) for item_id in state.owned_equipment]
        index = ui.choose(f"忍具精炼台 | {state.ryo} 两", options)
        if index == 0:
            return
        item_id = state.owned_equipment[index - 1]
        action = ui.choose(
            equipment.equipment_label(state, item_id),
            [
                ui.Choice("返回", ("actions", "retreat")),
                ui.Choice("强化等级", ("actions", "train")),
                ui.Choice("提升品质", ("actions", "status")),
                ui.Choice("重铸词缀", ("actions", "workshop")),
                ui.Choice("拆解回收", ("actions", "gather")),
            ],
        )
        if action == 1:
            upgrade_equipment(state, item_id)
        elif action == 2:
            refine_quality(state, item_id)
        elif action == 3:
            reforge_affix(state, item_id)
        elif action == 4:
            dismantle_equipment(state, item_id)


def _recipe_menu(state, category):
    recipes = [
        recipe_id for recipe_id, recipe in RECIPES.items()
        if recipe["category"] == category and recipe["unlock"](state)
    ]
    while True:
        options = [ui.Choice("返回", ("actions", "retreat"))]
        for recipe_id in recipes:
            recipe = RECIPES[recipe_id]
            costs = "、".join(f"{name}×{count}" for name, count in recipe["materials"].items())
            money = f"、{recipe.get('ryo', 0)}两" if recipe.get("ryo") else ""
            ready = "可制作" if can_craft(state, recipe_id) else "条件不足/已拥有"
            if recipe.get("equipment"):
                asset = ("equipment", recipe["equipment"])
            else:
                item_id = next(
                    (key for key, name in icon_assets.ITEM_NAMES.items() if name == recipe.get("item")),
                    "item",
                )
                asset = ("items", item_id) if item_id != "item" else ("actions", "item")
            options.append(ui.Choice(recipe["name"], asset, f"{costs}{money}", ready))
        index = ui.choose(f"持有 {state.ryo} 两 | 素材：{material_summary(state)}", options)
        if index == 0:
            return
        craft(state, recipes[index - 1])


def workshop_menu(state):
    while True:
        options = [
            ui.Choice("返回", ("actions", "retreat")),
            ui.Choice("忍具锻造", ("actions", "workshop")),
            ui.Choice("炼药", ("actions", "item")),
            ui.Choice("忍具精炼/强化/重铸/拆解", ("actions", "loadout")),
            ui.Choice("物资商店", ("items", "ryo_coin")),
        ]
        index = ui.choose(f"忍具工坊 | {state.ryo} 两 | 素材：{material_summary(state)}", options)
        if index == 0:
            return
        if index == 1:
            _recipe_menu(state, "forge")
        elif index == 2:
            _recipe_menu(state, "alchemy")
        elif index == 3:
            equipment_workbench(state)
        elif index == 4:
            shop_menu(state)
