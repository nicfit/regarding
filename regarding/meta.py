import toml
from pathlib import Path
from subprocess import run
from collections import namedtuple
from configparser import ConfigParser


class ProjectMeta:
    meta_file = None

    # Universal
    _name = None
    _version, _version_info = None, None
    _description = None
    _author, _author_email = None, None
    _homepage = None

    # Extensions
    _release_name = None
    _years = None

    @staticmethod
    def parseVersion(v):
        from pkg_resources import parse_version
        from pkg_resources.extern.packaging.version import Version

        # Some validation and normalization (e.g. 1.0-a1 -> 1.0a1)
        V = parse_version(v)
        if not isinstance(V, Version):
            raise ValueError(f"Invalid version: {v}")

        ver = str(V)
        if V._version.pre:
            rel = "".join([str(v) for v in V._version.pre])
        else:
            rel = "final"

        # Although parsed the following components are not captured: post, dev, local, epoch
        Version = namedtuple("Version", "major, minor, maint, release")
        ver_info = Version(V._version.release[0],
                           V._version.release[1] if len(V._version.release) > 1 else 0,
                           V._version.release[2] if len(V._version.release) > 2 else 0,
                           rel)
        return ver, ver_info

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def author(self):
        return self._author

    @property
    def author_email(self):
        return self._author_email

    @property
    def version(self):
        return self._version

    @property
    def version_info(self):
        return self._version_info

    @property
    def homepage(self):
        return self._homepage

    @property
    def release_name(self):
        return self._release_name

    @property
    def years(self):
        return self._years


class ProjectToml(ProjectMeta):
    """Poetry meta data"""
    meta_file = "pyproject.toml"

    def __init__(self):
        project_toml = toml.loads(Path(self.meta_file).read_text())
        self._poetry = project_toml["tool"]["poetry"]

        self._name = self._poetry["name"]
        self._version, self._version_info = self.parseVersion(self._poetry["version"])
        self._description = self._poetry["description"]
        self._homepage = self._poetry.get("homepage", "")

        author = self._poetry["authors"][0]
        self._author = author[:author.find("<")].strip()
        self._author_email = author[author.find("<") + 1:author.find(">")].strip()

        regarding = project_toml["tool"].get("regarding", {})
        self._release_name = regarding.get("release_name", "")
        self._years = regarding.get("years", "")

    @property
    def authors(self):
        return self._poetry["authors"]


class SetupPy(ProjectMeta):
    """Setup.py meta data"""
    meta_file = "setup.py"

    def __init__(self):
        self._setup_py = Path(self.meta_file)
        if not self._setup_py.exists():
            raise FileNotFoundError(f"File not found: {self.meta_file}")

        # XXX: yes, a setuptools loaded setup.py faster, and should be used if available
        self._name = self._run("--name")
        self._version, self._version_info = self.parseVersion(self._run("--version"))
        self._description = self._run("--description")
        self._homepage = self._run("--url")
        self._author = self._run("--author")
        self._author_email = self._run("--author-email")

        setup_cfg = Path("setup.cfg")
        if setup_cfg.exists():
            section = "tool:regarding"

            cfg = ConfigParser()
            cfg.read(str(setup_cfg))
            if cfg.has_section(section):
                self._release_name = cfg.get(section, "release_name", fallback=None)
                self._years = cfg.get(section, "years", fallback=None)

    def _run(self, option):
        proc = run(f"python {self._setup_py} {option}",
                   capture_output=True, check=True, shell=True, encoding="utf8")
        return proc.stdout.strip()


def load() -> ProjectMeta:
    all_meta_types = (ProjectToml, SetupPy)

    for MetaType in all_meta_types:
        try:
            meta = MetaType()
        except FileNotFoundError:
            continue
        else:
            return meta

    raise FileNotFoundError("Not files found: " + ", ".join([t.meta_file for t in all_meta_types]))
