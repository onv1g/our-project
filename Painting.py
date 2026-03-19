import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QFileDialog, QGraphicsView,
                             QGraphicsScene, QGraphicsPixmapItem, QGraphicsLineItem, QGraphicsEllipseItem)
from PyQt5.QtGui import QPixmap, QPen, QColor, QPainter
from PyQt5.QtCore import Qt
from AnglesFind import process_gaps


class DrawingView(QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.parent_window = parent

    def wheelEvent(self, event):
        factor = 1.25 if event.angleDelta().y() > 0 else 0.8
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        if self.parent_window.shift_pressed and event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            if 0 <= scene_pos.x() <= 1000 and 0 <= scene_pos.y() <= 1000:
                self.parent_window.add_point(scene_pos)
        super().mousePressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gap Mapper Pro")
        self.resize(1000, 800)
        self.setStyleSheet(
            "QMainWindow { background-color: white; } QPushButton { border: 2px solid black; padding: 10px; font-weight: bold; }")

        self.data_storage = {}
        self.gap_counter = 0
        self.current_gap_points = []
        self.shift_pressed = False
        self.history_items = []

        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Стартовый экран
        self.start_button = QPushButton("Выберите файл")
        self.start_button.setFixedSize(200, 60)
        self.main_layout.addWidget(self.start_button, 0, Qt.AlignCenter)
        self.start_button.clicked.connect(self.open_file_dialog)

        # Экран редактора
        self.editor_container = QWidget()
        layout = QVBoxLayout(self.editor_container)
        self.scene = QGraphicsScene(0, 0, 1000, 1000)
        self.view = DrawingView(self)
        self.view.setScene(self.scene)
        layout.addWidget(self.view)

        btn_layout = QHBoxLayout()
        self.btn_reset = QPushButton("Начать заново")
        self.btn_confirm = QPushButton("Подтвердить")
        self.btn_reset.clicked.connect(self.reset_ui)
        self.btn_confirm.clicked.connect(self.finalize_data)
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addWidget(self.btn_confirm)
        layout.addLayout(btn_layout)

        self.main_layout.addWidget(self.editor_container)
        self.editor_container.hide()

    def open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выбор", "", "Images (*.jpg *.jpeg *.png)")
        if path:
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                self.scene.clear()
                bg = QGraphicsPixmapItem(pixmap.scaled(1000, 1000, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
                self.scene.addItem(bg)
                self.start_button.hide()
                self.editor_container.show()
                self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Shift:
            self.shift_pressed = True
            self.gap_counter += 1
            self.current_gap_points = []
        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_Z:
            self.undo_last_action()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Shift:
            self.shift_pressed = False

    def add_point(self, point):
        radius = 6
        dot = QGraphicsEllipseItem(point.x() - radius, point.y() - radius, radius * 2, radius * 2)
        dot.setBrush(QColor(0, 0, 0))
        self.scene.addItem(dot)

        action_items = [dot]
        if self.current_gap_points:
            p1 = self.current_gap_points[-1]
            line = QGraphicsLineItem(p1.x(), p1.y(), point.x(), point.y())
            line.setPen(QPen(QColor(0, 0, 0), 4))
            self.scene.addItem(line)
            action_items.append(line)

            gap_key = f"gap_{self.gap_counter}"
            if gap_key not in self.data_storage:
                self.data_storage[gap_key] = []

            self.data_storage[gap_key].append({
                "x1": int(p1.x()), "y1": int(p1.y()),
                "x2": int(point.x()), "y2": int(point.y())
            })
            self.history_items.append({'graphics': action_items, 'gap_key': gap_key})
        else:
            self.history_items.append({'graphics': action_items, 'gap_key': None})

        self.current_gap_points.append(point)

    def finalize_data(self):
        process_gaps(self.data_storage)
        self.reset_ui()
        self.editor_container.hide()
        self.start_button.show()

    def undo_last_action(self):
        if self.history_items:
            last = self.history_items.pop()
            for item in last['graphics']:
                self.scene.removeItem(item)
            if last['gap_key'] and last['gap_key'] in self.data_storage:
                if self.data_storage[last['gap_key']]:
                    self.data_storage[last['gap_key']].pop()
            if self.current_gap_points:
                self.current_gap_points.pop()

    def reset_ui(self):
        self.data_storage = {};
        self.gap_counter = 0;
        self.history_items = [];
        self.current_gap_points = []
        for item in self.scene.items():
            if isinstance(item, (QGraphicsLineItem, QGraphicsEllipseItem)):
                self.scene.removeItem(item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
