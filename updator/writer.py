import re
import tempfile
import textwrap
import typing as T
from pathlib import Path

from .constants import Regex
from .handlers.handler import Handler
from .logger import logger
from .utils import find_checksum, get_repo_path, run_command


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
    def content(self) -> str:
        if hasattr(self, "_content"):
            return self._content
        with open(self.filename) as f:
            self._content = f.read()
            return self._content

    @content.setter
    def content(self, content):
        self._content = content

    # version writer begins
    def version_writer(self, match) -> str:
        return f"pkgver={self.handler.remote_version}"

    def pkgrel_writer(self, match) -> str:
        return f"pkgrel=1"

    def write_version(self) -> None:
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
        if hasattr(self, "_checksum_url"):
            return self._checksum_url
        content = self.content
        base = f"#!/bin/bash\n{content}"
        with tempfile.TemporaryDirectory() as tmpdirname:
            with open(Path(tmpdirname) / "test.sh", "w") as f:
                f.write(
                    base
                    + textwrap.dedent(
                        """\
                        for i in "${!source[@]}"; do
                            printf "${source[i]}\n"
                        done
                        """
                    )
                )
            out = run_command(
                f"bash {Path(tmpdirname).as_posix()}/test.sh", cwd=tmpdirname
            )
            out = out.split("\n")[:-1]
            if len(out) == 1:
                if "::" in out[0]:
                    out = out[0].split("::")[1]
                else:
                    out = out[0]
            for i, j in enumerate(out):
                if "::" in j:
                    out[i] = j.split("::")[1]
            run_command(f"rm test.sh", cwd=tmpdirname)
        self._checksum_url = out
        return out

    @property
    def checksum(self) -> T.Dict[str, str]:
        if hasattr(self, "_checksum"):
            return self._checksum
        urls = self.checksum_url
        regex = self.checksum_regex
        ctype = regex.search(self.content).group("type")
        if not isinstance(urls, list):
            self._checksum = [{urls: find_checksum(urls, ctype)}]
            return self._checksum
        checksums = {}
        for n in range(len(urls)):
            if urls[n][-4:] == ".sig":
                checksums[urls[n]] = None
                continue
            checksums[urls[n]] = find_checksum(urls[n], ctype)
        self._checksum = checksums
        return self._checksum

    def checksum_writer(self, match):
        checksum = self.checksum
        checksum_url = self.checksum_url
        if len(checksum_url) == 1:
            return f"{match.group('type')}sums=('{self.checksum}')\n"
        elif len(checksum_url) > 1:
            final = f"{match.group('type')}sums=('"
            indent = len(final) - 1
            logger.info(checksum_url)
            logger.info(checksum)
            for n, i in enumerate(checksum_url):
                if n == len(checksum_url) - 1:
                    indent = 0
                if checksum[i] is not None:
                    final += (
                        checksum[i] + "'\n"
                        if final[-1] == "'"
                        else "'" + checksum[i] + "'\n"
                    )
                    final += " " * indent
                else:
                    final += "SKIP'\n" if final[-1] == "'" else "'SKIP'\n"
                    final += " " * indent
            else:
                final += ")\n"
            return final
        else:
            ValueError("How can I consider that there is not checksum for a package?")

    def write_checksum(self):
        content = self.content
        checksum = self.checksum
        logger.info("Updating checksum of %s", self.name)
        regex_checksum = self.checksum_regex
        content = regex_checksum.sub(self.checksum_writer, content)
        self.content = content

    def finalise_content(self):
        with open(self.filename, "w") as f:
            f.write(self.content)
