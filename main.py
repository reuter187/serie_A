import os
import sys
import threading

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QGridLayout, QMainWindow, QDialog, QDialogButtonBox, \
    QVBoxLayout, QLabel, qApp, QAction
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore, QtWidgets, QtGui
import main_ui as window
import ag_drive as ag
from datetime import datetime
import time
import csv

# Para displays de alta resolução
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

# Endereço do teste.
ADDRESS = 2


class TestClass(threading.Thread):
    def __init__(self, name=None, query=None):
        threading.Thread.__init__(self)
        self.iterations = 0
        self.daemon = True  # Allow main to exit even if still running.
        self.paused = True  # Start out paused.
        self.state = threading.Condition()
        self.name = name
        self.query = query
        self.sample = 0
        self.lock = threading.Lock()
        self.stop_event = False
        self.it_check = False
        self.set_point_index = 0
        self.renew_plot = False
        self.log_path = 'log'

    def run(self):
        self.pause()
        h_file = 'none'
        while True:
            with self.state:
                if self.paused:
                    self.state.wait()  # Block execution until notified.
            # if self.name == "logger":
            #     if h_file == 'none':
            #         if os.path.exists(self.log_path):
            #             h_file = 'log/log' + str(datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")) + '.csv'
            w.a102.set(4, 100)
            time.sleep(.5)
            w.a102.set(4, 0)
            time.sleep(.5)

    def resume(self):
        with self.state:
            self.paused = False
            self.state.notify()  # Unblock self if waiting.

    def pause(self):
        self.paused = True  # Block self.
        self.stop_event = True


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = window.Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('logo.ico'))
        self.statusBar().showMessage('Escolha a porta serial e pressione "Iniciar".')
        # Criação do objeto do controlador. O baud é padrão de fábrica.
        self.a102 = ag.AgDrive(address=ADDRESS, parity='N', stop_bits=2, timeout=0.8, baud=9600)
        self.ui.pushButton.clicked.connect(self.relay_test)
        self.test = TestClass()

    def relay_test(self):
        self.statusBar().showMessage(' ')
        self.a102.port = self.ui.comboBox.currentText()
        self.ui.label_2.setStyleSheet("background-color: rgba(0,0,0,0%)")
        self.ui.label_2.setText('...')
        QApplication.processEvents()
        time.sleep(.3)
        if self.a102.connect2instrument():
            check = self.a102.get(2)
            if check > 0:
                self.ui.label_2.setText('TESTANDO')
                self.ui.label_2.setStyleSheet("background-color: green")
                # self.statusBar().showMessage(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ' - Comunicação OK')
                self.test.start()
                self.test.resume()
            else:
                self.ui.label_2.setText('REPROVADO')
                self.ui.label_2.setStyleSheet("background-color: red")
                self.statusBar().showMessage(datetime.now().strftime(
                    "%d/%m/%Y %H:%M:%S") + ' - Erro: certifique-se que a porta é correta e tente novamente')
        else:
            self.statusBar().showMessage(datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S") + ' - Erro: conecte o conversor USB e escolha a porta correta')
            self.ui.label_2.setText('CONVERSOR')
            self.ui.label_2.setStyleSheet("background-color: yellow")


app = QApplication(sys.argv)
w = AppWindow()
w.show()
sys.exit(app.exec_())
