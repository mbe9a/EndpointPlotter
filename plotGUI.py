"""
:platform: Unix, Windows
:synopsis: This module contains generated code from QtDesigner and custom code for the GUI containing the live plot.
:moduleauthor: Michael Eller <mbe9a@virginia.edu>
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QDialog
from animation import CustomFigCanvas
from PyQt5.QtWidgets import QFileDialog
import time
from settings_interface import read_port_configuration, get_sample_rate
import serial
import os
import csv
import hashlib

#: Member *_serial_port* is a global variable representing the serial connection to the ADC.
#: It will be opened when plotGUI.Ui_Dialog is initialized.
_serial_port = serial.Serial(baudrate=9600, timeout=2)

#: This global member is used to create a soft stop signal for a plotGUI.Ui_Dialog object
stop = 0

#: *initial_hash* is set on the creation of a plotGUI.Ui_Dialog object.
#: Hashing is used to detect a change in the settings files.
#: The program will periodically hash the settings files and compare with initial_hash.
#: If a change has been detected, plotGUI.Ui_dialog.update_plot() will be called.
initial_hash = 0


class MyThread(QThread):
    """
    This is a simple class to implement a QThread object and specify its *run()* method.
    """

    def __init__(self, callback1, callback2):
        """
        Initialize the QThread and set the callback stubs.

        :param callback1: Callback function for the thread to execute within *dataSendLoop()*. T
                his callback must send a new data point to the plot.
        :param callback2: Callback function triggered in *dataSendLoop()*
                and is responsible for triggering *update_plot()*.
        """
        QThread.__init__(self)
        self.callback1 = callback1
        self.callback2 = callback2

    def __del__(self):
        """
        Windows does not play well with threads. If you kill a thread in Windows, the main thread will crash.
        """
        self.wait()

    def run(self):
        """
        This overrides the parent *run()* method. Thread will run the infinite loop in *dataSendLoop()*.
        """
        dataSendLoop(self.callback1, self.callback2)


class Ui_Dialog(object):
    """
    The graphical structure of this *Ui_Dialog* was generated by QtDesigner.
    The window contains a few buttons and an embedded matplotlib animation.
    """

    def setupUi(self, Dialog):
        """
        This function initializes the window by altering the *Dialog* object passed (by reference) to it.

        :param Dialog: This must be of type PyQt5.QtWidgets.QDialog.
        """

        # get _serial_port from global context
        global _serial_port
        # get the current serial port setting (string)
        port = read_port_configuration()
        # set the port and open it, wait 2s for the microcontroller to settle
        _serial_port.setPort(port)
        _serial_port.open()
        time.sleep(2)

        # get the initial hash value from global context
        global initial_hash
        # set it here
        initial_hash = get_hash()

        # set window name, size, icon
        Dialog.setObjectName("Dialog")
        Dialog.resize(1000, 700)
        Dialog.setWindowIcon(QtGui.QIcon('resources/laser.ico'))

        # make a grid layout
        # grid layouts allow the window to be resized easily
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")

        # create a button to allow the user to save the plot
        self.pushButton_save_image = QtWidgets.QPushButton(Dialog)
        self.pushButton_save_image.setObjectName("pushButton_save_image")
        self.gridLayout.addWidget(self.pushButton_save_image, 0, 0, 1, 1)
        # connect the button click to the save_image() function
        self.pushButton_save_image.clicked.connect(lambda: self.save_image(Dialog))

        # create a button to allow the user to save the data as csv
        self.pushButton_save_csv = QtWidgets.QPushButton(Dialog)
        self.pushButton_save_csv.setObjectName("pushButton_save_csv")
        self.gridLayout.addWidget(self.pushButton_save_csv, 0, 1, 1, 1)
        # connect the button click to the save_csv() function
        self.pushButton_save_csv.clicked.connect(lambda: self.save_csv(Dialog))

        # create a close button
        # This window needs a controlled or 'soft' close
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 0, 2, 1, 1)
        # xonnect the button click to the *close()* function
        self.pushButton.clicked.connect(self.close)

        # This is a hidden button that will actually close the window.
        # This is automatically 'clicked' after *close()* is finished.
        self.pushButtonHIDDEN = QtWidgets.QPushButton(Dialog)
        self.pushButtonHIDDEN.setObjectName("pushButtonHIDDEN")
        self.pushButtonHIDDEN.clicked.connect(Dialog.reject)
        self.pushButtonHIDDEN.setVisible(False)

        # create the animation object
        self.myFig = CustomFigCanvas()
        self.gridLayout.addWidget(self.myFig, 1, 0, 1, 3)

        # Create the thread and start it.
        # The thread will execute the infinite loop in dataSendLoop()
        self.thread = MyThread(self.addData_callbackFunc, self.update_plot)
        self.thread.start()

        # the regular close button will make the program crash for unknown reasons, disable it
        Dialog.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

        # this function translates all the objects created here and sets all the text
        self.retranslateUi(Dialog)

        # make sure we connect *Dialog*'s signals to their corresponding slots
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        """
        This function translates the GUI objects of this class to the passed *Dialog* objcect,
        then sets the text of the various objects in the window.

        :param Dialog: This must be of type PyQt5.QtWidgets.QDialog.
        """

        # rename the function for readability
        _translate = QtCore.QCoreApplication.translate

        # set the window title and button text
        Dialog.setWindowTitle(_translate("Dialog", " "))
        self.pushButton_save_csv.setText(_translate("Dialog", "Save CSV"))
        self.pushButton_save_image.setText(_translate("Dialog", "Save Image"))
        self.pushButton.setText(_translate("Dialog", "Close"))

    def addData_callbackFunc(self, value):
        """
        This function adds the most recent ADC value to the buffer in the animation object.

        :param value: number from the serial port. This is 'emitted' from *mySrc* in *dataSendLoot()*.
        """
        self.myFig.addData(value)

    def update_plot(self, value):
        """
        This function calls a series of functions within the animation object to update the figure axes and filtering.

        :param value: the format of this function requires *value* to be present. It is unused in this function.
        """

        # update the number of samples to keep in the moving average filter and update the lines accordingly
        self.myFig.update_window()
        # update the range of the x-axis, add zeros if necessary
        self.myFig.update_xlim()
        # update the range of the y-axis
        self.myFig.update_ylim()

    def close(self):
        """
        This function creates a controlled and soft close.
        The figure and serial must be closed before the window is allowed to close.
        """

        # the following line is essential in order to have the main window
        # stay alive after closing this dialog. Without removing the canvas
        # widget, the entire program crashes.
        self.myFig.setParent(None)
        self.myFig.close()

        # get the _serial_port from global context
        global _serial_port
        # get the stop variable from global context
        global stop

        # set the stop variable so the program knows it needs to close
        # this will allow the thread to exit the infinite loop in dataSendLoop()
        stop = 1
        time.sleep(1)

        # close the _serial_port
        _serial_port.close()

        # click the hidden close button that actually closes the window
        self.pushButtonHIDDEN.click()

    def save_image(self, Dialog):
        """
        Saves the current plot canvas as an image file.
        It will open a save dialog in order to get the desired file path from the user.

        :param Dialog: The same PyQt5.QtWidgets.QDialog object passed to the PlotGUI.Ui_Dialog.
        """

        # easy way to open a save file dialog
        # returns the file path as a string
        fname = QFileDialog.getSaveFileName(Dialog, 'Save Image As',
                                            os.sep.join((os.path.expanduser('~'), 'Documents')),
                                            'Image Files (*.png *.jpg *.jpeg)')

        # if the user canceled, exit
        if fname[0] == '':
            return

        # else, save the figure at the specified file path
        self.myFig.fig.savefig(fname[0])

    def save_csv(self, Dialog):
        """
        This function saves all recorded data in a simple format.
        Opens a save file dialog to get the desired file path from the user.

        :param Dialog: The same PyQt5.QtWidgets.QDialog object passed to the PlotGUI.Ui_Dialog.
        """

        # easy way to open a save file dialog
        # returns the file path as a string
        fname = QFileDialog.getSaveFileName(Dialog, 'Save Data',
                                            os.sep.join((os.path.expanduser('~'), 'Documents')),
                                            'CSV Files (*.csv)')

        # if the user canceled, exit
        if fname[0] == '':
            return

        # else, save the data at the specified file path
        with open(fname[0], "w") as csvfile:
            fieldnames = ['Time (s)', 'Signal (V)']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
                                    delimiter=',', lineterminator='\n')
            writer.writeheader()
            # get time scaling factor based on the sample rate
            interval = float(get_interval())
            for x in range(0, len(self.myFig.all)):
                writer.writerow({'Time (s)': round(float(x) * interval, 2), 'Signal (V)': self.myFig.all[x]})


# You need to setup a signal slot mechanism, to
# send data to your GUI in a thread-safe way.
# Believe me, if you don't do this right, things
# go very very wrong.
class Communicate(QtCore.QObject):
    """
    In order to cleanly send data throughout the different processes within the GUI,
    a thread-safe mechanism must be used. This is an extension of a built-in pyqt signal.
    It can be connected to a slot (function) that will trigger when the signal emits a value.
    """
    data_signal = QtCore.pyqtSignal(float)


def dataSendLoop(addData_callbackFunc, update_plot):
    """
    This is the infinite loop executed by a separate thread. Based on the sample rate set by the user,
    it will periodically poll a new value over the serial port and send it to the animation through a
    signal-slot mechanism. This function is also responsible for re-hashing the settings files and
    checking for necessary updates to the plot axes and filtering. If a change is detected, it will
    trigger the *update_plot()* function.

    :param addData_callbackFunc: slot function for adding data to the plot.
    :param update_plot: slot function for updating the plot filtering and axes.
    """

    # Setup the signal-slot mechanism.
    # This signal is responsible for adding new data to the animation
    mySrc = Communicate()
    mySrc.data_signal.connect(addData_callbackFunc)

    # This signal is responsible for updating the plot window if a change has been detected
    mySrc2 = Communicate()
    mySrc2.data_signal.connect(update_plot)

    # this gets the sample rate from the settings file and calculates the delay for the data collection loop
    interval = get_interval()

    # enter infinite loop
    while True:

        # get stop variable from global context
        global stop

        # check if the user wants to exit
        # if so, exit the while loop so this thread can stop and we can do garbage collection later
        if stop:
            stop = 0
            break

        # check if the user has changed any of the settings
        # if so, trigger signal-slot mechanism in mySrc2 and update_plot()
        if check_for_change():
            mySrc2.data_signal.emit(0)

        # wait the specified interval
        time.sleep(interval)

        # get _serial_port from global context
        global _serial_port

        # request a new value from the ADC
        _serial_port.write(b'a')
        # read from the serial port to get the value
        val = int(_serial_port.readline().decode('ascii').strip())

        # emit a signal from mySrc, which will execute addData_callbackFunc(val)
        mySrc.data_signal.emit(val)


def get_interval():
    """
    This is a helper function to calculate the time between samples.
    It reads the sample rate value from the settings file and takes the inverse.

    :return: the interval in seconds.
    """
    samp_rate = float(get_sample_rate())
    interval = 1. / samp_rate
    return interval


def check_for_change():
    """
    If a change was detected return True. If no change, return False.

    :return: bool
    """

    # hash the settings file
    new_hash = get_hash()

    # get the initial hash from global context
    global initial_hash

    # check if they are the same or not
    if new_hash == initial_hash:
        return False
    else:
        initial_hash = new_hash
        return True


def get_hash():
    """
    This function uses *hashlib* to generate an md5 hash of the settings file.

    :return: the hash of the settings file
    """

    # create hash object
    hasher = hashlib.md5()

    # open the settings file and read it into the hash buffer
    with open('resources/plot_configuration.csv', 'r') as myfile:
        buf = myfile.read().encode('utf-8')
        hasher.update(buf)

    # generate the hashcode and return it
    return hasher.hexdigest()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
