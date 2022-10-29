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
from graphs.graph_speed import graph_speed, COLOR
from graphs.graph_temperature import graph_temperature
from graphs.graph_time import graph_time
from utils.connection import Connection
import steamdeck_input as Joystick
import time

connection = Connection()
joystick = Joystick.get_controller(0)

while not joystick.was_exit_pressed():
  time.sleep(1)