"""Directed additive-rank owned-MOVE packing upper on exact #7161."""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

PINS = {
    'OWNED.json': '08fd2af8ed7cc1ecab768674d984ce309ad861e8e8bfac1a8c510dbaa5ad74a8',
    'interval_gate.py': '60a743d13f668ef86db4b8215b4d5d04430a671ba6f1fe06d9c1c4c3dfe86da5',
}


def run(receipt_path, gate_path):
    raw = receipt_path.read_bytes()
    assert sha256(raw).hexdigest() == PINS['OWNED.json']
    assert sha256(gate_path.read_bytes()).hexdigest() == PINS['interval_gate.py']
    receipt = json.loads(raw)
    spec = spec_from_file_location('pinned_direct_sum_interval', gate_path)
    gate = module_from_spec(spec)
    spec.loader.exec_module(gate)
    assert receipt['head'] == 'e3f8d39c43b07063dfc5b800f71c5d21015259e6'
    target = Fraction(receipt['target'])
    assert target == Fraction('0.0040075385047236')
    hist = Counter({int(r): n for r, n in receipt['owned_rank_hist'].items()})
    assert hist == Counter(m['rank'] for m in receipt['owned'])
    sites = sum(hist.values())
    rank = sum(r*n for r, n in hist.items())
    stages = 17
    assert (sites, rank) == (47, 112)
    current = gate.smul(gate.moment(hist, target), stages)
    assert gate.show(current) == receipt['all_old_debits']
    signed = Counter(receipt['invoice']['T'])
    signed.subtract(receipt['invoice']['P'])
    baseline = gate.moment(signed, target)
    assert gate.show(baseline) == receipt['baseline']

    def bound(total_rank, packed_children):
        packed = gate.smul(gate.power(total_rank, target), packed_children)
        credit = gate.sub(current, packed)
        moment = gate.add(baseline, credit)
        return moment, dict(rank_per_child=total_rank, children=packed_children,
                            packed_debit=gate.show(packed), directed_credit=gate.show(credit),
                            directed_remaining_moment=gate.show(moment))

    native, native_record = bound(rank, stages)
    overall, overall_record = bound(stages*rank, 1)
    assert native[1] < 0 and overall[1] < 0
    fit, fit_record = bound(105, stages)
    miss, miss_record = bound(106, stages)
    assert fit[0] > 0 > miss[1]

    return dict(status='EXCLUDED_ADDITIVE_RANK_DIRECT_SUM', head=receipt['head'], pins=PINS,
                target=str(target), owned_rank_hist=hist, owned_sites_per_native=sites,
                native_invocations=stages, old_debit=gate.show(current), baseline=gate.show(baseline),
                one_per_native=native_record, one_across_all_natives=overall_record,
                same_rank_each_native_price_threshold=[fit_record, miss_record])


if __name__ == '__main__':
    assert __debug__, 'Run with assertions enabled'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('receipt_path', type=Path)
    parser.add_argument('gate_path', type=Path)
    print(json.dumps(run(**vars(parser.parse_args())), indent=2, sort_keys=True))
