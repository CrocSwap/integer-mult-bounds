#!/usr/bin/env python3
"""Fresh Lean4.34.1 kernel check and actual false-premise controls; Apache-2.0."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
THEOREMS = {'reverse_inverse', 'no_four_pivot', 'relaxed_diagonal',
            'relaxed_remaining_zeros', 'relaxed_four_pivot', 'relaxed_missing_edge'}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def run(lean, path):
    return subprocess.run([str(lean), '-j1', str(path)], capture_output=True,
                          text=True, encoding='utf-8', timeout=90)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lean', required=True, type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    version = subprocess.check_output([str(args.lean), '--version'], text=True).strip()
    need('version 4.34.1,' in version, 'Lean 4.34.1 required')
    raw = (HERE/'Schur.lean').read_bytes()
    source = raw.decode('utf-8')
    bare = re.sub(r'/-.*?-/', '', source, flags=re.S)
    bare = re.sub(r'--[^\n]*', '', bare)
    need(not re.search(r'\b(sorry|admit|axiom|native_decide|implemented_by|unsafe)\b', bare), 'unsupported formal shortcut')
    mutations = {
        'wrong_reversed_inverse': ('(h : mul x y = one) : mul y x = one', '(h : mul x y = one) : mul y x = zero'),
        'zero_diagonal': ('(∀ i, m i i = one)', '(∀ i, m i i = zero)'),
        'drop_nontriviality': ('(hne : (0 : K) ≠ 1)', '(hne : True)'),
        'free_B_D': ('(i.val+2)%5 = j.val ∨ (j.val+2)%5 = i.val',
                     '((i.val+2)%5 = j.val ∨ (j.val+2)%5 = i.val) ∧ ¬ ((i = 1 ∧ j = 3) ∨ (i = 3 ∧ j = 1))')}
    with tempfile.TemporaryDirectory(prefix='paired-c5-lean-') as tmp:
        path = Path(tmp)/'Schur.lean'
        path.write_bytes(raw)
        good = run(args.lean, path)
        need(good.returncode == 0, good.stdout+good.stderr)
        reports = re.findall(r"'PairedC5\.([^']+)' depends on axioms: \[([^\]]*)\]", good.stdout)
        need(len(reports) == len(THEOREMS) and {name for name, _ in reports} == THEOREMS, 'exact formal theorem inventory')
        axioms = {}
        for name, report in reports:
            values = sorted(v.strip() for v in report.split(',') if v.strip())
            need(set(values) <= {'propext', 'Classical.choice', 'Quot.sound'}, 'unexpected axiom: '+name)
            axioms[name] = values
        for label, (old, new) in mutations.items():
            need(source.count(old) == 1, 'mutation target: '+label)
            path.write_text(source.replace(old, new), encoding='utf-8', newline='\n')
            bad = run(args.lean, path)
            need(bad.returncode != 0 and 'error' in bad.stdout, 'false statement/premise accepted: '+label)
    receipt = {'status': 'PASS_PAIRED_C5_LEAN', 'version': version,
               'source_sha256': sha256(raw).hexdigest(), 'theorem_axioms': axioms,
               'rejected_mutations': list(mutations),
               'scope': 'C5 normalized-four-pivot obstruction and integer one-edge-relaxed counterexample; no formal matrix rank bridge.'}
    if args.out:
        with args.out.open('x', encoding='utf-8') as stream:
            json.dump(receipt, stream, indent=2)
            stream.write('\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
