from app.services.history_sync import HistorySyncService


async def run(sync_service: HistorySyncService, symbol: str, trade_date: str):
    """Synchronize all supported EOD datasets for one symbol and date."""
    return await sync_service.sync_symbol_range(symbol, trade_date, trade_date)
