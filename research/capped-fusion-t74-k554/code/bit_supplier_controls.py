"""Negative controls for the cited PR589 bit supplier and its derived rank-mass deficit.

Apache-2.0. Each control mutates one input of the changed bit-supplier sites in assemble.py (the pinned record, the
deficit derivation from the word's parameters, the profile/live binding, the claimed endpoint) and runs the unchanged
assemble() on the fresh owner/invoice receipts. Every control must be rejected; the unmutated run must pass.
`revert_hardcoded_9984` restores the PR543 constant the parent package hard-coded: with PR589's word it must fail.
"""
import argparse
import copy
import hashlib
import json
import os
import tempfile
from fractions import Fraction as Q
from pathlib import Path
import sys as _s,pathlib as _p;_s.path.insert(0,str(_p.Path(__file__).resolve().parent))

assert __debug__, 'Assertions required'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def verify(owner_path, invoice_path, source_package):
    os.environ['GAIN_PR564_SOURCE'] = str(source_package.resolve())
    import assemble as A
    owner = json.loads(owner_path.read_text())
    invoice = json.loads(invoice_path.read_text())
    args = (owner, invoice, sha(owner_path), sha(invoice_path))
    baseline = A.assemble(*args)
    data = A.BIT_PATH.read_bytes()
    record = A.load_bit(data)
    word = record['word']
    assert A.bit_deficit(word, record['nine']['bit']['live']) == 10272 == 32 * (8 * 111 - 9 * 63)

    real_load, real_deficit = A.load_bit, A.bit_deficit

    def with_record(mutate):
        def load(d):
            r = copy.deepcopy(real_load(d)); mutate(r); return r
        return load

    def shift_profile(r):  # one rank-1 child becomes rank 2: rank mass +1, totals unchanged
        p = r['nine']['profile']; p['1'] -= 1; p['2'] += 1; r['nine']['bit']['rank_mass'] += 1

    bumped = data.replace(record['nine']['bit_lower'].encode(),
                          str(Q(record['nine']['bit_lower']) + Q(1, 10**24)).encode(), 1)
    assert bumped != data
    pr543 = (source_package / 'inputs/PR543-EXPECTED.json').read_bytes()
    controls = [
        # deficit site: the parent's hard-coded constant, restored
        ('revert_hardcoded_9984', dict(bit_deficit=lambda w, live: 9984)),
        # deficit site: each word parameter perturbed alone
        ('ports_112', dict(load_bit=with_record(lambda r: r['word'].__setitem__('v', 112)))),
        ('decoder_constant_64_copy_ranks_unchanged', dict(load_bit=with_record(lambda r: r['word'].__setitem__('decoder_constant', 64)))),
        # v=111, cst=64 derives 32*(888-576)=9984: consistent word, wrong for the priced profile
        ('decoder_constant_64_with_one_copy_rank_8', dict(load_bit=with_record(lambda r: (r['word'].__setitem__('decoder_constant', 64), r['word']['copy_ranks'].__setitem__(0, 8))))),
        ('eight_retained_totals', dict(load_bit=with_record(lambda r: (r['word'].__setitem__('copy_ranks', [7] * 8), r['word'].__setitem__('decoder_constant', 56))))),
        ('live_minus_one', dict(load_bit=with_record(lambda r: r['nine']['bit'].__setitem__('live', r['nine']['bit']['live'] - 1)))),
        # profile binding: same totals, rank mass +1
        ('profile_rank_mass_plus_one', dict(load_bit=with_record(shift_profile))),
        ('profile_rank_mass_receipt_mismatch', dict(load_bit=with_record(lambda r: r['nine']['bit'].__setitem__('rank_mass', r['nine']['bit']['rank_mass'] + 1)))),
        # endpoint: the next 1e-24 grid point
        ('bit_lower_next_grid', dict(load_bit=with_record(lambda r: r['nine'].__setitem__('bit_lower', str(Q(r['nine']['bit_lower']) + Q(1, 10**24)))))),
        ('not_nine_stage_record', dict(load_bit=with_record(lambda r: r['nine'].__setitem__('pipeline', r['nine']['pipeline'].replace('nine-stage', 'eleven-stage'))))),
        # pinned-input site: tampered bytes and the parent's PR543 file under the PR589 pin
        ('tampered_bytes_next_grid', dict(read=bumped)),
        ('pr543_file_under_pr589_pin', dict(read=pr543)),
    ]
    rejected = []
    scratch = Path(tempfile.mkdtemp(prefix='bitctl-'))
    for name, patch in controls:
        saved_path = A.BIT_PATH
        try:
            if 'read' in patch:
                tmp = scratch / (name + '.json'); tmp.write_bytes(patch['read']); A.BIT_PATH = tmp
            A.load_bit = patch.get('load_bit', real_load)
            A.bit_deficit = patch.get('bit_deficit', real_deficit)
            try:
                A.assemble(*args)
            except (AssertionError, KeyError):
                rejected.append(name)
            else:
                raise AssertionError('Invalid bit supplier accepted: ' + name)
        finally:
            A.load_bit, A.bit_deficit, A.BIT_PATH = real_load, real_deficit, saved_path
            if 'read' in patch:
                tmp.unlink()
    scratch.rmdir()
    assert rejected == [n for n, _ in controls]
    again = A.assemble(*args)
    assert again['kappa'] == baseline['kappa'] and again['bit_lower'] == baseline['bit_lower']
    return dict(
        status='PASS_PR589_BIT_SUPPLIER_DERIVED_DEFICIT_NEGATIVE_CONTROLS',
        kappa=baseline['kappa_decimal'], bit_lower=baseline['bit_lower'], bit_decimal=baseline['bit_decimal'],
        binding=baseline['binding'], bit_supplier=baseline['bit_supplier'],
        derived_deficit=baseline['bit_supplier']['derived_deficit'],
        rejected_controls=rejected,
        assembler_sha256=sha(Path(__file__).resolve().parent / 'assemble.py'),
    )


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-package', type=Path, required=True)
    ap.add_argument('--owner', type=Path, required=True)
    ap.add_argument('--invoice', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    assert not a.out.exists()
    result = verify(a.owner, a.invoice, a.source_package)
    a.out.write_text(json.dumps(result, indent=2) + '\n', newline='\n')
    print(result['status'], len(result['rejected_controls']))
