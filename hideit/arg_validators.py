"""
Custom argparse validators for CLI argument validation.

These classes are used as `type=` callables in
`argparse.ArgumentParser.add_argument`.

Examples:
    parser = ArgumentParser()
    parser.add_argument("file", type=ArgFileOrDir())
"""

import argparse
from collections.abc import Iterable
from pathlib import Path


class ArgFile:
    def __init__(self, allowed_suffixes: Iterable[str]):
        self.allowed_suffixes = allowed_suffixes

    def __call__(self, value: str) -> Path:
        try:
            parsed_path = Path(value)
        except Exception as exc:
            raise argparse.ArgumentTypeError(
                f"'{value}' is not a valid file"
            ) from exc

        if not parsed_path.is_file():
            raise argparse.ArgumentTypeError(f"'{value}' is not a valid file")

        if parsed_path.suffix not in self.allowed_suffixes:
            allowed_suffixes = ', '.join(self.allowed_suffixes)
            raise argparse.ArgumentTypeError(
                f"'{value}' must have one of the following extensions: {allowed_suffixes}"
            )

        return parsed_path


class ArgFileOrDir:
    def __call__(self, value: str) -> Path:
        try:
            parsed_path = Path(value)
        except Exception as exc:
            raise argparse.ArgumentTypeError(
                f"'{value}' is not a valid file or folder"
            ) from exc

        if not parsed_path.is_file() and not parsed_path.is_dir():
            raise argparse.ArgumentTypeError(
                f"'{value}' is not a valid file or folder"
            )

        return parsed_path
