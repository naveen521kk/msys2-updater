import re
from enum import Enum
from pathlib import Path

PACKAGES_PATH = Path(__file__).parent.resolve().parent / "packages"
REPO_PATH = Path(__file__).parent.resolve().parent.parent
PYPI_URL_BASE = "https://pypi.org/pypi/{project_name}/{project_version}/json"
MINGW_PACKAGE_PREFIX = "mingw-w64-x86_64"


class Regex(Enum):
    checksum: re.Pattern = re.compile(
        r"(?P<type>\w*)sums=\((?P<checksum>[^\(\)]*)\)\n", re.MULTILINE
    )
    version_parse: re.Pattern = re.compile(r"pkgver=(?P<version>[\d\.\"\"]*)")
    pkgrel_parse: re.Pattern = re.compile(r"pkgrel=(?P<version>[\d\.\"\"]*)")
    dependency = re.compile(r"^depends=\((?P<checksum>[^\(\)]*)\)\n", re.MULTILINE)
