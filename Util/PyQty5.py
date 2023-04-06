import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout


#Exemplo 1
app = QApplication([])
window = QWidget()
layout = QVBoxLayout()
layout.addWidget(QPushButton('Top'))
layout.addWidget(QPushButton('Bottom'))
window.setLayout(layout)
window.show()
app.exec()

#Exemplo 2
def basicWindow():
    app = QtWidgets.QApplication(sys.argv)
    windowExample = QtWidgets.QWidget()
    windowExample.setWindowTitle('Teste Tela')
    windowExample.show()
    sys.exit(app.exec_())
basicWindow()


