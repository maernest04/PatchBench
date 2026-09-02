import argparse
import json
from pathlib import Path


def export_items(items, output):
    Path(output).write_text(json.dumps(items) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("items", nargs="+")
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args()
    export_items(arguments.items, arguments.output)


if __name__ == "__main__":
    main()
