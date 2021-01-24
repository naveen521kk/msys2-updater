import re
import typing as T
import json
from .constants import Regex, PACKAGES_PATH
from .handlers.handler import Handler
from .logger import logger
from .utils import PKGBUILD, find_checksum, get_repo_path, find_checksum_from_file


class Writer:
    def __init__(self, info, handler: Handler) -> None:
        self.name = info["name"]
        self.info = info
        REPO_PATH = get_repo_path(info)
        self.filename = REPO_PATH / self.name / "PKGBUILD"
        self.checksum_regex: re.Pattern = Regex.checksum.value
        self.handler = handler
        if handler.update:
            self.write_version()
            self.write_checksum()
            self.finalise_content()
            self.write_update()

    def write_update(self):
        self.info["update"] = True
        with open(PACKAGES_PATH / (self.info["name"] + ".json"), "w") as f:
            json.dump(self.info, f, indent=4)

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
        base = PKGBUILD(self.content)
        self._checksum_url = base.source
        return self._checksum_url

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
            if urls[n][-6:] == ".patch":
                checksums[urls[n]] = find_checksum_from_file(urls[n], ctype,self.info)
                continue
            checksums[urls[n]] = find_checksum(urls[n], ctype)
        self._checksum = checksums
        return self._checksum

    def checksum_writer(self, match):
        checksum = self.checksum
        checksum_url = self.checksum_url
        if len(checksum_url) == 1:
            return f"{match.group('type')}sums=('{self.checksum[checksum_url[0]]}')\n"
        elif len(checksum_url) > 1:
            final = f"{match.group('type')}sums=('"
            indent = len(final) - 1
            for n, i in enumerate(checksum_url):
                if checksum[i] is not None:
                    final += (
                        checksum[i] + "'"
                        if final[-1] == "'"
                        else "'" + checksum[i] + "'"
                    )
                else:
                    final += "SKIP'" if final[-1] == "'" else "'SKIP'"
                if n == len(checksum_url) - 1:
                    indent = 0
                else:
                    final+="\n"
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
