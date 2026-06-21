from datetime import datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.Score import HealthScores
from app.models.SymptomEntry import SymptomEntry


def clamp_score(value: float) -> int:
    return max(1, min(100, round(value)))


def sleep_hours_component(sleep_hours: float | None) -> float:
    if sleep_hours is None:
        return 50.0

    # 8 hours is treated as the center of the normal recovery range.
    return max(0.0, 100.0 - abs(float(sleep_hours) - 8.0) * 18.0)


def calculate_health_score(
    severity: float | None,
    sleep_quality: float | None,
    stress_level: float | None,
    sleep_hours: float | None = None,
) -> int:
    severity_value = float(severity or 0)
    sleep_quality_value = float(sleep_quality or 0)
    stress_value = float(stress_level or 0)

    severity_component = max(0.0, 100.0 - severity_value * 10.0)
    sleep_quality_score = max(0.0, min(100.0, sleep_quality_value * 10.0))
    stress_component = max(0.0, 100.0 - stress_value * 10.0)

    score = (
        severity_component * 0.45
        + sleep_quality_score * 0.20
        + stress_component * 0.20
        + sleep_hours_component(sleep_hours) * 0.15
    )
    return clamp_score(score)


async def update_daily_health_score(
    db: AsyncSession,
    user_id: int,
    event_timestamp: datetime,
) -> HealthScores:
    target_date = event_timestamp.date()
    day_start = datetime.combine(target_date, time.min)
    day_end = day_start + timedelta(days=1)

    metrics_query = select(
        func.avg(SymptomEntry.severity).label("avg_severity"),
        func.avg(SymptomEntry.sleep_quality).label("avg_sleep_quality"),
        func.avg(SymptomEntry.sleep_hours).label("avg_sleep_hours"),
        func.avg(SymptomEntry.stress_level).label("avg_stress"),
    ).where(
        SymptomEntry.user_id == user_id,
        SymptomEntry.start_at >= day_start,
        SymptomEntry.start_at < day_end,
    )

    metrics = (await db.execute(metrics_query)).one()
    new_score = calculate_health_score(
        severity=metrics.avg_severity,
        sleep_quality=metrics.avg_sleep_quality,
        sleep_hours=metrics.avg_sleep_hours,
        stress_level=metrics.avg_stress,
    )

    score_query = select(HealthScores).where(
        HealthScores.user_id == user_id,
        HealthScores.calculated_at >= day_start,
        HealthScores.calculated_at < day_end,
    )
    score_entry = (await db.execute(score_query)).scalars().first()

    if score_entry:
        score_entry.score = new_score
        score_entry.calculated_at = day_start
    else:
        score_entry = HealthScores(
            user_id=user_id,
            score=new_score,
            calculated_at=day_start,
        )
        db.add(score_entry)

    await db.commit()
    await db.refresh(score_entry)
    return score_entry
