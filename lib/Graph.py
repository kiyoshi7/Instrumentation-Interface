from PyQt5 import QtWidgets, uic
import os
PathSep = os.path.sep

class Graph(QtWidgets.QWidget):
    def __init__(self, MainDir = None):
        super(Graph, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi(MainDir + PathSep + 'UI' + PathSep + 'Graph.ui', self)  # Load the .ui file
        self.Show()  # Show the GUI

    def Show(self):
        self.show()

    def Hide(self):
        self.hide()
