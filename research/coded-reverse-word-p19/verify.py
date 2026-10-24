#!/usr/bin/env python3
"""Fast receipt for the p=19 uncoded-word supplier.

Runs the formal controller verifier, checks the p=19 diagonalisation receipt, then
the two package receipts: P19_PLAIN.json (the trace-certified word, its census and
the absence of a recoding bill) and P19_CLAIM.json (the price, guards, compiler,
BIT chain, budgets and outer ledger).  The long traces are the separate commands
p19_plain.py and p19_word.py.
"""
import json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OWNERS, SIZE = 112, 512

def need(ok, why):
    if not ok: raise ValueError(why)

def run(path, timeout=900):
    p = subprocess.run([sys.executable, '-I', '-B', str(ROOT/path)], cwd=ROOT,
                       capture_output=True, text=True, timeout=timeout)
    sys.stdout.write(p.stdout)
    sys.stderr.write(p.stderr)
    need(p.returncode == 0, 'subprocess failed: '+path)
    return p.stdout + p.stderr

def main():
    out1 = run('research/coded-reverse-controller/verify.py')
    need('PASS p=19 tail guards at C=0.0034' in out1, 'p=19 tail guards')
    need('0.007579' in out1, 'p=19 raw complex root')
    need('PASS p=2, 448x448' in out1, 'p=2 448x448 conjugation')
    need('at 0.0034 the only failing predicate is the BIT cap' in out1, 'outer ledger')
    diag = json.loads((HERE/'P19_DIAG.json').read_text())
    need(diag['diagonalized'] is True and diag['std']['outputs'] == diag['cod']['outputs']
         and diag['std']['denominators'] == [1], 'p19 diagonalization receipt')
    print('PASS formal controller: p=19 diagonalisation, guards, raw root and outer ledger')

    plain = json.loads((HERE/'P19_PLAIN.json').read_text())
    pw = plain['p19']
    need(plain['status'] == 'PASS_P19_UNCODED_WORD', 'word receipt status')
    need(pw['trace_identity'] == 'replayed in the controller algebra', 'trace identity')
    need(pw['denominators'] == [1], 'standard denominators')
    need((pw['retained_idles'], pw['idle_rank']) == (36, 198), 'idle census')
    need(pw['gates'] == 241 and pw['kinds']['LETTER'] == 39 and pw['kinds']['IDLE'] == 36, 'gate census')
    need((pw['recodings'], pw['terminal_gauge_decoder']) == (0, 0), 'no recoding bill')
    need(abs(pw['invoice_root'] - 0.007578535189897761) < 1e-9 and pw['ambient_rank'] == 153, 'price')
    print('PASS word: p=19 trace == controller, diagonalises with denominators [1], %d gates, '
          '%d retained idles, root %.12f, no recoding bill'
          % (pw['gates'], pw['retained_idles'], pw['invoice_root']))

    need('CLAIM kappa' in run('research/coded-reverse-word-p19/p19_claim.py'), 'claim checker')
    claim = json.loads((HERE/'P19_CLAIM.json').read_text())
    need(claim['status'] == 'CLAIM_P19_UNCODED_WORD_SUPPLIER', 'claim status')
    need(claim['kappa'] == '951999/280000000' and claim['gain_percent'] > 12.3, 'claim value')
    need(claim['compiler']['H0'] == 5170423668736, 'compiler ranks')
    print('PASS_P19_UNCODED_WORD_SUPPLIER kappa %s (+%.2f%% over %s): complex %s, BIT %s, '
          'compiler H0 = %s, zero recodings'
          % (claim['kappa'], claim['gain_percent'], claim['frontier'], claim['complex_supplier'],
             claim['bit_supplier'], claim['compiler']['H0']))
    print(json.dumps({'status': 'PASS_P19_UNCODED_WORD_SUPPLIER', 'kappa': claim['kappa'],
                      'gain_percent': claim['gain_percent'],
                      'complex_supplier': claim['complex_supplier'],
                      'bit_supplier': claim['bit_supplier']}, sort_keys=True))

if __name__ == '__main__':
    main()
