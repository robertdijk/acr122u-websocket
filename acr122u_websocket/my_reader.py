import dataclasses
import threading
from typing import Optional, List

import smartcard.Exceptions
from py_acr122u.nfc import Reader


class MyReader(Reader):
    """
    An extension on the Reader class from py_acr122u, to add
    some project-specific features.
    """

    def __init__(self):
        super().__init__()

    def apply_settings(self) -> None:
        """
        Disable auto-polling so that we can control the lights and
        the buzzer separately.
        Also, disable the buzzer and turn off the lights.
        """
        self.set_auto_polling(False)
        self.mute_buzzer()
        self.reset_lights()

    def green_light_on(self) -> None:
        """
        Turn on the green light.
        """
        self.led_control(0b00001010, 0, 0, 0, 0)

    def red_light_on(self) -> None:
        """
        Turn on the red light.
        """
        self.led_control(0b00000101, 0, 0, 0, 0)

    def scanned_beep(self) -> None:
        """
        Give one beep with a green blink.
        """
        self.led_control(0b10000000, 1, 0, 1, 0x01)

    def error_beep(self) -> None:
        """
        Give one long beep with 3 red flashes.
        """
        self.led_control(0b01010000, 2, 2, 3, 0x03)

    def confirm_beep(self) -> None:
        """
        Give 2 short beeps with a green blinking light.
        """
        self.led_control(0b10100000, 1, 1, 2, 0x01)

    def read_uuid(self) -> Optional[List[int]]:
        """
        Poll for a UUID using the PN532 Auto Poll function.

        :return: the UUID in the form of a List of integers
            or None is no UUID can be found.
        :rtype: Optional[List[int]]
        """
        try:
            data = self.pn532.in_auto_poll(0x05, 0x01, 0x10)
            if len(data) < 5:
                return None
            length = data[9]
            uuid = data[10 : 10 + length]
            return uuid
        except smartcard.Exceptions.CardConnectionException:
            return None


@dataclasses.dataclass
class ReaderContainer:
    """
    A classing containing a reader and a lock.
    """

    lock: threading.Lock = dataclasses.field(default_factory=threading.Lock)
    reader: Optional[MyReader] = None
