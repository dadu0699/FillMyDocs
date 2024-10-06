"""
Este módulo proporciona funciones para trabajar con plantillas de documentos
de Microsoft Word utilizando la biblioteca `docxtpl`. Las funciones incluyen
la interpolación de datos en plantillas y la gestión de archivos temporales.

El enfoque principal de este módulo es facilitar la generación dinámica de
documentos Word a partir de plantillas, permitiendo a los usuarios
personalizar el contenido de los documentos según sus necesidades.
"""

import os
import subprocess
from contextlib import contextmanager
from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import Union

from docxtpl import DocxTemplate
from fastapi import HTTPException

TEMPLATE_DIR = "app/templates/"
template_cache = {}


@contextmanager
def temporary_file(suffix: Union[str, None] = None):
    """
    Context manager para manejar la creación y
    eliminación de archivos temporales.
    """
    try:
        temp_file = NamedTemporaryFile(delete=False, suffix=suffix)
        yield temp_file.name
    finally:
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)


async def render_docx_template(
        template_name: str,
        context: dict,
        output_format: str = "docx"
) -> BytesIO:
    """
    Procesa un archivo .docx utilizando el contexto proporcionado
    y lo convierte a PDF si es necesario.
    """
    template_path = os.path.join(TEMPLATE_DIR, template_name)

    # Cargar la plantilla desde caché o desde disco
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
        with temporary_file(suffix=".docx") as docx_output_file_path:
            doc.render(context)
            doc.save(docx_output_file_path)

            if output_format == "pdf":
                # Convertir el archivo .docx a .pdf usando LibreOffice
                with temporary_file(suffix=".pdf") as pdf_output_file_path:
                    conversion_command = [
                        "libreoffice",
                        "--headless",
                        "--convert-to", "pdf",
                        "--outdir", os.path.dirname(pdf_output_file_path),
                        docx_output_file_path
                    ]
                    try:
                        # Ejecutar el comando de conversión
                        subprocess.run(
                            conversion_command,
                            check=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )

                        # Leer el archivo PDF generado
                        with open(pdf_output_file_path, "rb") as f:
                            pdf_content = f.read()
                            file_stream = BytesIO(pdf_content)
                            file_stream.seek(0)
                            return file_stream
                    except subprocess.CalledProcessError as e:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Error converting to PDF: {str(e)}"
                        ) from e
            else:
                # Leer el archivo DOCX generado
                with open(docx_output_file_path, "rb") as f:
                    docx_content = f.read()
                    file_stream = BytesIO(docx_content)
                    file_stream.seek(0)
                    return file_stream
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        ) from e
