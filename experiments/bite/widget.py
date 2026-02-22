# -*- coding: utf-8 -*-
"""Виджет для BiteExperiment - отображение прогресса и результатов эксперимента по кусанию."""

import numpy as np
import pygame



class BiteExperimentWidget:
    POPUP_WIDTH = 1100
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
        



        # ##########################################################################
        # Оформление окна
        # ##########################################################################

        # Центрирование
        screen_w, screen_h = screen.get_size()
        x = (screen_w - self.POPUP_WIDTH) // 2
        y = (screen_h - self.POPUP_HEIGHT) // 2
        
        # Фон
        rect = pygame.Rect(x, y, self.POPUP_WIDTH, self.POPUP_HEIGHT)
        pygame.draw.rect(screen, self.COLORS['bg'], rect)
        pygame.draw.rect(screen, self.COLORS['border'], rect, 2)
        
        # Заголовок
        title_rect = pygame.Rect(x, y, self.POPUP_WIDTH, 30)
        pygame.draw.rect(screen, self.COLORS['title_bg'], title_rect)
        title_text = self.font_title.render("BiteExperiment", True, self.COLORS['title_text'])
        screen.blit(title_text, (x + 20, y + 7))
        



        # ##########################################################################
        # Рисуем карту эксперимента
        # ##########################################################################

        # Параметры рисования матрицы
        MATRIX_START_X = 100
        MATRIX_START_Y = 100
        CELL_SIZE = 7
        
        experiment_map = experiment_dto.world


        # Рисуем матрицу карты
        map_data = experiment_map.map
        for row in range(map_data.shape[0]):
            for col in range(map_data.shape[1]):

                # Цвет сетки
                mesh_color = (40, 40, 40)
                # Нарисуем Вертикальные 
                line_start = (MATRIX_START_X + col * CELL_SIZE, MATRIX_START_Y)
                line_end = (MATRIX_START_X + col * CELL_SIZE, MATRIX_START_Y + map_data.shape[0] * CELL_SIZE)
                pygame.draw.line(screen, mesh_color, line_start, line_end)

                # Нарисуем Горизонтальные
                line_start = (MATRIX_START_X, MATRIX_START_Y + row * CELL_SIZE)
                line_end = (MATRIX_START_X + map_data.shape[1] * CELL_SIZE, MATRIX_START_Y + row * CELL_SIZE)
                pygame.draw.line(screen, mesh_color, line_start, line_end)

                # Далее - рисуем содержимое карты
                cell_x = MATRIX_START_X + col * CELL_SIZE
                cell_y = MATRIX_START_Y + row * CELL_SIZE
                cell_rect = pygame.Rect(cell_x, cell_y, CELL_SIZE, CELL_SIZE)
                
                # Определяем цвет ячейки на основе значения
                cell_value = map_data[row, col]
                if cell_value == 0:  # Пусто
                    cell_color = (10, 10, 10)
                elif cell_value == 1:  # Стена
                    cell_color = (50, 50, 50)
                elif cell_value == 2:  # Еда
                    cell_color = (219, 80, 74)
                elif cell_value == 3:  # Существо
                    cell_color = (50, 50, 255)
                else:
                    cell_color = (255, 10, 10)
                
                # Рисуем заполненный прямоугольник и границу
                pygame.draw.rect(screen, cell_color, cell_rect)
                #pygame.draw.rect(screen, (80, 80, 80), cell_rect, 1)

        # нарисуем точки Raycast
        if experiment_dto.creature_state is not None and experiment_dto.creature_state.raycast_dots is not None:
            for dot in experiment_dto.creature_state.raycast_dots:
                dot_x = MATRIX_START_X + dot[0] * CELL_SIZE
                dot_y = MATRIX_START_Y + dot[1] * CELL_SIZE
                pygame.draw.circle(screen, (255, 255, 0), (dot_x + CELL_SIZE//2, dot_y + CELL_SIZE//2), 1)
        
        # нарисуем круг четко вокруг существа
        # creature_pos = experiment_map.creature_position
        # creature_x = MATRIX_START_X + creature_pos[0] * CELL_SIZE
        # creature_y = MATRIX_START_Y + creature_pos[1] * CELL_SIZE
        # pygame.draw.circle(screen, (0, 255, 255), (creature_x, creature_y), 3, 1) 





        # ##########################################################################
        # Рисуем текущий vision input (15 лучей)
        # ##########################################################################

        # Преобразование в uint8 диапазон [0, 255]
        if experiment_dto.creature_state is not None and experiment_dto.creature_state.vision_input is not None:
            vision_int = (experiment_dto.creature_state.vision_input * 255).astype(np.uint8)
            vision_int_list = vision_int.tolist()
        # Преобразование в RGB кортежи
            rgb_tuples = list(zip(
                vision_int_list[0:15],
                vision_int_list[15:30],
                vision_int_list[30:45]
            ))
            
            # Рисуем видение в виде 15 цветных квадратов
            for i, color in enumerate(rgb_tuples):
                square_rect = pygame.Rect(x + 400, y + 60 + i * 25, 20, 20)
                pygame.draw.rect(screen, color, square_rect)
                pygame.draw.rect(screen, (80, 80, 80), square_rect, 1)
        





        # ##########################################################################
        # Информация о стадиях эксперимента и результатах
        # ##########################################################################

        # Какие данные нам могут понадобится?
        # experiment_dto.creature_id
        # experiment_dto.current_stage
        # experiment_dto.stage_run_counter
        # experiment_dto.num_runs_this_stage
        # experiment_dto.summary
        #   stage_stats = experiment_dto.summary[experiment_dto.current_stage]
        #   success_count = stage_stats.get('success', 0)
        #   total_count = stage_stats.get('total', 0)
        #   success_rate = stage_stats.get('success_rate', 0.0)



        content_y = y + 60
        lines = [
            f"Creature ID: {experiment_dto.creature_id}",
            f"Stage: {experiment_dto.current_stage}/6 (Run {experiment_dto.stage_run_counter}/{experiment_dto.num_runs_this_stage})",
            "",
            f"Results:"
        ]
        
        for line in lines:
            text_surface = self.font.render(line, True, self.COLORS['text'])
            screen.blit(text_surface, (x + 620, content_y))
            content_y += 25
        
        # Показать результаты из summary
        if experiment_dto.summary and experiment_dto.current_stage in experiment_dto.summary:
            stage_stats = experiment_dto.summary[experiment_dto.current_stage]
            
            # Основная статистика
            success_count = stage_stats.get('success', 0)
            total_count = stage_stats.get('total', 0)
            success_rate = stage_stats.get('success_rate', 0.0)
            
            stats_lines = [
                f"Total runs: {total_count}/{experiment_dto.num_runs_this_stage}",
                f"Success: {success_count}  Fail: {stage_stats.get('fail', 0)}",
                f"Success rate: {success_rate*100:.1f}%",
            ]
            
            print (f"[WIDGET] Drawing stats for stage {experiment_dto.current_stage}: "
                   f"Total={total_count}, Success={success_count}, Rate={success_rate*100:.1f}%")

            for line in stats_lines:
                color = self.COLORS['success'] if 'Success:' in line and success_count > total_count // 2 else self.COLORS['text']
                if 'rate' in line and success_rate > 0.5:
                    color = self.COLORS['success']
                text_surface = self.font.render(line, True, color)
                screen.blit(text_surface, (x + 620, content_y))
                content_y += 25


            
        # Выводим блоки информации по каждой стадии эксперимента
        # for stage in range(1, 7):
        #     stage_y = y + 60 + (6 + stage) * 25
        #     stage_text = f"Stage {stage}: "
        #     if experiment_dto.summary and stage in experiment_dto.summary:
        #         stage_stats = experiment_dto.summary[stage]
        #         success_count = stage_stats.get('success', 0)
        #         total_count = stage_stats.get('total', 0)
        #         success_rate = stage_stats.get('success_rate', 0.0)
        #         stage_text += f"Success {success_count}/{total_count} ({success_rate*100:.1f}%)"
        #     else:
        #         stage_text += "No data"
            
        #     text_surface = self.font.render(stage_text, True, self.COLORS['text'])
        #     screen.blit(text_surface, (x + 20, stage_y))

            
        
        # Реализуем небольшую паузу между кадрами
        pygame.time.delay(500)




