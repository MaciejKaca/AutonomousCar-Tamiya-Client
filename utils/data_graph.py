import matplotlib.pyplot as plt
import numpy as np
import time
from threading import Lock, Thread

class DataGraph:
    def __init__(self, name : str) -> None:
        self.time_expiration = int(10000) # 10 seconds

        self.__time_axis = []
        self.__value_axis = []

        self.__data_mutex = Lock()

        self.__keep_running = True
        # self.fig, self.data_graph = plt.subplots()
        # self.data_graph.plot(self.__time_axis, self.__value_axis)
        # self.data_graph.set_title(name)

        plt.ion()
        plt.show()

        self.__graph_thread = Thread(target=self.__display_routine, args=(), daemon=True)
        self.__graph_thread.start()

    def __get_time(self):
        return round(time.time() * 1000)
    
    def __clear_queue(self):
        while True:
            self.__data_mutex.acquire()
            if len(self.__time_axis):
                time_now = self.__get_time()
                if (time_now - self.__time_axis[0]) < self.time_expiration:
                    self.__time_axis.pop(0)
                    self.__value_axis.pop(0)
                    self.__data_mutex.release()
                else:
                    self.__data_mutex.release()
                    break
    
    def add_data(self, sent_time : int, value):
        self.__data_mutex.acquire()
        self.__time_axis.append(self.__get_time() - sent_time)
        self.__value_axis.append(value)
        self.__data_mutex.release()
    
    def __display_routine(self):
        while self.__keep_running:
            self.__data_mutex.acquire()
            plt.plot(self.__time_axis, self.__value_axis)
            self.__data_mutex.release()
            plt.draw()
            self.__clear_queue()
            plt.pause(0.1)

