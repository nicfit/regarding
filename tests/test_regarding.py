import os
import sys
import tempfile
import subprocess
import pytest

from io import StringIO
from pathlib import Path
from regarding.__main__ import main
from regarding.meta import ProjectMeta, SetupPy, ProjectToml

TOP_D = Path(__file__).parent.parent
tempdir = tempfile.mkdtemp()


def regardingMain(args: list):

    orig_stdout, orig_stderr = sys.stdout, sys.stderr
    stdout, stderr = StringIO(), StringIO()

    try:
        sys.stdout = stdout if stdout else orig_stdout
        sys.stderr = stderr if stdout else orig_stderr

        status = main(args)
    except SystemExit as sys_exit:
        status = sys_exit.code
    finally:
        sys.stdout = orig_stdout
        sys.stderr = orig_stderr

    return status, stdout, stderr


def test_module_version():
    from regarding import __version__, __version_info__
    from regarding.__about__ import version, version_info, project_name

    assert bool(__version__)
    assert bool(__version_info__)
    assert __version__ == version
    assert __version_info__ == version_info

    status, stdout, _ = regardingMain(["--version"])
    assert status == 0
    assert stdout.getvalue() == f"{project_name} {version}\n"


def test_module_all():
    from regarding.__about__ import project_name, author, author_email, years, description, homepage
    assert project_name == "regarding"
    assert author == "Travis Shirk"
    assert author_email == "travis@pobox.com"
    assert years is not None
    assert description is not None
    assert homepage is not None


def test_cmdline():
    os.chdir(TOP_D)

    status, *_ = regardingMain([])
    assert status == 0

    status, *_ = regardingMain(["--help"])
    assert status == 0

    status, *_ = regardingMain(["--dead-milkmen"])
    assert status != 0


def test_cmdline_default_output(tmp_path):
    os.chdir(TOP_D)

    out1 = tmp_path / "out1.py"
    proc = subprocess.run(f"regarding -o {out1}", shell=True)
    assert proc.returncode == 0
    out1_text = out1.read_text()
    assert len(out1_text) != 0

    out2 = tmp_path / "out2.py"
    proc = subprocess.run(f"regarding --out-file {out2}", shell=True)
    assert proc.returncode == 0
    out2_text = out2.read_text()
    assert out2_text == out1_text


def test_meta_parseVersion():
    vstr, version = ProjectMeta.parseVersion("0.0.0")
    assert vstr == "0.0.0"
    assert version == (0, 0, 0, "final", None, None)

    vstr, version = ProjectMeta.parseVersion("1.22.333")
    assert vstr == "1.22.333"
    assert version == (1, 22, 333, "final", None, None)


def test_meta_parseVersion_prereleases():
    for prel in ("-alpha45", "a45"):
        vstr, version = ProjectMeta.parseVersion(f"1.22.333{prel}")
        assert vstr == "1.22.333a45"
        assert version == (1, 22, 333, "a45", None, None)

    for prel in ("-beta", "b"):
        vstr, version = ProjectMeta.parseVersion(f"1.22.333{prel}")
        assert vstr == "1.22.333b0"
        assert version == (1, 22, 333, "b0", None, None)

    for prel in ("rc1",):
        vstr, version = ProjectMeta.parseVersion(f"1.22.333{prel}")
        assert vstr == "1.22.333rc1"
        assert version == (1, 22, 333, "rc1", None, None)


def test_meta_parseVersion_postreleases():
    vstr, version = ProjectMeta.parseVersion(f"1.0.0.post5")
    assert vstr == "1.0.0.post5"
    assert version == (1, 0, 0, "final", 5, None)

    vstr, version = ProjectMeta.parseVersion(f"1.0.0b4.post9")
    assert version == (1, 0, 0, "b4", 9, None)


def test_meta_parseVersion_devreleases():
    vstr, version = ProjectMeta.parseVersion(f"1.0.0.dev")
    assert vstr == "1.0.0.dev0"
    assert version == (1, 0, 0, "final", None, 0)

    vstr, version = ProjectMeta.parseVersion(f"1.0.0b4.dev9")
    assert vstr == "1.0.0b4.dev9"
    assert version == (1, 0, 0, "b4", None, 9)


def test_meta_parseVersion_invalid():
    with pytest.raises(ValueError):
        ProjectMeta.parseVersion(f"Godflesh")
    ...


def test_setuppy_meta(setup_py_project_path):
    os.chdir(str(setup_py_project_path))
    project = SetupPy()
    _assertProjectMeta(project)

    # FIXME: add tests for the extensions via setup.cfg


def test_pyprojecttoml_meta(pyproject_toml_project_path):
    os.chdir(str(pyproject_toml_project_path))
    project = ProjectToml()
    _assertProjectMeta(project)

    # FIXME: add tests for the extensions


def _assertProjectMeta(proj: ProjectMeta):
    assert proj.version == "6.6.6"
    assert proj.name == "Cibo Matto"
    assert proj.author == "Sugar Water"
    assert proj.author_email == "SugarWate@cibomatto.com"
    assert proj.description == "Test data for regarding tests"
    # FIXME: Not yet supported
    #assert proj.long_description == "TEST DATA FOR REGARDING TESTS"
    assert proj.homepage == "https://github.com/nicfit/regarding"

    assert proj.years is None
    assert proj.release_name is None


def test_null_meta(null_project_path):
    cwd = os.getcwd()
    try:
        os.chdir(null_project_path.project_dir)
        status = regardingMain([])
        assert status != 0
    finally:
        os.chdir(cwd)
