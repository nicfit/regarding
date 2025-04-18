import toml
from pathlib import Path
from packaging import version


class ProjectMeta:
    meta_file = None

    # Universal
    _name: str = None
    _version: version.Version = None
    _description: str = None
    _author: str = None
    _author_email: str = None
    _homepage: str = None

    # Extensions
    _release_name: str = None
    _years: str = None

    @staticmethod
    def parseVersion(v: str) -> version.Version:
        # Some validation and normalization (e.g. 1.0-a1 -> 1.0a1)
        return version.parse(v)

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
    def version(self) -> version.Version:
        return self._version

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
    """pyproject meta data"""
    meta_file = "pyproject.toml"

    def __init__(self):
        project_toml = toml.loads(Path(self.meta_file).read_text())
        self._pyproject = project_toml["project"]

        self._name = self._pyproject["name"]
        self._version = self.parseVersion(self._pyproject["version"])
        self._description = self._pyproject["description"]

        urls = self._pyproject.get("urls", None)
        if urls:
            self._homepage = urls.get("homepage", None)

        author = self._pyproject["authors"][0]
        self._author = author["name"]
        self._author_email = author["email"]

        if "tool" in project_toml:
            regarding = project_toml["tool"].get("regarding", {})
            self._release_name = regarding.get("release_name", None)
            self._years = regarding.get("years", None)

    @property
    def authors(self):
        return self._pyproject["authors"]


def load() -> ProjectMeta:
    all_meta_types = (ProjectToml,)

    for MetaType in all_meta_types:
        try:
            meta = MetaType()
        except FileNotFoundError:
            continue
        else:
            return meta

    raise FileNotFoundError("Not files found: " + ", ".join([t.meta_file for t in all_meta_types]))
