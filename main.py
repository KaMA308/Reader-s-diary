import sys
import sqlite3

from PyQt6 import uic

from PyQt6.QtSql import (
    QSqlDatabase,
    QSqlTableModel
)

from PyQt6.QtWidgets import (
    QWidget,
    QTableView,
    QApplication,
    QInputDialog,

)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class MainTable(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def update(self):
        self.model.setTable('literature')
        self.model.select()
        self.NameTable.setModel(self.model)

    def initUI(self):
        self.initDb()

        uic.loadUi('MainWindow.ui', self)

        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('Books')
        self.db.open()

        self.model = QSqlTableModel(self, self.db)

        self.update()

        self.AddBtn.clicked.connect(self.addName)
        self.DelBtn.clicked.connect(self.delName)
        self.DataBtn.clicked.connect(self.nameInfo)

    def initDb(self):
        self.con = sqlite3.connect('Books')
        self.cur = self.con.cursor()

    def addName(self):

        input_name, ok_pressed = QInputDialog.getText(self, '', 'Введите название произведения')

        if ok_pressed:
            self.cur.execute(f"INSERT INTO literature(Name) VALUES('{input_name}')")

        self.con.commit()
        self.update()

    # Доделать удаление вместе с именем информацию
    def delName(self):

        input_id, ok_pressed = QInputDialog.getText(self, '', 'Введите id произведения, которое хотите удалить')

        if ok_pressed:
            self.cur.execute(f'DELETE from literature WHERE id = ("{input_id}")')

        self.con.commit()
        self.update()

    def nameInfo(self):

        input_id, ok_pressed = QInputDialog.getText(self, '',
                                                         'Введите id произведения, чтобы получить по нему информацию')

        if ok_pressed:
            self.inf_widget = MainInformation(input_id)
            MainTable.hide(self)
            self.inf_widget.show()


class MainInformation(MainTable, QWidget):
    def __init__(self, id):
        super(QWidget, self).__init__()
        self.id = id
        self.initUI()

    def initUI(self):
        super().initDb()

        uic.loadUi('InfoWindow1.ui', self)
        cur_name = self.cur.execute(f'SELECT name FROM literature WHERE id = {self.id}').fetchone()
        self.setWindowTitle(f'Информация по произведению {str(*cur_name)}')

        cur_author = self.cur.execute(f'SELECT author FROM information WHERE id = {self.id}').fetchone()
        self.authorText.setPlainText(cur_author[0])
        # При пустых значениях таблицы выдает ошибку
        cur_author = self.cur.execute(f'SELECT characters FROM information WHERE id = {self.id}').fetchone()
        self.charactersText.setPlainText(cur_author[0])

        cur_author = self.cur.execute(f'SELECT KeyPoints FROM information WHERE id = {self.id}').fetchone()
        self.keyPointsText.setPlainText(cur_author[0])

        self.closeBtn.clicked.connect(self.closeWidget)
        self.nextWidBtn.clicked.connect(self.nextWidget)
        self.saveAuth.clicked.connect(self.saveInfo)
        self.saveChar.clicked.connect(self.saveInfo)
        self.savePoints.clicked.connect(self.saveInfo)



    def saveInfo(self):
        if self.sender().objectName() == 'saveAuth':
            sel_row = 'author'
            sel_plain = self.authorText

        elif self.sender().objectName() == 'saveChar':
            sel_row = 'characters'
            sel_plain = self.charactersText

        elif self.sender().objectName() == 'savePoints':
            sel_row = 'KeyPoints'
            sel_plain = self.keyPointsText

        info = sel_plain.toPlainText()

        self.cur.execute(f"""UPDATE information SET {sel_row} = '{info}' WHERE id = {self.id}""")
        self.con.commit()

    def closeWidget(self):
        self.main_widget = MainTable()
        MainInformation.hide(self)
        self.main_widget.show()

    def nextWidget(self):
        self.inf_widget = MoreInformation(self.id)
        MainInformation.hide(self)
        self.inf_widget.show()


class MoreInformation(MainInformation, MainTable, QWidget):
    def __init__(self, id):
        super().__init__(id)
        self.id = id
        self.initUI()

    def initUI(self):
        super().initDb()

        uic.loadUi('InfoWindow2.ui', self)
        cur_name = self.cur.execute(f'SELECT name FROM literature WHERE id = {self.id}').fetchone()
        self.setWindowTitle(f'Дополнительная информация по произведению {str(*cur_name)}')

        self.closeBtn.clicked.connect(self.closeWidget)
        self.backBtn.clicked.connect(self.backWidget)
        self.saveClash.clicked.connect(self.saveInfo)
        self.saveArgum.clicked.connect(self.saveInfo)

    def closeWidget(self):
        super().closeWidget()
        MoreInformation.hide(self)

    def backWidget(self):
        self.inf_widget = MainInformation(self.id)
        MoreInformation.hide(self)
        self.inf_widget.show()

    def saveInfo(self):
        pass #через super





if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainTable()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
#изменение шрифта при чтении