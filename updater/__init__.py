import argparse
import json
import logging
from pathlib import Path

from .constants import PACKAGES_PATH
from .deps.pypi import PyPiDepsManager
from .handlers.github import GithubHandler
from .handlers.gitlab import GitlabHandler
from .handlers.pypi import PyPiHandler
from .logger import console, logger
from .writer import Writer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug",
        action="store_true",
        help="enable debug mode",
    )
    args = parser.parse_args()

    if args.debug:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO
    logging.basicConfig(
        filename="update.log",
        format="%(levelname)s - %(message)s",
        level=logging_level,
    )
    for file in Path(PACKAGES_PATH).glob("*.json"):
        with open(file) as f:
            info = json.load(f)
        try:
            if info["type"] == "pypi":
                logger.info("Checking %s method PyPi", info["name"])
                a = PyPiHandler(info)
                info["version"] = a.remote_version
                with open(file, "w") as f:
                    json.dump(info, f, indent=4)
                Writer(info, a)
                with open(file) as f:
                    info = json.load(f)
                # check for dependency changes now
                PyPiDepsManager(a, info)
            elif info["type"] == "github":
                logger.info("Checking %s method Github", info["name"])
                a = GithubHandler(info)
                info["version"] = a.remote_version
                with open(file, "w") as f:
                    json.dump(info, f, indent=4)
                Writer(info, a)
            elif info["type"] == "gitlab":
                logger.info("Checking %s method Gitlab", info["name"])
                a = GitlabHandler(info)
                info["version"] = a.remote_version
                with open(file, "w") as f:
                    json.dump(info, f, indent=4)
                Writer(info, a)
            else:
                logger.error("Unknown handle %s", info["type"])
                logger.error(info)
        except Exception as e:
            console.print_exception()
            logging.error(e)
