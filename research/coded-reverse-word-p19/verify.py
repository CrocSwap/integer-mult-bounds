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

    bank = HERE/'P19_BANK.json'
    need(bank.exists(), 'the address-level replay receipt is missing (run p19_bank.py)')
    bk = json.loads(bank.read_text())
    need(bk['status'] == 'PASS_ADDRESS_LEVEL_TRACE_REPLAY' and sum(bk['differing_entries']) == 0,
         'the gate list realises the controller matrix at address level')
    print('PASS binding: p=%d address-level replay, %d addresses per role, %d roles, %d gates, 0 differing entries'
          % (bk['p'], bk['addresses_per_role'], bk['roles'], bk['gates']))

    need('CLAIM kappa' in run('research/coded-reverse-word-p19/p19_claim.py'), 'claim checker')
    claim = json.loads((HERE/'P19_CLAIM.json').read_text())
    need(claim['status'] == 'CLAIM_P19_UNCODED_WORD_SUPPLIER', 'claim status')
    need(claim['kappa'] == '951999/280000000', 'claim value')
    need(claim['gain_vs_selected_record_percent'] > 12.5 and claim['gain_vs_reported_percent'] > 12.3,
         'both gains are recorded')
    need(claim['compiler']['H0'] == 5170423668736, 'compiler ranks')
    bill = claim['field_level_bill']
    need(all(bill[k] == 0 for k in ('recodings', 'monomial_field_maps', 'scalar_adds',
                                    'owned_clears', 'terminal_gauge_decoder')),
         'the emitted claim carries a zero field bill')
    need(claim['uncoded_word']['gates'] == 241 and claim['uncoded_word']['gate_kinds']['LETTER'] == 39,
         'the emitted claim describes the uncoded word')
    need(claim['record_only_overlay']['status'].startswith('historical record'),
         'the coded overlay is labelled a record')
    need('not a proof' in claim['compiler']['classification'], 'the compiler stays conditional')
    print('PASS_P19_UNCODED_WORD_SUPPLIER kappa %s: +%.2f%% over the selected record, +%.2f%% over the reported '
          'frontier; complex %s, BIT %s, compiler H0 = %s, field bill all zero'
          % (claim['kappa'], claim['gain_vs_selected_record_percent'],
             claim['gain_vs_reported_percent'], claim['complex_supplier'],
             claim['bit_supplier'], claim['compiler']['H0']))
    print(json.dumps({'status': 'PASS_P19_UNCODED_WORD_SUPPLIER', 'kappa': claim['kappa'],
                      'gain_vs_selected_record_percent': claim['gain_vs_selected_record_percent'],
                      'gain_vs_reported_percent': claim['gain_vs_reported_percent'],
                      'field_level_bill': 'all zero'}, sort_keys=True))

if __name__ == '__main__':
    main()
