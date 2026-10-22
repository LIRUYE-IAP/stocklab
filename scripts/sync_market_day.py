import argparse
import asyncio
from datetime import date, timedelta

from _backend import service


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("symbol", nargs="?", default="SZ.000630")
    parser.add_argument("--date", default=date.today().strftime("%Y%m%d"))
    args = parser.parse_args()
    _, context, sync = service()
    try:
        jobs = await sync.sync_symbol_range(args.symbol, args.date, args.date)
        print("; ".join(f"{job.job_type}={job.status}:{job.received_records}" for job in jobs))
    finally: context.__exit__(None, None, None)


if __name__ == "__main__": asyncio.run(main())
