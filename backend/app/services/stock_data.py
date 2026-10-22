from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.models import MarketDataStatus, Stock, StockAdjFactor, StockDaily, StockDailyBasic, StockPositionDaily, TechnicalDaily
from app.providers.symbols import normalize_internal


def search_stocks(session: Session, query: str, limit: int = 10) -> list[dict]:
    key = query.strip()
    if not key:
        return []
    rows = list(session.scalars(select(Stock).where(or_(Stock.code.ilike(f"%{key}%"), Stock.name.ilike(f"%{key}%"), Stock.symbol.ilike(f"%{key}%"))).limit(50)))
    def rank(stock: Stock):
        return (0 if stock.code == key else 1 if stock.code.startswith(key) else 2 if stock.name == key else 3, stock.code)
    return [{"symbol": row.symbol, "code": row.code, "name": row.name, "exchange": row.exchange, "board": row.board, "industry": row.industry, "list_status": row.list_status, "source": row.source, "is_demo": False} for row in sorted(rows, key=rank)[:limit]]


def stock_detail(session: Session, symbol: str) -> dict | None:
    symbol = normalize_internal(symbol)
    stock = session.scalar(select(Stock).where(Stock.symbol == symbol))
    if not stock:
        return None
    daily = session.scalar(select(StockDaily).where(StockDaily.stock_id == stock.id).order_by(StockDaily.trade_date.desc()))
    basic = session.scalar(select(StockDailyBasic).where(StockDailyBasic.stock_id == stock.id).order_by(StockDailyBasic.trade_date.desc()))
    technical = session.scalar(select(TechnicalDaily).where(TechnicalDaily.stock_id == stock.id).order_by(TechnicalDaily.trade_date.desc()))
    position = session.scalar(select(StockPositionDaily).where(StockPositionDaily.stock_id == stock.id).order_by(StockPositionDaily.trade_date.desc()))
    return {
        "symbol": stock.symbol, "code": stock.code, "name": stock.name, "exchange": stock.exchange, "board": stock.board,
        "industry": stock.industry, "area": stock.area, "list_date": stock.list_date, "list_status": stock.list_status,
        "latest_trade_date": daily.trade_date if daily else None, "close": float(daily.close) if daily and daily.close is not None else None,
        "market_cap": float(basic.total_market_cap_cny) if basic and basic.total_market_cap_cny is not None else None,
        "pe_ttm": float(basic.pe_ttm) if basic and basic.pe_ttm is not None else None, "pb": float(basic.pb) if basic and basic.pb is not None else None,
        "turnover_rate": float(basic.turnover_rate) if basic and basic.turnover_rate is not None else None,
        "technical": ({column: float(getattr(technical, column)) if getattr(technical, column) is not None else None for column in ("ma5", "ma10", "ma20", "ma60", "ma120", "ma250", "macd_dif", "macd_dea", "macd_hist", "rsi14")} | {"technical_score": technical.technical_score, "algorithm_version": technical.algorithm_version}) if technical else None,
        "position": ({column: float(getattr(position, column)) if getattr(position, column) is not None else None for column in ("price_percentile_6m", "price_percentile_1y", "price_percentile_3y", "distance_60d_high", "distance_52w_high", "distance_52w_low")} | {"algorithm_version": position.algorithm_version}) if position else None,
        "source": stock.source, "is_demo": False,
    }


def stock_daily(session: Session, symbol: str, start_date: date | None, end_date: date | None, adjust: str) -> dict | None:
    symbol = normalize_internal(symbol)
    stock = session.scalar(select(Stock).where(Stock.symbol == symbol))
    if not stock:
        return None
    statement = select(StockDaily).where(StockDaily.stock_id == stock.id)
    if start_date: statement = statement.where(StockDaily.trade_date >= start_date)
    if end_date: statement = statement.where(StockDaily.trade_date <= end_date)
    rows = list(session.scalars(statement.order_by(StockDaily.trade_date)))
    factors = {row.trade_date: float(row.adj_factor) for row in session.scalars(select(StockAdjFactor).where(StockAdjFactor.stock_id == stock.id))}
    latest_factor = factors.get(rows[-1].trade_date, 1.0) if rows else 1.0
    bars = []
    for row in rows:
        factor = factors.get(row.trade_date, latest_factor)
        multiplier = 1.0 if adjust == "raw" else factor / latest_factor if adjust == "qfq" else factor
        bars.append({"date": row.trade_date, "open": float(row.open) * multiplier if row.open is not None else None, "high": float(row.high) * multiplier if row.high is not None else None, "low": float(row.low) * multiplier if row.low is not None else None, "close": float(row.close) * multiplier if row.close is not None else None, "pre_close": float(row.pre_close) * multiplier if row.pre_close is not None else None, "pct_change": float(row.pct_change) if row.pct_change is not None else None, "volume_shares": float(row.volume_shares) if row.volume_shares is not None else None, "amount_cny": float(row.amount_cny) if row.amount_cny is not None else None, "source": row.source})
    return {"symbol": symbol, "adjust": adjust, "bars": bars, "latest_trade_date": rows[-1].trade_date if rows else None, "source": "postgresql" if not str(session.bind.url).startswith("sqlite") else "local_database", "is_demo": False}


def data_health(session: Session) -> list[dict]:
    return [{"dataset": row.dataset, "latest_trade_date": row.latest_trade_date, "status": row.status, "record_count": row.record_count, "updated_at": row.updated_at, "detail": row.detail} for row in session.scalars(select(MarketDataStatus).order_by(MarketDataStatus.dataset))]
