from datetime import date, datetime, time
from io import BytesIO
from typing import Optional

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.SymptomEntry import SymptomEntry
from app.services.database import get_db
from app.services.function import generate_symptoms_pdf

router = APIRouter(prefix="/api/generation",
                   tags=["generation"])


@router.get("/pdf")
async def generate_pdf_report(
    start_date: Optional[date] = Query(None, description="Start date in YYYY-MM-DD"),
    end_date: Optional[date] = Query(None, description="End date in YYYY-MM-DD. Defaults to today."),
    user_id: Optional[int] = Query(None, description="Optional user id filter"),
    db: AsyncSession = Depends(get_db),
):
    if start_date and not end_date:
        end_date = date.today()
    if end_date and not start_date:
        start_date = end_date
    if start_date and end_date and end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date must be greater than or equal to start_date")

    query = sqlalchemy.select(SymptomEntry).order_by(SymptomEntry.start_at.asc())

    if user_id is not None:
        query = query.where(SymptomEntry.user_id == user_id)

    if start_date and end_date:
        start_dt = datetime.combine(start_date, time.min)
        end_dt = datetime.combine(end_date, time.max)
        query = query.where(SymptomEntry.start_at.between(start_dt, end_dt))

    result = await db.execute(query)
    symptoms_list = list(result.scalars().all())

    pdf_file: BytesIO = generate_symptoms_pdf(
        symptoms_list=symptoms_list,
        start_date=start_date,
        end_date=end_date,
    )

    if start_date and end_date:
        filename = f"symptoms_report_{start_date.isoformat()}_{end_date.isoformat()}.pdf"
    else:
        filename = "symptoms_report_all_data.pdf"

    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
