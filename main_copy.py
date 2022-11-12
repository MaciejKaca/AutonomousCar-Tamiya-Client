import sys
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
from graphs.graph_speed import SpeedGraph, COLOR
from utils.connection import Connection
from steamdeck_input import get_controller

app = QtWidgets.QApplication(sys.argv)
sock = Connection()
controller = get_controller(0)

speed = SpeedGraph(title="Spped/Brake")
speed.add_axis("speed", COLOR.GREEN)
speed.add_axis("brake", COLOR.RED)

pg.setConfigOption('background', (33, 33, 33))
pg.setConfigOption('foreground', (197, 198, 199))

view = pg.GraphicsView()
Layout = pg.GraphicsLayout()

view.setCentralItem(Layout)
view.show()
view.setWindowTitle('Raspberry Car')
view.resize(1200, 700)

# Fonts for text items
font = QtGui.QFont()
font.setPixelSize(90)

l1 = Layout.addLayout(colspan=20, rowspan=2)
l11 = l1.addLayout(rowspan=1, border=(83, 83, 83))

l11.addItem(speed)

speed.add_data(0, axis="speed")
speed.add_data(0, axis="brake")
speed.start_graph()

def update():
    speed.draw_graph()

timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)

if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()