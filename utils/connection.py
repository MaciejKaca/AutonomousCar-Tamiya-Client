import queue
import socket
import threading
import time
from threading import Lock
from autonomousCarConnection.messages import DataMessage, Heartbeat, deserialize_message, MessageType, SpeedData, \
    CurrentData


class ConnectionMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Connection(metaclass=ConnectionMeta):
    def __init__(self) -> None:
        self.__IS_CLIENT = False
        self.__CAR_SYSTEM_ID = 111
        self.__CLIENT_SYSTEM_ID = 222
        self.__HEARTBEAT_HZ = 1
        self.__UDPSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.__CLIENT_ADDRESS = "192.168.0.122"
        self.__CAR_ADDRESS = "192.168.0.115"
        self.__LOCAL_PORT = 5555
        self.__bufferSize = 1024
        self.__isConnected = False
        self.__messageSendQueue = queue.Queue()
        self.__keepRunning = True
        self.__lastHeartbeatTime = 0
        self.__HEARTBEAT_TIMEOUT = 2000  # 2 seconds
        self.__HEARTBEAT_MONITOR_REFRESH_TIME = 2  # 2 seconds

        self.__UDPSocket.bind((self.__CLIENT_ADDRESS, self.__LOCAL_PORT))
        self.__heartbeatMutex = Lock()

        # Queues for widgets
        self.__incomingSpeedGraphData = queue.Queue()
        self.__incomingCurrentGraphData = queue.Queue()

        self.__receiveThread = threading.Thread(target=self.__receive, args=(), daemon=True)
        self.__sendThread = threading.Thread(target=self.__send, args=(), daemon=True)
        self.__heartbeatThread = threading.Thread(target=self.__send_heartbeat, args=(), daemon=True)
        self.__monitorHeartbeatThread = threading.Thread(target=self.__monitor_heartbeat, args=(), daemon=True)
        self.__receiveThread.start()
        self.__sendThread.start()
        self.__heartbeatThread.start()
        self.__monitorHeartbeatThread.start()

    def __del__(self):
        self.__UDPSocket.close()
        self.__isConnected = False
        self.__keepRunning = False
        self.__receiveThread.join()
        self.__sendThread.join()
        self.__heartbeatThread.join()

    def add_to_queue(self, message: DataMessage):
        self.__messageSendQueue.put(message.serialize())

    def __send(self):
        while self.__keepRunning:
            message = self.__messageSendQueue.get()
            bytes_to_send = str.encode(message)
            self.__UDPSocket.sendto(bytes_to_send, (self.__CAR_ADDRESS, self.__LOCAL_PORT))

    def __receive(self):
        while self.__keepRunning:
            message = self.__UDPSocket.recvfrom(self.__bufferSize)
            data = deserialize_message(message[0])
            self.__handle_message(data)

    def __handle_message(self, message: DataMessage):
        if message.messageType == MessageType.HEARTBEAT:
            heartbeat: Heartbeat = message
            if heartbeat.systemID.value == self.__CAR_SYSTEM_ID:
                self.__heartbeatMutex.acquire()
                self.__lastHeartbeatTime = self.__get_time()
                self.__heartbeatMutex.release()

        elif message.messageType == MessageType.SPEED:
            self.__incomingSpeedGraphData.put(message)

        elif message.messageType == MessageType.CURRENT:
            self.__incomingCurrentGraphData.put(message)

    def __send_heartbeat(self):
        while self.__keepRunning:
            heartbeat = Heartbeat()
            heartbeat.systemID.value = self.__CLIENT_SYSTEM_ID
            self.add_to_queue(heartbeat)
            time.sleep(self.__HEARTBEAT_HZ)

    def __monitor_heartbeat(self):
        while self.__keepRunning:
            self.__heartbeatMutex.acquire()
            if (self.__get_time() - self.__lastHeartbeatTime) < self.__HEARTBEAT_TIMEOUT:
                if not self.__isConnected:
                    print("Connected to client")
                self.__isConnected = True
            else:
                if self.__isConnected:
                    print("Car disconnected")
                self.__isConnected = False
            self.__heartbeatMutex.release()
            time.sleep(self.__HEARTBEAT_MONITOR_REFRESH_TIME)

    @staticmethod
    def __get_time() -> int:
        return round(time.time() * 1000)

    def is_car_connected(self) -> bool:
        self.__heartbeatMutex.acquire()
        is_connected = self.__isConnected
        self.__heartbeatMutex.release()
        return is_connected

    def get_speed_data(self) -> SpeedData:
        return self.__incomingSpeedGraphData.get()

    def get_current_data(self) -> CurrentData:
        return self.__incomingCurrentGraphData.get()
