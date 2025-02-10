from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from analytics.dependencies import get_analytics_service
from analytics.exceptions import DocumentNotFound
from analytics.schema import EventType
from analytics.service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/period")
async def get_period_stats(
    start_date: str,
    end_date: str,
    field: str,
    service: AnalyticsService = Depends(get_analytics_service),
):
    return await service.get_period_stats(start_date, end_date, field)


@router.get("/daily")
async def get_daily_stats(date: str, service: AnalyticsService = Depends(get_analytics_service)):
    try:
        return await service.get_daily_stats(date)
    except DocumentNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get("/events")
async def get_events(
    user_id: UUID | None = None,
    event_type: EventType | None = None,
    event_name: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    page: int = 1,
    limit: int = 100,
    service: AnalyticsService = Depends(get_analytics_service),
):
    return await service.get_events(
        user_id, event_type, event_name, start_date, end_date, page, limit
    )
