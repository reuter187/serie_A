import minimalmodbus
import serial
import pandas as pd
import time
import random

# Special Functions Registers. Parameters registers range from 0 - 4095

# Read Only: indicates the total number of parameters
TOTAL_NUMBER_OF_PARAM = 4097
# Read Only: indicates the state of the inverter (on/off, cw/ccw, etc.)
STATE = 4100
# R/W: when 1, turns the inverter ON. When 0 turns OFF.
ON_OFF = 4101
# R/W: when 1, the output frequency is incremented by 0.1 Hz. When 0 it is decremented by 0.1 Hz
INC_DEC_FREQ = 4103
# Read Only: indicates the firmware version
VERSION = 4104
# R/W: resets the inverter
RESET = 4105
# R/W: sets the output frequency
FREQ_SET = 4106
# R/W: when 1 turns on the inverter CW. When 0 turns on the inverter CCW.
CW_CCW = 4107
# Read Only: parameter P003, output current.
OUT_CURRENT = 2
# Read Only: parameter P005, junction temperature.
TEMPERATURE = 4
# R/W: P301
FREQ_REF = 26
# R/W: P302
CTRL = 27


class NotConnectedError(Exception):
    """Raised if there's no target connected"""
    pass

class AgDrive:

    def __init__(self, port=None, address=0, baud=None, stop_bits=None, parity=None, timeout=None):
        self.instr = None
        self.port = port
        self.address = int(address)
        self.baud = baud
        self.stop_bits = stop_bits
        self.parity = parity
        self.timeout = timeout
        self.connected = False

    def connect2instrument(self):
        if self.port == "":
            self.port = "COM100"
        try:
            baud_int = int(self.baud)
        except ValueError:
            baud_int = 2400
            pass
        if self.parity == "":
            self.parity = 'N'
        if self.stop_bits == "":
            self.stop_bits = 1
        try:
            self.instr = minimalmodbus.Instrument(self.port, int(self.address))  # port name, slave address
            self.instr.serial.baudrate = baud_int
            self.instr.serial.stopbits = int(self.stop_bits)
            self.instr.serial.timeout = self.timeout
            self.instr.serial.parity = self.parity
            self.instr.clear_buffers_before_each_transaction = True
            self.instr.close_port_after_each_call = True
            self.connected = True
            return True
        except (minimalmodbus.ModbusException, NameError, serial.serialutil.SerialException):
            self.connected = False
            return False
            pass

    def inv_on(self):
        try:
            self.instr.write_register(ON_OFF, 1, 0, 6, False)
            return True
        except (minimalmodbus.NoResponseError, minimalmodbus.SlaveReportedException, minimalmodbus.InvalidResponseError,
                NameError, NotConnectedError):
            return False
            pass

    def inv_off(self):
        try:
            self.instr.write_register(ON_OFF, 0, 0, 6, False)
            return True
        except (minimalmodbus.NoResponseError, minimalmodbus.SlaveReportedException, minimalmodbus.InvalidResponseError,
                NameError, NotConnectedError):
            return False
            pass

    def inc_freq_step(self):
        try:
            self.instr.write_register(INC_DEC_FREQ, 1, 0, 6, False)
            return True
        except (minimalmodbus.NoResponseError, minimalmodbus.SlaveReportedException, minimalmodbus.InvalidResponseError,
                NameError, NotConnectedError):
            return False
            pass

    def dec_freq_step(self):
        try:
            self.instr.write_register(INC_DEC_FREQ, 0, 0, 6, False)
            return True
        except (minimalmodbus.NoResponseError, minimalmodbus.SlaveReportedException, minimalmodbus.InvalidResponseError,
                NameError, NotConnectedError):
            return False
            pass

    def inv_cw(self):
        try:
            self.instr.write_register(CW_CCW, 0, 0, 6, False)
            return True
        except (minimalmodbus.NoResponseError, minimalmodbus.SlaveReportedException, minimalmodbus.InvalidResponseError,
                NameError, NotConnectedError):
            return False
            pass

    def inv_ccw(self):
        try:
            self.instr.write_register(CW_CCW, 1, 0, 6, False)
            return True
        except (minimalmodbus.NoResponseError, minimalmodbus.SlaveReportedException, minimalmodbus.InvalidResponseError,
                NameError, NotConnectedError):
            return False
            pass

    def get(self, register):
        if self.connected:
            try:
                value = self.instr.read_register(register)
                return value
            except (minimalmodbus.NoResponseError, minimalmodbus.SlaveReportedException,
                    minimalmodbus.InvalidResponseError, NameError, NotConnectedError):
                return -1
                pass
        else:
            return -1

    def set(self, register, value):
        try:
            self.instr.write_register(register, value, 0, 6, False)
            return True
        except (minimalmodbus.NoResponseError, minimalmodbus.SlaveReportedException, minimalmodbus.InvalidResponseError,
                NameError, NotConnectedError):
            return False
            pass


def error_handling(error):
    if error == 'display':
        return ' Reprovado no teste do display.'
    elif error == 'dp1':
        return ' Tensão no display DP1 diferente da especificação.'
    elif error == 'dec':
        return ' Inversor não desacelera via comunicação.'
    elif error == 'acc':
        return ' Inversor não acelera via comunicação.'
    elif error == 'di2':
        return ' DI2 não funciona.'
    elif error == 'di1':
        return ' DI1 não funciona.'
    elif error == 'multispeed':
        return ' Falha no acionamento multispeed, não foi possível realizar a configuração via Modbus.'
    elif error == 'di3':
        return ' DI3 não funciona.'
    elif error == 'no_current':
        return ' Falha na leitura de corrente.'
    elif error == 'dc_voltage':
        return ' ensão do barramento CC fora da especificação, erro de leitura.'
    elif error == 'off':
        return ' Inversor não desliga via comunicação.'
    elif error == 'on':
        return ' Inversor não liga via comunicação.'


# def file_save():
#     f = filedialog.asksaveasfile(initialdir="/", title="testing='.txt'", initialfile="file",
#                                  defaultextension=".txt", filetypes=(("Text files", "*.txt"), ("all files", "*.*")))
#     if f is None:
#         return
#     return f.name