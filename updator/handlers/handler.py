# Copyright 2021 Naveen M K
# SPDX-License-Identifier: MIT

from ..constants import REPO_PATH, Regex
from ..utils import version_is_newer_than


class Handler:
    def __init__(self, info) -> None:
        pass

    @property
    def remote_version(self) -> None:
        pass

    @property
    def current_version(self) -> None:
        if hasattr(self,'_current_version'):
            return self._current_version
        info = self.info
        version_regex = Regex.version_parse.value
        path_folder = REPO_PATH / info["name"]
        with open(path_folder / "PKGBUILD") as f:
            temp = version_regex.search(f.read())
            version = temp.group("version")
        self._current_version = version
        return version

    @property
    def update(self):
        upstream = self.remote_version
        current_version = self.current_version
        return version_is_newer_than(upstream, current_version)
