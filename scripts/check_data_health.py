from _backend import BACKEND

from app.core.config import get_settings
from app.db.session import get_session, init_db
from app.services.stock_data import data_health

settings = get_settings(); init_db()
print(f"mode={settings.data_mode} database={'postgresql' if settings.database_url.startswith('postgresql') else 'sqlite-development'}")
print(f"tushare_configured={bool(settings.tushare_token)} ifind_configured={bool(settings.ifind_refresh_token or settings.ifind_access_token)}")
with get_session() as session:
    rows = data_health(session)
for row in rows: print(f"{row['dataset']}: {row['status']} latest={row['latest_trade_date']} records={row['record_count']}")
if not rows: print("No historical datasets have been synchronized.")
