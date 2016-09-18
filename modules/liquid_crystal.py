#
# liquidcrystal.py
#
# Class to control LCD using WebIOPi
#
# Written by Nobuki HIRAMINE
# http://www.hiramine.com
# Last modified : 2013/10/06
#

import webiopi

GPIO = webiopi.GPIO


class LiquidCrystal:
    _numlines = 2
    _data_pins = [0, 0, 0, 0]

    def __init__(self, rs, e, d4, d5, d6, d7):
        # Set member
        self._rs_pin = rs
        self._enable_pin = e
        self._data_pins[0] = d4
        self._data_pins[1] = d5
        self._data_pins[2] = d6
        self._data_pins[3] = d7

        # Set Pin Mode
        GPIO.setFunction(self._rs_pin, GPIO.OUT)  # Register Select pin
        GPIO.setFunction(self._enable_pin, GPIO.OUT)  # Enable Signale pin
        for i in range(4):
            GPIO.setFunction(self._data_pins[i], GPIO.OUT)  # Data pins

        GPIO.digitalWrite(self._rs_pin, False)  # RS pin LOW
        GPIO.digitalWrite(self._enable_pin, False)  # Enable pin LOW
        self._write4bits(0x03)  # Function Set Command : 8 bit interface data (1st)
        self._write4bits(0x03)  # Function Set Command : 8 bit interface data (2nd)
        self._write4bits(0x03)  # Function Set Command : 8 bit interface data (3rd)
        self._write4bits(0x02)  # Function Set Command : 4 bit interface data

        self._command(0x28)  # Function Set Command : multi line display
        self._command(0x0C)  # Display ON/OFF Command : Display ON, Cursor OFF, Blink OFF
        self._command(0x06)  # Entry Mode Set Command : Increment ON, Shift OFF

        self.clear()  # Clear display

    def clear(self):
        self._command(0x01)
        webiopi.sleep(0.002)  # 2msec

    def setCursor(self, col, row):
        row_offsets = [0x00, 0x40]
        if row >= self._numlines:
            row = self._numlines - 1
        self._command(0x80 | (row_offsets[row] + col))

    def write(self, value):
        for i in range(len(value)):
            self._send(ord(value[i]), True)

    def _command(self, value):
        self._send(value, False)

    def _send(self, value, mode):
        GPIO.digitalWrite(self._rs_pin, mode)
        self._write4bits(value >> 4)
        self._write4bits(value)

    def _write4bits(self, value):
        for i in range(4):
            GPIO.digitalWrite(self._data_pins[i], (value >> i) & 0x01)
        self._pulseEnable()

    def _pulseEnable(self):
        GPIO.digitalWrite(self._enable_pin, False)  # LOW
        webiopi.sleep(0.000001)  # 1microsec
        GPIO.digitalWrite(self._enable_pin, True)  # HIGH
        webiopi.sleep(0.000001)  # 1microsec(need 0.450microsec)
        GPIO.digitalWrite(self._enable_pin, False)  #
        webiopi.sleep(0.000100)  # 100microsec(need 37microsec)
