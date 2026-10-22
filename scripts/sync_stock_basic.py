import asyncio

from _backend import service


async def main():
    _, context, sync = service()
    try:
        job = await sync.sync_stock_basic()
        print(f"stock_basic {job.status}: received={job.received_records}, inserted={job.inserted_records}, updated={job.updated_records}")
    finally:
        context.__exit__(None, None, None)


if __name__ == "__main__": asyncio.run(main())
