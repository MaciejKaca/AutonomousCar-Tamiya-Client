import sys

from PyQt5.QtWidgets import QApplication
from pyqtgraph.Qt import QtCore, QtWidgets
from views.main_view import MainView

app = QApplication(sys.argv)
mainView = MainView()

if __name__ == '__main__':
    mainView.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QApplication.instance().exec_()
