import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    arguments = parser.parse_args()
    print(arguments.name.lower())


if __name__ == "__main__":
    main()
