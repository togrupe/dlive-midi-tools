# coding=utf-8
####################################################
# Mixing Station HTTP REST Client
#
# Author: Tobias Grupe
####################################################

import json
import urllib.error
import urllib.request


class MixingStationClient:
    def __init__(self, host, port):
        self._base = f"http://{host}:{port}"

    def set(self, param_path, value, fmt=None):
        url = f"{self._base}/console/data/set/{param_path}/val"
        if fmt is None:
            if isinstance(value, bool):
                fmt = "bool"
            elif isinstance(value, str):
                fmt = "string"
            elif isinstance(value, float):
                fmt = "float"
            else:
                fmt = "int"
        payload = json.dumps({"format": fmt, "value": value}).encode("utf-8")
        req = urllib.request.Request(
            url, data=payload, method="POST",
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5):
            pass

    def get(self, param_path):
        url = f"{self._base}/console/data/get/{param_path}/val"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())

    def test_connection(self):
        url = f"{self._base}/app/state"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            resp.read()

    def close(self):
        pass
