
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

    advertiser0.service_UUIDs = ['FEAA']
    advertiser0.service_data = {'FEAA': [0x10, 0x08, 0x0E, 70, 97,
                                         116, 79, 110, 101]}

    if not dongle.powered:
        dongle.powered = True
    ad_manager = advertisement.AdvertisingManager(dongle.path)
    ad_manager.register_advertisement(advertiser0, {})

    return ad_manager, advertiser0


def build_fat_service():
    html_string = """<html><head><style>
body { background-color: linen; }
h1 { color: maroon; margin-left: 40px; }
</style><title>FatBeacon Demo</title>
<meta charset='UTF-8'><meta name='description' content='FatBeacon Demo'/>
</head> <body> <h1>Fat Beacon</h1> <p>
A FatBeacon is a beacon that rather than advertising a URL
to load a web page from it actually hosts the web page on the
device and services it up from the BLE characteristic
</p> </body> </html>"""
    html_ord = []
    for char in html_string:
        html_ord.append(ord(char))

    app = localGATT.Application()
    srv = localGATT.Service(1, FAT_SERVICE, True)
    fat_html = localGATT.Characteristic(1,
                                        HTML_CHRC,
                                        srv,
                                        html_ord,
                                        False,
                                        ['read'])
    fat_html.service = srv.path
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
