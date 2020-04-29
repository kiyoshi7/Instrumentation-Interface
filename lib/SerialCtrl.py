# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 12:15:04 2019

@author: Daniel
"""
import serial
from serial.tools import list_ports
import time


class Connection:
    def __init__(self, port, baud, parent = None):
        self.port = port
        self.baud = baud
        self.Device = None
        self.Parent = parent
        self.TimeOut = 1*60

    def SetTimeOut(self, Time = 1):
        self.TimeOut = Time*60

    def Connect(self):
        try:
            self.Device = serial.Serial(self.port, baudrate=self.baud, timeout=4)
            self.Device.flushInput()
            self.Device.flushOutput()
            #self.SendRead("0000")
            return [True, None]
        except Exception as error:
            self.HandleError(error)
            return [False, error]

    def SendData(self, cmd):
        set_temp1 = f'Dani{str(cmd)}00000000\r\n'
        self.Device.write(set_temp1.encode())
        self.Device.flushInput()

    def ReadData(self):
        data = []
        start = time.time()
        device = self.Device.in_waiting
        while not device:
            if time.time()>start+self.TimeOut:
                return "Time out"
            pass
        while self.Device.in_waiting:
            try:
                d = self.Device.readline().decode('utf-8').rstrip("\n\r")
                d = [x.strip() for x in d.split("\t")]
                for i in d:
                    data.append(i)
                data.append(time.time())
            except Exception as error:
                self.HandleError(error)
        return data


class SerialConnection:
    BaudRates = [9600]  # , 14400, 19200, 28800, 38400, 57600, 115200]
    CommTest = "sKIAjfrcfvmo2CbzOsogvkR9dm7ZOaSN"
    EXCLUDE = []
    ID = ""

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            if name.upper() == "EXCLUDE":
                if isinstance(value, list):
                    for i in value:
                        self.EXCLUDE.append(i)

        # self.Find()
    def HandleError(self, error):
        # self.Error = True
        # print("{}. line:{}".format(error, error.__traceback__.tb_lineno))
        self.EMsg = "{}. line:{}".format(error, error.__traceback__.tb_lineno)
        # return  # self.EMsg
        # print("{}. line:{}".format(error, error.__traceback__.tb_lineno))

    def Find(self):
        # returned variable
        Devices = {'NumberOfDevices': 0, 'Ports': [], 'Baud': [], 'ID': []}
        # List all devices present on the computer
        devices = [p.device for p in serial.tools.list_ports.comports()]
        # Iterates through all devices excluding the EXCLUDE list
        for i in list(set(devices) - set(self.EXCLUDE)):
            #checks if device is a
            a = self.FindValidInstruments(i)
            if a[0]:
                Devices['NumberOfDevices'] += 1
                Devices['Ports'].append(i)
                Devices['Baud'].append(a[1])
                Devices['ID'].append(a[2])
                # self.EXCLUDE.append(i)

        return Devices

    def FindValidInstruments(self, COMPORT):
        for i in self.BaudRates:
            device = serial.Serial(COMPORT, baudrate=i, timeout=4)
            self.Device = device
            device.flushInput()
            device.flushOutput()
            for j in range(10):
                din = self.SendRead("0000")
                if len(din) != 0:
                    if din[0] == self.CommTest:
                        ID = (self.SendRead("0001")[0])
                        device.close()
                        return [True, i, ID]
            self.Disconnect()
            return [False]

    def SendData(self, cmd):
        set_temp1 = 'Dani' + str(cmd) + '\r\n'
        self.Device.write(set_temp1.encode())
        self.Device.flushInput()

    def SendRead(self, d):
        data = []
        while self.Device.in_waiting == 0:
            self.SendData(d)
            time.sleep(0.5)
        while self.Device.in_waiting:
            try:
                d = self.Device.readline().decode('utf-8').rstrip("\n\r")
                d = [x.strip() for x in d.split("\t")]
                for i in d:
                    data.append(i)
                data.append(time.time())
            except Exception as error:
                self.HandleError(error)
        return data

    def Connect(self, port, baud):
        try:
            Device = serial.Serial(port, baudrate=baud, timeout=4)
            Device.flushInput()
            Device.flushOutput()
            #self.SendRead("0000")
            return [True, Device]
        except Exception as error:
            self.HandleError(error)
            return [False, error]

    def Disconnect(self, Device):
        Device.close()
