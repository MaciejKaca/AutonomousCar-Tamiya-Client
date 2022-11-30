from PyQt5.QtGui import *
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, QSize
from PyQt5.QtGui import QFont, QPalette
from PyQt5.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout,QFrame
from pyqtgraph.Qt import QtGui
import pyqtgraph as pg
from graphs.speed_graph import SpeedGraph
from graphs.current_graph import CurrentGraph
from utils.camera_stream import CameraStream
from utils.connection import Connection
from steamdeck_input import get_controller


class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sock = Connection()
        self.controller = get_controller(0)

        self.speedGraph = SpeedGraph(title="Speed/Brake")
        self.currentGraph = CurrentGraph(title="Voltage")

        self.graph_layout_widget = pg.GraphicsLayoutWidget()

        self.voltage = QLabel()

        self.camera_stream = CameraStream()

        self.GRAPHS_PADDING = 40
        self.FONT_SIZE = 100

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_window)
        self.timer.start(30)

        self.setup_layout()
        self.setup_graphs()

    def setup_graphs(self):
        self.speedGraph.start_graph()
        self.currentGraph.start_graph()

    def update_window(self):
        self.set_graphs_size()

        self.speedGraph.draw_graph()
        self.currentGraph.draw_graph()
        self.voltage.setText(str(self.currentGraph.get_last_current())[0:3] + "V")
        self.camera_stream.draw()

    def set_graphs_size(self):
        size: QSize = self.graph_layout_widget.size()
        width = ((size.width() - self.GRAPHS_PADDING) / 2)
        self.currentGraph.setFixedWidth(width)
        self.speedGraph.setFixedWidth(width)

        self.voltage.setMaximumWidth(size.height())
        self.voltage.setFont(QFont('Arial', self.FONT_SIZE))

    def setup_layout(self):
        self.setWindowTitle("RaspberryPi Car")
        widget = QWidget()

        pg.setConfigOption('background', (33, 33, 33))
        pg.setConfigOption('foreground', (197, 198, 199))

        self.graph_layout_widget = pg.GraphicsLayoutWidget()

        # adding view box to the graphic layout widget
        graph_layout = self.graph_layout_widget.addLayout(border=(83, 83, 83))

        graph_layout.addItem(self.speedGraph)
        graph_layout.addItem(self.currentGraph)

        # Creating a grid layout
        graphs_layout = QHBoxLayout()

        # setting this layout to the widget
        main_layout = QVBoxLayout()
        widget.setLayout(main_layout)

        # plot window goes on right side, spanning 3 rows
        graphs_layout.addWidget(self.graph_layout_widget)

        # adding label in the layout
        self.voltage.setFrameStyle(QFrame.Panel)
        self.voltage.setAlignment(QtCore.Qt.AlignCenter)
        self.voltage.setStyleSheet('color: white')
        graphs_layout.addWidget(self.voltage)

        main_layout.addLayout(graphs_layout)

        # Setup camera view
        camera_layout = QHBoxLayout()
        camera_layout.addStretch()
        camera_layout.addWidget(self.camera_stream)
        camera_layout.addStretch()
        main_layout.addLayout(camera_layout)

        # setting this widget as central widget of the main window
        self.setCentralWidget(widget)

        self.setFixedWidth(1280)
        self.setFixedHeight(800)
        self.changeSkinDark()

        #self.showFullScreen()

    def changeSkinDark(self):
        darkpalette = QtGui.QPalette()
        darkpalette.setColor(QtGui.QPalette.Window, QtGui.QColor(33, 33, 33))
        darkpalette.setColor(QtGui.QPalette.Base, QtGui.QColor(33, 33, 33))
        darkpalette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(41, 44, 51))
        darkpalette.setColor(QtGui.QPalette.Button, QtGui.QColor(41, 44, 51))
        darkpalette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(100, 100, 225))
        QtGui.QGuiApplication.setPalette(darkpalette)
