# -*- coding: utf-8 -*-
"""游戏图标、徽章、通缉海报与 Boss 切入图的资源索引。"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ASSET_ROOT = ROOT / "assets"
ICON_ROOT = ASSET_ROOT / "icons"
WANTED_ROOT = ASSET_ROOT / "wanted"
BOSS_CUTIN_ROOT = ASSET_ROOT / "boss_cutins"


ELEMENT_NAMES = {
    "fire": "火",
    "wind": "风",
    "lightning": "雷",
    "water": "水",
    "earth": "土",
    "wood": "木",
    "yin": "阴",
    "yang": "阳",
    "seal": "封印",
    "medical": "医疗",
    "taijutsu": "体术",
    "genjutsu": "幻术",
    "tailed_beast": "尾兽",
}

STATUS_NAMES = {
    "burn": "灼烧",
    "paralyze": "麻痹",
    "poison": "中毒",
    "confuse": "混乱",
    "bleed": "流血",
    "spirit_shake": "精神动摇",
    "defense_up": "防御提升",
    "evade_up": "闪避提升",
    "clone_guard": "影分身护卫",
    "sealed": "封印",
    "cloak": "九尾外衣",
    "attack_up": "攻击提升",
    "nine_shield": "九命守护",
    "fear": "恐惧",
    "chakra_disorder": "查克拉紊乱",
    "wet": "湿润",
}

INTENT_NAMES = {
    "fatal": "致命攻击",
    "control": "控制招式",
    "support": "强化/恢复",
    "attack": "直接攻击",
}

REACTION_NAMES = {
    "douse": "水遁扑灭",
    "electrocharged": "感电",
    "steam_burst": "蒸汽爆发",
    "fan_flame": "风助火势",
    "mud_trap": "泥沼",
}

ACTION_NAMES = {
    "battle_start": "开始战斗",
    "attack": "忍术/体术",
    "guard": "防御/反击",
    "item": "使用道具",
    "contract": "契约支援",
    "retreat": "逃跑/退出",
    "position": "调整站位",
    "ally_order": "队友指令",
    "ally_ultimate": "队友奥义",
    "travel": "移动",
    "rest": "休息",
    "train": "锻炼",
    "explore": "深入探索",
    "gather": "采集素材",
    "observe": "观察四周",
    "visit": "拜访",
    "heart_talk": "个别谈心",
    "gift": "送礼",
    "contract_tree": "契约之树",
    "fate_corridor": "命运回廊",
    "training_court": "修炼庭院",
    "ninjutsu_research": "忍术研究",
    "tougen_build": "桃源建设",
    "quests": "任务",
    "status": "查看状态",
    "loadout": "战斗配置",
    "faction": "阵营声望",
    "workshop": "忍具工坊",
    "wanted": "通缉榜",
    "collection": "收藏馆",
    "new_cycle": "新周目挑战",
    "save": "保存游戏",
    "load": "读取游戏",
}

# 常见功能入口与动作图标的语义别名。旧场景仍可继续传纯字符串，GUI 也能
# 自动补上合适的图标；新代码优先使用 ui.Choice 显式绑定资源。
ACTION_ALIASES = {
    "个别谈心": "heart_talk",
    "送礼": "gift",
    "契约之树": "contract_tree",
    "命运回廊": "fate_corridor",
    "修炼庭院": "training_court",
    "忍术研究": "ninjutsu_research",
    "桃源建设": "tougen_build",
    "找佐助说话": "visit",
    "找小樱说话": "visit",
    "给卡卡西带一句话": "visit",
    "开始铃铛测试": "battle_start",
    "上床睡觉": "rest",
    "就寝": "rest",
    "报名中忍考试": "quests",
    "与自来也出发": "travel",
    "踏上三年修行之旅": "travel",
    "响应五影会谈召集": "quests",
    "眺望": "observe",
    "查看走廊尽头的老照片": "observe",
    "长椅上的小樱": "visit",
    "医疗班的见习生": "visit",
    "账房里的静音": "visit",
    "族地门口的佐助": "visit",
    "屋顶上的背影": "visit",
    "黄昏的训练场邀约": "visit",
    "驰援砂隐": "travel",
    "拜入蛤蟆仙人座下": "train",
    "【心动】": "contract",
    "【告白】": "contract",
    "调整技能": "loadout",
    "技能装备": "loadout",
    "忍术强化": "train",
    "忍具装备": "workshop",
    "调整同行者": "ally_order",
    "同行者": "ally_order",
    "队友培养": "ally_ultimate",
    "开始试炼": "battle_start",
    "现在就出发": "travel",
    "新的旅程": "new_cycle",
    "继续旅程": "load",
    "保存并退出": "save",
    "返回": "retreat",
    "取消": "retreat",
}

EQUIPMENT_NAMES = {
    "kunai_kit": "制式苦无包",
    "chakra_blade": "查克拉短刀",
    "spiral_gauntlet": "螺旋护腕",
    "hunter_blade": "追猎忍刀",
    "genin_vest": "下忍防护衣",
    "medic_coat": "医疗班外套",
    "nine_thread_cloak": "九命织衣",
    "serpent_guard": "蛇鳞护甲",
    "seal_charm": "漩涡封印符",
    "wind_talisman": "风切御守",
    "bond_token": "第七班纪念章",
    "war_emblem": "联军功勋章",
    "tempered_kunai": "百炼苦无组",
    "chakra_mail": "查克拉锁甲",
    "medic_charm": "医疗御守",
    "will_of_fire_charm": "火之意志护符",
    "suna_guard_mail": "砂之守护甲",
    "alliance_chakra_blade": "联军查克拉刃",
    "explosive_kunai": "爆裂苦无组",
    "poison_senbon": "医毒千本匣",
    "puppet_blade": "傀儡机关刃",
    "sage_staff": "妙木仙杖",
    "paper_fan": "式纸战扇",
    "forest_cloak": "森行斗篷",
    "sandweave_armor": "砂织护甲",
    "sage_robe": "仙术修行衣",
    "paper_mantle": "纸翼披风",
    "war_plate": "联军复合甲",
    "tracking_lens": "感知目镜",
    "toxin_charm": "百毒御守",
    "frog_charm": "妙木蛙御守",
    "rain_amulet": "雨隐纸花坠",
    "fate_compass": "命运罗盘",
}

ITEM_NAMES = {
    "ration_pill": "军粮丸",
    "healing_pill": "回复丹",
    "chakra_pill": "查克拉丸",
    "medicinal_herb": "药草",
    "antidote_pill": "解毒丸",
    "revival_elixir": "复苏秘药",
    "strong_ration": "强效军粮丸",
    "focus_pill": "凝神丸",
    "material_wood": "木材",
    "material_iron_sand": "铁砂",
    "material_chakra_shard": "查克拉晶片",
    "material_venom_sac": "毒囊",
    "material_beast_bone": "兽骨",
    "material_explosive_clay": "起爆黏土",
    "material_fine_cloth": "优质布",
    "material_seal_ink": "封印墨",
    "material_nature_crystal": "自然结晶",
    "material_paper_fiber": "纸纤维",
    "ryo_coin": "两",
}

AFFIX_NAMES = {
    "swift": "迅捷",
    "armored": "重甲",
    "berserk": "狂暴",
    "chakra": "查克拉充盈",
    "regenerative": "再生",
    "venomous": "剧毒",
    "gear_power": "锋锐",
    "gear_guard": "坚守",
    "gear_light": "轻灵",
    "gear_breaker": "破阵",
    "gear_medic": "回春",
    "gear_bond": "同心",
    "gear_reaction": "共鸣",
    "gear_seal": "封术",
}

CONTRACT_NAMES = {
    "kushina": "漩涡玖辛奈",
    "rin": "野原琳",
    "tsunade": "纲手",
    "sakura": "春野樱",
    "shizune": "静音",
    "hinata": "日向雏田",
    "konan": "小南",
    "mei": "照美冥",
    "gaia": "大地母亲",
}

ACHIEVEMENT_NAMES = {
    "first_action": "重生后的第一天",
    "event_hunter": "村子的倾听者",
    "world_walker": "足迹遍布",
    "full_loadout": "忍术师的工具箱",
    "two_companions": "我们一起上",
    "first_contract": "命线之始",
    "nine_contracts": "九命一系",
    "skill_scholar": "忍术研究者",
    "first_ending": "命运的岔路",
    "ending_collector": "命运收藏家",
    "true_end": "九命同归",
}

ENDING_NAMES = {
    "wave_canon": "波之国·原定命运",
    "wave_haku": "波之国·白的新生",
    "wave_perfect": "波之国·双生归途",
    "sasuke_canon": "终结谷·离村",
    "sasuke_promise": "终结谷·约定",
    "sasuke_guarded": "终结谷·监护下的木叶",
    "sasuke_alliance": "终结谷·改命同盟",
    "war_standard": "忍界大战·未尽的遗憾",
    "war_true": "忍界大战·九命同归",
}

WANTED_NAMES = {
    "forest_alpha": "森林狼王",
    "rogue_hunter": "越境猎忍",
    "serpent_king": "死亡森林蛇王",
    "red_cloud_agent": "赤云密使",
    "zetsu_commander": "白绝残党指挥体",
}

BOSS_META = {
    "zabuza_first": ("桃地再不斩", "zabuza", "wave_bridge", "#6db6d9", None),
    "haku_bridge": ("白", "haku", "wave_bridge", "#b9e8ff", None),
    "orochimaru_forest": ("大蛇丸", "orochimaru", "forest_of_death", "#9b72cf", None),
    "kiba_prelim": ("犬冢牙 & 赤丸", "kiba", "training_ground", "#d39b58", "akamaru"),
    "neji_final": ("日向宁次", "neji", "training_ground", "#d7d8ee", None),
    "gaara_berserk": ("我爱罗 (半兽化)", "gaara", "suna_village", "#d98c43", "shukaku"),
    "kabuto": ("药师兜", "kabuto", "konoha_forest", "#78d7cf", None),
    "sasuke_valley": ("宇智波佐助", "sasuke", "uchiha_ruins", "#766fe8", None),
    "sasuke_spar": ("宇智波佐助 (切磋)", "sasuke", "training_ground", "#629ce8", None),
    "deidara": ("迪达拉", "deidara", "suna_village", "#e8c14e", None),
    "sasori": ("赤砂之蝎", "sasori", "suna_village", "#cf4b4b", None),
    "hidan": ("飞段", "hidan", "konoha_forest", "#d34b63", None),
    "kakuzu": ("角都", "kakuzu", "konoha_forest", "#5fc08f", None),
    "pain_deva": ("佩恩·天道", "pain", "pain_ruins", "#b47be6", None),
    "obito_masked": ("带土 (面具之下)", "obito", "war_front", "#d97858", None),
    "madara_final": ("宇智波斑", "madara", "war_front", "#e34d4d", None),
}


def _load_skill_names():
    path = ROOT / "data" / "skills.json"
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    return {skill_id: skill["name"] for skill_id, skill in data.items()}


SKILL_NAMES = _load_skill_names()


def icon_path(category, asset_id):
    """返回指定类别图标路径。"""
    return ICON_ROOT / category / f"{asset_id}.png"


def wanted_path(target_id, thumbnail=False):
    folder = WANTED_ROOT / "thumbs" if thumbnail else WANTED_ROOT
    return folder / f"{target_id}.png"


def boss_cutin_path(enemy_id):
    return BOSS_CUTIN_ROOT / f"{enemy_id}.png"


def expected_icons():
    """枚举应存在的全部图标，供构建工具和测试共用。"""
    groups = {
        "elements": ELEMENT_NAMES,
        "status": STATUS_NAMES,
        "intents": INTENT_NAMES,
        "reactions": REACTION_NAMES,
        "actions": ACTION_NAMES,
        "equipment": EQUIPMENT_NAMES,
        "items": ITEM_NAMES,
        "affixes": AFFIX_NAMES,
        "contracts": CONTRACT_NAMES,
        "achievements": ACHIEVEMENT_NAMES,
        "endings": ENDING_NAMES,
        "skills": SKILL_NAMES,
    }
    for category, mapping in groups.items():
        for asset_id in mapping:
            yield category, asset_id, icon_path(category, asset_id)


def _match_named_asset(label, category, mapping):
    for asset_id, name in sorted(mapping.items(), key=lambda item: len(item[1]), reverse=True):
        if name and name in label:
            return category, asset_id
    return None


def option_asset(label):
    """根据 GUI 选项文本匹配最合适的图片资源。"""
    for category, mapping in (
        ("wanted", WANTED_NAMES),
        ("skills", SKILL_NAMES),
        ("equipment", EQUIPMENT_NAMES),
        ("items", ITEM_NAMES),
        ("contracts", CONTRACT_NAMES),
        ("affixes", AFFIX_NAMES),
        ("actions", ACTION_NAMES),
    ):
        match = _match_named_asset(label, category, mapping)
        if match:
            return match
    for phrase, asset_id in sorted(ACTION_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if phrase in label:
            return "actions", asset_id
    return None


def option_asset_path(label):
    match = option_asset(label)
    if not match:
        return None
    category, asset_id = match
    if category == "wanted":
        return wanted_path(asset_id, thumbnail=True)
    return icon_path(category, asset_id)
