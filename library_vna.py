import logging
from library_power_supply import *
from library_misc import *
import numpy as np
from time import sleep
import json
from RsInstrument.RsInstrument import RsInstrument

"""
This file contains necessary functions to control and operate the VNA.
"""

# Ensure logging is configured to capture detailed information
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setupConnectionVNA(give_additional_info: bool = False) -> RsInstrument:
    """
    Connects to the VNA.
    Returns object that contains methods to control the VNA.
    """
    resource_string_1 = 'TCPIP::192.168.2.101::INSTR'
    resource_string_2 = 'TCPIP::192.168.2.101::hislip0'
    resource_string_3 = 'GPIB::20::INSTR'
    resource_string_4 = 'USB::0x0AAD::0x0119::022019943::INSTR'
    resource_string_5 = 'RSNRP::0x0095::104015::INSTR'
    instr = RsInstrument(resource_string_3, True, False)

    idn = instr.query_str('*IDN?')
    logger.info("VNA connected correctly via GPIB")
    instr.write('*RST')
    instr.write("CALC1:PAR:DEL 'Trc1'")

    if give_additional_info:
        logger.info(f"\nHello, I am: '{idn}'")
        logger.info(f'RsInstrument driver version: {instr.driver_version}')
        logger.info(f'Instrument full name: {instr.full_instrument_model_name}')
        logger.info(f'Instrument installed options: {",".join(instr.instrument_options)}')

    return instr


def applySettings(instr: RsInstrument, settings: object) -> None:
    """
    This function takes the instrument object and a settings dict variable, then translates settings from the settings variable in queries for the VNA.
    """
    logger.info("Applying settings to VNA")

    instr.write("SENS1:FREQ:STAR " + f"{settings['start_frequency']}")
    instr.write("SENS1:FREQ:STOP " + f"{settings['stop_frequency']}")
    instr.write("SENS1:BAND " + f"{settings['bandwidth']}")
    instr.write("SOUR1:POW " + f"{settings['power']}")
    instr.write("SENS1:SWE:POIN " + f"{settings['number_of_points']}")
    instr.write_str(":MMEMORY:LOAD:CORRection 1, " + f"'{settings['cal_name']}.cal'")
    instr.visa_timeout = (settings['bandwidth']**-1 * settings['number_of_points'] * 10) * 1000 + 100

    logger.info("Settings applied successfully")


def measure_amp_and_phase(instr: RsInstrument, Sparam: str, i=0, avg=1) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Queries the VNA for values.
    Takes as input the VNA instrument object and the S parameter that should be measured.
    Returns frequencies, amplitude (linear), and phase.
    """
    logger.info("Measuring amplitude and phase for S-parameter: %s", Sparam)

    if i > 0:
        instr.write("CALC1:PAR:DEL 'Tr1'")
        instr.write("CALC1:PAR:DEL 'Tr2'")
        instr.write("CALC1:PAR:DEL 'Tr3'")
        instr.write("CALC1:PAR:DEL 'Tr4'")

    instr.write("CALC1:PAR:SDEF 'Tr1', 'S11AVG'")
    instr.write("DISP:WIND1:STAT ON")
    instr.write("DISP:WIND1:TRAC1:FEED 'Tr1'")

    instr.write("CALC1:PAR:SDEF 'Tr2', 'S21AVG'")
    instr.write("DISP:WIND2:STAT ON")
    instr.write("DISP:WIND2:TRAC2:FEED 'Tr2'")

    instr.write("CALC1:PAR:SDEF 'Tr3', 'S12AVG'")
    instr.write("DISP:WIND3:STAT ON")
    instr.write("DISP:WIND3:TRAC3:FEED 'Tr3'")

    instr.write("CALC1:PAR:SDEF 'Tr4', 'S22AVG'")
    instr.write("DISP:WIND4:STAT ON")
    instr.write("DISP:WIND4:TRAC4:FEED 'Tr4'")

    instr.write(":INITiate1:CONTinuous:ALL OFF")
    instr.write(":SENSE1:AVER:COUN 5; :AVER ON")

    for _ in range(avg):
        instr.query_with_opc(":INITiate1:IMMediate:ALL; *OPC?", 1000000)

    tracedata = instr.query_str('CALCulate1:DATA:ALL? SDAT')
    chan_list = instr.query_str('CONF:CHAN:CATalog?')
    logger.info("Channel list: %s", chan_list)

    trace_list = instr.query_str('CONF:CHAN:TRAC:CATalog?')
    logger.info("Trace list: %s", trace_list)

    tracelist = list(map(str, tracedata.split(',')))
    tracelist = np.array(tracelist, dtype='float32')

    re1, im1, S1, amp1, phase1 = [], [], [], [], []
    re2, im2, S2, amp2, phase2 = [], [], [], [], []
    re3, im3, S3, amp3, phase3 = [], [], [], [], []
    re4, im4, S4, amp4, phase4 = [], [], [], [], []

    for i in range(int(len(tracelist) / 4)):
        if (i % 2) == 0:
            re1.append(tracelist[i])
        else:
            im1.append(tracelist[i])

    for i in range(len(re1)):
        S1.append(re1[i] + 1j * im1[i])
        amp1.append(np.abs(S1[i]))
        phase1.append(np.angle(S1[i]))

    for i in range(int(len(tracelist) / 4), int(len(tracelist) / 2), 1):
        if (i % 2) == 0:
            re2.append(tracelist[i])
        else:
            im2.append(tracelist[i])

    for i in range(len(re2)):
        S2.append(re2[i] + 1j * im2[i])
        amp2.append(np.abs(S2[i]))
        phase2.append(np.angle(S2[i]))

    for i in range(int(len(tracelist) / 2), int(3 * len(tracelist) / 4), 1):
        if (i % 2) == 0:
            re3.append(tracelist[i])
        else:
            im3.append(tracelist[i])

    for i in range(len(re3)):
        S3.append(re3[i]+1j*im3[i]) 
        amp3.append(np.abs(S3[i]))
        phase3.append(np.angle(S3[i])) 


    for i in range(3*int(len(tracelist)/4),int(len(tracelist)),1):
        if (i%2)==0:
            re4.append(tracelist[i])
        else:
            im4.append(tracelist[i])

    for i in range(len(re4)):
        S4.append(re4[i]+1j*im4[i]) 
        amp4.append(np.abs(S4[i]))
        phase4.append(np.angle(S4[i])) 



    freqdata = instr.query_str('CALCulate1:DATA:STIMulus?')  # Get frequency list for complete trace
    freqlist = list(map(str, freqdata.split(',')))  # Convert the received string into a list
    freq = np.array(freqlist, dtype='float32')


    return freq, amp1, phase1, amp2, phase2, amp3, phase3, amp4, phase4, S1, S2, S3, S4