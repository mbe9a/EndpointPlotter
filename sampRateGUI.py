"""
:platform: Unix, Windows
:synopsis: This module is mostly generated code from QtDesigner. It describes the format of the settings
    dialog for editing the sample rate of the serial connection to the ADC.
:moduleauthor: Michael Eller <mbe9a@virginia.edu>
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from settings_interface import set_sample_rate, get_sample_rate


class Ui_Dialog(object):
    """
    The graphical structure of this *Ui_Dialog* was generated by QtDesigner.
    The window allows the user to set the sample rate of the ADC.
    """

    def setupUi(self, Dialog):
        """
        This function initializes the window by altering the *Dialog* object passed (by reference) to it.

        :param Dialog: This must be of type PyQt5.QtWidgets.QDialog.
        """

        # set window name, size, icon
        Dialog.setObjectName("Settings - Sample Rate")
        Dialog.resize(456, 214)
        Dialog.setWindowIcon(QtGui.QIcon('resources/gear.ico'))

        # make a grid layout
        # grid layouts allow the window to be resized easily
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")

        # create a label for the input box
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        # create the input box for the sample rate
        self.sample_rate_input = QtWidgets.QSpinBox(Dialog)
        self.sample_rate_input.setMinimum(1)
        self.sample_rate_input.setMaximum(100)
        rate = int(get_sample_rate())
        self.sample_rate_input.setValue(rate)
        self.sample_rate_input.setObjectName("sample_rate_input")
        self.gridLayout.addWidget(self.sample_rate_input, 2, 0, 1, 1)

        # create a save and cancel button, these are built in buttons that emit specific signals
        self.settings_sample_rate_box = QtWidgets.QDialogButtonBox(Dialog)
        self.settings_sample_rate_box.setOrientation(QtCore.Qt.Horizontal)
        self.settings_sample_rate_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.settings_sample_rate_box.setObjectName("settings_sample_rate_box")
        self.gridLayout.addWidget(self.settings_sample_rate_box, 6, 2, 1, 1)

        # the following spacer items organize the objects in the window nicely
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 6, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 0, 0, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 3, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 2, 1, 1, 2)

        # move the objects over to Dialog and set the text
        self.retranslateUi(Dialog)

        # set what to do when the save button is clicked
        self.settings_sample_rate_box.accepted.connect(lambda: self.save(Dialog))

        # set what to do when the cancel button is hit
        self.settings_sample_rate_box.rejected.connect(Dialog.reject)

        # connect the signals and slots by name
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        """
        This function translates the GUI objects of this class to the passed *Dialog* objcect,
        then sets the text of the various objects in the window.

        :param Dialog: This must be of type PyQt5.QtWidgets.QDialog.
        """

        # rename the function for readability
        _translate = QtCore.QCoreApplication.translate

        # set the window title and label text
        Dialog.setWindowTitle(_translate("Dialog", "Settings - Sample Rate"))
        self.label.setText(_translate("Dialog", "Sample Rate (samples / second)"))

    def save(self, Dialog):
        """
        This function saves the sample rate in the input box and closes the window.

        :param Dialog: This must be of type PyQt5.QtWidgets.QDialog.
        """

        # get the number from the input box
        rate = self.sample_rate_input.value()
        # save it
        set_sample_rate(rate)

        # close the window
        Dialog.accept()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
