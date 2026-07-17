# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from scenes import bonding
from systems import map as game_map, tougen
from systems.state import GameState


class ResourceLimitTests(unittest.TestCase):
    def test_tougen_supplies_are_claimed_once_per_day(self):
        state = GameState()
        state.flags["tougen_unlocked"] = True
        state.tougen_buildings = ["medical_room", "herb_field"]
        state.inventory.update({"回复丹": 0, "药草": 0})
        with (
            patch("systems.ui.choose", return_value=-1),
            patch("systems.ui.title"), patch("systems.ui.slow_print"),
        ):
            tougen.enter_tougen(state)
            tougen.enter_tougen(state)
        self.assertEqual(state.inventory["回复丹"], 1)
        self.assertEqual(state.inventory["药草"], 1)

    def test_gathering_has_daily_location_limit(self):
        state = GameState()
        state.location = "konoha_forest"
        with (
            patch("systems.crafting.gather_material") as gather,
            patch("systems.ui.slow_print"),
        ):
            for _ in range(4):
                game_map.do_gather(state)
        self.assertEqual(gather.call_count, 3)

    def test_tougen_training_is_daily_and_advances_time(self):
        state = GameState()
        before = state.player["attack"]
        with (
            patch("systems.ui.choose", return_value=2),
            patch("systems.ui.slow_print"), patch("systems.ui.pause"),
        ):
            tougen.train(state)
            tougen.train(state)
        self.assertGreater(state.player["attack"], before)
        self.assertEqual(state.tougen_training_sessions, 1)
        self.assertEqual(state.actions_taken, 1)

    def test_heart_talk_reward_is_once_per_partner_per_day(self):
        state = GameState()
        state.contracts["kushina"]["unlocked"] = True
        state.contracts["kushina"]["affection"] = 0
        before = state.contracts["kushina"]["affection"]
        with (
            patch("systems.ui.choose", return_value=0),
            patch("systems.ui.line"), patch("systems.ui.story"),
            patch("systems.ui.slow_print"), patch("systems.ui.pause"),
        ):
            bonding.heart_talk(state, set())
            bonding.heart_talk(state, set())
        self.assertEqual(state.contracts["kushina"]["affection"], before + bonding.TALK_GAIN["affection"])

    def test_daily_activity_survives_save_round_trip(self):
        state = GameState()
        self.assertTrue(state.consume_daily_use("tougen_supply"))
        state.tougen_training_sessions = 3
        loaded = GameState()
        loaded.from_dict(state.to_dict())
        self.assertEqual(loaded.daily_uses("tougen_supply"), 1)
        self.assertEqual(loaded.tougen_training_sessions, 3)


if __name__ == "__main__":
    unittest.main()
