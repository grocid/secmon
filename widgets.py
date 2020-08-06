from time import sleep
import math

from qtpy.QtCore import QThread, Signal, QSize, Qt, QRect
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget,  QListWidgetItem, QLabel, QStyle, QGraphicsOpacityEffect

from qtpy.QtGui import QFont, QPixmap, QIcon
from qtpy.QtGui import QPainter, QPainterPath, QColor, QPen
from subprocess import check_output


class LogThread(QThread):

    update = Signal(object)

    def __init__(self, parent=None, 
                 function=None, filename=None, interval=1):
        QThread.__init__(self, parent)
        self.function = function
        self.filename = filename
        self.interval = interval
    
    def run(self):
        with open(self.filename, 'r') as f:
            while True:
                data = f.readline()
                if data:
                    ret = self.function(data)
                    if ret:
                        self.update.emit(ret)
                else:
                    sleep(self.interval)


class CommandThread(QThread):
    
    update = Signal(object)

    def __init__(self, parent=None, 
                 function=None, command=None, interval=1):
        QThread.__init__(self, parent)
        self.function = function
        self.command = command
        self.interval = interval
    
    def run(self):
        current = None
        while True:
            out = check_output(self.command)
            ret = self.function(out)
            if not ret == current and ret:
                current = ret
                self.update.emit(ret)
            sleep(self.interval)


class GraphThread(QThread):

    update = Signal(object)

    def __init__(self, parent=None, 
                 function=None, 
                 filename=None,
                 interval=1,
                 delta=True
        ):
        QThread.__init__(self, parent)
        self.function = function
        self.filename = filename
        self.interval = interval
        self.delta = delta
        self.currentvalue = None
    
    def run(self):
        
        with open(self.filename, 'r') as f:
            while True:
                f.seek(0)
                try:
                    ret = int(f.read())
                except:
                    ret = 0
                if self.currentvalue is None:
                    self.currentvalue = ret
                    d = 0
                if self.delta and self.currentvalue is not None:
                    d = ret - self.currentvalue
                    self.currentvalue = ret - d//10
                    ret = d
                else:
                    self.currentvalue = ret
                self.update.emit(
                    self.function(ret)
                )
                sleep(self.interval)


class TitleWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.titleLabel = QLabel()
        font = QFont()
        font.setPointSize(72)
        self.titleLabel.setFont(font)
        self.iconLabel = QLabel()
        layout = QHBoxLayout()
        layout.addWidget(self.iconLabel)
        layout.addWidget(self.titleLabel)
        print("boom")
        
        self.setTitle("Terminal")
        self.setIcon("terminal")
    
    def setIcon(self, icon):
        self.iconLabel.setPixmap(
            QIcon.fromTheme(icon).pixmap(QSize(128, 128))
        )
    def setTitle(self, title):
        self.titleLabel.setText(title)
            

class SidebarWidget(QWidget):    
    def __init__(self, parent=None, thread=None, iconsize=32):
        QWidget.__init__(self, parent=parent)
        self.list = QListWidget()
        self.list.setAttribute(Qt.WA_TranslucentBackground)
        self.list.setSortingEnabled(True)
        layout = QVBoxLayout(self)
        layout.addWidget(self.list)
        self.iconsize = iconsize

    def addEntry(self, title, description, icon):
        entry = EntryWidget()
        entry.setTitle(title)
        entry.setDescription(description)
        entry.setDate("")
        entry.setIcon(QIcon.fromTheme(icon))
        
        item = QListWidgetItem(self.list)
        item.setSizeHint(entry.sizeHint())
        self.list.insertItem(0, item)
        self.list.setItemWidget(item, entry)
        
        return self.list.count()
        

class EntryWidget(QWidget):
    def __init__ (self, parent = None):
        super(EntryWidget, self).__init__(parent)
        self.textQVBoxLayout = QVBoxLayout()
        self.allQHBoxLayout = QHBoxLayout()
        self.allQHBoxLayout.setAlignment(Qt.AlignCenter)
        
        self.titleLabel = QLabel()
        boldFont = QFont()
        boldFont.setBold(True)
        self.titleLabel.setFont(boldFont)
        self.descriptionLabel = QLabel()
        self.textQVBoxLayout.addWidget(self.titleLabel)
        self.textQVBoxLayout.addWidget(self.descriptionLabel)
               
        self.dateLabel = QLabel()
        self.iconLabel = QLabel()
        
        self.allQHBoxLayout.addWidget(self.iconLabel, 0)
        self.allQHBoxLayout.addLayout(self.textQVBoxLayout, 1)
        self.allQHBoxLayout.addWidget(self.dateLabel, 0)
        self.setLayout(self.allQHBoxLayout)

    def setTitle(self, text):
        self.titleLabel.setText(text)

    def setDescription (self, text):
        self.descriptionLabel.setText(text)

    def setDate(self, text):
        self.dateLabel.setText(text)

    def setIcon(self, icon, iconsize=32):
        self.iconLabel.setPixmap(
            icon.pixmap(QSize(iconsize, iconsize))
        )
    
    def setStyle(self, style):
        self.dateLabel.setStyleSheet(style) 


class LogWidget(QWidget):
    
    def __init__(self, parent=None, thread=None, iconsize=32):
        QWidget.__init__(self, parent=parent)
        self.log = QListWidget()
        self.log.setSortingEnabled(True)
        layout = QVBoxLayout(self)
        layout.addWidget(self.log)
        self.iconsize = iconsize
        
        self.thread = thread
        assert(thread is not None)
        self.thread.update.connect(self.update_progress)
        self.thread.start()

    def update_progress(self, progress):
        if not progress:
            return
        title, description, date, icon = progress
        
        entry = EntryWidget()
        entry.setTitle(title)
        entry.setDescription(description)
        entry.setDate(date)
        entry.setIcon(QIcon.fromTheme(icon))
        
        item = QListWidgetItem(self.log)
        item.setSizeHint(entry.sizeHint())
        
        self.log.insertItem(0, item)
        self.log.setItemWidget(item, entry)


class UpdatingWidget(LogWidget):
    
    def __init__(self, parent=None, thread=None, iconsize=64, style_thresh=None):
        LogWidget.__init__(self, parent=parent, thread=thread, iconsize=iconsize)
        self.style_thresh = style_thresh

    def update_progress(self, progress):
        if not progress:
            return
        
        self.log.clear()
        
        for entry in progress:
            title, description, date, icon = entry
            
            entry = EntryWidget()
            entry.setTitle(title)
            entry.setDescription(description)
            entry.setDate(date)
            entry.setIcon(QIcon.fromTheme(icon), self.iconsize)

            if self.style_thresh:
                if (int(date) < self.style_thresh):
                    entry.setStyle("color: lightgreen")
                else:
                    entry.setStyle("color: lightsalmon")
            
            item = QListWidgetItem(self.log)
            item.setSizeHint(entry.sizeHint())
            
            self.log.insertItem(0, item)
            self.log.setItemWidget(item, entry)


class SplashWidget(QWidget):
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.image = QLabel(self)
        pixmap = (
            QPixmap('images/splash.png')
            .scaledToHeight(300, Qt.SmoothTransformation)
        )
        self.image.setPixmap(
            pixmap
        )
        self.image.setAlignment(
            Qt.AlignHCenter | 
            Qt.AlignVCenter
        )
        self.setFixedWidth(800)
        self.setFixedHeight(600)
        self.image.setFixedWidth(800)
        self.image.setFixedHeight(600)

class GraphWidget(QWidget):
    
    def __init__(self, parent=None, thread=None):
        QWidget.__init__(self, parent=parent)
        self.setFixedWidth(600)
        self.setFixedHeight(600)
        self.points = [3 for i in range(120-14)]
        self.colors = [
            QColor(0xff, 0xff, 0xff),
            QColor(0xff, 0xff, 0xcc),
            QColor(0xff, 0xed, 0xa0),
            QColor(0xfe, 0xd9, 0x76),
            QColor(0xfe, 0xb2, 0x4c),
            QColor(0xfd, 0x8d, 0x3c),
            QColor(0xfc, 0x4e, 0x2a),
            QColor(0xe3, 0x1a, 0x1c),
            QColor(0xdb, 0x00, 0x26),
            QColor(0x80, 0x00, 0x26)
        ]
        self.thread = thread
        assert(thread is not None)
        self.thread.update.connect(self.update_progress)
        self.thread.start()
    
    def update_progress(self, point):
        self.points.append(point)
        self.points.pop(0)
        self.repaint()
    
    def paintEvent(self, e):
        if self.points is None:
            return
        painter = QPainter(self)
        pen = QPen()  # creates a default pen

        pen.setWidth(2)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing)
 
        # to avoid zero division
        m = max(max(self.points), 10)
        for i, v in enumerate(self.points):
            pen.setBrush(self.colors[min(v * len(self.colors) // m, len(self.colors)-1)])
            painter.setPen(pen)
            painter.drawLine(
                40 + 5 * i, self.height() // 2 - min(v, self.height()) // 2,
                40 + 5 * i, self.height() // 2 + min(v, self.height()) // 2,
            )

        painter.end()

class TestGraph(GraphWidget):
    
    rx_bytes = "/sys/class/net/%s/statistics/rx_bytes"
    
    def __init__(self, parent=None, interface="eno1"):
        GraphWidget.__init__(self, parent=parent,
                           thread=GraphThread(
                               function=TestGraph.testGraphWidgetCallback, 
                               filename=(TestGraph.rx_bytes % interface),
                               interval=0.3
                            ))

    def testGraphWidgetCallback(data):
        try:
            return int(10 * math.log(data+1, 2) + 2)
        except Exception as e:
            print(e)
            return 0
        


class AuthLogWidget(LogWidget):
    
    authlogPath = "/var/log/auth.log"
    
    def __init__(self, parent=None):
        LogWidget.__init__(self, 
                                parent=parent,
                                iconsize=64,
                                thread=LogThread(
                                function=AuthLogWidget.authLogWidgetCallback, 
                                filename=AuthLogWidget.authlogPath,
                                interval=2)
                           )
        self.setFixedWidth(600)
        self.setFixedHeight(600)

    def authLogWidgetCallback(data):
        if "authentication failure" in data:
            sdata = data.split("authentication failure")
            date = sdata[0].split()[2][:-3]
            description = sdata[1].strip(";").strip(" ").strip()
            if "sshd:auth" in sdata[0]:
                title = "SSH authentication failure"
                icon = "network"
            else:
                title = "Local authentication failure"
                icon = "system-file-manager" # terminal
            return (title, description, date, icon)
        else:
            return False


class UfwLogWidget(UpdatingWidget):
    
    ufwCommand = "./get_ufw_stats.sh"
    
    def __init__(self, parent=None):
        UpdatingWidget.__init__(self, 
                                    parent=parent,
                                    thread=CommandThread(
                                    function=UfwLogWidget.ufwLogWidgetCallback, 
                                    command=UfwLogWidget.ufwCommand,
                                    interval=10
                               ),
                           iconsize=32, style_thresh=20)
        self.setFixedWidth(300)
        self.setFixedHeight(600)

    def ufwLogWidgetCallback(data):
        out = []
        for line in data.split(b'\n'):
            try:
                ltime, title = line.split()
                icon = "network-firewall"
                out.append((
                    title.decode("utf-8"), 
                    "blocked", 
                    ltime.decode("utf-8"),
                    icon
                ))
            except:
                pass
        return out
    

class LoggedInUsersWidget(UpdatingWidget):
    def __init__(self, parent=None):
        UpdatingWidget.__init__(self, parent=parent,
                           thread=CommandThread(
                               function=LoggedInUsersWidget.loggedInUsersWidgetCallback, 
                               command=["who"],
                               interval=2
                               ),
                            iconsize=32)
        self.setFixedWidth(300)

    def loggedInUsersWidgetCallback(data):
        out = []
        for line in data.split(b'\n'):
            try:
                if not line:
                    continue
                user, tty, date, ltime, addr = line.split()
                if addr == b"(:0)":
                    addr = b"local"
                    icon = "user"
                else:
                    addr = addr[1:-1]
                    icon = "network"
                out.append((
                    addr.decode("utf-8"), 
                    (user + b" on " + tty).decode("utf-8"),
                    ltime.decode("utf-8"),
                    icon)
                )
            except:
                pass
        return out

