from PyQt5.QtWidgets import QApplication
from animated_toggle import AnimatedDemo

app = QApplication([])

window = AnimatedDemo()
window.show()

app.exec()
