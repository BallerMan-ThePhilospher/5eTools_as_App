import threading
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

from config import ROOT, PORT


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def start_server():
    server = ThreadingHTTPServer(
        ("127.0.0.1", PORT), partial(QuietHandler, directory=ROOT)
    )
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server