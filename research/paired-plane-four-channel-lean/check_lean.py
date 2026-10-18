#!/usr/bin/env python3
"""Fresh isolated Lean 4.34.1 build; explicit axiom inventory and controls.
Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
SOURCES = ('Algebra.lean', 'Schur.lean', 'Pivot.lean')
NAMES = {'Four.det_mul', 'Four.adj_left', 'Four.reverse_inverse',
         'PairedC5.reverse_inverse', 'PairedC5.no_four_pivot',
         'PairedC5.relaxed_diagonal', 'PairedC5.relaxed_remaining_zeros',
         'PairedC5.relaxed_four_pivot', 'PairedC5.relaxed_missing_edge',
         'Pivot.factor_to_pivot', 'Pivot.no_four_channels',
         'Pivot.relaxed_through_four'}
CONTROLS = {
    'reverse_inverse_wrong_conclusion':
        ('(h : mul a b = one) : mul b a = one', '(h : mul a b = one) : mul b a = scale 0 one'),
    'pivot_nonzero_cross_block':
        ('(h02 : m 0 2 = zero)', '(h02 : m 0 2 = one)'),
    'remove_ring_nontriviality':
        ('(hne : (0 : K) ≠ 1)', '(hne : True)'),
    'relaxed_factor_zero_channels':
        ('if (group i && k.val == 0)', 'if (group i && k.val == 9)'),
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lean', required=True, type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    lean = args.lean.resolve()
    version = subprocess.check_output([str(lean), '--version'], text=True).strip()
    need('version 4.34.1,' in version, 'Lean4.34.1 required')
    raw = {name: (HERE/name).read_bytes() for name in SOURCES}
    with tempfile.TemporaryDirectory(prefix='four-channel-lean-') as tmp:
        work = Path(tmp)
        for name, data in raw.items():
            (work/name).write_bytes(data)
        # A private module directory prevents accidentally using an old .olean.
        env = dict(os.environ, LEAN_PATH=str(work))

        def run(name, compile_module=False):
            command = [str(lean), '-j1']
            if compile_module:
                command += ['-o', str(work/(Path(name).stem+'.olean'))]
            return subprocess.run(command+[str(work/name)], cwd=work, env=env,
                                  capture_output=True, text=True, encoding='utf-8',
                                  timeout=900 if name == 'Algebra.lean' else 120)

        output = ''
        for name in SOURCES:
            result = run(name, compile_module=True)
            need(result.returncode == 0, result.stdout+result.stderr)
            output += result.stdout
        reports = re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", output)
        need(len(reports) == len(NAMES) and {n for n, _ in reports} == NAMES,
             'exact theorem inventory missing or duplicated')
        axioms = {}
        for name, report in reports:
            values = sorted(v.strip() for v in report.split(',') if v.strip())
            need(set(values) <= {'propext', 'Classical.choice', 'Quot.sound'},
                 'unsupported axiom: '+name)
            axioms[name] = values
        source = raw['Pivot.lean'].decode('utf-8')
        for label, (old, new) in CONTROLS.items():
            need(source.count(old) == 1, 'mutation target: '+label)
            (work/'Mutation.lean').write_text(source.replace(old, new), encoding='utf-8', newline='\n')
            bad = run('Mutation.lean')
            need(bad.returncode != 0 and 'error:' in bad.stdout,
                 'mutation did not fail compilation: '+label)
    receipt = {'status': 'PASS_FOUR_CHANNEL_LEAN', 'version': version,
               'source_sha256': {name: sha256(data).hexdigest() for name, data in raw.items()},
               'theorem_axioms': axioms, 'rejected_mutations': list(CONTROLS),
               'scope': 'Four-channel factorization implies normalized pivot; no strict C5 fitting factorization. Ordinary rank and selected-mask embedding remain external.'}
    if args.out:
        with args.out.open('x', encoding='utf-8') as stream:
            json.dump(receipt, stream, indent=2)
            stream.write('\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
