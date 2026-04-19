import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QPushButton, QWidget, QVBoxLayout
from utils import dict_list_to_json, json_to_dict_list
from data_path import path_to_json
import os
import sys
import PyQt5
from rose import create_rose_data


dirname = os.path.dirname(PyQt5.__file__)
plugin_path = os.path.join(dirname, 'Qt5', 'plugins', 'platforms')

if not os.path.exists(plugin_path):
    plugin_path = os.path.join(dirname, 'Qt', 'plugins', 'platforms')

os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

path = path_to_json


def table_of_gaps(path_to_json):
    data = json_to_dict_list(path_to_json)
    app = QApplication(sys.argv)
    length = len(data)
    height = 39 * (length)
    window = QWidget()
    window.setWindowTitle("Результаты")
    window.setFixedSize(800, 800)
    layout = QVBoxLayout(window)


    table = QTableWidget(length, 2)
    table.setFixedSize(220,height-10)
    table.verticalHeader().setDefaultSectionSize(39)






    table.setHorizontalHeaderLabels(["Номер разрыва", "угол β"])
    for i in range(0,length):
        id = data[i]["number_of_the_gap"]
        angle = data[i]["final_beta"]
        table.setItem(i,0 , QTableWidgetItem(str(id)))
        table.setItem(i, 1, QTableWidgetItem(str(angle)))





    layout.addWidget(table,alignment=Qt.AlignCenter)
    layout.addStretch(1)
    button = QPushButton('построить розу диаграмм',window)
    button.resize(200,50)
    button.move(500,700)
    button.clicked.connect(lambda: create_rose_data(window,button,data))


    window.show()
    sys.exit(app.exec())