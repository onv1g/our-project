import sys
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem
from utils import dict_list_to_json, json_to_dict_list
from data_path import path_to_json
import os
import sys
import PyQt5

# Находим путь к папке с плагинами PyQt5
dirname = os.path.dirname(PyQt5.__file__)
plugin_path = os.path.join(dirname, 'Qt5', 'plugins', 'platforms')

# Если такой папки нет, пробуем альтернативный путь (зависит от версии установки)
if not os.path.exists(plugin_path):
    plugin_path = os.path.join(dirname, 'Qt', 'plugins', 'platforms')

os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

data = json_to_dict_list(path_to_json)
app = QApplication(sys.argv)
length = len(data)
# 1. Создаем таблицу 3x2 (строки x столбцы)
table = QTableWidget(length, 2)

# 2. Устанавливаем заголовки колонок
table.setHorizontalHeaderLabels(["Номер разрыва", "угол β"])
for i in range(0,length):
    id = data[i]["number_of_the_gap"]
    angle = data[i]["final_beta"]
    table.setItem(i,0 , QTableWidgetItem(str(id)))
    table.setItem(i, 1, QTableWidgetItem(str(angle)))


table.show()
sys.exit(app.exec())