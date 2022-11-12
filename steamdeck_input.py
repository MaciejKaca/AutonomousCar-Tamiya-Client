from multiprocessing import Event
import pygame

import threading
from threading import Lock
from queue import Queue
import time
from utils.connection import Connection
from autonomousCarConnection.messages import JoystickData

pygame.init()
pygame.joystick.init()


def get_count():
    return pygame.joystick.get_count()


def get_controller(x):
    count = pygame.joystick.get_count()
    if count == 0:
        print("no joysticks connected")
        return None
    elif x < count:
        return Joystick(pygame.joystick.Joystick(x))
    else:
        print("Joystick " + str(x) + " not connected")
        print("choose joystick from 0 to " + str(count - 1))
        return None


class Joystick:
    def __init__(self, controller):
        self.__socket = Connection()
        self.__keepRunning = True
        self.__keepRunning_mutex = Lock()

        self.__BUTTON_DOWN = True
        self.__BUTTON_UP = False

        self.__AXIS_EVENT = 1536
        self.__BUTTON_UP_EVENT = 1540
        self.__BUTTON_DOWN_EVENT = 1539
        self.__START_BUTTON = 7

        self.__button_state = {self.__START_BUTTON: self.__BUTTON_UP}

        self.__event_queue = Queue()

        self.__controller = controller
        self.__controller.init()
        self.__pad_thread = threading.Thread(target=self.__handle_events, args=(), daemon=True)
        self.__pad_thread.start()

    def __del__(self):
        self.__keepRunning = False
        self.__pad_thread.join()

    def __handle_button(self, event: Event):
        button = event.__dict__.get('button')

        if button == self.__START_BUTTON:
            self.__keepRunning_mutex.acquire()
            self.__keepRunning = False
            self.__keepRunning_mutex.release()

    def was_exit_pressed(self) -> bool:
        self.__keepRunning_mutex.acquire()
        temp_value = self.__keepRunning
        self.__keepRunning_mutex.release()
        return not temp_value

    def __handle_events(self):
        while not self.was_exit_pressed():
            for event in pygame.event.get():
                if event.type == self.__AXIS_EVENT or event.type == self.__BUTTON_DOWN_EVENT or \
                        event.type == self.__BUTTON_UP_EVENT:
                    message = JoystickData()
                    message.eventType = event.type
                    if event.type == self.__AXIS_EVENT:
                        message.axis = event.__dict__.get('axis')
                        message.value = event.__dict__.get('value')

                    if event.type != self.__AXIS_EVENT:
                        button = event.__dict__.get('button')
                        message.button = button
                        is_pressed = (event.type == self.__BUTTON_DOWN_EVENT)
                        self.__button_state[button] = bool(is_pressed)
                        self.__handle_button(event)

                    self.__socket.add_to_queue(message)
            time.sleep(0.01)  # 10ms

    def add_event(self, message: JoystickData):
        self.__event_queue.put(message)
