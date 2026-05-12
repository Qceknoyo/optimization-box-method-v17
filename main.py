import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QDoubleSpinBox, QFormLayout, QGroupBox, QSpinBox, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QHBoxLayout, QButtonGroup, QLineEdit, QRadioButton, QTabWidget, QTableWidgetItem, QHeaderView, QTableWidget, QComboBox)
from PyQt6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ОХП - Вход")
        # Настройка геометрии окна (1/3 экрана)
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry() # доступная область (без панели задач)
        sw = screen_geometry.width()
        sh = screen_geometry.height()
        
        width = int(sw / 4)
        height = int(sh / 4)
        x = int((sw - width) / 2)
        y = int((sh - height) / 2)
        self.setGeometry(x, y, width, height)

        # Компоновка (Layout)
        self.layout = QVBoxLayout()

        # Виджеты

        self.combo = QComboBox()
        self.combo.addItems(["Администратор", "Исследователь"])

        self.login_label = QLabel("Введите логин:")
        self.login_input = QLineEdit()

        self.password_label = QLabel("Введите пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.button_enter = QPushButton("Вход")
        
        self.result_label = QLabel("") 
        
        # Логика (Сигналы и Слоты)
        self.button_enter.clicked.connect(self.on_click)

        # Добавление на экран
        self.layout.addWidget(self.combo)
        self.layout.addWidget(self.login_label)
        self.layout.addWidget(self.login_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.button_enter)
        self.layout.addWidget(self.result_label)
        

        self.setLayout(self.layout)

    def on_click(self):
        text = self.login_input.text()
        if text:
            self.result_label.setText(f"Привет, {text}!")
        else:
            self.result_label.setText("Вы не ввели логин!")

class ResearcherWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ОХП - Окно исследователя")
        self.setGeometry(100, 100, 1200, 700)
        
        # Горизонтальный layout (левая панель + правая с вкладками)
        main_layout = QHBoxLayout(self)
        
        # ЛЕВАЯ ПАНЕЛЬ 
        left_panel = QWidget()
        left_panel.setMaximumWidth(300)
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("Поля ввода"))
        left_layout.addStretch()

        #вариант задачи
        self.option_label = QLabel("Вариант задачи:")
        self.option_combo = QComboBox()
        self.option_combo.addItems(["Вариант 17"]) #, "Вариант 67", "Вариант 54"
        self.option_combo.setCurrentIndex(0)
        left_layout.addWidget(self.option_label)
        left_layout.addWidget(self.option_combo)


        # Вид экстремума
        extr_layout = QHBoxLayout()  
        extr_label = QLabel('Вид экстремума:')
        self.radio_min = QRadioButton('min')
        # self.radio_max = QRadioButton('max')
        self.radio_min.setChecked(True)
        self.extremum_group = QButtonGroup()
        self.extremum_group.addButton(self.radio_min)
        # self.extremum_group.addButton(self.radio_max)
        extr_layout.addWidget(extr_label)
        extr_layout.addWidget(self.radio_min)
        # extr_layout.addWidget(self.radio_max)
        extr_layout.addStretch()
        left_layout.addLayout(extr_layout)

        method_layout = QHBoxLayout()

        #выбор метода оптимизации
        method_group = QGroupBox("Метод оптимизации:")
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Метод Бокса"]) #можно дополнить , "Метод сканирования", "Генетический алгоритм"
        self.method_combo.setCurrentIndex(0)
        method_layout.addWidget(self.method_combo)
        method_layout.addStretch()
        method_group.setLayout(method_layout)
        left_layout.addWidget(method_group)

        # ПАРАМЕТРЫ МАТЕМАТИЧЕСКОЙ МОДЕЛИ 
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


        # ОГРАНИЧЕНИЯ 
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


        # ПАРАМЕТРЫ МЕТОДА 
        method_group = QGroupBox("Параметры метода")
        method_layout = QFormLayout()

        self.spin_eps = QDoubleSpinBox()
        self.spin_eps.setDecimals(3)
        self.spin_eps.setRange(0.001, 1)
        self.spin_eps.setValue(0.1)

        self.spin_max_iter = QSpinBox()
        self.spin_max_iter.setRange(10, 1000)
        self.spin_max_iter.setValue(50)

        method_layout.addRow("Точность ε:", self.spin_eps)
        method_layout.addRow("Макс. итераций:", self.spin_max_iter)
        self.spin_grid_size = QSpinBox()
        self.spin_grid_size.setRange(5, 100)
        self.spin_grid_size.setValue(30)
        method_layout.addRow("Размер сетки:", self.spin_grid_size)
        
        method_group.setLayout(method_layout)
        left_layout.addWidget(method_group)

        #КНОПКИ РАСЧЁТА
        btns_group = QGroupBox("Расчитать")
        btns_layout = QHBoxLayout()
        self.calc_btn = QPushButton('Полностью')
        self.calc_btn.clicked.connect(self.calculate)
        self.step_btn = QPushButton('Пошагово')
        btns_layout.addWidget(self.calc_btn)
        btns_layout.addWidget(self.step_btn)
        btns_group.setLayout(btns_layout)
        left_layout.addWidget(btns_group)

        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)
        left_layout.addWidget(self.result_label)

        # ПРАВАЯ ПАНЕЛЬ 
        right_panel = QTabWidget()
        
        #Вкладка 1: 2D график 
        self.tab_2d = QWidget()
        tab_2d_layout = QVBoxLayout(self.tab_2d)
        self.figure_2d = Figure(facecolor='white')
        self.canvas_2d = FigureCanvas(self.figure_2d)
        tab_2d_layout.addWidget(self.canvas_2d)
        right_panel.addTab(self.tab_2d, "📊 2D - Линии уровня")
        
        # Вкладка 2: 3D график
        self.tab_3d = QWidget()
        tab_3d_layout = QVBoxLayout(self.tab_3d)
        self.figure_3d = Figure(facecolor='white')
        self.canvas_3d = FigureCanvas(self.figure_3d)
        tab_3d_layout.addWidget(self.canvas_3d)
        right_panel.addTab(self.tab_3d, "🌐 3D - Поверхность отклика")
        
        # Вкладка 3: Таблица результатов
        self.tab_table = QWidget()
        tab_table_layout = QVBoxLayout(self.tab_table)
        
        # Заголовок таблицы
        table_label = QLabel("📋 Значения целевой функции F(T₁, T₂)")
        table_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 5px;")
        tab_table_layout.addWidget(table_label)
        
        # Создание таблицы
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
        
        # Собираем всё
        main_layout.addWidget(left_panel, 1)   # l панель 1 часть
        main_layout.addWidget(right_panel, 3)  # r панель 3 части
        
        # Инициализируем пустую таблицу
        self.init_empty_table()
    
    

    def box_method(self, func, bounds, constraint, eps=0.1, max_iter=50):
        import random
        n = 2
        N = 2 * n
        points = []
        max_attempts = 10000
        attempts = 0
        while len(points) < N and attempts < max_attempts:
            T1 = random.uniform(bounds[0][0], bounds[0][1])
            T2 = random.uniform(bounds[1][0], bounds[1][1])
            if constraint(T1, T2):
                points.append([T1, T2])
            attempts += 1
        if len(points) < N:
            raise ValueError(f"Не удалось найти {N} допустимых точек. Проверьте ограничения.")
        for _ in range(max_iter):
            values = [func(p[0], p[1]) for p in points]
            worst = np.argmax(values)
            best = np.argmin(values)
            center = [
                sum(points[j][i] for j in range(N) if j != worst) / (N - 1)
                for i in range(n)
            ]
            B = (abs(center[0] - points[worst][0]) + abs(center[0] - points[best][0]) +
                abs(center[1] - points[worst][1]) + abs(center[1] - points[best][1])) / (2*n)
            if B < eps:
                break
            new = [2.3 * center[i] - 1.3 * points[worst][i] for i in range(n)]
            new[0] = max(bounds[0][0], min(bounds[0][1], new[0]))
            new[1] = max(bounds[1][0], min(bounds[1][1], new[1]))
            if not constraint(new[0], new[1]):
                new = [0.5 * (new[i] + center[i]) for i in range(n)]
            points[worst] = new
        final_vals = [func(p[0], p[1]) for p in points]
        best_idx = np.argmin(final_vals)
        return points[best_idx][0], points[best_idx][1], final_vals[best_idx]

    def calculate(self):
        if self.method_combo.currentText() != "Метод Бокса":
            self.result_label.setText("⚠️ Реализован только метод Бокса.")
            return
        if self.option_combo.currentText() != "Вариант 17":
            self.result_label.setText("⚠️ Реализован только вариант 17.")
            return

        N = self.spin_N.value()
        G = self.spin_G.value()
        A = self.spin_A.value()
        alpha = self.spin_alpha.value()
        beta = self.spin_beta.value()
        mu = self.spin_mu.value()
        delta = self.spin_delta.value()

        T1_min = self.spin_T1_min.value()
        T1_max = self.spin_T1_max.value()
        T2_min = self.spin_T2_min.value()
        T2_max = self.spin_T2_max.value()
        eps = self.spin_eps.value()
        max_iter = self.spin_max_iter.value()
        grid_size = self.spin_grid_size.value()

        def F(T1, T2):
            try:
                S = (T2 - beta * A) ** N
                S += mu * (np.exp(T1 + T2) ** N)
                S += delta * (T2 - T1)
                S *= alpha * G
                val = 1000.0 * S
                if np.isnan(val) or np.isinf(val) or val < 0:
                    return 1e15
                return val
            except:
                return 1e15

        bounds = [(T1_min, T1_max), (T2_min, T2_max)]
        constraint = lambda T1, T2: (T2 - T1) >= 1.0

        try:
            T1_opt, T2_opt, F_opt = self.box_method(F, bounds, constraint, eps, max_iter)
        except ValueError as e:
            self.result_label.setText(f"<span style='color:red;'>Ошибка: {str(e)}</span>")
            return

        self.result_label.setText(
            f"<b>Оптимум найден:</b><br>"
            f"T₁ = {T1_opt:.3f} °C<br>"
            f"T₂ = {T2_opt:.3f} °C<br>"
            f"<span style='color: #2ecc71; font-size: 16px;'>F = {F_opt:.2f} у.е.</span>"
        )


        self.result_table.clearContents()
        self.result_table.setRowCount(0)
        self.result_table.setColumnCount(0)


        T1_vals = np.linspace(T1_min, T1_max, grid_size)
        T2_vals = np.linspace(T2_min, T2_max, grid_size)
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
        self.result_table.viewport().update()

        # 3D
        self.figure_3d.clear()
        ax3 = self.figure_3d.add_subplot(111, projection='3d')
        T1g, T2g = np.meshgrid(T1_vals, T2_vals)
        Zg = np.zeros_like(T1g)
        for i in range(grid_size):
            for j in range(grid_size):
                if constraint(T1g[i, j], T2g[i, j]):
                    Zg[i, j] = F(T1g[i, j], T2g[i, j])
                else:
                    Zg[i, j] = np.nan
        surf = ax3.plot_surface(T1g, T2g, Zg, cmap='viridis', alpha=0.8, edgecolor='none')
        ax3.scatter(T1_opt, T2_opt, F_opt, color='red', s=80, label='Оптимум')
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
    
    def init_empty_table(self):
        """Создаёт пустую таблицу с заголовками"""
        # Диапазоны T₁ и T₂
        T1_values = np.linspace(-18, 7, 10)  # 10 значений от -18 до 7
        T2_values = np.linspace(-8, 8, 10)   # 10 значений от -8 до 8
        
        # Округляем для красоты
        T1_values = [round(x, 1) for x in T1_values]
        T2_values = [round(x, 1) for x in T2_values]
        
        # Настраиваем таблицу
        self.result_table.setRowCount(len(T1_values))
        self.result_table.setColumnCount(len(T2_values))
        
        # Горизонтальные заголовки (T₂)
        self.result_table.setHorizontalHeaderLabels([f"{x:.1f}" for x in T2_values])
        
        # Вертикальные заголовки (T₁)
        self.result_table.setVerticalHeaderLabels([f"{x:.1f}" for x in T1_values])
        
        # Растягиваем столбцы
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Заполняем заглушками
        for i in range(len(T1_values)):
            for j in range(len(T2_values)):
                item = QTableWidgetItem("—")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.result_table.setItem(i, j, item)
    
    def fill_table(self, func, resolution=10):
        """
        Заполняет таблицу значениями функции func(T1, T2)
        func — функция, которая принимает T1, T2 и возвращает число
        """
        T1_values = np.linspace(-18, 7, resolution)
        T2_values = np.linspace(-8, 8, resolution)
        
        # Округляем для заголовков
        T1_rounded = [round(x, 1) for x in T1_values]
        T2_rounded = [round(x, 1) for x in T2_values]
        
        # Настраиваем размер таблицы
        self.result_table.setRowCount(len(T1_values))
        self.result_table.setColumnCount(len(T2_values))
        
        # Устанавливаем заголовки
        self.result_table.setHorizontalHeaderLabels([f"{x:.1f}" for x in T2_rounded])
        self.result_table.setVerticalHeaderLabels([f"{x:.1f}" for x in T1_rounded])
        
        # Заполняем ячейки
        for i, T1 in enumerate(T1_values):
            for j, T2 in enumerate(T2_values):
                # Проверяем ограничение T₂ - T₁ ≥ 1
                if T2 - T1 >= 1:
                    value = func(T1, T2)
                    if np.isnan(value) or np.isinf(value) or value > 1e9:
                        item = QTableWidgetItem("∞")
                        item.setForeground(Qt.GlobalColor.red)
                    else:
                        item = QTableWidgetItem(f"{value:.2f}")
                        item.setForeground(Qt.GlobalColor.darkGreen)
                else:
                    item = QTableWidgetItem("❌")
                    item.setForeground(Qt.GlobalColor.red)
                
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.result_table.setItem(i, j, item)
        
        # Растягиваем столбцы
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ResearcherWindow()
    window.show()
    sys.exit(app.exec())