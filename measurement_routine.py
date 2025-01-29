import logging
from library_analysis import *
from library_power_supply import *
from library_misc import *
from library_vna import *
from library_file_management import *
import CONSTANTS as c

# Ensure logging is configured to capture detailed information
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def measurement_routine(settings, ps1: PowerSupply, ps2: PowerSupply, instr: RsInstrument, field_sweep: list[float], angle: float, user_folder: str, sample_folder: str, measurement_name: str, dipole: int, Sparam: str, avg:int = 1, demag: bool = False) -> str:
    """
    Main function that is called by other files. 
    Goes through the whole routine for initializing, measuring and saving.
    """

    try:    # Everything is encapsulated in a try-except to always set the current to 0 in case of an exception
        logger.info("Starting measurement routine...")

        if dipole == 1:
            ps = ps1
            offset = 2.7001
            conversion = 50.027
            offset1 = 0
            conversion1 = 0
            offset2 = 0
            conversion2 = 0

        elif dipole == 2:
            if ps1 is None or ps2 is None:
                raise Exception("Quadrupole selected but one of the power supplies is not properly connected.")
            psq1 = ps1
            psq2 = ps2
            conversion = 0
            offset = 0
            offset1 = 1.7091
            conversion1 = 43.884
            offset2 = 1.4364
            conversion2 = 42.473
        else:
            raise Exception("Invalid dipole_mode parameter")

        logger.info("Dipole mode and power supplies configured.")

        freqs_S11, fields_S11, amps_S11, phases_S11, S11 = np.array([]), np.array([]), np.array([]), np.array([]), np.array([], dtype='complex_')
        freqs_S12, fields_S12, amps_S12, phases_S12, S12 = np.array([]), np.array([]), np.array([]), np.array([]), np.array([], dtype='complex_')
        freqs_S21, fields_S21, amps_S21, phases_S21, S21 = np.array([]), np.array([]), np.array([]), np.array([]), np.array([], dtype='complex_')
        freqs_S22, fields_S22, amps_S22, phases_S22, S22 = np.array([]), np.array([]), np.array([]), np.array([]), np.array([], dtype='complex_')
        currents = np.array([])
        currents1 = np.array([])
        currents2 = np.array([])

        j = 0

        for i, field in enumerate(field_sweep):
            logger.info(f"Setting field to {field} mT (step {i+1}/{len(field_sweep)})...")

            if dipole == 1:
                current = (field - offset) / conversion
                current1 = 0
                current2 = 0
                ps.setCurrent(current)

            if dipole == 2:
                current = 0
                angle_rad = np.radians(angle)
                current1 = (field * np.cos(angle_rad) - offset1) / conversion1
                current2 = (field * np.sin(angle_rad) - offset2) / conversion2
                psq1.setCurrent(current1)
                psq2.setCurrent(current2)

            logger.info(f"Field set to {field} mT. Waiting for {c.SETTLING_TIME}s to stabilize.")
            sleep(c.SETTLING_TIME)
            logger.info("Settling time over. Starting measurement...")

            freq, a1, p1, a2, p2, a3, p3, a4, p4, S1, S2, S3, S4 = measure_amp_and_phase(instr, Sparam, j, int(avg))
            j += 1
            logger.info("Measurement completed.")

            currents = np.concatenate((currents, [current] * len(freq)))
            currents1 = np.concatenate((currents1, [current1] * len(freq)))
            currents2 = np.concatenate((currents2, [current2] * len(freq)))

            freqs_S11 = np.concatenate((freqs_S11, freq))
            fields_S11 = np.concatenate((fields_S11, [field] * len(freq)))
            amps_S11 = np.concatenate((amps_S11, a1))
            phases_S11 = np.concatenate((phases_S11, p1))
            S11 = np.concatenate((S11, S1))

            freqs_S21 = np.concatenate((freqs_S21, freq))
            fields_S21 = np.concatenate((fields_S21, [field] * len(freq)))
            amps_S21 = np.concatenate((amps_S21, a2))
            phases_S21 = np.concatenate((phases_S21, p2))
            S21 = np.concatenate((S21, S2))

            freqs_S12 = np.concatenate((freqs_S12, freq))
            fields_S12 = np.concatenate((fields_S12, [field] * len(freq)))
            amps_S12 = np.concatenate((amps_S12, a3))
            phases_S12 = np.concatenate((phases_S12, p3))
            S12 = np.concatenate((S12, S3))

            freqs_S22 = np.concatenate((freqs_S22, freq))
            fields_S22 = np.concatenate((fields_S22, [field] * len(freq)))
            amps_S22 = np.concatenate((amps_S22, a4))
            phases_S22 = np.concatenate((phases_S22, p4))
            S22 = np.concatenate((S22, S4))

            logger.info("Saving data...")
            save_data(currents, currents1, currents2, freqs_S11, fields_S11, amps_S11, phases_S11, S11, user_folder, sample_folder, measurement_name=f"{measurement_name}_S11")
            logger.info(f'Saved file "{measurement_name}_S11.csv"')
            settings["measurement_name"] = f"{measurement_name}_S11"
            settings["s_parameter"] = 'S11'
            save_metadata(settings)

            save_data(currents, currents1, currents2, freqs_S21, fields_S21, amps_S21, phases_S21, S21, user_folder, sample_folder, measurement_name=f"{measurement_name}_S21")
            logger.info(f'Saved file "{measurement_name}_S21.csv"')
            settings["measurement_name"] = f"{measurement_name}_S21"
            settings["s_parameter"] = 'S21'
            save_metadata(settings)

            save_data(currents, currents1, currents2, freqs_S12, fields_S12, amps_S12, phases_S12, S12, user_folder, sample_folder, measurement_name=f"{measurement_name}_S12")
            logger.info(f'Saved file "{measurement_name}_S12.csv"')
            settings["measurement_name"] = f"{measurement_name}_S12"
            settings["s_parameter"] = 'S12'
            save_metadata(settings)

            save_data(currents, currents1, currents2, freqs_S22, fields_S22, amps_S22, phases_S22, S22, user_folder, sample_folder, measurement_name=f"{measurement_name}_S22")
            logger.info(f'Saved file "{measurement_name}_S22.csv"')
            settings["measurement_name"] = f"{measurement_name}_S22"
            settings["s_parameter"] = 'S22'
            save_metadata(settings)

            logger.info("Data saved successfully.")

        if dipole == 1:
            ps.setCurrent(0)
        if dipole == 2:
            psq1.setCurrent(0)
            psq2.setCurrent(0)

        logger.info("Measurement routine completed successfully.")
        return

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        if dipole == 1:
            ps.setCurrent(0)
        if dipole == 2:
            psq1.setCurrent(0)
            psq2.setCurrent(0)
        raise e
