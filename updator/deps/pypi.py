import requests
import typing as T
from packaging.requirements import Requirement
from pathlib import Path
import json
from ..constants import MINGW_PACKAGE_PREFIX, PYPI_URL_BASE, Regex
from ..logger import logger
from ..utils import PKGBUILD, get_repo_path
from ..handlers.handler import Handler

with open(Path(__file__).parent.resolve().parent.parent / "pymapping.json") as f:
    pymappings = json.load(f)

class PyPiDepsManager:
    def __init__(
        self,
        handler: Handler,
        info: dict,
    ):
        """
        Here ``package_name`` is the name of the package
        to query for dependencies.

        Parameters
        ----------
        handler: :class:`Handler`
            The previous PyPI update handle.
        package_name: :class:`str`
            The package name of it in MSYS2/MINGW
        info: :class:`dict`
            A copy of the json dict.
        """
        pypi_project_name = info["project"]
        pypi_project_version = handler.remote_version
        logger.info(
            "Dependency solving for %s %s", pypi_project_name, pypi_project_version
        )
        REPO_PATH = get_repo_path(info)
        self.name = info["name"]
        self.info = info
        self.filename = REPO_PATH / self.name / "PKGBUILD"
        self.dependecy_regex = Regex.dependency.value
        self.package_name = pypi_project_name
        self.url = PYPI_URL_BASE.format(
            project_name=pypi_project_name, project_version=pypi_project_version
        )
        self.vendored = info["vendored"]
        if self.vendored:
            self.vendored_deps = info["vendored_deps"]
        logger.debug("API URL: %s", self.url)
        with open(REPO_PATH / info["name"] / "PKGBUILD") as f:
            self.pkgbuild = PKGBUILD(f.read())
        if handler.update:
            self.query_pypi()
            self.check_dep_change()
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

    def query_pypi(self):
        logger.info("Querying PyPI")
        con = requests.get(self.url).json()
        deps_req = []
        if con["info"]["requires_dist"]:
            for dep in con["info"]["requires_dist"]:
                a = Requirement(dep)
                if a.marker:
                    if "extra" in str(a.marker):
                        continue
                    if a.marker.evaluate():
                        deps_req.append(a)
                else:
                    deps_req.append(a)
                logger.debug("Got dependency:%s", dep)
            self.deps = deps_req
        else:
            self.deps = []

    def check_dep_change(self):
        """Check for dependecy in the ``PKGBUILD`` file."""
        pkgbuild = self.pkgbuild
        info = self.info
        #deps_from_pypi: T.List[str] = [
        #    MINGW_PACKAGE_PREFIX + "-python-" + str(i.name).replace('-','_') for i in self.deps
        #]
        deps_from_pypi = []
        for i in self.deps:
            if i in pymappings:
                deps_from_pypi.append(pymappings[i])
            else:
                deps_from_pypi.append(MINGW_PACKAGE_PREFIX + "-python-" + str(i.name))
        
        if self.vendored:
            for i in self.vendored_deps:
                deps_from_pypi.append(MINGW_PACKAGE_PREFIX + "-python-" + i)
        deps_in_pkgbuild = pkgbuild.depends
        deps_in_pkgbuild.sort()        
        deps_from_pypi.sort()
        logger.info("Got dependency from pkgbuild: %s", deps_in_pkgbuild)
        logger.info("Got dependency from pypi: %s", deps_from_pypi)
        for i in deps_in_pkgbuild:
            if "mingw-w64-x86_64-python" not in i:
                deps_from_pypi.append(i)
        deps_from_pypi.sort()

        if MINGW_PACKAGE_PREFIX + "-python" in deps_in_pkgbuild:
            deps_in_pkgbuild.remove(MINGW_PACKAGE_PREFIX + "-python")

        if deps_in_pkgbuild == deps_from_pypi:
            logger.info("No dependency Changes")
            return
        else:
            content = self.content
            for i in range(len(deps_from_pypi)):
                deps_from_pypi[i] = deps_from_pypi[i].replace(MINGW_PACKAGE_PREFIX, r"${MINGW_PACKAGE_PREFIX}")
            #if self.deps_from_pypi==[]:
            if deps_from_pypi == []:
                deps_from_pypi.append("${MINGW_PACKAGE_PREFIX}-python")
            self.deps_from_pypi = deps_from_pypi
            regex_dependency = self.dependecy_regex
            content = regex_dependency.sub(self.dependecy_writer, content)
            self.content = content

    def dependecy_writer(self, match):
        deps = self.deps_from_pypi
        final = f'depends=("'
        indent = len(final) - 1
        for n in range(len(deps)):
            final += deps[n] + "\"" if final[-1] == "\"" else "\"" + deps[n] + "\""
            if n == len(deps) - 1:
                indent = 0
            else:
                final += "\n"
            final += " " * indent
        else:
            final += ")\n"
        return final

    def finalise_content(self):
        if hasattr(self, "_content"):
            with open(self.filename, "w") as f:
                f.write(self.content)