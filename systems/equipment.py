# -*- coding: utf-8 -*-
"""忍具装备、解锁条件与套装加成。"""
from systems import ui


SLOTS = ("weapon", "armor", "accessory")
SLOT_NAMES = {"weapon": "武器", "armor": "防具", "accessory": "饰品"}
QUALITY_ORDER = ("common", "fine", "epic", "legendary")
QUALITY_NAMES = {"common": "普通", "fine": "精良", "epic": "史诗", "legendary": "传说"}
QUALITY_MULTIPLIERS = {"common": 1.0, "fine": 1.12, "epic": 1.25, "legendary": 1.4}

AFFIXES = {
    "power": {"name": "锋锐", "bonuses": {"power_mult": 1.06}},
    "guard": {"name": "坚守", "bonuses": {"incoming_mult": 0.94}},
    "swift": {"name": "轻灵", "bonuses": {"chakra_cost_mult": 0.95}},
    "breaker": {"name": "破阵", "bonuses": {"break_mult": 1.1}},
    "medic": {"name": "回春", "bonuses": {"item_heal_mult": 1.15}},
    "bond": {"name": "同心", "bonuses": {"ally_mult": 1.1}},
    "reaction": {"name": "共鸣", "bonuses": {"reaction_mult": 1.15}},
    "seal": {"name": "封术", "bonuses": {"effect_chance": 0.06}},
}

CATALOG = {
    "kunai_kit": {"name": "制式苦无包", "slot": "weapon", "description": "体术威力 +8%",
                  "bonuses": {"taijutsu_mult": 1.08}, "unlock": lambda s: True},
    "chakra_blade": {"name": "查克拉短刀", "slot": "weapon", "description": "忍术威力 +10%",
                      "bonuses": {"ninjutsu_mult": 1.1}, "unlock": lambda s: s.flags["chunin_done"]},
    "spiral_gauntlet": {"name": "螺旋护腕", "slot": "weapon", "description": "风遁威力和破势 +12%",
                         "bonuses": {"wind_mult": 1.12, "break_mult": 1.12}, "set": "nine_line",
                         "unlock": lambda s: "rasengan" in s.player["skills"]},
    "hunter_blade": {"name": "追猎忍刀", "slot": "weapon", "description": "全部攻击威力 +12%",
                     "bonuses": {"power_mult": 1.12}, "reward_only": True},
    "genin_vest": {"name": "下忍防护衣", "slot": "armor", "description": "受到伤害 -5%",
                    "bonuses": {"incoming_mult": 0.95}, "unlock": lambda s: True},
    "medic_coat": {"name": "医疗班外套", "slot": "armor", "description": "道具治疗 +25%，受到伤害 -5%",
                   "bonuses": {"item_heal_mult": 1.25, "incoming_mult": 0.95},
                   "unlock": lambda s: s.flags["tsunade_done"]},
    "nine_thread_cloak": {"name": "九命织衣", "slot": "armor", "description": "受到伤害 -10%，防御效果增强",
                           "bonuses": {"incoming_mult": 0.9, "guard_mult": 0.85}, "set": "nine_line",
                           "unlock": lambda s: sum(c["unlocked"] for c in s.contracts.values()) >= 6},
    "serpent_guard": {"name": "蛇鳞护甲", "slot": "armor", "description": "受到伤害 -12%",
                      "bonuses": {"incoming_mult": 0.88}, "reward_only": True},
    "seal_charm": {"name": "漩涡封印符", "slot": "accessory", "description": "异常触发率和封印能力提高",
                   "bonuses": {"effect_chance": 0.12}, "set": "nine_line",
                   "unlock": lambda s: s.flags["kushina_contacted"]},
    "wind_talisman": {"name": "风切御守", "slot": "accessory", "description": "元素反应伤害 +25%",
                      "bonuses": {"reaction_mult": 1.25},
                      "unlock": lambda s: "rasenshuriken" in s.player["skills"]},
    "bond_token": {"name": "第七班纪念章", "slot": "accessory", "description": "队友协战伤害 +15%",
                   "bonuses": {"ally_mult": 1.15}, "unlock": lambda s: s.flags["team7_assigned"]},
    "war_emblem": {"name": "联军功勋章", "slot": "accessory", "description": "队友伤害和破势 +20%",
                   "bonuses": {"ally_mult": 1.2, "break_mult": 1.2}, "reward_only": True},
    "tempered_kunai": {"name": "百炼苦无组", "slot": "weapon", "description": "全部攻击威力 +8%，破势 +8%",
                        "bonuses": {"power_mult": 1.08, "break_mult": 1.08}, "craft_only": True},
    "chakra_mail": {"name": "查克拉锁甲", "slot": "armor", "description": "受到伤害 -10%，忍术消耗 -5%",
                    "bonuses": {"incoming_mult": 0.9, "chakra_cost_mult": 0.95}, "craft_only": True},
    "medic_charm": {"name": "医疗御守", "slot": "accessory", "description": "道具治疗 +35%",
                    "bonuses": {"item_heal_mult": 1.35}, "craft_only": True},
    "will_of_fire_charm": {"name": "火之意志护符", "slot": "accessory",
                           "description": "队友伤害 +20%，契约支援更稳定",
                           "bonuses": {"ally_mult": 1.2, "effect_chance": 0.08}, "reward_only": True},
    "suna_guard_mail": {"name": "砂之守护甲", "slot": "armor",
                        "description": "受到伤害 -14%，防御效果增强",
                        "bonuses": {"incoming_mult": 0.86, "guard_mult": 0.9}, "reward_only": True},
    "alliance_chakra_blade": {"name": "联军查克拉刃", "slot": "weapon",
                              "description": "全部攻击和破势 +15%",
                              "bonuses": {"power_mult": 1.15, "break_mult": 1.15}, "reward_only": True},
    "explosive_kunai": {"name": "爆裂苦无组", "slot": "weapon", "description": "体术与元素反应 +12%",
                         "bonuses": {"taijutsu_mult": 1.12, "reaction_mult": 1.12}, "craft_only": True},
    "poison_senbon": {"name": "医毒千本匣", "slot": "weapon", "description": "忍术 +8%，异常率提高",
                       "bonuses": {"ninjutsu_mult": 1.08, "effect_chance": 0.1}, "craft_only": True},
    "puppet_blade": {"name": "傀儡机关刃", "slot": "weapon", "description": "攻击 +14%，破势 +10%",
                      "bonuses": {"power_mult": 1.14, "break_mult": 1.1}, "craft_only": True},
    "sage_staff": {"name": "妙木仙杖", "slot": "weapon", "description": "忍术 +15%，查克拉消耗 -8%",
                    "bonuses": {"ninjutsu_mult": 1.15, "chakra_cost_mult": 0.92}, "craft_only": True},
    "paper_fan": {"name": "式纸战扇", "slot": "weapon", "description": "风遁和异常触发强化",
                  "bonuses": {"wind_mult": 1.16, "effect_chance": 0.08}, "craft_only": True},
    "forest_cloak": {"name": "森行斗篷", "slot": "armor", "description": "受到伤害 -8%，道具治疗 +10%",
                     "bonuses": {"incoming_mult": 0.92, "item_heal_mult": 1.1}, "craft_only": True},
    "sandweave_armor": {"name": "砂织护甲", "slot": "armor", "description": "受到伤害 -12%，防御强化",
                        "bonuses": {"incoming_mult": 0.88, "guard_mult": 0.9}, "craft_only": True},
    "sage_robe": {"name": "仙术修行衣", "slot": "armor", "description": "受到伤害 -8%，忍术消耗 -10%",
                  "bonuses": {"incoming_mult": 0.92, "chakra_cost_mult": 0.9}, "craft_only": True},
    "paper_mantle": {"name": "纸翼披风", "slot": "armor", "description": "受到伤害 -9%，队友伤害 +12%",
                     "bonuses": {"incoming_mult": 0.91, "ally_mult": 1.12}, "craft_only": True},
    "war_plate": {"name": "联军复合甲", "slot": "armor", "description": "受到伤害 -15%，破势强化",
                  "bonuses": {"incoming_mult": 0.85, "break_mult": 1.12}, "craft_only": True},
    "tracking_lens": {"name": "感知目镜", "slot": "accessory", "description": "异常触发和队友行动强化",
                      "bonuses": {"effect_chance": 0.1, "ally_mult": 1.08}, "craft_only": True},
    "toxin_charm": {"name": "百毒御守", "slot": "accessory", "description": "治疗 +20%，受到伤害 -5%",
                    "bonuses": {"item_heal_mult": 1.2, "incoming_mult": 0.95}, "craft_only": True},
    "frog_charm": {"name": "妙木蛙御守", "slot": "accessory", "description": "忍术与元素反应 +12%",
                   "bonuses": {"ninjutsu_mult": 1.12, "reaction_mult": 1.12}, "craft_only": True},
    "rain_amulet": {"name": "雨隐纸花坠", "slot": "accessory", "description": "风遁 +12%，队友伤害 +15%",
                    "bonuses": {"wind_mult": 1.12, "ally_mult": 1.15}, "craft_only": True},
    "fate_compass": {"name": "命运罗盘", "slot": "accessory", "description": "破势和元素反应 +18%",
                     "bonuses": {"break_mult": 1.18, "reaction_mult": 1.18}, "craft_only": True},
}


def sync_unlocks(state):
    for item_id, item in CATALOG.items():
        if item.get("reward_only") or item.get("craft_only"):
            continue
        if item["unlock"](state) and item_id not in state.owned_equipment:
            state.owned_equipment.append(item_id)
            ui.slow_print(f"★ 忍具解锁：【{item['name']}】")
    normalize_equipment(state)


def grant(state, item_id, quality="common"):
    if item_id in CATALOG and item_id not in state.owned_equipment:
        state.owned_equipment.append(item_id)
        state.equipment_quality[item_id] = quality if quality in QUALITY_ORDER else "common"
        state.equipment_enhancements[item_id] = 0
        ui.slow_print(f"★ 获得装备：【{CATALOG[item_id]['name']}】")


def normalize_equipment(state):
    state.owned_equipment = list(dict.fromkeys(item for item in state.owned_equipment if item in CATALOG))
    state.equipment_quality = {
        item_id: quality if quality in QUALITY_ORDER else "common"
        for item_id, quality in state.equipment_quality.items()
        if item_id in state.owned_equipment
    }
    state.equipment_enhancements = {
        item_id: max(0, min(5, int(level)))
        for item_id, level in state.equipment_enhancements.items()
        if item_id in state.owned_equipment
    }
    state.equipment_affixes = {
        item_id: affix for item_id, affix in state.equipment_affixes.items()
        if item_id in state.owned_equipment and affix in AFFIXES
    }
    for item_id in state.owned_equipment:
        state.equipment_quality.setdefault(item_id, "common")
        state.equipment_enhancements.setdefault(item_id, 0)
    for slot in SLOTS:
        item_id = state.equipped_gear.get(slot, "")
        if item_id not in state.owned_equipment or CATALOG.get(item_id, {}).get("slot") != slot:
            replacement = next(
                (owned for owned in state.owned_equipment if CATALOG[owned]["slot"] == slot),
                "",
            )
            state.equipped_gear[slot] = replacement
    return state.equipped_gear


def combat_bonuses(state):
    normalize_equipment(state)
    bonuses = {
        "power_mult": 1.0, "taijutsu_mult": 1.0, "ninjutsu_mult": 1.0, "wind_mult": 1.0,
        "incoming_mult": 1.0, "guard_mult": 1.0, "item_heal_mult": 1.0,
        "reaction_mult": 1.0, "break_mult": 1.0, "ally_mult": 1.0, "effect_chance": 0.0,
        "chakra_cost_mult": 1.0,
    }
    set_counts = {}
    for item_id in state.equipped_gear.values():
        item = CATALOG.get(item_id)
        if not item:
            continue
        quality_scale = QUALITY_MULTIPLIERS[state.equipment_quality.get(item_id, "common")]
        upgrade_scale = 1 + state.equipment_enhancements.get(item_id, 0) * 0.08
        scale = quality_scale * upgrade_scale
        item_bonuses = dict(item.get("bonuses", {}))
        affix = AFFIXES.get(state.equipment_affixes.get(item_id))
        if affix:
            for key, value in affix["bonuses"].items():
                if key == "effect_chance":
                    item_bonuses[key] = item_bonuses.get(key, 0.0) + value
                else:
                    item_bonuses[key] = item_bonuses.get(key, 1.0) * value
        for key, value in item_bonuses.items():
            if key == "effect_chance":
                bonuses[key] += value * scale
            else:
                effective = 1 + (value - 1) * scale
                bonuses[key] *= max(0.5, effective)
        if item.get("set"):
            set_counts[item["set"]] = set_counts.get(item["set"], 0) + 1
    if set_counts.get("nine_line", 0) >= 2:
        bonuses["chakra_cost_mult"] *= 0.9
    if set_counts.get("nine_line", 0) >= 3:
        bonuses["break_mult"] *= 1.2
        bonuses["reaction_mult"] *= 1.2
    return bonuses


def apply_to_skill(skill, bonuses):
    adjusted = dict(skill)
    multiplier = bonuses["power_mult"]
    if adjusted.get("type") == "taijutsu":
        multiplier *= bonuses["taijutsu_mult"]
    else:
        multiplier *= bonuses["ninjutsu_mult"]
    if adjusted.get("element") == "wind":
        multiplier *= bonuses["wind_mult"]
    adjusted["power"] = max(0, int(adjusted.get("power", 0) * multiplier))
    adjusted["chakra_cost"] = max(0, int(adjusted.get("chakra_cost", 0) * bonuses["chakra_cost_mult"]))
    adjusted["_break_mult"] = adjusted.get("_break_mult", 1.0) * bonuses["break_mult"]
    adjusted["_reaction_mult"] = adjusted.get("_reaction_mult", 1.0) * bonuses["reaction_mult"]
    adjusted["_effect_chance"] = min(
        1.0,
        adjusted.get("_effect_chance", 0.6) + bonuses["effect_chance"],
    )
    return adjusted


def summary(state):
    normalize_equipment(state)
    parts = []
    for slot in SLOTS:
        item_id = state.equipped_gear.get(slot)
        parts.append(equipment_label(state, item_id) if item_id in CATALOG else "无")
    return " / ".join(parts)


def equipment_label(state, item_id):
    if item_id not in CATALOG:
        return "无"
    quality = QUALITY_NAMES[state.equipment_quality.get(item_id, "common")]
    level = state.equipment_enhancements.get(item_id, 0)
    affix = AFFIXES.get(state.equipment_affixes.get(item_id))
    affix_text = f"·{affix['name']}" if affix else ""
    return f"[{quality}] {CATALOG[item_id]['name']} +{level}{affix_text}"


def configure_equipment(state):
    sync_unlocks(state)
    while True:
        options = ["完成装备配置"] + [
            f"{SLOT_NAMES[slot]} | "
            f"{equipment_label(state, state.equipped_gear[slot]) if state.equipped_gear.get(slot) else '未装备'}"
            for slot in SLOTS
        ]
        index = ui.choose("忍具装备", options)
        if index == 0:
            return
        slot = SLOTS[index - 1]
        owned = [item_id for item_id in state.owned_equipment if CATALOG[item_id]["slot"] == slot]
        item_index = ui.choose(
            f"选择{SLOT_NAMES[slot]}",
            [
                f"{'◉' if state.equipped_gear.get(slot) == item_id else '○'} "
                f"{equipment_label(state, item_id)} - {CATALOG[item_id]['description']}"
                for item_id in owned
            ],
            allow_cancel=True,
        )
        if item_index >= 0:
            state.equipped_gear[slot] = owned[item_index]
            ui.slow_print(f"※ 已装备【{CATALOG[owned[item_index]]['name']}】。")
