import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QPushButton, QWidget, QVBoxLayout, QLineEdit,QLabel
from utils import dict_list_to_json, json_to_dict_list
from data_path import path_to_json
import os
import sys

import PyQt5

def pirnt():
    print('hi')

def create_rose_data(window, button):
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
    button_for_create.clicked.connect(lambda: create_rose(input_field))
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






def create_rose(input_field):
    interval = input_field.text()
    if interval == '':
        interval = 10
    print(interval)






