from bluezero import GATT
from bluezero import localGATT
from bluezero import advertisement
from bluezero import adapter
from bluezero import tools
from bluezero import constants

import dbus

from gpiozero import LED
from gpiozero import Button
from time import sleep
from signal import pause

SERVICE_UUID = '12341000-1234-1234-1234-123456789abc'
LIGHT_UUID = '12341002-1234-1234-1234-123456789abc'
SWITCH_UUID = '12341004-1234-1234-1234-123456789abc'


class board:
    def __init__(self, ble):
        self.led = LED(22)
        self.button = Button(25)
        self.ble = ble

    def switch_led(self, *args, **kwargs):
        print(self.led.is_lit, args, kwargs)
        if self.led.is_lit:
            self.led.off()
            self.ble.light.Set(constants.GATT_CHRC_IFACE, 'Value', [0x00])
        else:
            self.led.on()
            self.ble.light.Set(constants.GATT_CHRC_IFACE, 'Value', [0x01])


class ble:
    def __init__(self):
        self.bus = dbus.SystemBus()
        self.app = localGATT.Application()
        self.srv = localGATT.Service(1, SERVICE_UUID, True)
        self.light = localGATT.Characteristic(1,
                                              LIGHT_UUID,
                                              self.srv,
                                              [0xAA],
                                              True,
                                              ['read', 'notify'])
        self.switch = localGATT.Characteristic(2,
                                               SWITCH_UUID,
                                               self.srv,
                                               [0xBB],
                                               True,
                                               ['read', 'write', 'notify'])

        self.light.service = self.srv.path
        self.app.add_managed_object(self.srv)
        self.app.add_managed_object(self.light)
        self.app.add_managed_object(self.switch)

        self.srv_mng = GATT.GattManager(adapter.list_adapters()[0])
        self.srv_mng.register_application(self.app, {})

        self.dongle = adapter.Adapter(adapter.list_adapters()[0])
        advert = advertisement.Advertisement(1, 'peripheral')
        advert.service_UUIDs = [SERVICE_UUID]
        if not self.dongle.powered:
            self.dongle.powered = True
        ad_manager = advertisement.AdvertisingManager(self.dongle.path)
        ad_manager.register_advertisement(advert, {})

    def add_call_back(self, callback):
        self.switch.PropertiesChanged = callback

    def start_bt(self):
        # self.light.StartNotify()
        tools.start_mainloop()


if __name__ == '__main__':
    link = ble()
    hat = board(link)
    hat.button.when_pressed = hat.switch_led
    link.switch.add_call_back(hat.switch_led)

    link.start_bt()
