from bluezero import GATT
from bluezero import localGATT
from bluezero import advertisement
from bluezero import adapter
from bluezero import tools
import dbus
from blinkt import set_pixel, set_all, show

WEB_BLINKT = 'https://goo.gl/wQOjbe'
TX_POWER = 0x08
EDDYSTONE = 'FEAA'
SERVICE_UUID = '0000FFF0-0000-1000-8000-00805F9B34FB'
CHAR_UUID = '0000FFF3-0000-1000-8000-00805F9B34FB'


class blinkt:
    def __init__(self, ble):
        self.ble = ble

    def on_ble_write(self, *args, **kwargs):
        try:
            # bytes=[0x07, 0x02, 0x00, 0x01, 0x00, 0x0FF, 0x00]
            bytes = args[1]["Value"]
            if len(bytes) > 2:
                cmd = (bytes[0] << 8) + (bytes[1] & 0xff)

                if cmd == 0x0702:
                    if len(bytes) >= 7:
                        set_pixel(bytes[3] - 1, bytes[4], bytes[5], bytes[6])
                elif cmd == 0x0601:
                    if len(bytes) >= 5:
                        set_all(bytes[2], bytes[3], bytes[4])
                show()
        except Exception as inst:
            print(type(inst))
            print(inst.args)
            print(inst)
        return 0


class ble:
    def __init__(self):
        self.bus = dbus.SystemBus()
        self.app = localGATT.Application()
        self.srv = localGATT.Service(1, SERVICE_UUID, True)

        self.charc = localGATT.Characteristic(1,
                                              CHAR_UUID,
                                              self.srv,
                                              [0xBB],
                                              True,
                                              ['write'])

        self.charc.service = self.srv.path
        self.app.add_managed_object(self.srv)
        self.app.add_managed_object(self.charc)

        self.srv_mng = GATT.GattManager(adapter.list_adapters()[0])
        self.srv_mng.register_application(self.app, {})

        self.dongle = adapter.Adapter(adapter.list_adapters()[0])
        advert = advertisement.Advertisement(1, 'peripheral')

        advert.service_UUIDs = [SERVICE_UUID]
        eddystone_data = tools.url_to_advert(WEB_BLINKT, 0x10, TX_POWER)
        advert.service_data = {EDDYSTONE: eddystone_data}
        if not self.dongle.powered:
            self.dongle.powered = True
        ad_manager = advertisement.AdvertisingManager(self.dongle.path)
        ad_manager.register_advertisement(advert, {})

    def add_call_back(self, callback):
        self.charc.PropertiesChanged = callback

    def start_bt(self):
        # self.light.StartNotify()
        tools.start_mainloop()


if __name__ == '__main__':
    link = ble()
    blinkt_ble = blinkt(link)
    link.charc.add_call_back(blinkt_ble.on_ble_write)

    link.start_bt()
