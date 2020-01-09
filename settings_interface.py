"""
:platform: Unix, Windows
:synopsis: This module contains all get/set methods for settings.
            It's not particularly interesting but facilitates clean code.
:moduleauthor: Michael Eller <mbe9a@virginia.edu>
"""

import csv
import os

#: static fieldnames for the settings dict / csv file
fieldnames = ["window_samples", "sample_rate", "x_axis_size", "y_axis_min", "y_axis_max"]

#: default number of samples to average in a moving average filter
default_window_samples = 1

#: default sample rate in samples / sec
default_sample_rate = 10

#: default x axis range in seconds
default_x_axis_size = 30

#: default y-axis minimum in volts
default_y_axis_min = 0

#: default y-axis maximum in volts
default_y_axis_max = 60

#: slope of V_measured vs. V_in for V_in < 10 V
m1 = 14.3

#: intercept of V_measured vs. V_in for V_in < 10 V
b1 = -1

#: slope of V_measured vs. V_in for V_in > 10 V
m2 = 14.976

#: slope of V_measured vs. V_in for V_in > 10 V
b2 = -3.7


def generate_plotting_configuration_file():
    """
    Will write a new plot configuration (settings) file in the appropriate location.
    This will overwrite any existing settings.
    This is used when the user restores default settings from within the GUI.
    """

    # open and write a csv file with the default settings
    with open("resources/plot_configuration.csv", "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({fieldnames[0]: default_window_samples, fieldnames[1]: default_sample_rate,
                         fieldnames[2]: default_x_axis_size, fieldnames[3]: default_y_axis_min,
                         fieldnames[4]: default_y_axis_max})


def read_plotting_configuration():
    """
    Read the current settings configuration. If the file doesn't exist, generate the default.

    :return: Dict object containing the GUI's settings.
    """

    # check if the file exists
    if not os.path.isfile("resources/plot_configuration.csv"):
        # generate the default settings if it doesn't exist
        generate_plotting_configuration_file()

    # read the settings into a dict object
    with open("resources/plot_configuration.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=fieldnames)
        settings = next(reader)
        return settings


def save_plotting_configuration(settings):
    """
    This function will edit the file based on the dict of settings passed.

    :param settings: Dict of settings
    """

    # open the file and overwrite with the settings dict
    with open("resources/plot_configuration.csv", "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({fieldnames[0]: settings[fieldnames[0]], fieldnames[1]: settings[fieldnames[1]],
                         fieldnames[2]: settings[fieldnames[2]], fieldnames[3]: settings[fieldnames[3]],
                         fieldnames[4]: settings[fieldnames[4]]})


def set_window_samples(num):
    """
    Sets the number of samples to use in the moving average filter.

    :param num: number of samples
    :return: bool indicating whether or not the operation was successful
    """

    # check if num is within limits
    if num < 1 or num > 8:
        return False

    # get the current settings
    settings = read_plotting_configuration()
    # alter the window samples setting
    settings[fieldnames[0]] = num
    # save it
    save_plotting_configuration(settings)
    return True


def get_window_samples():
    """
    Read the saved window samples setting from the file.

    :return: saved window samples
    """

    # read in the file
    settings = read_plotting_configuration()
    # get the window samples
    num = settings[fieldnames[0]]
    return int(num)


def set_sample_rate(rate):
    """
    Set the sample rate and save it in the settings file.

    :param rate: ADC sample rate in samples per second. 1 < rate < 100.
    :return: bool indicating whether or not the operation was successful.
    """

    # check if the number is in the allowed range
    if rate < 1 or rate > 100:
        return False

    # read in the file
    settings = read_plotting_configuration()
    # set the sample rate portion
    settings[fieldnames[1]] = rate
    # rewrite the file with the new settings
    save_plotting_configuration(settings)
    return True


def get_sample_rate():
    """
    Get the saved ADC sample rate.

    :return: the ADC sample rate (float)
    """

    # read in the file
    settings = read_plotting_configuration()
    # get the sample rate portion and return it
    rate = settings[fieldnames[1]]
    return float(rate)


def set_x_axis_size(size):
    """
    Set the total width of the live plot in seconds. The number of samples depends on this and the sample rate.
    Total number of samples in the plot is equal to the x-axis size * sample rate.

    :param size: x-axis size in seconds. 5 < int(size) < 3600.
    :return: bool indicating whether or not the operation was successful.
    """

    # check if the input is in the correct range
    if size < 5 or size > 3660:
        return False

    # read in the file
    settings = read_plotting_configuration()
    # set the x-axis size setting
    settings[fieldnames[2]] = size
    # re-write the file
    save_plotting_configuration(settings)
    return True


def get_x_axis_size():
    """
    Get the x-axis length in seconds.

    :return: x-axis size (int)
    """

    # read in the file
    settings = read_plotting_configuration()
    # get the size and return it
    size = settings[fieldnames[2]]
    return int(size)


def set_y_axis_min(minimum):
    """
    Set the lower limit of the y-axis data in volts.

    :param minimum: lower limit of data y-axis. -60 < minimum < 69.9
    :return: bool indicating if the operation was so successful or not
    """

    # check if the input is in the correct range
    if minimum < -60 or minimum > 69.9:
        return False

    # read in the file
    settings = read_plotting_configuration()
    # set the y-axis minimum in the dict and save it
    settings[fieldnames[3]] = minimum
    save_plotting_configuration(settings)
    return True


def get_y_axis_min():
    """
    Get the y-axis lower limit in volts.

    :return: y-axis minimum (float)
    """

    # read in the file
    settings = read_plotting_configuration()
    # get the y-axis minimum
    minimum = settings[fieldnames[3]]
    return float(minimum)


def set_y_axis_max(maximum):
    """
    Set the upper limit of the y-axis in volts. 1 < maximum < 70

    :param maximum: upper limit of the y-axis in volts
    :return: bool indicating whether or not the operation was successful
    """

    # check if it's in the allowable range
    if maximum < 1 or maximum > 70:
        return False

    # read in the file
    settings = read_plotting_configuration()
    # set the y-axis maximum in the dict
    settings[fieldnames[4]] = maximum
    # save it
    save_plotting_configuration(settings)
    return True


def get_y_axis_max():
    """
    Get the y-axis upper limit in volts.

    :return: the y-axis maximum (float)
    """

    # read in the file
    settings = read_plotting_configuration()
    # get the y-axis upper limit
    maximum = settings[fieldnames[4]]
    return float(maximum)


def save_port_configuration(port):
    """
    This function sets the separate file that indicates which serial port to use.

    :param port: ADC serial port (string)
    """
    with open("resources/port_configuration.txt", "w") as outfile:
        outfile.write(port)


def read_port_configuration():
    """
    Get the saved ADC serial port.

    :return: serial port (string)
    """

    # if it doesn't exist, return empty string
    if not os.path.isfile("resources/port_configuration.txt"):
        return ""

    # else, read in the port
    with open("resources/port_configuration.txt", "r") as infile:
        port = infile.readline()
    return port.strip()


def restore_defaults():
    """
    This function resets all settings to the defaults stored in this file.
    """
    save_port_configuration("")
    generate_plotting_configuration_file()
