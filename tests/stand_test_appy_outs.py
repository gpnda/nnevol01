# -*- coding: utf-8 -*-
"""
Стенд для проверки apply_outs: как выходы нейросети применяются к
координатам, углу и скорости существа.

Standalone-скрипт, не зависит от остальных модулей проекта.

Управление:
  ↑ / ↓       — выбрать поле (out_angle / out_speed)
  Enter       — активировать / подтвердить ввод
  Backspace   — удалить последний символ при вводе
  Escape      — отменить ввод / выйти
  F5          — применить apply_outs и показать результат
  Q           — выйти
"""

import math
import sys
import pygame


# ---------------------------------------------------------------------------
# apply_outs — скопировано из world.py (источник истины)
# ---------------------------------------------------------------------------

def apply_outs(creature_x, creature_y, creature_angle, creature_speed, out_angle, out_speed):
		
    # Расчитываем новые координаты, куда существо хочет перейти
    new_angle = creature_angle + (out_angle)
    # print(f"{all_outs[index][0]:.8f}")
    # Нормализуем угол в диапазон [0, 2π)
    new_angle = new_angle % (2 * math.pi)
    # Если угол отрицательный, добавляем 2π чтобы получить положительное значение
    # @TODO Вообще это интересный вопрос - этот разрыв в управлении углом существа (2π) - создает ли это помехи в процессе отбора?
    # Думаю, что никак не влияет, потому что существо не знает своего угла, угол - абсолютный 
    # угол (который как раз прыгает) - это параметр относящийся к миру, само существо о нем не знает вообще.
    
    new_speed = out_speed*0.5
    
    # Этот клиппинг вроде бы не нужен, потому что нейросеть должна выдавать значения в диапазоне -1.0…1.0, и при умножении на 0.5 мы получаем -0.5…0.5
    #  if new_speed < -0.5:
    #     new_speed = -0.5
    # if new_speed > 0.5:
    #     new_speed = 0.5
    newx = creature_x + new_speed*math.cos(new_angle)
    newy = creature_y + new_speed*math.sin(new_angle)

    return new_angle, new_speed, newx, newy


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class StandState:
    def __init__(self):
        # Колонка 1: входные данные существа (фиксированные)
        self.creature_x     = 100.0
        self.creature_y     = 100.0
        self.creature_angle = 0.0
        self.creature_speed = 0.0

        # Колонка 2: выходы нейросети (редактируемые, диапазон 0.0…1.0)
        self.out_angle = 0.5
        self.out_speed = 0.5

        # Колонка 3: результат apply_outs (None до первого F5)
        self.result_angle = None
        self.result_speed = None
        self.result_x     = None
        self.result_y     = None

        # Управление редактором
        self.selected_row = 0   # 0 = out_angle,  1 = out_speed
        self.editing      = False
        self.input_buffer = ""

    def apply(self):
        self.result_angle, self.result_speed, self.result_x, self.result_y = \
            apply_outs(self.creature_x, self.creature_y,
                       self.creature_angle, self.creature_speed,
                       self.out_angle, self.out_speed)
        print("Before:--------------------------------------")
        print("self.creature_x: ", self.creature_x)
        print("self.creature_y: ", self.creature_y)
        print("self.creature_angle: ", self.creature_angle)
        print("self.creature_speed: ", self.creature_speed)
        print("Outs:----------------------------------------")
        print("self.out_angle: ", self.out_angle)
        print("self.out_speed: ", self.out_speed)
        print("After:---------------------------------------")
        print("self.result_angle: ", self.result_angle)
        print("self.result_speed: ", self.result_speed)
        print("self.result_x: ", self.result_x)
        print("self.result_y: ", self.result_y)

    def start_editing(self):
        self.editing = True
        val = self.out_angle if self.selected_row == 0 else self.out_speed
        self.input_buffer = f"{val:.4f}"

    def confirm_input(self):
        try:
            val = float(self.input_buffer)
        except ValueError:
            pass
        else:
            if self.selected_row == 0:
                self.out_angle = val
            else:
                self.out_speed = val
        self.editing = False
        self.input_buffer = ""

    def cancel_editing(self):
        self.editing = False
        self.input_buffer = ""


# ---------------------------------------------------------------------------
# Layout & color constants
# ---------------------------------------------------------------------------

WIN_W, WIN_H     = 1000, 720
TOP_H            = 220          # высота верхней панели с тремя колонками
COL_W            = WIN_W // 3   # ширина каждой колонки
FONT_SIZE        = 18
SMALL_FONT_SIZE  = 14
FONT_PATH        = "./tests/Ac437_Siemens_PC-D.ttf"

GRID_Y           = TOP_H + 10   # верхняя граница сетки
CELL_SIZE        = 100           # пикселей на клетку сетки
GRID_CENTER_X    = WIN_W // 2
GRID_CENTER_Y    = GRID_Y + (WIN_H - GRID_Y) // 2
ARROW_SCALE      = CELL_SIZE    # 1 единица speed → CELL_SIZE пикселей

COLORS = {
    "bg":            (18,  18,  24),
    "panel_bg":      (25,  25,  35),
    "border":        (60,  60,  80),
    "header":        (180, 180, 255),
    "label":         (140, 140, 160),
    "value":         (220, 220, 220),
    "selected_bg":   (40,  60,  100),
    "selected_fg":   (100, 200, 255),
    "editing_bg":    (20,  50,  20),
    "editing_fg":    (100, 255, 100),
    "result":        (100, 255, 160),
    "hint":          (90,  90,  110),
    "grid_line":     (40,  40,  55),
    "grid_axis":     (70,  70,  90),
    "grid_label":    (80,  80,  100),
    "arrow_before":  (80,  130, 255),
    "arrow_after":   (80,  255, 130),
    "marker_before": (80,  130, 255),
    "marker_after":  (80,  255, 130),
    "divider":       (50,  50,  70),
    "trajectory":    (60,  60,  80),
}


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def draw_arrow(screen, color, x0, y0, angle, length, width=2):
    """Стрелка из точки (x0, y0) в направлении angle длиной length пикселей."""
    if abs(length) < 1:
        pygame.draw.circle(screen, color, (int(x0), int(y0)), 5, 2)
        return
    x1 = x0 + length * math.cos(angle)
    y1 = y0 + length * math.sin(angle)
    pygame.draw.line(screen, color,
                     (int(x0), int(y0)), (int(x1), int(y1)), width)
    # Наконечник
    head_len   = max(8, abs(length) * 0.25)
    head_angle = 0.4  # радиан
    for side in (-1, 1):
        ax = x1 - head_len * math.cos(angle - side * head_angle)
        ay = y1 - head_len * math.sin(angle - side * head_angle)
        pygame.draw.line(screen, color,
                         (int(x1), int(y1)), (int(ax), int(ay)), width)


def fmt(val, precision=4):
    if val is None:
        return "---"
    return f"{val:.{precision}f}"


# ---------------------------------------------------------------------------
# draw_columns: три колонки сверху
# ---------------------------------------------------------------------------

def draw_columns(screen, font, small_font, state: StandState, tick: int):
    line_h  = font.get_height() + 6
    y_hdr   = 12
    y_row0  = y_hdr + line_h * 2

    # Фоны и рамки трёх колонок
    for col in range(3):
        rect = pygame.Rect(col * COL_W, 0, COL_W, TOP_H)
        pygame.draw.rect(screen, COLORS["panel_bg"], rect)
        pygame.draw.rect(screen, COLORS["border"], rect, 1)

    # ---- Колонка 1: INPUT ----
    x1 = 10
    screen.blit(font.render("INPUT", True, COLORS["header"]), (x1, y_hdr))
    pygame.draw.line(screen, COLORS["divider"],
                     (x1, y_hdr + line_h), (COL_W - 10, y_hdr + line_h), 1)

    for i, (label, val) in enumerate([
        ("x",     state.creature_x),
        ("y",     state.creature_y),
        ("angle", state.creature_angle),
        ("speed", state.creature_speed),
    ]):
        y = y_row0 + line_h * i
        screen.blit(font.render(f"{label}:", True, COLORS["label"]),  (x1,      y))
        screen.blit(font.render(fmt(val),    True, COLORS["value"]),  (x1 + 80, y))

    # ---- Колонка 2: OUTS (редактируемые) ----
    x2 = COL_W + 10
    screen.blit(font.render("OUTS  (NN outputs)", True, COLORS["header"]), (x2, y_hdr))
    pygame.draw.line(screen, COLORS["divider"],
                     (x2, y_hdr + line_h), (COL_W * 2 - 10, y_hdr + line_h), 1)

    hint = "↑↓ выбрать   Enter=ред.   F5=расчёт   Q=выход"
    screen.blit(small_font.render(hint, True, COLORS["hint"]), (x2, TOP_H - 22))

    for i, (label, val) in enumerate([
        ("out_angle", state.out_angle),
        ("out_speed", state.out_speed),
    ]):
        y       = y_row0 + line_h * i
        is_sel  = (state.selected_row == i)
        is_edit = is_sel and state.editing

        row_rect = pygame.Rect(COL_W + 2, y - 2, COL_W - 4, line_h)
        if is_edit:
            pygame.draw.rect(screen, COLORS["editing_bg"], row_rect)
        elif is_sel:
            pygame.draw.rect(screen, COLORS["selected_bg"], row_rect)

        lbl_color = (COLORS["editing_fg"] if is_edit
                     else COLORS["selected_fg"] if is_sel
                     else COLORS["label"])
        val_color = (COLORS["editing_fg"] if is_edit
                     else COLORS["selected_fg"] if is_sel
                     else COLORS["value"])

        # Курсор мигает раз в 30 тиков
        cursor    = "|" if (tick // 30) % 2 == 0 else " "
        disp_val  = (state.input_buffer + cursor) if is_edit else fmt(val)

        screen.blit(font.render(f"{label}:", True, lbl_color), (x2,       y))
        screen.blit(font.render(disp_val,    True, val_color),  (x2 + 130, y))
        screen.blit(small_font.render("[0.0 … 1.0]", True, COLORS["hint"]),
                    (x2 + 260, y + 3))

    # ---- Колонка 3: RESULT ----
    x3 = COL_W * 2 + 10
    screen.blit(font.render("RESULT  (after apply_outs)", True, COLORS["header"]), (x3, y_hdr))
    pygame.draw.line(screen, COLORS["divider"],
                     (x3, y_hdr + line_h), (WIN_W - 10, y_hdr + line_h), 1)

    for i, (label, val) in enumerate([
        ("new_angle", state.result_angle),
        ("new_speed", state.result_speed),
        ("new_x",     state.result_x),
        ("new_y",     state.result_y),
    ]):
        y         = y_row0 + line_h * i
        val_color = COLORS["result"] if val is not None else COLORS["hint"]
        screen.blit(font.render(f"{label}:", True, COLORS["label"]),  (x3,       y))
        screen.blit(font.render(fmt(val),    True, val_color),         (x3 + 120, y))


# ---------------------------------------------------------------------------
# draw_grid: координатная сетка со стрелками внизу
# ---------------------------------------------------------------------------

def draw_grid(screen, small_font, state: StandState):
    # Фон нижней части
    pygame.draw.rect(screen, COLORS["bg"],
                     pygame.Rect(0, GRID_Y, WIN_W, WIN_H - GRID_Y))
    pygame.draw.line(screen, COLORS["border"], (0, GRID_Y), (WIN_W, GRID_Y), 1)

    cx = GRID_CENTER_X
    cy = GRID_CENTER_Y

    origin_x = int(state.creature_x)
    origin_y = int(state.creature_y)

    cols_half = WIN_W // (2 * CELL_SIZE) + 1
    rows_half = (WIN_H - GRID_Y) // (2 * CELL_SIZE) + 2

    # Вертикальные линии сетки
    for dc in range(-cols_half, cols_half + 1):
        sx    = cx + dc * CELL_SIZE
        color = COLORS["grid_axis"] if dc == 0 else COLORS["grid_line"]
        pygame.draw.line(screen, color, (sx, GRID_Y), (sx, WIN_H))
        if dc % 5 == 0:
            lbl = small_font.render(str(origin_x + dc), True, COLORS["grid_label"])
            screen.blit(lbl, (sx + 2, GRID_Y + 2))

    # Горизонтальные линии сетки
    for dr in range(-rows_half, rows_half + 1):
        sy    = cy + dr * CELL_SIZE
        color = COLORS["grid_axis"] if dr == 0 else COLORS["grid_line"]
        pygame.draw.line(screen, color, (0, sy), (WIN_W, sy))
        if dr % 5 == 0:
            lbl = small_font.render(str(origin_y + dr), True, COLORS["grid_label"])
            screen.blit(lbl, (4, sy + 2))

    # --- Позиция ДО ---
    pygame.draw.circle(screen, COLORS["marker_before"], (cx, cy), 6, 2)
    before_len = abs(state.creature_speed) * ARROW_SCALE
    draw_arrow(screen, COLORS["arrow_before"],
               cx, cy, state.creature_angle, before_len, width=2)

    # --- Позиция ПОСЛЕ (только если есть результат) ---
    if state.result_angle is not None:
        dx       = state.result_x - state.creature_x
        dy       = state.result_y - state.creature_y
        after_sx = cx + dx * CELL_SIZE
        after_sy = cy + dy * CELL_SIZE

        # Пунктирная линия траектории ДО→ПОСЛЕ
        pygame.draw.line(screen, COLORS["trajectory"],
                         (cx, cy), (int(after_sx), int(after_sy)), 1)

        # Маркер ПОСЛЕ
        pygame.draw.circle(screen, COLORS["marker_after"],
                           (int(after_sx), int(after_sy)), 6, 2)

        # Стрелка нового направления из позиции ПОСЛЕ
        after_len = abs(state.result_speed) * ARROW_SCALE
        draw_arrow(screen, COLORS["arrow_after"],
                   after_sx, after_sy,
                   state.result_angle, after_len, width=2)

    # --- Легенда ---
    leg_x = WIN_W - 200
    leg_y = GRID_Y + 8
    pygame.draw.line(screen, COLORS["arrow_before"],
                     (leg_x, leg_y + 7), (leg_x + 20, leg_y + 7), 2)
    screen.blit(small_font.render("ДО  (before)", True, COLORS["arrow_before"]),
                (leg_x + 24, leg_y))
    if state.result_angle is not None:
        pygame.draw.line(screen, COLORS["arrow_after"],
                         (leg_x, leg_y + 25), (leg_x + 20, leg_y + 25), 2)
        screen.blit(small_font.render("ПОСЛЕ  (after)", True, COLORS["arrow_after"]),
                    (leg_x + 24, leg_y + 18))

    # Подстрочник
    info = (f"Центр: ({origin_x}, {origin_y})   "
            f"масштаб: {CELL_SIZE}px/unit   "
            f"стрелка: speed×{CELL_SIZE}px")
    screen.blit(small_font.render(info, True, COLORS["hint"]), (8, WIN_H - 18))


# ---------------------------------------------------------------------------
# Event handling
# ---------------------------------------------------------------------------

def handle_keydown(event: pygame.event.Event, state: StandState) -> bool:
    """Вернуть False если нужно завершить приложение."""
    if state.editing:
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            state.confirm_input()
        elif event.key == pygame.K_ESCAPE:
            state.cancel_editing()
        elif event.key == pygame.K_BACKSPACE:
            state.input_buffer = state.input_buffer[:-1]
        else:
            if event.unicode in "0123456789.-":
                state.input_buffer += event.unicode
        return True

    # Не в режиме редактирования
    if event.key in (pygame.K_q, pygame.K_ESCAPE):
        return False
    elif event.key == pygame.K_UP:
        state.selected_row = (state.selected_row - 1) % 2
    elif event.key == pygame.K_DOWN:
        state.selected_row = (state.selected_row + 1) % 2
    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
        state.start_editing()
    elif event.key == pygame.K_F5:
        state.apply()
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("apply_outs — stand  |  F5=расчёт  Enter=ввод  Q=выход")

    try:
        font       = pygame.font.Font(FONT_PATH, FONT_SIZE)
        small_font = pygame.font.Font(FONT_PATH, SMALL_FONT_SIZE)
    except Exception:
        font       = pygame.font.Font(None, FONT_SIZE + 6)
        small_font = pygame.font.Font(None, SMALL_FONT_SIZE + 6)

    state = StandState()
    clock = pygame.time.Clock()
    tick  = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if not handle_keydown(event, state):
                    pygame.quit()
                    sys.exit()

        screen.fill(COLORS["bg"])
        draw_columns(screen, font, small_font, state, tick)
        draw_grid(screen, small_font, state)
        pygame.display.flip()
        clock.tick(60)
        tick += 1


if __name__ == "__main__":
    main()
