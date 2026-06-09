import sys
from db import get_db_connection, get_user, get_tasks, get_methods, get_users
import numpy as np
from PyQt6.QtWidgets import (QApplication, QDoubleSpinBox, QFormLayout, QGroupBox, QSpinBox, QWidget, QVBoxLayout, QDialog, QListWidget, QTextEdit,
                             QPushButton, QLabel, QHBoxLayout, QButtonGroup, QLineEdit, QRadioButton, QTabWidget, QTableWidgetItem, QHeaderView,
                             QTableWidget, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sqlite3
import random


class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ОХП - Вход")

        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        sw = screen_geometry.width()
        sh = screen_geometry.height()
        width = int(sw / 4)
        height = int(sh / 4)
        x = int((sw - width) / 2)
        y = int((sh - height) / 2)
        self.setGeometry(x, y, width, height)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Оптимизация химических процессов")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(6)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.on_click)

        form.addRow("Логин:", self.login_input)
        form.addRow("Пароль:", self.password_input)
        layout.addLayout(form)

        self.button_enter = QPushButton("Войти")
        self.button_enter.clicked.connect(self.on_click)
        layout.addWidget(self.button_enter)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def on_click(self):
        login = self.login_input.text().strip()
        password = self.password_input.text()

        if not login or not password:
            self.result_label.setText("<span style='color: #e74c3c;'>Заполните все поля.</span>")
            return

        try:
            user = get_user(login)
        except Exception as e:
            self.result_label.setText(f"<span style='color: #e74c3c;'>Ошибка подключения к БД: {e}</span>")
            return

        if user is None or user["password"] != password:
            self.result_label.setText("<span style='color: #e74c3c;'>Неверный логин или пароль.</span>")
            return

        if user["role"] == "admin":
            self.admin_window = AdminWindow()
            self.admin_window.show()
            self.close()
        else:
            self.researcher_window = ResearcherWindow()
            self.researcher_window.show()
            self.close()


class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ОХП - Панель администратора")
        self.setGeometry(100, 100, 900, 600)

        self.users   = []
        self.tasks   = []
        self.methods = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)

        title = QLabel("Панель администратора")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 15px; font-weight: bold; margin-bottom: 4px;")
        main_layout.addWidget(title)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_users_tab(),   "👤 Пользователи")
        self.tabs.addTab(self._build_tasks_tab(),   "📋 Задачи")
        self.tabs.addTab(self._build_methods_tab(), "⚙️ Методы")
        main_layout.addWidget(self.tabs)

    # ── Пользователи ──

    def _build_users_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)

        left = QVBoxLayout()
        self.user_list = QListWidget()
        self.user_list.currentRowChanged.connect(self._show_user_info)
        left.addWidget(self.user_list)

        btns = QHBoxLayout()
        btn_add  = QPushButton("Добавить")
        btn_edit = QPushButton("Редактировать")
        btn_del  = QPushButton("Удалить")
        btn_add.clicked.connect(self._add_user)
        btn_edit.clicked.connect(self._edit_user)
        btn_del.clicked.connect(self._delete_user)
        for b in (btn_add, btn_edit, btn_del):
            btns.addWidget(b)
        left.addLayout(btns)

        right = QVBoxLayout()
        info_label = QLabel("Информация")
        info_label.setStyleSheet("font-weight: bold;")
        self.user_info = QTextEdit()
        self.user_info.setReadOnly(True)
        right.addWidget(info_label)
        right.addWidget(self.user_info)

        layout.addLayout(left,  2)
        layout.addLayout(right, 1)

        self._refresh_users_from_db()
        return tab

    def _refresh_users_from_db(self):
        self.users = list(get_users())
        self.user_list.clear()
        for u in self.users:
            role_text = "Администратор" if u["role"] == "admin" else "Исследователь"
            self.user_list.addItem(f"{u['username']}  ({role_text})")

    def _show_user_info(self, idx):
        if idx < 0 or idx >= len(self.users):
            self.user_info.clear()
            return
        u = self.users[idx]
        role_text = "Администратор" if u["role"] == "admin" else "Исследователь"
        self.user_info.setHtml(
            f"<b>Логин:</b> {u['username']}<br>"
            f"<b>Роль:</b> {role_text}"
        )

    def _add_user(self):
        dlg = _UserDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            username, password, role = dlg.get_data()
            if not username.strip() or not password.strip():
                return
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                            (username, password, role))
                conn.commit()
                self._refresh_users_from_db()
            except sqlite3.IntegrityError:
                pass
                QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже существует!")
            finally:
                cur.close()
                conn.close()

    def _edit_user(self):
        idx = self.user_list.currentRow()
        if idx < 0 or idx >= len(self.users):
            return
        u = self.users[idx]
        dlg = _UserDialog(u["username"], u["password"], u["role"], parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            username, password, role = dlg.get_data()
            if not username.strip() or not password.strip():
                return
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute('UPDATE users SET username=?, password=?, role=? WHERE id=?',
                            (username, password, role, u["id"]))
                conn.commit()
                self._refresh_users_from_db()
            except sqlite3.IntegrityError:
                pass
                QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже существует!")
            finally:
                cur.close()
                conn.close()

    def _delete_user(self):
        idx = self.user_list.currentRow()
        if idx < 0 or idx >= len(self.users):
            return
        u = self.users[idx]
        if u["username"] == "admin":
            QMessageBox.warning(self, "Ошибка", "Нельзя удалить пользователя admin!")
            return
        reply = QMessageBox.question(self, "Удалить пользователя",
                                     f'Удалить пользователя "{u["username"]}"?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('DELETE FROM users WHERE id=?', (u["id"],))
            conn.commit()
            cur.close()
            conn.close()
            self._refresh_users_from_db()
            self.user_info.clear()

    # ── Задачи ──

    def _build_tasks_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)

        left = QVBoxLayout()
        self.task_list = QListWidget()
        self.task_list.currentRowChanged.connect(self._show_task_info)
        left.addWidget(self.task_list)

        btns = QHBoxLayout()
        btn_add  = QPushButton("Добавить")
        btn_edit = QPushButton("Редактировать")
        btn_del  = QPushButton("Удалить")
        btn_add.clicked.connect(self._add_task)
        btn_edit.clicked.connect(self._edit_task)
        btn_del.clicked.connect(self._delete_task)
        for b in (btn_add, btn_edit, btn_del):
            btns.addWidget(b)
        left.addLayout(btns)

        right = QVBoxLayout()
        info_label = QLabel("Описание")
        info_label.setStyleSheet("font-weight: bold;")
        self.task_info = QTextEdit()
        self.task_info.setReadOnly(True)
        right.addWidget(info_label)
        right.addWidget(self.task_info)

        layout.addLayout(left,  2)
        layout.addLayout(right, 1)

        self._refresh_tasks_from_db()
        return tab

    def _refresh_tasks_from_db(self):
        self.tasks = list(get_tasks())
        self.task_list.clear()
        for t in self.tasks:
            self.task_list.addItem(t["title"])

    def _show_task_info(self, idx):
        if idx < 0 or idx >= len(self.tasks):
            self.task_info.clear()
            return
        t = self.tasks[idx]
        self.task_info.setHtml(f"<b>{t['title']}</b><br><br>{t['description']}")

    def _add_task(self):
        dlg = _TextDialog("Новая задача", parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            title, desc = dlg.get_data()
            if title.strip():
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('INSERT INTO tasks (title, description, is_active) VALUES (?, ?, ?)',
                            (title, desc, 1))
                conn.commit()
                cur.close()
                conn.close()
                self._refresh_tasks_from_db()

    def _edit_task(self):
        idx = self.task_list.currentRow()
        if idx < 0 or idx >= len(self.tasks):
            return
        t = self.tasks[idx]
        dlg = _TextDialog("Редактировать задачу", t["title"], t["description"], parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            title, desc = dlg.get_data()
            if title.strip():
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('UPDATE tasks SET title=?, description=? WHERE id=?',
                            (title, desc, t["id"]))
                conn.commit()
                cur.close()
                conn.close()
                self._refresh_tasks_from_db()

    def _delete_task(self):
        idx = self.task_list.currentRow()
        if idx < 0 or idx >= len(self.tasks):
            return
        reply = QMessageBox.question(self, "Удалить задачу",
                                     f'Удалить задачу "{self.tasks[idx]["title"]}"?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('DELETE FROM tasks WHERE id=?', (self.tasks[idx]["id"],))
            conn.commit()
            cur.close()
            conn.close()
            self._refresh_tasks_from_db()
            self.task_info.clear()

    # ── Методы ──

    def _build_methods_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)

        left = QVBoxLayout()
        self.method_list = QListWidget()
        self.method_list.currentRowChanged.connect(self._show_method_info)
        left.addWidget(self.method_list)

        btns = QHBoxLayout()
        btn_add  = QPushButton("Добавить")
        btn_edit = QPushButton("Редактировать")
        btn_del  = QPushButton("Удалить")
        btn_add.clicked.connect(self._add_method)
        btn_edit.clicked.connect(self._edit_method)
        btn_del.clicked.connect(self._delete_method)
        for b in (btn_add, btn_edit, btn_del):
            btns.addWidget(b)
        left.addLayout(btns)

        right = QVBoxLayout()
        info_label = QLabel("Описание")
        info_label.setStyleSheet("font-weight: bold;")
        self.method_info = QTextEdit()
        self.method_info.setReadOnly(True)
        right.addWidget(info_label)
        right.addWidget(self.method_info)

        layout.addLayout(left,  2)
        layout.addLayout(right, 1)

        self._refresh_methods_from_db()
        return tab

    def _refresh_methods_from_db(self):
        self.methods = list(get_methods())
        self.method_list.clear()
        for m in self.methods:
            self.method_list.addItem(m["name"])

    def _show_method_info(self, idx):
        if idx < 0 or idx >= len(self.methods):
            self.method_info.clear()
            return
        m = self.methods[idx]
        self.method_info.setHtml(f"<b>{m['name']}</b><br><br>{m['description']}")

    def _add_method(self):
        dlg = _TextDialog("Новый метод", parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name, desc = dlg.get_data()
            if name.strip():
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('INSERT INTO methods (name, description) VALUES (?, ?)', (name, desc))
                conn.commit()
                cur.close()
                conn.close()
                self._refresh_methods_from_db()

    def _edit_method(self):
        idx = self.method_list.currentRow()
        if idx < 0 or idx >= len(self.methods):
            return
        m = self.methods[idx]
        dlg = _TextDialog("Редактировать метод", m["name"], m["description"], parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name, desc = dlg.get_data()
            if name.strip():
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('UPDATE methods SET name=?, description=? WHERE id=?',
                            (name, desc, m["id"]))
                conn.commit()
                cur.close()
                conn.close()
                self._refresh_methods_from_db()

    def _delete_method(self):
        idx = self.method_list.currentRow()
        if idx < 0 or idx >= len(self.methods):
            return
        reply = QMessageBox.question(self, "Удалить метод",
                                     f'Удалить метод "{self.methods[idx]["name"]}"?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('DELETE FROM methods WHERE id=?', (self.methods[idx]["id"],))
            conn.commit()
            cur.close()
            conn.close()
            self._refresh_methods_from_db()
            self.method_info.clear()


# ── Диалоги ──

class _TextDialog(QDialog):
    def __init__(self, window_title, title="", description="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(window_title)
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.title_input = QLineEdit(title)
        self.desc_input  = QTextEdit(description)
        self.desc_input.setFixedHeight(80)

        form.addRow("Название:", self.title_input)
        form.addRow("Описание:", self.desc_input)
        layout.addLayout(form)

        btns = QHBoxLayout()
        ok     = QPushButton("Сохранить")
        cancel = QPushButton("Отмена")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        btns.addWidget(ok)
        btns.addWidget(cancel)
        layout.addLayout(btns)

    def get_data(self):
        return self.title_input.text().strip(), self.desc_input.toPlainText().strip()


class _UserDialog(QDialog):
    def __init__(self, username="", password="", role="researcher", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Пользователь")
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.username_input = QLineEdit(username)
        self.password_input = QLineEdit(password)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["Исследователь", "Администратор"])
        self.role_combo.setCurrentIndex(0 if role == "researcher" else 1)

        form.addRow("Логин:",  self.username_input)
        form.addRow("Пароль:", self.password_input)
        form.addRow("Роль:",   self.role_combo)
        layout.addLayout(form)

        btns = QHBoxLayout()
        ok     = QPushButton("Сохранить")
        cancel = QPushButton("Отмена")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        btns.addWidget(ok)
        btns.addWidget(cancel)
        layout.addLayout(btns)

    def get_data(self):
        role = "researcher" if self.role_combo.currentIndex() == 0 else "admin"
        return self.username_input.text().strip(), self.password_input.text(), role


# ── Окно исследователя ──

class ResearcherWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ОХП - Окно исследователя")
        self.setGeometry(100, 100, 1200, 700)

        main_layout = QHBoxLayout(self)

        # ЛЕВАЯ ПАНЕЛЬ
        left_panel = QWidget()
        left_panel.setMaximumWidth(310)
        left_layout = QVBoxLayout(left_panel)

        # Вариант задачи
        self.option_label = QLabel("Вариант задачи:")
        self.option_combo = QComboBox()
        self.tasks = list(get_tasks())
        for t in self.tasks:
            self.option_combo.addItem(t["title"])
        self.option_combo.setCurrentIndex(0)
        left_layout.addWidget(self.option_label)
        left_layout.addWidget(self.option_combo)

        # Вид экстремума
        extr_layout = QHBoxLayout()
        extr_label = QLabel("Вид экстремума:")
        self.radio_min = QRadioButton("min")
        self.radio_max = QRadioButton("max")
        self.radio_min.setChecked(True)
        self.extremum_group = QButtonGroup()
        self.extremum_group.addButton(self.radio_min)
        self.extremum_group.addButton(self.radio_max)
        extr_layout.addWidget(extr_label)
        extr_layout.addWidget(self.radio_min)
        extr_layout.addWidget(self.radio_max)
        extr_layout.addStretch()
        left_layout.addLayout(extr_layout)

        # Метод оптимизации
        method_select_group = QGroupBox("Метод оптимизации:")
        method_select_layout = QHBoxLayout()
        self.method_combo = QComboBox()
        self.methods = list(get_methods())
        for m in self.methods:
            self.method_combo.addItem(m["name"])
        self.method_combo.setCurrentIndex(0)
        method_select_layout.addWidget(self.method_combo)
        method_select_layout.addStretch()
        method_select_group.setLayout(method_select_layout)
        left_layout.addWidget(method_select_group)

        # Параметры математической модели
        params_group = QGroupBox("Параметры математической модели")
        params_layout = QFormLayout()

        self.spin_N = QSpinBox()
        self.spin_N.setRange(1, 10)
        self.spin_N.setValue(2)

        self.spin_G = QDoubleSpinBox()
        self.spin_G.setRange(0.1, 10)
        self.spin_G.setValue(1)
        self.spin_G.setSingleStep(0.1)

        self.spin_A = QDoubleSpinBox()
        self.spin_A.setRange(0.1, 10)
        self.spin_A.setValue(1)
        self.spin_A.setSingleStep(0.1)

        self.spin_alpha = QDoubleSpinBox()
        self.spin_alpha.setRange(0.1, 10)
        self.spin_alpha.setValue(1)
        self.spin_alpha.setSingleStep(0.1)

        self.spin_beta = QDoubleSpinBox()
        self.spin_beta.setRange(0.1, 10)
        self.spin_beta.setValue(1)
        self.spin_beta.setSingleStep(0.1)

        self.spin_mu = QDoubleSpinBox()
        self.spin_mu.setRange(0.1, 10)
        self.spin_mu.setValue(1)
        self.spin_mu.setSingleStep(0.1)

        self.spin_delta = QDoubleSpinBox()
        self.spin_delta.setRange(0.1, 10)
        self.spin_delta.setValue(1)
        self.spin_delta.setSingleStep(0.1)

        params_layout.addRow("Число теплообменников N (шт.):", self.spin_N)
        params_layout.addRow("Расход массы G (кг/ч):", self.spin_G)
        params_layout.addRow("Давление A (кПа):", self.spin_A)
        params_layout.addRow("Нормирующий множитель α:", self.spin_alpha)
        params_layout.addRow("Нормирующий множитель β:", self.spin_beta)
        params_layout.addRow("Нормирующий множитель μ:", self.spin_mu)
        params_layout.addRow("Нормирующий множитель Δ:", self.spin_delta)
        params_group.setLayout(params_layout)
        left_layout.addWidget(params_group)

        # Ограничения
        limits_group = QGroupBox("Ограничения")
        limits_layout = QFormLayout()

        self.spin_T1_min = QDoubleSpinBox()
        self.spin_T1_min.setRange(-100, 100)
        self.spin_T1_min.setValue(-18)

        self.spin_T1_max = QDoubleSpinBox()
        self.spin_T1_max.setRange(-100, 100)
        self.spin_T1_max.setValue(7)

        self.spin_T2_min = QDoubleSpinBox()
        self.spin_T2_min.setRange(-100, 100)
        self.spin_T2_min.setValue(-8)

        self.spin_T2_max = QDoubleSpinBox()
        self.spin_T2_max.setRange(-100, 100)
        self.spin_T2_max.setValue(8)

        limits_layout.addRow("T₁ min (°C):", self.spin_T1_min)
        limits_layout.addRow("T₁ max (°C):", self.spin_T1_max)
        limits_layout.addRow("T₂ min (°C):", self.spin_T2_min)
        limits_layout.addRow("T₂ max (°C):", self.spin_T2_max)
        limits_group.setLayout(limits_layout)
        left_layout.addWidget(limits_group)

        # Параметры метода
        method_params_group = QGroupBox("Параметры метода")
        method_params_layout = QFormLayout()

        self.spin_eps = QDoubleSpinBox()
        self.spin_eps.setDecimals(3)
        self.spin_eps.setRange(0.001, 1)
        self.spin_eps.setValue(0.01)

        self.spin_max_iter = QSpinBox()
        self.spin_max_iter.setRange(10, 1000)
        self.spin_max_iter.setValue(50)

        self.spin_grid_size = QSpinBox()
        self.spin_grid_size.setRange(5, 100)
        self.spin_grid_size.setValue(30)

        method_params_layout.addRow("Точность ε:", self.spin_eps)
        method_params_layout.addRow("Макс. итераций:", self.spin_max_iter)
        method_params_layout.addRow("Размер сетки:", self.spin_grid_size)
        method_params_group.setLayout(method_params_layout)
        left_layout.addWidget(method_params_group)

        # Кнопки расчёта
        btns_group = QGroupBox("Рассчитать")
        btns_layout = QHBoxLayout()
        self.calc_btn = QPushButton("Полностью")
        self.calc_btn.clicked.connect(self.calculate)
        self.step_btn = QPushButton("Пошагово")
        self.step_btn.clicked.connect(self.start_step_mode)
        self.step_history = []
        self.current_step = 0
        btns_layout.addWidget(self.calc_btn)
        btns_layout.addWidget(self.step_btn)
        btns_group.setLayout(btns_layout)
        left_layout.addWidget(btns_group)

        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)
        left_layout.addWidget(self.result_label)
        # Навигация по шагам
        self.step_nav_widget = QWidget()
        step_nav_layout = QHBoxLayout(self.step_nav_widget)

        self.prev_btn = QPushButton("← Назад")
        self.next_btn = QPushButton("Вперёд →")

        self.prev_btn.clicked.connect(self.prev_step)
        self.next_btn.clicked.connect(self.next_step)

        step_nav_layout.addWidget(self.prev_btn)
        step_nav_layout.addWidget(self.next_btn)

        self.step_nav_widget.hide()

        left_layout.addWidget(self.step_nav_widget)

        # Информация о шаге
        self.step_info = QTextEdit()
        self.step_info.setReadOnly(True)
        self.step_info.setMaximumHeight(220)
        self.step_info.hide()

        left_layout.addWidget(self.step_info)

        left_layout.addStretch()

        # ПРАВАЯ ПАНЕЛЬ
        right_panel = QTabWidget()

        self.tab_2d = QWidget()
        tab_2d_layout = QVBoxLayout(self.tab_2d)
        self.figure_2d = Figure(facecolor='white')
        self.canvas_2d = FigureCanvas(self.figure_2d)
        tab_2d_layout.addWidget(self.canvas_2d)
        right_panel.addTab(self.tab_2d, "📊 2D - Линии уровня")

        self.tab_3d = QWidget()
        tab_3d_layout = QVBoxLayout(self.tab_3d)
        self.figure_3d = Figure(facecolor='white')
        self.canvas_3d = FigureCanvas(self.figure_3d)
        tab_3d_layout.addWidget(self.canvas_3d)
        right_panel.addTab(self.tab_3d, "🌐 3D - Поверхность отклика")

        self.tab_table = QWidget()
        tab_table_layout = QVBoxLayout(self.tab_table)
        table_label = QLabel("📋 Значения целевой функции F(T₁, T₂)")
        table_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 5px;")
        tab_table_layout.addWidget(table_label)
        self.result_table = QTableWidget()
        self.result_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
                font-size: 11px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 5px;
                font-weight: bold;
            }
        """)
        tab_table_layout.addWidget(self.result_table)
        right_panel.addTab(self.tab_table, "📋 Таблица значений")

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 3)

        self.init_empty_table()

    @staticmethod
    def _generate_initial_complex(bounds, constraint, n, N, max_attempts=10000):
        points = []
        attempts = 0
        while len(points) < N and attempts < max_attempts:
            # Генерация в гиперкубе границ (ограничения 1-го рода)
            T1 = random.uniform(bounds[0][0], bounds[0][1])
            T2 = random.uniform(bounds[1][0], bounds[1][1])
            p = [T1, T2]
            
            # Проверка ограничений 2-го рода
            if constraint(p[0], p[1]):
                points.append(p)
            else:
                # Если уже есть хотя бы одна допустимая точка, смещаем недопустимую к центру
                if len(points) >= 1:
                    # Центр уже накопленных точек
                    center = [sum(pt[i] for pt in points) / len(points) for i in range(2)]
                    # Смещение на половину расстояния
                    p = [0.5 * (p[i] + center[i]) for i in range(2)]
                    # Повторная проверка; если всё равно недопустима – отбрасываем, генерируем новую
                    if constraint(p[0], p[1]):
                        points.append(p)
            attempts += 1
        
        if len(points) < N:
            raise ValueError(f"Не удалось построить комплекс из {N} точек после {max_attempts} попыток")
        return points

    def box_method(self, func, bounds, constraint, eps=0.1, max_iter=50):
        n = 2
        N = 2 * n
        # Формирование комплекса с коррекцией
        points = self._generate_initial_complex(bounds, constraint, n, N)
        
        for _ in range(max_iter):
            values = [func(p[0], p[1]) for p in points]
            worst_idx = int(np.argmax(values))
            best_idx  = int(np.argmin(values))
            
            # Центр без худшей вершины
            center = [
                sum(points[j][i] for j in range(N) if j != worst_idx) / (N - 1)
                for i in range(n)
            ]
            
            # Критерий останова
            B = (abs(center[0] - points[worst_idx][0]) + abs(center[0] - points[best_idx][0]) +
                abs(center[1] - points[worst_idx][1]) + abs(center[1] - points[best_idx][1])) / (2 * n)
            if B < eps:
                break
            
            # Отражение
            new = [2.3 * center[i] - 1.3 * points[worst_idx][i] for i in range(n)]
            
            # Коррекция по границам (1-го рода)
            new[0] = max(bounds[0][0], min(bounds[0][1], new[0]))
            new[1] = max(bounds[1][0], min(bounds[1][1], new[1]))
            
            # Коррекция по общим ограничениям (2-го рода)
            for _ in range(100):
                if constraint(new[0], new[1]):
                    break
                new = [0.5 * (new[i] + center[i]) for i in range(n)]
            
            # проверка улучшения и смещение к лучшей вершине 
            F_new = func(new[0], new[1])
            F_worst = values[worst_idx]
            for _ in range(100):
                if F_new <= F_worst:   # для минимизации
                    break
                # смещаем к лучшей вершине
                new = [0.5 * (new[i] + points[best_idx][i]) for i in range(n)]
                # после смещения проверяем ограничения 2-го рода
                for __ in range(20):
                    if constraint(new[0], new[1]):
                        break
                    # если нарушено – смещаем к центру (без худшей)
                    new = [0.5 * (new[i] + center[i]) for i in range(n)]
                F_new = func(new[0], new[1])
            # ----------------------------------------------------------
            
            points[worst_idx] = new
        
        final_vals = [func(p[0], p[1]) for p in points]
        best_idx = int(np.argmin(final_vals))
        return points[best_idx][0], points[best_idx][1], final_vals[best_idx]
    
    def coordinate_search(self, func, bounds, constraint, eps=0.1, max_iter=100):
        # Начальная точка: центр гиперкуба
        T1 = (bounds[0][0] + bounds[0][1]) / 2
        T2 = (bounds[1][0] + bounds[1][1]) / 2

        # Принудительная корректиркция точкт, чтобы она удовлетворяла ограничению T2 - T1 >= 1

        if not constraint(T1, T2):
            # поднятие T2
            needed_T2 = T1 + 1
            if needed_T2 <= bounds[1][1]:
                T2 = needed_T2
            else:
                # Если не хватает места сверху, опускается T1
                T1 = bounds[1][1] - 1
                T2 = bounds[1][1]
                if T1 < bounds[0][0]:
                    T1 = bounds[0][0]
                    T2 = T1 + 1
                    if T2 > bounds[1][1]:
                        raise ValueError("Нет допустимой точки в заданных границах и ограничениях")

        step = 1.0
        best_value = func(T1, T2)

        for _ in range(max_iter):
            improved = False
            candidates = [
                (T1 + step, T2),
                (T1 - step, T2),
                (T1, T2 + step),
                (T1, T2 - step)
            ]
            for new_T1, new_T2 in candidates:
                if not constraint(new_T1, new_T2):
                    continue
                if not (bounds[0][0] <= new_T1 <= bounds[0][1]):
                    continue
                if not (bounds[1][0] <= new_T2 <= bounds[1][1]):
                    continue
                value = func(new_T1, new_T2)
                if value < best_value:
                    T1, T2 = new_T1, new_T2
                    best_value = value
                    improved = True
            if not improved:
                step /= 2
            if step < eps:
                break

        return T1, T2, best_value
    
    def coordinate_search_steps(self, func, bounds, constraint,
                                eps=0.1, max_iter=100):

        T1 = (bounds[0][0] + bounds[0][1]) / 2
        T2 = (bounds[1][0] + bounds[1][1]) / 2

        while not constraint(T1, T2):
            T2 += 1

        step_size = 1.0

        best_value = func(T1, T2)

        history = []

        for iteration in range(max_iter):

            T1_prev = T1
            T2_prev = T2

            improved = False

            candidates = [
                (T1 + step_size, T2),
                (T1 - step_size, T2),
                (T1, T2 + step_size),
                (T1, T2 - step_size)
            ]

            for new_T1, new_T2 in candidates:

                if not constraint(new_T1, new_T2):
                    continue

                if not (bounds[0][0] <= new_T1 <= bounds[0][1]):
                    continue

                if not (bounds[1][0] <= new_T2 <= bounds[1][1]):
                    continue

                value = func(new_T1, new_T2)

                if value < best_value:
                    T1 = new_T1
                    T2 = new_T2
                    best_value = value
                    improved = True

            history.append({
                "step": iteration,
                "T1": T1,
                "T2": T2,
                "F": best_value,
                "delta": step_size,
                "T1_prev": T1_prev,
                "T2_prev": T2_prev
            })

            if not improved:
                step_size /= 2

            if step_size < eps:
                break

        return history

    def box_method_steps(self, func, bounds, constraint, eps=0.1, max_iter=50, initial_points=None):
        n = 2
        N = 2 * n
        
        if initial_points is not None:
            points = [p[:] for p in initial_points]
        else:
            points = self._generate_initial_complex(bounds, constraint, n, N)
        
        history = []
        
        for step in range(max_iter):
            values = [func(p[0], p[1]) for p in points]
            worst_idx = int(np.argmax(values))
            best_idx  = int(np.argmin(values))
            
            center = [
                sum(points[j][i] for j in range(N) if j != worst_idx) / (N - 1)
                for i in range(n)
            ]
            
            B = (abs(center[0] - points[worst_idx][0]) + abs(center[0] - points[best_idx][0]) +
                abs(center[1] - points[worst_idx][1]) + abs(center[1] - points[best_idx][1])) / (2 * n)
            
            history.append({
                "step": step,
                "points": [p[:] for p in points],
                "values": values[:],
                "best_idx": best_idx,
                "worst_idx": worst_idx,
                "center": center[:],
                "B": B
            })
            
            if B < eps:
                break
            
            # Отражение
            new = [2.3 * center[i] - 1.3 * points[worst_idx][i] for i in range(n)]
            
            # Коррекция по границам
            new[0] = max(bounds[0][0], min(bounds[0][1], new[0]))
            new[1] = max(bounds[1][0], min(bounds[1][1], new[1]))
            
            # Коррекция по ограничениям 2-го рода
            for _ in range(100):
                if constraint(new[0], new[1]):
                    break
                new = [0.5 * (new[i] + center[i]) for i in range(n)]
            
            # ДОБАВЛЕН ШАГ 9 
            F_new = func(new[0], new[1])
            F_worst = values[worst_idx]
            for _ in range(100):
                if F_new <= F_worst:
                    break
                # смещение к лучшей вершине
                new = [0.5 * (new[i] + points[best_idx][i]) for i in range(n)]
                # после смещения проверяем ограничения 2-го рода
                for __ in range(20):
                    if constraint(new[0], new[1]):
                        break
                    new = [0.5 * (new[i] + center[i]) for i in range(n)]
                F_new = func(new[0], new[1])
            # ================================================
            
            points[worst_idx] = new
        
        return history
    
    def calculate(self):
        method_idx = self.method_combo.currentIndex()
        if method_idx < 0 or method_idx >= len(self.methods):
            return
        
        method = self.methods[method_idx]

        task_idx = self.option_combo.currentIndex()
        if task_idx < 0 or task_idx >= len(self.tasks):
            return
        task = self.tasks[task_idx]
        if 'вариант №17' not in task['title'].lower():
            self.result_label.setText("⚠️ Реализован только вариант 17.")
            return

        minimize = self.radio_min.isChecked()

        N         = self.spin_N.value()
        G         = self.spin_G.value()
        A         = self.spin_A.value()
        alpha     = self.spin_alpha.value()
        beta      = self.spin_beta.value()
        mu        = self.spin_mu.value()
        delta     = self.spin_delta.value()
        T1_min    = self.spin_T1_min.value()
        T1_max    = self.spin_T1_max.value()
        T2_min    = self.spin_T2_min.value()
        T2_max    = self.spin_T2_max.value()
        eps       = self.spin_eps.value()
        max_iter  = self.spin_max_iter.value()
        grid_size = self.spin_grid_size.value()

        def F(T1, T2):
            try:
                S  = (T2 - beta * A) ** N
                S += mu * (np.exp(T1 + T2) ** N)
                S += delta * (T2 - T1)
                S *= alpha * G
                val = 1000.0 * S
                if np.isnan(val) or np.isinf(val) or val < 0:
                    return 1e15
                return val
            except:
                return 1e15

        def F_opt(T1, T2):
            val = F(T1, T2)
            return val if minimize else -val

        bounds     = [(T1_min, T1_max), (T2_min, T2_max)]
        constraint = lambda T1, T2: (T2 - T1) >= 1.0

        try:

            if 'метод бокса' in method['name'].lower():
                T1_opt, T2_opt, _ = self.box_method(
                    F_opt,
                    bounds,
                    constraint,
                    eps,
                    max_iter
                )

            elif 'метод координатного спуска' in method['name'].lower():
                T1_opt, T2_opt, _ = self.coordinate_search(
                    F_opt,
                    bounds,
                    constraint,
                    eps,
                    max_iter
                )

            else:
                self.result_label.setText("⚠️ Метод не реализован.")
                return

        except ValueError as e:

            self.result_label.setText(
                f"<span style='color:red;'>Ошибка: {str(e)}</span>"
            )
            return

        F_display  = F(T1_opt, T2_opt)
        extr_label = "min" if minimize else "max"

        self.result_label.setText(
            f"<b>Оптимум ({extr_label}) найден:</b><br>"
            f"T₁ = {T1_opt:.3f} °C<br>"
            f"T₂ = {T2_opt:.3f} °C<br>"
            f"<span style='color: #2ecc71; font-size: 16px;'>F = {F_display:.2f} у.е.</span>"
        )

        # Таблица
        T1_vals = np.linspace(T1_min, T1_max, grid_size)
        T2_vals = np.linspace(T2_min, T2_max, grid_size)
        self.result_table.clearContents()
        self.result_table.setRowCount(grid_size)
        self.result_table.setColumnCount(grid_size)
        self.result_table.setHorizontalHeaderLabels([f"{v:.1f}" for v in T2_vals])
        self.result_table.setVerticalHeaderLabels([f"{v:.1f}" for v in T1_vals])

        for i, t1 in enumerate(T1_vals):
            for j, t2 in enumerate(T2_vals):
                if constraint(t1, t2):
                    val = F(t1, t2)
                    if val > 1e9 or np.isnan(val):
                        item = QTableWidgetItem("∞")
                        item.setForeground(Qt.GlobalColor.red)
                    else:
                        item = QTableWidgetItem(f"{val:.1f}")
                        item.setForeground(Qt.GlobalColor.darkGreen)
                else:
                    item = QTableWidgetItem("❌")
                    item.setForeground(Qt.GlobalColor.red)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.result_table.setItem(i, j, item)

        self.result_table.resizeColumnsToContents()

        # 3Dа
        T1g, T2g = np.meshgrid(T1_vals, T2_vals)
        Zg = np.zeros_like(T1g)
        for i in range(grid_size):
            for j in range(grid_size):
                Zg[i, j] = F(T1g[i, j], T2g[i, j]) if constraint(T1g[i, j], T2g[i, j]) else np.nan

        self.figure_3d.clear()
        ax3 = self.figure_3d.add_subplot(111, projection='3d')
        surf = ax3.plot_surface(T1g, T2g, Zg, cmap='viridis', alpha=0.8, edgecolor='none')
        ax3.scatter(T1_opt, T2_opt, F_display, color='red', s=80, label='Оптимум')
        ax3.set_xlabel("T₁ (°C)")
        ax3.set_ylabel("T₂ (°C)")
        ax3.set_zlabel("F (у.е.)")
        ax3.set_title("Поверхность отклика")
        ax3.legend()
        self.figure_3d.colorbar(surf, ax=ax3, shrink=0.5)
        self.canvas_3d.draw()

        # 2D
        self.figure_2d.clear()
        ax2 = self.figure_2d.add_subplot(111)
        contour = ax2.contourf(T1g, T2g, Zg, levels=20, cmap='coolwarm')
        ax2.contour(T1g, T2g, Zg, levels=10, colors='black', linewidths=0.5, alpha=0.3)
        ax2.scatter(T1_opt, T2_opt, color='red', s=100, marker='*', label='Оптимум')
        ax2.set_xlabel("T₁ (°C)")
        ax2.set_ylabel("T₂ (°C)")
        ax2.set_title("Линии равного уровня F")
        ax2.legend()
        self.figure_2d.colorbar(contour, ax=ax2)
        self.canvas_2d.draw()

    def start_step_mode(self):
        method_idx = self.method_combo.currentIndex()
        if method_idx < 0 or method_idx >= len(self.methods):
            return

        method = self.methods[method_idx]
        is_box   = 'метод бокса' in method['name'].lower()
        is_coord = 'координатного' in method['name'].lower()

        if not is_box and not is_coord:
            self.result_label.setText("⚠️ Пошаговый режим реализован только для метода Бокса и координатного спуска.")
            return

        minimize = self.radio_min.isChecked()
        T1_min   = self.spin_T1_min.value()
        T1_max   = self.spin_T1_max.value()
        T2_min   = self.spin_T2_min.value()
        T2_max   = self.spin_T2_max.value()
        eps      = self.spin_eps.value()
        max_iter = self.spin_max_iter.value()
        N        = self.spin_N.value()
        G        = self.spin_G.value()
        A        = self.spin_A.value()
        alpha    = self.spin_alpha.value()
        beta     = self.spin_beta.value()
        mu       = self.spin_mu.value()
        delta    = self.spin_delta.value()

        def F(T1, T2):
            try:
                S  = (T2 - beta * A) ** N
                S += mu * (np.exp(T1 + T2) ** N)
                S += delta * (T2 - T1)
                S *= alpha * G
                val = 1000.0 * S
                if np.isnan(val) or np.isinf(val) or val < 0:
                    return 1e15
                return val
            except:
                return 1e15

        def F_opt(T1, T2):
            val = F(T1, T2)
            return val if minimize else -val

        bounds     = [(T1_min, T1_max), (T2_min, T2_max)]
        constraint = lambda T1, T2: (T2 - T1) >= 1

        if is_box:
            self.step_method_type = 'box'
            self.step_history = self.box_method_steps(F_opt, bounds, constraint, eps, max_iter)
        else:
            self.step_method_type = 'coord'
            self.step_history = self.coordinate_search_steps(F_opt, bounds, constraint, eps, max_iter)

        if not self.step_history:
            return

        self.current_step = 0
        self.step_nav_widget.show()
        self.step_info.show()
        self.show_step()
    
    def show_box_step(self, step):

        self.result_label.setText(
            f'Шаг {step["step"] + 1} | '
            f'B = {step["B"]:.4f}'
        )

        info = f'<b>Шаг {step["step"] + 1}</b><br>'
        info += f'Критерий B = {step["B"]:.4f}<br><br>'

        info += 'Вершины комплекса:<br>'

        for i, (p, v) in enumerate(zip(step["points"], step["values"])):

            mark = ""

            if i == step["best_idx"]:
                mark += " ← лучшая"

            if i == step["worst_idx"]:
                mark += " ← худшая"

            info += (
                f'{i+1}: '
                f'({p[0]:.3f}, {p[1]:.3f}) '
                f'F={v:.3f}'
                f'{mark}<br>'
            )

        self.step_info.setHtml(info)

        self.figure_2d.clear()

        ax = self.figure_2d.add_subplot(111)

        pts = np.array(step["points"])

        ax.scatter(
            pts[:,0],
            pts[:,1],
            s=120
        )

        ax.scatter(
            pts[step["best_idx"],0],
            pts[step["best_idx"],1],
            s=220,
            c='green'
        )

        ax.scatter(
            pts[step["worst_idx"],0],
            pts[step["worst_idx"],1],
            s=220,
            c='red'
        )

        ax.scatter(
            step["center"][0],
            step["center"][1],
            s=250,
            marker='*',
            c='orange'
        )

        ax.set_title(
            f'Метод Бокса — шаг {step["step"] + 1}'
        )

        ax.grid(True)

        self.canvas_2d.draw()

    def show_coordinate_step(self, step):

        self.result_label.setText(
            f'Шаг {step["step"] + 1} | '
            f'F = {step["F"]:.4f}'
        )

        info = f'<b>Шаг {step["step"] + 1}</b><br><br>'

        info += f'T1 = {step["T1"]:.4f}<br>'
        info += f'T2 = {step["T2"]:.4f}<br>'
        info += f'δ = {step["delta"]:.4f}<br>'
        info += f'F = {step["F"]:.4f}<br>'

        self.step_info.setHtml(info)

        self.figure_2d.clear()

        ax = self.figure_2d.add_subplot(111)

        trajectory_x = []
        trajectory_y = []

        for s in self.step_history[:self.current_step + 1]:
            trajectory_x.append(s["T1"])
            trajectory_y.append(s["T2"])

        ax.plot(
            trajectory_x,
            trajectory_y,
            '-o',
            linewidth=2
        )

        ax.scatter(
            step["T1"],
            step["T2"],
            s=200,
            c='red'
        )

        ax.set_title(
            f'Координатный спуск — шаг {step["step"] + 1}'
        )

        ax.set_xlabel("T1")
        ax.set_ylabel("T2")

        ax.grid(True)

        self.canvas_2d.draw()
    
    def show_step(self):

        if not self.step_history:
            return

        step = self.step_history[self.current_step]

        method_name = self.method_combo.currentText().lower()

        if "бокса" in method_name:
            self.show_box_step(step)
        else:
            self.show_coordinate_step(step)
    
    def next_step(self):
        if self.current_step < len(self.step_history) - 1:
            self.current_step += 1
            self.show_step()
    
    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.show_step()

    def init_empty_table(self):
        T1_values = [round(x, 1) for x in np.linspace(-18, 7, 10)]
        T2_values = [round(x, 1) for x in np.linspace(-8, 8, 10)]

        self.result_table.setRowCount(len(T1_values))
        self.result_table.setColumnCount(len(T2_values))
        self.result_table.setHorizontalHeaderLabels([f"{x:.1f}" for x in T2_values])
        self.result_table.setVerticalHeaderLabels([f"{x:.1f}" for x in T1_values])

        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for i in range(len(T1_values)):
            for j in range(len(T2_values)):
                item = QTableWidgetItem("—")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.result_table.setItem(i, j, item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Login()
    window.show()
    sys.exit(app.exec())