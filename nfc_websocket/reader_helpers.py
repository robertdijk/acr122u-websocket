import threading
from time import sleep
from typing import Callable, List

from nfc_websocket.my_reader import MyReader, ReaderContainer


class NoCardReaderConnected(Exception):
    pass


class CardReaderConnector(threading.Thread):
    def __init__(self, card_reader_container: ReaderContainer):
        super().__init__()
        self._card_reader_container = card_reader_container

    def run(self):
        while True:
            while self._card_reader_container.reader is None:
                try:
                    with self._card_reader_container.lock:
                        self._card_reader_container.reader = MyReader()
                        self._card_reader_container.reader.connect()
                        self._card_reader_container.reader.apply_settings()
                except Exception as e:
                    print(e)
                    self._card_reader_container.reader = None
                sleep(0.1)
            if self._card_reader_container.reader is not None:
                try:
                    self._card_reader_container.reader.get_uid()
                except Exception as e:
                    print(e)
                    self._card_reader_container.reader = None
            sleep(1)


class CardReaderPoller(threading.Thread):
    def __init__(self, card_reader_container: ReaderContainer, uuid_callback: Callable[[List[int]], None]):
        super().__init__()
        self._card_reader_container = card_reader_container
        self._uuid_callback = uuid_callback
        self._polling: bool = False
        self._current_uuid = None
        self._last_uuid = None

    def run(self):
        while True:
            while self._card_reader_container.reader is not None:
                if self._polling:
                    try:
                        with self._card_reader_container.lock:
                            self._current_uuid = self._card_reader_container.reader.read_uuid()

                            if self._current_uuid is not None and self._current_uuid != self._last_uuid:
                                self._card_reader_container.reader.scanned_beep()
                                self._uuid_callback(self._current_uuid)

                            self._last_uuid = self._current_uuid
                    except Exception as e:
                        print(e)
                sleep(0.05)
            sleep(1)

    def start_polling(self):
        if self._polling:
            return

        self._current_uuid = None
        self._last_uuid = None

        with self._card_reader_container.lock:
            if self._card_reader_container.reader is None:
                raise NoCardReaderConnected()
            self._card_reader_container.reader.green_light_on()

        self._polling = True

    def stop_polling(self):
        if not self._polling:
            return

        with self._card_reader_container.lock:
            if self._card_reader_container.reader is None:
                raise NoCardReaderConnected()
            self._card_reader_container.reader.reset_lights()

        self._polling = False

        self._current_uuid = None
        self._last_uuid = None
