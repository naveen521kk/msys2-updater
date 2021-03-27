from itertools import zip_longest
from typing import List, Tuple, Optional, Dict, Set
import requests
import hashlib
from .logger import logger
from .constants import REPO_PATH
import subprocess
import shlex
import tempfile
import textwrap
from pathlib import Path
from distutils.version import Version


def vercmp(v1: str, v2: str) -> int:
    """
    Copyright 2016-2020 Christoph Reiter
    SPDX-License-Identifier: MIT
    """

    def cmp(a: int, b: int) -> int:
        return (a > b) - (a < b)

    def split(v: str) -> Tuple[str, str, Optional[str]]:
        if "~" in v:
            e, v = v.split("~", 1)
        else:
            e, v = ("0", v)

        r: Optional[str] = None
        if "-" in v:
            v, r = v.rsplit("-", 1)
        else:
            v, r = (v, None)

        return (e, v, r)

    digit, alpha, other = range(3)

    def get_type(c: str) -> int:
        assert c
        if c.isdigit():
            return digit
        elif c.isalpha():
            return alpha
        else:
            return other

    def parse(v: str) -> List[Tuple[int, Optional[str]]]:
        parts: List[Tuple[int, Optional[str]]] = []
        seps = 0
        current = ""
        for c in v:
            if get_type(c) == other:
                if current:
                    parts.append((seps, current))
                    current = ""
                seps += 1
            else:
                if not current:
                    current += c
                else:
                    if get_type(c) == get_type(current):
                        current += c
                    else:
                        parts.append((seps, current))
                        current = c

        parts.append((seps, current or None))

        return parts

    def rpmvercmp(v1: str, v2: str) -> int:
        for (s1, p1), (s2, p2) in zip_longest(
            parse(v1), parse(v2), fillvalue=(None, None)
        ):

            if s1 is not None and s2 is not None:
                ret = cmp(s1, s2)
                if ret != 0:
                    return ret

            if p1 is None and p2 is None:
                return 0

            if p1 is None:
                if get_type(p2) == alpha:
                    return 1
                return -1
            elif p2 is None:
                if get_type(p1) == alpha:
                    return -1
                return 1

            t1 = get_type(p1)
            t2 = get_type(p2)
            if t1 != t2:
                if t1 == digit:
                    return 1
                elif t2 == digit:
                    return -1
            elif t1 == digit:
                ret = cmp(int(p1), int(p2))
                if ret != 0:
                    return ret
            elif t1 == alpha:
                ret = cmp(p1, p2)
                if ret != 0:
                    return ret

        return 0

    e1, v1, r1 = split(v1)
    e2, v2, r2 = split(v2)

    ret = rpmvercmp(e1, e2)
    if ret == 0:
        ret = rpmvercmp(v1, v2)
        if ret == 0 and r1 is not None and r2 is not None:
            ret = rpmvercmp(r1, r2)

    return ret


def version_is_newer_than(v1: str, v2: str) -> bool:
    return vercmp(v1, v2) == 1


class VersionSort(Version):
    """VersionSort, compare two version using ``>`` and ``<``
    using the previously defined version comparing functions.

    This inherits from ``distutils.version.Version``, when it is
    depreciated, compatibity code should be added.
    This uses `version_is_newer_than` to check whether the version
    passed here is newer than the other, to which comparing to.
    This is helpful when using ``list.sort(key=VersionSort)``.

    Examples
    ========

    >>> a = VersionSort("1.0.0")
    >>> b = VersionSort("2.0.0")
    >>> a > b
    False
    >>> a < b
    True
    >>> c = ['1.0.0','1.1.0','1.0.1','1.0.2','1.0.3','1.1.3','1.1.2']
    >>> c.sort(key=VersionSort)
    >>> c
    ['1.0.0', '1.0.1', '1.0.2', '1.0.3', '1.1.0', '1.1.2', '1.1.3']
    """

    def parse(self, vstring):
        self.version = vstring

    def __str__(self):
        return self.versions

    def _cmp(self, other):
        if isinstance(other, str):
            other = VersionSort(other)
        elif not isinstance(other, VersionSort):
            return NotImplemented
        if version_is_newer_than(self.version, other.version):
            return 1
        return -1


def find_checksum_from_file(fname, hashtype, info):
    path = get_repo_path(info)
    hash = hashlib.new(hashtype)
    with open(path / info["name"] / fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()


def find_checksum(url, hashtype):
    logger.info("Finding checksum for URL: %s", url)
    logger.info("Hash type: %s", hashtype)
    con = requests.get(url)
    con.raise_for_status()
    file_hash = hashlib.new(hashtype)
    file_hash.update(con.content)
    return file_hash.hexdigest()


def get_repo_path(info):
    return REPO_PATH / (info["repo"] + "-packages")


def run_command(command, cwd):
    """Runs a command using subprocess"""
    k = shlex.split(command)
    a = subprocess.Popen(
        k,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        cwd=cwd,
    )
    stdout, stderr = a.communicate()
    if stderr:
        raise Exception(stderr.decode())
    return stdout.decode()


class PKGBUILD:
    """An utility class to get Data from the
    content of ``PKGBUILD`` provided.

    Examples
    --------

    >>> a=PKGBUILD(open('./PKGBUILD').read())
    >>> a.pkgrel
    1
    >>> a.pkgver
    1.2.3
    """

    def __init__(self, content) -> None:
        self.content = content

    def __getattr__(self, var):
        att = self.get_variable_from_pkgbuild(var)
        if not att:
            raise AttributeError(f"No attribute {att} in PKGBUILD")
        else:
            return att

    def check_variable_is_array(self, variable):
        content = self.content
        base = f"#!/bin/bash\n{content}\n"
        base += f"declare -p {variable} 2> /dev/null | grep -q 'declare \-a' && echo 1 || echo 0\n"
        with tempfile.TemporaryDirectory() as tmpdirname:
            # tmpdirname = Path(".")
            with open(Path(tmpdirname) / "var.sh", "w", encoding="utf-8") as f:
                f.write(base)
            out = run_command(
                f"bash {Path(tmpdirname).as_posix()}/var.sh", cwd=tmpdirname
            )
            run_command(f"rm var.sh", cwd=tmpdirname)
        return bool(int(out))

    def get_variable_from_pkgbuild(self, variable):
        content = self.content
        base = f"#!/bin/bash\n{content}\n"
        base += f"isarray=$(declare -p {variable} 2> /dev/null | grep -q 'declare \-a' && echo true || echo false)\n"
        with tempfile.TemporaryDirectory() as tmpdirname:
            # tmpdirname = Path(".")
            tmpdirname = Path(tmpdirname)
            with open(Path(tmpdirname) / "test.sh", "w", encoding="utf-8") as f:
                f.write(
                    base
                    + f"declare -n tempvar={variable}\n"
                    + textwrap.dedent(
                        """\
                            if [ $isarray=true ]
                            then
                                for i in "${!tempvar[@]}"; do
                                    printf "${tempvar[i]}\\n"
                                done
                            else
                                printf "${variable}\\n"
                            fi
                        """
                    )
                )
            out = run_command(
                f"bash {Path(tmpdirname).as_posix()}/test.sh", cwd=tmpdirname
            )
            run_command(f"rm test.sh", cwd=tmpdirname)
            out = out[:-1]
            if self.check_variable_is_array(variable):
                out = out.split("\n")
                for i, j in enumerate(out):
                    if "::" in j:
                        out[i] = j.split("::")[1]
                return out
            return out