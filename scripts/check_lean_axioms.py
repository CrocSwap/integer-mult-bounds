#!/usr/bin/env python3
"""Run a Lean #print axioms audit and reject missing or extra dependencies."""
import argparse
from pathlib import Path
import re
import subprocess

ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}

def source_queries(text):
    """Read print commands outside nested Lean comments and ordinary strings."""
    masked = list(text)
    i, depth, string = 0, 0, False
    while i < len(text):
        if depth:
            if text.startswith('/-', i):
                count, depth = 2, depth + 1
            elif text.startswith('-/', i):
                count, depth = 2, depth - 1
            else:
                count = 1
        elif string:
            count = 2 if text[i] == '\\' else 1
            if text[i] == '"':
                string = False
        elif text.startswith('--', i):
            end = text.find('\n', i)
            count = (len(text) if end == -1 else end) - i
        elif text.startswith('/-', i):
            count, depth = 2, 1
        elif text[i] == '"':
            count, string = 1, True
        else:
            i += 1
            continue
        for j in range(i, min(i + count, len(text))):
            if text[j] not in '\r\n':
                masked[j] = ' '
        i += count
    if depth or string:
        raise ValueError('Unterminated comment or string in audit source')
    expected = re.findall(r'^[ \t]*#print\s+axioms\s+(\S+)[ \t]*$', ''.join(masked), re.M)
    if not expected or len(expected) != len(set(expected)):
        raise ValueError('Audit must list distinct theorem names')
    return expected


def check_output(output, expected):
    rows = re.findall(r"^'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)[ \t]*$",
                      output, re.M)
    headers = re.findall(r"^'[^']+' (?:depends on axioms:|does not depend on any axioms)", output, re.M)
    bad = []
    for name, raw in rows:
        axioms = [] if not raw else [part.strip() for part in raw.split(',')]
        if any(axiom not in ALLOWED for axiom in axioms):
            bad.append((name, axioms))
    if (len(headers) != len(rows) or len(rows) != len(expected)
            or {name for name, _ in rows} != set(expected) or bad):
        raise ValueError(f'Axiom audit failed: reported {len(rows)}/{len(expected)}; unexpected {bad}')
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--audit', type=Path, required=True)
    args = parser.parse_args()
    audit = args.audit.resolve()
    try:
        expected = source_queries(audit.read_text(encoding='utf-8'))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    result = subprocess.run(['lake', 'env', 'lean', str(audit)],
                            cwd=args.project.resolve(), text=True, encoding='utf-8', capture_output=True)
    output = result.stdout + result.stderr
    try:
        if result.returncode:
            raise ValueError(f'Lean exited with status {result.returncode}')
        count = check_output(output, expected)
    except ValueError as exc:
        print(output)
        raise SystemExit(str(exc)) from exc
    print(f'PASS {count} declarations; only propext, Classical.choice and Quot.sound')


if __name__ == '__main__':
    main()
