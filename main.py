import sys
from pyqtgraph.Qt import QtCore, QtWidgets
from views.mainView import MainView

mainView = MainView()

if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()