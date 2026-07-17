# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from systems import battle, skill_mastery
from systems.state import GameState


class CombatTacticsTests(unittest.TestCase):
    def test_intent_categories_are_readable(self):
        fatal = {"name": "尾兽玉", "power": 120, "effect": None}
        control = {"name": "封印术", "power": 30, "effect": "sealed"}
        support = {"name": "土流壁", "power": 0, "effect": "defense_up"}
        self.assertIn("致命攻击", battle._intent_description(fatal))
        self.assertIn("控制招式", battle._intent_description(control))
        self.assertIn("强化/恢复", battle._intent_description(support))

    def test_break_gauge_interrupts_next_action(self):
        enemy = {"name": "测试敌人", "max_break": 20, "break": 20, "broken": False}
        log = {"break_count": 0}
        with patch("systems.ui.slow_print"):
            broken = battle._apply_break(enemy, 25, log, "测试攻击")
        self.assertTrue(broken)
        self.assertTrue(enemy["broken"])
        self.assertEqual(enemy["break"], 0)
        self.assertEqual(log["break_count"], 1)

    def test_precision_counter_reduces_damage(self):
        attacker = {
            "id": "enemy", "name": "敌人", "attack": 30, "defense": 15,
            "speed": 10, "hp": 100, "max_hp": 100, "chakra": 100,
            "status": [], "elements": ["fire"],
        }
        defender = {
            "id": "naruto", "name": "鸣人", "attack": 20, "defense": 20,
            "speed": 20, "hp": 100, "max_hp": 100, "chakra": 100,
            "status": [], "elements": ["wind"], "_guard_mode": "counter",
        }
        skill = {
            "id": "test", "name": "测试攻击", "type": "taijutsu", "element": "taijutsu",
            "power": 50, "chakra_cost": 0, "accuracy": 100, "effect": None,
        }
        with (
            patch("systems.battle.calc_damage", return_value=100),
            patch("systems.battle.random.random", return_value=0),
            patch("systems.ui.slow_print"),
        ):
            result = battle.execute_skill(attacker, defender, skill)
        self.assertTrue(result["counter_success"])
        self.assertEqual(result["damage"], 35)
        self.assertEqual(defender["hp"], 65)

    def test_survival_objective_finishes_without_defeating_enemy(self):
        state = GameState()
        state.player["attack"] = 1
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
            result = battle.battle(
                state,
                "training_dummy",
                special_rules={"objective": {"type": "survive", "turns": 1, "result": "survived"}},
            )
        self.assertEqual(result, "survived")
        self.assertNotIn("_guard_mode", state.player)

    def test_ally_order_can_switch_to_disruption(self):
        log = {"ally_order": "balanced"}
        with patch("systems.ui.choose", return_value=3), patch("systems.ui.slow_print"):
            self.assertTrue(battle._configure_ally_order(log))
        self.assertEqual(log["ally_order"], "disrupt")

    def test_wet_lightning_reaction(self):
        target = {
            "name": "目标", "hp": 200, "max_hp": 200, "chakra": 100,
            "status": [{"id": "wet", "turns": 2}],
        }
        skill = {"element": "lightning"}
        result = {"hit": True, "damage": 100}
        with patch("systems.ui.slow_print"):
            battle._apply_element_reaction(target, skill, result)
        self.assertEqual(target["hp"], 165)
        self.assertFalse(any(status["id"] == "wet" for status in target["status"]))
        self.assertTrue(any(status["id"] == "paralyze" for status in target["status"]))

    def test_environment_and_position_modify_skill(self):
        skill = {
            "id": "test", "name": "测试", "type": "taijutsu", "element": "taijutsu",
            "power": 100, "chakra_cost": 0, "accuracy": 90, "effect": None,
        }
        front = battle._position_skill(skill, {"id": "naruto"}, {"player_position": "front"})
        self.assertEqual(front["power"], 120)
        self.assertGreater(front["_break_mult"], 1)

        fire = dict(skill, element="fire")
        rainy_fire = battle._environment_skill(fire, {"id": "rain"})
        self.assertEqual(rainy_fire["power"], 80)

    def test_skill_branch_changes_runtime_skill(self):
        state = GameState()
        state.player["skills"].append("rasengan")
        state.skill_upgrades["rasengan"] = "impact"
        upgraded = skill_mastery.apply_upgrade(state, state.skills_db["rasengan"])
        self.assertEqual(upgraded["_upgrade_name"], "破势型")
        self.assertEqual(upgraded["_break_mult"], 2.0)
        self.assertLess(upgraded["power"], state.skills_db["rasengan"]["power"])


if __name__ == "__main__":
    unittest.main()
