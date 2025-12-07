import os
import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QWidget, QFileDialog, QMessageBox,
    QFrame, QSizePolicy
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class DatasetNavigator:
    """
    Класс-переборщик для изображений в датасете.
    Позволяет проходить по списку файлов вперёд/назад и
    получать текущее изображение.
    """

    def __init__(self, annotation=None, directory=None):
        self.annotation = annotation
        self.directory = directory

        self.index = 0
        self.paths = []

        self._prepare_data()

    def _prepare_data(self):
        """Собирает список изображений из CSV или папки."""
        if self.annotation and os.path.exists(self.annotation):
            df = pd.read_csv(self.annotation)

            if {"absolute_path", "relative_path"}.issubset(df.columns):
                self.paths = df["absolute_path"].tolist()
            else:
                # fallback, если названия колонок отличаются
                self.paths = df.iloc[:, 1].tolist()

        elif self.directory and os.path.isdir(self.directory):
            exts = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"}
            for f in os.listdir(self.directory):
                if any(f.lower().endswith(ext) for ext in exts):
                    self.paths.append(os.path.join(self.directory, f))

        self.paths.sort()

    def __len__(self):
        return len(self.paths)

    def get_current(self):
        if not self.paths:
            return None
        return self.paths[self.index]

    def next(self):
        if not self.paths:
            return None
        self.index = (self.index + 1) % len(self.paths)
        return self.get_current()

    def prev(self):
        if not self.paths:
            return None
        self.index = (self.index - 1) % len(self.paths)
        return self.get_current()

    def current_index(self):
        return self.index

    def total(self):
        return len(self.paths)

    def reset(self):
        self.index = 0


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
        self.setWindowTitle("Просмотрщик датасета птиц")
        self.setMinimumSize(800, 600)

        container = QWidget()
        self.setCentralWidget(container)

        main = QVBoxLayout(container)

        # Панель управления
        controls = QHBoxLayout()

        self.btn_load_dir = QPushButton("Загрузить папку")
        self.btn_load_dir.clicked.connect(self.load_dir)

        self.btn_load_csv = QPushButton("Загрузить аннотацию")
        self.btn_load_csv.clicked.connect(self.load_csv)

        self.btn_prev = QPushButton("← Назад")
        self.btn_prev.clicked.connect(self.show_prev)

        self.btn_next = QPushButton("Вперёд →")
        self.btn_next.clicked.connect(self.show_next)

        controls.addWidget(self.btn_load_dir)
        controls.addWidget(self.btn_load_csv)
        controls.addStretch()
        controls.addWidget(self.btn_prev)
        controls.addWidget(self.btn_next)

        self.lbl_info = QLabel("Загрузите датасет для начала просмотра")
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

    # ---------------- Работа с датасетом ----------------

    def load_dir(self):
        path = QFileDialog.getExistingDirectory(
            self, "Выберите папку с изображениями"
        )
        if path:
            self._load_from_dir(path)

    def load_csv(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл аннотации",
            filter="CSV (*.csv)"
        )
        if file:
            self._load_from_csv(file)

    def _load_from_dir(self, path):
        try:
            self.navigator = DatasetNavigator(directory=path)
            if len(self.navigator) == 0:
                QMessageBox.warning(self, "Ошибка", "В папке нет изображений!")
                self._update_buttons()
                return
            self._refresh_image()
            self._set_info("Датасет загружен из папки")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            self._update_buttons()

    def _load_from_csv(self, path):
        try:
            self.navigator = DatasetNavigator(annotation=path)
            if len(self.navigator) == 0:
                QMessageBox.warning(self, "Ошибка", "Аннотация пуста!")
                self._update_buttons()
                return
            self._refresh_image()
            self._set_info("Датасет загружен из аннотации")
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
        if not self.navigator or len(self.navigator) == 0:
            return

        path = self.navigator.get_current()

        if not os.path.exists(path):
            self.lbl_img.setText("Файл не найден:\n" + path)
            return

        pixmap = QPixmap(path)

        if pixmap.isNull():
            self.lbl_img.setText("Ошибка загрузки:\n" + path)
            return

        self.lbl_img.setPixmap(self._scale(pixmap))
        self._set_info()
        self._update_buttons()

    def _scale(self, pixmap):
        """Масштабирует изображение под размеры QLabel."""
        lab_size = self.lbl_img.size()
        w, h = lab_size.width() - 20, lab_size.height() - 20

        ow, oh = pixmap.width(), pixmap.height()
        scale = min(w / ow, h / oh, 1.0)

        return pixmap.scaled(int(ow * scale), int(oh * scale),
                             Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def _set_info(self, msg=None):
        if msg:
            self.lbl_info.setText(msg)
        elif self.navigator:
            idx = self.navigator.current_index() + 1
            total = self.navigator.total()
            fname = os.path.basename(self.navigator.get_current())
            self.lbl_info.setText(f"{idx}/{total} | {fname}")
        else:
            self.lbl_info.setText("Датасет не загружен")

    def _update_buttons(self):
        active = self.navigator is not None and len(self.navigator) > 0
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
