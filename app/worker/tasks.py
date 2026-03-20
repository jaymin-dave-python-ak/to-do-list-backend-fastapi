import asyncio
from datetime import datetime, timedelta, timezone
from app.worker.celery_app import celery_app
from app.db.database import AsyncSessionLocal
from app.repositories.item_repo import ItemRepository
from app.service.email_service import EmailService
from app.db.models.user import UserModel
from app.db.models.item import ItemModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload


def run_async(coro):
    """Helper to run async logic in sync Celery environment"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
        asyncio.set_event_loop(None)


@celery_app.task(name="execute_reminder_email")
def execute_reminder_email(item_id: str):
    """The Worker task: Runs at the exact ETA provided by Redis"""

    async def send_logic():
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(ItemModel)
                .where(ItemModel.id == item_id)
                .options(selectinload(ItemModel.owner))
            )
            item = result.scalar_one_or_none()
            now = datetime.now(timezone.utc)
            if not item or item.reminded or item.remind_me_at is None:
                return
            
            email_service = EmailService()
            await email_service.send_reminder_email(
                email_to=item.owner.email,
                subject=f"Reminder: {item.title}",
                body=f"This is a reminder for your task: {item.title}",
            )
            item.reminded = True
            item.dispatched = False
            await db.commit()

    run_async(send_logic())


@celery_app.task(name="dispatch_reminders_batch")
def dispatch_reminders_batch():
    """The Beat task: Runs every 1 minute to fill the Redis queue"""

    async def dispatch_logic():
        async with AsyncSessionLocal() as db:
            repo = ItemRepository()

            now = datetime.now(timezone.utc)
            window_end = now + timedelta(seconds=60)

            pending_items = await repo.get_all_pending_reminders(window_end, db)
            if pending_items:
                for item in pending_items:
                    execute_reminder_email.apply_async(
                        args=[str(item.id)], eta=item.remind_me_at
                    )
                    item.dispatched = True
                await db.commit()

    run_async(dispatch_logic())
