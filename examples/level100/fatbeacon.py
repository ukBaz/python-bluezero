
from bluezero import tools
from bluezero import constants
from bluezero import adapter
from bluezero import advertisement
from bluezero import localGATT
from bluezero import GATT


FAT_SERVICE = 'AE5946D4-E587-4BA8-B6A5-A97CCA6AFFD3'
HTML_CHRC = 'D1A517F0-2499-46CA-9CCC-809BC1C966FA'


def advertise_beacon():
    dongle = adapter.Adapter('/org/bluez/hci0')

    advertiser0 = advertisement.Advertisement(0, 'peripheral')

    advertiser0.Set(constants.LE_ADVERTISEMENT_IFACE,
                    'ServiceData',
                    {'FEAA': [0x10, 0x08, 0x0E, 70, 97, 116, 79, 110, 101]})

    advertiser0.Set(constants.LE_ADVERTISEMENT_IFACE,
                    'ServiceUUIDs',
                    ['FEAA'])

    if not dongle.powered():
        dongle.powered(True)
    ad_manager = advertisement.AdvertisingManager(dongle.adapter_path)
    ad_manager.register_advertisement(advertiser0, {})

    return ad_manager, advertiser0


def build_fat_service():
    # value_string = '<html><head><title></title>
    #                   </head><body>Fat beacon</body></html>'
    value_string = [60, 104, 116, 109, 108, 62, 60, 104, 101, 97, 100, 62,
                    60, 116, 105, 116, 108, 101, 62, 60, 47, 116, 105, 116,
                    108, 101, 62, 60, 47, 104, 101, 97, 100, 62, 60, 98, 111,
                    100, 121, 62, 70, 97, 116, 32, 98, 101, 97, 99, 111, 110,
                    60, 47, 98, 111, 100, 121, 62, 60, 47, 104, 116, 109,
                    108, 62]

    app = localGATT.Application()
    srv = localGATT.Service(1, FAT_SERVICE, True)
    fat_html = localGATT.Characteristic(1,
                                        HTML_CHRC,
                                        srv,
                                        value_string,
                                        False,
                                        ['read'])
    fat_html.Set(constants.GATT_SERVICE_IFACE, 'Service', srv.get_path())
    app.add_managed_object(srv)
    app.add_managed_object(fat_html)
    srv_mng = GATT.GattManager('/org/bluez/hci0')
    srv_mng.register_application(app, {})


if __name__ == '__main__':

    ad_manager, advertiser = advertise_beacon()

    build_fat_service()

    try:
        tools.start_mainloop()
    except KeyboardInterrupt:
        tools.stop_mainloop()
        ad_manager.unregister_advertisement(advertiser)
    finally:
        pass
