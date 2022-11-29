from typing import Dict, List
import pyqtgraph as pg
from threading import Thread, Lock
import time
from utils.connection import Connection
from utils.colors import Color


class DataTime:
    def __init__(self, data_time=int(0)) -> None:
        self.timeOfData = data_time
        self.passedTime = int(0)
        self.update_time()

    @staticmethod
    def get_time() -> int:
        return round(time.time() * 1000)

    def update_time(self):
        self.passedTime = self.timeOfData - self.get_time()


class BaseDataGraph(pg.PlotItem):
    def __init__(self, parent=None, name=None, labels=None, title='Graph', view_box=None, axis_items=None,
                 enable_menu=True, **kargs):
        super().__init__(parent, name, labels, title, view_box, axis_items, enable_menu, **kargs)

        self.addLegend()
        self._timeExpiration = int(-5000)  # 5 seconds

        self.__dataNames = []
        self.__dataMutex: Dict[str, Lock] = dict()
        self.__timeAxis: Dict[str, List: DataTime] = dict()
        self.__valueAxis: Dict[str, List] = dict()
        self.__lastValue: Dict[str, int] = dict()

        self.__valuePlot = {}

        self._connection: Connection = Connection()

        self.__updateThread = Thread(target=self.update, args=(), daemon=True)

    def start_graph(self):
        self.__updateThread.start()

    def add_axis(self, axis_name: str, color: Color):
        self.__dataNames.append(axis_name)
        self.__valuePlot[axis_name] = self.plot(pen=color, name=axis_name)
        self.__dataMutex[axis_name] = Lock()
        self.__timeAxis[axis_name] = []
        self.__valueAxis[axis_name] = []
        self.__timeAxis[axis_name] = []
        self.__lastValue[axis_name] = 0

    def update_from_socket(self):
        pass

    def draw_graph(self):
        self.update()

        for data_name in self.__dataNames:
            self.__dataMutex[data_name].acquire()
            time_axis = []

            for time_data in self.__timeAxis[data_name]:
                time_axis.append(time_data.passedTime)

            value_axis = list(self.__valueAxis[data_name])
            self.__valuePlot.get(data_name).setData(time_axis, value_axis)
            self.__dataMutex[data_name].release()

    def update(self):
        for data_name in self.__dataNames:
            self.__dataMutex[data_name].acquire()
            self.__update_time()
            self.__update_last_value()
            self.__clear_queue()
            self.__dataMutex[data_name].release()

    def add_data(self, value, axis: str, sent_time: int = 0):
        if axis in self.__dataNames:
            if not sent_time:
                sent_time = DataTime.get_time()

            self.__dataMutex[axis].acquire()
            data_time = DataTime(sent_time)

            if len(self.__valueAxis[axis]):
                self.__valueAxis[axis].append(self.__valueAxis[axis][-1])
                self.__timeAxis[axis].append(data_time)

            self.__valueAxis[axis].append(value)
            self.__timeAxis[axis].append(data_time)

            self.__lastValue[axis] = value

            self.__dataMutex[axis].release()
        else:
            print("Axis: ", axis, " not found")

    def __clear_queue(self):
        for data_name in self.__dataNames:
            if len(self.__timeAxis[data_name]):
                while self.__timeAxis[data_name][0].passedTime < self._timeExpiration:
                    self.__timeAxis[data_name].pop(0)
                    self.__valueAxis[data_name].pop(0)

    def __update_time(self):
        for data_name in self.__dataNames:
            if len(self.__timeAxis[data_name]):
                for index in range(len(self.__timeAxis[data_name])):
                    self.__timeAxis[data_name][index].update_time()

    def __update_last_value(self):
        for data_name in self.__dataNames:
            if len(self.__timeAxis[data_name]):
                self.__valueAxis[data_name].append(self.__valueAxis[data_name][-1])
                self.__timeAxis[data_name].append(DataTime(DataTime.get_time()))
