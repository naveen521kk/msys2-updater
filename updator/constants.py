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
    version_parse: re.Pattern = re.compile(r"pkgver=(?P<version>([\w\d\.\'\"])*)")
    pkgrel_parse: re.Pattern = re.compile(r"pkgrel=(?P<version>[\d\.\"\"]*)")
    dependency = re.compile(r"^depends=\((?P<checksum>[^\(\)]*)\)\n", re.MULTILINE)
    # from https://github.com/django/django/blob/stable/1.3.x/django/core/validators.py#L45
    url_check = re.compile(
        r"^(?:http|ftp)s?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
