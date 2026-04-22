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
from excel import create_exel_file
from data_path import path_to_venv

import PyQt5

base_dir = os.path.dirname(os.path.abspath(__file__))

# Собираем путь к venv относительно этой папки
venv_path = os.path.join(base_dir, '.venv')

# Исправляем путь к плагинам Qt
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(
    venv_path, 'Lib', 'site-packages', 'PyQt5', 'Qt5', 'plugins')
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
    button_for_create.clicked.connect(lambda: create_rose(input_field, data, window,input_field_filename))
    button_for_create.show()

    label_interval = QLabel("Введите интервал:", window)
    label_interval.move(140, 716)
    label_interval.setStyleSheet("font-size: 14px;font-weight: bold;")
    label_interval.adjustSize()

    label_interval_180 = QLabel("(Остаток при делении 180 на интервал должен быть равен 0)", window)
    label_interval_180.move(170, 770)
    label_interval_180.setStyleSheet("font-size: 14px;font-weight: bold;")
    label_interval_180.adjustSize()


    input_field = QLineEdit(window)
    input_field.setFixedSize(100, 50)
    input_field.move(280, 700)
    input_field.show()
    input_field.setStyleSheet("font-size: 14px;font-weight: bold;")
    label_interval.show()
    label_interval_180.show()

    label_filename = QLabel("Введите название excel файла:", window)
    label_filename.move(51, 656)
    label_filename.setStyleSheet("font-size: 14px;font-weight: bold;")
    label_filename.adjustSize()

    input_field_filename = QLineEdit(window)
    input_field_filename.setFixedSize(100, 50)
    input_field_filename.move(280, 640)
    input_field_filename.show()
    input_field_filename.setStyleSheet("font-size: 14px;font-weight: bold;")
    label_filename.show()


def create_rose(input_field, data, window,input_field_filename):
    layout = QVBoxLayout(window)
    window.setLayout(layout)
    angles=[]
    interval = input_field.text()
    if interval == '':
        interval = 10
    else:
        interval = int(interval)
    intervals_azimuths = list(range(0, 361, interval))
    data_of_intervals = {}
    for i in range(1, len(intervals_azimuths)):
        quantity_of_angles_in_interval = 0
        for j in range(len(data)):
            if (90-data[j]["final_beta"]) % 360 <= intervals_azimuths[i] and (90-data[j]["final_beta"]) % 360 > intervals_azimuths[i - 1]:
                quantity_of_angles_in_interval += 1
        angles.append(intervals_azimuths[i])
        data_of_intervals[str(intervals_azimuths[i-1])+"-"+str(intervals_azimuths[i])] = quantity_of_angles_in_interval
    print("интервалы:",data_of_intervals)


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


    print(values)
    print("углы",angles)

    mirrored_angles = []
    mirrored_values = []

    for i in range(len(angles)):
        angle_rad = np.deg2rad(angles[i] - interval / 2)
        val = values[i]


        mirrored_angles.append(angle_rad % (2 * np.pi))
        mirrored_values.append(val)


        mirrored_angles.append((angle_rad + np.pi) % (2 * np.pi))
        mirrored_values.append(val)
    all_angles = mirrored_angles
    all_values = mirrored_values
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
    ax.set_yticklabels([])
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
    filename = input_field_filename.text()
    create_exel(percents, data_of_intervals, intervals_azimuths,filename)




def create_exel(percents,data_of_intervals,intervals,filename):
    create_exel_file(percents, data_of_intervals, intervals,filename)