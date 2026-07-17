# -*- coding: utf-8 -*-
import unittest

from systems import progression_graphs
from systems.state import GameState


def by_id(graph, node_id):
    return next(node for node in graph["nodes"] if node["id"] == node_id)


class StoryGraphTests(unittest.TestCase):
    def test_fresh_save_marks_only_first_stage_current(self):
        graph = progression_graphs.story_graph(GameState())
        self.assertEqual(by_id(graph, "team7")["status"], "current")
        self.assertEqual(by_id(graph, "bell")["status"], "locked")
        self.assertEqual(by_id(graph, "wave_perfect")["status"], "locked")

    def test_current_and_collected_routes_are_distinct(self):
        state = GameState()
        state.flags["wave_done"] = True
        state.flags["haku_alive"] = True
        state.flags["zabuza_alive"] = True
        state.endings_seen = ["wave_canon"]
        graph = progression_graphs.story_graph(state)
        self.assertEqual(by_id(graph, "wave_perfect")["status"], "route_good")
        self.assertEqual(by_id(graph, "wave_canon")["status"], "collected")


class RomanceGraphTests(unittest.TestCase):
    def test_romance_stage_progression(self):
        state = GameState()
        graph = progression_graphs.romance_graph(state)
        hinata = next(row for row in graph["rows"] if row["id"] == "hinata")
        self.assertEqual(hinata["stages"][1]["status"], "locked")

        state.flags["shippuden_started"] = True
        state.flags["hinata_contracted"] = True
        state.contracts["hinata"]["unlocked"] = True
        graph = progression_graphs.romance_graph(state)
        hinata = next(row for row in graph["rows"] if row["id"] == "hinata")
        self.assertEqual(hinata["stages"][0]["status"], "complete")
        self.assertEqual(hinata["stages"][1]["status"], "current")

        state.flags["rom_hinata_1"] = True
        state.flags["rom_hinata_2"] = True
        state.flags["war_done"] = True
        state.romance["hinata"] = 55
        graph = progression_graphs.romance_graph(state)
        hinata = next(row for row in graph["rows"] if row["id"] == "hinata")
        self.assertEqual(hinata["stages"][3]["status"], "current")

        state.flags["lover"] = "hinata"
        graph = progression_graphs.romance_graph(state)
        hinata = next(row for row in graph["rows"] if row["id"] == "hinata")
        sakura = next(row for row in graph["rows"] if row["id"] == "sakura")
        self.assertEqual(hinata["stages"][3]["status"], "love")
        self.assertEqual(sakura["stages"][3]["status"], "family")


if __name__ == "__main__":
    unittest.main()
