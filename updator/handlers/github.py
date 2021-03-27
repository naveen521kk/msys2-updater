# Copyright 2021 Naveen M K
# SPDX-License-Identifier: MIT
import os

from github import Github

from .handler import Handler
from ..utils import VersionSort

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", None)


class GithubHandler(Handler):
    def __init__(self, info) -> None:
        self.info = info
        if info["api_url"] == "":
            self.gh = Github(GITHUB_TOKEN)
        else:
            self.gh = Github(base_url=info["api_url"], login_or_token=GITHUB_TOKEN)

    @property
    def remote_version(self) -> None:
        if hasattr(self, "_remote_version"):
            return self._remote_version
        gh = self.gh
        info = self.info
        repo = gh.get_repo(info["slug"])
        versions = repo.get_tags()
        latest = versions.sort(key=VersionSort)[-1]
        version = latest.name if latest.name[0] != "v" else latest.name[1:]
        self._remote_version = version
        return version
