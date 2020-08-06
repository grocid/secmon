import sys

from os.path import join, dirname, abspath, basename, isdir
from os import listdir

from qtpy.QtCore import Slot, Qt, QCoreApplication
from qtpy.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QGraphicsBlurEffect, QLabel

import qtmodern.styles
import qtmodern.windows

from widgets import SidebarWidget, AuthLogWidget, LoggedInUsersWidget, UfwLogWidget, SplashWidget, TestGraph, TitleWidget

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
       
        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.widget = QWidget()
        self.widget.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)       
        self.setContentsMargins(0, 0, 0, 0)
        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("Arkiv")
        #fileMenu.addAction(exitAct)

        self.sidebar = SidebarWidget()
        self.sidebar.list.clicked.connect(self.action)
        self.sidebar.setFixedWidth(258)
        self.sidebar.setObjectName('sideBar')
        self.sidebar.move(-10, 0)
        self.layout.addWidget(self.sidebar)
        self.currentView = 0
        
        self.titleLabel = TitleWidget()
        self.titleLabel.setTitle("Bongo")
        self.titleLabel.setIcon("terminal")
        self.subLayout = QVBoxLayout()
        self.layout.addLayout(self.subLayout)
        self.innerLayout = QHBoxLayout()
        self.subLayout.addWidget(self.titleLabel)
        self.subLayout.addLayout(self.innerLayout)
        
        
        self.actions = {
            self.sidebar.addEntry( # 1
                "Autentiseringar", 
                "Visar anslutningar",
                "terminal"
            ): self._show_auths,
            self.sidebar.addEntry( # 2
                "Brandvägg",
                "Status på brandvägg",
                "firewall"
            ): self._show_firewall,
            self.sidebar.addEntry( # 3
                "PAM", 
                "Aktiva PAM-moduler", 
                "security-high"
            ): self._show_pams,
            self.sidebar.addEntry( # 4
                "Tjänster", 
                "Körande tjänster", 
                "settings"
            ): self._show_services
        }

        self.widgets = {
            0: [
                self.titleLabel,
                SplashWidget()
            ],
            1: [
                self.titleLabel,
                AuthLogWidget(),
                LoggedInUsersWidget(),
            ], 
            2: [
                self.titleLabel,
                UfwLogWidget(),
                TestGraph(),
            ],
            3: [],
            4: []
        }
        
        # add all widgets to be run in the background
        for group in self.widgets.values():
            for widget in group:
                self.innerLayout.addWidget(widget)
                
        self.updateWidgets()
        self.show()

    def updateWidgets(self):
        for group in self.widgets:
            for widget in self.widgets.get(group):
                widget.setHidden(True)
        for widget in self.widgets.get(self.currentView):
            widget.setHidden(False)
        
        self.resize(self.sizeHint())
        self.fixSize()
        self.show()

    def action(self):
        # this is simple way to get 
        # around the unhashable property of
        # QListWidgetItem
        idx = self.sidebar.list.count() - self.sidebar.list.currentRow()
        if self.currentView != idx:
            self.actions.get(
                idx
            )()
            self.currentView = idx
            self.updateWidgets()

    
    def _show_auths(self):
        self.updateWidgets()

    def _show_firewall(self):
        self.updateWidgets()
        
    def _show_pams(self):
        self.updateWidgets()
        
    def _show_services(self):
        self.updateWidgets()
    
    def fixSize(self):
        self.widget.resize(self.widget.sizeHint())
        self.resize(self.sizeHint())
        
    def lightTheme(self):
        qtmodern.styles.light(QApplication.instance())

    def darkTheme(self):
        qtmodern.styles.dark(QApplication.instance())

    @Slot()
    def on_pushButton_clicked(self):
        self.close()

    @Slot()
    def closeEvent(self, event):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Säkerhetsmonitor")
    qtmodern.styles.dark(app)
    mw = qtmodern.windows.ModernWindow(MainWindow())
    mw.show()

    sys.exit(app.exec_())
