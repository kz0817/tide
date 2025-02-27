#!/usr/bin/env python3
import argparse


def run(args):
    pass


def main():
    parser = argparse.ArgumentParser(description="This is a sample script.")

    parser.add_argument('-p', '--port', default=3423)

    args = parser.parse_args()
    run(args)


if __name__ == '__main__':
    main()
