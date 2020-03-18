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
    log.debug(f'{indent_char=} {line=}')
    while char in INDENT_CHARS:
        count += 1
        char = line[count]
    if indent_char not in INDENT_CHARS:
        log.debug('Analysis: no indent')
        return None, 0
    log.debug(f'Analysis: {count} "{indent_char}"s')
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
    stats_spaces: Dict[int, int] = collections.defaultdict(lambda: 0)
    stats_indent_chars: Dict[Optional[str],
                             int] = collections.defaultdict(lambda: 0)
    total = 0
    with open(filename, 'r') as fd:
        for line in fd:
            char, count = analyze_line2(line)
            total += 1
            stats_indent_chars[char] += 1
            if char == ' ':
                stats_spaces[count] += 1
    return total, stats_indent_chars, stats_spaces


def analyze_indent(total: int, stats_indent_chars: Dict[Optional[str], int]):
    return stats_indent_chars


def analyze_spaces(total: int, stats_spaces: Dict[int, int]):
    return stats_spaces


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
        total, indent_chars, spaces = analyze_file(filename)
        log.debug((total, indent_chars, spaces))
        print(analyze_indent(total, indent_chars))
        print(analyze_spaces(total, spaces))


if __name__ == '__main__':
    main()
