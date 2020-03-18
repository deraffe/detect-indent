#!/usr/bin/env python3
import argparse
import collections
import enum
import logging
import re
from typing import Dict, Optional, Tuple

log = logging.getLogger(__name__)

INDENT = re.compile('^([ \t]+)')

INDENT_CHARS = set((' ', '\t'))

SPACE_INDENT_SIZES = (8, 4, 2)


class IndentType(enum.Enum):
    SPACES = 0
    TABS = 1
    MIXED = 2
    NONE = 3


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


def analyze_dominant_indent(
    total: int, stats_indent_chars: Dict[Optional[str], int]
) -> IndentType:
    dominant_indent = []
    for char, count in stats_indent_chars.items():
        if char is None:
            continue
        if count / total > 0.33:
            dominant_indent.append(char)
    if len(dominant_indent) > 1:
        return IndentType.MIXED
    elif len(dominant_indent) == 1:
        if dominant_indent[0] == ' ':
            return IndentType.SPACES
        elif dominant_indent[0] == '\t':
            return IndentType.TABS
    return IndentType.NONE


def analyze_indent(
    total: int, stats_indent_chars: Dict[Optional[str], int]
) -> IndentType:
    has_spaces = False
    has_tabs = False
    for char, count in stats_indent_chars.items():
        if char is None:
            continue
        elif char == ' ':
            has_spaces = True
        elif char == '\t':
            has_tabs = True
    if has_spaces and has_tabs:
        return IndentType.MIXED
    elif has_spaces:
        return IndentType.SPACES
    elif has_tabs:
        return IndentType.TABS
    return IndentType.NONE


def analyze_spaces(total: int, stats_spaces: Dict[int, int]) -> Optional[int]:
    for space_size in SPACE_INDENT_SIZES:
        yay = 0
        nay = 0
        for num_spaces, occurences in stats_spaces.items():
            if num_spaces % space_size == 0:
                yay += occurences
            else:
                nay += occurences
        if nay / yay < 0.1:
            return space_size
    return None


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
        indent_type = analyze_indent(total, indent_chars)
        print(f'Indent Type: {indent_type}')
        dominant_type = analyze_dominant_indent(total, indent_chars)
        print(f'Dominant Type: {dominant_type}')
        if indent_type in (IndentType.SPACES, IndentType.MIXED):
            print(analyze_spaces(total, spaces))


if __name__ == '__main__':
    main()
