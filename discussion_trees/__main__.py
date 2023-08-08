import argparse

from builder import setup_builder
# from ingest import setup_ingest


def main():
    argument_parser = argparse.ArgumentParser(description="Run builder or ingest process")
    subparsers = argument_parser.add_subparsers(dest='command', help="Subcommand to run")

    _builder_parser = subparsers.add_parser('build', help="Run the build process to build the index.")
    _parser_parser = subparsers.add_parser('ingest', help="Run the ingest process to ingest documents.")

    args = argument_parser.parse_args()

    if args.command == "build":
        setup_builder()
    elif args.command == "ingest":
        pass
        # setup_ingest()
    else:
        print("Please select either 'build' or 'ingest' as a subcommand")


if __name__ == "__main__":
    main()