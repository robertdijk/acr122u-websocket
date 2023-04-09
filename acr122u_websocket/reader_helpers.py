import threading
from time import sleep
from typing import Callable, List

from acr122u_websocket.my_reader import MyReader, ReaderContainer


class NoCardReaderConnected(Exception):
    """
    Raised when there is no reader connected
    """

    pass


class CardReaderConnector(threading.Thread):
    """
    Thread that constantly polls the card reader
    by requesting a UUID, and tries to reconnect
    if the request fails.
    """

    def __init__(self, card_reader_container: ReaderContainer):
        super().__init__()
        self._card_reader_container = card_reader_container

    def run(self):
        while True:
            # While it is not connected, try to connect
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

            # If it is connected, see if it is still connected
            if self._card_reader_container.reader is not None:
                try:
                    self._card_reader_container.reader.get_uid()
                except Exception as e:
                    print(e)
                    self._card_reader_container.reader = None

            sleep(1)


class CardReaderPoller(threading.Thread):
    """
    Thread to poll the card reader for UUIDs.
    It supports a callback function that is called
    when a UUID is scanned.
    """

    def __init__(
        self,
        card_reader_container: ReaderContainer,
        uuid_callback: Callable[[List[int]], None],
    ):
        """
        Initiate a new thread.

        :param card_reader_container: The card reader connection and lock
        :type card_reader_container: ReaderContainer
        :param uuid_callback: A callback for when a UUID is scanned. It will be
            called with a List of integers that represent the UUID.
        :type uuid_callback: Callable[[List[int]], None]
        """
        super().__init__()
        self._card_reader_container = card_reader_container
        self._uuid_callback = uuid_callback
        self._polling: bool = False
        self._current_uuid = None
        self._last_uuid = None

    def run(self) -> None:
        while True:
            while self._card_reader_container.reader is not None:
                if self._polling:
                    try:
                        with self._card_reader_container.lock:
                            self._current_uuid = (
                                self._card_reader_container.reader.read_uuid()
                            )

                            if (
                                self._current_uuid is not None
                                and self._current_uuid != self._last_uuid
                            ):
                                self._card_reader_container.reader.scanned_beep()
                                self._uuid_callback(self._current_uuid)

                            self._last_uuid = self._current_uuid
                    except Exception as e:
                        print(e)
                sleep(0.05)
            sleep(1)

    def start_polling(self) -> None:
        """
        Start the polling.
        If the polling was not already started, it will turn on the
        green light, and start the polling.
        """
        if self._polling:
            return

        self._current_uuid = None
        self._last_uuid = None

        with self._card_reader_container.lock:
            if self._card_reader_container.reader is None:
                raise NoCardReaderConnected()
            self._card_reader_container.reader.green_light_on()

        self._polling = True

    def stop_polling(self) -> None:
        """
        Stop the polling.
        If the polling was not already stopped, it will turn off the
        green light, and stop the polling.
        """
        if not self._polling:
            return

        with self._card_reader_container.lock:
            if self._card_reader_container.reader is None:
                raise NoCardReaderConnected()
            self._card_reader_container.reader.reset_lights()

        self._polling = False

        self._current_uuid = None
        self._last_uuid = None

    def is_polling(self) -> bool:
        """
        Returns true iff the poller is polling.
        :return: true iff the poller is polling
        :rtype: bool
        """
        return self._polling
