import asyncio

from .ingester import Ingester
from .config import IngesterConfig


async def run_ingester():
    print("Hello from run_ingester()")
    config = IngesterConfig()