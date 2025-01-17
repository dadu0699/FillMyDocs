from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.services.docx_service import render_docx_template
from app.services.excel_service import render_xlsx_template

router = APIRouter()


@router.post("/docx/generate-file")
async def generate_docx_file(
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

    get_pdf = file_format == "pdf"
    file_stream, error = await render_docx_template(template_name, context, get_pdf=get_pdf)

    if error or not file_stream:
        raise HTTPException(status_code=500, detail=error)

    media_type = "application/pdf" if get_pdf else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    file_extension = "pdf" if get_pdf else "docx"

    return StreamingResponse(
        file_stream,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename=interpolated_document.{file_extension}",
            "Content-Length": str(file_stream.getbuffer().nbytes)
        }
    )


@router.post("/xlsx/generate-file")
async def generate_xlsx_file(
    template_name: str,
    context: dict,
    file_format: str = "xlsx",
):
    """
    Endpoint para generar un archivo interpolado (XLSX o PDF)
    basado en una plantilla de Excel.
    """
    if file_format not in ["xlsx", "pdf"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Use 'xlsx' or 'pdf'."
        )

    get_pdf = file_format == "pdf"
    file_stream, error = await render_xlsx_template(template_name, context, get_pdf=get_pdf)

    if error or not file_stream:
        raise HTTPException(status_code=500, detail=error)

    media_type = "application/pdf" if get_pdf else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    file_extension = "pdf" if get_pdf else "xlsx"

    return StreamingResponse(
        file_stream,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename=interpolated_document.{file_extension}",
            "Content-Length": str(file_stream.getbuffer().nbytes)
        }
    )
