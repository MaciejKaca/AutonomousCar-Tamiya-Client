import sys
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
from communication import Communication
from dataBase import data_base
from PyQt5.QtWidgets import QPushButton
from graphs.graph_acceleration import graph_acceleration
from graphs.graph_altitude import graph_altitude
from graphs.graph_battery import graph_battery
from graphs.graph_free_fall import graph_free_fall
from graphs.graph_gyro import graph_gyro
from graphs.graph_pressure import graph_pressure
from graphs.graph_speed import graph_speed, COLORS
from graphs.graph_temperature import graph_temperature
from graphs.graph_time import graph_time
from utils.socket_server import CarSocket
from utils.messages import Direction


sock = CarSocket()

pg.setConfigOption('background', (33, 33, 33))
pg.setConfigOption('foreground', (197, 198, 199))
# Interface variables
app = QtWidgets.QApplication(sys.argv)
view = pg.GraphicsView()
Layout = pg.GraphicsLayout()
view.setCentralItem(Layout)
view.show()
view.setWindowTitle('Raspberry Car')
view.resize(1200, 700)

# declare object for storage in CSV
data_base = data_base()
# Fonts for text items
font = QtGui.QFont()
font.setPixelSize(90)

# buttons style
style = "background-color:rgb(29, 185, 84);color:rgb(0,0,0);font-size:14px;"


# Declare graphs
# Button 1
proxy = QtWidgets.QGraphicsProxyWidget()
save_button = QtWidgets.QPushButton('Save data')
save_button.setStyleSheet(style)
save_button.clicked.connect(data_base.start)
proxy.setWidget(save_button)

# Button 2
proxy2 = QtWidgets.QGraphicsProxyWidget()
end_save_button = QtWidgets.QPushButton('Stop saving')
end_save_button.setStyleSheet(style)
end_save_button.clicked.connect(data_base.stop)
proxy2.setWidget(end_save_button)


speed = graph_speed(data_names = ["speed"])
                
Layout.nextRow()

layout_button = Layout.addLayout(colspan=21)
layout_button.addItem(proxy)
layout_button.nextCol()
layout_button.addItem(proxy2)

Layout.nextRow()

l1 = Layout.addLayout(colspan=20, rowspan=2)
l11 = l1.addLayout(rowspan=1, border=(83, 83, 83))

l11.addItem(speed)

speed.add_data(0)

def update():
    try:
        data_list = sock.get_data()
        if len(data_list):
            for data in data_list:
                if data.direction == Direction.FORWARD:
                    speed.add_data(data.speed, data.sent_time, axis="speed")
                elif data.direction == Direction.BACKWARD:
                    speed.add_data(-data.speed, data.sent_time, axis="speed")
        speed.update()
    except IndexError:
        print('starting, please wait a moment')

timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(500)

if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()
