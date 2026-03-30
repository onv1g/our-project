import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QPushButton, QWidget, QVBoxLayout, QLineEdit, \
    QLabel
from utils import dict_list_to_json, json_to_dict_list
from data_path import path_to_json
import os
import matplotlib.pyplot as plt
from windrose import WindroseAxes
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import PyQt5

venv_path = r'C:\Users\Дети\PycharmProjects\pythonProject7\.venv'
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(venv_path, 'Lib', 'site-packages', 'PyQt5', 'Qt5', 'plugins')


def create_rose_data(window, button, data):
    if window.layout() is not None:
        QWidget().setLayout(window.layout())
        button.deleteLater()

    layout = QVBoxLayout(window)
    window.setLayout(layout)
    image_input_field = QLineEdit()
    image_input_field.setReadOnly(True)

    image_input_field.setFixedSize(600, 600)

    image_input_field.setStyleSheet("""
        QLineEdit {
            border: 2px dashed black; 
            color: black;

        }
    """)
    layout.addWidget(image_input_field, alignment=Qt.AlignCenter)
    layout.addStretch(1)
    button_for_create = QPushButton('построить розу диаграмм', window)
    button_for_create.resize(200, 50)
    button_for_create.move(500, 700)
    button_for_create.clicked.connect(lambda: create_rose(input_field, data, window))
    button_for_create.show()

    label = QLabel("Введите интервал:", window)
    label.move(100, 716)
    label.setStyleSheet("font-size: 14px;font-weight: bold;")
    label.adjustSize()

    input_field = QLineEdit(window)
    input_field.setFixedSize(100, 50)
    input_field.move(240, 700)
    input_field.show()
    input_field.setStyleSheet("font-size: 14px;font-weight: bold;")
    label.show()


def create_rose(input_field, data, window):
    layout = QVBoxLayout(window)
    window.setLayout(layout)

    interval = input_field.text()
    if interval == '':
        interval = 10
    else:
        interval = int(interval)
    intervals = []
    intervals.append(0)
    d = 0
    r = 1
    while d != 180:
        d = interval * r
        intervals.append(d)
        r += 1
    print(intervals)
    data_of_intervals = {}
    for i in range(1, len(intervals)):
        quantity_of_angles_in_interval = 0
        for j in range(len(data)):
            if data[j]["final_beta"] <= intervals[i] and data[j]["final_beta"] > intervals[i - 1]:
                quantity_of_angles_in_interval += 1
        data_of_intervals[intervals[i]] = quantity_of_angles_in_interval
    print(data_of_intervals)
    quantity_of_gaps = len(data)
    percents = {}
    for i in data_of_intervals:
        percent = (data_of_intervals[i] / quantity_of_gaps) * 100
        percent = int(percent)

        percents[i] = percent

    print(percents)

    values = []
    for i in percents:
        values.append(percents[i])

    angles = intervals[1:]

    print(values)
    print(angles)

    all_angles = np.deg2rad(angles + [a + 180 for a in angles])
    all_values = values + values
    width = np.deg2rad(interval * 0.8)
    tick_degrees = list(range(0, 360, interval))


    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'polar'}, facecolor='black')
    ax.set_facecolor('black')
    ax.bar(all_angles, all_values, width=width, color='#00FF00', edgecolor='black', alpha=0.9)

    ax.set_xticks(np.deg2rad(tick_degrees))
    ax.set_xticklabels([f"{d}°" for d in tick_degrees], color='white', fontsize=9)

    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.grid(color='white', alpha=0.15, linestyle='--')


    canvas = FigureCanvas(fig)
    current_layout = window.layout()

    if current_layout is not None:

        for i in reversed(range(current_layout.count())):
            item = current_layout.itemAt(i)
            widget = item.widget()

            if isinstance(widget, (FigureCanvas, QLineEdit)) and widget != input_field:
                widget.setParent(None)


        current_layout.insertWidget(0, canvas, alignment=Qt.AlignCenter)
        canvas.draw()
