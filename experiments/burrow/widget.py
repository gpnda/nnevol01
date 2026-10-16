# -*- coding: utf-8 -*-
"""Виджет результатов эксперимента с норками."""

from typing import Any, Callable, Optional

import pygame


class BurrowExperimentWidget:
    POPUP_WIDTH = 1100
    POPUP_HEIGHT = 650
    FONT_SIZE = 20
    COLORS = {
        "bg": (5, 41, 158),
        "border": (170, 170, 170),
        "title_bg": (0, 167, 225),
        "title_text": (0, 0, 0),
        "text": (230, 230, 230),
        "open": (10, 10, 10),
        "wall": (70, 70, 70),
        "burrow": (142, 85, 45),
        "creature": (50, 100, 255),
        "ray": (255, 230, 40),
        "stayed": (60, 230, 110),
        "entered_then_left": (255, 170, 40),
        "never_entered": (255, 90, 90),
    }
    OUTCOME_LABELS = {
        "stayed": "Stayed in burrow",
        "entered_then_left": "Entered, then left",
        "never_entered": "Never entered",
    }

    def __init__(self, on_parameter_change: Optional[Callable[[str, Any], None]] = None):
        self.on_parameter_change = on_parameter_change
        self.input_buffer = "500"
        self.input_edited = False
        try:
            self.font = pygame.font.Font("./tests/Ac437_Siemens_PC-D.ttf", self.FONT_SIZE)
            self.title_font = pygame.font.Font("./tests/Ac437_Siemens_PC-D.ttf", self.FONT_SIZE + 4)
            self.small_font = pygame.font.Font("./tests/Ac437_Siemens_PC-D.ttf", self.FONT_SIZE - 4)
        except (FileNotFoundError, pygame.error):
            self.font = pygame.font.Font(None, self.FONT_SIZE)
            self.title_font = pygame.font.Font(None, self.FONT_SIZE + 4)
            self.small_font = pygame.font.Font(None, self.FONT_SIZE - 4)

    def draw(self, screen: pygame.Surface, experiment_dto) -> None:
        if experiment_dto is None:
            return

        screen_width, screen_height = screen.get_size()
        x = (screen_width - self.POPUP_WIDTH) // 2
        y = (screen_height - self.POPUP_HEIGHT) // 2
        popup = pygame.Rect(x, y, self.POPUP_WIDTH, self.POPUP_HEIGHT)
        pygame.draw.rect(screen, self.COLORS["bg"], popup)
        pygame.draw.rect(screen, self.COLORS["border"], popup, 2)
        pygame.draw.rect(
            screen,
            self.COLORS["title_bg"],
            pygame.Rect(x, y, self.POPUP_WIDTH, 32),
        )
        self._draw_text(screen, "Burrow Experiment", x + 18, y + 5, self.title_font, self.COLORS["title_text"])

        if experiment_dto.awaiting_parameter_selection:
            self._draw_text(screen, "Required continuous stay in burrow (ticks):", x + 40, y + 100)
            self._draw_text(screen, self.input_buffer or "0", x + 40, y + 145, self.title_font)
            self._draw_text(screen, "Type 1-10000, then press Enter. Backspace edits.", x + 40, y + 195, self.small_font)
            return

        map_data = experiment_dto.world.map
        map_height, map_width = map_data.shape
        map_x, map_y = x + 25, y + 55
        available_width, available_height = 500, 500
        cell_size = max(1, min(available_width // map_width, available_height // map_height))

        for row in range(map_height):
            for col in range(map_width):
                if map_data[row, col] == 1:
                    color = self.COLORS["wall"]
                elif experiment_dto.burrow_mask[row, col]:
                    color = self.COLORS["burrow"]
                else:
                    color = self.COLORS["open"]
                cell = pygame.Rect(
                    map_x + col * cell_size,
                    map_y + row * cell_size,
                    cell_size,
                    cell_size,
                )
                pygame.draw.rect(screen, color, cell)
                pygame.draw.rect(screen, (40, 40, 40), cell, 1)

        creature_state = experiment_dto.creature_state
        if creature_state is not None:
            for dot in creature_state.raycast_dots:
                px = map_x + int(float(dot[0]) * cell_size + cell_size / 2)
                py = map_y + int(float(dot[1]) * cell_size + cell_size / 2)
                pygame.draw.circle(screen, self.COLORS["ray"], (px, py), 1)
            creature_x = map_x + int(creature_state.x * cell_size + cell_size / 2)
            creature_y = map_y + int(creature_state.y * cell_size + cell_size / 2)
            pygame.draw.circle(screen, self.COLORS["creature"], (creature_x, creature_y), max(2, cell_size // 2))

        stats_x = map_x + available_width + 35
        stats_y = map_y
        self._draw_text(screen, f"Creature: {experiment_dto.creature_id}", stats_x, stats_y)
        completed_runs = sum(experiment_dto.outcomes.values())
        current_run = min(completed_runs + 1, experiment_dto.total_runs)
        if not experiment_dto.is_running and completed_runs >= experiment_dto.total_runs:
            current_run = experiment_dto.total_runs
        self._draw_text(screen, f"Run: {current_run} / {experiment_dto.total_runs}", stats_x, stats_y + 35)
        self._draw_text(screen, f"Tick: {experiment_dto.ticks_in_run}", stats_x, stats_y + 70)
        if experiment_dto.entry_tick is not None:
            self._draw_text(screen, f"Entered burrow at tick: {experiment_dto.entry_tick}", stats_x, stats_y + 105)
        self._draw_text(screen, f"Required stay: {experiment_dto.burrow_stay_ticks} ticks", stats_x, stats_y + 140)
        self._draw_text(screen, "Outcomes:", stats_x, stats_y + 160)

        for index, outcome in enumerate(self.OUTCOME_LABELS):
            label = self.OUTCOME_LABELS[outcome]
            count = experiment_dto.outcomes[outcome]
            self._draw_text(
                screen,
                f"{label}: {count}",
                stats_x,
                stats_y + 200 + index * 38,
                color=self.COLORS[outcome],
            )

        if experiment_dto.current_run_outcome:
            outcome_text = self.OUTCOME_LABELS[experiment_dto.current_run_outcome]
            self._draw_text(screen, f"Last run: {outcome_text}", stats_x, stats_y + 330)
        status = "Running" if experiment_dto.is_running else "Finished"
        self._draw_text(screen, status, stats_x, stats_y + 380, color=self.COLORS["text"])

    def _draw_text(self, screen, text, x, y, font=None, color=None) -> None:
        surface = (font or self.font).render(
            text, True, color or self.COLORS["text"]
        )
        screen.blit(surface, (x, y))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type != pygame.KEYDOWN:
            return False
        if event.key == pygame.K_BACKSPACE:
            self.input_buffer = self.input_buffer[:-1]
            self.input_edited = True
            return True
        if event.key == pygame.K_RETURN:
            if not self.input_buffer or self.on_parameter_change is None:
                return True
            value = int(self.input_buffer)
            if 1 <= value <= 10000:
                self.on_parameter_change("burrow_stay_ticks", value)
            return True
        if pygame.K_0 <= event.key <= pygame.K_9:
            if not self.input_edited:
                self.input_buffer = ""
                self.input_edited = True
            if len(self.input_buffer) < 5:
                self.input_buffer += str(event.key - pygame.K_0)
            return True
        return False
