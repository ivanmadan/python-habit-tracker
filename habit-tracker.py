import sys 
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QWidget, QInputDialog, QHBoxLayout, QButtonGroup, QSizePolicy
from PyQt5.QtCore import Qt
from datetime import datetime, timedelta
import pandas as pd
import os

class CheckButtonGroup(QWidget):
    def __init__(self, initial_state=False):
        super().__init__()

        self.button = QPushButton("✗")
        self.button.setCheckable(True)
        self.button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.button.setStyleSheet("""
            QPushButton { 
                background-color: red; 
                border: none; 
                margin: 0px; 
                padding: 0px;
            }
        """)

        self.button.clicked.connect(self.toggle_button)

        # Disconnect the button's clicked signal, set the initial state, and then reconnect the signal.
        self.button.clicked.disconnect()
        self.button.setChecked(initial_state)
        self.button.clicked.connect(self.toggle_button)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        if initial_state:
            self.button.setText("✓")
            self.button.setStyleSheet("""
                QPushButton { 
                    background-color: green; 
                    border: none; 
                    margin: 0px; 
                    padding: 0px;
                }
            """)


    def toggle_button(self):
        if self.button.isChecked():
            self.button.setText("✓")
            self.button.setStyleSheet("""
                QPushButton { 
                    background-color: green; 
                    border: none; 
                    margin: 0px; 
                    padding: 0px;
                }
            """)
        else:
            self.button.setText("✗")
            self.button.setStyleSheet("""
                QPushButton { 
                    background-color: red; 
                    border: none; 
                    margin: 0px; 
                    padding: 0px;
                }
            """)

class HabitTracker(QMainWindow):
    def __init__(self):
        super().__init__()

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(0)

        self.add_habit_button = QPushButton("Add Habit")
        self.add_habit_button.clicked.connect(self.add_habit)

        self.remove_habit_button = QPushButton("Remove Habit")
        self.remove_habit_button.clicked.connect(self.remove_habit)

        self.view_habit_button = QPushButton("View Habit")
        self.view_habit_button.clicked.connect(self.view_habit_calendar)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.add_habit_button)
        self.layout.addWidget(self.remove_habit_button)
        self.layout.addWidget(self.view_habit_button)
        self.layout.addWidget(self.table_widget)

        self.main_widget = QWidget()
        self.main_widget.setLayout(self.layout)

        self.setCentralWidget(self.main_widget)

        self.load_habits()

    def add_habit(self):
        habit, ok = QInputDialog.getText(self, 'Add habit', 'Enter a new habit:')
        if ok:
            column = self.table_widget.columnCount()
            self.table_widget.insertColumn(column)
            header = QTableWidgetItem(habit)
            self.table_widget.setHorizontalHeaderItem(column, header)
            
            for i in range(self.table_widget.rowCount()):
                button_group = CheckButtonGroup()
                self.table_widget.setCellWidget(i, column, button_group)
        self.save_habits()

    def remove_habit(self):
        habit, ok = QInputDialog.getText(self, 'Remove habit', 'Enter habit name to remove:')
        if ok:
            for i in range(self.table_widget.columnCount()):
                if self.table_widget.horizontalHeaderItem(i).text() == habit:
                    self.table_widget.removeColumn(i)
                    break
        self.save_habits()

    def save_habits(self):
        habits = {self.table_widget.horizontalHeaderItem(i).text(): [] for i in range(self.table_widget.columnCount())}
        for i in range(self.table_widget.rowCount()):
            date = self.table_widget.verticalHeaderItem(i).text()
            for j in range(self.table_widget.columnCount()):
                habits[self.table_widget.horizontalHeaderItem(j).text()].append(self.table_widget.cellWidget(i, j).button.isChecked())
        df = pd.DataFrame(habits, index=[self.table_widget.verticalHeaderItem(i).text() for i in range(self.table_widget.rowCount())])
        df.to_csv('habits.csv')

    def load_habits(self):
        if os.path.exists('habits.csv'):
            df = pd.read_csv('habits.csv', index_col=0)

            # for i, date in enumerate(df.index):
            #     self.table_widget.insertRow(i)
            #     item = QTableWidgetItem(date)
            #     self.table_widget.setVerticalHeaderItem(i, item)
            
            # for habit in df.columns:
            #     column = self.table_widget.columnCount()
            #     self.table_widget.insertColumn(column)
            #     header = QTableWidgetItem(habit)
            #     self.table_widget.setHorizontalHeaderItem(column, header)
            #     for i, date in enumerate(df.index):
            #         print(df.at[date, habit])
            #         print(df.at[date, habit] == True)
            #         button_group = CheckButtonGroup()
            #         button_group.button.setChecked(df.at[date, habit] == True)
            #         #self.table_widget.setCellWidget(i, column, button_group)
                    
            #         self.table_widget.setCellWidget(i, column, button_group)

            for habit in df.columns:
                column = self.table_widget.columnCount()
                self.table_widget.insertColumn(column)
                header = QTableWidgetItem(habit)
                self.table_widget.setHorizontalHeaderItem(column, header)
                for i, date in enumerate(df.index):
                    if i >= self.table_widget.rowCount():
                        self.table_widget.insertRow(i)
                        item = QTableWidgetItem(date)
                        self.table_widget.setVerticalHeaderItem(i, item)
                    initial_state = df.at[date, habit]
                    print(initial_state)
                    button_group = CheckButtonGroup(initial_state)
                    self.table_widget.setCellWidget(i, column, button_group)
                self.table_widget.resizeColumnsToContents()
            
            self.add_today_if_not_exists(df)
        else:
            self.table_widget.setRowCount(7) # for example, one week
            for i in range(7):
                date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
                item = QTableWidgetItem(date)
                self.table_widget.setVerticalHeaderItem(i, item)

    def add_today_if_not_exists(self, df):
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in df.index:
            self.table_widget.insertRow(self.table_widget.rowCount())
            item = QTableWidgetItem(today)
            self.table_widget.setVerticalHeaderItem(self.table_widget.rowCount()-1, item)
            for j in range(self.table_widget.columnCount()):
                button_group = CheckButtonGroup()
                self.table_widget.setCellWidget(self.table_widget.rowCount()-1, j, button_group)

    def closeEvent(self, event):
        self.save_habits()
        event.accept()

    def view_habit_calendar(self):  
        habit, ok = QInputDialog.getItem(self, 'View habit', 'Select a habit to view:', [self.table_widget.horizontalHeaderItem(i).text() for i in range(self.table_widget.columnCount())]) 
        if ok:
            print(f"Viewing calendar for habit: {habit}") 
            # TODO: Implement the calendar view for the selected habit.

app = QApplication(sys.argv)
win = HabitTracker()
win.resize(800, 300)
win.show()
sys.exit(app.exec())
