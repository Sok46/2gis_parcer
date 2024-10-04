from PyQt6.QtGui import QWindow
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget,\
    QLabel
import win32con
import win32gui


class Window(QWidget):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.resize(800, 600)
        layout = QVBoxLayout(self)

        self.myhwnd = int(self.winId())


        layout.addWidget(QPushButton('Show Tab', self,clicked=self._getWindowList, maximumHeight=30))
        layout.addWidget(
            QLabel('Double click to Embedd\nĐịnh dạng là: xử lý | xử lý mẹ | tiêu đề | tên lớp', self, maximumHeight=30))
        self.windowList = QListWidget(
            self, itemDoubleClicked=self.onItemDoubleClicked, maximumHeight=200)
        layout.addWidget(self.windowList)


    def _getWindowList(self):
        self.windowList.clear()
        win32gui.EnumWindows(self._enumWindows, None)
        # print(win32gui.EnumWindows(self._enumWindows, None))

    def onItemDoubleClicked(self, item):
        self.windowList.takeItem(self.windowList.indexFromItem(item).row())
        hwnd, phwnd, _, _ = item.text().split('|')

        hwnd, phwnd = int(hwnd), int(phwnd)
        print(hwnd, phwnd)
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        print('save', hwnd, style, exstyle)

        widget = QWidget.createWindowContainer(QWindow.fromWinId(hwnd))
        widget.setFixedHeight(400)
        widget.hwnd = hwnd
        widget.phwnd = phwnd
        widget.style = style
        widget.exstyle = exstyle
        widget.setParent(self)
        layout = QVBoxLayout()
        layout.addWidget(widget)
        self.layout().addLayout(layout)


    def _enumWindows(self, hwnd, _):
        if hwnd == self.myhwnd:
            return
        if win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            phwnd = win32gui.GetParent(hwnd)
            title = win32gui.GetWindowText(hwnd)
            name = win32gui.GetClassName(hwnd)
            self.windowList.addItem(
                '{0}|{1}|\tTiêu đề：{2}\t|\Lớp: {3}'.format(hwnd, phwnd, title, name))


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec())





