from PyQt5 import QtWidgets, uic, QtCore, QtGui
from lib import SerialCtrl
from Devices import Instruments
import inspect
import os
import sip
from lib import Collapsible

PathSep = os.path.sep

class Devices(QtWidgets.QWidget):
    ConnectedDevices = []
    FoundDeviceButtons = []
    Instruments = {}

    def __init__(self, parent = None, MainDir = None):
        super(Devices, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi(MainDir + PathSep + 'UI' + PathSep + 'Devices.ui', self)  # Load the .ui file
        self.MainDir = MainDir
        self.parent = parent
        self.Serial = SerialCtrl.SerialConnection()
        self.show()  # Show the GUI
        self.RefreshButton.clicked.connect(lambda: self.NumberOfDevices())
        self.DevicesLayout.setAlignment(QtCore.Qt.AlignTop)

    def NumberOfDevices(self):
        devices = self.Serial.Find()
        self.DevicesLabel.setText(f'Devices: {devices["NumberOfDevices"] + len(self.ConnectedDevices)}')
        # self.FoundDeviceButtons
        for i in self.FoundDeviceButtons:
            self.DevicesLayout.removeWidget(i)
        for i in range(devices["NumberOfDevices"]):
            button = self.DeviceButton(devices["Ports"][i], devices["Baud"][i], f"{devices['ID'][i]}")
            self.DevicesLayout.addWidget(button)
            self.FoundDeviceButtons.append(button)

    def DeviceButton(self, Port, baud, text=''):
        button = QtWidgets.QPushButton(text)
        button.setIcon(QtGui.QIcon(self.MainDir + PathSep + 'Images' + PathSep + 'DisCon.png'))
        button.clicked.connect(lambda: self.DeviceButtonFunction(button, Port, baud, text))
        return button

    def DeviceButtonFunction(self, button, port, baud, id):
        if (button) in self.FoundDeviceButtons:
            a = SerialCtrl.Connection(port, baud, parent=self)
            s = a.Connect()
            # a returns true if connected [t/f, None/error]
            if s:
                button.setIcon(QtGui.QIcon(self.MainDir + PathSep + 'Images' + PathSep + 'Conn.png'))
                self.FoundDeviceButtons.remove(button)
                self.ConnectedDevices.append(button)
                self.Serial.EXCLUDE.append(port)

                if id not in self.Instruments:
                    self.Instruments[id] = a
                    self.AddInstrumentButtons(id)
                    self.parent.Console.localNamespace[f'_{id}'] = a
                else:
                    i = 0
                    l = True
                    while l:
                        if (id + f'{i}') not in self.Instruments:
                            self.Instruments[id] = a
                            self.AddInstrumentButtons(id)
                            l = False
                        else:
                            i += 1
            else:
                print(f"{s[1]}. line:{s[1].__traceback__.tb_lineno}")
                pass
        elif (button) in self.ConnectedDevices:
            button.setIcon(QtGui.QIcon(self.MainDir + PathSep + 'Images' + PathSep + 'DisCon.png'))
            self.FoundDeviceButtons.append(button)
            self.ConnectedDevices.remove(button)
            k = list({key: val for key, val in self.Instruments.items() if val != button}.keys())[0]
            del self.Instruments[k]
            self.Serial.EXCLUDE.remove(port)
            self.RemoveInstrumentButtons(id)
            del self.parent.Console.localNamespace[f'_{id}']

    def AddInstrumentButtons(self, id):
        # find device class
        clsmembers = inspect.getmembers(Instruments, inspect.isclass)
        for i in clsmembers:
            if id[:4] in i[0]:
                DeviceClass = getattr(__import__('Devices', fromlist=[i[0]]), i[0])
                a = DeviceClass.Info(id)
                DeviceInfo = a.get()
        # self.parent.Commands.AddButtons(id)
        self.parent.Commands.Add(id, DeviceInfo)
        pass

    def RemoveInstrumentButtons(self, id):
        self.parent.Commands.Remove(id)
        pass

class ColapsableCommands(QtWidgets.QWidget):
    def __init__(self, parent = None, MainDir = None):
        super(ColapsableCommands, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi(MainDir + PathSep + 'UI' + PathSep + 'Commands.ui', self)  # Load the .ui file
        self.DevicesLayout.setAlignment(QtCore.Qt.AlignTop)
        self.categories = ['Id',
                           'AnalogIn',
                           'AnalogOut',
                           'Digital']
        self.ActiveDevices={}
        self.parent = parent
        self.show()  # Show the GUI

    def ButtonFunction(self, command):
        self.parent.Console.input.insert(command)


    def Add(self, id, DeviceInfo):
        DeviceBox = Collapsible.CollapsibleBox(f"{id}")
        self.ActiveDevices[id] = DeviceBox
        self.DevicesLayout.addWidget(DeviceBox)
        DeviceBoxLay = QtWidgets.QVBoxLayout()
        DeviceBoxLay.addStretch()
        for i in self.categories:
            if len(DeviceInfo[i]) != 0:
                for j in DeviceInfo[i]:
                    button = QtWidgets.QPushButton(j[0])
                    button.clicked.connect(lambda ch, i=j[1]: self.ButtonFunction(i))  # < ---
                    DeviceBoxLay.addWidget(button)

        DeviceBox.setContentLayout(DeviceBoxLay)

    def Remove(self, id):
        self.DevicesLayout.removeWidget(self.ActiveDevices[id])
        sip.delete(self.ActiveDevices[id])
        self.ActiveDevices[id] = None

################
################
################
class Commands(QtWidgets.QWidget):
    def __init__(self, parent = None, MainDir = None):
        super(Commands, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi(MainDir + PathSep + 'UI' + PathSep + 'Commands.ui', self)  # Load the .ui file
        self.Instruments = {}
        self.DigitalLineIndex = 0
        self.DigitalLineIndexInstrument = {}
        self.categories = [['Id', self.DevicesLayout],
                           ['AnalogIn', self.AnalogInLayout],
                           ['AnalogOut', self.AnalogOutLayout],
                           ['Digital', self.DigitalLayout]]
        self.DevicesLayout.setAlignment(QtCore.Qt.AlignTop)
        self.AnalogInLayout.setAlignment(QtCore.Qt.AlignTop)
        self.AnalogOutLayout.setAlignment(QtCore.Qt.AlignTop)
        self.DigitalLayout.setAlignment(QtCore.Qt.AlignTop)
        self.show()  # Show the GUI


    def AddButtons(self, id):
        self.DigitalLineIndexInstrument[id] = 0
        self.Instruments[id] = {}
        for i in self.categories:
            self.Instruments[id][i[0]] = []

        # find device class
        clsmembers = inspect.getmembers(Instruments, inspect.isclass)
        for i in clsmembers:
            if id[:4] in i[0]:
                DeviceClass = getattr(__import__('Devices', fromlist=[i[0]]), i[0])
                a = DeviceClass.Info(id)
                DeviceInfo = a.get()

        for j in self.categories:
            if (j[0] != 'Id')&(len(DeviceInfo[j[0]]) != 0) :
                label = QtWidgets.QLabel(id)
                self.Instruments[id][j[0]].append(label)
                j[1].addWidget(self.Instruments[id][j[0]][-1])
                if j[0] == 'Digital':
                    self.DigitalLineIndex += 1
                    self.DigitalLineIndexInstrument[id] += 1
            if j[0] != 'Digital':
                for i in DeviceInfo[j[0]]:
                    button = QtWidgets.QPushButton(i[0])
                    self.Instruments[id][j[0]].append(button)
                    j[1].addWidget(self.Instruments[id][j[0]][-1])
            else:
                for i in DeviceInfo['Digital']:
                    label = QtWidgets.QLabel(i[0]+': ')
                    buttonLow = QtWidgets.QPushButton("Low")
                    buttonHigh = QtWidgets.QPushButton("High")
                    buttonRead = QtWidgets.QPushButton("Read")

                    self.DigitalLayout.addWidget(label, self.DigitalLineIndex, 0)
                    self.DigitalLayout.addWidget(buttonLow, self.DigitalLineIndex, 1)
                    self.DigitalLayout.addWidget(buttonHigh, self.DigitalLineIndex, 2)
                    self.DigitalLayout.addWidget(buttonRead, self.DigitalLineIndex, 3)

                    self.Instruments[id][j[0]].append(label)
                    self.Instruments[id][j[0]].append(buttonLow)
                    self.Instruments[id][j[0]].append(buttonHigh)
                    self.Instruments[id][j[0]].append(buttonRead)
                    self.DigitalLineIndex += 1
                    self.DigitalLineIndexInstrument[id] += 1

        #self.DevicesLayout.addWidget(button)

    def DeleteButtons(self, id):
        for i in self.categories:
            for j in self.Instruments[id][i[0]]:
                i[1].removeWidget(j)