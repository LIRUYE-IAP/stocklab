import argparse
import asyncio

from _backend import BACKEND

from app.core.config import get_settings
from app.providers.ifind import IFindProvider


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("symbol", nargs="?", default="SZ.000630")
    args = parser.parse_args(); settings = get_settings(); provider = IFindProvider(settings)
    if not provider.configured: raise SystemExit("iFinD not configured: set IFIND_REFRESH_TOKEN in backend/.env")
    quotes = await provider.get_quotes([args.symbol]); quote = quotes[args.symbol]
    print({"symbol": quote.symbol, "price": quote.price, "open": quote.open, "high": quote.high, "low": quote.low, "trade_time": quote.trade_time, "source": quote.source, "availability": quote.availability})


if __name__ == "__main__": asyncio.run(main())
