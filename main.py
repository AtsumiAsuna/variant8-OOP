# Выполнила студентка 43ИС-21 Юлдашева Валерия.
# Вариант 8. Ежедневник
# В базе данных хранятся сведения о запланированных событиях (делах, встречах и звонках) и их выполнении.
# Таблицы: Виды событий (Код вида события, название вида), События (Код события, код вида события, название события, время начала,
# продолжительность, отметка о выполнении). Требуется:
# определить относительную долю загрузки рабочего дня по приоритетам;
# построить список невыполненных дел в порядке срока давности.

import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QDateTimeEdit,
                             QComboBox, QMessageBox)
from PyQt6.QtCore import QDateTime
import MySQLdb
from openpyxl import Workbook

connect = MySQLdb.connect('localhost', 'root', '', 'variant8')
cursor = connect.cursor()

class Planner(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ежедневние")
        self.setGeometry(100, 100, 300, 300)
        self.layout = QVBoxLayout()

        #поле для ввода названия события
        self.event_name_input = QLineEdit(self)
        self.event_name_input.setPlaceholderText('Название события')
        self.layout.addWidget(self.event_name_input)

        #выпадающий список для выбора типа события
        self.event_type_combo = QComboBox(self)
        self.layout.addWidget(self.event_type_combo)
        self.load_event_types()

        #для записи даты и времени
        self.start_time_input = QDateTimeEdit(self)
        self.start_time_input.setDateTime(QDateTime())
        self.layout.addWidget(self.start_time_input)

        #поле для ввода продолжительности события (в минутах)
        self.duration_input = QLineEdit(self)
        self.duration_input.setPlaceholderText('Продолжительность в минутах')
        self.layout.addWidget(self.duration_input)

        #кнопка для сохранения события
        self.add_event_button = QPushButton('Добавить событие', self)
        self.add_event_button.clicked.connect(self.add_event)
        self.layout.addWidget(self.add_event_button)

        #кнопка для списка невыполненных дел
        self.list_incomplete_button = QPushButton('Список невыполненных дел в Excel', self)
        self.list_incomplete_button.clicked.connect(self.list_incomplete_tasks)
        self.layout.addWidget(self.list_incomplete_button)

        #кнопка для отображения загрузки рабочего дня
        self.show_load_button = QPushButton('Показать загрузку рабочего дня', self)
        self.show_load_button.clicked.connect(self.daily_load)
        self.layout.addWidget(self.show_load_button)

        self.setLayout(self.layout)

    #метод для отображения типов событий в ComboBox
    def load_event_types(self):
        cursor.execute("SELECT * FROM types_event")
        types = cursor.fetchall()
        for types_event_id, name_type in types:
            self.event_type_combo.addItem(name_type, types_event_id)

    #метод для добавления события в БД
    def add_event(self):
        event_name = self.event_name_input.text()
        event_type_id = self.event_type_combo.currentData()
        start_time = self.start_time_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        duration = self.duration_input.text()
        mark_of_completion = 'не выполнено'                     #изменить на "выполнено" можно через БД

        if event_name and duration.isdigit():
            try:
                cursor.execute(
                    "INSERT INTO events (event_type_id, event_name, start_time, duration, mark_of_completion) VALUES (%s, %s, %s, %s, %s)",
                    (event_type_id, event_name, start_time, int(duration), mark_of_completion))
                connect.commit()
                QMessageBox.information(self, 'успех', 'событие добавлено.')
                self.event_name_input.clear()
                self.duration_input.clear()
            except MySQLdb.Error as e:
                QMessageBox.warning(self, 'ошибка', f'не получилось добавить событие: {e}')
        else:
            QMessageBox.warning(self, 'ошибка', 'заполните все поля корректно.')

    #метод для экспорта списка невыполненных дел в Excel
    def list_incomplete_tasks(self):
        cursor.execute(
            "SELECT event_name, start_time FROM events WHERE mark_of_completion = 'не выполнено'")
        tasks = cursor.fetchall()

        # создание листа в книге Excel
        wb = Workbook()
        sheet = wb.create_sheet("невыполненные дела")
        sheet.append(["название события", "дата и время"])

        for task in tasks:
            sheet.append(task)
        # сохранение
        file_path = 'incomplete_tasks.xlsx'
        wb.save(file_path)
        QMessageBox.information(self, 'экспорт завершен', f'невыполненные дела экспортированы в {file_path}')

    #метод для отображения загрузки рабочего дня
    def daily_load(self):
        cursor.execute(
            "SELECT SUM(duration) FROM events WHERE mark_of_completion = 'не выполнено'")
        total_duration = cursor.fetchone()[0]

        work_day_duration = 480                                 #допустим, что рабочий день составляет 8 часов (480 минут)
        percent = (total_duration/work_day_duration) * 100      #делим общее время на продолжительность рабочего дня

        #отображение полученного результата
        QMessageBox.information(self, 'доля загрузки рабочего дня',
                                f'доля загрузки рабочего дня: {percent:.2f}%')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    planner = Planner()
    planner.show()
    sys.exit(app.exec())

