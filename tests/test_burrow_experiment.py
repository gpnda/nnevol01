import math
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import numpy as np

from experiments.burrow.experiment import BurrowExperiment, VisionSimulator
from experiments.toolbox import StatsCollector


class BurrowExperimentTests(unittest.TestCase):
    def test_loads_semicolon_map_and_separates_burrows_from_walls(self):
        with tempfile.TemporaryDirectory() as directory:
            map_path = Path(directory) / "burrows.csv"
            map_path.write_text(
                "1;1;1;1;1\n"
                "1;9;0;9;1\n"
                "1;0;0;0;1\n"
                "1;9;0;9;1\n"
                "1;1;1;1;1\n",
                encoding="utf-8",
            )

            world, burrow_mask = BurrowExperiment._load_experiment_map(map_path)

        self.assertEqual((world.width, world.height), (5, 5))
        self.assertEqual(int(world.walls_map[0, 0]), 1)
        self.assertEqual(int(world.walls_map[1, 1]), 0)
        self.assertTrue(burrow_mask[1, 1])
        self.assertFalse(burrow_mask[2, 2])

    def test_rejects_values_other_than_open_wall_and_burrow(self):
        with tempfile.TemporaryDirectory() as directory:
            map_path = Path(directory) / "burrows.csv"
            map_path.write_text(
                "1;1;1;1;1\n"
                "1;9;0;9;1\n"
                "1;0;2;0;1\n"
                "1;9;0;9;1\n"
                "1;1;1;1;1\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "Unsupported value"):
                BurrowExperiment._load_experiment_map(map_path)

    def make_experiment(self, x=1.95, stay_ticks=2):
        experiment = BurrowExperiment.__new__(BurrowExperiment)
        experiment.test_world = SimpleNamespace(
            width=5,
            height=5,
            walls_map=np.zeros((5, 5), dtype=np.int32),
            update_map=Mock(),
        )
        experiment.burrow_mask = np.zeros((5, 5), dtype=bool)
        experiment.burrow_mask[2, 2] = True
        experiment.inspecting_creature = SimpleNamespace(
            x=x,
            y=2.5,
            angle=0.0,
            speed=1.0,
            input_wayblocked=0.0,
            input_bite_success=0.0,
        )
        experiment.burrow_stay_ticks = stay_ticks
        experiment.DEFAULT_MAX_TICKS_PER_RUN = 10
        experiment.ticks_in_run = 0
        experiment.consecutive_burrow_ticks = 0
        experiment.has_entered_burrow = False
        experiment.entry_tick = None
        experiment.run_finished = False
        experiment.current_run_outcome = None
        experiment.current_creature_state = None
        experiment.outcome_counts = {outcome: 0 for outcome in experiment.OUTCOMES}
        experiment.stats_collector = StatsCollector()
        experiment.current_stage = 0
        experiment.stage_run_counter = 0
        experiment.plan = [{"num_runs": 10}]
        experiment.is_running = True
        experiment.stage_run_counter_increment = Mock()
        experiment.finish_experiment = Mock()
        return experiment

    def test_run_counts_success_after_required_continuous_burrow_ticks(self):
        experiment = self.make_experiment(stay_ticks=2)
        vision = np.zeros(45, dtype=np.float32)
        dots = np.empty((0, 2), dtype=np.float32)

        with patch.object(VisionSimulator, "get_creature_vision", return_value=(vision, dots)), \
                patch.object(VisionSimulator, "simulate_nn_output", return_value=(0.0, 1.0, 0.0)):
            BurrowExperiment._stage_0(experiment)
            self.assertEqual(experiment.outcome_counts["stayed"], 0)
            BurrowExperiment._stage_0(experiment)

        self.assertEqual(experiment.current_run_outcome, "stayed")
        self.assertEqual(experiment.outcome_counts["stayed"], 1)

    def test_run_counts_entered_then_left_before_required_duration(self):
        experiment = self.make_experiment(stay_ticks=3)
        vision = np.zeros(45, dtype=np.float32)
        dots = np.empty((0, 2), dtype=np.float32)

        with patch.object(VisionSimulator, "get_creature_vision", return_value=(vision, dots)), \
                patch.object(VisionSimulator, "simulate_nn_output", return_value=(0.0, 1.0, 0.0)):
            BurrowExperiment._stage_0(experiment)
            experiment.inspecting_creature.angle = math.pi
            BurrowExperiment._stage_0(experiment)

        self.assertEqual(experiment.current_run_outcome, "entered_then_left")
        self.assertEqual(experiment.outcome_counts["entered_then_left"], 1)

    def test_run_counts_never_entered_when_timeout_is_reached(self):
        experiment = self.make_experiment(x=1.5, stay_ticks=2)
        experiment.DEFAULT_MAX_TICKS_PER_RUN = 1
        experiment.ticks_in_run = 2
        vision = np.zeros(45, dtype=np.float32)
        dots = np.empty((0, 2), dtype=np.float32)

        with patch.object(VisionSimulator, "get_creature_vision", return_value=(vision, dots)), \
                patch.object(VisionSimulator, "simulate_nn_output", return_value=(0.0, 1.0, 0.0)):
            BurrowExperiment._stage_0(experiment)

        self.assertEqual(experiment.current_run_outcome, "never_entered")
        self.assertEqual(experiment.outcome_counts["never_entered"], 1)


if __name__ == "__main__":
    unittest.main()
