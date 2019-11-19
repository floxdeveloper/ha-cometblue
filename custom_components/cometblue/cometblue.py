"""
Home Assistant Support for German Eurotronic CometBlue thermostats.
They are identical to the THERMy Blue (Aldi) Bluetooth thermostats.

This is a modified version of neffs ha-cometblue integration. 
I just adapted the handles for the pin and the temperature.

This version is based on the bluepy library and works on hassio. 
Currently only current and target temperature in manual mode is supported, nothing else. 

Add your cometblue thermostats to configuration.yaml:

climate cometblue:
  platform: cometblue
  devices:
    thermostat1:
      mac: 11:22:33:44:55:66
      pin: 0

"""
import logging
from datetime import timedelta
from datetime import datetime
import threading
import voluptuous as vol

import time
import struct

from bluepy import btle



from sys import stderr

REQUIREMENTS = ['bluepy>=1.3.0']

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(10)



PASSWORD_HANDLE = 0x48
TEMPERATURE_HANDLE = 0x3d
_TEMPERATURES_STRUCT_PACKING = '<bbbbbbb'
_PIN_STRUCT_PACKING = '<I'
_DATETIME_STRUCT_PACKING = '<BBBBB'
_BATTERY_STRUCT_PACKING = '<B'
_DAY_STRUCT_PACKING = '<BBBBBBBB'


class CometBlue(object):
    """CometBlue Thermostat """
    def __init__(self, address, pin):
        super(CometBlue, self).__init__()
        self._address = address
        self._conn = btle.Peripheral()
        self._pin = pin
        self._manual_temp = None
        self._cur_temp = None
        self._temperature = None
        self.available = False
        self._manual_mode=False
#        self.update()

    def connect(self):
        try:
            self._conn.connect(self._address)
        except btle.BTLEException as ex:
            _LOGGER.debug("Unable to connect to the device %s, retrying: %s", self._address, ex)
            try:
                self._conn.connect(self._address)
            except Exception as ex2:
                _LOGGER.debug("Second connection try to %s failed: %s", self._address, ex2)
                raise 
        try:
            self._conn.writeCharacteristic(PASSWORD_HANDLE, struct.pack(_PIN_STRUCT_PACKING, self._pin), True)
        except btle.BTLEException as ex:
            _LOGGER.error("Writing the pin did not work!")

    def disconnect(self):
        
        self._conn.disconnect()
        self._conn = btle.Peripheral()

    def should_update(self):
        return self._temperature != None

    @property
    def manual_temperature(self):
        if self._manual_temp:
            return self._manual_temp / 2.0
        else:
            return None
 
    @property
    def current_temperature(self):
        if self._cur_temp:
            return self._cur_temp / 2.0
        else:
            return None 
    
    @property
    def manual_mode(self):
        if self._manual_mode:
            return self._manual_temp
        else:
            return None 
 
    def update(self):
        _LOGGER.debug("Connecting to device %s", self._address)
        self.connect()
        time.sleep(1)
        try:
            data = self._conn.readCharacteristic(TEMPERATURE_HANDLE)
            self._cur_temp, self._manual_temp, self._target_low, self._target_high, self._offset_temp, \
                    self._window_open_detect, self._window_open_minutes = struct.unpack(
                            _TEMPERATURES_STRUCT_PACKING, data)
            
            if self._temperature:
                _LOGGER.debug("Updating Temperature for device %s to %d", self._address, self._temperature)
                self.write_temperature()
            self.available = True
            
        except btle.BTLEGattError:
            _LOGGER.error("Can't read cometblue data (%s). Did you set the correct PIN?", self._address)
            self.available = False
        finally:
            self.disconnect()
            _LOGGER.debug("Disconnected from device %s", self._address)

 
    @manual_temperature.setter
    def manual_temperature(self, temperature):
        self._temperature = temperature
    
    
    def write_temperature(self):
        self._manual_temp = int(self._temperature * 2.0)
        data = struct.pack(
                    _TEMPERATURES_STRUCT_PACKING,
                    -128, self._manual_temp,
                    -128, -128, -128, -128, -128)
        self._conn.writeCharacteristic(TEMPERATURE_HANDLE,data, True)
        
        self._temperature = None