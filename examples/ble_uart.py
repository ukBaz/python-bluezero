from gi.repository import GLib

# Bluezero modules
from bluezero import adapter
from bluezero import peripheral
from bluezero import device

# constants
UART_SERVICE = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
RX_CHARACTERISTIC = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
TX_CHARACTERISTIC = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'


class UARTDevice:
    tx_obj = None

    @classmethod
    def on_connect(cls, ble_device: device.Device):
        print("Connected to " + str(ble_device.address))

    @classmethod
    def on_disconnect(cls, adapter_address, device_address):
        print("Disconnected from " + device_address)

    @classmethod
    def uart_notify(cls, notifying, characteristic):
        if notifying:
            cls.tx_obj = characteristic
        else:
            cls.tx_obj = None

    @classmethod
    def update_tx(cls, value):
        if cls.tx_obj:
            print("Sending")
            cls.tx_obj.set_value(value)

    @classmethod
    def uart_write(cls, value, options):
        print('raw bytes:', value)
        print('With options:', options)
        print('Text value:', bytes(value).decode('utf-8'))
        cls.update_tx(value)


def main(adapter_address):
    ble_uart = peripheral.Peripheral(adapter_address, local_name='BLE UART')
    ble_uart.add_service(srv_id=1, uuid=UART_SERVICE, primary=True)
    ble_uart.add_characteristic(srv_id=1, chr_id=1, uuid=RX_CHARACTERISTIC,
                                value=[], notifying=False,
                                flags=['write', 'write-without-response'],
                                write_callback=UARTDevice.uart_write,
                                read_callback=None,
                                notify_callback=None)
    ble_uart.add_characteristic(srv_id=1, chr_id=2, uuid=TX_CHARACTERISTIC,
                                value=[], notifying=False,
                                flags=['notify'],
                                notify_callback=UARTDevice.uart_notify,
                                read_callback=None,
                                write_callback=None)

    ble_uart.on_connect = UARTDevice.on_connect
    ble_uart.on_disconnect = UARTDevice.on_disconnect

    ble_uart.publish()


if __name__ == '__main__':
    main(list(adapter.Adapter.available())[0].address)
