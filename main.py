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
    QMessageBox
)

from PyQt6.QtCore import Qt


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
        self.DataBtn.clicked.connect(self.openInfo)

    def initDb(self):
        self.con = sqlite3.connect('Books')
        self.cur = self.con.cursor()

    def addName(self):
        input_name, ok_pressed = QInputDialog.getText(self, '', 'Введите название произведения')

        if ok_pressed:
            self.cur.execute(f"INSERT INTO literature(Name) VALUES('{input_name}')")
            sel_id = self.cur.execute(f"SELECT id FROM literature WHERE name = '{input_name}'").fetchone()[0]
            self.cur.execute(f"INSERT INTO information(id) VALUES({sel_id})")

        self.con.commit()
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_O:
            self.openInfo()

        elif event.key() == Qt.Key.Key_D:
            self.delName()

        elif event.key() == Qt.Key.Key_A:
            self.addName()

    def delName(self):

        input_id, ok_pressed = QInputDialog.getText(self, '', 'Введите id произведения, которое хотите удалить')

        if ok_pressed:
            self.cur.execute(f'DELETE from literature WHERE id = ("{input_id}")')
            self.cur.execute(f'DELETE from information WHERE id = ("{input_id}")')

        self.con.commit()
        self.update()

    def openInfo(self):

        input_id, ok_pressed = QInputDialog.getText(self, '',
                                                    'Введите id произведения, чтобы получить по нему информацию')

        if ok_pressed:
            if bool(self.cur.execute(f'SELECT id FROM literature WHERE id = {input_id}').fetchone()):
                self.inf_widget = MainInformation(input_id)
                MainTable.hide(self)
                self.inf_widget.show()

            else:
                error_mes = QMessageBox()
                error_mes.setWindowTitle('Ошибка')
                error_mes.setText('Указанное id не найдено')
                error_mes.exec()


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
        self.editAut.clicked.connect(self.editLock)
        self.editChar.clicked.connect(self.editLock)
        self.editKeyP.clicked.connect(self.editLock)

    def saveInfo(self, plain=''):

        if bool(plain):
            if plain == 'saveAuth':
                sel_row = 'author'
                sel_plain = self.authorText

            elif plain == 'saveChar':
                sel_row = 'characters'
                sel_plain = self.charactersText

            elif plain == 'savePoints':
                sel_row = 'KeyPoints'
                sel_plain = self.keyPointsText

            elif plain == 'saveClash':
                sel_row = 'Clash'
                sel_plain = self.clashText

            elif plain == 'saveArgum':
                sel_row = 'Arguments'
                sel_plain = self.argumText

        else:
            if self.sender().objectName() == 'saveAuth':
                sel_row = 'author'
                sel_plain = self.authorText

            elif self.sender().objectName() == 'saveChar':
                sel_row = 'characters'
                sel_plain = self.charactersText

            elif self.sender().objectName() == 'savePoints' or plain == 'savePoints':
                sel_row = 'KeyPoints'
                sel_plain = self.keyPointsText

            elif self.sender().objectName() == 'saveClash':
                sel_row = 'Clash'
                sel_plain = self.clashText

            elif self.sender().objectName() == 'saveArgum':
                sel_row = 'Arguments'
                sel_plain = self.argumText
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

    def editLock(self):
        if self.sender().text() == 'Редактировать':
            self.sender().setText('Прекратить')

        else:
            self.sender().setText('Редактировать')

        if self.sender().objectName() == 'editAut':
            sel_plain = self.authorText

        elif self.sender().objectName() == 'editChar':
            sel_plain = self.charactersText

        elif self.sender().objectName() == 'editKeyP':
            sel_plain = self.keyPointsText

        elif self.sender().objectName() == 'editClash':
            sel_plain = self.clashText

        elif self.sender().objectName() == 'editArgum':
            sel_plain = self.argumText

        if sel_plain.isReadOnly():
            sel_plain.setReadOnly(False)

        else:
            sel_plain.setReadOnly(True)

    def editLockHotKey(self, sel_plain):
        if sel_plain == self.authorText:
            sel_btn = self.editAut

        elif sel_plain == self.charactersText:
            sel_btn = self.editChar

        elif sel_plain == self.keyPointsText:
            sel_btn = self.editKeyP





        if sel_plain.isReadOnly():
            sel_plain.setReadOnly(False)
            sel_btn.setText('Прекратить')

        else:
            sel_plain.setReadOnly(True)
            sel_btn.setText('Редактировать')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_N:
            self.nextWidget()

        elif event.key() == Qt.Key.Key_Escape:
            self.closeWidget()

        elif event.modifiers() == Qt.KeyboardModifier.AltModifier:
            if event.key() == Qt.Key.Key_A:
                self.editLockHotKey(self.authorText)

            elif event.key() == Qt.Key.Key_C:
                self.editLockHotKey(self.charactersText)

            elif event.key() == Qt.Key.Key_K:
                self.editLockHotKey(self.keyPointsText)

        elif event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            if event.key() == Qt.Key.Key_A:
                self.saveInfo(plain='saveAuth')

            elif event.key() == Qt.Key.Key_C:
                self.saveInfo(plain='saveChar')

            elif event.key() == Qt.Key.Key_K:
                self.saveInfo(plain='savePoints')


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

        cur_author = self.cur.execute(f'SELECT Clash FROM information WHERE id = {self.id}').fetchone()
        self.clashText.setPlainText(cur_author[0])

        cur_author = self.cur.execute(f'SELECT Arguments FROM information WHERE id = {self.id}').fetchone()
        self.argumText.setPlainText(cur_author[0])

        self.closeBtn.clicked.connect(self.closeWidget)
        self.backBtn.clicked.connect(self.backWidget)
        self.saveClash.clicked.connect(self.saveInfo)
        self.saveArgum.clicked.connect(self.saveInfo)
        self.editClash.clicked.connect(self.editLock)
        self.editArgum.clicked.connect(self.editLock)

    def closeWidget(self):
        super().closeWidget()
        MoreInformation.hide(self)

    def backWidget(self):
        self.inf_widget = MainInformation(self.id)
        MoreInformation.hide(self)
        self.inf_widget.show()

    def saveInfo(self):
        super().saveInfo()

    def editLock(self):
        super().editLock()

    def editLockHotKey(self, sel_plain):
        if sel_plain == self.argumText:
            sel_btn = self.editArgum

        elif sel_plain == self.clashText:
            sel_btn = self.editClash

        if sel_plain.isReadOnly():
            sel_plain.setReadOnly(False)
            sel_btn.setText('Прекратить')

        else:
            sel_plain.setReadOnly(True)
            sel_btn.setText('Редактировать')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.closeWidget()

        elif event.key() == Qt.Key.Key_B:
            self.backWidget()

        elif event.modifiers() == Qt.KeyboardModifier.AltModifier:
            if event.key() == Qt.Key.Key_A:
                self.editLockHotKey(self.argumText)

            elif event.key() == Qt.Key.Key_C:
                self.editLockHotKey(self.clashText)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainTable()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
