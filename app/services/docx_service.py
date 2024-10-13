"""
Este módulo proporciona funciones para trabajar con plantillas de documentos
de Microsoft Word utilizando la biblioteca `docxtpl`. Las funciones incluyen
la interpolación de datos en plantillas y la gestión de archivos temporales.
"""

from io import BytesIO
from os import path

from docxtpl import DocxTemplate

from app.services.pdf_service import convert_to_pdf

TEMPLATE_DIR = "app/templates/"
template_cache = {}


async def render_docx_template(template_name: str, context: dict, get_pdf: bool = False):
    """
    Procesa un archivo .docx utilizando el contexto proporcionado.
    Si get_pdf es True, convierte el archivo a PDF antes de devolverlo.
    Devuelve un BytesIO con el contenido del archivo (docx o pdf) y un mensaje de error o None.
    """
    template_path = path.join(TEMPLATE_DIR, template_name)

    if template_name not in template_cache:
        try:
            template_cache[template_name] = DocxTemplate(template_path)
        except FileNotFoundError:
            return None, f"Template not found: {template_name}"

    doc = template_cache[template_name]

    try:
        file_stream = BytesIO()
        doc.render(context)
        doc.save(file_stream)
        file_stream.seek(0)

        if get_pdf:
            pdf_stream, error = await convert_to_pdf(file_stream, ".docx")
            if error:
                return None, error
            return pdf_stream, None

        return file_stream, None

    except Exception as exception:
        return None, str(exception)
