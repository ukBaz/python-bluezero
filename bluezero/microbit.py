"""
This is a simple API for reading data from a micro:bit.

You will need the Bluetooth services of the micro:bit exposed.

This code was developed using the 'Bluetooth Most Services, No Security'
micro:bit hex file from:
http://www.bittysoftware.com/downloads.html
The hex file called "For micro:bit Blue - Main Bluetooth services,
pairing not required" was used.

The following link is a good reference for Bluetooth on the microbit
http://bluetooth-mdw.blogspot.co.uk/p/bbc-microbit.html
"""
from time import sleep

from bluezero import constants
from bluezero import tools
from bluezero import adapter
from bluezero import device

import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

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

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger.addHandler(NullHandler())


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
        logger.debug('Adapter powered')
        logger.debug('Start discovery')
        self.dongle.nearby_discovery()
        device_path = None
        if name is not None:
            device_path = tools.get_dbus_path(
                constants.DEVICE_INTERFACE,
                'Name',
                name)
        elif address is not None:
            device_path = tools.get_dbus_path(
                constants.DEVICE_INTERFACE,
                'Address',
                address)

        self.ubit = device.Device(device_path[0])

        # dbus paths
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

        # dbus interfaces()
        self.scroll_iface = None
        self.led_txt_iface = None
        self.pixels_iface = None
        self.temp_iface = None
        self.btn_a_iface = None
        self.btn_b_iface = None
        self.accel_iface = None
        self.mag_iface = None
        self.mag_bear_iface = None
        self.pin_conf_iface = None
        self.pin_ad_iface = None
        self.pin_states_iface = None
        self.pin_pwm_iface = None

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

    def _config_dbus_ifaces(self):
        self._config_scroll_iface()
        self._config_led_txt_iface()
        self._config_pixels_iface()
        self._config_temp_iface()
        self._config_btn_a_iface()
        self._config_btn_b_iface()
        self._config_accel_iface()
        self._config_mag_iface()
        self._config_mag_bear_iface()
        self._config_pin_conf_iface()
        self._config_pin_ad_iface()
        self._config_pin_states_iface()
        self._config_pin_pwm_iface()

    def _config_scroll_iface(self):
        scroll_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                        self.led_scroll_path)
        self.scroll_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                                 scroll_obj)

    def _config_led_txt_iface(self):
        led_txt_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                         self.led_text_path)
        self.led_txt_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                                  led_txt_obj)

    def _config_pixels_iface(self):
        pixels_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                        self.led_state_path)
        self.pixels_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                                 pixels_obj)

    def _config_temp_iface(self):
        temp_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                      self.temp_data_path)
        self.temp_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                               temp_obj)

    def _config_btn_a_iface(self):
        btn_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                     self.btn_a_state_path)
        self.btn_a_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                                btn_obj)

    def _config_btn_b_iface(self):
        btn_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                     self.btn_b_state_path)
        self.btn_a_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                                btn_obj)

    def _config_accel_iface(self):
        accel_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                       self.accel_data_path)
        self.accel_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                                accel_obj)

    def _config_mag_iface(self):
        mag_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                     self.magneto_data_path)
        self.mag_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                              mag_obj)

    def _config_mag_bear_iface(self):
        mag_bear_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                          self.magneto_bearing_path)
        self.mag_bear_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                                   mag_bear_obj)

    def _config_pin_conf_iface(self):
        pin_conf_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                          self.io_pin_config_path)

        self.pin_conf_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                                   pin_conf_obj)

    def _config_pin_ad_iface(self):
        pin_ad_conf_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                             self.io_ad_config_path)
        self.pin_ad_conf_iface = tools.get_dbus_iface(
            constants.GATT_CHRC_IFACE,
            pin_ad_conf_obj)

    def _config_pin_states_iface(self):
        pin_states_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                            self.io_pin_data_path)

        self.pin_states_iface = tools.get_dbus_iface(
            constants.GATT_CHRC_IFACE,
            pin_states_obj)

    def _config_pin_pwm_iface(self):
        pin_pwm_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                         self.io_pin_pwm_path)

        self.pin_pwm_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                                  pin_pwm_obj)

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
        self._config_dbus_ifaces()

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

        if delay is None:
            return int.from_bytes(self.scroll_iface.ReadValue(()),
                                  byteorder='little',
                                  signed=False)
        else:
            if delay < 0:
                delay = 0
            elif delay > 2**16:
                delay = 2**16
            self.scroll_iface.WriteValue(tools.int_to_uint16(delay), ())

    def display_text(self, words):
        """
        Specify text to be displayed. Limit of 20 characters.
        The content will be restricted to that number of characters.
        :param words:
        """

        data = []
        text = ''
        if len(words) > 20:
            text = words[:19]
        else:
            text = words
        for letter in text:
            data.append(ord(letter))
        self.led_txt_iface.WriteValue(data, ())

    def _write_pixels(self, data):
        """
        Utility function for the different display functions
        :param data: list of 5 numbers in the range 0 to 255
        (e.g. [0xff, 0x00, 0, 255, 0b10101]
        """
        self.pixels_iface.WriteValue(data, ())

    def display_clear(self):
        """
        Clear the LED display on the microbit
        """
        self._write_pixels([0x00, 0x00, 0x00, 0x00, 0x00])

    def display_pixels(self, row0, row1, row2, row3, row4):
        """
        For each row of LEDs specify which LEDs will be on.
        :example:
        0b11111 will turn all LEDs in specified row on
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
        rows = self.pixels_iface.ReadValue(())
        return [bin(i) for i in rows]

    def read_temperature(self):
        """
        Temperature from sensors in micro:bit processors
        :return: Integer of temperature in Celsius
        """
        tmp_val = self.temp_iface.ReadValue(())

        return int.from_bytes(tmp_val, byteorder='little', signed=True)

    def read_button_a(self):
        """
        Read the state of button A on a micro:bit
        3 button states are defined and represented by a simple numeric
        enumeration:  0 = not pressed, 1 = pressed, 2 = long press.
        :return: integer representing button value
        """
        btn_val = self.btn_a_iface.ReadValue(())

        return int.from_bytes(btn_val, byteorder='little', signed=False)

    def read_button_b(self):
        """
        Read the state of button B on a micro:bit
        3 button states are defined and represented by a simple numeric
        enumeration:  0 = not pressed, 1 = pressed, 2 = long press.
        :return: integer representing button value
        """
        btn_val = self.btn_b_iface.ReadValue(())

        return int.from_bytes(btn_val, byteorder='little', signed=False)

    def _button_notify_cb(self):
        print('Button subscribed!!!')
        return 1

    def _button_prop_cb(self, iface, changed_props, invalidated_props):
        print(iface, changed_props, invalidated_props)

    def subscribe_button_a(self, user_callback):
        btn_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                     self.btn_a_state_path)
        btn_iface = tools.get_dbus_iface(constants.DBUS_PROP_IFACE,
                                         btn_obj)
        btn_iface.connect_to_signal('PropertiesChanged',
                                    user_callback)
        btn_obj.StartNotify(reply_handler=self._button_notify_cb,
                            error_handler=tools.generic_error_cb,
                            dbus_interface=constants.GATT_CHRC_IFACE)

    def subscribe_button_b(self, user_callback):
        btn_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                     self.btn_b_state_path)
        btn_iface = tools.get_dbus_iface(constants.DBUS_PROP_IFACE,
                                         btn_obj)
        btn_iface.connect_to_signal('PropertiesChanged',
                                    user_callback)
        btn_obj.StartNotify(reply_handler=self._button_notify_cb,
                            error_handler=tools.generic_error_cb,
                            dbus_interface=constants.GATT_CHRC_IFACE)

    def read_accelerometer(self):
        """
        Read the values of the accelerometer on the microbit
        :return: return a list in the order of x, y & z
        """
        # [16, 0, 64, 0, 32, 252]
        # x=0.16, y=0.024, z=-0.992
        accel_bytes = self.accel_iface.ReadValue(())

        return tools.bytes_to_xyz(accel_bytes)

    def read_magnetometer(self):
        """
        Exposes magnetometer data.
        A magnetometer measures a magnetic field such
        as the earth's magnetic field in 3 axes.
        :return: List of x, y & z value
        """
        mag_bytes = self.mag_iface.ReadValue(())

        return tools.bytes_to_xyz(mag_bytes)

    def read_bearing(self):
        """
        Compass bearing in degrees from North.
        :return: degrees in integer
        """
        mag_bear_val = self.mag_bear_iface.ReadValue(())

        return int.from_bytes(mag_bear_val,
                              byteorder='little', signed=False)

    def _pin_config(self, states=None):
        """
        A bit mask (32 bit) which defines which inputs will be read.
        A value of 0 means configured for output and 1 means configured
        for input.
        """
        if states is None:
            return self.pin_conf_iface.ReadValue(())
        else:
            self.pin_conf_iface.WriteValue(states, ())

    def _pin_ad_config(self, states=None):
        """
        A bit mask (32 bit) which allows each pin to be configured for
        analogue or digital use.
        A value of 0 means digital and 1 means analogue.
        If no states are specified then the current state is returned
        """

        if states is None:
            return self.pin_ad_conf_iface.ReadValue(())
        else:
            self.pin_ad_conf_iface.WriteValue(states, ())

    def _pin_states(self, pin_value_pairs=None):
        """
        Contains data relating to zero or more pins.
        Structured as a variable length list of up to 19 Pin
        Number / Value pairs.
        """
        if pin_value_pairs is None:
            return self.pin_states_iface.ReadValue(())
        else:
            self.pin_states_iface.WriteValue(pin_value_pairs, ())

    def _pin_pwm_control(self, pin, value, period):
        """
        Write only method to set the PWM control data
        :param pin: pin number [range 0-19]
        :param value: Value is in the range 0 to 1024, per the current DAL API
            (e.g. setAnalogValue). 0 means OFF.
        :param period: Period is in microseconds and is an unsigned integer
        :return:
        """
        byte_value = tools.int_to_uint16(value)
        byte_period = tools.int_to_uint32(period)
        self.pin_pwm_iface.WriteValue([pin,
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
        self._pin_pwm_control(0, 512, 2094)
        sleep(duration)
        self._pin_pwm_control(0, 0, 0)


class BitBot(Microbit):
    """
    Class to simplify interacting with a microbit attached to a bit:bot
    over Bluetooth Low Energy
    """
    def __init__(self, name=None, address=None):
        """
        Initialization of an instance of a remote bit:bot
        :param name: Will look for a BLE device with this string in its name
        :param address: Will look for a BLE device with this address
        """
        self.inputs_configured = False
        self.left_light = False
        Microbit.__init__(self, name, address)

    def stop(self):
        """
        Stop both wheels of the bit:bot
        """
        self._pin_states([0x01, 0x00, 0x0C, 0x00, 0x00, 0x00, 0x08, 0x00])

    def spin_right(self):
        """
        Spin right wheel forward and left wheel backwards so bit:bot spins
        """
        self._pin_states([0x01, 0x01, 0x0C, 0x00, 0x00, 0x00, 0x08, 0x01])

    def spin_left(self):
        """
        Spin left wheel forward and right wheel backwards so bit:bot spins
        """
        self._pin_states([0x01, 0x00, 0x0C, 0x01, 0x00, 0x01, 0x08, 0x00])

    def forward(self):
        """
        Spin both wheels forward
        """
        self._pin_states([0x01, 0x01, 0x0C, 0x00, 0x00, 0x01, 0x08, 0x00])

    def reverse(self):
        """
        Spin both wheels backwards
        """
        self._pin_states([0x01, 0x00, 0x0C, 0x01, 0x00, 0x00, 0x08, 0x01])

    def _left_motor(self, pwm_value, reverse=False):
        if not reverse:
            self._pin_states([0x08, 0x00])
        else:
            self._pin_states([0x08, 0x01])
        self._pin_pwm_control(0, pwm_value, 20000)

    def _right_motor(self, pwm_value, reverse=False):
        if not reverse:
            self._pin_states([0x0C, 0x00])
        else:
            self._pin_states([0x0C, 0x01])
        self._pin_pwm_control(1, pwm_value, 20000)

    def _update_motors(self, left_val, right_val,
                       left_rev, right_rev,
                       pwm_period=20000):
        period = tools.int_to_uint32(pwm_period)
        left_pwm = tools.int_to_uint16(left_val)
        right_pwm = tools.int_to_uint16(right_val)
        self.pin_pwm_iface.WriteValue([0,
                                       left_pwm[0],
                                       left_pwm[1],
                                       period[0],
                                       period[1],
                                       period[2],
                                       period[3],
                                       1,
                                       right_pwm[0],
                                       right_pwm[1],
                                       period[0],
                                       period[1],
                                       period[2],
                                       period[3]
                                       ], ())
        self._pin_states([0x08, left_rev, 0x0C, right_rev])

    def drive(self, left=100, right=100):
        """

        :param left:
        :param right:
        """
        left_direction = 0
        left_motor = self._percentage_to_pwm(left)

        right_direction = 0
        right_motor = self._percentage_to_pwm(right)

        if left < 0:
            left_direction = 1

        if right < 0:
            right_direction = 1

        self._update_motors(left_motor, right_motor,
                            left_direction, right_direction)

    def _percentage_to_pwm(self, percent):
        if percent < 0:
            percent += 100
        return int(10.23 * percent)

    def buzzer_on(self):
        """
        Play the buzzer
        """
        self._pin_states([0x0E, 0x01])

    def buzzer_off(self):
        """
        Stop the buzzer
        """
        self._pin_states([0x0E, 0x00])

    def read_left_line(self):
        """
        Read the left line sensor
        :return: False = No line  True = Line
        """
        return bool(self._get_pin_value(11))

    def read_right_line(self):
        """
        Read the right line sensor
        :return: False = No line  True = Line
        """
        return bool(self._get_pin_value(5))

    def read_lines(self):
        if not self.inputs_configured:
            self._config_inputs()
            self.inputs_configured = True
        pins = self._pin_states()
        return bool(pins[3]), bool(pins[5])

    def read_left_light(self):
        self._pin_states([0x10, 0x00])
        return int(self._get_pin_value(2))

    def read_right_light(self):
        self._pin_states([0x10, 0x01])
        return int(self._get_pin_value(2))

    def _config_inputs(self):
        self._pin_config([0x24, 0x08, 0x00, 0x00])
        self._pin_ad_config([0x04, 0x00, 0x00, 0x00])

    def _build_pin_value_pairs(self, pin_states):
        val_dict = {}
        if len(pin_states) > 0:
            val_dict = dict(zip(pin_states[::2], pin_states[1::2]))
        return val_dict

    def _get_pin_value(self, pin):
        if not self.inputs_configured:
            self._config_inputs()
            self.inputs_configured = True
        pin_value_pairs = self._build_pin_value_pairs(self._pin_states())
        if pin in pin_value_pairs.keys():
            return pin_value_pairs[pin]
        else:
            return None
