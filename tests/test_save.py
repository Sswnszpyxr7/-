# -*- coding: utf-8 -*-
import json
import os
import tempfile
import unittest

from systems import save
from systems.state import GameState


class SaveSystemTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="nine_lives_save_test_")
        self.original_save_dir = save.SAVE_DIR
        save.set_save_dir(self.temp_dir.name)

    def tearDown(self):
        save.set_save_dir(self.original_save_dir)
        self.temp_dir.cleanup()

    def test_round_trip_and_metadata(self):
        state = GameState()
        state.fate_points = 9
        state.world_day = 4
        state.time_index = 2
        state.actions_taken = 17
        state.flags["team7_assigned"] = True
        state.selected_party = ["sakura"]
        state.equipped_skills = ["basic_taijutsu", "shadow_clone"]
        state.skill_upgrades = {"basic_taijutsu": "breaker"}
        state.owned_equipment.append("war_emblem")
        state.equipped_gear["accessory"] = "war_emblem"
        state.wanted_records = {"forest_alpha": 2}
        state.new_game_plus = 1
        state.challenge_modifiers = ["veteran_enemies"]
        save.save_game(state, 1, silent=True)

        path = os.path.join(self.temp_dir.name, "save_01.json")
        with open(path, encoding="utf-8") as file:
            payload = json.load(file)
        self.assertEqual(payload["_meta"]["schema_version"], save.SAVE_SCHEMA_VERSION)

        loaded = GameState()
        self.assertTrue(save.load_game(loaded, 1))
        self.assertEqual(loaded.fate_points, 9)
        self.assertEqual((loaded.world_day, loaded.time_index, loaded.actions_taken), (4, 2, 17))
        self.assertEqual(loaded.selected_party, ["sakura"])
        self.assertEqual(loaded.equipped_skills, ["basic_taijutsu", "shadow_clone"])
        self.assertEqual(loaded.skill_upgrades, {"basic_taijutsu": "breaker"})
        self.assertIn("war_emblem", loaded.owned_equipment)
        self.assertEqual(loaded.equipped_gear["accessory"], "war_emblem")
        self.assertEqual(loaded.wanted_records, {"forest_alpha": 2})
        self.assertEqual(loaded.new_game_plus, 1)
        self.assertEqual(loaded.challenge_modifiers, ["veteran_enemies"])

    def test_corrupt_primary_falls_back_to_backup(self):
        state = GameState()
        state.fate_points = 3
        save.save_game(state, 1, silent=True)
        state.fate_points = 7
        save.save_game(state, 1, silent=True)

        path = os.path.join(self.temp_dir.name, "save_01.json")
        with open(path, "w", encoding="utf-8") as file:
            file.write("{")

        loaded = GameState()
        self.assertTrue(save.load_game(loaded, 1))
        self.assertEqual(loaded.fate_points, 3)

    def test_invalid_slot_is_rejected(self):
        with self.assertRaises(ValueError):
            save.save_game(GameState(), 0, silent=True)

    def test_collection_profile_is_shared_across_slots(self):
        first = GameState()
        first.endings_seen.append("wave_perfect")
        first.achievements.append("first_ending")
        save.save_game(first, 1, silent=True)

        second = GameState()
        self.assertTrue(save.load_profile(second))
        self.assertIn("wave_perfect", second.endings_seen)
        self.assertIn("first_ending", second.achievements)


if __name__ == "__main__":
    unittest.main()
