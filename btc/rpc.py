import json
import base64
from twisted.internet import defer
from twisted.web import client

from logzero import logger


class BitcoinRPC(object):
    def __init__(self, host, port, username, password):
        self.url = f"http://{host}:{port}"
        self.credentials = base64.b64encode(f"{username}:{password}".encode("utf-8"))
        self.headers = {
            "Content-Type": "text/json",
            "Authorization": f"Basic {self.credentials}"
        }

    def _call_raw(self, data):
        pass

    def _call(self, method, params):
        return self._call_raw(json.dumps({
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": "1"
        }))
