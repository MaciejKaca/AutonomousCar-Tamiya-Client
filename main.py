import sys
from pyqtgraph.Qt import QtCore, QtWidgets
from views.mainView import MainView
import pyqtgraph as pg

mainView = MainView()
#timer = pg.QtCore.QTimer()
#timer.timeout.connect(mainView.updateWindow)
#timer.start(50)

if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()