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
from bluezero import GATT

# For flattening lists
import itertools

# Logging
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        """Empty Null Handler for the logger."""

        def emit(self, record):
            """Emit function to match default logging behaviour."""
            pass

# Microbit UUIDs
ACCEL_DATA = 'E95DCA4B-251D-470A-A062-FA1922DFA9A8'
MAGNETO_DATA = 'E95DFB11-251D-470A-A062-FA1922DFA9A8'
MAGNETO_BEARING = 'E95D9715-251D-470A-A062-FA1922DFA9A8'
BTN_A_STATE = 'E95DDA90-251D-470A-A062-FA1922DFA9A8'
BTN_B_STATE = 'E95DDA91-251D-470A-A062-FA1922DFA9A8'
IO_PIN_DATA = 'E95D8D00-251D-470A-A062-FA1922DFA9A8'
IO_AD_CONFIG = 'E95D5899-251D-470A-A062-FA1922DFA9A8'
IO_PIN_CONFIG = 'E95DB9FE-251D-470A-A062-FA1922DFA9A8'
IO_PIN_PWM = 'E95DD822-251D-470A-A062-FA1922DFA9A8'
LED_STATE = 'E95D7B77-251D-470A-A062-FA1922DFA9A8'
LED_TEXT = 'E95D93EE-251D-470A-A062-FA1922DFA9A8'
LED_SCROLL = 'E95D0D2D-251D-470A-A062-FA1922DFA9A8'
TEMP_DATA = 'E95D9250-251D-470A-A062-FA1922DFA9A8'

# Unused Microbit UUIDs
# ACCEL_SRV = 'E95D0753-251D-470A-A062-FA1922DFA9A8'
# ACCEL_PERIOD = 'E95DFB24-251D-470A-A062-FA1922DFA9A8'
# MAGNETO_SRV = 'E95DF2D8-251D-470A-A062-FA1922DFA9A8'
# MAGNETO_PERIOD = 'E95D386C-251D-470A-A062-FA1922DFA9A8'
# BTN_SRV = 'E95D9882-251D-470A-A062-FA1922DFA9A8'
# IO_PIN_SRV = 'E95D127B-251D-470A-A062-FA1922DFA9A8'
# LED_SRV = 'E95DD91D-251D-470A-A062-FA1922DFA9A8'
# TEMP_SRV = 'E95D6100-251D-470A-A062-FA1922DFA9A8'
# TEMP_PERIOD = 'E95D1B25-251D-470A-A062-FA1922DFA9A8'

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger.addHandler(NullHandler())


class ConnectionError(Exception):
    """Class to handle error cases when the microbit is disconnected."""

    pass


class Microbit:
    """Simplify interaction with a microbit over Bluetooth Low Energy."""

    def __init__(self, name=None, address=None):
        """
        Initialize an instance of a remote microbit.

        :param name: Will look for a BLE device with this string in its name
        :param address: Will look for a BLE device with this address
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
        self._magneto_data = None
        self._magneto_bearing = None
        self._btn_a_state = None
        self._btn_a_cb = None
        self._btn_b_state = None
        self._btn_b_cb = None
        self._io_pin_data = None
        self._io_ad_config = None
        self._io_pin_config = None
        self._io_pin_pwm = None
        self._led_state = None
        self._led_text = None
        self._led_scroll = None
        self._temp_data = None

        # Unused dbus paths
        # self.accel_srv = None
        # self.aceel_period = None
        # self.magneto_srv = None
        # self.magneto_period = None
        # self.btn_srv = None
        # self._accel_data = None
        # self.io_pin_srv = None
        # self.led_srv = None
        # self.temp_srv = None
        # self.temp_period = None

    def _unsigned_int_from_bytes(self, byteval):
        """Convert a DBus Byte Array from the Microbit to an unsigned int."""
        return int.from_bytes(byteval, byteorder='little', signed=False)

    def _signed_int_from_bytes(self, byteval):
        """Convert a DBus Byte Array from the Microbit to a signed int."""
        return int.from_bytes(byteval, byteorder='little', signed=True)

    def _initialise_BLE(self):
        """Utility function to initialise the BLE interfaces."""
        self._led_scroll = GATT.Characteristic(LED_SCROLL)
        self._led_text = GATT.Characteristic(LED_TEXT)
        self._led_state = GATT.Characteristic(LED_STATE)
        self._temp_data = GATT.Characteristic(TEMP_DATA)
        self._btn_a_state = GATT.Characteristic(BTN_A_STATE)
        self._btn_b_state = GATT.Characteristic(BTN_B_STATE)
        self._accel_data = GATT.Characteristic(ACCEL_DATA)
        self._magneto_data = GATT.Characteristic(MAGNETO_DATA)
        self._magneto_bearing = GATT.Characteristic(MAGNETO_BEARING)
        self._io_pin_config = GATT.Characteristic(IO_PIN_CONFIG)
        self._io_ad_config = GATT.Characteristic(IO_AD_CONFIG)
        self._io_pin_pwm = GATT.Characteristic(IO_PIN_PWM)
        self._io_pin_data = GATT.Characteristic(IO_PIN_DATA)

        # Unused UUIDs, inherited from previous implementation
        # self.accel_srv = GATT.Service(ACCEL_SRV)
        # self.accel_period = GATT.Characteristic(ACCEL_PERIOD)
        # self.magneto_srv = GATT.Service(MAGNETO_SRV)
        # self.magneto_period = GATT.Characteristic(MAGNETO_PERIOD)
        # self.btn_srv = GATT.Service(BTN_SRV)
        # self.io_pin_srv = GATT.Service(IO_PIN_SRV)
        # self.led_srv = GATT.Service(LED_SRV)
        # self.temp_srv = GATT.Service(TEMP_SRV)
        # self.temp_period = GATT.Characteristic(TEMP_PERIOD)

    def _test_property_is_valid(self, prop_name):
        """
        Test that a property has been created and the ubit is connected.

        :param prop_name: name of the property to test
        :type prop_name: string
        """
        if self.connected is False:
            raise ConnectionError('Microbit is disconnected.')
        if getattr(self, prop_name) is None:
            raise ConnectionError('Haven\'t connected to the microbit')

    @property
    def connected(self):
        """Indicate whether the remote device is currently connected."""
        return self.ubit.connected

    def connect(self):
        """Connect to the microbit."""
        self.ubit.connect()
        while not self.ubit.services_resolved:
            sleep(0.5)
        self._initialise_BLE()

    def disconnect(self):
        """Disconnect from the microbit."""
        self.ubit.disconnect()

    @property
    def display_scroll_delay(self):
        """
        Specify the scroll delay.

        Specifies a millisecond delay to wait for in between showing each
        character on the display.
        """
        self._test_property_is_valid('_led_scroll')
        return self._unsigned_int_from_bytes(self._led_scroll.value)

    @display_scroll_delay.setter
    def display_scroll_delay(self, delay):
        """
        Specify the scroll delay.

        Specifies a millisecond delay to wait for in between showing each
        character on the display.
        """
        self._test_property_is_valid('_led_scroll')
        if delay < 0:
            delay = 0
        elif delay > 2**16:
            delay = 2**16
        self._led_scroll.value = tools.int_to_uint16(delay)

    def set_display_text(self, words):
        """
        Set the text to be displayed.

        Limit of 20 characters.  The content will be restricted to that number
        of characters.

        :param words: text to be displayed
        :type words: string
        """
        text = len(words) <= 20 and words or words[:19]
        self._led_text.value = [ord(letter) for letter in text]

    @property
    def display(self):
        """
        Get or set the state of the LED display.

        Returns a list of 5 binary numbers. Each number represents a row
        from top to bottom.

        To write, pass a 5 value list of 5 bit numbers representing each LED.

        To clear, set to 0

        :example:
        0b11111 will turn all LEDs in specified row on
        0b10101 will turn alternate LEDs on
        0b00000 will turn all LEDs in row off
        :param row0: top row
        :param row1:
        :param row2: middle row
        :param row3:
        :param row4: bottom row

        :return: Example [0b1110, 0b10000, 0b10000, 0b10000, 0b1110]
        """
        return [bin(i) for i in self._led_state.value]

    @display.setter
    def display(self, pixarray):
        if type(pixarray) is int and not pixarray:
            self._led_state.value = [0x00, 0x00, 0x00, 0x00, 0x00]
        elif len(pixarray) == 5:
            self._led_state.value = pixarray
        else:
            raise ValueError('LED display requires a pixel list of 5x 5-bit '
                             'values.  The array passed had {} values.'
                             .format(len(pixarray)))

    @property
    def temperature(self):
        """
        Read Microbit temperature sensors.

        :return: Integer of temperature in Celsius
        """
        self._test_property_is_valid('_temp_data')
        return self._signed_int_from_bytes(self._temp_data.value)

    @property
    def button_a(self):
        """
        Read the state of button A on a micro:bit.

        3 button states are defined and represented by a simple numeric
        enumeration:  0 = not pressed, 1 = pressed, 2 = long press.
        :return: integer representing button value
        """
        return self._unsigned_int_from_bytes(self._btn_a_state.value)

    @property
    def button_b(self):
        """
        Read the state of button B on a micro:bit.

        3 button states are defined and represented by a simple numeric
        enumeration:  0 = not pressed, 1 = pressed, 2 = long press.
        :return: integer representing button value
        """
        return self._unsigned_int_from_bytes(self._btn_b_state.value)

    def _button_prop_cb(self, value):
        """
        Default callback for button notifications.

        This function is provided as an example (and default) callback for
        receiving button notifications.

        :param value: the button state
        :type value: DBus array
        """
        print('Button is {}'.format(self._unsigned_int_from_bytes(value)))

    def subscribe_button_a(self, callback=None):
        """Subscribe to notifications on Button A.

        :param callback: function called when a button notification is received
        :type callback: function
        """
        if callback is None:
            callback = self._button_prop_cb
        self._btn_a_state.notify_cb = callback
        self._btn_a_state.notifying = True

    def subscribe_button_b(self, callback=None):
        """Subscribe to notifications on Button B.

        :param callback: function called when a button notification is received
        :type callback: function
        """
        if callback is None:
            callback = self._button_prop_cb
        self._btn_b_state.notify_cb = callback
        self._btn_b_state.notifying = True

    @property
    def accelerometer(self):
        """
        Read the values of the accelerometer on the microbit.

        :return: return a list in the order of x, y & z
        :rtype: list
        """
        return tools.bytes_to_xyz(self._accel_data.value)

    @property
    def magnetometer(self):
        """
        Expose magnetometer data.

        A magnetometer measures a magnetic field such
        as the earth's magnetic field in 3 axes.
        :return: List of x, y & z value
        """
        return tools.bytes_to_xyz(self._magneto_data.value)

    @property
    def bearing(self):
        """
        Compass bearing in degrees from North.

        :return: degrees in integer
        """
        return self._unsigned_int_from_bytes(self._magneto_bearing.value)

    @property
    def pin_io_config(self):
        """
        A bit mask (32 bit) which defines which inputs will be read.

        A value of 0 means configured for output and 1 means configured
        for input.
        """
        return self._io_pin_config.value

    @pin_io_config.setter
    def pin_io_config(self, states):
        """
        A bit mask (32 bit) which defines which inputs will be read.

        A value of 0 means configured for output and 1 means configured
        for input.
        """
        self._io_pin_config.value = states

    @property
    def pin_ad_config(self):
        """
        Analogue/Digital pin configuration.

        A bit mask (32 bit) which allows each pin to be configured for
        analogue or digital use.
        A value of 0 means digital and 1 means analogue.
        """
        return self._io_ad_config.value

    @pin_ad_config.setter
    def _pin_ad_config(self, states):
        """
        Analogue/Digital pin configuration.

        A bit mask (32 bit) which allows each pin to be configured for
        analogue or digital use.
        A value of 0 means digital and 1 means analogue.
        """
        self._io_ad_config.value = states

    @property
    def pin_states(self):
        """
        Pin States.

        Contains data relating to zero or more pins.

        Structured as a variable length list of up to 19 Pin
        Number / Value pairs.
        """
        return self._io_pin_data.value

    @pin_states.setter
    def pin_states(self, pin_value_pairs):
        """
        Pin States.

        Contains data relating to zero or more pins.

        Structured as a variable length list of up to 19 Pin
        Number / Value pairs.
        """
        self._io_pin_data.value = pin_value_pairs

    @property
    def pin_pwm_control(self):
        """
        The PWM control data.

        :param pin: pin number [range 0-19]
        :param value: Value is in the range 0 to 1024, per the current DAL API
            (e.g. setAnalogValue). 0 means OFF.
        :param period: Period is in microseconds and is an unsigned integer
        :return:
        """
        return self._io_pin_pwm.value

    @pin_pwm_control.setter
    def pin_pwm_control(self, pwm_data):
        """
        Write only method to set the PWM control data.

        :param pwm_data: a three member list as follows: [pin, value, period]
        - pin: pin number [range 0-19]
        - value: value is in the range 0 to 1024, per the current DAL API
                 (e.g. setAnalogValue). 0 means OFF.
        - period: period is in microseconds and is an unsigned integer
        :type pwm_data: list
        """
        byte_value = tools.int_to_uint16(pwm_data[1])
        byte_period = tools.int_to_uint32(pwm_data[2])
        pwm_value = [[pwm_data[0]], byte_value, byte_period]
        self._io_pin_pwm.value = list(itertools.chain.from_iterable(pwm_value))

    def play_beep(self, duration):
        """
        If a buzzer is attached to pin 0 then a beep will be played.

        :param duration: time in seconds
        """
        self.pin_pwm_control = [0, 512, 2094]
        sleep(duration)
        self.pin_pwm_control = [0, 0, 0]


class BitBot(Microbit):
    """
    Class to simplify interacting with a bit:bot over Bluetooth Low Energy.

    A Bit:bot is a robot controlled by a microbit.
    """

    def __init__(self, name=None, address=None):
        """
        Initialization of an instance of a remote bit:bot.

        :param name: Will look for a BLE device with this string in its name
        :param address: Will look for a BLE device with this address
        """
        self._inputs_configured = False
        self.left_light = False
        super(BitBot, self).__init__(self, name, address)

    def stop(self):
        """Stop both wheels of the bit:bot."""
        self.pin_states = [0x01, 0x00, 0x0C, 0x00, 0x00, 0x00, 0x08, 0x00]

    def spin_right(self):
        """Spin right wheel forward and left wheel backwards."""
        self.pin_states = [0x01, 0x01, 0x0C, 0x00, 0x00, 0x00, 0x08, 0x01]

    def spin_left(self):
        """Spin left wheel forward and right wheel backwards."""
        self.pin_states = [0x01, 0x00, 0x0C, 0x01, 0x00, 0x01, 0x08, 0x00]

    def forward(self):
        """Spin both wheels forward."""
        self.pin_states = [0x01, 0x01, 0x0C, 0x00, 0x00, 0x01, 0x08, 0x00]

    def reverse(self):
        """Spin both wheels backwards."""
        self.pin_states = [0x01, 0x00, 0x0C, 0x01, 0x00, 0x00, 0x08, 0x01]

    def _left_motor(self, pwm_value, reverse=False):
        """
        Move the left motor.

        :param pwm_value: value for the PWM output
        :param reverse: (optional) runs the motor in reverse.
        :type pwm_value: integer between 0 and 1023.  0 is off.
        :type reverse: boolean
        """
        if not reverse:
            self.pin_states = [0x08, 0x00]
        else:
            self._pin_states = [0x08, 0x01]
        self.pin_pwm_control = [0, pwm_value, 20000]

    def _right_motor(self, pwm_value, reverse=False):
        """
        Move the right motor.

        :param pwm_value: value for the PWM output
        :param reverse: (optional) runs the motor in reverse.
        :type pwm_value: integer between 0 and 1023.  0 is off.
        :type reverse: boolean
        """
        if not reverse:
            self.pin_states = [0x0C, 0x00]
        else:
            self.pin_states = [0x0C, 0x01]
        self.pin_pwm_control = [1, pwm_value, 20000]

    def _update_motors(self, left_val, right_val,
                       left_rev, right_rev,
                       pwm_period=20000):
        """Update motors using the PWM characteristic.

        :param left_val: value for the left motor.
        :param right_val: value for the right motor.
        :param left_rev: whether the left motor reverses.
        :param right_rev: whether the right motor reverses.
        :param pwm_period: period for the PWM signal.
        :type left_val: unsigned integer
        :type right_val: unsigned integer
        :type left_rev: boolean
        :type right_rev: boolean
        :type pwm_period: unsigned integer
        """
        period = tools.int_to_uint32(pwm_period)
        left_pwm = tools.int_to_uint16(left_val)
        right_pwm = tools.int_to_uint16(right_val)
        pwm_value = [[0], left_pwm, period, [1], right_pwm, period]
        self._io_pin_pwm.value = list(itertools.chain.from_iterable(pwm_value))
        self.pin_states = [0x08, left_rev, 0x0C, right_rev]

    def drive(self, left=100, right=100):
        """
        Drive the motors.

        :param left: percentage drive of the left motor (-100 to +100)
        :param right: percentage drive of the right motor (-100 to +100)
        :type left: signed integer
        :type right: signed integer
        """
        left_dir = left < 0 and 1 or 0
        left_motor = self._percentage_to_pwm(left)

        right_dir = right < 0 and 1 or 0
        right_motor = self._percentage_to_pwm(right)

        self._update_motors(left_motor, right_motor, left_dir, right_dir)

    def _percentage_to_pwm(self, percent):
        """
        Convert a percentage drive strength to a motor PWM drive strength.

        :param percent: drive strength of the motor
        :type percent: signed integer (percent)
        """
        return int(10.23 * abs(percent))

    def buzzer_on(self):
        """Play the buzzer."""
        self.pin_states = [0x0E, 0x01]

    def buzzer_off(self):
        """Stop the buzzer."""
        self.pin_states = [0x0E, 0x00]

    @property
    def left_line(self):
        """
        Read the left line sensor.

        :return: False = No line  True = Line
        :rtype: Boolean
        """
        return bool(self._get_pin_value(11))

    @property
    def right_line(self):
        """
        Read the right line sensor.

        :return: False = No line  True = Line
        :rtype: Boolean
        """
        return bool(self._get_pin_value(5))

    @property
    def lines(self):
        """Lines."""
        if not self._inputs_configured:
            self._config_inputs()
            self._inputs_configured = True
        pins = self.pin_states
        return [bool(pins[x]) for x in [3, 5]]

    @property
    def left_light(self):
        """Left light state."""
        self.pin_states = [0x10, 0x00]
        return int(self._get_pin_value(2))

    @property
    def right_light(self):
        """Right light state."""
        self.pin_states = [0x10, 0x01]
        return int(self._get_pin_value(2))

    def _config_inputs(self):
        """Configure inputs."""
        self._pin_config = [0x24, 0x08, 0x00, 0x00]
        self._pin_ad_config = [0x04, 0x00, 0x00, 0x00]

    def _build_pin_value_pairs(self, pin_states):
        """
        Convert pin states from the bitbot into pin - value pairs.

        :param pin_states: list of pin states
        """
        val_dict = {}
        if len(pin_states) > 0:
            val_dict = dict(zip(pin_states[::2], pin_states[1::2]))
        return val_dict

    def _get_pin_value(self, pin):
        """
        Get the value of a particular pin.

        :param pin: pin to return the value of
        :type pin: integer
        """
        if not self.inputs_configured:
            self._config_inputs()
            self.inputs_configured = True
        pin_value_pairs = self._build_pin_value_pairs(self._pin_states())
        if pin in pin_value_pairs.keys():
            return pin_value_pairs[pin]
        else:
            return None
