#!/usr/bin/env python3
"""Run a Lean #print axioms audit and reject missing or extra dependencies."""
import argparse
from pathlib import Path
import re
import subprocess

ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--project', type=Path, required=True)
parser.add_argument('--audit', type=Path, required=True)
args = parser.parse_args()
audit = args.audit.resolve()
expected = re.findall(r'^#print axioms (\S+)\s*$', audit.read_text(), re.M)
if not expected or len(expected) != len(set(expected)):
    raise SystemExit('Audit must list distinct theorem names')
result = subprocess.run(['lake', 'env', 'lean', str(audit)],
                        cwd=args.project.resolve(), text=True, capture_output=True)
output = result.stdout + result.stderr
rows = re.findall(r"^'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",
                  output, re.M)
bad = [(name, ax) for name, ax in rows if set(ax.split(', '))-{''}-ALLOWED]
if result.returncode or len(rows) != len(expected) or {n for n, _ in rows} != set(expected) or bad:
    print(output)
    raise SystemExit(f'Axiom audit failed: reported {len(rows)}/{len(expected)}; unexpected {bad}')
print(f'PASS {len(rows)} declarations; only propext, Classical.choice and Quot.sound')
