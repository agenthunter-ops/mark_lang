"""Mark Lang - creative brief processing toolkit."""
from importlib.metadata import version, PackageNotFoundError

try:  # pragma: no cover
    __version__ = version("mark-lang")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = ["__version__"]
