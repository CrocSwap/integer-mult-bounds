#!/usr/bin/env python3
"""Differential verification of the complete checker and its exact cell logic."""
from collections import Counter
from contextlib import redirect_stdout
from copy import deepcopy
import gzip
import importlib.util
import io
import itertools
import json
from pathlib import Path
import random
import tempfile
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('footprint_adapter', HERE / 'adapter.py')
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
sweep_spec = importlib.util.spec_from_file_location('endpoint_sweep', HERE / 'sweep.py')
sweep = importlib.util.module_from_spec(sweep_spec)
sweep_spec.loader.exec_module(sweep)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def fragments(source):
    """Exercise the actual transformed expressions, not a second bitset kernel."""
    lines = source.splitlines()
    update = next(line for line in lines if "need(t in window" in line)
    update = update[update.index('need(t in window'):]
    compact = next(line for line in lines if "'compacted prefix'" in line)
    compact = compact.split(';', 1)[1]
    idle = next(line.strip() for line in lines if 'idle[cap-' in line)
    namespace = {'need': need, 'Counter': Counter,
                 'interval_mask': adapter.PR727.interval_mask, 'is_prefix': adapter.PR727.is_prefix}
    exec('def add(used, offset, w, cap):\n'
         " r={'offset':offset};key=0;t=0;window={0}\n " + update +
         '\n return used[0]\n'
         'def remainder(cells, cap):\n idle=Counter()\n ' + compact +
         '\n ' + idle + '\n return dict(idle)\n', namespace)
    return namespace['add'], namespace['remainder']


def outcome(function, *args):
    try:
        return ('accept', function(*args))
    except ValueError as exc:
        return ('reject', str(exc))


def exhaustive(source):
    add, remainder = fragments(source)
    cases = 0
    for cap in range(8):
        for mask in range(1 << cap):
            occupied = [i for i in range(cap) if mask >> i & 1]
            # A boolean occupancy vector supplies an independent finite oracle.
            for offset, width in itertools.product(range(-1, cap + 2), repeat=2):
                actual = outcome(add, {0: mask}, offset, width, cap)
                if not 0 <= offset <= offset + width <= cap:
                    expected = ('reject', 'window and footprint')
                elif any(i in occupied for i in range(offset, offset + width)):
                    expected = ('reject', 'disjoint footprints')
                else:
                    expected = ('accept', sum(1 << i for i in range(cap)
                                              if i in occupied or offset <= i < offset + width))
                need(actual == expected, f'Interval mismatch: {(cap, mask, offset, width)}')
                swept = outcome(sweep.span_count, [(i, 1) for i in occupied] + [(offset, width)], cap)
                if expected[0] == 'reject':
                    need(swept == expected, 'Sweep rejection differs')
                else:
                    cells = sorted(set(occupied) | set(range(offset, offset + width)))
                    need(swept == ('accept', (len(cells), cells == list(range(len(cells))))),
                         'Sweep cardinality or compactness differs')
                cases += 1
            expected = (('accept', {cap - len(occupied): 1} if len(occupied) < cap else {})
                        if occupied == list(range(len(occupied)))
                        else ('reject', 'compacted prefix'))
            need(outcome(remainder, mask, cap) == expected, f'Prefix mismatch: {(cap, mask)}')
            cases += 1
    return cases


def full_run(engine, output):
    with redirect_stdout(io.StringIO()):
        return adapter.execute(engine, output)


def main():
    adapter.check_pins()
    reference = adapter.checker_source('reference')
    candidate = adapter.checker_source('bitset')
    cases = exhaustive(candidate)
    mutations = {
        'interval endpoint': candidate.replace("interval_mask(r['offset'],w)", "interval_mask(r['offset'],w+1)"),
        'interval origin': candidate.replace("interval_mask(r['offset'],w)", "interval_mask(r['offset']+1,w)"),
        'omit overlap': candidate.replace("need(not used[key]&cells,'disjoint footprints')", 'pass'),
        'omit compactness': candidate.replace("need(is_prefix(cells),'compacted prefix')", 'need(True,\'compacted prefix\')'),
        'undercharge remainder': candidate.replace('idle[cap-cells.bit_count()]', 'idle[cap-cells.bit_count()+1]'),
    }
    for label, mutant in mutations.items():
        need(mutant != candidate, 'Inactive mutation: ' + label)
        need(outcome(exhaustive, mutant)[0] == 'reject', 'Undetected mutation: ' + label)

    with tempfile.TemporaryDirectory(prefix='owner-footprint-') as directory:
        directory = Path(directory)
        ref_output, bit_output = directory / 'reference.json', directory / 'bitset.json'
        ref = full_run('reference', ref_output)
        bit = full_run('bitset', bit_output)
        need(ref_output.read_bytes() == bit_output.read_bytes(), 'Complete receipts differ')
        need(bit_output.read_bytes() == (HERE / 'OWNER-CHECK.json').read_bytes(),
             'Committed exact receipt differs')
        need(ref['used'].keys() == bit['used'].keys(), 'Owner keys differ')
        swept_counts, swept_idle = sweep.recount(ref['roles'], ref['plan']['windows'])
        need(swept_idle == ref['idle'], 'Independent sweep idle histogram differs')
        for key, cells in ref['used'].items():
            need(sum(1 << i for i in cells) == bit['used'][key], 'Occupied cells differ')
            need(len(cells) == swept_counts[key], 'Independent per-owner cardinality differs')
        for key in ('helpers', 'families', 'widths_by_pid', 'paid_by_pid', 'paid', 'idle', 'costs'):
            need(ref[key] == bit[key], 'Complete checker state differs: ' + key)

        # Large offsets test arbitrary-precision semantics beyond the selected cap 48.
        ref_add, ref_rem = fragments(reference)
        bit_add, bit_rem = fragments(candidate)
        rng = random.Random(89)
        for _ in range(500):
            cap = rng.choice((48, 63, 64, 65, 127, 128, 129, 256, 1024))
            ref_used, bit_used = {0: set()}, {0: 0}
            for _ in range(12):
                offset, width = rng.randrange(-1, cap + 2), rng.randrange(-1, 12)
                a = outcome(ref_add, ref_used, offset, width, cap)
                b = outcome(bit_add, bit_used, offset, width, cap)
                need(a[0] == b[0] and (a[0] == 'accept' or a == b), 'Sequence rejection differs')
                need(sum(1 << i for i in ref_used[0]) == bit_used[0], 'Sequence state differs')
            need(outcome(ref_rem, ref_used[0], cap) == outcome(bit_rem, bit_used[0], cap),
                 'Sequence remainder differs')

        roles = ref['roles']
        plan = ref['plan']
        groups = {}
        for index, role in enumerate(roles):
            key = role['owner_replica'], role['child'], role['port']
            groups.setdefault(key, []).append(index)
        repeated = next(v for v in groups.values() if len(v) > 1)
        overlap_index, other = repeated[1], repeated[0]
        gap_index = next(max(indices, key=lambda i: roles[i]['offset'])
                         for (rep, child, _), indices in groups.items()
                         if max(roles[i]['offset'] + roles[i]['width'] for i in indices)
                         < plan['windows'][f'{rep},{child}'][0])
        chosen = rng.randrange(len(roles))
        role = roles[chosen]
        cap = plan['windows'][f"{role['owner_replica']},{role['child']}"][0]
        changes = {
            'overlap': (overlap_index, {'offset': roles[other]['offset']}, 'disjoint footprints'),
            'gap': (gap_index, {'offset': roles[gap_index]['offset'] + 1}, 'compacted prefix'),
            'negative offset': (chosen, {'offset': -1}, 'window and footprint'),
            'beyond capacity': (chosen, {'offset': cap - role['width'] + 1}, 'window and footprint'),
            'width': (chosen, {'width': role['width'] + 1}, 'actual width'),
            'family': (chosen, {'family': 10**9}, 'physical family'),
            'copy': (chosen, {'copy': -1}, 'copy'),
            'stage': (chosen, {'stage': -1}, 'ordered complete call'),
            'missing role': (None, {}, 'all helper calls'),
        }
        owner_bytes = gzip.decompress((adapter.SOURCE.parents[1] / 'data/OWNERS.json.gz').read_bytes())
        real_loads = json.loads
        for label, (index, fields, message) in changes.items():
            changed = deepcopy(roles)
            if index is None:
                changed.pop()
            else:
                changed[index].update(fields)

            if label in ('overlap', 'gap', 'negative offset', 'beyond capacity'):
                need(outcome(sweep.recount, changed, plan['windows']) == ('reject', message),
                     'Independent sweep missed footprint corruption')

            def altered_loads(data, *args, **kwargs):
                # Mutate after loading to reach mathematics rather than the byte-pin guard.
                return changed if data == owner_bytes else real_loads(data, *args, **kwargs)

            for engine in ('reference', 'bitset'):
                output = directory / f'{engine}-{label}.json'
                with patch.object(json, 'loads', altered_loads):
                    actual = outcome(full_run, engine, output)
                need(actual == ('reject', message), f'{engine}: wrong rejection for {label}: {actual[0]}')
                need(not output.exists(), 'Rejected input produced a receipt')

        original_read = Path.read_bytes
        for relative in ('research/complex-k492-owner-repair/extras/check_owner_map.py',
                         'research/complex-k492-owner-repair/extras/exact_intervals.py',
                         'research/complex-k492-owner-repair/data/OWNERS.json.gz',
                         'research/community-k492-audit/pr622/replay/ck-local/LOCAL-PROGRAMS.json.gz'):
            target = adapter.ROOT / relative

            def corrupted(path):
                data = original_read(path)
                return data + b'\n' if path == target else data

            with patch.object(Path, 'read_bytes', corrupted):
                need(outcome(adapter.check_pins) == ('reject', 'Pinned input changed: ' + relative),
                     'Source drift was not rejected')
        need(outcome(full_run, 'bitset', bit_output)[0] == 'reject', 'Existing output overwritten')
        print(f'PASS_OWNER_FOOTPRINT_CROSSCHECK roles={len(roles)} owners={len(ref["used"])} '
              f'exhaustive={cases} sequence_steps=6000 checker_controls={len(changes)} '
              f'kernel_mutations={len(mutations)} pin_controls=4 sweep_owners={len(swept_counts)}')


if __name__ == '__main__':
    main()
