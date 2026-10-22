import base64

from PyQt6.QtGui import QIcon, QPixmap

from icon_data import ICON_B64

try:
    import pyi_splash
except ImportError:
    pyi_splash = None  # running as a normal script, no splash

_splash_closed = False


def close_splash():
    global _splash_closed
    if pyi_splash and not _splash_closed:
        pyi_splash.close()
        _splash_closed = True


def load_icon():
    pm = QPixmap()
    data = ICON_B64.strip()
    if data and pm.loadFromData(base64.b64decode(data)):
        return QIcon(pm)
    return QIcon()