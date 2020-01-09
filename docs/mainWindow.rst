mainWindow module
=================

.. automodule:: mainWindow
   :members:
   :undoc-members:
   :show-inheritance:

Usage
#####

.. code-block:: python

	import sys
	from PyQt5 import QtWidgets
	from mainWindow import Ui_MainWindow

	app = QtWidgets.QApplication(sys.argv)
	MainWindow = QtWidgets.QMainWindow()
	ui = Ui_MainWindow()
	ui.setupUi(MainWindow)
	MainWindow.show()
	sys.exit(app.exec_())
	