from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from app.models.Score import HealthScores
from app.schema.Score import HealthScoresResponse
from app.services.database import get_db
from app.services.scoring import clamp_score

router = APIRouter(tags=["health-scores"])


@router.get("/api/health-scores", response_model=list[HealthScoresResponse])
async def list_health_scores(user_id: int, db: AsyncSession = Depends(get_db)):
    query = (
        select(HealthScores)
        .where(HealthScores.user_id == user_id)
        .order_by(HealthScores.calculated_at.asc(), HealthScores.id.asc())
    )
    result = await db.execute(query)
    scores_by_day = {}

    for score in result.scalars().all():
        score_day = (
            score.calculated_at.date()
            if hasattr(score.calculated_at, "date")
            else score.calculated_at
        )
        scores_by_day[score_day] = score

    return [
        {
            "id": score.id,
            "user_id": score.user_id,
            "score": clamp_score(score.score),
            "calculated_at": score.calculated_at,
        }
        for score in scores_by_day.values()
    ]
