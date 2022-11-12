from graphs.BaseDataGraph import *
from autonomousCarConnection.messages import SpeedData, Direction


class SpeedGraph(BaseDataGraph):
    def __init__(self, parent=None, name=None, labels=None, title='Graph', view_box=None, axis_items=None,
                 enable_menu=True, **kargs):
        super().__init__(parent, name, labels, title, view_box, axis_items, enable_menu, **kargs)

        self.addLegend()
        self._timeExpiration = int(-6000)  # 6 seconds

        self.setXRange(-5000, 0, padding=0)  # 5 seconds
        self.setYRange(500, -500, padding=0)

        self.__updateFromSocketThread: Thread = Thread(target=self.__update_from_socket, args=(), daemon=True)

    def start_graph(self):
        super().start_graph()
        self.__updateFromSocketThread.start()

    def __update_from_socket(self):
        while True:
            data: SpeedData = self._connection.get_speed_data()
            if data.direction == Direction.BACKWARD:
                self.add_data(value=-data.speed, axis="speed")
            elif data.direction == Direction.FORWARD:
                self.add_data(value=data.speed, axis="speed")
            elif data.direction == Direction.BRAKE:
                self.add_data(value=data.speed, axis="brake")
