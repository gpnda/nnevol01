# -*- coding: utf-8 -*-
"""Виджет для BiteExperiment - отображение прогресса и результатов эксперимента по кусанию."""

import pygame

class BiteExperimentWidget:
    POPUP_WIDTH = 700
    POPUP_HEIGHT = 500
    FONT_SIZE = 14
    COLORS = {
        'bg': (5, 41, 158),
        'border': (170, 170, 170),
        'title_bg': (0, 167, 225),
        'title_text': (0, 0, 0),
        'text': (170, 170, 170),
        'success': (0, 255, 100),
        'fail': (255, 100, 100),
    }
    
    def __init__(self):
        try:
            self.font = pygame.font.Font('./tests/Ac437_Siemens_PC-D.ttf', self.FONT_SIZE)
            self.font_title = pygame.font.Font('./tests/Ac437_Siemens_PC-D.ttf', self.FONT_SIZE + 4)
        except:
            self.font = pygame.font.Font(None, self.FONT_SIZE)
            self.font_title = pygame.font.Font(None, self.FONT_SIZE + 4)
    
    def draw(self, screen: pygame.Surface, experiment_dto):
        if experiment_dto is None:
            return
        
        # Центрирование
        screen_w, screen_h = screen.get_size()
        x = (screen_w - self.POPUP_WIDTH) // 2
        y = (screen_h - self.POPUP_HEIGHT) // 2
        
        # Фон
        rect = pygame.Rect(x, y, self.POPUP_WIDTH, self.POPUP_HEIGHT)
        pygame.draw.rect(screen, self.COLORS['bg'], rect)
        pygame.draw.rect(screen, self.COLORS['border'], rect, 2)
        
        # Заголовок
        title_rect = pygame.Rect(x, y, self.POPUP_WIDTH, 40)
        pygame.draw.rect(screen, self.COLORS['title_bg'], title_rect)
        title_text = self.font_title.render("BiteExperiment", True, self.COLORS['title_text'])
        screen.blit(title_text, (x + 20, y + 10))
        
        # Контент
        content_y = y + 60
        lines = [
            f"Creature ID: {experiment_dto.creature_id}",
            f"Stage: {experiment_dto.current_stage}/6 (Run {experiment_dto.stage_run_counter}/20)",
            "",
            f"Results: {experiment_dto.random_value:.2f}"
        ]
        
        for line in lines:
            text_surface = self.font.render(line, True, self.COLORS['text'])
            screen.blit(text_surface, (x + 20, content_y))
            content_y += 25
        
        # Показать результаты из summary
        # Пока заглушено, статистика не собирается

