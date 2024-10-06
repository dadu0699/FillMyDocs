import os
import subprocess
from io import BytesIO
from tempfile import NamedTemporaryFile


async def convert_to_pdf(file_stream: BytesIO, suffix: str = ".docx"):
    """
    Convierte un archivo (docx, xlsx, etc.) a PDF utilizando LibreOffice en modo headless.
    Devuelve una tupla con el archivo BytesIO o None y un mensaje de error o None.
    """
    try:
        with NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_file.write(file_stream.read())
            temp_file.flush()
            temp_file_name = temp_file.name

        temp_pdf_name = temp_file_name.replace(suffix, '.pdf')

        try:
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
            return pdf_stream, None  # Éxito

        finally:
            if os.path.exists(temp_file_name):
                os.remove(temp_file_name)
            if os.path.exists(temp_pdf_name):
                os.remove(temp_pdf_name)

    except subprocess.CalledProcessError as exception:
        return None, str(exception)
