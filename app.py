import sys
import os
import PyQt5
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QLabel, QFileDialog, QScrollArea)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QEvent

# Настройка путей (стандартная часть)
dirname = os.path.dirname(PyQt5.__file__)
plugin_path = os.path.join(dirname, 'Qt5', 'plugins', 'platforms')
if not os.path.exists(plugin_path):
    plugin_path = os.path.join(dirname, 'Qt', 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path



class PreciseImageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.zoom_level = 1.0
        self.original_pixmap = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Precise Pixel Zoom')
        self.resize(1100, 900)
        self.setStyleSheet("background-color: #2E3234;")

        self.layout = QVBoxLayout(self)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(False)
        self.scroll.setAlignment(Qt.AlignCenter)
        self.scroll.setStyleSheet("background-color: #1A1A1A; border: 2px solid #444;")

        # --- ВАЖНО: Устанавливаем фильтр событий на область просмотра ---
        self.scroll.viewport().installEventFilter(self)

        self.img_label = QLabel("Выберите файл")
        self.img_label.setStyleSheet("color: #AAA;")
        self.scroll.setWidget(self.img_label)

        self.btn = QPushButton('Загрузить изображение')
        self.btn.setFixedSize(220, 45)
        self.btn.setStyleSheet("background-color: #646464; color: white; font-weight: bold;")
        self.btn.clicked.connect(self.load_image)

        self.layout.addWidget(self.scroll)
        self.layout.addWidget(self.btn, 0, Qt.AlignCenter)

    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Открыть", "", "Images (*.png *.jpg *.bmp)")
        if path:
            self.original_pixmap = QPixmap(path)
            self.zoom_level = 1.0
            self.display_image()

    def display_image(self):
        if self.original_pixmap:
            w = int(self.original_pixmap.width() * self.zoom_level)
            h = int(self.original_pixmap.height() * self.zoom_level)
            scaled = self.original_pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.FastTransformation)
            self.img_label.setPixmap(scaled)
            self.img_label.setFixedSize(w, h)

    # --- ЭТА ФУНКЦИЯ ПЕРЕХВАТЫВАЕТ КОЛЕСИКО ---
    def eventFilter(self, source, event):
        # Если событие — это прокрутка колесика и зажат Ctrl
        if event.type() == QEvent.Wheel and event.modifiers() == Qt.ControlModifier:
            self.handle_zoom(event)
            return True  # Говорим системе: "Я обработал это сам, не крути страницу!"
        return super().eventFilter(source, event)

    def handle_zoom(self, event):
        if not self.original_pixmap:
            return

        h_bar = self.scroll.horizontalScrollBar()
        v_bar = self.scroll.verticalScrollBar()

        # Позиция курсора внутри видимой области
        cursor_pos = event.pos()

        # Точка на картинке, куда мы навели (в текущем масштабе)
        target_x = (h_bar.value() + cursor_pos.x()) / self.zoom_level
        target_y = (v_bar.value() + cursor_pos.y()) / self.zoom_level

        # Масштабируем
        old_zoom = self.zoom_level
        if event.angleDelta().y() > 0:
            self.zoom_level *= 1.2
        else:
            self.zoom_level /= 1.2

        self.zoom_level = max(0.05, min(self.zoom_level, 50.0))

        self.display_image()

        # Корректируем скролл, чтобы пиксель остался под мышкой
        h_bar.setValue(int(target_x * self.zoom_level - cursor_pos.x()))
        v_bar.setValue(int(target_y * self.zoom_level - cursor_pos.y()))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PreciseImageApp()
    window.show()
    sys.exit(app.exec_())