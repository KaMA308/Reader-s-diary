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

#
# def except_hook(cls, exception, traceback):
#     sys.__excepthook__(cls, exception, traceback)


class MainTable(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def update(self):
        self.model.setTable('literature')
        self.model.select()
        self.NameTable.setModel(self.model)

    def initUI(self):
        self.con = sqlite3.connect('Books')
        self.cur = self.con.cursor()

        uic.loadUi('MainWindow.ui', self)

        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('Books')
        self.db.open()

        self.model = QSqlTableModel(self, self.db)

        self.update()

        self.AddBtn.clicked.connect(self.addName)
        self.DelBtn.clicked.connect(self.delName)
        self.DataBtn.clicked.connect(self.nameInfo)

    def addName(self):

        input_name, ok_pressed = QInputDialog.getText(self, '', 'Введите название произведения')

        if ok_pressed:
            self.cur.execute(f"INSERT INTO literature(Name) VALUES('{input_name}')")

        self.con.commit()
        self.update()


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


class MainInformation(QWidget):
    def __init__(self, id):
        super().__init__()
        self.initUI(id)

    def initUI(self, id):
        self.con = sqlite3.connect('Books')
        self.cur = self.con.cursor()


        uic.loadUi('InfoWindow1.ui', self)
        cur_name = self.cur.execute(f'SELECT name FROM literature WHERE id = {id}').fetchone()
        self.setWindowTitle(f'Информация по произведению {str(*cur_name)}')

        cur_author = self.cur.execute(f'SELECT author FROM information WHERE id = {id}').fetchall()

        cur_author = [string[0] for string in cur_author]
        print('\n'.join(cur_author))
        self.authorText.setPlainText('\n'.join(cur_author))

        self.closeBtn.clicked.connect(self.closeWidget)
        self.nextWidBtn.clicked.connect(self.nextWidget)

    def closeWidget(self):
        self.main_widget = MainTable()
        MainInformation.hide(self)
        self.main_widget.show()

    def nextWidget(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainTable()
    ex.show()
    # sys.excepthook = except_hook
    sys.exit(app.exec())
