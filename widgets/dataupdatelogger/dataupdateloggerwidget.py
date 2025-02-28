# -*- coding: utf-8 -*-


import datetime
import os
from widgets.dataupdatelogger.ui_dataupdatelogger import Ui_DataUpdateLogger
from PyQt5 import QtWidgets, QtCore
from pypipboy.types import eValueType
from pypipboy.datamanager import eValueUpdatedEventType
from .. import widgets


class DataUpdateLoggerWidget(widgets.WidgetBase):
    _signalPrintToLog = QtCore.pyqtSignal(str)
    
    def __init__(self, mhandle, parent):
        super().__init__('Data Update Logger', parent)
        self.widget.ui = Ui_DataUpdateLogger()
        self.widget.ui.setupUi(self.widget)
        self.setWidget(self.widget)
        self._signalPrintToLog.connect(self._slotPrintToLog)
        self.widget.ui.clearButton.clicked.connect(self._slotClearLog)
        self.widget.ui.enableCheckBox.stateChanged.connect(self._slotEnableLogging)
        self.widget.ui.logTextEdit.setMaximumBlockCount(10000)
        
    def init(self, app, datamanager):
        super().init(app, datamanager)
        self.dataManager = datamanager
        self.networkchannel = datamanager.networkchannel
        
    def getMenuCategory(self):
        return 'Development'
        
    
    @QtCore.pyqtSlot(str)
    def _slotPrintToLog(self, msg):
        self.widget.ui.logTextEdit.appendPlainText(str(datetime.datetime.now()) + ': ' + msg)
        
    @QtCore.pyqtSlot()
    def _slotClearLog(self):
        self.widget.ui.logTextEdit.clear()
        
    @QtCore.pyqtSlot(bool)
    @QtCore.pyqtSlot(int)
    def _slotEnableLogging(self, value):
        if value:
            self.networkchannel.registerConnectionListener(self._onConnectionStateChange)
            self.dataManager.registerRootObjectListener(self._onRootObjectEvent)
            self.dataManager.registerValueUpdatedListener(self._onValueUpdatedEvent)
        else:
            self.networkchannel.unregisterConnectionListener(self._onConnectionStateChange)
            self.dataManager.unregisterRootObjectListener(self._onRootObjectEvent)
            self.dataManager.unregisterValueUpdatedListener(self._onValueUpdatedEvent)
        
        
    def _onConnectionStateChange(self, state, errstatus, errmsg):
        if state:
            self._signalPrintToLog.emit('New connection established.')
        else:
            if errstatus != 0:
                self._signalPrintToLog.emit('Connection Error: ' + errmsg)
            else:
                self._signalPrintToLog.emit('Connection Lost.')
                
    def _onRootObjectEvent(self, rootObject):
        self.widget.ui.logTextEdit.appendPlainText('Root Object resetted.')
        
    
    def _onValueUpdatedEvent(self, value, eventtype):
        msg = str()
        if eventtype == eValueUpdatedEventType.NEW:
            msg += 'New'
        elif eventtype == eValueUpdatedEventType.UPDATED:
            msg += 'Updated'
        else:
            msg += 'Deleted'
        msg += ' Record(' + str(value.pipId) + '): ' 
        if eventtype != eValueUpdatedEventType.NEW:
            msg += value.pathStr() + ' => '
        if value.valueType == eValueType.BOOL:
            msg += 'bool( '
        elif value.valueType == eValueType.INT_8:
            msg += 'int8( '
        elif value.valueType == eValueType.UINT_8:
            msg += 'uint8( '
        elif value.valueType == eValueType.INT_32:
            msg += 'int32( '
        elif value.valueType == eValueType.UINT_32:
            msg += 'uint32( '
        elif value.valueType == eValueType.FLOAT:
            msg += 'float( '
        elif value.valueType == eValueType.STRING:
            msg += 'string( '
        elif value.valueType == eValueType.ARRAY:
            msg += 'array( '
        elif value.valueType == eValueType.OBJECT:
            msg += 'object( '
        msg += str(value.value()) + ' )'
        self._signalPrintToLog.emit(msg)
