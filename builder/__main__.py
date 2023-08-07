import asyncio

from .builder import Builder
from .config import BuilderConfig


async def main():
    print("Hello from main()")
    config = BuilderConfig()
    config.load_environment_variables() # explicitly load the environment variables
    print("API key: " + config.openai_api_key)

    builder = Builder()


if __name__ == "__main__":
    asyncio.run(main())