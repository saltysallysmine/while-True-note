import sys
import sqlite3
from form import Ui_MainWindow
from removing_widget import Ui_Form
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QPushButton, QVBoxLayout, QFileDialog, \
    QMessageBox, QInputDialog, QWidget, QCheckBox, QLabel

DB_NAME = 'notes_information.sqlite'


def enabling_main(main_window):
    main_window.setEnabled(True)
    main_window.refresh_sidebar()


class RemoveNotesWidget(QWidget, Ui_Form):
    def __init__(self, parent=None):
        self.parent = parent

        super().__init__(parent, QtCore.Qt.Window)
        self.setupUi(self)
        self.list_notes_filling()
        self.init_ui()

    def list_notes_filling(self):
        # open DB
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        self.list_notes_name = cur.execute(
            f'SELECT title FROM info').fetchall()
        con.commit()
        con.close()

    def init_ui(self):
        # form filling
        self.checkboxes = list()
        self.scrollnotes = QVBoxLayout(self)
        for el in self.list_notes_name:
            self.checkboxes.append(QCheckBox(self))
            self.scrollnotes.addWidget(self.checkboxes[-1])
            self.scrollnotes.addWidget(QLabel(el[0], self))

        w = QWidget(self)
        w.setLayout(self.scrollnotes)
        self.removing_notes_area.setWidget(w)

        # events connection
        self.ok_btn.clicked.connect(self.ok_click)
        self.cancel_btn.clicked.connect(self.cancel_click)
        self.closeEvent = self.ended_by_x

    def ok_click(self):
        # open DB
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        for i in range(len(self.list_notes_name)):
            box = self.checkboxes[i]
            name = self.list_notes_name[i][0]
            if box.isChecked():
                cur.execute(
                    f'DELETE FROM info WHERE title = "{name}"')

        con.commit()
        con.close()
        enabling_main(self.parent)
        self.close()

    def cancel_click(self):
        enabling_main(self.parent)
        self.close()

    def ended_by_x(self, x):
        enabling_main(self.parent)


class NoteWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        self.note_font_size = self.font_size = '18'

        super().__init__()
        self.setupUi(self)
        self.init_ui()
        self.styling_ui()

    def init_ui(self):
        # saving tools
        self.saved = True
        self.all_btns_without_saves = [
            self.txt_btn,
            self.new_note_btn,
            self.remove_multiple_notes_btn,
            self.convert_to_txt_btn
        ]

        for el in self.all_btns_without_saves:
            el.clicked.connect(self.not_saved_close)
        self.new_note_text.textChanged.connect(self.cancel_saved)

        # topbar
        self.txt_btn.clicked.connect(self.convert_txt_to_note)
        self.new_note_btn.clicked.connect(self.new_note)
        self.remove_this_note_btn.clicked.connect(self.remove_this_note)
        self.remove_multiple_notes_btn.clicked.connect(
            self.remove_multiple_notes)

        # sidebar
        self.list_notes_name = list()
        self.list_notes = list()
        self.untitled_note_number = 1
        self.refresh_sidebar()

        # footer
        self.save_note_btn.clicked.connect(self.save_note)
        self.save_note_as_btn.clicked.connect(self.save_note_as)
        self.convert_to_txt_btn.clicked.connect(self.convert_note_to_txt)

        # tools block
        self.all_size_spin.valueChanged.connect(self.all_size_changed)
        self.note_size_spin.valueChanged.connect(self.note_size_changed)

        # other
        self.number_of_notes = 1
        self.update_info_button.clicked.connect(self.this_note_information)

    def styling_ui(self):
        self.setStyleSheet(f'font-size: {self.font_size}px;')
        self.note_name_title.setStyleSheet(f'font-size: '
                                           f'{int(self.font_size) + 2}px;')
        self.number_of_notes_label.setStyleSheet(f'font-size: '
                                                 f'{int(self.font_size) + 2}'
                                                 f'px;')
        self.new_note_text.setStyleSheet(f'font-size: '
                                         f'{self.note_font_size}px;')

        self.info_labels = [self.lines_number, self.lines_number_value]
        for el in self.info_labels:
            el.setStyleSheet(f'font-size: {int(self.font_size) + 1}px;')

    def all_size_changed(self):
        self.font_size = self.all_size_spin.text()
        self.styling_ui()

    def note_size_changed(self):
        self.note_font_size = self.note_size_spin.text()
        self.styling_ui()

    def not_saved_close(self):
        if not self.saved:
            reply = QMessageBox.question(
                self, 'You want to close unsaved note',
                'Dou you want to save it?',
                QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.save_note()

            else:
                pass

    def cancel_saved(self):
        self.saved = False

    def convert_note_to_txt(self):
        name_txt = QFileDialog.getSaveFileName(
            self, 'Выбрать документ', '', 'Документ (*.txt)')[0]
        try:
            with open(name_txt, 'w', encoding='utf-8') as fp:
                fp.write(self.new_note_text.toPlainText())
        except FileNotFoundError:
            pass

    def convert_txt_to_note(self):
        name_txt = QFileDialog.getOpenFileName(
            self, 'Выбрать документ', '',
            'Документ (*.txt);;Все файлы (*)')[0]
        try:
            with open(name_txt, 'r', encoding='utf-8') as fp:
                gotten_text = fp.readlines()

            self.new_note_text.setPlainText('')
            for el in gotten_text:
                self.new_note_text.insertPlainText(el)
        except FileNotFoundError:
            pass

    def new_note(self, should_ask_about_saving=True):
        if should_ask_about_saving:
            reply = QMessageBox.question(
                self, 'Your note doesn`t saved', 'Save the note?',
                QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.save_note()
            else:
                self.new_note_text.setPlainText('')
                self.note_name_title.setText(f'Note '
                                             f'{self.untitled_note_number}')
                self.untitled_note_number += 1
        else:
            self.new_note_text.setPlainText('')
            self.note_name_title.setText(f'Note {self.untitled_note_number}')
            self.untitled_note_number += 1

    def save_note(self):
        new_note_text = self.new_note_text.toPlainText()
        name = self.note_name_title.text()
        # open DB
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

        reply = cur.execute(f'SELECT id FROM info'
                            f' WHERE title = "{name}"').fetchone()
        if reply is None:
            self.save_note_as()
        else:
            cur.execute(f'UPDATE info SET note_text = "{new_note_text}" '
                        f'WHERE title = "{name}"')
        con.commit()
        con.close()

        self.saved = True

    def save_note_as(self):
        new_note_text = self.new_note_text.toPlainText()

        unn = self.untitled_note_number
        name, ok_pressed = QInputDialog.getText(self,
                                                "How would you "
                                                "like to name it?",
                                                "Name?",
                                                text=f'Note {unn}')
        if ok_pressed:
            if name == f'Note {self.untitled_note_number}':
                self.untitled_note_number += 1

            # open DB
            con = sqlite3.connect(DB_NAME)
            cur = con.cursor()

            # finding the same file
            same_note = cur.execute(f'SELECT id FROM info'
                                    f' WHERE title = "{name}"').fetchone()
            if same_note is not None:
                reply = QMessageBox.question(
                    self, 'You have the same named note',
                    'Overwrite the note?',
                    QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    cur.execute(f'UPDATE info SET note_text = '
                                f'"{new_note_text}" '
                                f'WHERE title = "{name}"')
                else:
                    pass
            else:
                cur.execute(f'INSERT INTO info(title, note_text) '
                            f'VALUES ("{name}", "{new_note_text}")')
            self.note_name_title.setText(name)
            con.commit()
            con.close()

            self.refresh_sidebar()
            self.saved = True

    def remove_this_note(self):
        self.removing_name = self.note_name_title.text()
        reply = QMessageBox.question(
            self, 'Do you really want to remove this note?',
            f'Remove {self.removing_name}?',
            QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # open DB
            con = sqlite3.connect(DB_NAME)
            cur = con.cursor()

            cur.execute(
                f'DELETE FROM info WHERE title = "{self.removing_name}"')

            con.commit()
            con.close()
            self.new_note(False)
            self.refresh_sidebar()
        else:
            pass

    def remove_multiple_notes(self):
        self.setEnabled(False)
        rmv_widget = RemoveNotesWidget(self)
        rmv_widget.show()

    def this_note_information(self):
        line_count = 'line'
        numb_line = len(self.new_note_text.toPlainText().split('\n'))
        if numb_line != 1:
            line_count += 's'
        self.lines_number_value.setText(f'{numb_line}  {line_count}')

    def refresh_sidebar(self):
        # open DB
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

        # scroll notes widget clear

        self.list_notes_name.clear()
        self.list_notes.clear()

        # getting notes
        self.list_notes_name = cur.execute(f'SELECT title FROM info') \
            .fetchall()

        self.scrollnotes = QVBoxLayout(self)

        if self.list_notes_name is not None:
            for el in self.list_notes_name:
                self.list_notes.append(QPushButton(str(el[0]), self))
                self.list_notes[-1].clicked.connect(self.not_saved_close)
                self.list_notes[-1].clicked.connect(self.open_note)
                self.list_notes[-1].setMinimumHeight(40)
                self.scrollnotes.addWidget(self.list_notes[-1])

        # refresh scroll bar
        w = QWidget(self)
        w.setLayout(self.scrollnotes)
        self.scroll.setWidget(w)

        con.close()

        self.number_of_notes = len(self.list_notes_name)
        right_number_noun = 'note'
        if self.number_of_notes != 1:
            right_number_noun += 's'

        self.number_of_notes_label.setText(f'You have {self.number_of_notes}'
                                           f' {right_number_noun}')

    def open_note(self):
        self.note_name = self.sender().text()
        self.note_name_title.setText(self.note_name)
        # open DB
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

        sender_text = cur.execute(
            f'SELECT note_text FROM info WHERE title = "{self.note_name}"') \
            .fetchall()[0]
        con.close()
        self.new_note_text.setPlainText(sender_text[0])
        self.saved = True


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = NoteWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
