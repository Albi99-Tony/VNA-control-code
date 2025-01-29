from library_misc import *
from time import sleep
import serial
from dataclasses import dataclass
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
This library contains the PowerSupply object and other functions required to control the power supplies.
One can choose between using a F2031 single power supply, a F2031 pair of power supplies or a Kepco BOP series power supply
"""

class PowerSupply:

    def __init__(self, port, baud_rate) -> None:
        self.ser = serial.Serial(port, baud_rate)
        logger.info(f"Power supply initialized on port {port} with baud rate {baud_rate}")

    def getID(self) -> None:
        logger.info('Getting power supply ID...')
        self.ser.write(b'*IDN?\r') 
        response = self.read_to_r()
        logger.info(f"ID: {response}")

    def getConnectionStatus(self) -> None:
        if self.ser.isOpen(): 
            logger.info(f"Power supply connected on port {self.ser.name}")

    def setCurrent(self, i: float, give_additional_info=False) -> None:
        maxCurrent = 3.6

        if abs(i) > maxCurrent:
            logger.error(f'Current {i}A exceeds max current of {maxCurrent}A')
            return

        command = f'CUR {i:+}\r'

        if give_additional_info:
            logger.info(f'Query: {command}')

        self.ser.write(bytes(command, 'utf-8'))

        response = self.read_to_r()

        if response != 'CMLT\r':
            logger.warning(f"Unexpected response in setCurrent: {response}")

        if i == 0:
            self.setOutputState(0)
        else:
            self.setOutputState(1)

    def setOutputState(self, state: int) -> None:
        command = f'OUT {state}\r'
        self.ser.write(bytes(command, 'utf-8'))

        response = self.read_to_r()
        if response != 'CMLT\r':
            logger.warning(f"Unexpected response in setOutputState: {response}")

    def setRampRate(self, rate: float) -> None:
        if rate < 0.01:
            rate = 0.01
            logger.warning("Using rate smaller than 0.01 A/s, using 0.01 A/s instead")

        if rate > 2:
            rate = 2
            logger.warning('Using rate greater than 2 A/s, using 2 A/s instead')

        command = f'RATE {rate}\r'
        logger.info(f'Query: {command}')

        self.ser.write(bytes(command, 'utf-8'))

        response = self.read_to_r()
        if response != 'CMLT\r':
            logger.warning(f"Unexpected response in setRampRate: {response}")

    def read_to_r(self) -> str:
        ch = ''
        line = []
        while ch != b'\r':
            ch = self.ser.read()
            line.append(ch.decode('utf-8'))
        return ''.join(line)

    def closeConnection(self) -> None:
        self.ser.close()
        logger.info("Closed connection to power supply")

    def demag_sweep(self) -> None:
        demag_sweep = [3, -1.5, 0.75, -0.375, 0.1875, -0.09375, 0.045, -0.02, 0.01, -0.005, 0.002, -0.001, 0.0005]
        logger.info("Executing demagnetizing sweep...")
        
        for current in demag_sweep:
            self.setCurrent(current)
            sleep(0.5)

        self.setCurrent(0)
        logger.info("Completed demagnetizing sweep.")

    def setTriggers(self, val, give_additional_info=False) -> None:
        command = f'SWTRIG n{val}'
        if give_additional_info:
            logger.info(f'Query: {command}')

        self.ser.write(bytes(command, 'utf-8'))

        command = f'NTRIG n{val}'
        if give_additional_info:
            logger.info(f'Query: {command}')

        self.ser.write(bytes(command, 'utf-8'))

@dataclass
class TwoPowerSupply:
    ps1: PowerSupply
    ps2: PowerSupply

    def setCurrent(self, current):
        self.ps1.setCurrent(current)
        self.ps2.setCurrent(current)

    def demag_sweep(self):
        self.ps1.demag_sweep()
        self.ps2.demag_sweep()

def setupConnectionPS(port, baud_rate: int, give_additional_info=False) -> PowerSupply | None:
    try:
        ps = PowerSupply(port, baud_rate)
        ps.getConnectionStatus()
        return ps
    except serial.SerialException as e:
        logger.warning(f"Could not connect to power supply on {port}. Error: {e}")
        if give_additional_info: 
            logger.info(f"Error message: {e}")
        return None
