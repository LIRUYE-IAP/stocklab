import argparse
import asyncio
from datetime import date, timedelta

from _backend import service


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default=(date.today() - timedelta(days=45)).strftime("%Y%m%d"))
    parser.add_argument("--end", default=date.today().strftime("%Y%m%d"))
    args = parser.parse_args()
    _, context, sync = service()
    try:
        job = await sync.sync_trade_calendar(args.start, args.end)
        print(f"trade_calendar {job.status}: received={job.received_records}")
    finally: context.__exit__(None, None, None)


if __name__ == "__main__": asyncio.run(main())
