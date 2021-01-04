import re
from pathlib import Path
from enum import Enum

PACKAGES_PATH = Path(__file__).parent.resolve().parent / "packages"
REPO_PATH=Path(__file__).parent.resolve().parent.parent / "repos"
class Regex(Enum):
    checksum:re.Pattern = re.compile(r"(?P<type>\w*)sums=\((?P<checksum>[^\(\)]*)\)\n",re.MULTILINE)
    version_parse:re.Pattern = re.compile(r"pkgver=(?P<version>[\d\.\"\"]*)")
    pkgrel_parse:re.Pattern = re.compile(r"pkgrel=(?P<version>[\d\.\"\"]*)")

