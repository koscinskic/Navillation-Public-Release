import sys

import qdarkstyle
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QAction, qApp

from app.DocViewer import DocViewer
from app.EntryViewer import EntryViewer
from app.MatrixViewer import MatrixViewer
from app.NaviDock import NaviDock


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):

        super(MainWindow, self).__init__(*args, **kwargs)

        # TODO: add cfg and use sys args
        res = (1920, 1080)
        self.resize(res[0], res[1])
        self.setWindowTitle("Navillation")

        # Central Widget
        self.__main_window = QWidget()
        self.__layout = QVBoxLayout()
        self.__main_window.setLayout(self.__layout)
        self.setCentralWidget(self.__main_window)

        # Standard Dock Features
        self.__navi_dock = NaviDock(res)
        self.__matrix_viewer = MatrixViewer(resolution=res)
        # TODO: generalize data update
        self.__entry_viewer = EntryViewer(
            data_update_signal=self.__matrix_viewer.get_data_update_signal(),
            resolution=res
        )
        self.__doc_viewer = DocViewer(resolution=res)
        self.__navi_dock.add_navi_tool(self.__matrix_viewer)
        self.__navi_dock.add_navi_tool(self.__entry_viewer)
        self.__navi_dock.add_navi_tool(self.__doc_viewer)
        self.__layout.addWidget(self.__navi_dock)

        # Menus

        menu_bar = self.menuBar()
        status_bar = self.statusBar()

        exit_act = QAction(QIcon('exit.png'), '&Exit', self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.setStatusTip('Exit application')
        exit_act.triggered.connect(qApp.quit)

        add_file_act = QAction(QIcon('add.png'), '&Add File(s)', self)
        add_file_act.setShortcut('Ctrl+A')
        add_file_act.setStatusTip('Add files for analysis')
        add_file_act.triggered.connect(self.__navi_dock.get_file_handler().add_files_option)

        del_file_act = QAction(QIcon('delete.png'), 'Remove File(s)', self)
        del_file_act.setShortcut('Ctrl+R')
        del_file_act.setStatusTip('Remove files from analysis')
        del_file_act.triggered.connect(self.__navi_dock.get_file_handler().delete_files_option)

        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(exit_act)
        file_menu.addAction(add_file_act)
        file_menu.addAction(del_file_act)


# TODO: better logging
def logger_handler(type, value, tb):
    # logging.getLogger("mylogger").exception("Uncaught exception: {0}".format(str(value)))
    # print("AH!\n")
    tb.print_exception()


def main():

    sys.excepthook = logger_handler

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    # TODO: better exception handling
    # try:
    #     main()
    # except Exception as e:
    #     print(f"Exception: {e}")
    main()

