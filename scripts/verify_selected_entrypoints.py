#!/usr/bin/env python3
"""Bind the public restatements of the selected result to its record.

certificates/selected-result.json is authoritative. README.md,
docs/research/current-status.md, CONTRIBUTORS.md, CONTRIBUTING.md and
CITATION.cff restate parts of it for readers, contributors and citation tools.
This check requires each restatement to agree with the record: the exact kappa
and its decimal, the primary source PR, the current review and receipt, and the
replay command. It also binds the record's own replay target and previous
checkpoint.

A missing anchor fails like a contradicting one. The check reads metadata
only; it does not replay, review or certify the construction.

Prepared by Ian Libânio with substantial AI assistance (Claude Opus 5.5,
Anthropic, via Claude Code). Apache-2.0.
"""
from fractions import Fraction
from pathlib import Path, PurePosixPath
import argparse
import json
import posixpath
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
RECORD = 'certificates/selected-result.json'
ENTRY_POINTS = ('README.md', 'docs/research/current-status.md', 'CONTRIBUTORS.md', 'CONTRIBUTING.md',
                'CITATION.cff', 'Makefile')

DECIMAL = r'([0-9]+\.[0-9]+)'
DENOMINATOR = r'([0-9]+|10\^\{?[0-9]+\}?)'
README_KAPPA = re.compile(r'\\kappa\s*=\s*\\frac\{([0-9]+)\}\{' + DENOMINATOR + r'\}\s*=\s*' + DECIMAL
                          + r'(?:\s*\\times\s*10\^\{?(-?[0-9]+)\}?)?')
STATUS_KAPPA = re.compile(r'κ[^*\n]*\*\*' + DECIMAL + r'\*\*')
MAKE_COMMAND = re.compile(r'`make ([A-Za-z0-9_.-]+)`')
LINK = re.compile(r'\]\(([^)\s#]+)(?:#[^)]*)?\)')
CONTRIBUTING_REVIEW = re.compile(r'\[current maintainer review\]\(([^)\s]+)\)')
CONTRIBUTING_REPLAY = re.compile(r'currently\s+`make ([A-Za-z0-9_.-]+)`')
CITATION_KAPPA = re.compile(r'kappa\s*=\s*([0-9]+)/([0-9]+)\s*=\s*' + DECIMAL)
CITATION_PRIMARY = re.compile(r'selected checkpoint is\s+PR\s*([0-9]+)')
CONTRIBUTORS_CURRENT = re.compile(r'Current reviewed composition:\s*#([0-9]+)[^κ\n]*κ\s*=\s*' + DECIMAL)


def finding(entry, field, expected, found):
    status = 'missing' if found is None else ('match' if found == expected else 'mismatch')
    return {'entry': entry, 'field': field, 'status': status,
            'expected': None if expected is None else str(expected),
            'found': None if found is None else str(found)}


def exact(text):
    return Fraction(text)


def decimal_finding(entry, record, found):
    """Compare a printed decimal exactly with the record, reporting both as printed."""
    out = finding(entry, 'decimal', record['decimal'], found)
    if found is not None and exact(found) == exact(record['decimal']):
        out['status'] = 'match'
    return out


def denominator(text):
    if text.startswith('10^'):
        return 10 ** int(text[3:].strip('{}'))
    return int(text)


def section(text, heading):
    """Return the first block that starts at a line beginning with heading."""
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith(heading)]
    if not starts:
        return ''
    end = next((i for i in range(starts[0] + 1, len(lines)) if lines[i].startswith(heading)), len(lines))
    return '\n'.join(lines[starts[0]:end])


def first_section(text):
    """Return the text before the second top-level heading."""
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith('# ')]
    end = starts[1] if len(starts) > 1 else len(lines)
    return '\n'.join(lines[:end])


def links(text, base):
    return {posixpath.normpath(str(PurePosixPath(base) / target)) for target in LINK.findall(text)}


def linked(entry, field, text, base, expected):
    return finding(entry, field, expected, expected if expected in links(text, base) else None)


def primary_pr(record):
    """The source PR whose reviewed head is the audited source head."""
    head = record.get('audited_source_head')
    matches = [int(pr) for pr, sha in record.get('reviewed_dependency_heads', {}).items() if sha == head]
    return matches[0] if head and len(matches) == 1 else None


def read(root, relative):
    p = root / relative
    return p.read_text(encoding='utf-8') if p.is_file() else None


def check_readme(text, record, kappa):
    entry, out = 'README.md', []
    current = section(text, '## ')
    m = README_KAPPA.search(current)
    out.append(finding(entry, 'kappa', kappa, m and Fraction(int(m.group(1)), denominator(m.group(2)))))
    printed = m and (m.group(3) + ('e' + m.group(4) if m.group(4) else ''))
    out.append(decimal_finding(entry, record, printed))
    out.append(linked(entry, 'review link', current, '.', record['review']))
    return out


def check_status(text, record):
    entry, out = 'docs/research/current-status.md', []
    current = first_section(text)
    m = STATUS_KAPPA.search(current)
    out.append(decimal_finding(entry, record, m and m.group(1)))
    m = MAKE_COMMAND.search(current)
    out.append(finding(entry, 'replay', record['reproduce'], m and 'make ' + m.group(1)))
    out.append(linked(entry, 'review link', current, 'docs/research', record['review']))
    out.append(linked(entry, 'receipt link', current, 'docs/research', record['validation']))
    return out


def check_contributors(text, record):
    entry = 'CONTRIBUTORS.md'
    m = CONTRIBUTORS_CURRENT.search(text)
    head = text.split('\n## ', 1)[0]
    return [finding(entry, 'primary PR', primary_pr(record), m and int(m.group(1))),
            decimal_finding(entry, record, m and m.group(2)),
            linked(entry, 'review link', head, '.', record['review'])]


def check_contributing(text, record):
    entry = 'CONTRIBUTING.md'
    m = CONTRIBUTING_REVIEW.search(text)
    review = m and posixpath.normpath(m.group(1))
    m = CONTRIBUTING_REPLAY.search(text)
    return [finding(entry, 'current review', record['review'], review),
            finding(entry, 'replay', record['reproduce'], m and 'make ' + m.group(1))]


def check_citation(text, record, kappa):
    entry, out = 'CITATION.cff', []
    m = CITATION_PRIMARY.search(text)
    out.append(finding(entry, 'primary PR', primary_pr(record), m and int(m.group(1))))
    claims = CITATION_KAPPA.findall(text)
    if not claims:
        out.append(finding(entry, 'kappa', kappa, None))
    for numerator, denom, decimal in claims:
        out.append(finding(entry, 'kappa', kappa, Fraction(int(numerator), int(denom))))
        out.append(decimal_finding(entry, record, decimal))
    return out


def check_record(record, root, makefile):
    entry, out = RECORD, []
    command = record.get('reproduce', '')
    target = command[len('make '):] if command.startswith('make ') else None
    defined = target if target and makefile and re.search(
        r'^' + re.escape(target) + r'\s*:', makefile, re.M) else None
    out.append(finding(entry, 'replay target', target or command, defined))
    if 'previous_record' in record:
        previous = read(root, record['previous_record'])
        found = previous and json.loads(previous).get('kappa')
        out.append(finding(entry, 'previous kappa', exact(record['previous_kappa']), found and exact(found)))
    return out


def check(record, root=ROOT):
    """Return one finding per bound restatement; every status must be 'match'."""
    kappa = exact(record['kappa'])
    texts = {name: read(root, name) for name in ENTRY_POINTS}
    out = [finding(RECORD, 'decimal', kappa, exact(record['decimal']))]
    for name, text in texts.items():
        if text is None:
            out.append(finding(name, 'file', name, None))
    if texts['README.md'] is not None:
        out += check_readme(texts['README.md'], record, kappa)
    if texts['docs/research/current-status.md'] is not None:
        out += check_status(texts['docs/research/current-status.md'], record)
    if texts['CONTRIBUTORS.md'] is not None:
        out += check_contributors(texts['CONTRIBUTORS.md'], record)
    if texts['CONTRIBUTING.md'] is not None:
        out += check_contributing(texts['CONTRIBUTING.md'], record)
    if texts['CITATION.cff'] is not None:
        out += check_citation(texts['CITATION.cff'], record, kappa)
    out += check_record(record, root, texts['Makefile'])
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', type=Path, default=ROOT, help='Repository tree to check')
    parser.add_argument('--json', action='store_true', help='Print every finding as JSON')
    args = parser.parse_args()
    root = args.root.resolve()
    record = json.loads((root / RECORD).read_text(encoding='utf-8'))
    findings = check(record, root)
    failures = [f for f in findings if f['status'] != 'match']
    if args.json:
        print(json.dumps(findings, indent=1, ensure_ascii=False))
    for f in failures:
        print('{status}: {entry} {field}: expected {expected}, found {found}'.format(**f), file=sys.stderr)
    if failures:
        raise SystemExit(f'FAIL {len(failures)} of {len(findings)} selected-result restatements disagree or are missing')
    print(f'PASS {len(findings)} selected-result restatements agree with {RECORD}: kappa {exact(record["kappa"])}')


if __name__ == '__main__':
    main()
