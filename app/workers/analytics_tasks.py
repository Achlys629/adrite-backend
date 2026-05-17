from app.workers.celery_app import celery_app

@celery_app.task
def track_event_task(event_type: str, user_id: int, description: str = None):
    from app.core.database import SessionLocal
    from app.models.analytics import AnalyticsEvent

    db = SessionLocal()
    try:
        event = AnalyticsEvent(
            event_type=event_type,
            user_id=user_id,
            description=description
        )
        db.add(event)
        db.commit()
    finally:
        db.close()

@celery_app.task
def cleanup_old_events_task():
    # Delete analytics events older than 90 days
    from app.core.database import SessionLocal
    from app.models.analytics import AnalyticsEvent
    from datetime import datetime, timedelta, timezone

    db = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=90)
        db.query(AnalyticsEvent).filter(
            AnalyticsEvent.created_at < cutoff
        ).delete()
        db.commit()
    finally:
        db.close()