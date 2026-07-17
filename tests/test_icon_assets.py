# -*- coding: utf-8 -*-
import struct
import unittest

from systems import battle, crafting, equipment, icon_assets, ui


def png_size(path):
    with path.open("rb") as handle:
        signature = handle.read(24)
    if signature[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(path)
    return struct.unpack(">II", signature[16:24])


class IconAssetTests(unittest.TestCase):
    def test_manifest_counts_match_game_systems(self):
        self.assertEqual(len(icon_assets.ELEMENT_NAMES), 13)
        self.assertEqual(len(icon_assets.STATUS_NAMES), 16)
        self.assertEqual(len(icon_assets.INTENT_NAMES), 4)
        self.assertEqual(len(icon_assets.REACTION_NAMES), 5)
        self.assertEqual(len(icon_assets.ACTION_NAMES), 33)
        self.assertEqual(
            icon_assets.EQUIPMENT_NAMES,
            {item_id: item["name"] for item_id, item in equipment.CATALOG.items()},
        )
        self.assertEqual(
            set(icon_assets.ITEM_NAMES.values()),
            set(battle.ITEM_EFFECTS) | crafting.MATERIALS | {"两"},
        )
        self.assertEqual(
            set(icon_assets.AFFIX_NAMES.values()),
            {meta[0] for meta in battle.ELITE_AFFIXES.values()}
            | {meta["name"] for meta in equipment.AFFIXES.values()},
        )
        self.assertEqual(len(icon_assets.CONTRACT_NAMES), 9)
        self.assertEqual(len(icon_assets.ACHIEVEMENT_NAMES), 11)
        self.assertEqual(len(icon_assets.ENDING_NAMES), 9)
        self.assertEqual(len(icon_assets.SKILL_NAMES), 72)

    def test_option_matching(self):
        self.assertEqual(icon_assets.option_asset("螺旋丸 (威力100)"), ("skills", "rasengan"))
        self.assertEqual(icon_assets.option_asset("回复丹 ×2"), ("items", "healing_pill"))
        self.assertEqual(icon_assets.option_asset("森林狼王 | ★首胜"), ("wanted", "forest_alpha"))
        self.assertEqual(icon_assets.option_asset("制式苦无包 - 体术威力+8%"), ("equipment", "kunai_kit"))
        self.assertEqual(icon_assets.option_asset("开始战斗"), ("actions", "battle_start"))
        self.assertEqual(icon_assets.option_asset("调整技能 | 已装备4项"), ("actions", "loadout"))
        self.assertEqual(icon_assets.option_asset("队友培养 | 路线与羁绊"), ("actions", "ally_ultimate"))
        self.assertEqual(icon_assets.option_asset("拜访火影"), ("actions", "visit"))
        self.assertEqual(icon_assets.option_asset("契约之树 (查看/提升契约)"), ("actions", "contract_tree"))
        self.assertEqual(icon_assets.option_asset("忍术研究 (以前世记忆开发新术)"), ("actions", "ninjutsu_research"))

    def test_structured_choices_keep_explicit_assets_and_string_compatibility(self):
        choice = ui.Choice("春野樱", ("portraits", "sakura"), "Lv.8 · 羁绊 30", "同行")
        self.assertEqual(choice, "春野樱")
        self.assertEqual(ui.choice_label(choice), "春野樱")
        self.assertIn("Lv.8", ui.choice_text(choice))
        self.assertEqual(choice.asset, ("portraits", "sakura"))
        self.assertTrue(choice.startswith("春野"))
        self.assertEqual(choice[:2], "春野")

    def test_all_boss_cutins_exist_at_gui_size(self):
        for enemy_id in icon_assets.BOSS_META:
            path = icon_assets.boss_cutin_path(enemy_id)
            self.assertTrue(path.is_file(), enemy_id)
            self.assertEqual(png_size(path), (832, 208), enemy_id)

    def test_visual_events_are_optional_and_forwarded(self):
        original = ui.VISUAL_EVENT_HANDLER
        received = []
        try:
            ui.VISUAL_EVENT_HANDLER = lambda event, payload: received.append((event, payload))
            ui.emit_visual_event("reaction", reaction="electrocharged")
        finally:
            ui.VISUAL_EVENT_HANDLER = original
        self.assertEqual(received, [("reaction", {"reaction": "electrocharged"})])


if __name__ == "__main__":
    unittest.main()
