# -*- coding: utf-8 -*-
import unittest

from systems.runtime import chapter_hint
from systems.state import GameState
from systems.validation import DataValidationError, validate_game_state


class DataValidationTests(unittest.TestCase):
    def test_current_data_is_consistent(self):
        self.assertEqual(validate_game_state(GameState()), [])

    def test_missing_skill_is_reported(self):
        state = GameState()
        state.player["skills"].append("missing_skill")
        with self.assertRaises(DataValidationError):
            validate_game_state(state)

    def test_progress_hint_uses_latest_story_state(self):
        state = GameState()
        state.flags["war_done"] = True
        self.assertIn("自由模式", chapter_hint(state))


if __name__ == "__main__":
    unittest.main()
