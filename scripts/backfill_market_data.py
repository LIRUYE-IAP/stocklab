import argparse
import asyncio
from datetime import date, timedelta

from _backend import service


async def main():
    parser = argparse.ArgumentParser(description="Backfill one StockLab symbol; start with 30 days before expanding.")
    parser.add_argument("symbol", nargs="?", default="SZ.000630")
    parser.add_argument("--start", default=(date.today() - timedelta(days=45)).strftime("%Y%m%d"))
    parser.add_argument("--end", default=date.today().strftime("%Y%m%d"))
    args = parser.parse_args()
    _, context, sync = service()
    try:
        jobs = await sync.sync_symbol_range(args.symbol, args.start, args.end)
        print("; ".join(f"{job.job_type}={job.status}:{job.received_records}" for job in jobs))
    finally: context.__exit__(None, None, None)


if __name__ == "__main__": asyncio.run(main())
