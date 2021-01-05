import argparse
import json
from .logger import logger,console
from pathlib import Path
from updator.writer import Writer
import logging
from .constants import PACKAGES_PATH
from .handlers.github import GithubHandler
from .handlers.gitlab import GitlabHandler
from .handlers.pypi import PyPiHandler

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="enable debug mode")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(filename='update.log',format="%(levelname)s - %(message)s", level=logging.DEBUG)
    else:
        logging.basicConfig(filename='update.log',format="%(levelname)s - %(message)s", level=logging.INFO)
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
            try:
                logger.info("Checking %s",info['name'])
                a = PyPiHandler(info)
                Writer(info, a)
            except Exception as e:
                console.print_exception()
                logging.error(e)