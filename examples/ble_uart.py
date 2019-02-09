from gi.repository import GLib
from evdev import InputDevice, categorize, ecodes

# Bluezero modules
from bluezero import peripheral

# constants
UART_SERIVCE = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
RX_CHARACTERISTIC = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
TX_CHARACTERISTIC = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'


class UartService:
    def __init__(self):
        self.app = peripheral.Application()
        self.ble_uart = peripheral.Service(UART_SERIVCE,
                                           True)
        self.rx_uart = peripheral.Characteristic(RX_CHARACTERISTIC,
                                                 ['write',
                                                  'write-without-response'],
                                                 self.ble_uart)
        self.tx_uart = peripheral.Characteristic(TX_CHARACTERISTIC,
                                                 ['notify'],
                                                 self.ble_uart)
        self.rx_uart.add_write_event(self.uart_print)
        self.tx_uart.add_notify_event(print)
        self.tx_uart.StartNotify()
        self.ble_uart.add_characteristic(self.rx_uart)
        self.ble_uart.add_characteristic(self.tx_uart)
        self.app.add_service(self.ble_uart)

    @staticmethod
    def _from_bytes(data):
        return ''.join(chr(letter) for letter in data)

    @staticmethod
    def _to_bytes(word):
        return [ord(x) for x in word]

    def uart_print(self, value):
        print(self._from_bytes(value))

    def start(self):
        self.app.start()

    def stop(self):
        self.app.stop()


def detect_keys(dev_loop):
    event = dev.read_one()
    if event is not None:
        if event.code == ecodes.KEY_DOWN and event.value == 1:
            dev_loop.tx_uart.send_notify_event('down')
        elif event.code == ecodes.KEY_UP and event.value == 1:
            dev_loop.tx_uart.send_notify_event('up')
        elif event.code == ecodes.KEY_LEFT and event.value == 1:
            dev_loop.tx_uart.send_notify_event('left')
        elif event.code == ecodes.KEY_RIGHT and event.value == 1:
            dev_loop.tx_uart.send_notify_event('right')
        elif event.code == ecodes.KEY_ENTER and event.value == 1:
            dev_loop.disconnect()
            dev_loop.stop()
    return True


if __name__ == '__main__':
    dev = InputDevice('/dev/input/event0')
    uart = UartService()
    uart.app.dongle.alias = 'RPi_UART'
    GLib.idle_add(detect_keys, uart)
    uart.start()
