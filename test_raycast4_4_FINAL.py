import pygame
import random
import math

# Ваш метод (скопирован из вашего запроса)
def fast_get_all_visions(map, creatures_pos):
    step = 0.9 # шаг перемещения взгляда (для raycast - дистанция на котороую двигаем вперед указатель)
    resolution = 15 # разрешение взгляда - по сути сколько лучше отправит raycast?
    angleofview = 1.04719 # это примерно 60 градусов
    anglestep = 1.04719 / resolution
    raycast_dots = []
    all_visions = []

    for index, cr in enumerate(creatures_pos):
        vision = []
        visionRed = []
        visionGreen = []
        visionBlue = []
        
        for a in range(resolution):
            adelta = -1*angleofview/2 + a*anglestep
            d = 0
            cur_vision = 0
            while d < cr[3]:
                d += step
                x = cr[0] + d*math.cos(cr[2]+adelta)
                y = cr[1] + d*math.sin(cr[2]+adelta)
                if int(x) == int(cr[0]) and int(y) == int(cr[1]):
                    continue # Если смотрит на свое тело, то пропустим эту итерацию
                if True: #index == 0
                    raycast_dots.append([x , y])
                dot = 0

                ix = int(x)
                iy = int(y)
                mw = len(map[0])
                mh = len(map)
                if ix < 0 or ix >= mw or iy < 0 or iy >= mh:
                    # за пределами карты → чёрный
                    vision.append(0)
                    visionRed.append(0)
                    visionGreen.append(0)
                    visionBlue.append(0)
                    break
                else:
                    dot = map[iy][ix]
                
                # Если взгляд во что-то уперся, то Сохраняем цвет точки и Прерываем raycast
                if dot > 0:
                    cur_vision = dot
                    # Сюда надо вставлять опреденений цветов и разложение на каналы.
                    dotColor = []
                    if dot == 1:
                        dotColor = [255,0,0]
                    elif dot == 2:
                        dotColor = [0,0,255]
                    elif dot == 3:
                        dotColor = [0,255,0]
                    else:
                        dotColor = [0,0,0]
                
                    # Сюда вставляем искажение цвета, в зависимости от дистанции
                    # Условие нужно, потому что иногда d улетает больше чем self.viewdistance, 
                    # тогда цвет станет больше 255
                    # if d < self.viewdistance:
                    #     dotColor = Creature.__fadeColors(dotColor , d/self.viewdistance )


                    vision.append(cur_vision)
                    # тут переменная dotColor содержит RGB Представление цвета
                    visionRed.append(dotColor[0])
                    visionGreen.append(dotColor[1])
                    visionBlue.append(dotColor[2])
                    break

            else:
                # В этой ветке обслуживаем ситуацию, когда Raycast достиг 
                # максимальной дистанции взгляда и ничего не увидел
                vision.append(0)
                visionRed.append(0)
                visionGreen.append(0)
                visionBlue.append(0)
            
        # Превратим массив элементами карты в массив с цветами
        visionRGB = visionRed + visionGreen + visionBlue
        visionResult = visionRGB
        # print("visionRed: " + str(visionRed))
        # print("visionGreen: " + str(visionGreen))
        # print("visionBlue: " + str(visionBlue))

        all_visions.append(visionResult)
        
    print("Длина массива all_visions: " + str(len(all_visions)))
    for index,v in enumerate(all_visions):
        print("Длина " + str(index) + " массива vision: " + str(len(v)))
    return all_visions, raycast_dots



def print_vision_array(vision):
    if len(vision) != 45:
        print("Массив не содержит 45 значений. А содержит: " + str(len(vision)))
        

    red_part = vision[:15]
    green_part = vision[15:30]
    blue_part = vision[30:45]

    def format_row(part):
        return " ".join(f"{val:3}" for val in part)

    print("Red:  ", format_row(red_part))
    print("Green:", format_row(green_part))
    print("Blue: ", format_row(blue_part))

# Инициализация Pygame
pygame.init()
cell_size = 20
map_width = 30
map_height = 30
map_panel_width = map_width * cell_size  # Ширина области карты
panel_width = 1000  # Ширина правой панели
screen_width = map_panel_width + panel_width
screen_height = map_height * cell_size
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("RayCast Test Stand")
clock = pygame.time.Clock()

# Создаем отдельную поверхность для карты
map_surface = pygame.Surface((map_panel_width, screen_height))

# Переменные для масштабирования и перемещения
zoom_level = 1.0
offset_x = 0
offset_y = 0
dragging = False
drag_start_x = 0
drag_start_y = 0

def generate_map():
    # Создаем пустую карту
    game_map = [[0 for _ in range(map_width)] for _ in range(map_height)]
    
    # Добавляем случайные препятствия
    for _ in range(50):  # 50 случайных препятствий
        x = random.randint(0, map_width - 1)
        y = random.randint(0, map_height - 1)
        game_map[y][x] = random.randint(1, 3)  # 1 - красный, 2 - синий, 3 - зеленый
    
    return game_map

def generate_creatures():
    creatures = []
    for _ in range(5):
        x = random.uniform(0.5, map_width - 1.5)
        y = random.uniform(0.5, map_height - 1.5)
        angle = random.uniform(0, 2 * math.pi)  # угол направления
        view_distance = 10.0  # максимальная дистанция зрения
        creatures.append([x, y, angle, view_distance])
    return creatures

def draw_map(map_surface, game_map):
    # Очищаем поверхность карты
    map_surface.fill((0, 0, 0))
    
    for y in range(map_height):
        for x in range(map_width):
            # Применяем масштабирование и смещение
            rect_x = (x * cell_size * zoom_level) + offset_x
            rect_y = (y * cell_size * zoom_level) + offset_y
            rect_width = cell_size * zoom_level
            rect_height = cell_size * zoom_level
            
            # Проверяем, находится ли клетка в пределах поверхности карты
            if (rect_x + rect_width < 0 or rect_x > map_panel_width or 
                rect_y + rect_height < 0 or rect_y > screen_height):
                continue
                
            rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
            if game_map[y][x] == 1:
                color = (255, 0, 0)  # Красный
            elif game_map[y][x] == 2:
                color = (0, 0, 255)  # Синий
            elif game_map[y][x] == 3:
                color = (0, 255, 0)  # Зеленый
            else:
                color = (0, 0, 0)  # Черный
            pygame.draw.rect(map_surface, color, rect)
            pygame.draw.rect(map_surface, (40, 40, 40), rect, 1)  # Сетка

def draw_vision_panel(screen, selected_index, all_visions):
    panel_x = map_panel_width  # Начало панели справа от карты
    panel_y = 0
    box_size = 50
    spacing = 10   # Увеличено для пропорциональности

    if selected_index is not None and selected_index < len(all_visions):
        vision = all_visions[selected_index]
        num_segments = 15
        red_part = vision[:num_segments]
        green_part = vision[num_segments:2*num_segments]
        blue_part = vision[2*num_segments:3*num_segments]

        font = pygame.font.SysFont(None, 18)

        for i in range(num_segments):
            color = (red_part[i], green_part[i], blue_part[i])
            rect_x = panel_x + 10 + i * (box_size + spacing)  # Горизонтальное расположение
            rect_y = panel_y + 10
            pygame.draw.rect(screen, color, (rect_x, rect_y, box_size, box_size))
            pygame.draw.rect(screen, (100, 100, 100), (rect_x, rect_y, box_size, box_size), 1)

            # Отображение значений под квадратом
            value_text = f"{red_part[i]},{green_part[i]},{blue_part[i]}"
            text = font.render(value_text, True, (200, 200, 200))
            text_x = rect_x
            text_y = rect_y + box_size + 2
            screen.blit(text, (text_x, text_y))
    else:
        # Пустая панель или надпись "Нет выбора"
        font = pygame.font.SysFont(None, 24)
        text = font.render("No creature selected", True, (200, 200, 200))
        screen.blit(text, (panel_x + 10, panel_y + 10))

def draw_creatures(map_surface, creatures, selected_index=None):
    for i, creature in enumerate(creatures):
        x, y, angle, view_distance = creature
        # Применяем масштабирование и смещение
        center_x = int((x * cell_size) * zoom_level + offset_x)
        center_y = int((y * cell_size) * zoom_level + offset_y)

        # Проверяем, находится ли существо в пределах поверхности карты
        if (center_x < -20 or center_x > map_panel_width + 20 or 
            center_y < -20 or center_y > screen_height + 20):
            continue

        # Определяем цвет в зависимости от того, выбрано ли существо
        if i == selected_index:
            creature_color = (255, 255, 0)  # Жёлтый для выбранного
            outline = True
        else:
            creature_color = (255, 255, 255)  # Белый для остальных
            outline = False

        # Рисуем тело существа с учетом масштаба
        radius = int(8 * zoom_level) if outline else int(6 * zoom_level)
        pygame.draw.circle(map_surface, creature_color, (center_x, center_y), radius)

        # Если существо выделено, рисуем обводку
        if outline:
            pygame.draw.circle(map_surface, (255, 255, 255), (center_x, center_y), int(8 * zoom_level), 2)

        # Рисуем направление взгляда с учетом масштаба
        line_length = 15 * zoom_level
        end_x = center_x + int(math.cos(angle) * line_length)
        end_y = center_y + int(math.sin(angle) * line_length)
        pygame.draw.line(map_surface, creature_color, (center_x, center_y), (end_x, end_y), max(1, int(2 * zoom_level)))

def draw_raycast_dots(map_surface, dots):
    for x, y in dots:
        # Применяем масштабирование и смещение
        screen_x = int((x * cell_size) * zoom_level + offset_x)
        screen_y = int((y * cell_size) * zoom_level + offset_y)
        
        # Проверяем, находится ли точка в пределах поверхности карты
        if (screen_x < -5 or screen_x > map_panel_width + 5 or 
            screen_y < -5 or screen_y > screen_height + 5):
            continue
            
        pygame.draw.circle(map_surface, (255, 255, 0), (screen_x, screen_y), max(1, int(2 * zoom_level)))

def draw_instructions(screen):
    font = pygame.font.SysFont(None, 18)
    x_offset = map_panel_width + 20  # Отступ от карты
    y_offset = 100
    line_spacing = 20

    instructions = [
        "Инструкция:",
        "• [R] — перегенерировать карту и существ",
        "• [стрелки влево-вправо] — повернуть всех существ на 5 градусов.",
        "  (всех - чтобы подчеркнуть, что видение расчитывается одним массивом для всех существ)",
        "• [стрелки вперед-назад] — двигает выбранное существо",
        "• [ЛКМ] — выбрать существо",
        "• [V] — Вывести массив vision выбранного существа непосредственно из выхода быстрой функции",
        "• Панель справа — vision выбранного существа (R,G,B)",
        "• [Колесико мыши] — увеличить/уменьшить масштаб",
        "• [Правая кнопка мыши + перетаскивание] — перемещать карту",
    ]

    for i, line in enumerate(instructions):
        text = font.render(line, True, (200, 200, 200))
        screen.blit(text, (x_offset, y_offset + i * line_spacing))

def redraw_all():
    game_map = generate_map()
    creatures = generate_creatures()
    all_visions, raycast_dots = fast_get_all_visions(game_map, creatures)
    return game_map, creatures, all_visions, raycast_dots

# Инициализация начальных данных
game_map, creatures, all_visions, raycast_dots = redraw_all()

# Константа для поворота (5 градусов в радианах)
rotation_step = math.radians(5)

running = True
selected_creature_index = None
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # Перегенерация по нажатию R
                game_map, creatures, all_visions, raycast_dots = redraw_all()
                # Сброс масштаба и смещения при перегенерации
                zoom_level = 1.0
                offset_x = 0
                offset_y = 0
            elif event.key == pygame.K_LEFT:  # Поворот всех существ влево на 5 градусов
                for creature in creatures:
                    creature[2] -= rotation_step
                # Пересчитываем видимость после поворота
                all_visions, raycast_dots = fast_get_all_visions(game_map, creatures)
            elif event.key == pygame.K_RIGHT:  # Поворот всех существ вправо на 5 градусов
                for creature in creatures:
                    creature[2] += rotation_step
                # Пересчитываем видимость после поворота
                all_visions, raycast_dots = fast_get_all_visions(game_map, creatures)
            elif event.key == pygame.K_UP:  # Движение вперёд
                if selected_creature_index is not None:
                    creature = creatures[selected_creature_index]
                    # Двигаем по направлению угла
                    speed = 0.5  # Скорость движения
                    creature[0] += speed * math.cos(creature[2])
                    creature[1] += speed * math.sin(creature[2])
                    # Пересчитываем видимость после движения
                    all_visions, raycast_dots = fast_get_all_visions(game_map, creatures)
            elif event.key == pygame.K_DOWN:  # Движение назад
                if selected_creature_index is not None:
                    creature = creatures[selected_creature_index]
                    speed = 0.5
                    creature[0] -= speed * math.cos(creature[2])  # Движение в противоположную сторону
                    creature[1] -= speed * math.sin(creature[2])
                    # Пересчитываем видимость после движения
                    all_visions, raycast_dots = fast_get_all_visions(game_map, creatures)
            elif event.key == pygame.K_v:  # Например, нажмите "V", чтобы вывести в консоль
                if selected_creature_index is not None:
                    vis1 = all_visions[selected_creature_index]
                    print(f"Vision of creature {selected_creature_index}:")
                    print_vision_array(vis1)
                    print("Координаты и угол существа: " + str(creatures[selected_creature_index]))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левая кнопка мыши
                mouse_x, mouse_y = event.pos
                
                # Проверяем, что клик был в области карты
                if mouse_x < map_panel_width:
                    closest_index = None
                    min_distance = float('inf')

                    for i, creature in enumerate(creatures):
                        # Учитываем масштаб и смещение при расчете позиции существа
                        creature_screen_x = int((creature[0] * cell_size) * zoom_level + offset_x)
                        creature_screen_y = int((creature[1] * cell_size) * zoom_level + offset_y)
                        distance = math.sqrt((mouse_x - creature_screen_x)**2 + (mouse_y - creature_screen_y)**2)

                        # Радиус клика с учетом масштаба
                        click_radius = 10 * zoom_level
                        if distance <= click_radius:
                            if distance < min_distance:
                                min_distance = distance
                                closest_index = i

                    selected_creature_index = closest_index
                    if selected_creature_index is not None:
                        print("Выбрано существо с индексом: " + str(selected_creature_index))
                    else:
                        print("Существо не выбрано")
                
            elif event.button == 3:  # Правая кнопка мыши - начало перетаскивания
                mouse_x, mouse_y = event.pos
                # Начинаем перетаскивание только если клик в области карты
                if mouse_x < map_panel_width:
                    dragging = True
                    drag_start_x, drag_start_y = event.pos
                
            elif event.button == 4:  # Колесико мыши вверх - увеличение
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Масштабируем только если курсор в области карты
                if mouse_x < map_panel_width:
                    old_zoom = zoom_level
                    zoom_level = min(3.0, zoom_level * 1.1)  # Максимальный зум 3x
                    
                    # Корректируем смещение для сохранения позиции под курсором
                    offset_x = mouse_x - (mouse_x - offset_x) * (zoom_level / old_zoom)
                    offset_y = mouse_y - (mouse_y - offset_y) * (zoom_level / old_zoom)
                
            elif event.button == 5:  # Колесико мыши вниз - уменьшение
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Масштабируем только если курсор в области карты
                if mouse_x < map_panel_width:
                    old_zoom = zoom_level
                    zoom_level = max(0.5, zoom_level * 0.9)  # Минимальный зум 0.5x
                    
                    # Корректируем смещение для сохранения позиции под курсором
                    offset_x = mouse_x - (mouse_x - offset_x) * (zoom_level / old_zoom)
                    offset_y = mouse_y - (mouse_y - offset_y) * (zoom_level / old_zoom)
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:  # Правая кнопка мыши - конец перетаскивания
                dragging = False
                
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                # Перетаскивание карты
                mouse_x, mouse_y = event.pos
                offset_x += mouse_x - drag_start_x
                offset_y += mouse_y - drag_start_y
                drag_start_x, drag_start_y = mouse_x, mouse_y
    
    # Очистка экрана
    screen.fill((0, 0, 0))
    
    # Рисование на отдельной поверхности карты
    draw_map(map_surface, game_map)
    draw_raycast_dots(map_surface, raycast_dots)
    draw_creatures(map_surface, creatures, selected_creature_index)
    
    # Отображаем поверхность карты на основном экране
    screen.blit(map_surface, (0, 0))
    
    # Рисуем разделительную линию между картой и панелью
    pygame.draw.line(screen, (100, 100, 100), (map_panel_width, 0), (map_panel_width, screen_height), 2)
    
    # Рисуем панель с видением и инструкциями
    draw_vision_panel(screen, selected_creature_index, all_visions)
    draw_instructions(screen)
    
    # Обновление экрана
    pygame.display.flip()
    clock.tick(60)

pygame.quit()