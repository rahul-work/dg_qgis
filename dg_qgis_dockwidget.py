# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DGQgisPluginDockWidget
								 A QGIS plugin
 A general tool for "Digital Geography" using QGIS.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
							 -------------------
		begin                : 2022-12-19
		git sha              : $Format:%H$
		copyright            : (C) 2022 by GISE-Hub
		email                : rahul.work223@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal

from qgis.PyQt.QtWidgets import QMessageBox

from .qgis_dg_cmdln import handle
from .qgis_dg_cmdln import stub


FORM_CLASS, _ = uic.loadUiType(os.path.join(
	os.path.dirname(__file__), 'dg_qgis_dockwidget_base.ui'))


class DGQgisPluginDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

	closingPlugin = pyqtSignal()

	def __init__(self, iface, parent=None):
		"""Constructor."""
		super(DGQgisPluginDockWidget, self).__init__(parent)
		# Set up the user interface from Designer.
		# After setupUI you can access any designer object by doing
		# self.<objectname>, and you can use autoconnect slots - see
		# http://doc.qt.io/qt-5/designer-using-a-ui-file.html
		# #widgets-and-dialogs-with-auto-connect
		self.setupUi(self)

		# self.issueCommandButton.clicked.connect( lambda: stub(
		# 	iface, handle(self.commandEdit.toPlainText())
		# ))
		self.issueCommandButton.clicked.connect(lambda: self.test_message_box(
			stub(iface, handle(self.commandEdit.toPlainText()))
		))
	
	def test_message_box(self, msg):
		QMessageBox.about(self, 'Received Message:', msg)
	
	def closeEvent(self, event):
		self.closingPlugin.emit()
		event.accept()
