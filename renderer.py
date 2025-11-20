# -*- coding: utf-8 -*-

import pygame
from debugger import debug

class Renderer:
    
    def __init__(self, world, cell_size=20):
        self.world = world
        self.cell_size = cell_size
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.world.width * cell_size, self.world.height * cell_size)
        )
        self.font = pygame.font.SysFont('Arial', 12)
        self.clock = pygame.time.Clock()
    

    
    def draw(self):
        """Основной метод отрисовки"""
        self.screen.fill((0, 0, 0))  # Черный фон
        
        width = self.world.width    # Кэшируем в локальную переменную
        height = self.world.height
        # Отрисовка содержимого карты
        for x in range(width):
            for y in range(height):
                if self.world.get_cell(x,y) == 0:
                    pass
                elif self.world.get_cell(x,y) == 1:
                    rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size)
                    color = (50, 50, 50)
                    pygame.draw.rect(self.screen, color, rect, 0)
                elif self.world.get_cell(x,y) == 2:
                    rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size)
                    color = (255, 50, 50)
                    pygame.draw.rect(self.screen, color, rect, 0)
                elif self.world.get_cell(x,y) == 3:
                    rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size)
                    color = (50, 50, 255)
                    pygame.draw.rect(self.screen, color, rect, 0)
        
        # Отрисовка raycast_dots
        raycast_dots = debug.get("raycast_dots")
        for dot in raycast_dots:
            pygame.draw.rect(self.screen, (100,100,100), pygame.Rect(
                int(dot[0]*self.cell_size)-1, 
                int(dot[1]*self.cell_size)-1, 
                2, 2))

                
        
        # Отрисовка сущностей
        # for entity in self.world.foods:
        #     if hasattr(entity, 'get_position') and hasattr(entity, 'get_color'):
        #         x, y = entity.get_position()
        #         pixel_x = x * self.cell_size
        #         pixel_y = y * self.cell_size
                
        #         # Отрисовка тела существа
        #         pygame.draw.rect(
        #             self.screen,
        #             entity.get_color(),
        #             (pixel_x + 1, pixel_y + 1, self.cell_size - 2, self.cell_size - 2))
                
        #         # Отрисовка символа
        #         if hasattr(entity, 'get_sprite'):
        #             text = self.font.render(
        #                 entity.get_sprite(),
        #                 True,
        #                 (255, 255, 255))
        #             self.screen.blit(text, (pixel_x + 5, pixel_y + 5))
                
        #         # Отрисовка здоровья
        #         self.draw_health_bar(entity, pixel_x, pixel_y)
        
        pygame.display.flip()

    def terminate(self):
        pygame.quit()
        return(True)

    def getEvents(self):
        return pygame.event.get()

    def isGotQuitEvent(self):
        quitFlag = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitFlag = True
        return quitFlag
