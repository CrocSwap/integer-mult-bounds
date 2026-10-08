"""Screen dimensions admitted by the regular intersection-graph matching.

Counts are exact circuit checks; saving estimates are exploratory floats.
Uses the attributed, unchanged PR #7 producer and PR #9 template rules.
"""
from collections import Counter
from pathlib import Path
from math import comb, log, log1p
import argparse
import json
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'research/prime-field-followup'
sys.path[:0] = [str(SOURCE), str(SOURCE/'vendor'), str(ROOT/'scripts')]
from prime_field_circuit import export_local, canonical, optimize
from star_duality import alternative_greedy, check


def screen(h):
    assert 8 <= h <= 32
    folder = ROOT / 'build/geometric-dimensions' / str(h)
    folder.mkdir(parents=True, exist_ok=True)
    binary = folder.parent / 'check'
    local, demands, selected = [folder / name for name in ('local.bin', 'demands.txt', 'templates.bin')]
    local_result = export_local(local, n=h-2)
    print(json.dumps(dict(h=h, local=local_result)), flush=True)
    first = subprocess.run([str(binary), str(local), '-', str(demands)], check=True, capture_output=True, text=True)
    original = json.loads(first.stdout)
    original.pop('seconds', None)
    counts = Counter()
    for line in demands.read_text().splitlines():
        core, old, *masks = map(int, line.split())
        counts[canonical(core, masks, h)] += 1
    records, gates_by_targets = [], {}
    for targets, multiplicity in sorted(counts.items()):
        masks = list(targets)
        choices = {'published': optimize(masks),
                   'large': alternative_greedy(masks, large=True),
                   'large_reverse': alternative_greedy(masks, large=True, reverse=True)}
        winner = min(choices, key=lambda name: (len(choices[name]), name))
        gates = choices[winner]
        check(masks, gates)
        gates_by_targets[targets] = gates
        records.append(dict(multiplicity=multiplicity, winner=winner,
                            additions={name: len(gs) for name, gs in choices.items()}))
    with selected.open('wb') as stream:
        def words(*xs):
            stream.write(struct.pack('<'+'I'*len(xs), *xs))
        words(h, len(gates_by_targets))
        for targets, gates in sorted(gates_by_targets.items()):
            words(len(targets), len(gates), *targets)
            for a, b in gates:
                words(a, b)
    second = subprocess.run([str(binary), str(local), '-', str(folder/'repeated.txt'), str(selected)], check=True, capture_output=True, text=True)
    repeated, checked = map(json.loads, second.stdout.splitlines())
    repeated.pop('seconds', None)
    assert repeated == original
    assert demands.read_bytes() == (folder/'repeated.txt').read_bytes()
    roles = checked['role_upper_bound']
    v, m = comb(h, 5), h**3
    deficit = v - 6*comb(h, 2)*(h-2)
    eta = deficit/(2*(v+roles)*m)
    result = dict(h=h, local=local_result, original=original, checked=checked,
                  templates=records, v=v, m=m, deficit_per_v_squared=deficit,
                  eta=eta, estimated_bit_saving=-log1p(-eta)/log(m),
                  status='EXACT CIRCUIT SCREEN; NO NEW ASSEMBLED WITNESS')
    (folder/'result.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('local','original','templates')}), flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dimensions', nargs='+', type=int)
    for h in parser.parse_args().dimensions:
        screen(h)
