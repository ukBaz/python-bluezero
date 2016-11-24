"""
This is a simple example of how to read data from a micro:bit.

You will need the Bluetooth services of the micro:bit exposed.

This code was developed using the 'Bluetooth Most Services, No Security'
micro:bit hex file from:
http://www.bittysoftware.com/downloads.html
The hex file called "For micro:bit Blue - Main Bluetooth services,
pairing not required" was used.
It had a file name of:
microbit-2-0-0-rc4-ABDEILMT-N-pwr7.hex


The following link is a good reference for Bluetooth on the microbit
http://bluetooth-mdw.blogspot.co.uk/p/bbc-microbit.html

"""
from time import sleep
import logging

from bluezero import constants
from bluezero import tools
from bluezero import adapter
from bluezero import device


ACCEL_SRV = 'E95D0753-251D-470A-A062-FA1922DFA9A8'
ACCEL_DATA = 'E95DCA4B-251D-470A-A062-FA1922DFA9A8'
ACCEL_PERIOD = 'E95DFB24-251D-470A-A062-FA1922DFA9A8'
MAGNETO_SRV = 'E95DF2D8-251D-470A-A062-FA1922DFA9A8'
MAGNETO_DATA = 'E95DFB11-251D-470A-A062-FA1922DFA9A8'
MAGNETO_PERIOD = 'E95D386C-251D-470A-A062-FA1922DFA9A8'
MAGNETO_BEARING = 'E95D9715-251D-470A-A062-FA1922DFA9A8'
BTN_SRV = 'E95D9882-251D-470A-A062-FA1922DFA9A8'
BTN_A_STATE = 'E95DDA90-251D-470A-A062-FA1922DFA9A8'
BTN_B_STATE = 'E95DDA91-251D-470A-A062-FA1922DFA9A8'
IO_PIN_SRV = 'E95D127B-251D-470A-A062-FA1922DFA9A8'
IO_PIN_DATA = 'E95D8D00-251D-470A-A062-FA1922DFA9A8'
IO_AD_CONFIG = 'E95D5899-251D-470A-A062-FA1922DFA9A8'
IO_PIN_CONFIG = 'E95DB9FE-251D-470A-A062-FA1922DFA9A8'
IO_PIN_PWM = 'E95DD822-251D-470A-A062-FA1922DFA9A8'
LED_SRV = 'E95DD91D-251D-470A-A062-FA1922DFA9A8'
LED_STATE = 'E95D7B77-251D-470A-A062-FA1922DFA9A8'
LED_TEXT = 'E95D93EE-251D-470A-A062-FA1922DFA9A8'
LED_SCROLL = 'E95D0D2D-251D-470A-A062-FA1922DFA9A8'
TEMP_SRV = 'E95D6100-251D-470A-A062-FA1922DFA9A8'
TEMP_DATA = 'E95D9250-251D-470A-A062-FA1922DFA9A8'
TEMP_PERIOD = 'E95D1B25-251D-470A-A062-FA1922DFA9A8'

logging.basicConfig(level=logging.DEBUG)


class Microbit:
    """
    Class to simplify interacting with a microbit over Bluetooth Low Energy
    """
    def __init__(self, name=None, address=None):
        """
        Initialization of an instance of a remote microbit
        :param name: Will look for a BLE device with this string in its name
        :param address: Will look for a BLE device with this address
         (Currently not implemented)
        """
        self.name = name
        self.address = address
        self.dongle = adapter.Adapter(adapter.list_adapters()[0])
        if not self.dongle.powered:
            self.dongle.powered = True
        logging.debug('Adapter powered')
        logging.debug('Start discovery')
        self.dongle.nearby_discovery()
        self.ubit = device.Device(
            tools.get_dbus_path(
                constants.DEVICE_INTERFACE,
                'Name',
                name)[0])

        self.accel_srv_path = None
        self.accel_data_path = None
        self.aceel_period_path = None
        self.magneto_srv_path = None
        self.magneto_data_path = None
        self.magneto_period_path = None
        self.magneto_bearing_path = None
        self.btn_srv_path = None
        self.btn_a_state_path = None
        self.btn_b_state_path = None
        self.io_pin_srv_path = None
        self.io_pin_data_path = None
        self.io_ad_config_path = None
        self.io_pin_config_path = None
        self.io_pin_pwm_path = None
        self.led_srv_path = None
        self.led_state_path = None
        self.led_text_path = None
        self.led_scroll_path = None
        self.temp_srv_path = None
        self.temp_data_path = None
        self.temp_period_path = None

    @property
    def connected(self):
        """Indicate whether the remote device is currently connected."""
        return self.ubit.connected

    def connect(self):
        """
        Connect to the specified microbit for this instance
        """
        self.ubit.connect()
        while not self.ubit.services_resolved:
            sleep(0.5)
        self._get_dbus_paths()

    def _get_dbus_paths(self):
        """
        Utility function to get the paths for UUIDs
        """
        self.accel_srv_path = tools.uuid_dbus_path(
            constants.GATT_SERVICE_IFACE,
            ACCEL_SRV)[0]
        self.accel_data_path = tools.uuid_dbus_path(
            constants.GATT_CHRC_IFACE,
            ACCEL_DATA)[0]
        self.aceel_period_path = tools.uuid_dbus_path(
            constants.GATT_CHRC_IFACE,
            ACCEL_PERIOD)[0]
        self.magneto_srv_path = tools.uuid_dbus_path(
            constants.GATT_SERVICE_IFACE,
            MAGNETO_SRV)[0]
        self.magneto_data_path = tools.uuid_dbus_path(
            constants.GATT_CHRC_IFACE,
            MAGNETO_DATA)[0]
        self.magneto_period_path = tools.uuid_dbus_path(
            constants.GATT_CHRC_IFACE,
            MAGNETO_PERIOD)[0]
        self.magneto_bearing_path = tools.uuid_dbus_path(
            constants.GATT_CHRC_IFACE,
            MAGNETO_BEARING)[0]
        self.btn_srv_path = tools.uuid_dbus_path(
            constants.GATT_SERVICE_IFACE,
            BTN_SRV)[0]
        self.btn_a_state_path = tools.uuid_dbus_path(
            constants.GATT_CHRC_IFACE,
            BTN_A_STATE)[0]
        self.btn_b_state_path = tools.uuid_dbus_path(
            constants.GATT_CHRC_IFACE,
            BTN_B_STATE)[0]
        self.io_pin_srv_path = tools.uuid_dbus_path(
            constants.GATT_SERVICE_IFACE,
            IO_PIN_SRV)[0]
        self.io_pin_data_path = tools.uuid_dbus_path(
            constants.GATT_CHRC_IFACE,
            IO_PIN_DATA)[0]
        self.io_pin_config_path = tools.uuid_dbus_path(
            constants.GATT_CHRC_IFACE,
            IO_PIN_CONFIG)[0]
        self.io_pin_pwm_path = tools.uuid_dbus_path(
            constants.GATT_CHRC_IFACE,
            IO_PIN_PWM)[0]
        self.io_ad_config_path = tools.uuid_dbus_path(
            constants.GATT_CHRC_IFACE,
            IO_AD_CONFIG)[0]
        self.led_srv_path = tools.uuid_dbus_path(
            constants.GATT_SERVICE_IFACE,
            LED_SRV)[0]
        self.led_state_path = tools.uuid_dbus_path(
            constants.GATT_CHRC_IFACE,
            LED_STATE)[0]
        self.led_text_path = tools.uuid_dbus_path(
            constants.GATT_CHRC_IFACE,
            LED_TEXT)[0]
        self.led_scroll_path = tools.uuid_dbus_path(
            constants.GATT_CHRC_IFACE,
            LED_SCROLL)[0]
        self.temp_srv_path = tools.uuid_dbus_path(
            constants.GATT_SERVICE_IFACE,
            TEMP_SRV)[0]
        self.temp_data_path = tools.uuid_dbus_path(
            constants.GATT_CHRC_IFACE,
            TEMP_DATA)[0]
        self.temp_period_path = tools.uuid_dbus_path(
            constants.GATT_CHRC_IFACE,
            TEMP_PERIOD)[0]

    def disconnect(self):
        """
        Disconnect from the microbit
        """
        self.ubit.disconnect()

    def display_scroll_delay(self, delay=None):
        """
        Specifies a millisecond delay to wait for in between showing each
        character on the display.
        """
        scroll_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                        self.led_scroll_path)

        scroll_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                            scroll_obj)
        if delay is None:
            return int.from_bytes(scroll_iface.ReadValue(()),
                                  byteorder='little',
                                  signed=False)
        else:
            if delay < 0:
                delay = 0
            elif delay > 2**16:
                delay = 2**16
            scroll_iface.WriteValue(tools.int_to_uint16(delay), ())

    def display_text(self, words):
        """
        Specify text to be displayed. Limit of 20 characters.
        The content will be restricted to that number of characters.
        :param words:
        """
        led_txt_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                         self.led_text_path)
        led_txt_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                             led_txt_obj)
        data = []
        text = ''
        if len(words) > 20:
            text = words[:19]
        else:
            text = words
        for letter in text:
            data.append(ord(letter))
        led_txt_iface.WriteValue(data, ())

    def _write_pixels(self, data):
        """
        Utility function for the different display functions
        :param data: list of 5 numbers in the range 0 to 255
        (e.g. [0xff, 0x00, 0, 255, 0b10101]
        """
        pixels_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                        self.led_state_path)
        pixels_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                            pixels_obj)
        pixels_iface.WriteValue(data, ())

    def display_clear(self):
        """
        Clear the LED display on the microbit
        """
        self._write_pixels([0x00, 0x00, 0x00, 0x00, 0x00])

    def display_pixels(self, row0, row1, row2, row3, row4):
        """
        For each row of LEDs specify which LEDs will be on.
        e.g. 0b11111 will turn all LEDs in specified row on
             0b10101 will turn alternate LEDs on
             0b00000 will turn all LEDs in row off
        :param row0: top row
        :param row1:
        :param row2: middle row
        :param row3:
        :param row4: bottom row
        """
        self._write_pixels([row0, row1, row2, row3, row4])

    def read_pixels(self):
        """
        Returns a list of 5 binary numbers. Each number represents a row
        from top to bottom
        :return: Example [0b1110, 0b10000, 0b10000, 0b10000, 0b1110]
        """
        pixels_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                        self.led_state_path)
        pixels_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                            pixels_obj)
        rows = pixels_iface.ReadValue(())
        return [bin(i) for i in rows]

    def read_temperature(self):
        """
        Temperature from sensors in micro:bit processors
        :return: Integer of temperature in Celsius
        """
        temp_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                      self.temp_data_path)
        temp_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE, temp_obj)

        # Read button value
        tmp_val = temp_iface.ReadValue(())

        return int.from_bytes(tmp_val, byteorder='little', signed=True)

    def _read_button(self, btn_path):
        """
        Read the button characteristic on the micro:bit and return value
        3 button states are defined and represented by a simple numeric
        enumeration:  0 = not pressed, 1 = pressed, 2 = long press.
        :param btn_path: The Bluez path to the button characteristic
        :return: integer representing button value
        """

        # Get characteristic interface for data
        btn_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME, btn_path)
        btn_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE, btn_obj)

        # Read button value
        btn_val = btn_iface.ReadValue(())

        answer = int.from_bytes(btn_val, byteorder='little', signed=False)
        return answer

    def read_button_a(self):
        """
        Read the state of button A on a micro:bit
        3 button states are defined and represented by a simple numeric
        enumeration:  0 = not pressed, 1 = pressed, 2 = long press.
        :return: integer representing button value
        """
        return self._read_button(self.btn_a_state_path)

    def read_button_b(self):
        """
        Read the state of button B on a micro:bit
        3 button states are defined and represented by a simple numeric
        enumeration:  0 = not pressed, 1 = pressed, 2 = long press.
        :return: integer representing button value
        """
        return self._read_button(self.btn_b_state_path)

    def read_accelerometer(self):
        """
        Read the values of the accelerometer on the microbit
        :return: return a list in the order of x, y & z
        """
        # [16, 0, 64, 0, 32, 252]
        # x=0.16, y=0.024, z=-0.992
        accel_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                       self.accel_data_path)
        accel_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                           accel_obj)

        # Read button value
        bytes = accel_iface.ReadValue(())

        return tools.bytes_to_xyz(bytes)

    def read_magnetometer(self):
        """
        Exposes magnetometer data.
        A magnetometer measures a magnetic field such
        as the earth's magnetic field in 3 axes.
        :return: List of x, y & z value
        """
        mag_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                     self.magneto_data_path)
        mag_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE, mag_obj)

        bytes = mag_iface.ReadValue(())

        return tools.bytes_to_xyz(bytes)

    def read_bearing(self):
        """
        Compass bearing in degrees from North.
        :return: degrees in integer
        """
        mag_bear_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                          self.magneto_bearing_path)
        mag_bear_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                              mag_bear_obj)

        mag_bear_val = mag_bear_iface.ReadValue(())

        return int.from_bytes(mag_bear_val,
                              byteorder='little', signed=False)

    def _pin_config(self, states=None):
        """
        A bit mask (32 bit) which defines which inputs will be read.
        A value of 0 means configured for output and 1 means configured
        for input.
        """
        pin_conf_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                          self.io_pin_config_path)

        pin_conf_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                              pin_conf_obj)

        if states is None:
            return pin_conf_iface.ReadValue(())
        else:
            pin_conf_iface.WriteValue([states], ())

    def _pin_ad_config(self, states=None):
        """
        A bit mask (32 bit) which allows each pin to be configured for
        analogue or digital use.
        A value of 0 means digital and 1 means analogue.
        If no states are specified then the current state is returned
        """
        pin_ad_conf_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                             self.io_ad_config_path)

        pin_ad_conf_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                                 pin_ad_conf_obj)
        if states is None:
            return pin_ad_conf_iface.ReadValue(())
        else:
            pin_ad_conf_iface.WriteValue([states], ())

    def _pin_states(self, pin_value_pairs):
        """
        Contains data relating to zero or more pins.
        Structured as a variable length list of up to 19 Pin
        Number / Value pairs.
        """
        pin_states_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                            self.io_pin_data_path)

        pin_states_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                                pin_states_obj)
        if states is None:
            return pin_states_iface.ReadValue(())
        else:
            pin_states_iface.WriteValue([pin_value_pairs], ())

    def _pin_pwn_control(self, pin, value, period):
        """
        Write only method to set the PWM control data
        :param pin: pin number [range 0-19]
        :param value: Value is in the range 0 to 1024, per the current DAL API
            (e.g. setAnalogValue). 0 means OFF.
        :param period: Period is in microseconds and is an unsigned integer
        :return:
        """
        pin_pwm_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                         self.io_pin_pwm_path)

        pin_pwm_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                             pin_pwm_obj)
        byte_value = tools.int_to_uint16(value)
        byte_period = tools.int_to_uint32(period)
        pin_pwm_iface.WriteValue([pin,
                                  byte_value[0],
                                  byte_value[1],
                                  byte_period[0],
                                  byte_period[1],
                                  byte_period[2],
                                  byte_period[3]
                                  ], ())

    def play_beep(self, duration):
        """
        If a buzzer is attached to pin 0 then a beep will be played
        :param duration: time in seconds
        """
        self._pin_config(0)
        self._pin_ad_config(1)
        self._pin_pwn_control(0, 512, 2094)
        sleep(duration)
        self._pin_pwn_control(0, 0, 0)
