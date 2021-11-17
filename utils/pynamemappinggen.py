# run from the root of updater repo.
# pass the repo path

import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.append(str(Path(__file__).parent.resolve().parent))
import argparse
import json

from updater.constants import MINGW_PACKAGE_PREFIX
from updater.utils import PKGBUILD

final = {}


def add_things(path: Path, final: dict):
    if path.is_dir():
        if "mingw-w64-python-" in path.stem:
            print(path.absolute())
            with open(path / "PKGBUILD", encoding="utf-8") as f:
                pkgbuild = PKGBUILD(f.read())
            realname = pkgbuild._realname
            try:
                pyname = pkgbuild._pyname
            except:
                pyname = None
            pkgbase = pkgbuild.pkgbase
            if pyname:
                if "mingw-w64-python-" + pyname != pkgbase:
                    final[pyname] = pkgbase.replace("mingw-w64", MINGW_PACKAGE_PREFIX)
            else:
                if "mingw-w64-python-" + realname != pkgbase:
                    final[realname] = pkgbase.replace("mingw-w64", MINGW_PACKAGE_PREFIX)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate pynamemapping json.")
    parser.add_argument("repo", type=str, help="path to the repo")

    args = parser.parse_args()
    repo_path = args.repo
    print(Path(repo_path).resolve().absolute())
    with ThreadPoolExecutor() as executor:
        for path in Path(repo_path).iterdir():
            executor.submit(add_things,path,final)
        # final_list.append({"realname": realname, "pkgbase": pkgbase})
    final["PrettyTable"] = MINGW_PACKAGE_PREFIX + "-python-prettytable"
    final["jinja2"] = MINGW_PACKAGE_PREFIX + "-python-jinja"
    with open(
        Path(__file__).parent.resolve().parent / "pymapping.json", "w", encoding="utf-8"
    ) as f:
        json.dump(final, f)
    print(json.dumps(final, indent=4))
