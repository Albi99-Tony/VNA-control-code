import os
import numpy as np
import json
import matplotlib.pyplot as plt

from logger import logger
import CONSTANTS as c

"""
This library contains general functions that are used throughout the program and are not related to a specific instrument or procedure.
"""


def set_default_pyplot_style_settings():
    plt.rcParams["font.size"] = 16
    plt.rcParams["figure.figsize"] = c.FULLSCREEN_SIZE
    plt.rcParams["axes.grid"] = True
    plt.rcParams["lines.linewidth"] = 2
    plt.rcParams["lines.marker"] = '.'
    plt.rcParams["lines.markersize"] = 4



def sendWarning(s: str):
    # Function used for user interface
    print("WARNING: " + s)

def sendError(s: str):
    # Function used for user interface
    print("ERROR: " + s)

def sendLog(s: str):  
    # Function used for user interface
    print("LOG: " + s)



def update_log(settings: object):
    with open("log.txt", "r") as f:
        text = f.read()

    new_text = f"""
    Date-time: {settings["datetime"]}
    User: {settings["user_name"]}
    File name: {settings["measurement_name"]}
    Description: {settings["description"]}


    """

    file_content = text + new_text
    with open("log.txt", "w") as f:
        f.write(file_content)

