# -*- coding: utf-8 -*-
"""Виджет для ConeExperiment - отображение эксперимента с конусом."""

import numpy as np
import pygame



class ConeExperimentWidget:
    POPUP_WIDTH = 1100
    POPUP_HEIGHT = 500
    FONT_SIZE = 20
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
            self.small_font = pygame.font.Font('./tests/Ac437_Siemens_PC-D.ttf', self.FONT_SIZE - 4)
        except:
            self.font = pygame.font.Font(None, self.FONT_SIZE)
            self.font_title = pygame.font.Font(None, self.FONT_SIZE + 4)
            self.small_font = pygame.font.Font(None, self.FONT_SIZE - 4)
    
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
        title_text = self.font_title.render("ConeExperiment", True, self.COLORS['title_text'])
        screen.blit(title_text, (x + 20, y + 7))
        



        # ##########################################################################
        # Рисуем карту эксперимента
        # ##########################################################################

        # Параметры рисования матрицы
        MATRIX_START_X = 100
        MATRIX_START_Y = 100
        CELL_SIZE = 15
        
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
        if experiment_dto.creature_state is not None:
            creature_x = MATRIX_START_X + experiment_dto.creature_state.x * CELL_SIZE
            creature_y = MATRIX_START_Y + experiment_dto.creature_state.y * CELL_SIZE
            pygame.draw.circle(screen, (255, 255, 255), (creature_x + CELL_SIZE//2, creature_y + CELL_SIZE//2), CELL_SIZE//2, 1)





        # ##########################################################################
        # Рисуем текущий vision input (15 лучей)
        # ##########################################################################

        # Определить координату левого края виджета
        screen_w, screen_h = screen.get_size()
        x = (screen_w - self.POPUP_WIDTH) // 2
        y = (screen_h - self.POPUP_HEIGHT) // 2
        
        VISION_MATRIX_X = x + 25
        VISION_MATRIX_Y = y + 420
        VISION_CELL_SIZE = 17

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
            
            # Рисуем видение в виде 15 цветных квадратов (горизонтально)
            for i, color in enumerate(rgb_tuples):
                square_rect = pygame.Rect(VISION_MATRIX_X + i * VISION_CELL_SIZE, VISION_MATRIX_Y, VISION_CELL_SIZE, VISION_CELL_SIZE)
                pygame.draw.rect(screen, color, square_rect)
                pygame.draw.rect(screen, (80, 80, 80), square_rect, 1)
        





        # ##########################################################################
        # Информация о стадиях эксперимента и результатах
        # ##########################################################################
        # Нарисуем таблицу с ходом эксперимента, на основании данных из: 
        #    experiment_dto.plan
        #    experiment_dto.stats
        # TABLE_STATS_X = 500
        # TABLE_STATS_Y = 150
        # TABLE_LINE_HEIGHT = 25
        # COLUMN_WIDTHS = [250, 40, 100, 50, 50]  # ширина каждой колонки
        # PADDING = 3
        # OFFSET_Y = -5

        # # Draw table header
        # header_text = self.font.render("Experiment Stages Progress", False, self.COLORS['text'])
        # screen.blit(header_text, (TABLE_STATS_X, TABLE_STATS_Y - 40))

        # # Сначала нарисуем все стадии экспмеримента и их статус
        # if experiment_dto.plan is not None:
        #     for stage_num, stage_info in enumerate(experiment_dto.plan):
        #         # Получим статистику по количеству прогонов и успешных прогонов для этой стадии
        #         # Все данные по идее хранятся в experiment_dto.stats, который содержит stats_collector.get_all_stages_stats()
        #         stage_stats = experiment_dto.stats.get(stage_num, {})
        #         total_runs = stage_stats.get('total', 0)        # Всего прогонов
        #         success_runs = stage_stats.get('success', 0)    # Успешных
        #         fail_runs = total_runs - success_runs           # Неудачных
        #         success_rate = int(success_runs / total_runs * 100) if total_runs > 0 else 0
        #         goal_treshold = int(stage_info['result_threshold']*100)


                
        #         # Первая колонка - название номер стадии
        #         text_surface = self.small_font.render(f"{stage_num}. {stage_info['stage_name']}", False, self.COLORS['text'])
        #         screen.blit(text_surface, (TABLE_STATS_X, TABLE_STATS_Y + stage_num * TABLE_LINE_HEIGHT))
                
        #         # Вторая колонка - порог успеха для стадии в виде текста
        #         text_surface = self.small_font.render(f"{goal_treshold}%", False, self.COLORS['text'])
        #         screen.blit(text_surface, (TABLE_STATS_X + COLUMN_WIDTHS[0], TABLE_STATS_Y + stage_num * TABLE_LINE_HEIGHT))

        #         # Третья колонка - success_rate в виде прогресс-бара
        #         # Рисуем рамку вокруг прогресс-бара
        #         progress_bar_rect = pygame.Rect(TABLE_STATS_X + COLUMN_WIDTHS[0] + COLUMN_WIDTHS[1] + PADDING, 
        #                                         TABLE_STATS_Y + stage_num * TABLE_LINE_HEIGHT + PADDING + OFFSET_Y,
        #                                         COLUMN_WIDTHS[2] - PADDING*2, TABLE_LINE_HEIGHT - PADDING*2)
        #         pygame.draw.rect(screen, (80, 80, 80), progress_bar_rect, 1)

        #         # Заполняем прогресс-бар в зависимости от success_rate
        #         progress_width = int((success_rate / 100) * COLUMN_WIDTHS[2])
        #         progress_rect = pygame.Rect(TABLE_STATS_X + COLUMN_WIDTHS[0] + COLUMN_WIDTHS[1] + PADDING + 2 , 
        #                                         TABLE_STATS_Y + stage_num * TABLE_LINE_HEIGHT + PADDING + OFFSET_Y + 2,
        #                                         progress_width - PADDING*2 - 4, TABLE_LINE_HEIGHT - PADDING*2 - 4)
        #         pygame.draw.rect(screen, self.COLORS['success'], progress_rect)

                
        #         # Внутри прогресс-бара напишем текстом процент успеха
        #         text_surface = self.small_font.render(f"{success_rate}%", False, self.COLORS['text'])
        #         text_rect = text_surface.get_rect(center=progress_bar_rect.center)
        #         screen.blit(text_surface, text_rect)

        #         # Обозначим полоской порог успеха (goal_treshold)
        #         threshold_x = TABLE_STATS_X + COLUMN_WIDTHS[0] + COLUMN_WIDTHS[1] + PADDING + int((goal_treshold / 100) * (COLUMN_WIDTHS[2] - PADDING*2))
        #         pygame.draw.line(screen, self.COLORS['fail'], (threshold_x, TABLE_STATS_Y + stage_num * TABLE_LINE_HEIGHT + PADDING + OFFSET_Y), (threshold_x, TABLE_STATS_Y + stage_num * TABLE_LINE_HEIGHT + TABLE_LINE_HEIGHT - PADDING + OFFSET_Y), 2)    


        #         # Четвертая колонка - текстом plan_runs
        #         # Если данная стадия является текущей стадией эксперимента
        #         if stage_num == experiment_dto.current_stage:
        #             # Нарисуем рамку вокруг этой колонки
        #             current_stage_rect = pygame.Rect(TABLE_STATS_X + COLUMN_WIDTHS[0] + COLUMN_WIDTHS[1] + COLUMN_WIDTHS[2], 
        #                                                 TABLE_STATS_Y + stage_num * TABLE_LINE_HEIGHT + PADDING + OFFSET_Y,
        #                                                 COLUMN_WIDTHS[3] + COLUMN_WIDTHS[4], TABLE_LINE_HEIGHT - PADDING*2 )
        #             pygame.draw.rect(screen, self.COLORS['text'], current_stage_rect, 1)
        #             # Заполним прогресс-бар в зависимости от количества прогонов внутри стадии
        #             progress_width = int((total_runs / stage_info['num_runs']) * (COLUMN_WIDTHS[3] + COLUMN_WIDTHS[4])) - 4
        #             progress_rect = pygame.Rect(current_stage_rect.x + 2 , current_stage_rect.y + 2, progress_width, current_stage_rect.height - 4)
        #             pygame.draw.rect(screen, self.COLORS['success'], progress_rect)
        #             # Внутри прогресс-бара напишем текстом количество прогонов внутри стадии
        #             text_surface = self.small_font.render(f"{total_runs}/{stage_info['num_runs']}", False, self.COLORS['text'])
        #             text_rect = text_surface.get_rect(center=current_stage_rect.center)
        #             screen.blit(text_surface, text_rect)
        #         else:
        #             # Хочу тут текст внутри ячейки по центру
        #             text_surface = self.small_font.render(f"{stage_info['num_runs']}", False, self.COLORS['text'])
        #             text_rect = text_surface.get_rect(center=(TABLE_STATS_X + COLUMN_WIDTHS[0] + COLUMN_WIDTHS[1] + COLUMN_WIDTHS[2] + COLUMN_WIDTHS[3] // 2, 
        #                                                       TABLE_STATS_Y + stage_num * TABLE_LINE_HEIGHT + PADDING + OFFSET_Y + (TABLE_LINE_HEIGHT - PADDING*2) // 2))
        #             screen.blit(text_surface, text_rect)

                
                
        #         # Пятая колонка - текстом, если success_rate> goal_treshold to пишем pass иначе пишем fail
        #         if total_runs == stage_info['num_runs']:
        #             result_text = "PASS" if success_rate >= goal_treshold else "FAIL"
        #             # draw tag background
        #             tag_color = self.COLORS['success'] if result_text == "PASS" else self.COLORS['fail']
        #             tag_rect = pygame.Rect(TABLE_STATS_X + COLUMN_WIDTHS[0] + COLUMN_WIDTHS[1] + COLUMN_WIDTHS[2] + COLUMN_WIDTHS[3], 
        #                                     TABLE_STATS_Y + stage_num * TABLE_LINE_HEIGHT + PADDING + OFFSET_Y,
        #                                     COLUMN_WIDTHS[4], TABLE_LINE_HEIGHT - PADDING*2)
        #             pygame.draw.rect(screen, tag_color, tag_rect)
        #             text_surface = self.small_font.render(result_text, False, self.COLORS['text'])
        #             text_rect = text_surface.get_rect(center=tag_rect.center)
        #             screen.blit(text_surface, text_rect)

                
        # Реализуем небольшую паузу между кадрами
        # pygame.time.delay(500)




