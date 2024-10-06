"""
Este módulo proporciona funciones para trabajar con plantillas de documentos
de Microsoft Word utilizando la biblioteca `docxtpl`. Las funciones incluyen
la interpolación de datos en plantillas y la gestión de archivos temporales.
"""

import os
from contextlib import contextmanager
from io import BytesIO
from tempfile import NamedTemporaryFile

from docxtpl import DocxTemplate
from fastapi import HTTPException

TEMPLATE_DIR = "app/templates/"
template_cache = {}


@contextmanager
def temporary_file(suffix: str | None = None):
    """
    Context manager para manejar la creación y
    eliminación de archivos temporales.
    """
    try:
        # Crear un archivo temporal
        temp_file = NamedTemporaryFile(delete=False, suffix=suffix)
        yield temp_file.name  # Pasar la ruta del archivo temporal
    finally:
        # Eliminar el archivo temporal si existe
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)


async def render_docx_template(template_name: str, context: dict) -> BytesIO:
    """
    Procesa un archivo .docx utilizando el contexto proporcionado.
    """
    template_path = os.path.join(TEMPLATE_DIR, template_name)

    if template_name not in template_cache:
        try:
            template_cache[template_name] = DocxTemplate(template_path)
        except FileNotFoundError as file_not_found_error:
            raise HTTPException(
                status_code=404,
                detail=f"Template not found: {template_name}"
            ) from file_not_found_error

    doc = template_cache[template_name]

    try:
        with temporary_file(suffix=".docx") as output_file_path:
            doc.render(context)
            doc.save(output_file_path)

            with open(output_file_path, "rb") as f:
                content = f.read()
                file_stream = BytesIO(content)
                file_stream.seek(0)
                return file_stream
    except Exception as exception:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(exception)}"
        ) from exception
