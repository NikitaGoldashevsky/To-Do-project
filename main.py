import sqlite3
from sqlite3 import Error

import PyQt5.Qt
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QInputDialog, QListWidgetItem, QMessageBox
import sys

from PyQt5.uic.properties import QtGui


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        PyQt5.uic.loadUi('main_widget.ui', self)
        self.show()

        # setting up a connection to the database
        self.create_connection("databases/db.sql")

        # connecting BUTTONS
        self.add_group_btn.clicked.connect(self.add_group)
        self.delete_group_btn.clicked.connect(self.delete_group)
        self.add_note_btn.clicked.connect(self.add_note)
        self.delete_note_btn.clicked.connect(self.delete_note)

        # dict to storage local data (keys are groups, values are notes)
        self.data = dict()

        # other
        self.groups = []
        vbox = PyQt5.Qt.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)
        self.group_list.setSpacing(6)
        self.note_list.setSpacing(4)
        # self.note_list.wordWrap(True)
        self.note_size = 100, 70
        self.note_font = 'Calibri', 17
        self.group_font = 'Arial', 16
        self.update_group_list()

        with open("style_sheet.txt") as source:
            self.setStyleSheet(f"""{source.read()}""")

        # connecting EVENTS
        self.update_local_data()
        self.group_list.itemClicked.connect(self.update_note_list)

    def update_local_data(self, update_widgets=False):
        groups = map(lambda x: x[0], self.cursor.execute(f"""SELECT * FROM groups""").fetchall())
        for group in groups:
            its_notes = list(map(lambda x: x[0], self.cursor.execute(
                f"""SELECT \"note\" FROM notes WHERE \"group\"=\"{group}\"""").fetchall()))
            self.data[group] = its_notes
        if update_widgets:
            for group_name in self.data.keys():
                self.group_list.addItem(self.set_group_item(group_name))
            if len(self.group_list.selectedItems()) != 0:
                for note in self.data[self.group_list.selectedItems()[0].text()]:
                    self.note_list.addItem(self.set_note_item(note))
        print(self.data)

    def update_group_list(self):
        data = self.cursor.execute(f"""SELECT * FROM groups""").fetchall()
        data = map(lambda x: x[0], data)
        for elem in data:
            self.group_list.addItem(self.set_group_item(elem))

    def update_note_list(self):
        self.note_list.clear()
        # print(self.data['8989'])
        if len(self.data[self.group_list.selectedItems()[0].text()]) != 0:
            for elem in self.data[self.group_list.selectedItems()[0].text()]:
                self.note_list.addItem(self.set_note_item(elem))

    def add_group(self):
        name, ok = QInputDialog.getText(self, 'Adding new group', 'Enter the name')
        if ok:
            # print(f"INSERT INTO groups (\"name\") VALUES (\"{name}\")")
            self.cursor.execute(f"""INSERT INTO groups (\"name\") VALUES (\"{name}\")""")
            self.connection.commit()

            self.group_list.addItem(self.set_group_item(name))

    def set_group_item(self, name):
        name_item = QListWidgetItem(name)
        name_item.setSizeHint(PyQt5.Qt.QSize(100, 50))
        # name_item.setIcon(PyQt5.Qt.QIcon(PyQt5.Qt.QPixmap('C:/Users/admin/Desktop/Безымянный.png')))
        font = PyQt5.Qt.QFont(*self.group_font, 16)
        font.setBold(True)
        # font.setBold(self.is_bold['group'])
        name_item.setFont(font)
        return name_item

    def delete_note(self):
        if len(self.note_list.selectedItems()) != 1:
            return
        ret = QMessageBox.question(self, 'Confirm', f"Are you sure you want to delete the note?",
                                   QMessageBox.Yes | QMessageBox.No)
        if ret != QMessageBox.Yes:
            return
        note = self.note_list.selectedItems()[0].text()
        self.cursor.execute(f"""DELETE FROM notes WHERE note=\"{note}\"""")
        self.connection.commit()
        self.note_list.takeItem(self.note_list.row(self.note_list.selectedItems()[0]))
        self.note_list.clearSelection()

    def set_note_item(self, text):
        note_item = QListWidgetItem(text)
        note_item.setSizeHint(PyQt5.Qt.QSize(*self.note_size))
        # note_item.setIcon(PyQt5.Qt.QIcon(PyQt5.Qt.QPixmap('C:/Users/admin/Desktop/Безымянный.png')))
        font = PyQt5.Qt.QFont(*self.note_font)
        # font.setBold(True)
        note_item.setFont(font)
        return note_item

    def add_note(self):
        note, ok = QInputDialog.getText(self, 'Adding new note', 'Enter the note')
        if len(note) == 0:
            return
        if ok:
            try:
                group_name = self.group_list.selectedItems()[0].text()
            except Exception:
                return
            # print(f"INSERT INTO notes (\"note\", \"group\") VALUES (\"{note}\", \"{group_name}\")")
            self.cursor.execute(f"""INSERT INTO notes (\"note\", \"group\") VALUES (\"{note}\", \"{group_name}\")""")
            self.connection.commit()

            self.note_list.addItem(self.set_note_item(note))

    def create_connection(self, path):
        try:
            self.connection = sqlite3.connect(path)
            print('Connection to SQLite database is successful')
        except Error as e:
            print(f"The error '{e}'occurred")
        self.cursor = self.connection.cursor()

    def delete_group(self):
        if len(self.group_list.selectedItems()) != 1:
            return
        name = self.group_list.selectedItems()[0].text()
        ret = QMessageBox.question(self, 'Confirm', f"Are you sure you want to delete the group \"{name}\"?",
                                   QMessageBox.Yes | QMessageBox.No)

        if ret != QMessageBox.Yes:
            return
        self.cursor.execute(f"""DELETE FROM groups WHERE name=\"{name}\"""")
        # print(f"DELETE FROM groups WHERE name=\"{name}\"")
        self.cursor.execute(f"""DELETE FROM notes WHERE \"group\"=\"{name}\"""")
        self.connection.commit()
        self.group_list.takeItem(self.group_list.row(self.group_list.selectedItems()[0]))
        self.note_list.clear()
        self.group_list.clearSelection()


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
app.exec()
