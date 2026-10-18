#!/usr/bin/env python3
"""Exact finite witnesses for a conditional full-packet row-divisor theorem.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor Python executes. No physical supplier is simulated.
"""
import argparse
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
import hashlib
from itertools import product
import json
from math import lcm
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREDECESSOR_PIN = "082a6a3fbb3bae2370ad303df8d7851efcf300f87384ed7015b6b58bd180a268"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def integer(x, minimum=0):
    need(type(x) is int and x >= minimum, "invalid integer domain")


@dataclass(frozen=True)
class Packet:
    live: int
    low: int
    high: int

    def __post_init__(self):
        for x in (self.live, self.low, self.high):
            integer(x, 1)

    @property
    def size(self):
        return self.live * self.low * self.high

    def split(self, row, rows):
        integer(rows, 1)
        integer(row)
        need(row < rows and rows % self.size == 0, "incomplete live packet")
        unused = rows // self.size
        prefix, quotient = divmod(row, unused)
        prefix, high = divmod(prefix, self.high)
        family, low = divmod(prefix, self.low)
        return family, low, high, quotient

    def join(self, fields, rows):
        integer(rows, 1)
        need(rows % self.size == 0, "incomplete live packet")
        radices = (self.live, self.low, self.high, rows // self.size)
        need(len(fields) == 4, "wrong field count")
        value = 0
        for x, radix in zip(fields, radices):
            integer(x)
            need(x < radix, "field outside its complete range")
            value = value * radix + x
        return value


def path_split(packet, row, depth, multiplicity):
    integer(depth)
    integer(multiplicity, 1)
    integer(row)
    need(row < multiplicity * packet.size**depth, "path row outside range")
    fields = []
    for remaining in range(depth, 0, -1):
        a, b, c, row = packet.split(row, multiplicity * packet.size**remaining)
        fields.append((a, b, c))
    return tuple(fields), row


def path_join(packet, fields, tail, multiplicity):
    integer(tail)
    need(tail < multiplicity, "tail outside multiplicity")
    row = tail
    for level, triple in enumerate(reversed(fields), 1):
        row = packet.join((*triple, row), multiplicity * packet.size**level)
    return row


def depth(n):
    integer(n)
    answer = 0
    while n >= 64:
        n = 42 * (n // 64)
        answer += 1
    return answer


def validate_path_table(packet, d, t, table):
    triples = list(product(range(packet.live), range(packet.low), range(packet.high)))
    expected = set(product(product(triples, repeat=d), range(t)))
    need(len(table) == t * packet.size**d, "lost arbitrary input row")
    need(set(table) == expected, "incomplete or aliased descendant fibers")
    for row, fields in enumerate(table):
        need(path_join(packet, *fields, t) == row, "ancestor/row coordinate changed")


def layout_checks():
    rows_seen = cases = child_checks = 0
    for spec in ((2, 2, 1), (2, 2, 3), (3, 4, 1), (2, 6, 2)):
        p = Packet(*spec)
        for d in range(4):
            for t in (1, 2):
                count = t * p.size**d
                table = [path_split(p, row, d, t) for row in range(count)]
                validate_path_table(p, d, t, table)
                rows_seen += count
                cases += 1
                if d:
                    unused = count // p.size
                    for child_depth in range(d):
                        divisor = p.size**child_depth
                        need(unused % divisor == 0, "child reserve does not divide quotient")
                        expected = Counter({r: unused // divisor for r in range(divisor)})
                        for ancestor in product(range(p.live), range(p.low), range(p.high)):
                            got = Counter(p.split(p.join((*ancestor, u), count), count)[3] % divisor
                                          for u in range(unused))
                            need(got == expected, "fresh child range depends on ancestor")
                            child_checks += 1
    p = Packet(2, 2, 1)
    incompatible = [d for d in range(1, 9) if p.size**d % (3*p.low*p.high)**d]
    need(incompatible == list(range(1, 9)), "old physical-format gate silently retained")
    return dict(cases=cases, rows=rows_seen, child_fiber_checks=child_checks,
                incompatible_physical_depths=incompatible)


def depth_checks():
    checks = 0
    for n in range(64, 10001):
        for rank in range(1, 43):
            need(depth(rank*(n//64)) < depth(n), "selected child consumes too many levels")
            checks += 1
        for child in (n//64, (n//64)//2):
            need(depth(child) < depth(n), "fallback depth mismatch")
            checks += 1
    threshold = 64
    thresholds = []
    for d in range(1, 65):
        need(depth(threshold) == d and depth(threshold-1) == d-1,
             "inverse threshold boundary")
        thresholds.append(threshold)
        threshold = 64*((threshold+41)//42)
    return dict(widths=10001, all_child_checks=checks, threshold_pairs=len(thresholds),
                final_threshold=thresholds[-1])


def compatibility_checks():
    cases = common_reserves = selected_boundaries = 0
    # Rational reduction supplies a second route to the required multiplicity.
    for W, P, d, t, NH in product(range(1, 10), range(1, 14), range(7),
                                  range(1, 31), (1, 6, 15)):
        required = (Fraction(W, P)**d).denominator
        need(((t*(W*NH)**d) % (P*NH)**d == 0) == (t % required == 0),
             'two-format acceptance mismatch')
        cases += 1
        if t == 1:
            need(lcm((W*NH)**d, (P*NH)**d) == (lcm(W, P)*NH)**d,
                 'common fixed-format minimum mismatch')
            common_reserves += 1
    W, P, NH = 28416, 28425, 6
    for d in range(13):
        required = (Fraction(W, P)**d).denominator
        need(required == 9475**d, 'selected compatibility factor changed')
        for t in sorted({1, max(1, required-1), required, 2*required}):
            need(((t*(W*NH)**d) % (P*NH)**d == 0) == (t % required == 0),
                 'selected compatibility boundary')
            selected_boundaries += 1
    return dict(exact_equivalences=cases, common_reserve_identities=common_reserves,
                selected_depths=13, selected_boundaries=selected_boundaries,
                required_selected_multiplicity='9475^D')


def wrapper(row, h, d, modulus):
    # PR2234 ordinary wrapper, with an abstract row-uniform F_I on one atom.
    d = (d-h) % modulus
    h, d = d, h
    d = (d+h) % modulus
    h, d = d, h
    d = (h-d) % modulus
    return row, h, d


def restricted_payload(rows, genuine, radix, row_permutation=None):
    """Push distinct arbitrary symbols through the completed abstract endpoint."""
    source = {(r, h, d): ((r, h, d) if r < genuine else None)
              for r, h, d in product(range(rows), range(radix), range(radix))}
    output = {}
    for (r, h, d), value in source.items():
        rr, hh, dd = wrapper(r, h, d, radix)
        rr = rr if row_permutation is None else row_permutation[rr]
        output[rr, hh, dd] = value
    return {key: value for key, value in output.items() if key[0] < genuine}


def padding_and_work_checks():
    cases = symbols = 0
    for reserve in (1, 4, 12, 16, 144):
        for genuine in sorted({reserve, reserve+1, 2*reserve-1, 2*reserve+1}):
            rows = ((genuine+reserve-1)//reserve)*reserve
            need(genuine <= rows < 2*genuine and rows % reserve == 0, "padding bound")
            for radix in (2, 3, 5):
                got = restricted_payload(rows, genuine, radix)
                want = {(r, h, d): (r, d, h)
                        for r, h, d in product(range(genuine), range(radix), range(radix))}
                need(got == want, "completed endpoint does not preserve genuine rows")
                cases += 1
                symbols += len(want)
    dirty_source, dirty_target = frozenset({'s'}), frozenset({'t'})
    private = frozenset()
    private ^= dirty_source
    dirty_target ^= private
    private ^= dirty_source
    need(dirty_source == frozenset({'s'}) and dirty_target == frozenset({'s', 't'})
         and not private, "private copy/use/erase endpoint")
    W, P = 28416, 28425
    bills = []
    for N in (1, 2, 48):
        V = 7*W*N
        v = Fraction(V, W*N)
        occupied = V+4*v
        B0 = W+4
        parked = 5*occupied-v+9*B0-2
        need(parked == 5*V+19*v+9*B0-2, "parking bill was undercharged")
        need(P-W == 9 and B0 == 28420, "physical inventory changed")
        bills.append(dict(low_classes=N, logical_volume=V, packet_volume=int(v),
                          occupied=int(occupied), parking=int(parked)))
    return dict(padding_cases=cases, distinct_payload_symbols=symbols, work_bills=bills)


def controls():
    rejected = []
    def rejects(name, action):
        try:
            action()
        except (ValueError, TypeError):
            rejected.append(name)
        else:
            raise ValueError('accepted defect: '+name)
    p = Packet(2, 2, 3)
    valid = [path_split(p, r, 2, 1) for r in range(p.size**2)]
    rejects('omit_high_fibers', lambda: validate_path_table(p, 2, 1, valid[:16]))
    rejects('short_reserve', lambda: p.split(0, p.size**2-1))
    alias = list(valid); alias[-1] = alias[0]
    rejects('alias_one_dirty_row', lambda: validate_path_table(p, 2, 1, alias))
    swapped = list(valid); swapped[0], swapped[1] = swapped[1], swapped[0]
    rejects('multiset_only_row_restoration', lambda: validate_path_table(p, 2, 1, swapped))
    rows, genuine, radix = 8, 5, 2
    perm = list(range(rows)); perm[0], perm[7] = perm[7], perm[0]
    rejects('padded_row_leaks_into_genuine', lambda: need(
        restricted_payload(rows, genuine, radix, perm) ==
        restricted_payload(rows, genuine, radix), 'dummy leakage'))
    rejects('physical_live_denominator', lambda: need(Fraction(28416, 28425) == 1,
                                                     'P is not live W'))
    rejects('drop_physical_compatibility_factor', lambda: need(
        (28416*6)**2 % (28425*6)**2 == 0, 'missing 9475^D multiplicity'))
    rejects('private_starts_dirty', lambda: need(not (frozenset({'u'}) ^
        frozenset({'s'}) ^ frozenset({'s'})), 'private not erased'))
    rejects('erase_arbitrary_input_for_scratch', lambda: need(frozenset() ==
        frozenset({'u'}), 'arbitrary input lost'))
    rejects('omit_work_buffers', lambda: need(5*100-1+9*28420-2 ==
        5*(100+4)-1+9*28420-2, 'four buffers remain paid'))
    rejects('nonpositive_packet', lambda: Packet(0, 2, 3))
    rejects('boolean_cardinality', lambda: Packet(True, 2, 3))
    return rejected


def source_checks():
    raw = (HERE/'PREDECESSORS.json').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PREDECESSOR_PIN, 'predecessor manifest changed')
    manifest = json.loads(raw)
    need(len(manifest) == 6, 'incomplete predecessor inventory')
    for item in manifest:
        data = (HERE/item['path']).read_bytes()
        need(len(data) == item['bytes'], 'source size mismatch')
        need(hashlib.sha256(data).hexdigest() == item['sha256'], 'source SHA256 mismatch')
        need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
             == item['git_blob'], 'source Git blob mismatch')
    proof = (HERE/'sources/pr2195/PROOF.md').read_text()
    caller = (HERE/'sources/pr2234/PROOF.md').read_text()
    need('W=28,416 live families and P=W+9=28,425' in proof, 'live/work source binding')
    need('explicit alternative layout with an overreserve' in proof, 'predecessor scope binding')
    need('5V+19v+9B0-2' in caller, 'parking source binding')
    need('Allocate private and selector copies as work, not arbitrary input rows' in caller,
         'separate work source binding')
    return {'predecessor_files': len(manifest), 'executed_predecessor_code': False}


def certificate():
    return {'status':'PASS_SELECTED_LIVE_ROW_DIVISOR', 'scope':'conditional fixed-format theorem; no_new_kappa',
            'selected': {'live':28416, 'physical':28425, 'private_inventory':9,
                         'old_lcm':lcm(28416,28425), 'removed_factor_per_depth':lcm(28416,28425)//28416,
                         'new_packet':'28416*|GL64(F_q)|*q^(4096*(w-1))'},
            'sources':source_checks(), 'layouts':layout_checks(), 'depth':depth_checks(),
            'compatibility':compatibility_checks(),
            'padding_and_work':padding_and_work_checks(), 'rejected_controls':controls()}


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write-receipt', type=Path)
    args = ap.parse_args()
    result = certificate()
    if args.write_receipt:
        with args.write_receipt.open('x') as stream:
            stream.write(json.dumps(result, indent=2)+'\n')
    else:
        need(canonical(result) == canonical(json.loads((HERE/'RESULT.json').read_text())),
             'stored receipt differs from exact replay')
    print(json.dumps(result, indent=2))
    print('PASS_SELECTED_LIVE_ROW_DIVISOR factor=9475^D no_new_kappa')


if __name__ == '__main__':
    main()
