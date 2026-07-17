# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from systems import battle, crafting, factions, new_game_plus, party
from systems.state import GameState


class _StableRandom:
    def shuffle(self, values):
        return values

    def random(self):
        return 0.99

    def choices(self, names, weights=None, k=1):
        _ = weights, k
        return [names[0]]


class FactionQuestTests(unittest.TestCase):
    def test_faction_content_has_full_template_and_story_sets(self):
        self.assertEqual(len(factions.TEMPLATES), 21)
        self.assertEqual(sum(len(chain) for chain in factions.FACTION_CHAINS.values()), 15)

    def test_dynamic_quest_progress_awards_reputation(self):
        state = GameState()
        quests = factions.refresh_board(state, force=True, rng=_StableRandom())
        hunt = next(quest for quest in quests if quest["event"] == "defeat")
        with patch("systems.ui.slow_print"):
            self.assertTrue(factions.accept_quest(state, hunt["id"]))
            factions.record_progress(state, "defeat", "forest_wolf", hunt["required"])
        self.assertEqual(state.dynamic_quests[hunt["id"]]["status"], "completed")
        self.assertEqual(state.faction_reputation[hunt["faction"]], hunt["rep"])

    def test_new_progress_fields_survive_state_round_trip(self):
        state = GameState()
        state.faction_reputation["konoha"] = 37
        state.teammate_progress["sakura"] = {
            "level": 4, "exp": 12, "bond": 30, "route": "medic", "milestones": [10, 30]
        }
        state.combo_mastery["combo_rin"] = {"uses": 4, "level": 2}
        state.faction_story["konoha_oath_1"] = {"status": "active", "progress": 1}
        state.faction_rank_rewards = ["konoha_20"]
        loaded = GameState()
        loaded.from_dict(state.to_dict())
        self.assertEqual(loaded.faction_reputation["konoha"], 37)
        self.assertEqual(loaded.teammate_progress["sakura"]["level"], 4)
        self.assertEqual(loaded.teammate_progress["sakura"]["route"], "medic")
        self.assertEqual(loaded.combo_mastery["combo_rin"]["level"], 2)
        self.assertEqual(loaded.faction_story["konoha_oath_1"]["progress"], 1)
        self.assertEqual(loaded.faction_rank_rewards, ["konoha_20"])

    def test_story_chain_progress_and_rank_reward(self):
        state = GameState()
        story = factions.available_story_quests(state)[0]
        with patch("systems.ui.slow_print"), patch("systems.ui.story"), patch("systems.ui.title"):
            self.assertTrue(factions.accept_story_quest(state, story["id"]))
            factions.record_progress(state, "patrol", "konoha_forest", 2)
            factions.add_reputation(state, "konoha", 40, "测试阶位")
        self.assertEqual(state.faction_story[story["id"]]["status"], "completed")
        self.assertIn("will_of_fire_charm", state.owned_equipment)
        self.assertIn("konoha_50", state.faction_rank_rewards)


class GrowthAndCraftingTests(unittest.TestCase):
    def test_teammate_levels_and_becomes_stronger(self):
        state = GameState()
        state.flags["team7_assigned"] = True
        state.selected_party = ["sakura"]
        party.normalize_progress(state)
        before = party.combat_allies(state)[0]["power"]
        with patch("systems.ui.slow_print"):
            party.gain_teammate_exp(state, ["sakura"], 500, bond=5)
        after = party.combat_allies(state)[0]["power"]
        self.assertGreater(state.teammate_progress["sakura"]["level"], 1)
        self.assertGreater(after, before)

    def test_combo_mastery_reduces_cost(self):
        state = GameState()
        base = party.combo_stats(state, "combo_kushina", 25)
        with patch("systems.ui.slow_print"):
            for _ in range(3):
                party.gain_combo_mastery(state, "combo_kushina")
        upgraded = party.combo_stats(state, "combo_kushina", 25)
        self.assertEqual(base["level"], 1)
        self.assertEqual(upgraded["level"], 2)
        self.assertLess(upgraded["cost"], base["cost"])
        self.assertGreater(upgraded["power_mult"], 1)

    def test_teammate_route_grants_active_ability(self):
        state = GameState()
        state.flags["team7_assigned"] = True
        state.selected_party = ["sakura"]
        party.normalize_progress(state)
        state.teammate_progress["sakura"]["route"] = "strength"
        ally = party.combat_allies(state)[0]
        enemy = battle._prepare_enemy(state, "training_dummy", {})
        before = enemy["hp"]
        with patch("systems.ui.choose", return_value=0), patch("systems.ui.slow_print"):
            self.assertTrue(party.use_active_ability(state, state.player, enemy, {}, [ally]))
        self.assertLess(enemy["hp"], before)

    def test_bond_milestone_is_recorded(self):
        state = GameState()
        party.normalize_progress(state)
        with patch("systems.ui.title"), patch("systems.ui.story"), patch("systems.ui.slow_print"):
            party.gain_teammate_exp(state, ["sasuke"], 0, bond=10)
        self.assertIn(10, state.teammate_progress["sasuke"]["milestones"])

    def test_forge_and_alchemy_consume_materials(self):
        state = GameState()
        state.chapter = 3
        state.inventory.update({"铁砂": 3, "木材": 1, "药草": 2})
        with patch("systems.ui.slow_print"):
            self.assertTrue(crafting.craft(state, "tempered_kunai"))
            self.assertTrue(crafting.craft(state, "healing_pill"))
        self.assertIn("tempered_kunai", state.owned_equipment)
        self.assertEqual(state.inventory["铁砂"], 0)
        self.assertEqual(state.inventory["回复丹"], 2)

    def test_new_cycle_preserves_growth_and_reputation(self):
        state = GameState()
        state.teammate_progress["sakura"] = {"level": 8, "exp": 10, "bond": 30}
        state.combo_mastery["combo_rin"] = {"uses": 8, "level": 3}
        state.faction_reputation["konoha"] = 50
        with (
            patch("scenes.chapter_01.intro"),
            patch("systems.map.show_location"),
            patch("systems.ui.banner"),
            patch("systems.ui.slow_print"),
        ):
            new_game_plus.start_new_cycle(state, [])
        self.assertEqual(state.teammate_progress["sakura"]["level"], 8)
        self.assertEqual(state.combo_mastery["combo_rin"]["level"], 3)
        self.assertEqual(state.faction_reputation["konoha"], 50)


class EncounterTests(unittest.TestCase):
    @staticmethod
    def _choose(prompt, options, allow_cancel=False):
        _ = allow_cancel
        if prompt == "你的行动:":
            return options.index("忍术/体术")
        return 0

    def test_multi_target_battle_defeats_whole_group(self):
        state = GameState()
        state.player["attack"] = 99999
        state.equipped_skills = ["basic_taijutsu"]
        with (
            patch("systems.ui.choose", side_effect=self._choose),
            patch("systems.ui.title"),
            patch("systems.ui.story"),
            patch("systems.ui.slow_print"),
            patch("systems.ui.line"),
            patch("builtins.print"),
            patch("systems.crafting.award_battle_material", return_value=None),
        ):
            result = battle.multi_target_battle(
                state,
                ["training_dummy", "forest_wolf"],
                special_rules={"skip_preparation": True},
            )
        self.assertEqual(result, "win")
        self.assertIn("training_dummy", state.discovered_enemies)
        self.assertIn("forest_wolf", state.discovered_enemies)

    def test_multi_stage_boss_sets_transition_rules(self):
        state = GameState()
        phases = [
            {"name": "第一形态", "enemy_id": "training_dummy"},
            {"name": "第二形态", "enemy_id": "forest_wolf", "transition_heal": 0.1},
        ]
        with (
            patch("systems.battle.battle", return_value="win") as mocked,
            patch("systems.ui.title"),
            patch("systems.ui.story"),
            patch("systems.ui.slow_print"),
        ):
            result = battle.multi_stage_boss_battle(state, phases)
        self.assertEqual(result, "win")
        second_rules = mocked.call_args_list[1].kwargs["special_rules"]
        self.assertTrue(second_rules["skip_preparation"])
        self.assertTrue(second_rules["preserve_player_status"])

    def test_multi_target_boss_inherits_a_cutin_asset(self):
        state = GameState()
        phases = [{
            "name": "冰镜与水分身",
            "enemy_ids": [
                {"enemy_id": "haku_bridge", "enemy_name": "白·冰镜本体"},
                {"enemy_id": "zabuza_first", "enemy_name": "再不斩·水分身"},
            ],
        }]
        with (
            patch("systems.battle.multi_target_battle", return_value="win") as mocked,
            patch("systems.ui.title"),
            patch("systems.ui.slow_print"),
        ):
            result = battle.multi_stage_boss_battle(state, phases)
        self.assertEqual(result, "win")
        self.assertEqual(mocked.call_args.kwargs["special_rules"]["visual_id"], "haku_bridge")


if __name__ == "__main__":
    unittest.main()
