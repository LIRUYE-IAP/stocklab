from app.services.history_sync import HistorySyncService


async def run(sync_service: HistorySyncService):
    """Synchronize security master data without coupling to a scheduler."""
    return await sync_service.sync_stock_basic()
