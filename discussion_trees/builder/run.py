import asyncio

from .builder import Builder
from .config import BuilderConfig


async def run_builder():
    print("Hello from run_builder()")
    config = BuilderConfig()
    config.load_environment_variables() # explicitly load the environment variables
    print("TASK DOCUMENT: ", config.builder_task_document)
    builder = Builder(config)


def setup_builder():
    asyncio.run(run_builder())


if __name__ == "__main__":
    asyncio.run(run_builder())