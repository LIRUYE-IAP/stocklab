import asyncio
from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.catalog import STOCKS
from app.core.config import get_settings
from app.db.session import get_session, init_db
from app.providers.tushare_history import TushareHistoryProvider
from app.providers.symbols import normalize_internal
from app.services.market_status import derive_market_status
from app.services.quote_service import QuoteService
from app.services.stock_data import data_health, search_stocks, stock_daily, stock_detail

settings = get_settings()
quote_service = QuoteService(settings)
history_provider = TushareHistoryProvider(settings)


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.database_auto_create:
        init_db()
    yield


app = FastAPI(title="StockLab Market API", version="0.3.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"], allow_credentials=True, allow_methods=["GET"], allow_headers=["*"])


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "service": "stocklab-market"}


@app.get("/api/v1/realtime/status")
async def realtime_status():
    return quote_service.status()


def finalize_quotes(values):
    for quote in values.values():
        if quote.availability == "unavailable": quote.market_status = "OFFLINE"
        elif quote.is_stale: quote.market_status = "STALE"
        else: quote.market_status = derive_market_status(quote.trade_time, quote.received_at, settings.quote_stale_after_seconds, settings.quote_timezone)
    return values


def parse_symbols(value: str) -> list[str]:
    symbols = [part.strip() for part in value.split(",") if part.strip()]
    if not symbols or len(symbols) > 100:
        raise HTTPException(400, "Provide between 1 and 100 symbols")
    try:
        return [normalize_internal(symbol) for symbol in symbols]
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@app.get("/api/v1/realtime/quotes")
async def quotes(symbols: str = Query(...)):
    values = parse_symbols(symbols)
    return {"quotes": list(finalize_quotes(await quote_service.get_quotes(values)).values()), "status": quote_service.status()}


@app.get("/api/v1/realtime/quotes/{symbol}")
async def quote(symbol: str):
    values = parse_symbols(symbol)
    return finalize_quotes(await quote_service.get_quotes(values))[values[0]]


@app.get("/api/v1/realtime/minutes/{symbol}")
async def minutes(symbol: str, date: str | None = None):
    value = parse_symbols(symbol)[0]
    if quote_service.ifind.configured:
        return {"symbol": value, "date": date, "bars": [], "availability": "not_implemented_for_current_entitlement"}
    return {"symbol": value, "date": date, "bars": [], "availability": "provider_not_configured"}


@app.get("/api/v1/stocks/search")
async def search(q: str = ""):
    key = q.strip().lower()
    with get_session() as session:
        rows = search_stocks(session, key, 10)
    if rows or settings.data_mode == "live":
        return rows
    return [{**item, "source": "mock", "is_demo": True} for item in STOCKS if key and (key in item["code"] or key in item["name"].lower())][:10]


@app.get("/api/v1/stocks/{symbol}/daily")
async def daily(symbol: str, start_date: date | None = None, end_date: date | None = None, adjust: str = Query("qfq", pattern="^(raw|qfq|hfq)$")):
    try: normalized = normalize_internal(symbol)
    except ValueError as exc: raise HTTPException(422, str(exc)) from exc
    with get_session() as session:
        result = stock_daily(session, normalized, start_date, end_date, adjust)
    if result is None and settings.data_mode == "mock" and any(item["symbol"] == normalized for item in STOCKS):
        return {"symbol": normalized, "adjust": adjust, "bars": [], "latest_trade_date": None, "source": "mock", "is_demo": True}
    if result is None: raise HTTPException(404, f"Stock {normalized} not found in historical database")
    return result


@app.get("/api/v1/stocks/{symbol}")
async def stock(symbol: str):
    try: normalized = normalize_internal(symbol)
    except ValueError as exc: raise HTTPException(422, str(exc)) from exc
    with get_session() as session:
        result = stock_detail(session, normalized)
    if result is None and settings.data_mode == "mock":
        catalog_item = next((item for item in STOCKS if item["symbol"] == normalized), None)
        if catalog_item:
            return {
                **catalog_item, "board": "UNKNOWN", "industry": None, "area": None,
                "list_date": None, "list_status": "DEMO", "latest_trade_date": None,
                "close": None, "market_cap": None, "pe_ttm": None, "pb": None,
                "turnover_rate": None, "technical": None, "position": None,
                "source": "mock", "is_demo": True,
            }
    if result is None: raise HTTPException(404, f"Stock {normalized} not found in historical database")
    return result


@app.get("/api/v1/settings/data")
async def data_status():
    with get_session() as session:
        datasets = data_health(session)
    return {"data_mode": settings.data_mode, "historical_provider": {"name": settings.history_provider, "configured": history_provider.configured}, "realtime_provider": {"name": settings.realtime_provider, "configured": quote_service.ifind.configured, "active_source": quote_service.active_source, "last_quote_at": quote_service.last_success_at}, "redis": {"configured": settings.quote_cache_backend == "redis", "active_backend": quote_service.status().cache_backend}, "database": {"configured": bool(settings.database_url), "engine": "postgresql" if settings.database_url.startswith("postgresql") else "sqlite-development"}, "datasets": datasets}


@app.websocket("/api/v1/ws/quotes")
async def quote_socket(websocket: WebSocket):
    origin = websocket.headers.get("origin")
    if origin and origin not in {"http://127.0.0.1:5173", "http://localhost:5173"}:
        await websocket.close(code=1008)
        return
    await websocket.accept()
    subscribed: list[str] = []
    try:
        while True:
            try:
                message = await asyncio.wait_for(websocket.receive_json(), timeout=settings.quote_list_interval_seconds)
                action = message.get("action")
                if action == "ping":
                    await websocket.send_json({"type": "pong"})
                    continue
                values = parse_symbols(",".join(message.get("symbols", []))) if message.get("symbols") else []
                if action == "subscribe":
                    subscribed = list(dict.fromkeys([*subscribed, *values]))[:100]
                elif action == "unsubscribe":
                    subscribed = [s for s in subscribed if s not in values]
                await websocket.send_json({"type": "ack", "symbols": subscribed})
            except asyncio.TimeoutError:
                pass
            if subscribed:
                current = finalize_quotes(await quote_service.get_quotes(subscribed))
                await websocket.send_json({"type": "snapshot", "quotes": [q.model_dump(mode="json") for q in current.values()], "status": quote_service.status().model_dump(mode="json")})
            else:
                await websocket.send_json({"type": "heartbeat"})
    except WebSocketDisconnect:
        return
