import pyvisa as visa

rm = visa.ResourceManager()
dmm4050 = rm.open_resource('TCPIP0::10.1.2.53::3490::SOCKET')
dmm4050.write_termination = "\r"
dmm4050.read_termination = "\r"

# try:
#     dmm4050.query('*IDN?')
# except visa.errors.VisaIOError:
#     dmm4050 = rm.open_resource('TCPIP0::10.1.2.53::3490::SOCKET')

dmm4050.query('*IDN?')

dmm4050.write(':SYSTem:REMote')
data = dmm4050.query(':MEAS:VOLT:ac? DEF')
print(data)

# def measure_voltage(*args):
#     data = dmm4050.query(':MEAS:VOLT:DC?')
#     return