import asyncio

from .ingester import Ingester
from .config import IngesterConfig


async def run_ingester():
    print("Hello from run_ingester()")
    config = IngesterConfig()
    config.load_environment_variables()
    ingester = Ingester(config)
    ingester.ingest()

def setup_ingester():
    asyncio.run(run_ingester())


if __name__ == "__main__":
    asyncio.run(run_ingester())