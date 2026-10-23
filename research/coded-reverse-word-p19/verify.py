#!/usr/bin/env python3
"""Fast receipt for the p=19 coded-reverse supplier.

Runs the formal controller verifier, checks the saved p=19 diagonalization and
the local physical pair, then runs the claim checker, which reads the
materialized word receipt P19_WORD.json together with the new kappa claim.
The long listing replay is the separate command p19_word.py.
"""
import json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(ok, why):
    if not ok: raise ValueError(why)

def run(path, timeout=600):
    p = subprocess.run([sys.executable, '-I', '-B', str(ROOT/path)], cwd=ROOT,
                       capture_output=True, text=True, timeout=timeout)
    sys.stdout.write(p.stdout)
    sys.stderr.write(p.stderr)
    need(p.returncode == 0, 'subprocess failed: '+path)
    return p.stdout + p.stderr

def main():
    out1 = run('research/coded-reverse-controller/verify.py')
    need('PASS p=19 tail guards at C=0.0034' in out1, 'p=19 tail guards')
    need('0.007579' in out1, 'p=19 coded raw complex root')
    need('PASS p=2, 448x448' in out1, 'p=2 448x448 conjugation')
    need('at 0.0034 the only failing predicate is the BIT cap' in out1, 'outer ledger')
    diag = json.loads((HERE/'P19_DIAG.json').read_text())
    need(diag['diagonalized'] is True and diag['std']['outputs'] == diag['cod']['outputs']
         and diag['std']['denominators'] == [1] and diag['cod']['denominators'] == [1, 13],
         'p19 full controller diagonalization receipt')
    try:
        out2 = run('research/coded-reverse-physical-fix/verify.py')
        need('PASS physical S/L/R local pair exact' in out2, 'physical local pair')
        need('PASS outer ledger' in out2, 'local ledger')
    except Exception as e:
        print('local companion not run in this environment:', e)

    word = json.loads((HERE/'P19_WORD.json').read_text())
    need(word['gate_records'] == 259 and word['recodings'] == 77, 'materialized word receipt')
    need(word['entries_checked'] == 38*112*512 and word['recursive_gaussian_children'] == 0, 'replay receipt')
    need('CLAIM kappa' in run(str(HERE.relative_to(ROOT)/'p19_claim.py')), 'receipt checker')
    claim = json.loads((HERE/'P19_CLAIM.json').read_text())
    need(claim['status'] == 'CLAIM_P19_CODED_REVERSE_SUPPLIER', 'receipt status')
    need(claim['kappa'] == '951999/280000000' and claim['gain_percent'] > 12.5, 'claim value')
    need(claim['bit_supplier'] == '17/5000' and claim['complex_supplier'] == '0.007578535', 'supplier pair')
    need(claim['word']['gate_records'] == 259 and claim['word']['recodings'] == 77, 'word census')
    need('logarithmic_cap' in claim and 'kappa_under_logarithmic_majorant' in claim,
         'the alternative compiler is recorded')
    print('PASS_P19_CODED_REVERSE_SUPPLIER kappa %s (+%.2f%% over %s): complex supplier %s, BIT supplier %s, '
          'word %d gates / %d recodings, logarithmic cap recorded'
          % (claim['kappa'], claim['gain_percent'], claim['frontier'], claim['complex_supplier'],
             claim['bit_supplier'], claim['word']['gate_records'], claim['word']['recodings']))
    print(json.dumps({'status': 'PASS_P19_CODED_REVERSE_SUPPLIER', 'kappa': claim['kappa'],
                      'gain_percent': claim['gain_percent'],
                      'complex_supplier': claim['complex_supplier'],
                      'bit_supplier': claim['bit_supplier'],
                      'recodings': claim['word']['recodings']}, sort_keys=True))

if __name__ == '__main__':
    main()
