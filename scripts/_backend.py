import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.core.config import get_settings  # noqa: E402
from app.db.session import get_session, init_db  # noqa: E402
from app.providers.tushare_history import TushareHistoryProvider  # noqa: E402
from app.services.history_sync import HistorySyncService  # noqa: E402


def service():
    settings = get_settings()
    if not settings.tushare_token:
        raise SystemExit("Tushare not configured: set TUSHARE_TOKEN in backend/.env")
    init_db()
    session_context = get_session()
    session = session_context.__enter__()
    return settings, session_context, HistorySyncService(TushareHistoryProvider(settings), session)
