import os

from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QFileDialog, QToolButton
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

from config import HOME
from page import Page


def on_download(download):
    start = os.path.join(os.path.expanduser("~"), "Downloads", download.downloadFileName())
    path, _ = QFileDialog.getSaveFileName(QApplication.activeWindow(), "Save file", start)
    if not path:
        download.cancel()
        return
    download.setDownloadDirectory(os.path.dirname(path))
    download.setDownloadFileName(os.path.basename(path))
    download.accept()


class Browser(QMainWindow):
    windows = []  # keeps references so windows aren't garbage collected

    def __init__(self, profile):
        super().__init__()
        self.profile = profile
        Browser.windows.append(self)
        self.setWindowTitle("5etools")
        self.resize(1400, 900)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        add_btn = QToolButton()
        add_btn.setText("+")
        add_btn.setToolTip("New tab (Ctrl+T)")
        add_btn.setAutoRaise(True)
        add_btn.clicked.connect(lambda: self.new_tab(HOME))
        add_btn.setStyleSheet("QToolButton { font-size: 18px; font-weight: bold; padding: 2px 10px; }")
        self.tabs.setCornerWidget(add_btn, Qt.Corner.TopLeftCorner)

        QShortcut(QKeySequence("Ctrl+N"), self, activated=self.new_window)
        QShortcut(QKeySequence("Ctrl+T"), self, activated=lambda: self.new_tab(HOME))
        QShortcut(QKeySequence("Ctrl+W"), self, activated=lambda: self.close_tab(self.tabs.currentIndex()))
        QShortcut(QKeySequence("Ctrl+Tab"), self, activated=lambda: self.cycle(1))
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self, activated=lambda: self.cycle(-1))
        QShortcut(QKeySequence("F5"), self, activated=lambda: self.tabs.currentWidget().reload())
        QShortcut(QKeySequence("Alt+Left"), self, activated=lambda: self.tabs.currentWidget().back())
        QShortcut(QKeySequence("Alt+Right"), self, activated=lambda: self.tabs.currentWidget().forward())

        self.new_tab(HOME)

    def new_window(self):
        w = Browser(self.profile)
        w.setWindowIcon(self.windowIcon())
        w.move(self.x() + 30, self.y() + 30)
        w.show()

    def closeEvent(self, event):
        if self in Browser.windows:
            Browser.windows.remove(self)
        super().closeEvent(event)

    def new_tab(self, url=None):
        view = QWebEngineView()
        view.setPage(Page(self.profile, self))
        i = self.tabs.addTab(view, "New Tab")
        self.tabs.setCurrentIndex(i)
        view.titleChanged.connect(
            lambda t, v=view: self.tabs.setTabText(self.tabs.indexOf(v), t[:25] or "New Tab")
        )
        if url:
            view.load(QUrl(url))
        return view

    def close_tab(self, i):
        if self.tabs.count() <= 1:
            self.close()
            return
        w = self.tabs.widget(i)
        self.tabs.removeTab(i)
        w.deleteLater()

    def cycle(self, step):
        self.tabs.setCurrentIndex((self.tabs.currentIndex() + step) % self.tabs.count())
