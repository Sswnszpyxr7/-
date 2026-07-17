# -*- coding: utf-8 -*-
"""GUI 头像、场景插图与剧情文本的轻量映射。"""
from pathlib import Path
import re


ASSET_ROOT = Path(__file__).resolve().parent.parent / "assets"
PORTRAIT_ROOT = ASSET_ROOT / "portraits"
ILLUSTRATION_ROOT = ASSET_ROOT / "illustrations"


PORTRAITS = {
    name: f"{name}.png"
    for name in (
        "naruto", "sasuke", "sakura", "kakashi", "kushina", "minato", "rin",
        "tsunade", "shizune", "hinata", "konan", "mei", "earth_mother", "jiraiya",
        "gaara", "haku", "zabuza", "iruka", "hiruzen", "itachi", "orochimaru",
        "neji", "nagato", "pain", "obito", "madara", "kurama", "chiyo", "asuma",
        "deidara", "sasori", "hidan", "kakuzu", "kabuto", "kiba", "shikamaru",
        "yahiko", "teuchi", "tazuna", "might_guy", "akamaru", "white_zetsu", "shukaku",
    )
}

ILLUSTRATIONS = {
    name: f"{name}.png"
    for name in (
        "naruto_home", "konoha_day", "ninja_academy", "training_ground", "konoha_forest",
        "uchiha_ruins", "wave_bridge", "forest_of_death", "tougen", "suna_village",
        "myoboku", "pain_ruins", "war_front", "ending_nine_lives",
    )
}


_CHARACTERS = {
    "naruto": ("漩涡鸣人", ("漩涡鸣人", "鸣人")),
    "sasuke": ("宇智波佐助", ("宇智波佐助", "佐助")),
    "sakura": ("春野樱", ("春野樱", "小樱")),
    "kakashi": ("旗木卡卡西", ("旗木卡卡西", "卡卡西")),
    "kushina": ("漩涡玖辛奈", ("漩涡玖辛奈", "玖辛奈")),
    "minato": ("波风水门", ("波风水门", "水门", "第四代火影", "四代目")),
    "rin": ("野原琳", ("野原琳", "琳")),
    "tsunade": ("纲手", ("纲手大人", "纲手")),
    "shizune": ("静音", ("静音" ,)),
    "hinata": ("日向雏田", ("日向雏田", "雏田")),
    "konan": ("小南", ("小南", "纸之天使")),
    "mei": ("照美冥", ("照美冥", "水影")),
    "earth_mother": ("大地母亲", ("大地母亲",)),
    "jiraiya": ("自来也", ("自来也", "好色仙人")),
    "gaara": ("我爱罗", ("我爱罗", "风影")),
    "haku": ("白", ("水无月白",)),
    "zabuza": ("桃地再不斩", ("桃地再不斩", "再不斩", "雾隐之鬼")),
    "iruka": ("海野伊鲁卡", ("海野伊鲁卡", "伊鲁卡")),
    "hiruzen": ("猿飞日斩", ("猿飞日斩", "三代火影", "三代目", "三代")),
    "itachi": ("宇智波鼬", ("宇智波鼬", "鼬")),
    "orochimaru": ("大蛇丸", ("大蛇丸",)),
    "neji": ("日向宁次", ("日向宁次", "宁次")),
    "nagato": ("长门", ("漩涡长门", "长门")),
    "pain": ("佩恩·天道", ("佩恩·天道", "佩恩", "天道")),
    "obito": ("宇智波带土", ("宇智波带土", "带土", "阿飞")),
    "madara": ("宇智波斑", ("宇智波斑", "斑")),
    "kurama": ("九喇嘛", ("九喇嘛", "九尾妖狐")),
    "chiyo": ("千代婆婆", ("千代婆婆", "千代")),
    "asuma": ("猿飞阿斯玛", ("猿飞阿斯玛", "阿斯玛")),
    "deidara": ("迪达拉", ("迪达拉",)),
    "sasori": ("赤砂之蝎", ("赤砂之蝎", "蝎")),
    "hidan": ("飞段", ("飞段",)),
    "kakuzu": ("角都", ("角都",)),
    "kabuto": ("药师兜", ("药师兜", "兜")),
    "kiba": ("犬冢牙", ("犬冢牙", "牙和赤丸")),
    "shikamaru": ("奈良鹿丸", ("奈良鹿丸", "鹿丸")),
    "yahiko": ("弥彦", ("弥彦",)),
    "teuchi": ("手打", ("手打大叔", "手打")),
    "tazuna": ("达兹纳", ("达兹纳",)),
    "might_guy": ("迈特凯", ("迈特凯", "凯老师")),
    "akamaru": ("赤丸", ("赤丸",)),
    "white_zetsu": ("白绝", ("白绝",)),
    "shukaku": ("守鹤", ("一尾守鹤", "守鹤")),
}

_ALIASES = sorted(
    (
        (alias, character_id, display_name)
        for character_id, (display_name, aliases) in _CHARACTERS.items()
        for alias in aliases
    ),
    key=lambda item: len(item[0]),
    reverse=True,
)

_HAKU_LINE = re.compile(
    r"(?m)(?:^|\n)[（(\s　]*白(?=(?:[：:「『，。？！]|轻声|望|说|笑|抬|挡|转身|点头|摇头|把|还活着))"
)


LOCATION_ILLUSTRATIONS = {
    "naruto_home": "naruto_home",
    "ninja_academy": "ninja_academy",
    "hokage_office": "konoha_day",
    "ichiraku": "konoha_day",
    "training_ground_7": "training_ground",
    "konoha_hospital": "konoha_day",
    "hokage_rock": "konoha_day",
    "uchiha_ruins": "uchiha_ruins",
    "konoha_forest": "konoha_forest",
    "konoha_gate": "konoha_day",
    "forest_of_death": "forest_of_death",
    "tougen_gate": "tougen",
    "suna_village": "suna_village",
    "myoboku": "myoboku",
    "war_front": "war_front",
}

_STORY_ILLUSTRATIONS = {
    "ending_nine_lives": ("九命同归", "真结局", "第九契约", "九条命线"),
    "pain_ruins": ("佩恩袭村", "超·神罗天征", "神罗天征", "木叶废墟", "巨大深坑"),
    "war_front": ("第四次忍界大战", "忍界大战", "忍界联军", "联军前线", "天碍震星", "完成体须佐能乎"),
    "wave_bridge": ("波之国", "鸣人大桥", "大桥决战", "魔镜冰晶", "冰镜环立"),
    "forest_of_death": ("死亡森林", "第44演习场"),
    "tougen": ("桃源花海", "桃源", "契约之树", "命运回廊"),
    "suna_village": ("砂隐村", "风影夺还"),
    "myoboku": ("妙木山", "仙人模式修行"),
}


def portrait_path(character_id):
    filename = PORTRAITS.get(character_id)
    return PORTRAIT_ROOT / filename if filename else None


def illustration_path(illustration_id):
    filename = ILLUSTRATIONS.get(illustration_id)
    return ILLUSTRATION_ROOT / filename if filename else None


def character_for_text(text):
    """返回文本中最后出现的已配置角色，尽量贴近当前说话者。"""
    best = None
    for alias, character_id, display_name in _ALIASES:
        pos = text.rfind(alias)
        if pos >= 0 and (best is None or pos > best[0] or (pos == best[0] and len(alias) > best[1])):
            best = (pos, len(alias), character_id, display_name)
    for match in _HAKU_LINE.finditer(text):
        pos = match.start()
        if best is None or pos > best[0]:
            best = (pos, 1, "haku", "白")
    return (best[2], best[3]) if best else (None, None)


def illustration_for_text(text):
    """返回最近出现的关键剧情场景插图。"""
    best = None
    for illustration_id, keywords in _STORY_ILLUSTRATIONS.items():
        for keyword in keywords:
            pos = text.rfind(keyword)
            if pos >= 0 and (best is None or pos > best[0]):
                best = (pos, illustration_id)
    return best[1] if best else None


def illustration_for_location(location_id):
    return LOCATION_ILLUSTRATIONS.get(location_id, "konoha_day")
