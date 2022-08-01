from pickletools import int4
from typing import Dict, List
import pyqtgraph as pg
import numpy as np
from enum import Enum
from threading import Thread, Lock
import time

class COLOR:
    RED = (255, 0 ,0)
    GREEN = (0, 255 ,0)
    BLUE = (0, 0 ,255)

class DataTime():
    def __init__(self, data_time = int(0)) -> None:
        self.time_of_data = data_time
        self.passed_time = int(0)
        self.update_time()
    
    def __get_time(self) -> int:
        return round(time.time() * 1000)
    
    def update_time(self):
        self.passed_time = self.time_of_data - self.__get_time()

class graph_speed(pg.PlotItem):
    def __init__(self, parent=None, name=None, labels=None, title='Graph', viewBox=None, axisItems=None, enableMenu=True, **kargs):
        super().__init__(parent, name, labels, title, viewBox, axisItems, enableMenu, **kargs)
        
        self.addLegend()
        self.time_expiration = int(-5000) # 5 seconds

        self.__data_names = []
        self.__data_mutex: dict[str, Lock] = dict()
        self.__time_axis: dict(List[DataTime]) = dict()
        self.__value_axis: dict(List) = dict()
        self.__last_value: dict[str, int] = dict()

        self.value_plot = {}

        self.value_plot["MAX"] = self.plot(pen=(33, 33, 33), name = "MIN")
        self.value_plot["MIN"] = self.plot(pen=(33, 33, 33), name = "MAX")
        MAX = [[self.time_expiration, 500],[0, 500]]
        MIN = [[self.time_expiration, -500],[0, -500]]
        self.value_plot.get("MAX").setData([ x[0] for x in MAX ], [ x[1] for x in MAX])
        self.value_plot.get("MIN").setData([ x[0] for x in MIN ], [ x[1] for x in MIN])
    
    def add_axis(self, axis_name : str, color : COLOR):
        self.__data_names.append(axis_name)
        self.value_plot[axis_name] = self.plot(pen=color, name = axis_name)
        self.__data_mutex[axis_name] = Lock()
        self.__time_axis[axis_name] = []
        self.__value_axis[axis_name] = []
        self.__time_axis[axis_name] = []
        self.__last_value[axis_name] = 0
    
    def update(self):
        for data_name in self.__data_names:
            if len(self.__time_axis[data_name]):
                self.__data_mutex[data_name].acquire()
                self.__update_time()
                #self.__update_last_value()
                self.__clear_queue()

                time_axis = []
                for time_data in self.__time_axis[data_name]:
                    time_axis.append(time_data.passed_time)
                time_axis.append(0)

                value_axis = list(self.__value_axis[data_name])
                value_axis.append(self.__last_value[data_name])

                if len(self.__value_axis[data_name]) == 1:
                    print("!EMPTY!")
                    value_axis.append(self.__last_value[data_name])
                    time_axis.append(self.time_expiration)

                print(len(self.__value_axis[data_name]))
                print("time_axis: ", time_axis)
                print("value_axis: ", value_axis)
                self.value_plot.get(data_name).setData(time_axis, value_axis)
                self.__data_mutex[data_name].release()

    def __get_time(self):
        return round(time.time() * 1000)

    def add_data(self, value, axis : str, sent_time : int = 0):
        if axis in self.__data_names :
            if not sent_time:
                sent_time = self.__get_time()
        
            self.__data_mutex[axis].acquire()
            data_time = DataTime(sent_time)

            self.__value_axis[axis].append(self.__last_value[axis])
            self.__time_axis[axis].append(data_time)

            self.__value_axis[axis].append(value)
            self.__time_axis[axis].append(data_time)

            self.__last_value[axis] = value
    
            self.__data_mutex[axis].release()
        else:
            print("Axis: ", axis, " not found")

    def __clear_queue(self):
        for data_name in self.__data_names:
            if len(self.__time_axis[data_name]):
                time_now = self.__get_time()

                while (self.__time_axis[data_name][0].passed_time < self.time_expiration):
                    self.__time_axis[data_name].pop(0)
                    self.__value_axis[data_name].pop(0)
    
    def __update_time(self):
        for data_name in self.__data_names:
            if len(self.__time_axis[data_name]):
                for index in range(len(self.__time_axis[data_name])):
                    self.__time_axis[data_name][index].update_time()

    def __update_last_value(self):
        for data_name in self.__data_names:
            if len(self.__time_axis[data_name]):
                #self.add_data(self.__value_axis[data_name][-1], axis = data_name)
                self.__value_axis[data_name].append(self.__value_axis[data_name][-1])
                data_time = DataTime(sent_time)
                self.__time_axis[axis].append(data_time)