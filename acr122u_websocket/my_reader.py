import dataclasses
import threading
from typing import Optional, List

import smartcard.Exceptions
from py_acr122u.nfc import Reader


class MyReader(Reader):
    def __init__(self):
        super().__init__()

    def apply_settings(self):
        self.set_auto_polling(False)
        self.mute_buzzer()
        self.reset_lights()

    def green_light_on(self):
        self.led_control(0b00001010, 0, 0, 0, 0)

    def red_light_on(self):
        self.led_control(0b00000101, 0, 0, 0, 0)

    def scanned_beep(self):
        self.led_control(0b10000000, 1, 0, 1, 0x01)

    def error_beep(self):
        self.led_control(0b01010000, 2, 2, 3, 0x03)

    def confirm_beep(self):
        self.led_control(0b10100000, 1, 1, 2, 0x01)

    def read_uuid(self) -> Optional[List[int]]:
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
    lock: threading.Lock = dataclasses.field(default_factory=threading.Lock)
    reader: Optional[MyReader] = None
