import textwrap
import pytest


class RegardingProjectPath:
    def __init__(self, path, meta):
        self.project_dir = path
        self.meta = meta

    def __str__(self):
        return str(self.project_dir)


@pytest.fixture()
def pyproject_toml_project_path(tmp_path):
    pyproject_toml = tmp_path / "pyproject.toml"
    pyproject_toml.write_text(textwrap.dedent("""
    [project]
    name="Cibo Matto"
    version = "6.6.6"
    authors = [{name = "Sugar Water", email = "SugarWate@cibomatto.com"}]
    description = "Test data for regarding tests"
    
    [project.urls]
    homepage = "https://github.com/nicfit/regarding"
    """))

    return RegardingProjectPath(tmp_path, pyproject_toml)


@pytest.fixture()
def null_project_path(tmp_path):
    return RegardingProjectPath(tmp_path, None)
