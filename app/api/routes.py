from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.services.docx_service import render_docx_template

router = APIRouter()


@router.post("/generate-file")
async def generate_file(
    template_name: str,
    context: dict,
    output_format: str = "docx"
):
    """
    Endpoint para generar un archivo interpolado (DOCX o PDF)
    basado en una plantilla de Word.
    """
    file_stream = await render_docx_template(
        template_name,
        context,
        output_format
    )

    media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document" if output_format == "docx" else "application/pdf"
    return StreamingResponse(
        file_stream,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename=generated.{output_format}"
        })
