import pyqtgraph.console
from PyQt5 import QtWidgets, uic
import sys
import os
ScriptDir = os.path.dirname(os.path.realpath(__file__))
PathSep = os.path.sep

from lib import Graph, LeftWidget

class Main(QtWidgets.QMainWindow):
    def __init__(self):
        #self.text = 'aba'
        super(Main, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi(ScriptDir + PathSep + 'UI' + PathSep + 'Main.ui', self)  # Load the .ui file
        self.showMaximized()

        # Widgets
        self.Devices = LeftWidget.Devices(parent=self, MainDir=ScriptDir)
        self.Commands = LeftWidget.ColapsableCommands(parent=self, MainDir=ScriptDir)
        self.Console = pyqtgraph.console.ConsoleWidget(namespace={})
        self.Graph = Graph.Graph(MainDir=ScriptDir)
        self.Graph.resize(100, self.Graph.height())
        self.RightSplitter.resize(100, self.RightSplitter.height())

        self.LeftSplitter.addWidget(self.Devices)
        self.LeftSplitter.addWidget(self.Commands)
        self.CenterSplitter.addWidget(self.Console)
        self.RightSplitter.addWidget(self.Graph)
        self.show()  # Show the GUI



app = QtWidgets.QApplication(sys.argv)
window = Main()
app.exec_()
