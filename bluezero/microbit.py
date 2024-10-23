"""
This is a simple API for reading data from a micro:bit.

You will need the Bluetooth services on the micro:bit exposed.

This code was developed using the 'Bluetooth Most Services, No Security'
micro:bit hex file from:
http://www.bittysoftware.com/downloads.html
The hex file called "For micro:bit Blue - Main Bluetooth services,
pairing not required" was used.

The following link is a good reference for Bluetooth on the microbit
http://bluetooth-mdw.blogspot.co.uk/p/bbc-microbit.html
"""
from time import sleep

from bluezero import central
from bluezero import tools
from bluezero import constants

ACCEL_SRV = 'E95D0753-251D-470A-A062-FA1922DFA9A8'
ACCEL_DATA = 'E95DCA4B-251D-470A-A062-FA1922DFA9A8'
ACCEL_PERIOD = 'E95DFB24-251D-470A-A062-FA1922DFA9A8'
BTN_SRV = 'E95D9882-251D-470A-A062-FA1922DFA9A8'
BTN_A_STATE = 'E95DDA90-251D-470A-A062-FA1922DFA9A8'
BTN_B_STATE = 'E95DDA91-251D-470A-A062-FA1922DFA9A8'
LED_SRV = 'E95DD91D-251D-470A-A062-FA1922DFA9A8'
LED_STATE = 'E95D7B77-251D-470A-A062-FA1922DFA9A8'
LED_TEXT = 'E95D93EE-251D-470A-A062-FA1922DFA9A8'
LED_SCROLL = 'E95D0D2D-251D-470A-A062-FA1922DFA9A8'
MAGNETO_SRV = 'E95DF2D8-251D-470A-A062-FA1922DFA9A8'
MAGNETO_DATA = 'E95DFB11-251D-470A-A062-FA1922DFA9A8'
MAGNETO_PERIOD = 'E95D386C-251D-470A-A062-FA1922DFA9A8'
MAGNETO_BEARING = 'E95D9715-251D-470A-A062-FA1922DFA9A8'
MAGNETO_CALIBRATE = 'E95DB358-251D-470A-A062-FA1922DFA9A8'
IO_PIN_SRV = 'E95D127B-251D-470A-A062-FA1922DFA9A8'
IO_PIN_DATA = 'E95D8D00-251D-470A-A062-FA1922DFA9A8'
IO_AD_CONFIG = 'E95D5899-251D-470A-A062-FA1922DFA9A8'
IO_PIN_CONFIG = 'E95DB9FE-251D-470A-A062-FA1922DFA9A8'
IO_PIN_PWM = 'E95DD822-251D-470A-A062-FA1922DFA9A8'
TEMP_SRV = 'E95D6100-251D-470A-A062-FA1922DFA9A8'
TEMP_DATA = 'E95D9250-251D-470A-A062-FA1922DFA9A8'
TEMP_PERIOD = 'E95D1B25-251D-470A-A062-FA1922DFA9A8'
UART_SRV = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
UART_TX = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
UART_RX = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'

MICROBIT = {ACCEL_SRV: [ACCEL_DATA, ACCEL_PERIOD],
            BTN_SRV: [BTN_A_STATE, BTN_B_STATE],
            LED_SRV: [LED_STATE, LED_TEXT, LED_SCROLL],
            MAGNETO_SRV: [MAGNETO_DATA, MAGNETO_PERIOD,
                          MAGNETO_BEARING, MAGNETO_CALIBRATE],
            IO_PIN_SRV: [IO_PIN_DATA, IO_AD_CONFIG, IO_PIN_CONFIG, IO_PIN_PWM],
            TEMP_SRV: [TEMP_DATA, TEMP_PERIOD],
            UART_SRV: [UART_TX, UART_RX]}
SERVICE_NAMES = {ACCEL_SRV: 'Accelerometer Service',
                 BTN_SRV: 'Button Service',
                 LED_SRV: 'LED Service',
                 MAGNETO_SRV: 'Magnetometer Service',
                 IO_PIN_SRV: 'IO Pin Service',
                 TEMP_SRV: 'Temperature Service',
                 UART_SRV: 'Nordic Semiconductor UART service',
                 }
logger = tools.create_module_logger(__name__)


class Microbit:
    """
    Class to simplify interacting with a micro:bit over Bluetooth Low Energy
    """
    def __init__(self, device_addr, adapter_addr=None, **kwargs):
        """
        Initialization of an instance of a remote micro:bit

        :param device_addr: Discovered microbit device with this address
        :param adapter_addr: Optional unless you have more than one adapter
                             on your machine
        """
        legacy_params = ['accelerometer_service', 'button_service',
                         'led_service', 'magnetometer_service',
                         'pin_service', 'temperature_service',
                         'uart_service']
        for kwarg in kwargs:
            if kwarg in legacy_params:
                logger.warning('The parameter %s has been deprecated. There '
                               'is no longer a requirement to specify which '
                               'services the micro:bit has.\nYou will get an '
                               'Error in the log if you access a '
                               'characteristic that does not exist on '
                               'micro:bit')
        self.ubit = central.Central(adapter_addr=adapter_addr,
                                    device_addr=device_addr)

        self.user_pin_callback = None
        self.user_btn_a_callback = None
        self.user_btn_b_callback = None
        self.user_calibrate_cb = None
        self.uart_tx_cb = None
        self.user_accel_cb = None

        # Micro:bit Characteristics
        # if accelerometer_service:
        self._accel_data = self.ubit.add_characteristic(ACCEL_SRV,
                                                        ACCEL_DATA)
        self._accel_period = self.ubit.add_characteristic(ACCEL_SRV,
                                                          ACCEL_PERIOD)
        # if button_service:
        self._btn_a_state = self.ubit.add_characteristic(BTN_SRV,
                                                         BTN_A_STATE)
        self._btn_b_state = self.ubit.add_characteristic(BTN_SRV,
                                                         BTN_B_STATE)
        # if led_service:
        self._led_state = self.ubit.add_characteristic(LED_SRV,
                                                       LED_STATE)
        self._led_text = self.ubit.add_characteristic(LED_SRV,
                                                      LED_TEXT)
        self._led_scroll = self.ubit.add_characteristic(LED_SRV,
                                                        LED_SCROLL)
        # if magnetometer_service:
        self._magneto_data = self.ubit.add_characteristic(
            MAGNETO_SRV,
            MAGNETO_DATA)
        self._magneto_period = self.ubit.add_characteristic(
            MAGNETO_SRV,
            MAGNETO_PERIOD)
        self._magneto_bearing = self.ubit.add_characteristic(
            MAGNETO_SRV,
            MAGNETO_BEARING)
        self._magneto_calibrate = self.ubit.add_characteristic(
            MAGNETO_SRV,
            MAGNETO_CALIBRATE)
        # if pin_service:
        self._io_pin_data = self.ubit.add_characteristic(IO_PIN_SRV,
                                                         IO_PIN_DATA)
        self._io_ad_config = self.ubit.add_characteristic(IO_PIN_SRV,
                                                          IO_AD_CONFIG)
        self._io_pin_config = self.ubit.add_characteristic(IO_PIN_SRV,
                                                           IO_PIN_CONFIG)
        self._io_pin_pwm = self.ubit.add_characteristic(IO_PIN_SRV,
                                                        IO_PIN_PWM)
        # if temperature_service:
        self._temp_data = self.ubit.add_characteristic(TEMP_SRV,
                                                       TEMP_DATA)
        self._temp_period = self.ubit.add_characteristic(TEMP_SRV,
                                                         TEMP_PERIOD)
        # if uart_service:
        self._uart_tx = self.ubit.add_characteristic(UART_SRV,
                                                     UART_TX)
        self._uart_rx = self.ubit.add_characteristic(UART_SRV,
                                                     UART_RX)

    @staticmethod
    def available(adapter_address=None):
        """
        Generator to find already discovered micro:bit's and return a tuple
        of their address and name

        :param adapter_address: Optional if you want o find devices on specific
         adapter
        :return: Microbit Object
        """
        for ubit in central.Central.available(adapter_address):
            if ubit.name and 'micro:bit' in ubit.name:
                yield Microbit(device_addr=ubit.address,
                               adapter_addr=ubit.adapter)

    def services_available(self):
        """Return a list of service names available on this micro:bit"""
        named_services = []
        for service in self.ubit.services_available:
            if service.upper() in SERVICE_NAMES:
                named_services.append(SERVICE_NAMES[service.upper()])
        return named_services

    @property
    def name(self):
        """Read the devices Bluetooth address"""
        return self.ubit.rmt_device.name

    @property
    def address(self):
        """Read the devices Bluetooth address"""
        return self.ubit.rmt_device.address

    @property
    def connected(self):
        """Indicate whether the remote device is currently connected."""
        return self.ubit.connected

    def connect(self):
        """
        Connect to the specified micro:bit for this instance
        """
        self.ubit.connect()

    def disconnect(self):
        """
        Disconnect from the micro:bit
        """
        self.ubit.disconnect()

    @property
    def scroll_delay(self):
        """
        Specifies a millisecond delay to wait for in between showing each
        character on the display.
        """
        return int.from_bytes(self._led_scroll.value,
                              byteorder='little',
                              signed=False)

    @scroll_delay.setter
    def scroll_delay(self, delay=None):
        """
        Specifies a millisecond delay to wait for in between showing each
        character on the display.
        """
        if delay < 0:
            delay = 0
        elif delay > 2**16:
            delay = 2**16
        self._led_scroll.value = tools.int_to_uint16(delay)

    @property
    def text(self):
        """
        Specify text to be displayed. Limit of 20 characters.
        The content will be restricted to that number of characters.

        :param words:
        """
        pass

    @text.setter
    def text(self, words):
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
        self._led_text.value = data

    def _write_pixels(self, data):
        """
        Utility function for the different display functions

        :param data: list of 5 numbers in the range 0 to 255
        (e.g. [0xff, 0x00, 0, 255, 0b10101]
        """

        self._led_state.value = data

    def clear_display(self):
        """
        Clear the LED display on the microbit
        """
        self._write_pixels([0x00, 0x00, 0x00, 0x00, 0x00])

    @property
    def pixels(self):
        """
        Returns a list of 5 binary numbers. Each number represents a row
        from top to bottom

        :return: Example [0b01110, 0b01000, 0b10000, 0b10000, 0b01110]
        """
        rows = self._led_state.value
        return [int(i) for i in rows]

    @pixels.setter
    def pixels(self, rows):
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
        self._write_pixels([rows[0], rows[1], rows[2], rows[3], rows[4]])

    @property
    def temperature(self):
        """
        Temperature from sensors in micro:bit processors

        :return: Integer of temperature in Celsius
        """
        tmp_val = self._temp_data.value

        return int.from_bytes(tmp_val, byteorder='little', signed=True)

    @property
    def button_a(self):
        """
        Read the state of button A on a micro:bit
        3 button states are defined and represented by a simple numeric
        enumeration:  0 = not pressed, 1 = pressed, 2 = long press.

        :return: integer representing button value
        """
        btn_val = self._btn_a_state.value

        return int.from_bytes(btn_val, byteorder='little', signed=False)

    @property
    def button_b(self):
        """
        Read the state of button B on a micro:bit
        3 button states are defined and represented by a simple numeric
        enumeration:  0 = not pressed, 1 = pressed, 2 = long press.

        :return: integer representing button value
        """
        btn_val = self._btn_b_state.value

        return int.from_bytes(btn_val, byteorder='little', signed=False)

    def _decode_btn_a(self, *button_values):
        """Decode button A state and pass on to user callback."""
        if 'Value' in button_values[1]:
            self.user_btn_a_callback(int(button_values[1]['Value'][0]))

    def _decode_btn_b(self, *button_values):
        """Decode button B state and pass on to user callback."""
        if 'Value' in button_values[1]:
            self.user_btn_b_callback(int(button_values[1]['Value'][0]))

    def subscribe_button_a(self, user_callback):
        """
        Execute user_callback on Button A being press on micro:bit

        :param user_callback: User callback method receiving the button state
        :return:
        """
        self.user_btn_a_callback = user_callback
        self._btn_a_state.add_characteristic_cb(self._decode_btn_a)
        self._btn_a_state.start_notify()

    def subscribe_button_b(self, user_callback):
        """
        Execute user_callback on Button B being press on micro:bit

        :param user_callback: User callback method receiving the button state
        :return:
        """
        self.user_btn_b_callback = user_callback
        self._btn_b_state.add_characteristic_cb(self._decode_btn_b)
        self._btn_b_state.start_notify()

    def _decode_pins(self, *pin_values):
        if pin_values[0] != 'org.bluez.GattCharacteristic1':
            return
        if 'Value' in pin_values[1]:
            self.user_pin_callback(int(pin_values[1]['Value'][0]),
                                   int(pin_values[1]['Value'][1]))

    def subscribe_pins(self, user_callback):
        """
        Execute user_callback on input pin being changed on micro:bit

        :param user_callback:
        :return:
        """
        self.user_pin_callback = user_callback
        self._io_pin_data.add_characteristic_cb(self._decode_pins)
        self._io_pin_data.start_notify()

    @property
    def accelerometer(self):
        """
        Read the values of the accelerometer on the microbit

        :return: return a list in the order of x, y & z
        """
        # [16, 0, 64, 0, 32, 252]
        # x=0.16, y=0.024, z=-0.992
        accel_bytes = self._accel_data.value

        return tools.bytes_to_xyz(accel_bytes)

    def _decode_accel(self, *accel_values):
        """Decode accelerometer values and pass on to user callback."""
        self.user_accel_cb(*tools.bytes_to_xyz(accel_values[1]['Value']))

    def subscribe_accelerometer(self, user_callback):
        """
        Execute user_callback on data being received on accelerometer service

        :param user_callback: User callback method receiving the accelerometer
            values
        :return:
        """
        self.user_accel_cb = user_callback
        self._accel_data.add_characteristic_cb(self._decode_accel)
        self._accel_data.start_notify()

    @property
    def magnetometer(self):
        """
        Exposes magnetometer data.
        A magnetometer measures a magnetic field such
        as the earth's magnetic field in 3 axes.

        :return: List of x, y & z value
        """
        mag_bytes = self._magneto_data.value

        return tools.bytes_to_xyz(mag_bytes)

    @property
    def bearing(self):
        """
        Compass bearing in degrees from North.

        :return: degrees in integer
        """
        mag_bear_val = self._magneto_bearing.value

        return int.from_bytes(mag_bear_val,
                              byteorder='little', signed=False)

    def calibrate(self):
        """
        Request a calibration of the magnetometer
        """
        self._magneto_calibrate.value = 0x01

    def subscribe_calibrate(self, user_callback):
        """
        Execute user_callback when calibration of magnetometer is complete

        :param user_callback:
        :return:
        """
        self.user_calibrate_cb = user_callback
        self._magneto_calibrate.add_characteristic_cb(self._magneto_cal_cb)
        self._magneto_calibrate.start_notify()

    def _magneto_cal_cb(self, iface, changed_props, invalidated_props):
        if iface != 'org.bluez.GattCharacteristic1':
            return
        if 'Value' in changed_props:
            self.user_calibrate_cb(int(changed_props['Value'][0]))

    def set_pin(self, pin_number, pin_input, pin_analogue):
        """
        For a given pin, set the direction and type for the microbit pin.

        :param pin_number: Pin number of the microbit
        :param pin_input: False for output, True for input
        :param pin_analogue: False for digital, True for analogue
        :return:
        """
        pin_bit = tools.int_to_uint32(2 ** pin_number)
        current_io_setting = self._pin_config
        current_ad_setting = self._pin_ad_config
        if pin_input:
            new_setting = tools.bitwise_or_2lists(pin_bit, current_io_setting)
            self._pin_config = new_setting
        else:
            pin_mask = tools.bitwise_xor_2lists(pin_bit,
                                                [0xff, 0xff, 0xff, 0xff])
            new_setting = tools.bitwise_and_2lists(pin_mask,
                                                   current_io_setting)
            self._pin_config = new_setting
        if pin_analogue:
            new_setting = tools.bitwise_or_2lists(pin_bit,
                                                  current_ad_setting)
            self._pin_ad_config = new_setting
        else:
            pin_mask = tools.bitwise_xor_2lists(pin_bit,
                                                [0xff, 0xff, 0xff, 0xff])
            new_setting = tools.bitwise_and_2lists(pin_mask,
                                                   current_ad_setting)
            self._pin_ad_config = new_setting

    @property
    def _pin_config(self):
        """
        A bit mask (32 bit) which defines which inputs will be read.
        A value of 0 means configured for output and 1 means configured
        for input.
        """
        return_val = []
        current_setting = self._io_pin_config.value
        for i in range(len(current_setting)):
            return_val.append(int(current_setting[i]))
        return return_val

    @_pin_config.setter
    def _pin_config(self, states):
        """
        A bit mask (32 bit) which defines which inputs will be read.
        A value of 0 means configured for output and 1 means configured
        for input.
        """
        self._io_pin_config.value = states

    @property
    def _pin_ad_config(self):
        """
        A bit mask (32 bit) which allows each pin to be configured for
        analogue or digital use.
        A value of 0 means digital and 1 means analogue.
        If no states are specified then the current state is returned
        """
        return_val = []
        current_setting = self._io_ad_config.value
        for i in range(len(current_setting)):
            return_val.append(int(current_setting[i]))
        return return_val

    @_pin_ad_config.setter
    def _pin_ad_config(self, states):
        """
        A bit mask (32 bit) which allows each pin to be configured for
        analogue or digital use.
        A value of 0 means digital and 1 means analogue.
        If no states are specified then the current state is returned
        """
        self._io_ad_config.value = states

    @property
    def _pin_states(self):
        """
        Contains data relating to zero or more pins.
        Structured as a variable length list of up to 19 Pin
        Number / Value pairs.
        """
        return self._io_pin_data.value

    @_pin_states.setter
    def _pin_states(self, pin_value_pairs):
        """
        Contains data relating to zero or more pins.
        Structured as a variable length list of up to 19 Pin
        Number / Value pairs.
        """
        self._io_pin_data.value = pin_value_pairs

    @property
    def pin_values(self):
        """
        Get the values of all the pins that are set as inputs

        :return: Dictionary (keys are pins)
        """
        return_dict = {}
        values = self._io_pin_data.value
        for i in range(0, len(values), 2):
            return_dict[str(int(values[i]))] = int(values[i + 1])
        return return_dict

    @property
    def _pin_pwm_control(self):
        """
        Write only method to set the PWM control data

        :param pin: pin number [range 0-19]
        :param value: Value is in the range 0 to 1024, per the current DAL API
            (e.g. setAnalogValue). 0 means OFF.
        :param period: Period is in microseconds and is an unsigned integer
        :return:
        """
        return self._io_pin_pwm.value

    @_pin_pwm_control.setter
    def _pin_pwm_control(self, data):
        """
        Write only method to set the PWM control data

        :param pin: pin number [range 0-19]
        :param value: Value is in the range 0 to 1024, per the current DAL API
            (e.g. setAnalogValue). 0 means OFF.
        :param period: Period is in microseconds and is an unsigned integer
        :return:
        """
        pin = data[0]
        value = data[1]
        period = data[2]
        byte_value = tools.int_to_uint16(value)
        byte_period = tools.int_to_uint32(period)
        self._io_pin_pwm.value = [pin,
                                  byte_value[0],
                                  byte_value[1],
                                  byte_period[0],
                                  byte_period[1],
                                  byte_period[2],
                                  byte_period[3]
                                  ]

    @property
    def uart(self):
        """
        Write string to micro:bit UART service. To read from UART, use

        :return:
        """
        pass

    @uart.setter
    def uart(self, txt):
        data = []
        text = ''
        if len(txt) > 20:
            text = txt[:19]
        else:
            text = txt
        for letter in text:
            data.append(ord(letter))
        self._uart_rx.value = data

    def subscribe_uart(self, user_callback):
        """
        Execute user_callback on data being received on UART service

        :param user_callback:
        :return:
        """
        self.uart_tx_cb = user_callback
        self._uart_tx.add_characteristic_cb(self._uart_read)
        self._uart_tx.start_notify()

    def _uart_read(self, iface, changed_props, invalidated_props):
        if iface != constants.GATT_CHRC_IFACE:
            return
        if 'Value' in changed_props:
            self.uart_tx_cb(''.join([str(v) for v in changed_props['Value']]))

    @property
    def on_disconnect(self):
        """Add callback for on_disconnect action"""
        return self.ubit.dongle.on_disconnect

    @on_disconnect.setter
    def on_disconnect(self, callback):
        self.ubit.dongle.on_disconnect = callback

    def run_async(self):
        """
        Puts the code into asynchronous mode

        :return:
        """
        self.ubit.run()

    def quit_async(self):
        """
        Stops asynchronous mode

        :return:
        """
        self.ubit.quit()


class MIpower(Microbit):
    """
    Initialization of an instance of a remote micro:bit
    with a MI:power board attached

    :param device_addr: Connect to a BLE device with this address
    :param adapter_addr: Use the adapter with this address
    """
    def __init__(self, device_addr, adapter_addr=None,
                 accelerometer_service=True,
                 button_service=True,
                 led_service=True,
                 magnetometer_service=False,
                 pin_service=False,
                 temperature_service=True
                 ):

        Microbit.__init__(self, device_addr, adapter_addr,
                          accelerometer_service=accelerometer_service,
                          button_service=button_service,
                          led_service=led_service,
                          magnetometer_service=magnetometer_service,
                          pin_service=pin_service,
                          temperature_service=temperature_service)

    def beep(self, duration=1):
        """
        If a buzzer is attached to pin 0 then a beep will be played

        :param duration: time in seconds
        """
        self._pin_pwm_control = [0, 512, 2094]
        sleep(duration)
        self._pin_pwm_control = [0, 0, 0]


class BitBot:
    """
    Class to simplify interacting with a microbit attached to a bit:bot
    over Bluetooth Low Energy
    The bit:bot is a micro:bit robot available from 4tronix.co.uk
    """
    def __init__(self, device_addr, adapter_addr=None,
                 accelerometer_service=False,
                 button_service=True,
                 led_service=True,
                 magnetometer_service=False,
                 pin_service=True,
                 temperature_service=False):
        """
        Initialization of an instance of a remote bit:bot

        :param name: Will look for a BLE device with this string in its name
        :param device_addr: Will look for a BLE device with this address
        """
        self._pins_configured = False
        self.ubit = Microbit(device_addr, adapter_addr,
                             accelerometer_service=accelerometer_service,
                             button_service=button_service,
                             led_service=led_service,
                             magnetometer_service=magnetometer_service,
                             pin_service=pin_service,
                             temperature_service=temperature_service)

    def __enter__(self):
        return self

    def __del__(self):
        self.clean_up()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clean_up()

    def clean_up(self):
        """
        Stop bitbot and turn buzzer is off

        :return:
        """
        if self.connected:
            self.stop()
            self.buzzer_off()

    def connect(self):
        """
        Connect to the bit:bot
        """
        self.ubit.connect()
        self._config_pins()

    def disconnect(self):
        """
        Disconnect from the bit:bot
        """
        self.clean_up()
        self.ubit.disconnect()

    @property
    def connected(self):
        """
        Returns true if bit:bot is connected
        """
        return self.ubit.connected

    def stop(self):
        """
        Stop both wheels of the bit:bot
        """
        self.ubit._pin_states = [0x01, 0x00,
                                 0x0C, 0x00,
                                 0x00, 0x00,
                                 0x08, 0x00]

    def spin_right(self):
        """
        Spin right wheel forward and left wheel backwards so bit:bot spins
        """
        self.ubit._pin_states = [0x01, 0x01,
                                 0x0C, 0x00,
                                 0x00, 0x00,
                                 0x08, 0x01]

    def spin_left(self):
        """
        Spin left wheel forward and right wheel backwards so bit:bot spins
        """
        self.ubit._pin_states = [0x01, 0x00,
                                 0x0C, 0x01,
                                 0x00, 0x01,
                                 0x08, 0x00]

    def forward(self):
        """
        Spin both wheels forward
        """
        self.ubit._pin_states = [0x01, 0x01,
                                 0x0C, 0x00,
                                 0x00, 0x01,
                                 0x08, 0x00]

    def reverse(self):
        """
        Spin both wheels backwards
        """
        self.ubit._pin_states = [0x01, 0x00,
                                 0x0C, 0x01,
                                 0x00, 0x00,
                                 0x08, 0x01]

    def _left_motor(self, pwm_value, reverse=False):
        if not reverse:
            self.ubit._pin_states = [0x08, 0x00]
        else:
            self.ubit._pin_states = [0x08, 0x01]
        self.ubit._pin_pwm_control = [0, pwm_value, 20000]

    def _right_motor(self, pwm_value, reverse=False):
        if not reverse:
            self.ubit._pin_states = [0x0C, 0x00]
        else:
            self.ubit._pin_states = [0x0C, 0x01]
        self.ubit._pin_pwm_control = [1, pwm_value, 20000]

    def _update_motors(self, left_val, right_val,
                       left_rev, right_rev,
                       pwm_period=20000):
        period = tools.int_to_uint32(pwm_period)
        left_pwm = tools.int_to_uint16(left_val)
        right_pwm = tools.int_to_uint16(right_val)
        self.ubit._io_pin_pwm.value = [0,
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
                                       ]
        self.ubit._pin_states = [0x08, left_rev, 0x0C, right_rev]

    def drive(self, left=100, right=100):
        """
        Set the drive power of both wheels at same time

        :param left: percentage of power (negative numbers are reverse)
        :param right: percentage of power (negative numbers are reverse)
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
        self.ubit._pin_states = [0x0E, 0x01]

    def buzzer_off(self):
        """
        Stop the buzzer
        """
        self.ubit._pin_states = [0x0E, 0x00]

    @property
    def left_line_senor(self):
        """
        Value ofthe left line sensor

        :return: False = No line  True = Line
        """
        return bool(self._get_pin_value(11))

    @property
    def right_line_sensor(self):
        """
        Value of the right line sensor

        :return: False = No line  True = Line
        """
        return bool(self._get_pin_value(5))

    @property
    def line_sensors(self):
        """
        Get the value of both line sensors

        :return: (left, right)
        """
        if not self._pins_configured:
            self._config_pins()
            self._pins_configured = True
        pins = self.ubit._pin_states
        return bool(pins[3]), bool(pins[5])

    @property
    def left_light_sensor(self):
        """
        Get the value of the left light sensor
        """
        self.ubit._pin_states = [0x10, 0x00]
        return int(self._get_pin_value(2))

    @property
    def right_light_sensor(self):
        """
        Get the value of the left light sensor
        """
        self.ubit._pin_states = [0x10, 0x01]
        return int(self._get_pin_value(2))

    def _config_pins(self):
        self.ubit._pin_config = [0x24, 0x08, 0x00, 0x00]
        self.ubit._pin_ad_config = [0x04, 0x00, 0x00, 0x00]

    def _build_pin_value_pairs(self, pin_states):
        val_dict = {}
        if len(pin_states) > 0:
            val_dict = dict(zip(pin_states[::2], pin_states[1::2]))
        return val_dict

    def _get_pin_value(self, pin):
        if not self._pins_configured:
            self._config_pins()
            self._pins_configured = True
        pin_value_pairs = self._build_pin_value_pairs(self.ubit._pin_states)
        if pin in pin_value_pairs.keys():
            return pin_value_pairs[pin]
        else:
            return None


class BitCommander:
    """
    Class to simplify interacting with a microbit attached to a bit:commander
    over Bluetooth Low Energy
    The bit:commander is a micro:bit controller available from 4tronix.co.uk
    """
    def __init__(self, device_addr, adapter_addr=None,
                 accelerometer_service=True,
                 button_service=True,
                 led_service=True,
                 magnetometer_service=False,
                 pin_service=False,
                 temperature_service=True):
        """
        Initialization of an instance of a remote bit:bot

        :param name: Will look for a BLE device with this string in its name
        :param device_addr: Will look for a BLE device with this address
        """
        self._pins_configured = False
        self.ubit = Microbit(device_addr, adapter_addr,
                             accelerometer_service=accelerometer_service,
                             button_service=button_service,
                             led_service=led_service,
                             magnetometer_service=magnetometer_service,
                             pin_service=pin_service,
                             temperature_service=temperature_service)

    def __enter__(self):
        return self

    def __del__(self):
        self.clean_up()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clean_up()

    def clean_up(self):
        """Put BitCommander back to known state"""
        if self.connected:
            pass

    def connect(self):
        """
        Connect to the bit:bot
        """
        self.ubit.connect()
        self._config_pins()

    def disconnect(self):
        """
        Disconnect from the bit:bot
        """
        self.clean_up()
        self.ubit.disconnect()

    @property
    def connected(self):
        """
        Returns true if bit:bot is connected
        """
        return self.ubit.connected

    def _config_pins(self):
        # Buttons
        self.ubit.set_pin(12, True, False)
        self.ubit.set_pin(14, True, False)
        self.ubit.set_pin(15, True, False)
        self.ubit.set_pin(16, True, False)
        # Dial
        self.ubit.set_pin(2, True, True)
        # Joy sticks
        self.ubit.set_pin(8, True, False)
        self.ubit.set_pin(1, True, True)
        self.ubit.set_pin(0, True, True)
        self._pins_configured = True

    def subscribe_pins(self, user_cb):
        """
        Get notification when pins configured as input values change

        :param user_cb: User callback to call when change happens
        :return:
        """
        self.ubit.subscribe_pins(user_cb)

    @property
    def joystick(self):
        """
        The value of the joystick as a list of x, y and z
        x and y are analogue values in the range -255 to 255
        z is a button with a binary value of 1 for pressed
        :return: x, y, z
        """
        values = self.ubit.pin_values
        if '1' in values:
            x, y, z = (values['1'],  # pylint: disable=invalid-name
                       values['0'], values['8'])
        return x, y, z

    @property
    def dial(self):
        """
        The value of the dial.

        :return: integer in range 0 - 255
        """
        values = self.ubit.pin_values
        return values['2']

    def _read_button(self, pin):
        values = self.ubit.pin_values
        if pin in values:
            return values[pin]
        else:
            return None

    @property
    def button_a(self):
        """
        The state of button a of bit:commander

        :return: when pressed returns 1
        """
        return self._read_button('12')

    @property
    def button_b(self):
        """
        The state of button b of bit:commander

        :return: when pressed returns 1
        """
        return self._read_button('14')

    @property
    def button_c(self):
        """
        The state of button c of bit:commander

        :return: when pressed returns 1
        """
        return self._read_button('16')

    @property
    def button_d(self):
        """
        The state of button d of bit:commander

        :return: when pressed returns 1
        """
        return self._read_button('15')

    def run_async(self):
        """
        Puts the code into asynchronous mode

        :return:
        """
        self.ubit.run_async()

    def quit_async(self):
        """
        Stops asynchronose mode

        :return:
        """
        self.ubit.quit_async()
