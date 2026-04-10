"""Version information for the OMOPHub SDK."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("omophub")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"


def get_version() -> str:
    """Return the current SDK version."""
    return __version__
