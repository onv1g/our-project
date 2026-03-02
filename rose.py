import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QPushButton, QWidget, QVBoxLayout, QLineEdit,QLabel
from utils import dict_list_to_json, json_to_dict_list
from data_path import path_to_json
import os
import sys

import PyQt5



def create_rose_data(window, button,data):
    if window.layout() is not None:
        QWidget().setLayout(window.layout())
        button.deleteLater()





    layout = QVBoxLayout(window)
    window.setLayout(layout)
    image_input_field = QLineEdit()
    image_input_field.setReadOnly(True)

    image_input_field.setFixedSize(600,600)

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
    button_for_create.clicked.connect(lambda: create_rose(input_field,data))
    button_for_create.show()

    label = QLabel("Введите интервал:", window)
    label.move(100,716  )
    label.setStyleSheet("font-size: 14px;font-weight: bold;")
    label.adjustSize()

    input_field = QLineEdit(window)
    input_field.setFixedSize(100,50)
    input_field.move(240,700)
    input_field.show()
    input_field.setStyleSheet("font-size: 14px;font-weight: bold;")
    label.show()






def create_rose(input_field,data):
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
    for i in range(1,len(intervals)):
        quantity_of_angles_in_interval = 0
        for j in range(len(data)):
            if data[j]["final_beta"] <= intervals[i] and data[j]["final_beta"] > intervals[i-1]:
                quantity_of_angles_in_interval += 1
        data_of_intervals[intervals[i]] = quantity_of_angles_in_interval
    print(data_of_intervals)
    quantity_of_gaps = len(data)
    percents = {}
    for i in data_of_intervals:

        percent = (data_of_intervals[i]/quantity_of_gaps)*100
        percent = int(percent)

        percents[i] = percent

    print(percents)















