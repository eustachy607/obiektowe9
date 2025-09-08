from PyQt5 import QtWidgets
from power_bar import PowerBar

app = QtWidgets.QApplication([])
volume = PowerBar()
volume.show()
app.exec()
