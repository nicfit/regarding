from regarding import __version__, __version_info__


def test_version():
    assert bool(__version__)
    assert bool(__version_info__)
    print(__version__)
    print(__version_info__)
    # FIXME: more tests
