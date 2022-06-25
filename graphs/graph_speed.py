from typing import Dict, List
import pyqtgraph as pg
import numpy as np
from enum import Enum
from threading import Thread, Lock
import time

COLORS = [ (255, 0 ,0), (0, 255 ,0), (0, 0 ,255)]

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
    def __init__(self, parent=None, name=None, labels=None, title='Graph', viewBox=None, axisItems=None, enableMenu=True, data_names: List[str] = ["default"], **kargs):
        super().__init__(parent, name, labels, title, viewBox, axisItems, enableMenu, **kargs)
        
        self.time_expiration = int(-5000) # 10 seconds

        self.__data_names = data_names
        self.__data_mutex: dict[str, Lock] = dict()
        self.__time_axis: dict(List[DataTime]) = dict()
        self.__value_axis: dict(List) = dict()

        self.value_plot = {}
        for data_name in self.__data_names:
            self.value_plot[data_name] = self.plot(pen=COLORS[len(self.value_plot)], name = data_name)
            self.__data_mutex[data_name] = Lock()
            self.__time_axis[data_name] = []
            self.__value_axis[data_name] = []
            self.__time_axis[data_name] = []

    def update(self):
        for data_name in self.__data_names:
            if len(self.__time_axis[data_name]):
                self.__update_time()
                self.__update_last_value()
                self.__clear_queue()

                time_axis = []
                for time_data in self.__time_axis[data_name]:
                    time_axis.append(time_data.passed_time)

                self.value_plot.get(data_name).setData(time_axis, self.__value_axis[data_name])

    def __get_time(self):
        return round(time.time() * 1000)

    def add_data(self, value, sent_time : int = 0, axis = ""):
        if not axis:
            axis = self.__data_names[0]

        if not sent_time:
            sent_time = self.__get_time()
    
        self.__data_mutex[axis].acquire()
        self.__value_axis[axis].append(value)
        data_time = DataTime(sent_time)

        self.__time_axis[axis].append(data_time)
        self.__data_mutex[axis].release()

    def __clear_queue(self):
        for data_name in self.__data_names:
            self.__data_mutex[data_name].acquire()
            if len(self.__time_axis[data_name]):
                time_now = self.__get_time()

                while (self.__time_axis[data_name][0].passed_time < self.time_expiration):
                    self.__time_axis[data_name].pop(0)
                    self.__value_axis[data_name].pop(0)
                self.__data_mutex[data_name].release()
    
    def __update_time(self):
        for data_name in self.__data_names:
            self.__data_mutex[data_name].acquire()
            if len(self.__time_axis[data_name]):
                for index in range(len(self.__time_axis[data_name])):
                    self.__time_axis[data_name][index].update_time()
            self.__data_mutex[data_name].release()

    def __update_last_value(self):
        for data_name in self.__data_names:
            if len(self.__time_axis[data_name]):
                self.add_data(self.__value_axis[data_name][-1], axis = data_name)