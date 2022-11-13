import sys
from pyqtgraph.Qt import QtGui, QtWidgets
import pyqtgraph as pg
from graphs.SpeedGraph import SpeedGraph
from graphs.current_graph import CurrentGraph
from utils.connection import Connection
from steamdeck_input import get_controller
from utils.colors import Color


class MainView:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.sock = Connection()
        self.controller = get_controller(0)
        self.speedGraph = SpeedGraph(title="Speed/Brake")
        self.currentGraph = CurrentGraph(title="Voltage")

        pg.setConfigOption('background', (33, 33, 33))
        pg.setConfigOption('foreground', (197, 198, 199))

        self.view = pg.GraphicsView()
        self.layout = pg.GraphicsLayout()
        self.font = QtGui.QFont()

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_window)
        self.timer.start(50)

        self.setup_layout()
        self.setup_graphs()

    def setup_graphs(self):
        self.speedGraph.start_graph()
        self.currentGraph.start_graph()

    def update_window(self):
        self.speedGraph.draw_graph()
        self.currentGraph.draw_graph()

    def setup_layout(self):
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
        l11.addItem(self.currentGraph)
