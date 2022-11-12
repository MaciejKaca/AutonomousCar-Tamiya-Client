import sys
from pyqtgraph.Qt import QtGui, QtWidgets
import pyqtgraph as pg
from graphs.graph_speed import SpeedGraph, COLOR
from utils.connection import Connection
from steamdeck_input import get_controller

class MainView():
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.sock = Connection()
        self.controller = get_controller(0)
        self.speedGraph = SpeedGraph(title="Spped/Brake")

        pg.setConfigOption('background', (33, 33, 33))
        pg.setConfigOption('foreground', (197, 198, 199))

        self.view = pg.GraphicsView()
        self.layout = pg.GraphicsLayout()
        self.font = QtGui.QFont()
        
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.updateWindow)
        self.timer.start(50)

        self.setupLayout()
        self.setupGrapghs()

    def setupGrapghs(self):
        self.speedGraph.add_axis("speed", COLOR.GREEN)
        self.speedGraph.add_axis("brake", COLOR.RED)
        self.speedGraph.add_data(0, axis="speed")
        self.speedGraph.add_data(0, axis="brake")
        self.speedGraph.start_graph()

    def updateWindow(self):
        self.speedGraph.draw_graph()

    def setupLayout(self):
        self.font.setPixelSize(90)

        pg.setConfigOption('background', (33, 33, 33))
        pg.setConfigOption('foreground', (197, 198, 199))

        self.view.setCentralItem(self.layout)
        self.view.show()
        self.view.setWindowTitle('Raspberry Car')
        self.view.resize(1200, 700)

        l1 = self.layout.addLayout(colspan=20, rowspan=2)
        l11 = l1.addLayout(rowspan=1, border=(83, 83, 83))
        l11.addItem(self.speedGraph)