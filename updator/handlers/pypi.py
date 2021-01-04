# Copyriglt 2021 Naveen M K
# SPDX-License-Identifier: MIT
import os

import requests

from .handler import Handler


class PyPiHandler(Handler):
    def __init__(self, info) -> None:
        self.info = info
        self.api_url = f"https://pypi.org/pypi/{info['project']}/json"
    @property
    def remote_version(self) -> str:
        if hasattr(self,'_remote_version'):
            return self._remote_version
        con = requests.get(self.api_url).json()
        version = con['info']['version']
        self._remote_version = version
        return version
