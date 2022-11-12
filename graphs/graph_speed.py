from graphs.data_graph import *
from utils.connection import Connection
from autonomousCarConnection.messages import SpeedData, Direction

class SpeedGraph(DataGraph):
    def __init__(self, parent=None, name=None, labels=None, title='Graph', viewBox=None, axisItems=None, enableMenu=True, **kargs):
        super().__init__(parent, name, labels, title, viewBox, axisItems, enableMenu, **kargs)

        self.addLegend()
        self.time_expiration = int(-6000) # 6 seconds

        self.setXRange(-5000, 0, padding=0) # 5 seconds
        self.setYRange(500, -500, padding=0)

        self.__update_from_socket_thread : Thread = Thread(target=self.update_from_socket, args=(), daemon=True)

    def start_graph(self):
        super().start_graph()
        self.__update_from_socket_thread.start()

    def update_from_socket(self):
        while(True):
            data : SpeedData = self.connection.incoming_speed_data.get()
            print(data.serialize())
            if data.direction == Direction.BACKWARD:
                self.add_data(-data.speed, axis="speed")
            elif data.direction == Direction.FORWARD:
                self.add_data(data.speed, axis="speed")
            elif data.direction == Direction.BRAKE:
                self.add_data(data.speed, axis="brake")