#!/usr/bin/env python3
import argparse
import collections
import logging
import re
from typing import Dict, Optional, Tuple

log = logging.getLogger(__name__)

INDENT = re.compile('^([ \t]+)')

INDENT_CHARS = set((' ', '\t'))

SPACE_INDENT_SIZES = (8, 4, 2)


def analyze_line2(line: str) -> Tuple[Optional[str], int]:
    char = line[0]
    indent_char = char
    count = 0
    while char in INDENT_CHARS:
        count += 1
        char = line[count]
    else:
        return None, 0
    return indent_char, count


def analyze_line1(line: str) -> Tuple[Optional[str], int]:
    matches = INDENT.match(line)
    if matches:
        indent_chars = matches.group(1)
        if indent_chars[0] == '\t':
            return '\t', len(indent_chars)
        else:
            return ' ', len(indent_chars)
    else:
        return None, 0


def analyze_file(filename: str):
    stats: Dict[Tuple[Optional[str], int],
                int] = collections.defaultdict(lambda: 0)
    total = 0
    with open(filename, 'r') as fd:
        for line in fd:
            stats[analyze_line2(line)] += 1
            total += 1
    return total, stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--loglevel', default='WARNING', help="Loglevel", action='store'
    )
    parser.add_argument('file', nargs='+')
    args = parser.parse_args()
    loglevel = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(loglevel, int):
        raise ValueError('Invalid log level: {}'.format(args.loglevel))
    logging.basicConfig(level=loglevel)
    for filename in args.file:
        print(analyze_file(filename))


if __name__ == '__main__':
    main()
