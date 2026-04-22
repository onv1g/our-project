import sys
import os
import json
import PyQt5
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QFileDialog, QGraphicsView,
                             QGraphicsScene, QGraphicsPixmapItem, QGraphicsLineItem,
                             QGraphicsEllipseItem, QTableWidget, QTableWidgetItem,
                             QGraphicsTextItem)
from PyQt5.QtGui import QPixmap, QPen, QColor, QPainter, QMouseEvent
from PyQt5.QtCore import Qt, QObject, QEvent
from rose import create_rose_data
from angles import process_gaps_to_list

dirname = os.path.dirname(PyQt5.__file__)
plugin_path = os.path.join(dirname, 'Qt5', 'plugins', 'platforms')
if not os.path.exists(plugin_path):
    plugin_path = os.path.join(dirname, 'Qt', 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

state = {
    "main_window": None,
    "scene": None,
    "view": None,
    "editor": None,
    "btn_results": None,
    "data_storage": {},
    "gap_counter": 0,
    "current_gap_points": [],
    "shift_pressed": False,
    "history_items": [],
    "final_list": [],
    "table_window": None,
}


def add_point(p):
    current_action = []
    if not state["current_gap_points"]:
        state["gap_counter"] += 1
        text = QGraphicsTextItem(str(state["gap_counter"]))
        text.setDefaultTextColor(QColor(255, 0, 0))
        font = text.font()
        font.setPointSize(25)
        text.setFont(font)
        text.setPos(p.x() + 6, p.y() - 6)
        state["scene"].addItem(text)
        current_action.append(text)
    dot = QGraphicsEllipseItem(p.x() - 10, p.y() - 10, 20, 20)
    dot.setBrush(QColor(255, 0, 0))
    state["scene"].addItem(dot)
    current_action.append(dot)
    gap_key = f"gap_{state['gap_counter']}"
    if state["current_gap_points"]:
        p1 = state["current_gap_points"][-1]
        line = QGraphicsLineItem(p1.x(), p1.y(), p.x(), p.y())
        line.setPen(QPen(Qt.black, 5))
        state["scene"].addItem(line)
        current_action.append(line)

        if gap_key not in state["data_storage"]:
            state["data_storage"][gap_key] = []
        state["data_storage"][gap_key].append({
            "x1": int(p1.x()), "y1": int(p1.y()),
            "x2": int(p.x()), "y2": int(p.y())
        })

    state["history_items"].append({
        'graphics': current_action,
        'gap_key': gap_key,
        'is_first_point': len(state["current_gap_points"]) == 0
    })
    state["current_gap_points"].append(p)


def undo_last():
    if state["history_items"]:
        last = state["history_items"].pop()
        for item in last['graphics']:
            state["scene"].removeItem(item)
        key = last['gap_key']
        if key in state["data_storage"] and state["data_storage"][key]:
            state["data_storage"][key].pop()
        if state["current_gap_points"]:
            state["current_gap_points"].pop()
        if last.get('is_first_point'):
            state["gap_counter"] -= 1


def open_file():
    p, _ = QFileDialog.getOpenFileName(state["main_window"], "Выбор изображения", "", "Images (*.png *.jpg *.jpeg)")
    if p:
        state["scene"].clear()
        state["data_storage"] = {}
        state["gap_counter"] = 0
        state["current_gap_points"] = []
        state["history_items"] = []
        pix = QPixmap(p).scaled(10000, 10000, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        state["scene"].addItem(QGraphicsPixmapItem(pix))
        state["editor"].show()
        state["btn_results"].hide()
        state["view"].setSceneRect(0, 0, 10000, 10000)


def finalize():
    state["final_list"] = process_gaps_to_list(state["data_storage"])
    with open("gaps.json", "w", encoding="utf-8") as f:
        json.dump(state["final_list"], f, indent=2, ensure_ascii=False)
    state["editor"].hide()
    state["btn_results"].show()


def open_table_window():
    data = state["final_list"]
    tw = QWidget()
    state["table_window"] = tw
    tw.setWindowTitle("Таблица разломов")
    tw.resize(800, 850)
    main_layout = QVBoxLayout(tw)
    content_widget = QWidget()
    content_layout = QVBoxLayout(content_widget)
    main_layout.addWidget(content_widget)

    table = QTableWidget(len(data), 2)
    table.setHorizontalHeaderLabels(["Номер разрыва", "Угол β"])
    table.horizontalHeader().setStretchLastSection(True)
    for i, entry in enumerate(data):
        table.setItem(i, 0, QTableWidgetItem(str(entry["number_of_the_gap"])))
        table.setItem(i, 1, QTableWidgetItem(str(entry["final_beta"])))
    content_layout.addWidget(table)

    btn_rose = QPushButton("Построить розу-диаграмму")
    btn_rose.setFixedHeight(50)
    content_layout.addWidget(btn_rose)

    def start_rose_process():
        table.setParent(None)
        btn_rose.setParent(None)
        content_widget.setParent(None)
        create_rose_data(tw, btn_rose, data)

    btn_rose.clicked.connect(start_rose_process)
    tw.show()


class EventFilter(QObject):
    def eventFilter(self, obj, event):
        if obj == state["view"].viewport() or obj == state["view"]:
            if event.type() == QEvent.Wheel:
                f = 1.25 if event.angleDelta().y() > 0 else 0.8
                state["view"].scale(f, f)
                return True

            if event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    if state["shift_pressed"]:
                        pos = state["view"].mapToScene(event.pos())
                        add_point(pos)
                        return True
                    else:
                        state["view"].setDragMode(QGraphicsView.ScrollHandDrag)
                        fake = QMouseEvent(event.type(), event.pos(), Qt.LeftButton, Qt.LeftButton, event.modifiers())
                        state["view"].mousePressEvent(fake)
                        return True

            if event.type() == QEvent.MouseButtonRelease:
                if event.button() == Qt.LeftButton:
                    state["view"].setDragMode(QGraphicsView.NoDrag)
                    return False

        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Shift:
                if not state["shift_pressed"]:
                    state["shift_pressed"] = True
                    state["current_gap_points"] = []
                return True
            if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_Z:
                undo_last()
                return True

        if event.type() == QEvent.KeyRelease and event.key() == Qt.Key_Shift:
            state["shift_pressed"] = False
            return True

        return super().eventFilter(obj, event)


def main():
    app = QApplication(sys.argv)
    win = QMainWindow()
    state["main_window"] = win
    win.setWindowTitle("SKAT")
    win.resize(1000, 850)
    central = QWidget()
    win.setCentralWidget(central)
    layout = QVBoxLayout(central)
    menu_container = QWidget()
    menu_layout = QHBoxLayout(menu_container)
    btn_open = QPushButton("Добавить фото разрывов")
    btn_open.setFixedSize(200, 60)
    btn_open.clicked.connect(open_file)
    btn_results = QPushButton("Вывести таблицу")
    state["btn_results"] = btn_results
    btn_results.setFixedSize(200, 60)
    btn_results.clicked.connect(open_table_window)
    btn_results.hide()
    menu_layout.addWidget(btn_open)
    menu_layout.addWidget(btn_results)
    layout.addWidget(menu_container, 0, Qt.AlignCenter)
    editor = QWidget()
    state["editor"] = editor
    ed_layout = QVBoxLayout(editor)
    scene = QGraphicsScene(0, 0, 10000, 10000)
    state["scene"] = scene
    view = QGraphicsView()
    state["view"] = view
    view.setScene(scene)
    view.setRenderHint(QPainter.Antialiasing)
    view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
    view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
    ed_layout.addWidget(view)
    btn_confirm = QPushButton("Закончить разметку")
    btn_confirm.setFixedHeight(50)
    btn_confirm.clicked.connect(finalize)
    ed_layout.addWidget(btn_confirm)
    layout.addWidget(editor)
    editor.hide()
    handler = EventFilter()
    app.installEventFilter(handler)
    view.viewport().installEventFilter(handler)
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
