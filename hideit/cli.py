import argparse
import getpass
import os
import sys
from pathlib import Path

from hideit import crypt
from hideit.arg_validators import ArgFile, ArgFileOrDir
from hideit.crypt import IncorrectPasswordOrFileCorrupted


def cli() -> None:
    parser = argparse.ArgumentParser(prog='hideit')
    subparsers = parser.add_subparsers(required=True)

    hide_parser = subparsers.add_parser('hide', help='Hide a file or folder')
    hide_parser.add_argument(
        '--password',
        default=os.getenv('HIDEIT_PASSWORD'),
        required=False,
        help='Password used to hide the file or folder (envvar: HIDEIT_PASSWORD)',
    )
    hide_parser.add_argument(
        'path', type=ArgFileOrDir(), help='File or folder to hide'
    )
    hide_parser.set_defaults(
        func=lambda args: hide(parser=hide_parser, args=args)
    )

    unhide_parser = subparsers.add_parser(
        'unhide', help='Unhide a file or folder'
    )
    unhide_parser.add_argument(
        '--password',
        default=os.getenv('HIDEIT_PASSWORD'),
        required=False,
        help='Password used to unhide the file or folder (envvar: HIDEIT_PASSWORD)',
    )
    unhide_parser.add_argument(
        'path',
        type=ArgFile(allowed_suffixes=['.lock']),
        help='File or folder to unhide',
    )
    unhide_parser.set_defaults(
        func=lambda args: unhide(parser=unhide_parser, args=args)
    )

    args = parser.parse_args()
    args.func(args)


def hide(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    password: str = args.password
    path: Path = args.path

    if not password:
        password = getpass.getpass()

    if path.is_dir():
        crypt.encrypt_dir(path=path, password=password)
    elif path.is_file():
        crypt.encrypt_file(path=path, password=password)


def unhide(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    password: str = args.password
    path: Path = args.path

    if not password:
        password = getpass.getpass()

    try:
        if str(path).endswith('.tar.lock'):
            crypt.decrypt_dir(path=path, password=password)
        else:
            crypt.decrypt_file(path=path, password=password)
    except IncorrectPasswordOrFileCorrupted as error:
        print(error, file=sys.stderr)
