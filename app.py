import os, sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtWebEngineCore import QWebEngineProfile

from browser import Browser, on_download
from helpers import load_icon, close_splash
from server import start_server
from site_manager import ensure_site, update_site


def main():
    app = QApplication(sys.argv)
    icon = load_icon()
    app.setWindowIcon(icon)

    if not ensure_site(app):
        sys.exit(0)

    update_site()
    server = start_server()

    profile = QWebEngineProfile("5etools-app", app)
    profile.setPersistentStoragePath(os.path.join(os.path.expanduser("~"), ".5etools-app"))
    profile.downloadRequested.connect(on_download)

    win = Browser(profile)
    win.setWindowIcon(icon)
    win.show()
    close_splash()

    code = app.exec()
    server.shutdown()
    sys.exit(code)


if __name__ == "__main__":
    main()