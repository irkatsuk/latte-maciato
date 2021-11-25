import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
import ui
import addEditCoffeeForm


class AddCoffee(QMainWindow, addEditCoffeeForm.Ui_MainWindow):
    def __init__(self, parent, row=None):
        super().__init__()
        self.parent = parent
        self.con = self.parent.con
        self.row = row
        self.initUI()

    def initUI(self):
        self.setupUi(self)
        self.setWindowModality(Qt.ApplicationModal)
        if self.row is not None:
            self.ids = self.parent.table.item(self.row, 0).text()
            cur = self.con.cursor()
            queue = "SELECT * FROM coffee WHERE ID = " + self.ids
            result = cur.execute(queue).fetchall()
            name = result[0][1]
            roasting = result[0][2]
            ground = result[0][3]
            taste = result[0][4]
            cost = result[0][5]
            volume = result[0][6]
            cur = self.con.cursor()
            self.lineEditName.setText(name)
            self.lineEditRoasting.setText(roasting)
            if ground is True:
                self.checkBoxGround.setChecked(True)
            else:
                self.checkBoxGround.setChecked(False)
            self.lineEditDescribing.setText(taste)
            self.lineEditCost.setText(str(cost))
            self.lineEditVolume.setText(str(volume))
        self.pushButtonSave.clicked.connect(self.save)

    def save(self):
        self.labelStatus.setText('')
        name = self.lineEditName.text()
        roasting = self.lineEditRoasting.text()
        ground = self.checkBoxGround.isChecked()
        if ground is True:
            ground = 'True'
        else:
            ground = 'False'
        taste = self.lineEditDescribing.text()
        cost = self.lineEditCost.text()
        volume = self.lineEditVolume.text()
        if not cost.isdigit():
            self.labelStatus.setText('Неверно заполнена форма')
            return
        if not volume.isdigit():
            self.labelStatus.setText('Неверно заполнена форма')
            return
        cost = int(cost)
        volume = int(volume)
        cur = self.con.cursor()
        if self.row is None:
            cur.execute("""INSERT INTO coffee('Название сорта', 
            'Степень обжарки', 'Молотый/в зернах', 'Описание вкуса',
             'Цена', 'Обьем упаковки')
                                VALUES(?, ?, ?, ?, ?, ?)
                                """, (name, roasting, ground, taste,
                                      cost, volume))
        else:
            cur.execute("""UPDATE coffee SET 'Название сорта' = ?, 
            'Степень обжарки' = ?, 'Молотый/в зернах' = ?, 
            'Описание вкуса' = ?, 'Цена' = ?, 'Обьем упаковки' = ?
                        WHERE id = ?""", (name, roasting, ground, taste,
                                      cost, volume, self.ids))
        self.con.commit()
        self.parent.update_result()
        self.close()


class MyWidget(QMainWindow, ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.con = sqlite3.connect("data/coffee.sqlite")
        self.pushButtonAdd.clicked.connect(self.add)
        self.pushButtonChange.clicked.connect(self.change)
        self.update_result()

    def add(self):
        self.widget = AddCoffee(self)
        self.widget.show()

    def change(self):
        rows = list(set([i.row() for i in self.table.selectedItems()]))
        if len(rows) == 0:
            return
        self.widget = AddCoffee(self, rows[0])
        self.widget.show()

    def update_result(self):
        cur = self.con.cursor()
        names = ['ID', 'Название сорта', 'Степень обжарки', 'Молотый/в зернах',
                 'Описание вкуса', 'Цена', 'Обьем упаковки']
        # Получили результат запроса, который ввели в текстовое поле
        queue = "SELECT * FROM coffee"
        result = cur.execute(queue).fetchall()
        # Заполнили размеры таблицы
        self.table.setRowCount(len(result))
        if not result:
            return
        self.table.setColumnCount(len(result[0]))
        self.table.setHorizontalHeaderLabels(names)
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))
        self.table.resizeColumnsToContents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
