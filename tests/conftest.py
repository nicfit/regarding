import textwrap
import pytest


class RegardingProjectPath:
    def __init__(self, path, meta):
        self.project_dir = path
        self.meta = meta

    def __str__(self):
        return str(self.project_dir)


@pytest.fixture()
def setup_py_project_path(tmp_path):
    setup_py = tmp_path / "setup.py"
    setup_py.write_text(textwrap.dedent("""
    import setuptools
    setuptools.setup(
        name="Cibo Matto",
        version="6.6.6",
        author="Sugar Water",
        author_email="SugarWate@cibomatto.com",
        description="Test data for regarding tests",
        long_description="TEST DATA FOR REGARDING TESTS",
        url="https://github.com/nicfit/regarding",
    ) 
    """))

    return RegardingProjectPath(tmp_path, setup_py)


@pytest.fixture()
def pyproject_toml_project_path(tmp_path):
    pyproject_toml = tmp_path / "pyproject.toml"
    pyproject_toml.write_text(textwrap.dedent("""
    [tool.poetry]
    name="Cibo Matto"
    version = "6.6.6"
    authors = ["Sugar Water <SugarWate@cibomatto.com>"]
    homepage = "https://github.com/nicfit/regarding"
    description = "Test data for regarding tests"
    """))

    return RegardingProjectPath(tmp_path, pyproject_toml)


@pytest.fixture()
def null_project_path(tmp_path):
    return RegardingProjectPath(tmp_path, None)
