from graphs.base_data_graph import *
from autonomousCarConnection.messages import CurrentData


class CurrentGraph(BaseDataGraph):
    def __init__(self, parent=None, name=None, labels=None, title='Graph', view_box=None, axis_items=None,
                 enable_menu=True, **kargs):
        super().__init__(parent, name, labels, title, view_box, axis_items, enable_menu, **kargs)

        self.addLegend()
        self._timeExpiration = int(-6000)  # 6 seconds

        self.setXRange(-5000, 0, padding=0)  # 5 seconds
        self.setYRange(9, 6, padding=0)

        self.__updateFromSocketThread: Thread = Thread(target=self.__update_from_socket, args=(), daemon=True)

        self.add_axis("voltage", Color.GREEN)
        self.add_axis("minimum_voltage", Color.RED)
        self.add_data(0, axis="voltage")
        self.add_data(6.6, axis="minimum_voltage")

        self.last_current = 0.0

    def start_graph(self):
        super().start_graph()
        self.__updateFromSocketThread.start()

    def __update_from_socket(self):
        while True:
            data: CurrentData = self._connection.get_current_data()
            current = data.voltage.value
            self.add_data(value=current, axis="voltage")
            self.last_current = current

    def get_last_current(self):
        return self.last_current
