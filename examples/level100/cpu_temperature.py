# Standard modules
import os
import dbus
try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

# Bluezero modules
from bluezero import tools
from bluezero import constants
from bluezero import adapter
from bluezero import advertisement
from bluezero import localGATT
from bluezero import GATT

# constants
CPU_TMP_SRVC = '12341000-1234-1234-1234-123456789abc'
CPU_TMP_CHRC = '2A6E'
CPU_FMT_DSCP = '2904'


def get_cpu_temperature():
    # return random.randrange(3200, 5310, 10) / 100
    cpu_temp = os.popen('vcgencmd measure_temp').readline()
    return float(cpu_temp.replace('temp=', '').replace("'C\n", ''))


def sint16(value):
    return int(value * 100).to_bytes(2, byteorder='little', signed=True)


def cpu_temp_sint16(value):
    answer = []
    value_int16 = sint16(value[0])
    for bytes in value_int16:
        answer.append(dbus.Byte(bytes))

    return answer


class TemperatureChrc(localGATT.Characteristic):
    def __init__(self, service):
        localGATT.Characteristic.__init__(self,
                                          1,
                                          CPU_TMP_CHRC,
                                          service,
                                          [get_cpu_temperature()],
                                          False,
                                          ['read', 'notify'])

    def temperature_cb(self):
        reading = [get_cpu_temperature()]
        print('Getting new temperature',
              reading,
              self.props[constants.GATT_CHRC_IFACE]['Notifying'])
        self.props[constants.GATT_CHRC_IFACE]['Value'] = reading

        self.PropertiesChanged(constants.GATT_CHRC_IFACE,
                               {'Value': dbus.Array(cpu_temp_sint16(reading))},
                               [])
        print('Array value: ', cpu_temp_sint16(reading))
        return self.props[constants.GATT_CHRC_IFACE]['Notifying']

    def _update_temp_value(self):
        if not self.props[constants.GATT_CHRC_IFACE]['Notifying']:
            return

        print('Starting timer event')
        GObject.timeout_add(500, self.temperature_cb)

    def ReadValue(self, options):
        return dbus.Array(
            cpu_temp_sint16(self.props[constants.GATT_CHRC_IFACE]['Value'])
        )

    def StartNotify(self):
        if self.props[constants.GATT_CHRC_IFACE]['Notifying']:
            print('Already notifying, nothing to do')
            return
        print('Notifying on')
        self.props[constants.GATT_CHRC_IFACE]['Notifying'] = True
        self._update_temp_value()

    def StopNotify(self):
        if not self.props[constants.GATT_CHRC_IFACE]['Notifying']:
            print('Not notifying, nothing to do')
            return

        print('Notifying off')
        self.props[constants.GATT_CHRC_IFACE]['Notifying'] = False
        self._update_temp_value()


class ble:
    def __init__(self):
        self.bus = dbus.SystemBus()
        self.app = localGATT.Application()
        self.srv = localGATT.Service(1, CPU_TMP_SRVC, True)

        self.charc = TemperatureChrc(self.srv)

        self.charc.service = self.srv.path

        cpu_format_value = dbus.Array([dbus.Byte(0x0E),
                                       dbus.Byte(0xFE),
                                       dbus.Byte(0x2F),
                                       dbus.Byte(0x27),
                                       dbus.Byte(0x01),
                                       dbus.Byte(0x00),
                                       dbus.Byte(0x00)])
        self.cpu_format = localGATT.Descriptor(4,
                                               CPU_FMT_DSCP,
                                               self.charc,
                                               cpu_format_value,
                                               ['read'])

        self.app.add_managed_object(self.srv)
        self.app.add_managed_object(self.charc)
        self.app.add_managed_object(self.cpu_format)

        self.srv_mng = GATT.GattManager(adapter.list_adapters()[0])
        self.srv_mng.register_application(self.app, {})

        self.dongle = adapter.Adapter(adapter.list_adapters()[0])
        advert = advertisement.Advertisement(1, 'peripheral')

        advert.service_UUIDs = [CPU_TMP_SRVC]
        # eddystone_data = tools.url_to_advert(WEB_BLINKT, 0x10, TX_POWER)
        # advert.service_data = {EDDYSTONE: eddystone_data}
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
    print('CPU temperature is {}C'.format(get_cpu_temperature()))
    print(sint16(get_cpu_temperature()))
    pi_cpu_monitor = ble()
    pi_cpu_monitor.start_bt()
