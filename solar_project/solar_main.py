# coding: utf-8
# license: GPLv3

import time
import numpy as np
import sys

import tkinter as tk
import tkinter.filedialog
import pygame as pg
import thorpy

import solar_vis as vis
import solar_model as model
import solar_input as input
import solar_objects as objects



timer = None

alive = True

perform_execution = False
"""Флаг цикличности выполнения расчёта"""

model_time = 0
"""Физическое время от начала расчёта.
Тип: float"""

time_scale = 1000.0
"""Шаг по времени при моделировании.
Тип: float"""

space_objects = []
"""Список космических объектов."""

FPS = 60
"""Колчество обновлений в секунду"""

# def exception_hook():
#     pg.quit()

# sys.excepthook = exception_hook()

def execution(delta):
    """Функция исполнения -- выполняется циклически, вызывая обработку всех небесных тел,
    а также обновляя их положение на экране.
    Цикличность выполнения зависит от значения глобальной переменной perform_execution.
    При perform_execution == True функция запрашивает вызов самой себя по таймеру через от 1 мс до 100 мс.
    """
    global model_time
    global displayed_time
    model.recalculate_space_objects_positions([dr.obj for dr in space_objects], delta)
    model_time += delta


def start_execution():
    """Обработчик события нажатия на кнопку Start.
    Запускает циклическое исполнение функции execution.
    """
    global perform_execution
    perform_execution = True

def pause_execution():
    global perform_execution
    perform_execution = False

def stop_execution():
    """Обработчик события нажатия на кнопку Start.
    Останавливает циклическое исполнение функции execution.
    """
    global alive
    alive = False


def dialogOpenFile():
    root = tk.Tk()
    root.withdraw()
    fileName = tk.filedialog.Open(root, filetypes = [('*.txt files', '.txt'), ("Все файлы", "*.*")]).show()
    if fileName == '':
        return ''
    if not fileName.endswith(".txt"):
        fileName += ".txt"
    return fileName

def dialogSaveFile():
    root = tk.Tk()
    root.withdraw()
    fileName = tk.filedialog.SaveAs(root, filetypes = [('*.txt files', '.txt'), ("Все файлы", "*.*")]).show()
    if fileName == '':
        return ''
    if not fileName.endswith(".txt"):
        fileName += ".txt"
    return fileName


def open_file():
    """Открывает диалоговое окно выбора имени файла и вызывает
    функцию считывания параметров системы небесных тел из данного файла.
    Считанные объекты сохраняются в глобальный список space_objects
    """
    global space_objects
    global browser
    global model_time

    model_time = 0.0
    in_filename = dialogOpenFile()
    space_objects = input.read_space_objects_data_from_file(in_filename)
    max_distance = max([max(abs(obj.obj.x), abs(obj.obj.y)) for obj in space_objects])
    vis.calculate_scale_factor(max_distance)

def save_file():
    """
    """
    global space_objects
    global browser
    global model_time

    out_filename = dialogSaveFile()
    input.write_space_objects_data_to_file(out_filename, space_objects)

def handle_events(events, menu):
    global alive
    for event in events:
        menu.react(event)
        if event.type == pg.QUIT:
            alive = False

def slider_to_real(val):
    return np.exp(5 + val)

def slider_reaction(event):
    global time_scale
    time_scale = slider_to_real(event.el.get_value())

def init_ui(screen):
    global browser
    slider = thorpy.SliderX(200, (-20, 20), "Simulation speed")
    slider.user_func = slider_reaction
    button_stop = thorpy.make_button("Quit", func=stop_execution)
    button_pause = thorpy.make_button("Pause", func=pause_execution)
    button_play = thorpy.make_button("Play", func=start_execution)
    timer = thorpy.OneLineText("Seconds passed")

    button_load = thorpy.make_button(text="Load from file", func=open_file)
    button_save = thorpy.make_button(text="Save to file", func=save_file)

    box = thorpy.Box(elements=[
        slider,
        button_pause, 
        button_stop, 
        button_play, 
        button_load,
        button_save,
        timer])
    reaction1 = thorpy.Reaction(reacts_to=thorpy.constants.THORPY_EVENT,
                                reac_func=slider_reaction,
                                event_args={"id":thorpy.constants.EVENT_SLIDE},
                                params={},
                                reac_name="slider reaction")
    box.add_reaction(reaction1)
    
    menu = thorpy.Menu(box)
    for element in menu.get_population():
        element.surface = screen

    box.set_topleft((0,0))
    box.blit()
    box.update()
    return menu, box, timer

def main():
    """Главная функция главного модуля.
    Создаёт объекты графического дизайна библиотеки tkinter: окно, холст, фрейм с кнопками, кнопки.
    """
    
    global physical_time
    global displayed_time
    global time_step
    global time_speed
    global space
    global start_button
    global perform_execution
    global timer
    global FPS

    print('Modelling started!')
    physical_time = 0

    pg.init()
    
    width = 1000
    height = 900
    screen = pg.display.set_mode((width, height))
    last_time = time.perf_counter()
    drawer = vis.Drawer(screen)
    menu, box, timer = init_ui(screen)
    perform_execution = True
    last_update_time = 0

    while alive:
        handle_events(pg.event.get(), menu)
        cur_time = time.perf_counter()
        if perform_execution:
            execution((cur_time - last_time) * time_scale)
            text = "%d seconds passed" % (int(model_time))
            timer.set_text(text)

        if cur_time - last_update_time > 0.01:
            last_update_time = cur_time
            drawer.update(space_objects, box)

        last_time = cur_time
        #time.sleep(1.0 / FPS)

    print('Modelling finished!')
    pg.quit()

if __name__ == "__main__":
    try:
        main()
    finally:
        pg.quit()
