# -*- coding: utf-8 -*-
import unittest

from systems.state import GameState
from systems import visual_assets


class VisualAssetTests(unittest.TestCase):
    def test_character_detection_uses_latest_name(self):
        self.assertEqual(visual_assets.character_for_text("鸣人回头。卡卡西：集合。")[:1], ("kakashi",))
        self.assertEqual(visual_assets.character_for_text("\n白轻声说：谢谢你。")[:1], ("haku",))

    def test_story_detection(self):
        self.assertEqual(visual_assets.illustration_for_text("众人踏上波之国的大桥决战"), "wave_bridge")
        self.assertEqual(visual_assets.illustration_for_text("九命同归·真结局"), "ending_nine_lives")

    def test_all_locations_have_an_illustration(self):
        state = GameState()
        for location_id in state.maps:
            illustration_id = visual_assets.illustration_for_location(location_id)
            self.assertIn(illustration_id, visual_assets.ILLUSTRATIONS)

    def test_declared_assets_exist(self):
        for character_id in visual_assets.PORTRAITS:
            self.assertTrue(visual_assets.portrait_path(character_id).is_file(), character_id)
        for illustration_id in visual_assets.ILLUSTRATIONS:
            self.assertTrue(visual_assets.illustration_path(illustration_id).is_file(), illustration_id)


if __name__ == "__main__":
    unittest.main()
