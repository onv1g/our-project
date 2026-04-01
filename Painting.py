import sys
import os
import math
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import PyQt5
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QFileDialog, QGraphicsView,
                             QGraphicsScene, QGraphicsPixmapItem, QGraphicsLineItem,
                             QGraphicsEllipseItem, QTableWidget, QTableWidgetItem,
                             QLineEdit, QLabel, QFrame)
from PyQt5.QtGui import QPixmap, QPen, QColor, QPainter
from PyQt5.QtCore import Qt


dirname = os.path.dirname(PyQt5.__file__)
plugin_path = os.path.join(dirname, 'Qt5', 'plugins', 'platforms')
if not os.path.exists(plugin_path):
    plugin_path = os.path.join(dirname, 'Qt', 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


def calculate_beta(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0: return 180
    if dy == 0: return 90
    tan = dy / dx
    tangle = abs(math.degrees(math.atan(tan)))
    return math.floor(tangle)


def process_gaps_to_list(raw_data):
    final_list = []
    for gap_id, segments in raw_data.items():
        if not segments: continue
        betas = []
        try:
            gap_num = int(gap_id.split('_')[1])
        except:
            gap_num = 1
        gap_entry = {"number_of_the_gap": gap_num, "final_beta": 0, "segments": []}
        for i, seg in enumerate(segments, 1):
            beta = calculate_beta(seg['x1'], seg['y1'], seg['x2'], seg['y2'])
            betas.append(beta)
            gap_entry["segments"].append({
                "number": i, "beta": beta,
                "x_1": seg['x1'], "y_1": seg['y1'],
                "x_2": seg['x2'], "y_2": seg['y2']
            })
        if betas:
            gap_entry["final_beta"] = math.floor(sum(betas) / len(betas))
        final_list.append(gap_entry)
    return final_list



class GapsTableWindow(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.setWindowTitle("Результаты анализа")
        self.resize(600, 700)
        self.main_layout = QVBoxLayout(self)

        self.table = QTableWidget(len(self.data), 2)
        self.table.setHorizontalHeaderLabels(["Номер разрыва", "Угол β"])
        self.table.horizontalHeader().setStretchLastSection(True)
        for i, entry in enumerate(self.data):
            self.table.setItem(i, 0, QTableWidgetItem(str(entry["number_of_the_gap"])))
            self.table.setItem(i, 1, QTableWidgetItem(str(entry["final_beta"])))
        self.main_layout.addWidget(self.table)

        self.button_frame = QFrame()
        self.btn_row = QHBoxLayout(self.button_frame)
        self.btn_row.setContentsMargins(0, 0, 0, 0)

        self.btn_rose = QPushButton("Построить розу")
        self.btn_close = QPushButton("Закрыть")

        for btn in [self.btn_rose, self.btn_close]:
            btn.setFixedHeight(50)
            self.btn_row.addWidget(btn)

        self.main_layout.addWidget(self.button_frame)
        self.btn_rose.clicked.connect(self.setup_rose_ui)
        self.btn_close.clicked.connect(self.close)

    def setup_rose_ui(self):
        self.table.hide()
        self.btn_rose.hide()
        self.chart_container = QWidget()
        self.chart_container.setLayout(QVBoxLayout())
        self.main_layout.insertWidget(0, self.chart_container)

        input_row = QHBoxLayout()
        lbl = QLabel("Интервал:")
        self.int_input = QLineEdit("10")
        self.int_input.setFixedWidth(50)
        btn_gen = QPushButton("Обновить")
        btn_gen.clicked.connect(self.draw_rose)

        input_row.addStretch();
        input_row.addWidget(lbl);
        input_row.addWidget(self.int_input);
        input_row.addWidget(btn_gen);
        input_row.addStretch()
        self.main_layout.addLayout(input_row)
        self.draw_rose()

    def draw_rose(self):
        val = self.int_input.text()
        interval = int(val) if val.isdigit() and int(val) > 0 else 10
        intervals = list(range(0, 181, interval))
        counts = [sum(1 for d in self.data if intervals[i - 1] < d["final_beta"] <= intervals[i]) for i in
                  range(1, len(intervals))]

        q = len(self.data) if self.data else 1
        values = [(c / q) * 100 for c in counts]
        angles = intervals[1:]
        all_angles = np.deg2rad(angles + [a + 180 for a in angles])
        all_values = values + values
        width = np.deg2rad(interval * 0.8)

        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw={'projection': 'polar'})
        ax.bar(all_angles, all_values, width=width, color='#00FF00', edgecolor='black', alpha=0.8)
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)

        canvas = FigureCanvas(fig)
        while self.chart_container.layout().count():
            item = self.chart_container.layout().takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.chart_container.layout().addWidget(canvas)
        canvas.draw()



class DrawingView(QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.parent_window = parent
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)


    def wheelEvent(self, event):
        f = 1.25 if event.angleDelta().y() > 0 else 0.8
        self.scale(f, f)

    def mousePressEvent(self, event):

        if self.parent_window.shift_pressed and event.button() == Qt.LeftButton:
            pos = self.mapToScene(event.pos())
            self.parent_window.add_point(pos)
        elif event.button() == Qt.RightButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)

            fake_event = PyQt5.QtGui.QMouseEvent(event.type(), event.pos(), Qt.LeftButton, Qt.LeftButton,
                                                 event.modifiers())
            super().mousePressEvent(fake_event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.setDragMode(QGraphicsView.NoDrag)
        super().mouseReleaseEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gap Mapper Pro")
        self.resize(1000, 850)
        self.data_storage = {}
        self.gap_counter = 0
        self.current_gap_points = []
        self.shift_pressed = False
        self.history_items = []  # Для Ctrl+Z
        self.final_list = []
        self.init_ui()

    def init_ui(self):
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QVBoxLayout(self.central)

        self.menu_container = QWidget()
        self.menu_layout = QHBoxLayout(self.menu_container)

        self.btn_open = QPushButton("Выберите файл")
        self.btn_open.setFixedSize(200, 60)
        self.btn_open.clicked.connect(self.open_file)

        self.btn_results = QPushButton("Вывести таблицу")
        self.btn_results.setFixedSize(200, 60)
        self.btn_results.clicked.connect(self.open_table)
        self.btn_results.hide()

        self.menu_layout.addWidget(self.btn_open)
        self.menu_layout.addWidget(self.btn_results)
        self.layout.addWidget(self.menu_container, 0, Qt.AlignCenter)

        self.editor = QWidget()
        self.ed_layout = QVBoxLayout(self.editor)
        self.scene = QGraphicsScene(0, 0, 1000, 1000)
        self.view = DrawingView(self)
        self.view.setScene(self.scene)
        self.ed_layout.addWidget(self.view)

        self.btn_confirm = QPushButton("Подтвердить")
        self.btn_confirm.setFixedHeight(50)
        self.btn_confirm.clicked.connect(self.finalize)
        self.ed_layout.addWidget(self.btn_confirm)

        self.layout.addWidget(self.editor)
        self.editor.hide()

    def open_file(self):
        p, _ = QFileDialog.getOpenFileName(self, "Выбор изображения", "", "Images (*.png *.jpg *.jpeg)")
        if p:
            self.scene.clear()
            self.data_storage = {}
            self.gap_counter = 0
            self.current_gap_points = []
            self.history_items = []
            pix = QPixmap(p).scaled(1000, 1000, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            self.scene.addItem(QGraphicsPixmapItem(pix))
            self.editor.show()
            self.btn_results.hide()

    def add_point(self, p):
        dot = QGraphicsEllipseItem(p.x() - 5, p.y() - 5, 10, 10)
        dot.setBrush(QColor(255, 0, 0))
        self.scene.addItem(dot)

        current_action = [dot]
        gap_key = f"gap_{self.gap_counter}"

        if self.current_gap_points:
            p1 = self.current_gap_points[-1]
            line = QGraphicsLineItem(p1.x(), p1.y(), p.x(), p.y())
            line.setPen(QPen(Qt.black, 3))
            self.scene.addItem(line)
            current_action.append(line)

            if gap_key not in self.data_storage: self.data_storage[gap_key] = []
            self.data_storage[gap_key].append(
                {"x1": int(p1.x()), "y1": int(p1.y()), "x2": int(p.x()), "y2": int(p.y())})

        self.history_items.append({'graphics': current_action, 'gap_key': gap_key})
        self.current_gap_points.append(p)

    def undo_last(self):
        if self.history_items:
            last = self.history_items.pop()
            # Удаляем графику
            for item in last['graphics']:
                self.scene.removeItem(item)
            # Удаляем данные
            key = last['gap_key']
            if key in self.data_storage and self.data_storage[key]:
                self.data_storage[key].pop()
            if self.current_gap_points:
                self.current_gap_points.pop()

    def finalize(self):
        self.final_list = process_gaps_to_list(self.data_storage)
        with open("gaps.json", "w", encoding="utf-8") as f:
            json.dump(self.final_list, f, indent=2, ensure_ascii=False)
        self.editor.hide()
        self.btn_results.show()

    def open_table(self):
        self.tw = GapsTableWindow(self.final_list)
        self.tw.show()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Shift:
            self.shift_pressed = True
            self.gap_counter += 1
            self.current_gap_points = []
        # Обработка Ctrl + Z
        if e.modifiers() & Qt.ControlModifier and e.key() == Qt.Key_Z:
            self.undo_last()

    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key_Shift: self.shift_pressed = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
