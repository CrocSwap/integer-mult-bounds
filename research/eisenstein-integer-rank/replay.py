#!/usr/bin/env python3
"""Optional output-identical full PR2017 replay using exact integer K-rank."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import retained


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', action='store_true', help='timing control: retained rank unchanged')
    args = parser.parse_args()
    old = retained.load()
    if not args.original:
        retained.install(old)
    old.main()


if __name__ == '__main__':
    main()
