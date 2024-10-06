from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.services.docx_service import render_docx_template
from app.services.pdf_service import convert_to_pdf

router = APIRouter()


@router.post("/generate-file")
async def generate_file(
    template_name: str,
    context: dict,
    file_format: str = "docx",
):
    """
    Endpoint para generar un archivo interpolado (DOCX o PDF)
    basado en una plantilla de Word.
    """
    if file_format not in ["docx", "pdf"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Use 'docx' or 'pdf'."
        )

    file_stream, error = await render_docx_template(template_name, context)
    if error or not file_stream:
        raise HTTPException(status_code=500, detail=error)

    if file_format == "pdf":
        pdf_stream, error = await convert_to_pdf(file_stream, ".docx")
        if error or not pdf_stream:
            # Maneja el error
            raise HTTPException(status_code=500, detail=error)

        pdf_stream.seek(0)
        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=interpolated_document.pdf",
                "Content-Length": str(pdf_stream.getbuffer().nbytes)
            }
        )

    file_stream.seek(0)
    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": "attachment; filename=interpolated_document.docx",
            "Content-Length": str(file_stream.getbuffer().nbytes)
        }
    )
