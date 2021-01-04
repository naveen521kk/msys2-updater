import argparse
import json
import logging
from pathlib import Path
from updator.writer import Writer

from .constants import PACKAGES_PATH
from .handlers.github import GithubHandler
from .handlers.gitlab import GitlabHandler
from .handlers.pypi import PyPiHandler
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="enable debug mode")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(format="%(levelname)s - %(message)s", level=logging.DEBUG)
    else:
        logging.basicConfig(format="%(levelname)s - %(message)s", level=logging.INFO)
    for file in Path(PACKAGES_PATH).glob("*.json"):
        # with open(file) as f:
        #     info = json.load(f)
        # if info["type"] == "github":
        #     a = GithubHandler(info)
        #     Writer(info,a)
        # elif info["type"] == "gitlab":
        #     a = GitlabHandler(info)
        #     Writer(info,a)
        # elif info["type"] == "pypi":
        #     a = PyPiHandler(info)
        #     Writer(info,a)
        with open(file) as f:
            info = json.load(f)
        if info["type"] == "pypi":
            a = PyPiHandler(info)
            Writer(info,a)