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
from PyQt5.QtCore import Qt, QObject, QEvent, QPointF
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

    base_factor = 1.0
    if state["view"]:
        transform = state["view"].transform()
        scale_factor = transform.m11()
        if scale_factor > 0:
            base_factor = 1.0 / scale_factor

    if not state["current_gap_points"]:
        max_idx = 0
        for key in state["data_storage"].keys():
            try:
                num = int(key.split('_')[1])
                if num > max_idx:
                    max_idx = num
            except (IndexError, ValueError):
                pass

        state["gap_counter"] = max_idx + 1
        gap_key = f"gap_{state['gap_counter']}"

        text = QGraphicsTextItem(str(state["gap_counter"]))
        text.setDefaultTextColor(QColor(255, 0, 0))
        font = text.font()
        font.setPointSize(int(25 * base_factor))
        text.setFont(font)
        text.setPos(p.x() + (6 * base_factor), p.y() - (6 * base_factor))
        text.setData(0, "gap_text")
        text.setData(1, gap_key)
        state["scene"].addItem(text)
        current_action.append(text)
    else:
        gap_key = f"gap_{state['gap_counter']}"

    current_radius = 10 * base_factor
    dot = QGraphicsEllipseItem(p.x() - current_radius, p.y() - current_radius, current_radius * 2, current_radius * 2)
    dot.setBrush(QColor(255, 0, 0))

    dot.setData(1, gap_key)
    if len(state["current_gap_points"]) == 0:
        dot.setData(0, "start_point")
    else:
        dot.setData(0, "regular_point")

    state["scene"].addItem(dot)
    current_action.append(dot)

    if state["current_gap_points"]:
        p1 = state["current_gap_points"][-1]
        line = QGraphicsLineItem(p1.x(), p1.y(), p.x(), p.y())
        line.setPen(QPen(QColor(0, 255, 0), 5 * base_factor))

        line.setData(0, "gap_line")
        line.setData(1, gap_key)

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
        'is_first_point': len(state["current_gap_points"]) == 1
    })
    state["current_gap_points"].append(p)


def undo_last():
    target_key = f"gap_{state['gap_counter']}" if state["current_gap_points"] else None

    idx_to_remove = -1
    if target_key:
        for i in range(len(state["history_items"]) - 1, -1, -1):
            if state["history_items"][i]['gap_key'] == target_key:
                idx_to_remove = i
                break
    elif state["history_items"]:
        idx_to_remove = len(state["history_items"]) - 1

    if idx_to_remove != -1:
        last = state["history_items"].pop(idx_to_remove)
        for item in last['graphics']:
            state["scene"].removeItem(item)
        key = last['gap_key']
        if key in state["data_storage"] and state["data_storage"][key]:
            state["data_storage"][key].pop()
            if not state["data_storage"][key]:
                del state["data_storage"][key]
        if state["current_gap_points"]:
            state["current_gap_points"].pop()


def open_file():
    p, _ = QFileDialog.getOpenFileName(state["main_window"], "Выбор изображения", "", "Images (*.png *.jpg *.jpeg)")
    if p:
        state["scene"].clear()
        state["data_storage"] = {}
        state["gap_counter"] = 0
        state["current_gap_points"] = []
        state["history_items"] = []
        pix = QPixmap(p).scaled(10000, 10000, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
    table.setHorizontalHeaderLabels(["Номер разлома", "Угол β"])
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
    def __init__(self):
        super().__init__()
        self.last_hovered_gap_key = None
        self.active_selected_gap_key = None

    def update_gap_lines_color(self, gap_key, color):
        if not gap_key:
            return
        for item in state["scene"].items():
            if isinstance(item, QGraphicsLineItem) and item.data(1) == gap_key:
                pen = item.pen()
                pen.setColor(color)
                item.setPen(pen)

    def refresh_highlights(self):
        for item in state["scene"].items():
            if isinstance(item, QGraphicsLineItem):
                pen = item.pen()
                if self.active_selected_gap_key and item.data(1) == self.active_selected_gap_key:
                    pen.setColor(QColor(0, 255, 0))
                else:
                    pen.setColor(QColor(0, 0, 0))
                item.setPen(pen)

    def eventFilter(self, obj, event):
        if obj == state["view"].viewport() or obj == state["view"]:
            if event.type() == QEvent.MouseMove:
                scene_pos = state["view"].mapToScene(event.pos())
                item = state["scene"].itemAt(scene_pos, state["view"].transform())

                detected_key = None
                if isinstance(item, (QGraphicsEllipseItem, QGraphicsLineItem)) and item.data(1) is not None:
                    detected_key = item.data(1)

                if detected_key:
                    if detected_key != self.active_selected_gap_key:
                        if self.last_hovered_gap_key and self.last_hovered_gap_key != detected_key and self.last_hovered_gap_key != self.active_selected_gap_key:
                            self.update_gap_lines_color(self.last_hovered_gap_key, QColor(0, 0, 0))

                        self.update_gap_lines_color(detected_key, QColor(0, 255, 0))
                        self.last_hovered_gap_key = detected_key
                else:
                    if self.last_hovered_gap_key and self.last_hovered_gap_key != self.active_selected_gap_key:
                        self.update_gap_lines_color(self.last_hovered_gap_key, QColor(0, 0, 0))
                        self.last_hovered_gap_key = None

            if event.type() == QEvent.Wheel:
                f = 1.25 if event.angleDelta().y() > 0 else 0.8
                state["view"].scale(f, f)

                transform = state["view"].transform()
                scale_factor = transform.m11()

                if scale_factor > 0:
                    base_factor = 1.0 / scale_factor

                    for item in state["scene"].items():
                        if isinstance(item, QGraphicsLineItem):
                            pen = item.pen()
                            pen.setWidthF(5 * base_factor)
                            item.setPen(pen)

                        elif isinstance(item, QGraphicsEllipseItem):
                            rect = item.rect()
                            center = rect.center()
                            new_radius = 10 * base_factor
                            item.setRect(center.x() - new_radius, center.y() - new_radius, new_radius * 2,
                                         new_radius * 2)

                        elif isinstance(item, QGraphicsTextItem):
                            font = item.font()
                            font.setPointSize(int(25 * base_factor))
                            item.setFont(font)

                return True

            if event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    pos = state["view"].mapToScene(event.pos())

                    if state["shift_pressed"]:
                        clicked_item = state["scene"].itemAt(pos, state["view"].transform())
                        if isinstance(clicked_item, (QGraphicsEllipseItem, QGraphicsLineItem)) and clicked_item.data(
                                1) is not None:
                            gap_key = clicked_item.data(1)
                            try:
                                gap_num = int(gap_key.split('_')[1])
                                state["gap_counter"] = gap_num
                                self.active_selected_gap_key = gap_key

                                segments = state["data_storage"].get(gap_key, [])
                                points = []
                                if segments:
                                    points.append(QPointF(segments[0]["x1"], segments[0]["y1"]))
                                    for seg in segments:
                                        points.append(QPointF(seg["x2"], seg["y2"]))
                                else:
                                    if isinstance(clicked_item, QGraphicsEllipseItem):
                                        points.append(clicked_item.rect().center())
                                    else:
                                        for item in state["scene"].items():
                                            if isinstance(item, QGraphicsEllipseItem) and item.data(
                                                    1) == gap_key and item.data(0) == "start_point":
                                                points.append(item.rect().center())
                                                break

                                state["current_gap_points"] = points
                                self.refresh_highlights()
                                return True
                            except (ValueError, IndexError):
                                pass

                        if not state["current_gap_points"]:
                            self.active_selected_gap_key = None

                        add_point(pos)
                        self.active_selected_gap_key = f"gap_{state['gap_counter']}"
                        self.refresh_highlights()
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
                return True
            if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_Z:
                undo_last()
                self.refresh_highlights()
                return True

        if event.type() == QEvent.KeyRelease and event.key() == Qt.Key_Shift:
            state["shift_pressed"] = False
            state["current_gap_points"] = []
            return True

        return super().eventFilter(obj, event)


def main():
    app = QApplication(sys.argv)
    win = QMainWindow()
    state["main_window"] = win
    win.setWindowTitle("SKAT")

    win.showMaximized()

    central = QWidget()
    win.setCentralWidget(central)
    layout = QVBoxLayout(central)
    menu_container = QWidget()
    menu_layout = QHBoxLayout(menu_container)
    btn_open = QPushButton("Добавить фото карты")
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

    view.setMouseTracking(True)
    view.viewport().setMouseTracking(True)

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