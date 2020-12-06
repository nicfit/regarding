try:
    from .__about__ import version as __version__
    from .__about__ import version_info as __version_info__
except ImportError:
    # During bootstrap
    __version__, __version_info__ = None, None

__all__ = ["__version__", "__version_info__"]
