import httpx
import base64
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from app.services.report_generator import generate_pdf

router = APIRouter(prefix="/report", tags=["reports"])


class ReportRequest(BaseModel):
    study: dict[str, Any]
    image_urls: dict[str, str]


@router.post("/generate")
async def generate_report(req: ReportRequest):
    # Download images as base64
    image_b64: dict[str, str] = {}
    async with httpx.AsyncClient(timeout=30) as client:
        for img_type, url in req.image_urls.items():
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    image_b64[img_type] = base64.b64encode(resp.content).decode()
            except Exception:
                pass

    pdf_bytes = generate_pdf(req.study, image_b64)
    return {"pdf_base64": base64.b64encode(pdf_bytes).decode()}
