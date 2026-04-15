import sys, os, math, json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import PyQt5
from rose import create_rose_data
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QFileDialog, QGraphicsView,
                             QGraphicsScene, QGraphicsPixmapItem, QGraphicsLineItem,
                             QGraphicsEllipseItem, QTableWidget, QTableWidgetItem,
                             QLineEdit, QLabel, QFrame)
from PyQt5.QtGui import QPixmap, QPen, QColor, QPainter, QMouseEvent
from PyQt5.QtCore import Qt, QObject, QEvent, QPointF, QRectF


dirname = os.path.dirname(PyQt5.__file__)
plugin_path = os.path.join(dirname, 'Qt5', 'plugins', 'platforms')
if not os.path.exists(plugin_path):
    plugin_path = os.path.join(dirname, 'Qt', 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


state = {
    "scene": None, "view": None, "editor": None, "btn_res": None,
    "data_storage": {}, "gap_counter": 0, "current_gap_points": [],
    "shift_pressed": False, "history_items": [], "final_list": [],
    "img_rect": QRectF(), "table_window": None, "chart_container": None
}



def calculate_beta(p1, p2):
    dx, dy = p2.x() - p1.x(), p2.y() - p1.y()
    return math.floor(abs(math.degrees(math.atan2(dy, dx)))) if dx != 0 else 90


def build_final_data():
    res = []
    for g_id, segments in state["data_storage"].items():
        if not segments: continue
        betas = [calculate_beta(QPointF(s['x1'], s['y1']), QPointF(s['x2'], s['y2'])) for s in segments]
        num = int(g_id.split('_')[1])
        res.append({
            "number_of_the_gap": num,
            "final_beta": math.floor(sum(betas) / len(betas)) if betas else 0,
            "segments": segments
        })
    return sorted(res, key=lambda x: x["number_of_the_gap"])



def add_point_safe(pos):
    if not state["img_rect"].contains(pos): return

    gap_key = f"gap_{state['gap_counter']}"
    dot = QGraphicsEllipseItem(pos.x() - 5, pos.y() - 5, 10, 10)
    dot.setBrush(QColor(255, 50, 50));
    dot.setZValue(10)
    state["scene"].addItem(dot)

    action_items = [dot]

    if state["current_gap_points"]:
        p_prev = state["current_gap_points"][-1]
        line = QGraphicsLineItem(p_prev.x(), p_prev.y(), pos.x(), pos.y())
        line.setPen(QPen(Qt.black, 3, Qt.SolidLine, Qt.RoundCap));
        line.setZValue(5)
        state["scene"].addItem(line)
        action_items.append(line)

        if gap_key not in state["data_storage"]: state["data_storage"][gap_key] = []
        state["data_storage"][gap_key].append({"x1": p_prev.x(), "y1": p_prev.y(), "x2": pos.x(), "y2": pos.y()})

    state["current_gap_points"].append(pos)
    state["history_items"].append({"items": action_items, "key": gap_key})


def undo():
    if not state["history_items"]: return
    last = state["history_items"].pop()
    for item in last["items"]:
        if item.scene(): state["scene"].removeItem(item)
    key = last["key"]
    if key in state["data_storage"] and state["data_storage"][key]: state["data_storage"][key].pop()
    if state["current_gap_points"]: state["current_gap_points"].pop()



def draw_rose():
    data = state["final_list"]
    if not data: return
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw={'projection': 'polar'})
    vals = [r["final_beta"] for r in data]
    bins = np.deg2rad(np.arange(0, 181, 10))
    counts, _ = np.histogram(np.deg2rad(vals), bins=bins)
    ax.bar(np.concatenate([bins[:-1], bins[:-1] + np.pi]), np.concatenate([counts, counts]),
           width=np.deg2rad(8), color='lime', alpha=0.7, edgecolor='k')
    ax.set_theta_zero_location('N');
    ax.set_theta_direction(-1)

    canvas = FigureCanvas(fig)
    layout = state["chart_container"].layout()
    while layout.count():
        item = layout.takeAt(0)
        if item.widget(): item.widget().deleteLater()
    layout.addWidget(canvas)


def open_table():
    tw = QWidget();
    state["table_window"] = tw
    tw.setWindowTitle("Анализ данных");
    tw.resize(600, 700)
    vbox = QVBoxLayout(tw)
    table = QTableWidget(len(state["final_list"]), 2)
    table.setHorizontalHeaderLabels(["№ Разрыва", "Угол β"])
    table.horizontalHeader().setStretchLastSection(True)
    for i, r in enumerate(state["final_list"]):
        table.setItem(i, 0, QTableWidgetItem(str(r["number_of_the_gap"])))
        table.setItem(i, 1, QTableWidgetItem(str(r["final_beta"]) + "°"))
    vbox.addWidget(table)

    btn_rose = QPushButton("Построить розу");
    btn_rose.setFixedHeight(50)
    vbox.addWidget(btn_rose)
    state["chart_container"] = QWidget();
    state["chart_container"].setLayout(QVBoxLayout())
    vbox.addWidget(state["chart_container"]);
    state["chart_container"].hide()

    btn_rose.clicked.connect(lambda: (table.hide(), btn_rose.hide(), state["chart_container"].show(), draw_rose()))
    tw.show()


class GlobalHandler(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Shift:
                state["shift_pressed"] = True;
                state["gap_counter"] += 1;
                state["current_gap_points"] = []
            if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_Z:
                undo();
                return True
        elif event.type() == QEvent.KeyRelease and event.key() == Qt.Key_Shift:
            state["shift_pressed"] = False

        if obj == state["view"].viewport():
            if event.type() == QEvent.Wheel:
                f = 1.2 if event.angleDelta().y() > 0 else 0.8
                state["view"].setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
                state["view"].scale(f, f);
                return True
            if event.type() == QEvent.MouseButtonPress:
                if state["shift_pressed"] and event.button() == Qt.LeftButton:
                    add_point_safe(state["view"].mapToScene(event.pos()));
                    return True
                if event.button() == Qt.RightButton:
                    state["view"].setDragMode(QGraphicsView.ScrollHandDrag);
                    return True
            if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.RightButton:
                state["view"].setDragMode(QGraphicsView.NoDrag)
        return False



def open_image():
    path, _ = QFileDialog.getOpenFileName(None, "Открыть фото", "", "Images (*.png *.jpg *.jpeg)")
    if path:
        state["scene"].clear()
        state["data_storage"].clear();
        state["history_items"].clear();
        state["current_gap_points"].clear()
        state["gap_counter"] = 0
        pix = QPixmap(path)
        state["scene"].addPixmap(pix)
        state["img_rect"] = QRectF(pix.rect())
        state["scene"].setSceneRect(state["img_rect"])
        state["editor"].show();
        state["btn_res"].hide()
        state["view"].fitInView(state["img_rect"], Qt.KeepAspectRatio)


def confirm():
    state["final_list"] = build_final_data()
    state["editor"].hide();
    state["btn_res"].show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setWindowTitle("Gap Mapper Pro")

    win.setWindowState(Qt.WindowMaximized)

    state["win"] = win
    central = QWidget()
    win.setCentralWidget(central)
    main_layout = QVBoxLayout(central)


    menu_box = QHBoxLayout()
    menu_box.addStretch()
    btn_load = QPushButton("📂 Выбрать изображение");
    btn_load.setFixedSize(250, 60)
    state["btn_res"] = QPushButton("📊 Показать таблицу");
    state["btn_res"].setFixedSize(250, 60)
    state["btn_res"].hide()
    menu_box.addWidget(btn_load);
    menu_box.addWidget(state["btn_res"])
    menu_box.addStretch()
    main_layout.addLayout(menu_box)
    state["editor"] = QWidget();
    ed_lay = QVBoxLayout(state["editor"])
    state["scene"] = QGraphicsScene()
    state["view"] = QGraphicsView(state["scene"])
    state["view"].setRenderHint(QPainter.Antialiasing)
    state["view"].setBackgroundBrush(QColor(35, 35, 35))
    btn_box = QHBoxLayout()
    btn_box.addStretch()
    btn_ok = QPushButton("✅ Завершить разметку");
    btn_ok.setFixedSize(300, 50)
    btn_box.addWidget(btn_ok);
    btn_box.addStretch()
    ed_lay.addWidget(state["view"]);
    ed_lay.addLayout(btn_box)
    main_layout.addWidget(state["editor"]);
    state["editor"].hide()
    btn_load.clicked.connect(open_image)
    btn_ok.clicked.connect(confirm)
    state["btn_res"].clicked.connect(open_table)
    handler = GlobalHandler()
    app.installEventFilter(handler)
    state["view"].viewport().installEventFilter(handler)
    win.show()
    win.showMaximized()

    sys.exit(app.exec_())

