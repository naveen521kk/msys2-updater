import json
import os

from github import Github

from .handler import Handler

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN",None)


class GithubHandler(Handler):
    def __init__(self, info) -> None:
        self.info = info
        self.gh = Github(GITHUB_TOKEN)
        self.get_remote_version()

    def get_remote_version(self) -> None:
        gh=self.gh
        info=self.info
        repo = gh.get_repo(info['slug'])
        latest = repo.get_tags()[0]
        self.remote_version = latest.name

