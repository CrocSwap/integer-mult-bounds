#!/usr/bin/env python3
"""Bank-absorption schedule for the rank-22 residual family on the PR200/PR205 bit word.

Everything here is exact integer / rational arithmetic on pinned inputs:
the enumerated rank-22 increment occurrences (inputs/absorbed-occurrences.json),
PR200's bit certificate (references/pr200-bit.certificate.json) and PR205's packed
certificate (references/pr205-packed.certificate.json).

What this builds (all machine-checked here):
  * the absorbed family's exact inventory, with chain/frame provenance;
  * the whole-bank volume condition and the bank count it implies;
  * the retained child ledger and the row identity W*m - mass = D;
  * candidate block tilings of width m=72 mixing the word's residual families
    (4 and 24) with the new 22-blocks, and the divisibility of their patterns.

What this does NOT build: the physical realization of the new residual type
(formal columns, charts, normalizers, routing, prime witnesses). See
obligations.json and PROOF.md.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

M = 72
NEW_RANK = 22


def _int(x):
    assert isinstance(x, int)
    return x


def build():
    occ = json.loads((HERE / 'inputs/absorbed-occurrences.json').read_text())
    bit = json.loads((HERE / 'references/pr200-bit.certificate.json').read_text())['bit']
    pack = json.loads((HERE / 'references/pr205-packed.certificate.json').read_text())['physical']

    # --- 1. inventory of the absorbed family -----------------------------------
    per_vertex = occ['counts_per_vertex']
    counts = {
        'physical_internal_chain_jumps': len(occ['occurrences_per_vertex']['H']),
        'copied_centre_children': len(occ['occurrences_per_vertex']['H_center']),
        'physical_target_jumps': len(occ['occurrences_per_vertex']['Y']),
        'source_chain_jumps': len(occ['occurrences_per_vertex']['src']),
    }
    listed = sum(counts.values())
    assert listed == per_vertex['physical_internal_H'] + per_vertex['physical_target_Y'] \
        + per_vertex['source_chain_src'] == 2224, counts
    hist = {int(r): int(n) for r, n in bit['profile']['child_histogram'].items()}
    assert hist[NEW_RANK] == per_vertex['ledger_bin_22_per_vertex'] == 3 * listed, hist[NEW_RANK]
    normalization = 3
    occurrences = normalization * hist[NEW_RANK]           # 20,016 three-copy normalization
    volume = NEW_RANK * occurrences                        # 440,352 registers of dirt

    # --- 2. whole-bank volume condition ---------------------------------------
    assert volume % M == 0, 'absorbed volume must fill whole banks'
    banks = volume // M                                     # 6,116
    assert banks == 6116

    # --- 3. retained ledger and row identity ----------------------------------
    kept = {int(r): int(n) for r, n in pack['child_histogram'].items()}
    assert kept[NEW_RANK] == occurrences
    kept.pop(NEW_RANK)
    mass_before = int(pack['rank_mass'])
    assert sum(r * n for r, n in {int(r): int(n) for r, n in pack['child_histogram'].items()}.items()) == mass_before
    mass = mass_before - volume
    D = int(pack['deficit'])
    W = int(pack['W'])
    W_new = (mass + D) // M
    assert M * W_new == mass + D, 'row identity after absorption'
    assert W_new == W - banks == 50286
    assert sum(r * n for r, n in kept.items()) == mass
    assert max(kept) == 21

    # --- 4. block tilings of the bank width -----------------------------------
    # A bank is a coordinate-block partition of width 72. The word's own residual
    # families are 4 and 24; the new type contributes 22-blocks. Every tiling of 72
    # over {4, 24, 22} using at least one 22-block:
    patterns = []
    for c in range(1, 4):
        for b in range(0, 4):
            for a in range(0, 19):
                if 4 * a + 24 * b + 22 * c == 72:
                    patterns.append(dict(rank4=a, rank24=b, rank22=c, blocks=a + b + c))
    patterns.sort(key=lambda p: (p['rank22'], p['rank4'], p['rank24']))
    assert patterns, 'no certified-shape tiling'
    # Divisibility of the absorbed occurrence count under uniform 22-block banks:
    uniform22 = [dict(pattern=p, exact_full_banks=(occurrences % p['rank22'] == 0),
                      banks_if_pattern=occurrences / p['rank22'] if occurrences % p['rank22'] == 0 else None)
                 for p in patterns]
    fills = [u for u in uniform22 if u['exact_full_banks']]
    assert fills, 'no pattern divides the absorbed occurrence count'

    schedule = {
        'status': 'bank-absorption schedule, accounting and tiling invariants; '
                  'no physical column, chart or prime witness is built here',
        'absorbed_family': {
            'rank': NEW_RANK,
            'provenance_counts_per_vertex': counts,
            'ledger_bin_per_vertex': hist[NEW_RANK],
            'normalization_factor': normalization,
            'occurrences_three_copies': occurrences,
            'dirt_volume_registers': volume,
        },
        'banks': dict(width=M, banks_from_volume=banks, volume=M * banks,
                      whole_bank_condition=True),
        'retained_profile': dict(m=M, W_before=W, W_after=W_new, deficit=D,
                                rank_mass_before=mass_before, rank_mass_after=mass,
                                children_before=int(pack['children']) if 'children' in pack else sum(
                                    int(n) for n in pack['child_histogram'].values()),
                                children_after=sum(kept.values()),
                                maxchild=max(kept),
                                histogram={str(r): n for r, n in sorted(kept.items())}),
        'row_identity': dict(before=f'{M}*{W} - {mass_before} = {D}',
                             after=f'{M}*{W_new} - {mass} = {D}', stock_drop=W - W_new,
                             stock_drop_equals_banks=(W - W_new == banks)),
        'block_tilings': dict(patterns=patterns, uniform_22_block_banks=uniform22,
                              feasible_patterns=[u['pattern'] for u in fills]),
    }
    return schedule


if __name__ == '__main__':
    out = build()
    print(json.dumps(out, indent=1, sort_keys=True))
