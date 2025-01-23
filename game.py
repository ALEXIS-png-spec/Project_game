import pygame as pg
import random
import time
import sys
from pygame.locals import *

# Настройки
fps = 25
window_w, window_h = 600, 500
block, cup_h, cup_w = 20, 20, 10

side_freq, down_freq = 0.15, 0.1  # передвижение в сторону и вниз

side_margin = int((window_w - cup_w * block) / 2)
top_margin = window_h - (cup_h * block) - 5

colors = ((0, 0, 225), (0, 225, 0), (225, 0, 0), (225, 225, 0))  # синий, зеленый, красный, желтый
lightcolors = ((30, 30, 255), (50, 255, 50), (255, 30, 30),
               (255, 255, 30))  # светло-синий, светло-зеленый, светло-красный, светло-желтый

white, gray, black = (255, 255, 255), (185, 185, 185), (0, 0, 0)
brd_color, bg_color, txt_color, title_color, info_color = white, black, white, colors[3], colors[0]

fig_w, fig_h = 5, 5
empty = 'o'

# Определение фигур
figures = {
    'S': [['ooooo', 'ooooo', 'ooxxo', 'oxxoo', 'ooooo'],
          ['ooooo', 'ooxoo', 'ooxxo', 'oooxo', 'ooooo']],
    'Z': [['ooooo', 'ooooo', 'oxxoo', 'ooxxo', 'ooooo'],
          ['ooooo', 'ooxoo', 'oxxoo', 'oxooo', 'ooooo']],
    'J': [['ooooo', 'oxooo', 'oxxxo', 'ooooo', 'ooooo'],
          ['ooooo', 'ooxxo', 'ooxoo', 'ooxoo', 'ooooo'],
          ['ooooo', 'ooooo', 'oxxxo', 'oooxo', 'ooooo'],
          ['ooooo', 'ooxoo', 'ooxoo', 'oxxoo', 'ooooo']],
    'L': [['ooooo', 'oooxo', 'oxxxo', 'ooooo', 'ooooo'],
          ['ooooo', 'ooxoo', 'ooxoo', 'ooxxo', 'ooooo'],
          ['ooooo', 'ooooo', 'oxxxo', 'oxooo', 'ooooo'],
          ['ooooo', 'oxxoo', 'ooxoo', 'ooxoo', 'ooooo']],
    'I': [['ooxoo', 'ooxoo', 'ooxoo', 'ooxoo', 'ooooo'],
          ['ooooo', 'ooooo', 'xxxxo', 'ooooo', 'ooooo']],
    'O': [['ooooo', 'ooooo', 'oxxoo', 'oxxoo', 'ooooo']],
    'T': [['ooooo', 'ooxoo', 'oxxxo', 'ooooo', 'ooooo'],
          ['ooooo', 'ooxoo', 'ooxxo', 'ooxoo', 'ooooo'],
          ['ooooo', 'ooooo', 'oxxxo', 'ooxoo', 'ooooo'],
          ['ooooo', 'ooxoo', 'oxxoo', 'ooxoo', 'ooooo']]
}



def pauseScreen():
    pause = pg.Surface((600, 500), pg.SRCALPHA)
    pause.fill((0, 0, 255, 127))
    display_surf.blit(pause, (0, 0))


def draw3DText(text, font, color, x, y):
    # Рисуем объемный текст
    shadow_color = (50, 50, 50)  # Цвет для тени
    # Рисуем тень
    text_surface, text_rect = txtObjects(text, font, shadow_color)
    text_rect.topleft = (x + 2, y + 2)
    display_surf.blit(text_surface, text_rect)
    # Рисуем основной текст
    text_surface, text_rect = txtObjects(text, font, color)
    text_rect.topleft = (x, y)
    display_surf.blit(text_surface, text_rect)


def main():
    global fps_clock, display_surf, basic_font, big_font
    pg.init()
    fps_clock = pg.time.Clock()
    display_surf = pg.display.set_mode((window_w, window_h))
    basic_font = pg.font.SysFont('arial', 20)
    big_font = pg.font.SysFont('verdana', 45)
    pg.display.set_caption('Block Breakers')  # Изменено название игры
    showText('Block Breakers')  # Изменено название игры
    while True:  # начинаем игру
        runTetris()
        pauseScreen()
        showText('Игра закончена')


def showRules():
    display_surf.fill(bg_color)
    draw3DText('Правила игры:', big_font, title_color, 150, 30)
    rules = [
        "1. Используйте стрелки для управления фигурой.",
        "2. Нажмите 'Вверх' для поворота фигуры.",
        "3. Нажмите 'Пробел' для паузы.",
        "4. Нажмите 'Enter' для мгновенного падения фигуры.",
        "5. Цель игры - заполнить ряды, чтобы они исчезли."
    ]
    for i, line in enumerate(rules):
        draw3DText(line, basic_font, txt_color, 100, 100 + i * 30)

    draw3DText('Нажмите любую клавишу для возвращения в меню', basic_font, txt_color, 100, 300)

    while checkKeys() is None:
        pg.display.update()
        fps_clock.tick()


def runTetris():
    cup = emptycup()
    last_move_down = time.time()
    last_side_move = time.time()
    last_fall = time.time()
    going_down = False
    going_left = False
    going_right = False
    points = 0
    level, fall_speed = calcSpeed(points)
    fallingFig = getNewFig()
    nextFig = getNewFig()

    while True:
        if fallingFig is None:
            # если нет падающих фигур, генерируем новую
            fallingFig = nextFig
            nextFig = getNewFig()
            last_fall = time.time()

            if not checkPos(cup, fallingFig):
                return  # если на игровом поле нет свободного места - игра закончена
        quitGame()
        for event in pg.event.get():
            if event.type == KEYUP:
                if event.key == K_SPACE:
                    pauseScreen()
                    showText('Пауза')
                    last_fall = time.time()
                    last_move_down = time.time()
                    last_side_move = time.time()
                elif event.key == K_LEFT:
                    going_left = False
                elif event.key == K_RIGHT:
                    going_right = False
                elif event.key == K_DOWN:
                    going_down = False
                elif event.key == K_r:  # Добавляем возможность открыть правила
                    showRules()

            elif event.type == KEYDOWN:
                # перемещение фигуры вправо и влево
                if event.key == K_LEFT and checkPos(cup, fallingFig, adjX=-1):
                    fallingFig['x'] -= 1
                    going_left = True
                    going_right = False
                    last_side_move = time.time()

                elif event.key == K_RIGHT and checkPos(cup, fallingFig, adjX=1):
                    fallingFig['x'] += 1
                    going_right = True
                    going_left = False
                    last_side_move = time.time()

                # поворачиваем фигуру, если есть место
                elif event.key == K_UP:
                    fallingFig['rotation'] = (fallingFig['rotation'] + 1) % len(figures[fallingFig['shape']])
                    if not checkPos(cup, fallingFig):
                        fallingFig['rotation'] = (fallingFig['rotation'] - 1) % len(figures[fallingFig['shape']])

                # ускоряем падение фигуры
                elif event.key == K_DOWN:
                    going_down = True
                    if checkPos(cup, fallingFig, adjY=1):
                        fallingFig['y'] += 1
                    last_move_down = time.time()

                # мгновенный сброс вниз
                elif event.key == K_RETURN:
                    going_down = False
                    going_left = False
                    going_right = False
                    for i in range(1, cup_h):
                        if not checkPos(cup, fallingFig, adjY=i):
                            break
                    fallingFig['y'] += i - 1

        # управление падением фигуры при удержании клавиш
        if (going_left or going_right) and time.time() - last_side_move > side_freq:
            if going_left and checkPos(cup, fallingFig, adjX=-1):
                fallingFig['x'] -= 1
            elif going_right and checkPos(cup, fallingFig, adjX=1):
                fallingFig['x'] += 1
            last_side_move = time.time()

        if going_down and time.time() - last_move_down > down_freq and checkPos(cup, fallingFig, adjY=1):
            fallingFig['y'] += 1
            last_move_down = time.time()

        if time.time() - last_fall > fall_speed:  # свободное падение фигуры
            if not checkPos(cup, fallingFig, adjY=1):  # проверка "приземления" фигуры
                addToCup(cup, fallingFig)  # фигура приземлилась, добавляем ее в содержимое стакана
                points += clearCompleted(cup)
                level, fall_speed = calcSpeed(points)
                fallingFig = None
            else:  # фигура пока не приземлилась, продолжаем движение вниз
                fallingFig['y'] += 1
                last_fall = time.time()

        # Отрисовка окна игры со всеми надписями
        display_surf.fill(bg_color)
        drawTitle()
        gamecup(cup)
        drawInfo(points, level)
        drawnextFig(nextFig)
        if fallingFig is not None:
            drawFig(fallingFig)
        pg.display.update()
        fps_clock.tick(fps)


def txtObjects(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def stopGame():
    pg.quit()
    sys.exit()


def checkKeys():
    quitGame()

    for event in pg.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None


def showText(text):
    titleSurf, titleRect = txtObjects(text, big_font, title_color)
    titleRect.center = (int(window_w / 2) - 3, int(window_h / 2) - 3)
    display_surf.blit(titleSurf, titleRect)

    pressKeySurf, pressKeyRect = txtObjects('Нажмите любую клавишу для продолжения', basic_font, title_color)
    pressKeyRect.center = (int(window_w / 2), int(window_h / 2) + 100)
    display_surf.blit(pressKeySurf, pressKeyRect)

    while checkKeys() is None:
        pg.display.update()
        fps_clock.tick()


def quitGame():
    for event in pg.event.get(QUIT):  # проверка всех событий, приводящих к выходу из игры
        stopGame()
    for event in pg.event.get(KEYUP):
        if event.key == K_ESCAPE:
            stopGame()
        pg.event.post(event)


def calcSpeed(points):
    # вычисляет уровень
    level = int(points / 10) + 1
    fall_speed = 0.27 - (level * 0.02)
    return level, fall_speed


def getNewFig():
    # возвращает новую фигуру со случайным цветом и углом поворота
    shape = random.choice(list(figures.keys()))
    newFigure = {'shape': shape,
                 'rotation': random.randint(0, len(figures[shape]) - 1),
                 'x': int(cup_w / 2) - int(fig_w / 2),
                 'y': -2,
                 'color': random.randint(0, len(colors) - 1)}
    return newFigure


def addToCup(cup, fig):
    for x in range(fig_w):
        for y in range(fig_h):
            if figures[fig['shape']][fig['rotation']][y][x] != empty:
                cup[x + fig['x']][y + fig['y']] = fig['color']


def emptycup():
    # создает пустой стакан
    cup = []
    for i in range(cup_w):
        cup.append([empty] * cup_h)
    return cup


def incup(x, y):
    return x >= 0 and x < cup_w and y < cup_h


def checkPos(cup, fig, adjX=0, adjY=0):
    # проверяет, находится ли фигура в границах стакана, не сталкиваясь с другими фигурами
    for x in range(fig_w):
        for y in range(fig_h):
            abovecup = y + fig['y'] + adjY < 0
            if abovecup or figures[fig['shape']][fig['rotation']][y][x] == empty:
                continue
            if not incup(x + fig['x'] + adjX, y + fig['y'] + adjY):
                return False
            if cup[x + fig['x'] + adjX][y + fig['y'] + adjY] != empty:
                return False
    return True


def isCompleted(cup, y):
    # проверяем наличие полностью заполненных рядов
    for x in range(cup_w):
        if cup[x][y] == empty:
            return False
    return True


def clearCompleted(cup):
    # Удаление заполенных рядов и сдвиг верхних рядов вниз
    removed_lines = 0
    y = cup_h - 1
    while y >= 0:
        if isCompleted(cup, y):
            for pushDownY in range(y, 0, -1):
                for x in range(cup_w):
                    cup[x][pushDownY] = cup[x][pushDownY - 1]
            for x in range(cup_w):
                cup[x][0] = empty
            removed_lines += 1
        else:
            y -= 1
    return removed_lines


def convertCoords(block_x, block_y):
    return (side_margin + (block_x * block)), (top_margin + (block_y * block))


def drawBlock(block_x, block_y, color, pixelx=None, pixely=None):
    # отрисовка квадратных блоков, из которых состоят фигуры
    if color == empty:
        return
    if pixelx is None and pixely is None:
        pixelx, pixely = convertCoords(block_x, block_y)
    pg.draw.rect(display_surf, colors[color], (pixelx + 1, pixely + 1, block - 1, block - 1), 0, 3)
    pg.draw.rect(display_surf, lightcolors[color], (pixelx + 1, pixely + 1, block - 4, block - 4), 0, 3)
    pg.draw.circle(display_surf, colors[color], (pixelx + block / 2, pixely + block / 2), 5)


def gamecup(cup):
    # граница игрового поля-стакана
    pg.draw.rect(display_surf, brd_color, (side_margin - 4, top_margin - 4, (cup_w * block) + 8, (cup_h * block) + 8),
                 5)

    # фон игрового поля
    pg.draw.rect(display_surf, bg_color, (side_margin, top_margin, block * cup_w, block * cup_h))
    for x in range(cup_w):
        for y in range(cup_h):
            drawBlock(x, y, cup[x][y])


def drawTitle():
    draw3DText('Block Breakers', big_font, title_color, window_w - 425, 30)  # Изменено название игры


def drawInfo(points, level):
    pointsSurf = basic_font.render(f'Баллы: {points}', True, txt_color)
    pointsRect = pointsSurf.get_rect()
    pointsRect.topleft = (window_w - 550, 180)
    display_surf.blit(pointsSurf, pointsRect)

    levelSurf = basic_font.render(f'Уровень: {level}', True, txt_color)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (window_w - 550, 250)
    display_surf.blit(levelSurf, levelRect)

    pausebSurf = basic_font.render('Пауза: пробел', True, info_color)
    pausebRect = pausebSurf.get_rect()
    pausebRect.topleft = (window_w - 550, 420)
    display_surf.blit(pausebSurf, pausebRect)

    escbSurf = basic_font.render('Выход: Esc', True, info_color)
    escbRect = escbSurf.get_rect()
    escbRect.topleft = (window_w - 550, 450)
    display_surf.blit(escbSurf, escbRect)


def drawFig(fig, pixelx=None, pixely=None):
    figToDraw = figures[fig['shape']][fig['rotation']]
    if pixelx is None and pixely is None:
        pixelx, pixely = convertCoords(fig['x'], fig['y'])

    # отрисовка элементов фигур
    for x in range(fig_w):
        for y in range(fig_h):
            if figToDraw[y][x] != empty:
                drawBlock(None, None, fig['color'], pixelx + (x * block), pixely + (y * block))


def drawnextFig(fig):  # превью следующей фигуры
    nextSurf = basic_font.render('Следующая:', True, txt_color)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (window_w - 150, 180)
    display_surf.blit(nextSurf, nextRect)
    drawFig(fig, pixelx=window_w - 150, pixely=230)

def drawBackground():
    # Рисуем фон с блоками
    for x in range(0, window_w, block):
        for y in range(0, window_h, block):
            color = random.choice(colors)  # Случайный цвет для блока
            pg.draw.rect(display_surf, color, (x, y, block, block))

def showText(text):
    display_surf.fill(bg_color)  # Заливаем фон
    drawBackground()  # Рисуем фон

    # Создаем полупрозрачный фон для текста
    text_background = pg.Surface((400, 100))  # Размер фона под текст
    text_background.set_alpha(150)  # Полупрозрачность
    text_background.fill((0, 0, 0))  # Цвет фона (черный)
    display_surf.blit(text_background, (int(window_w / 2) - 200, int(window_h / 2) - 50))  # Позиция фона

    titleSurf, titleRect = txtObjects(text, big_font, title_color)
    titleRect.center = (int(window_w / 2), int(window_h / 2) - 30)  # Центрируем заголовок по горизонтали
    display_surf.blit(titleSurf, titleRect)

    pressKeySurf, pressKeyRect = txtObjects('Нажмите любую клавишу для продолжения', basic_font, txt_color)
    pressKeyRect.center = (int(window_w / 2), int(window_h / 2) + 50)  # Центрируем текст для продолжения
    display_surf.blit(pressKeySurf, pressKeyRect)

    while checkKeys() is None:
        pg.display.update()
        fps_clock.tick()

def main():
    global fps_clock, display_surf, basic_font, big_font
    pg.init()
    fps_clock = pg.time.Clock()
    display_surf = pg.display.set_mode((window_w, window_h))
    basic_font = pg.font.SysFont('arial', 20)
    big_font = pg.font.SysFont('verdana', 45)
    pg.display.set_caption('Block Breakers')  # Изменено название игры
    showText('Block Breakers')  # Изменено название игры
    while True:  # начинаем игру
        runTetris()
        pauseScreen()
        showText('Игра закончена')

if __name__ == '__main__':
    main()
