import os
import numpy as np
import json
import pandas as pd
from matplotlib import pyplot as plt
import logging

from logger import logger
import CONSTANTS as c

logging.basicConfig(level=logging.INFO)

def create_measurement_path(settings):
    return os.path.join(c.DATA_FOLDER_NAME, settings["user_name"], settings["sample_name"], settings["measurement_name"])

def save_data(currents: list[float], currents1: list[float], currents2: list[float], freqs: list[float], fields: list[float], amps: list[float], phases: list[float], S, user_folder: str, sample_folder: str, measurement_name: str):
    """
    Saves data in as {root_folder}/{user_folder}/{sample_folder}/{measurement_name}, checks if existing measurements exist already and adds a suffix
    """
    df = pd.DataFrame()
    df["Frequency"] = freqs
    df["Field"] = fields
    df["Current (dipole mode)"] = currents
    df["Current1 (quadrupole mode)"] = currents1
    df["Current2 (quadrupole mode)"] = currents2
    df["Amplitude"] = amps
    df["Phase"] = phases
    df["S_param"] = S

    root_folder = f"{c.DATA_FOLDER_NAME}/"
    initialname = measurement_name
    format = ".csv"

    os.makedirs(f"{root_folder}/{user_folder}/{sample_folder}/{measurement_name}", exist_ok=True)

    df.to_csv(f"{root_folder}/{user_folder}/{sample_folder}/{measurement_name}/{measurement_name}{format}", sep=',', index=False)
    logging.info(f"Data saved to {root_folder}/{user_folder}/{sample_folder}/{measurement_name}/{measurement_name}{format}")

def load_measurement(measurement_path: str, transpose: bool = False) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Reads data from CSV file.
    Takes filename as input and returns relevant data.
    Information about the measurement is given by the metadata.
    """
    with open(os.path.join(measurement_path, "measurement_info.json"), "r") as f:
        metadata = json.load(f)

    fields = np.array(metadata["field_sweep"])
    n_field_points = len(fields)
    n_freq_points = metadata["number_of_points"]
    measurement_name = metadata["measurement_name"]

    df = pd.read_csv(os.path.join(measurement_path, f"{measurement_name}.csv"))
    freqs = (df.loc[df["Field"] == fields[0]])["Frequency"]
    amps, phases = np.zeros((n_field_points, n_freq_points)), np.zeros((n_field_points, n_freq_points))
    
    for i, field in enumerate(fields):
        amps[i, :] = (df.loc[df["Field"] == field])["Amplitude"]
        phases[i, :] = (df.loc[df["Field"] == field])["Phase"]

    if transpose:
        amps = np.transpose(amps)
        phases = np.transpose(phases)

    logging.info(f"Measurement data loaded from {measurement_path}")

    return freqs, fields, amps, phases

def save_metadata(settings: object) -> None:
    user_folder = settings["user_name"]
    sample_name = settings["sample_name"]
    filename = settings["measurement_name"]

    temp = settings.pop("field_sweep")    
    settings["field_sweep"] = temp  # puts the field sweep at the end of the JSON for readability

    measurement_path = create_measurement_path(settings)
    os.makedirs(measurement_path, exist_ok=True)
    with open(os.path.join(measurement_path, "measurement_info.json"), 'w') as f:
        json.dump(settings, f, indent=4)
    logging.info(f"Metadata saved to {measurement_path}")

def load_metadata(measurement_path: str) -> object:
    """
    Loads the metadata file for a measurement.
    """
    with open(os.path.join(measurement_path, "measurement_info.json"), "r") as f:
        metadata = json.load(f)
    logging.info(f"Metadata loaded from {measurement_path}")
    return metadata

def save_settings(settings):    
    """
    Save the current settings to a file.
    """
    settings_file = os.path.join(os.path.dirname(__file__), "last_settings.json")
    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=4)
    logging.info(f"Settings saved to {settings_file}")

def save_plot(path: str, name: str):
    folder_path = os.path.join(path, "Plots")
    os.makedirs(folder_path, exist_ok=True)
    plt.savefig(os.path.join(folder_path, name))
    logging.info(f"Plot saved to {os.path.join(folder_path, name)}")
