"""
Este módulo proporciona funciones para trabajar con plantillas de documentos
de Microsoft Word utilizando la biblioteca `docxtpl`. Las funciones incluyen
la interpolación de datos en plantillas y la gestión de archivos temporales.
"""

import os
from io import BytesIO

from docxtpl import DocxTemplate
from app.utils.file_utils import temporary_file

TEMPLATE_DIR = "app/templates/"
template_cache = {}


async def render_docx_template(template_name: str, context: dict):
    """
    Procesa un archivo .docx utilizando el contexto proporcionado.
    Devuelve una tupla con el archivo BytesIO o None y un mensaje de error o None.
    """
    template_path = os.path.join(TEMPLATE_DIR, template_name)

    if template_name not in template_cache:
        try:
            template_cache[template_name] = DocxTemplate(template_path)
        except FileNotFoundError:
            return None, f"Template not found: {template_name}"

    doc = template_cache[template_name]

    try:
        with temporary_file(suffix=".docx") as output_file_path:
            doc.render(context)
            doc.save(output_file_path)

            with open(output_file_path, "rb") as f:
                docx_content = f.read()

            file_stream = BytesIO(docx_content)
            file_stream.seek(0)
            return file_stream, None

    except Exception as exception:
        return None, str(exception)
