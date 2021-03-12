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
from .deps.pypi import PyPiDepsManager
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="enable debug mode")
    args = parser.parse_args()


    logging.basicConfig(filename='update.log',format="%(levelname)s - %(message)s", level=logging.DEBUG)
    for file in Path(PACKAGES_PATH).glob("*.json"):
        with open(file) as f:
            info = json.load(f)
        try:
            if info["type"] == "pypi":
                logger.info("Checking %s method PyPi",info['name'])
                a = PyPiHandler(info)
                info["version"] = a.remote_version
                with open(file,'w') as f:
                    json.dump(info,f,indent=4)
                Writer(info, a)
                with open(file) as f:
                    info = json.load(f)
                # check for dependency changes now
                PyPiDepsManager(a,info)
            elif info["type"] == "github":
                logger.info("Checking %s method Github",info['name'])
                a = GithubHandler(info)
                info["version"] = a.remote_version
                with open(file,'w') as f:
                    json.dump(info,f,indent=4)
                Writer(info,a)
            elif info["type"] == "gitlab":
                logger.info("Checking %s method Gitlab",info['name'])
                a = GitlabHandler(info)
                info["version"] = a.remote_version
                with open(file,'w') as f:
                    json.dump(info,f,indent=4)
                Writer(info,a)
        except Exception as e:
            console.print_exception()
            logging.error(e)
