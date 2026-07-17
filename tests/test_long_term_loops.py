# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from systems import contract, crafting, equipment, world_events
from systems.state import GameState


class _FixedRandom:
    def random(self):
        return 0.1

    def choice(self, values):
        return list(values)[0]


class EconomyLoopTests(unittest.TestCase):
    def test_craft_quality_upgrade_affix_and_dismantle(self):
        state = GameState()
        state.chapter = 3
        state.ryo = 5000
        state.inventory.update({"铁砂": 12, "起爆黏土": 2, "查克拉晶片": 5})
        with patch("systems.ui.slow_print"):
            self.assertTrue(crafting.craft(state, "explosive_kunai", rng=_FixedRandom()))
        self.assertEqual(state.equipment_quality["explosive_kunai"], "epic")
        state.equipped_gear["weapon"] = "explosive_kunai"
        before = equipment.combat_bonuses(state)["reaction_mult"]
        with patch("systems.ui.slow_print"):
            self.assertTrue(crafting.upgrade_equipment(state, "explosive_kunai"))
            self.assertTrue(crafting.reforge_affix(state, "explosive_kunai", rng=_FixedRandom()))
        after = equipment.combat_bonuses(state)["reaction_mult"]
        self.assertGreater(after, before)
        self.assertIn(state.equipment_affixes["explosive_kunai"], equipment.AFFIXES)
        state.equipped_gear["weapon"] = "kunai_kit"
        with patch("systems.ui.slow_print"):
            self.assertTrue(crafting.dismantle_equipment(state, "explosive_kunai"))
        self.assertNotIn("explosive_kunai", state.owned_equipment)

    def test_reputation_reduces_shop_price(self):
        state = GameState()
        state.location = "konoha_hospital"
        state.ryo = 1000
        state.faction_reputation["konoha"] = 50
        with patch("systems.ui.slow_print"):
            self.assertTrue(crafting.buy_item(state, "药草", 100, "konoha"))
        self.assertEqual(state.ryo, 910)

    def test_economy_fields_survive_round_trip(self):
        state = GameState()
        state.ryo = 4321
        state.owned_equipment.append("explosive_kunai")
        state.equipment_quality["explosive_kunai"] = "legendary"
        state.equipment_enhancements["explosive_kunai"] = 4
        state.equipment_affixes["explosive_kunai"] = "breaker"
        loaded = GameState()
        loaded.from_dict(state.to_dict())
        self.assertEqual(loaded.ryo, 4321)
        self.assertEqual(loaded.equipment_quality["explosive_kunai"], "legendary")
        self.assertEqual(loaded.equipment_enhancements["explosive_kunai"], 4)
        self.assertEqual(loaded.equipment_affixes["explosive_kunai"], "breaker")


class WorldChainTests(unittest.TestCase):
    def test_every_location_has_three_chain_stages(self):
        self.assertEqual(len(world_events.EVENTS), 75)
        self.assertEqual(len(world_events.CHAIN_DEFS), 15)
        self.assertTrue(all(len(stages) == 3 for _, _, _, stages in world_events.CHAIN_DEFS))

    def test_chain_advances_only_in_order(self):
        state = GameState()
        state.location = "naruto_home"

        def choose_stage(values):
            stage = state.world_event_chains.get("home_letters", 0)
            return next(event for event in values if event.get("chain") == "home_letters" and event["stage"] == stage)

        with (
            patch("systems.world_events.random.choice", side_effect=choose_stage),
            patch("systems.ui.title"), patch("systems.ui.story"), patch("systems.ui.slow_print"),
        ):
            self.assertTrue(world_events.trigger_random_event(state, force=True))
            self.assertEqual(state.world_event_chains["home_letters"], 1)
            state.actions_taken += 2
            state.time_index = 2
            self.assertTrue(world_events.trigger_random_event(state, force=True))
            self.assertEqual(state.world_event_chains["home_letters"], 2)
            state.actions_taken += 2
            self.assertTrue(world_events.trigger_random_event(state, force=True))
        self.assertEqual(state.world_event_chains["home_letters"], 3)


class ContractTrialTests(unittest.TestCase):
    def setUp(self):
        self.state = GameState()
        self.contract = self.state.contracts["kushina"]
        self.contract["unlocked"] = True
        for key in ("affection", "trust", "safety", "fate_resonance"):
            self.contract[key] = 100

    def test_understanding_and_final_trials(self):
        with (
            patch("systems.ui.choose", return_value=0), patch("systems.ui.title"),
            patch("systems.ui.story"), patch("systems.ui.slow_print"),
        ):
            self.assertTrue(contract.run_trial(self.state, self.contract, 3))
            self.assertTrue(contract.run_trial(self.state, self.contract, 9))
        self.assertTrue(contract.trial_completed(self.state, "kushina", 3))
        self.assertTrue(contract.trial_completed(self.state, "kushina", 9))

    def test_cooperation_trial_uses_battle(self):
        with (
            patch("systems.battle.battle", return_value="win") as mocked,
            patch("systems.ui.title"), patch("systems.ui.story"), patch("systems.ui.slow_print"),
        ):
            self.assertTrue(contract.run_trial(self.state, self.contract, 5))
        self.assertTrue(mocked.called)
        self.assertTrue(contract.trial_completed(self.state, "kushina", 5))


if __name__ == "__main__":
    unittest.main()
