# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from systems import battle, equipment, new_game_plus, wanted
from systems.state import GameState


class EquipmentTests(unittest.TestCase):
    def test_unlocks_and_three_piece_set_bonus(self):
        state = GameState()
        state.flags["team7_assigned"] = True
        state.flags["kushina_contacted"] = True
        state.player["skills"].append("rasengan")
        for contract in list(state.contracts.values())[:6]:
            contract["unlocked"] = True
        with patch("systems.ui.slow_print"):
            equipment.sync_unlocks(state)
        self.assertIn("spiral_gauntlet", state.owned_equipment)
        self.assertIn("nine_thread_cloak", state.owned_equipment)
        self.assertIn("seal_charm", state.owned_equipment)
        state.equipped_gear = {
            "weapon": "spiral_gauntlet",
            "armor": "nine_thread_cloak",
            "accessory": "seal_charm",
        }
        bonuses = equipment.combat_bonuses(state)
        self.assertLess(bonuses["chakra_cost_mult"], 1)
        self.assertGreater(bonuses["break_mult"], 1.3)
        self.assertGreater(bonuses["reaction_mult"], 1)

    def test_equipment_modifies_runtime_skill(self):
        skill = {
            "id": "rasengan", "name": "螺旋丸", "type": "ninjutsu", "element": "wind",
            "power": 100, "chakra_cost": 20, "accuracy": 90, "effect": None,
        }
        bonuses = equipment.combat_bonuses(GameState())
        adjusted = equipment.apply_to_skill(skill, bonuses)
        self.assertEqual(adjusted["power"], 100)


class EliteAndWantedTests(unittest.TestCase):
    def test_elite_affixes_change_stats(self):
        enemy = {
            "hp": 100, "max_hp": 100, "attack": 20, "defense": 10,
            "speed": 10, "chakra": 50, "max_chakra": 50, "exp_reward": 20,
        }
        battle._apply_elite_affixes(enemy, ["armored", "berserk"])
        self.assertEqual(enemy["hp"], 125)
        self.assertGreater(enemy["attack"], 20)
        self.assertEqual(set(enemy["_elite_affixes"]), {"armored", "berserk"})
        self.assertGreater(enemy["exp_reward"], 20)

    def test_wanted_targets_unlock_by_chapter(self):
        state = GameState()
        self.assertEqual([target["id"] for target in wanted.available_targets(state)], ["forest_alpha"])
        state.chapter = 10
        self.assertEqual(len(wanted.available_targets(state)), len(wanted.TARGETS))

    def test_wanted_first_clear_grants_record_and_gear(self):
        state = GameState()
        state.chapter = 2
        with (
            patch("systems.ui.choose", return_value=1),
            patch("systems.ui.slow_print"),
            patch("systems.battle.battle", return_value="win"),
            patch("systems.wanted.random.sample", return_value=["armored"]),
        ):
            wanted.show_wanted_board(state)
        self.assertEqual(state.wanted_records["rogue_hunter"], 1)
        self.assertIn("hunter_blade", state.owned_equipment)
        self.assertGreaterEqual(state.fate_points, 1)


class NewGamePlusTests(unittest.TestCase):
    def test_new_cycle_preserves_growth_and_resets_story(self):
        state = GameState()
        state.flags["war_done"] = True
        state.flags["true_end"] = True
        state.player["level"] = 30
        state.endings_seen = ["war_true"]
        state.skill_upgrades = {"basic_taijutsu": "breaker"}
        state.owned_equipment.append("war_emblem")
        with (
            patch("scenes.chapter_01.intro"),
            patch("systems.map.show_location"),
            patch("systems.ui.banner"),
            patch("systems.ui.slow_print"),
        ):
            new_game_plus.start_new_cycle(state, ["veteran_enemies"])
        self.assertEqual(state.new_game_plus, 1)
        self.assertEqual(state.challenge_modifiers, ["veteran_enemies"])
        self.assertEqual(state.player["level"], 30)
        self.assertFalse(state.flags["war_done"])
        self.assertIn("war_true", state.endings_seen)
        self.assertIn("war_emblem", state.owned_equipment)


if __name__ == "__main__":
    unittest.main()
