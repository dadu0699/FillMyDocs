import os
from contextlib import contextmanager
from tempfile import NamedTemporaryFile


@contextmanager
def temporary_file(suffix: str | None = None):
    """
    Context manager para manejar la creación y eliminación de archivos temporales.
    """
    try:
        temp_file = NamedTemporaryFile(delete=False, suffix=suffix)
        yield temp_file.name
    finally:
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
