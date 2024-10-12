import os
import subprocess
from io import BytesIO

from app.utils.file_utils import temporary_file


async def convert_to_pdf(file_stream: BytesIO, suffix: str = ".docx"):
    """
    Convierte un archivo (docx, xlsx, etc.) a PDF utilizando LibreOffice en modo headless.
    Devuelve un BytesIO con el contenido PDF.
    """
    try:
        with temporary_file(suffix=suffix) as temp_file_name:
            with open(temp_file_name, "wb") as temp_file:
                temp_file.write(file_stream.read())
                temp_file.flush()

            temp_pdf_name = temp_file_name.replace(suffix, '.pdf')

            subprocess.run(
                [
                    "libreoffice",
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", os.path.dirname(temp_pdf_name),
                    temp_file_name
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )

            with open(temp_pdf_name, "rb") as f:
                pdf_content = f.read()

            if not pdf_content:
                return None, "PDF content is empty."

            pdf_stream = BytesIO(pdf_content)
            pdf_stream.seek(0)

            return pdf_stream, None

    except subprocess.CalledProcessError as exception:
        return None, str(exception)

    finally:
        if os.path.exists(temp_file_name):
            os.remove(temp_file_name)
        if os.path.exists(temp_pdf_name):
            os.remove(temp_pdf_name)
