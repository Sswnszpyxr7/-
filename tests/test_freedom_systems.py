# -*- coding: utf-8 -*-
import unittest
from collections import Counter
from unittest.mock import patch

from systems import battle, collection, loadout, party, time_system, world_events
from systems.state import GameState


class TimeSystemTests(unittest.TestCase):
    def test_time_rolls_into_next_day(self):
        state = GameState()
        state.time_index = 3
        with patch("systems.ui.slow_print"):
            time_system.advance_time(state)
        self.assertEqual(state.world_day, 2)
        self.assertEqual(state.time_index, 0)
        self.assertEqual(state.actions_taken, 1)


class LoadoutAndPartyTests(unittest.TestCase):
    def test_loadout_is_limited_and_keeps_basic_attack(self):
        state = GameState()
        state.player["skills"] = list(state.skills_db)[:12]
        state.equipped_skills = list(state.player["skills"])
        equipped = loadout.normalize_loadout(state)
        self.assertLessEqual(len(equipped), loadout.MAX_EQUIPPED_SKILLS)
        self.assertIn("basic_taijutsu", equipped)

    def test_two_available_teammates_join_combat(self):
        state = GameState()
        state.flags["team7_assigned"] = True
        state.selected_party = ["sasuke", "sakura"]
        allies = party.combat_allies(state)
        self.assertEqual(len(allies), 2)
        self.assertEqual({ally["id"] for ally in allies}, {"party_sasuke", "party_sakura"})

    def test_battle_uses_preparation_and_equipped_skills(self):
        state = GameState()
        state.player["attack"] = 999
        state.equipped_skills = ["basic_taijutsu"]

        def choose(prompt, options, allow_cancel=False):
            _ = allow_cancel
            if prompt == "战斗准备":
                return 0
            if prompt == "你的行动:":
                return options.index("忍术/体术")
            if prompt == "使用哪个技能?":
                return 0
            return 0

        with (
            patch("systems.ui.choose", side_effect=choose),
            patch("systems.ui.title"),
            patch("systems.ui.story"),
            patch("systems.ui.slow_print"),
            patch("systems.ui.line"),
            patch("builtins.print"),
        ):
            result = battle.battle(state, "training_dummy")
        self.assertEqual(result, "win")
        self.assertIn("training_dummy", state.discovered_enemies)


class WorldEventTests(unittest.TestCase):
    def test_every_map_has_an_event_pool(self):
        state = GameState()
        counts = Counter(event["location"] for event in world_events.EVENTS)
        self.assertEqual(set(counts), set(state.maps))
        self.assertTrue(all(counts[location] >= 2 for location in state.maps))

    def test_forced_event_records_history(self):
        state = GameState()
        state.actions_taken = 100
        with (
            patch("systems.ui.title"),
            patch("systems.ui.story"),
            patch("systems.ui.slow_print"),
            patch("systems.world_events.random.choice", side_effect=lambda values: values[0]),
        ):
            self.assertTrue(world_events.trigger_random_event(state, force=True))
        self.assertEqual(len(state.random_event_history), 1)


class CollectionTests(unittest.TestCase):
    def test_endings_and_achievements_are_collected(self):
        state = GameState()
        state.flags["wave_done"] = True
        state.flags["haku_alive"] = True
        state.flags["zabuza_alive"] = True
        state.flags["team7_assigned"] = True
        state.selected_party = ["sasuke", "sakura"]
        state.equipped_skills = list(state.skills_db)[:6]
        collection.refresh(state)
        self.assertIn("wave_perfect", state.endings_seen)
        self.assertIn("two_companions", state.achievements)
        self.assertIn("full_loadout", state.achievements)


if __name__ == "__main__":
    unittest.main()
