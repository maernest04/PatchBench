import argparse
from pathlib import Path


def read_lines(input_path):
    return Path(input_path).read_text(encoding="ascii").splitlines()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path")
    arguments = parser.parse_args()
    print("\n".join(read_lines(arguments.input_path)))


if __name__ == "__main__":
    main()
