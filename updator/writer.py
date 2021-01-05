from .constants import Regex
from .handlers.handler import Handler
from .logger import logger
import re
import subprocess
import shlex
import textwrap
import tempfile
from pathlib import Path
from .utils import find_checksum,get_repo_path


def run_command(command, cwd):
    # """bash -c 'dsdas=hi kqw=pol && echo "${dsdas}${kqw}"'"""
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


class Writer:
    def __init__(self, info, handler: Handler) -> None:
        self.name = info["name"]
        REPO_PATH = get_repo_path(info)
        self.filename = REPO_PATH / self.name / "PKGBUILD"
        self.checksum_regex: re.Pattern = Regex.checksum.value
        self.handler = handler
        if handler.update:
            self.write_version()
            self.write_checksum()
            self.finalise_content()

    @property
    def content(self):
        if hasattr(self, "_content"):
            return self._content
        with open(self.filename) as f:
            self._content = f.read()
            return self._content

    @content.setter
    def content(self, content):
        self._content = content

    # version writer begins
    def version_writer(self, match):
        return f"pkgver={self.handler.remote_version}"

    def pkgrel_writer(self, match):
        return f"pkgrel=1"

    def write_version(self):
        content = self.content
        handler = self.handler
        latest_version = handler.remote_version
        prev_version = handler.current_version
        regex_version = Regex.version_parse.value
        regex_pkg_rel = Regex.pkgrel_parse.value
        logger.info(
            "Updating %s from %s to %s",
            self.name,
            prev_version,
            latest_version,
        )
        content = regex_version.sub(self.version_writer, content, count=1)
        content = regex_pkg_rel.sub(self.pkgrel_writer, content, count=1)
        self.content = content

    # version writer ends

    # checksum writer begins
    @property
    def checksum_url(self):
        content = self.content
        base = f"#!/bin/bash\n{content}"
        with tempfile.TemporaryDirectory() as tmpdirname:
            with open(Path(tmpdirname) / "test.sh", "w") as f:
                f.write(
                    base
                    + textwrap.dedent(
                        """\
                        for i in "${!source[@]}"; do
                            printf "${source[i]}"
                        done
                        """
                    )
                )
            out = run_command(
                f"bash {Path(tmpdirname).as_posix()}/test.sh", cwd=tmpdirname
            )
            out = out.split("\n")
            if len(out) == 1:
                if "::" in out[0]:
                    out = out[0].split("::")[1]
                else:
                    out=out[0]
            for i, j in enumerate(out):
                if "::" in j:
                    out[i] = j.split("::")[1]
            run_command(f"rm test.sh", cwd=tmpdirname)
        return out

    @property
    def checksum(self):
        url = self.checksum_url
        regex = self.checksum_regex
        ctype = regex.search(self.content).group("type")
        return find_checksum(url, ctype)

    def checksum_writer(self, match):
        return f"{match.group('type')}sums=('{self.checksum}')\n"

    def write_checksum(self):
        content = self.content
        checksum = self.checksum
        logger.info("Updating checksum of %s", self.name)
        regex_checksum = self.checksum_regex
        content = regex_checksum.sub(self.checksum_writer, content, count=1)
        self.content = content

    def finalise_content(self):
        with open(self.filename, "w") as f:
            f.write(self.content)
