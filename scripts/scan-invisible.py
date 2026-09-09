#!/usr/bin/env python3
"""
scan-invisible.py -- invisible-character scan (standing convention).

Scans one or more files for zero-width and other invisible/confusable
characters that can silently break inline JavaScript or slip past visual
review: ZWSP, ZWNJ, ZWJ, BOM, word-joiner, NBSP, and the four smart quotes.

Usage:
    python3 scripts/scan-invisible.py <file> [<file> ...]

Exit code 0 if every file is clean; 1 if any hit is found. Prints, per file,
either "CLEAN" or the codepoint counts and the 1-indexed line numbers where
they occur.

Why this exists, not a `grep -P`/`python3 -c` one-liner: a one-liner's
character class was mangled by shell quoting and produced 2312 false
positives on 2026-09-08; the same mangling can produce a false negative,
and this check is trusted to catch a bug that silently breaks a page.
Versioned once here instead of duplicated inline across multiple repos'
CLAUDE.md and work-session command files, where copies can drift.
"""
import sys
import io
import collections

BAD = {
    0x200B: 'ZWSP',
    0x200C: 'ZWNJ',
    0x200D: 'ZWJ',
    0xFEFF: 'BOM',
    0x2060: 'WJ',
    0x00A0: 'NBSP',
    0x2018: 'LSQUO',
    0x2019: 'RSQUO',
    0x201C: 'LDQUO',
    0x201D: 'RDQUO',
}


def scan(path):
    with io.open(path, encoding='utf-8') as f:
        text = f.read()
    hits = collections.Counter(BAD[ord(c)] for c in text if ord(c) in BAD)
    lines = sorted({
        i for i, line in enumerate(text.split('\n'), 1)
        for c in line if ord(c) in BAD
    })
    return hits, lines


def main(argv):
    if not argv:
        print('Usage: python3 scripts/scan-invisible.py <file> [<file> ...]', file=sys.stderr)
        return 2

    bad_total = 0
    for path in argv:
        hits, lines = scan(path)
        bad_total += sum(hits.values())
        status = dict(hits) if hits else 'CLEAN'
        suffix = f'  lines: {lines}' if lines else ''
        print(f'{path}: {status}{suffix}')

    return 1 if bad_total else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
