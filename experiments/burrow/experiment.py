# -*- coding: utf-8 -*-
"""Эксперимент: движение существа от центра карты к норкам."""

import csv
import math
import random
from pathlib import Path

import numpy as np

from experiments.base.dto import ExperimentCreatureStateDTO, ExperimentWorldStateDTO
from experiments.base.staged_experiment_base import StagedExperimentBase
from experiments.burrow.dto import BurrowExperimentDTO
from experiments.toolbox import ScenarioBuilder, StatsCollector, VisionSimulator
from world import World


class BurrowExperiment(StagedExperimentBase):
    MAP_FILENAME = "burrows.csv"
    DEFAULT_NUM_RUNS = 1000
    DEFAULT_BURROW_STAY_TICKS = 500
    DEFAULT_MAX_TICKS_PER_RUN = 2000
    MAX_BURROW_STAY_TICKS = 10000

    OUTCOMES = ("stayed", "entered_then_left", "never_entered")

    def __init__(self, target_creature_id: int, world: World):
        super().__init__(target_creature_id, world)

        self.plan = [{
            "stage_method": self._stage_0,
            "stage_name": "Find and stay in a burrow",
            "num_runs": self.DEFAULT_NUM_RUNS,
            "result_threshold": 0.0,
        }]

        self.inspecting_creature = ScenarioBuilder.copy_creature(self.target_creature)
        self.test_world, self.burrow_mask = self._load_experiment_map(
            Path(__file__).with_name(self.MAP_FILENAME)
        )
        self.center_x = self.test_world.width / 2.0
        self.center_y = self.test_world.height / 2.0
        center_cell = (int(self.center_y), int(self.center_x))
        if self.burrow_mask[center_cell]:
            raise ValueError("The center cell of the burrow experiment map must be empty.")
        if self.test_world.walls_map[center_cell] == 1:
            raise ValueError("The center cell of the burrow experiment map cannot be a wall.")
        if not np.any(self.burrow_mask):
            raise ValueError("The burrow experiment map must contain at least one burrow (value 9).")

        self.stats_collector = StatsCollector()
        self.outcome_counts = {outcome: 0 for outcome in self.OUTCOMES}
        self.ticks_in_run = 0
        self.consecutive_burrow_ticks = 0
        self.has_entered_burrow = False
        self.entry_tick = None
        self.run_finished = False
        self.current_run_outcome = None
        self.current_creature_state = None
        self.burrow_stay_ticks = self.DEFAULT_BURROW_STAY_TICKS
        self.awaiting_parameter_selection = True
        self._reset_run()
        self.test_world.add_creature(self.inspecting_creature)

    @staticmethod
    def _load_experiment_map(path: Path) -> tuple[World, np.ndarray]:
        """Load a semicolon-delimited 0/1/9 map without adding random entities."""
        if not path.is_file():
            raise FileNotFoundError(
                f"Burrow experiment map not found: {path}. "
                f"Place the experiment map at {path.name}."
            )

        rows = []
        with path.open("r", newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.reader(csv_file, delimiter=";")
            for line_number, row in enumerate(reader, start=1):
                if not row or all(not cell.strip() for cell in row):
                    continue
                try:
                    values = [int(cell.strip()) for cell in row if cell.strip()]
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid integer in burrow map {path} at line {line_number}."
                    ) from exc
                rows.append(values)

        if not rows:
            raise ValueError(f"Burrow experiment map is empty: {path}")
        width = len(rows[0])
        if width == 0 or any(len(row) != width for row in rows):
            raise ValueError(f"Burrow experiment map rows have different lengths: {path}")

        map_data = np.asarray(rows, dtype=np.int32)
        invalid_values = set(np.unique(map_data).tolist()) - {0, 1, 9}
        if invalid_values:
            raise ValueError(
                f"Unsupported value(s) in burrow map {path}: {sorted(invalid_values)}. "
                "Use 0 for open space, 1 for walls, and 9 for burrows."
            )

        test_world = ScenarioBuilder.create_test_world(width, len(rows))
        test_world.walls_map = (map_data == 1).astype(np.int32)
        test_world.map = test_world.walls_map.copy()
        return test_world, map_data == 9

    def _reset_run(self) -> None:
        creature = self.inspecting_creature
        creature.x = self.center_x
        creature.y = self.center_y
        creature.angle = random.uniform(0.0, math.tau)
        creature.speed = 1.0
        creature.energy = 1.0
        creature.health = 1.0
        creature.age = 0
        creature.bite_effort = 0.0
        creature.input_hurting = 0.0
        creature.input_starving = 0.0
        creature.input_wayblocked = 0.0
        creature.input_bite_success = 0.0

        self.ticks_in_run = 0
        self.consecutive_burrow_ticks = 0
        self.has_entered_burrow = False
        self.entry_tick = None
        self.run_finished = False
        self.current_run_outcome = None
        self.current_creature_state = None
        self.test_world.update_map()

    def start(self) -> None:
        super().start()
        self._reset_run()

    def _stage_0(self) -> None:
        if self.run_finished:
            self._reset_run()

        vision, raycast_dots = VisionSimulator.get_creature_vision(
            self.test_world, self.inspecting_creature
        )
        out_angle, out_speed, bite_output = VisionSimulator.simulate_nn_output(
            self.inspecting_creature, vision
        )
        angle, speed, new_x, new_y = World.apply_outs(
            creature_x=self.inspecting_creature.x,
            creature_y=self.inspecting_creature.y,
            creature_angle=self.inspecting_creature.angle,
            creature_speed=self.inspecting_creature.speed,
            out_angle=out_angle,
            out_speed=out_speed,
        )
        self.inspecting_creature.angle = angle
        self.inspecting_creature.speed = speed
        self.inspecting_creature.input_wayblocked = 0.0

        cell_x = int(new_x)
        cell_y = int(new_y)
        in_bounds = 0 <= cell_x < self.test_world.width and 0 <= cell_y < self.test_world.height
        if in_bounds and self.test_world.walls_map[cell_y, cell_x] != 1:
            self.inspecting_creature.x = new_x
            self.inspecting_creature.y = new_y
        else:
            self.inspecting_creature.input_wayblocked = 1.0

        self.inspecting_creature.input_bite_success = 0.0
        self.ticks_in_run += 1

        creature_cell_x = int(self.inspecting_creature.x)
        creature_cell_y = int(self.inspecting_creature.y)
        in_burrow = bool(self.burrow_mask[creature_cell_y, creature_cell_x])
        if in_burrow:
            if not self.has_entered_burrow:
                self.entry_tick = self.ticks_in_run
            self.has_entered_burrow = True
            self.consecutive_burrow_ticks += 1
        elif self.has_entered_burrow:
            self._update_creature_state(vision, (out_angle, out_speed, bite_output), raycast_dots)
            self.test_world.update_map()
            self._finish_run("entered_then_left")
            return
        else:
            self.consecutive_burrow_ticks = 0

        self._update_creature_state(vision, (out_angle, out_speed, bite_output), raycast_dots)
        self.test_world.update_map()

        if self.consecutive_burrow_ticks >= self.burrow_stay_ticks:
            self._finish_run("stayed")
        elif self.ticks_in_run >= max(
            self.DEFAULT_MAX_TICKS_PER_RUN, self.burrow_stay_ticks + 1
        ):
            self._finish_run("never_entered")

    def _update_creature_state(self, vision, outputs, raycast_dots) -> None:
        self.current_creature_state = ExperimentCreatureStateDTO(
            x=self.inspecting_creature.x,
            y=self.inspecting_creature.y,
            angle=self.inspecting_creature.angle,
            vision_input=vision,
            nn_outputs=tuple(float(value) for value in outputs),
            raycast_dots=raycast_dots,
        )

    def _finish_run(self, outcome: str) -> None:
        self.current_run_outcome = outcome
        self.run_finished = True
        self.outcome_counts[outcome] += 1
        self.stats_collector.add_run(
            stage=self.current_stage,
            success=(outcome == "stayed"),
            outcome=outcome,
            ticks=self.ticks_in_run,
            consecutive_burrow_ticks=self.consecutive_burrow_ticks,
            entry_tick=self.entry_tick,
        )
        self.stage_run_counter_increment()
        if not self.is_running:
            self.finish_experiment()

    def get_experiment_dto(self) -> BurrowExperimentDTO:
        return BurrowExperimentDTO(
            creature_id=self.target_creature.id,
            is_running=self.is_running,
            current_stage=self.current_stage,
            stage_run_counter=self.stage_run_counter,
            world=ExperimentWorldStateDTO(
                map=self.test_world.map,
                width=self.test_world.width,
                height=self.test_world.height,
            ),
            burrow_mask=self.burrow_mask,
            creature_state=self.current_creature_state,
            outcomes=self.outcome_counts.copy(),
            total_runs=self.plan[0]["num_runs"],
            ticks_in_run=self.ticks_in_run,
            entry_tick=self.entry_tick,
            burrow_stay_ticks=self.burrow_stay_ticks,
            current_run_outcome=self.current_run_outcome,
            awaiting_parameter_selection=self.awaiting_parameter_selection,
        )

    def _get_total_stages(self) -> int:
        return len(self.plan)

    def set_parameter(self, param_name: str, value) -> None:
        if param_name != "burrow_stay_ticks":
            raise ValueError(f"Unknown burrow experiment parameter: {param_name}")
        stay_ticks = int(value)
        if not 1 <= stay_ticks <= self.MAX_BURROW_STAY_TICKS:
            raise ValueError(
                f"burrow_stay_ticks must be between 1 and {self.MAX_BURROW_STAY_TICKS}."
            )
        self.burrow_stay_ticks = stay_ticks
        if self.awaiting_parameter_selection:
            self.awaiting_parameter_selection = False
            self.start()

    def finish_experiment(self) -> None:
        total = sum(self.outcome_counts.values())
        print(f"Burrow experiment summary for creature {self.target_creature.id}:")
        print(f"  Runs: {total}")
        for outcome in self.OUTCOMES:
            count = self.outcome_counts[outcome]
            rate = 100.0 * count / total if total else 0.0
            print(f"  {outcome}: {count} ({rate:.1f}%)")
