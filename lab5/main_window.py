#!/usr/bin/env python3

import os
import sys
import csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QWidget, QFileDialog, QMessageBox,
    QFrame, QSizePolicy
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from iterator import ImageIterator


class IteratorWrapper:
    """
    Обёртка над моим ImageIterator, чтобы можно было двигаться вперёд-назад
    """

    def __init__(self, csv_file):
        self.original_iter = ImageIterator(csv_file)
        self.items = list(self.original_iter)
        self.index = 0

    def total(self):
        return len(self.items)

    def get_current(self):
        if not self.items:
            return None
        return self.items[self.index]

    def next(self):
        if not self.items:
            return None
        self.index = (self.index + 1) % len(self.items)
        return self.get_current()

    def prev(self):
        if not self.items:
            return None
        self.index = (self.index - 1) % len(self.items)
        return self.get_current()

    def current_index(self):
        return self.index


class ImageDatasetViewer(QMainWindow):
    """
    Главное окно для просмотра изображений.
    """

    def __init__(self):
        super().__init__()
        self.navigator = None
        self._build_ui()

    # ---------------- UI ----------------

    def _build_ui(self):
        self.setWindowTitle("Просмотрщик датасета")
        self.setMinimumSize(800, 600)

        container = QWidget()
        self.setCentralWidget(container)

        main = QVBoxLayout(container)

        # Панель управления
        controls = QHBoxLayout()

        self.btn_load_csv = QPushButton("Загрузить аннотацию CSV")
        self.btn_load_csv.clicked.connect(self.load_csv)

        self.btn_prev = QPushButton("← Назад")
        self.btn_prev.clicked.connect(self.show_prev)

        self.btn_next = QPushButton("Вперёд →")
        self.btn_next.clicked.connect(self.show_next)

        controls.addWidget(self.btn_load_csv)
        controls.addStretch()
        controls.addWidget(self.btn_prev)
        controls.addWidget(self.btn_next)

        self.lbl_info = QLabel("Загрузите аннотацию CSV для начала")
        self.lbl_info.setAlignment(Qt.AlignCenter)

        # Область изображения
        self.frame = QFrame()
        self.frame.setFrameStyle(QFrame.Box)
        self.frame.setMinimumSize(400, 300)

        img_layout = QVBoxLayout(self.frame)

        self.lbl_img = QLabel("Изображение не загружено")
        self.lbl_img.setAlignment(Qt.AlignCenter)
        self.lbl_img.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        img_layout.addWidget(self.lbl_img)

        # Добавление элементов
        main.addLayout(controls)
        main.addWidget(self.lbl_info)
        main.addWidget(self.frame, 1)

        self._update_buttons()

    # ---------------- Работа с аннотацией ----------------

    def load_csv(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Выберите CSV аннотацию",
            filter="CSV (*.csv)"
        )
        if not file:
            return

        try:
            self.navigator = IteratorWrapper(file)

            if self.navigator.total() == 0:
                QMessageBox.warning(self, "Ошибка", "Аннотация пуста!")
                return

            self._refresh_image()
            self._set_info("Аннотация CSV загружена")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

        self._update_buttons()

    # ---------------- Навигация ----------------

    def show_next(self):
        if self.navigator:
            self.navigator.next()
            self._refresh_image()

    def show_prev(self):
        if self.navigator:
            self.navigator.prev()
            self._refresh_image()

    # ---------------- Отображение ----------------

    def _refresh_image(self):
        if not self.navigator:
            return

        path = self.navigator.get_current()

        if not os.path.exists(path):
            self.lbl_img.setText("Файл не найден:\n" + path)
            return

        pixmap = QPixmap(path)

        if pixmap.isNull():
            self.lbl_img.setText("Ошибка загрузки:\n" + path)
            return

        # Масштабирование без искажений
        self.lbl_img.setPixmap(self._scale(pixmap))
        self._set_info()
        self._update_buttons()

    def _scale(self, pixmap):
        lab_size = self.lbl_img.size()
        w, h = lab_size.width() - 20, lab_size.height() - 20

        ow, oh = pixmap.width(), pixmap.height()
        scale = min(w / ow, h / oh, 1.0)

        return pixmap.scaled(int(ow * scale), int(oh * scale),
                             Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def _set_info(self, msg=None):
        if not self.navigator:
            self.lbl_info.setText("Аннотация не загружена")
            return

        if msg:
            self.lbl_info.setText(msg)
            return

        idx = self.navigator.current_index() + 1
        total = self.navigator.total()
        fname = os.path.basename(self.navigator.get_current())
        self.lbl_info.setText(f"{idx}/{total} | {fname}")

    def _update_buttons(self):
        active = self.navigator is not None and self.navigator.total() > 0
        self.btn_next.setEnabled(active)
        self.btn_prev.setEnabled(active)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.navigator:
            self._refresh_image()


def main():
    app = QApplication(sys.argv)
    w = ImageDatasetViewer()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
