# run from the root of updator repo.
# pass the repo path

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.resolve().parent))
import argparse
import json
from updator.constants import MINGW_PACKAGE_PREFIX
from updator.utils import PKGBUILD
final = {}
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate pynamemapping json.")
    parser.add_argument("repo", type=str, help="path to the repo")

    args = parser.parse_args()
    repo_path = args.repo
    print(Path(repo_path).resolve().absolute())
    for path in Path(repo_path).iterdir():
        if path.is_dir():
            if "mingw-w64-python-" in path.stem:
                # print(path.absolute())
                with open(path / "PKGBUILD", encoding="utf-8") as f:
                    pkgbuild = PKGBUILD(f.read())
                realname = pkgbuild._realname
                pkgbase = pkgbuild.pkgbase
                if "mingw-w64-python-" + realname != pkgbase:
                    final[realname] = pkgbase.replace("mingw-w64",MINGW_PACKAGE_PREFIX)
                    #final_list.append({"realname": realname, "pkgbase": pkgbase})
    with open(Path(__file__).parent.resolve() / "pymapping.json") as f:
        json.dump(final,f)
    print(json.dumps(final,indent=4))