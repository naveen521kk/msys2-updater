# Copyriglt 2021 Naveen M K
# SPDX-License-Identifier: MIT
import os

from gitlab import Gitlab

from .handler import Handler
from ..utils import VersionSort

GITLAB_TOKEN = os.getenv("GITLAB_TOKEN", None)


class GitlabHandler(Handler):
    def __init__(self, info) -> None:
        self.info = info
        if info["api_url"] == "":
            self.gl = Gitlab("https://gitlab.com", private_token=GITLAB_TOKEN)
        else:
            self.gl = Gitlab(info["api_url"])

    @property
    def remote_version(self) -> None:
        if hasattr(self, "_remote_version"):
            return self._remote_version
        gl = self.gl
        info = self.info
        repo = gl.projects.get(info["id"])
        versions = repo.get_tags()
        latest = versions.sort(key=VersionSort)[-1]
        version = latest.name if latest.name[0] != "v" else latest.name[1:]
        self._remote_version = version
        return version
