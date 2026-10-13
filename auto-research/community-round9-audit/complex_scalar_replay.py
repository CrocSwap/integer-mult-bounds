#!/usr/bin/env python3
"""Exact all-column scalar check of PR210's retained five-stage complex helper.

This checks the literal scalar schedule with recursive calls replaced by the
identity, as appropriate to the scalar contract. It does not check the address
frames, the recursive operators, or the analytic transfer theorem.
Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time


def need(ok, message):
    if not ok:
        raise ValueError(message)


def replay(package, direction):
    path = package / 'code/complex_scalars.py'
    spec = importlib.util.spec_from_file_location('submitted_complex_schedule', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = package / 'inputs/complex/gcert1-p11-pr193.json.gz'
    c = json.loads(gzip.decompress(source.read_bytes()))
    n, v = 2*c['v']+c['R'], c['v']
    need((n, v) == (12052, 1320), 'Unexpected source')
    events = list(module.inv_schedule(direction, module.flat(c['A']), module.flat(c['B']), c))

    def execute(initial, absolute=False, omit=None):
        # A row is an integer numerator vector / (2**u * 3**v). The same
        # denominator updates work for its packed encoding and its L1 majorant.
        rows = dict(initial)
        maxima = [0, 0, 0]
        for index, (_, event) in enumerate(events):
            if index == omit:
                continue
            op = event[0]
            if op == 'recursive_center':
                continue
            target = event[1]
            if op == 'clear':
                rows[target] = (0, 0, 0)
            elif op == 'copy':
                rows[target] = rows[event[2]]
            else:
                need(op == 'add', 'Unknown scalar opcode')
                _, _, source, a, b = event
                need(b in (1, 2, 3, 6), 'Unsupported denominator')
                x, u, w = rows[target]
                y, j, k = rows[source]
                j += int(b % 2 == 0)
                k += int(b % 3 == 0)
                new_u, new_w = max(u, j), max(w, k)
                coefficient = abs(a) if absolute else a
                rows[target] = (x * 2**(new_u-u) * 3**(new_w-w)
                                + coefficient*y * 2**(new_u-j) * 3**(new_w-k), new_u, new_w)
            if absolute:
                x, u, w = rows[target]
                maxima = [max(maxima[0], x.bit_length()), max(maxima[1], u), max(maxima[2], w)]
        return rows, maxima

    bound, maxima = execute({('L', i): (1, 0, 0) for i in range(n)}, absolute=True)
    # Include the final expected vector after clearing that row's denominator.
    max_difference = 0
    for i in range(n):
        b, u, w = bound[('L', i)]
        rhs_l1 = 2 if (direction == 'forward' and v <= i < 2*v) or (direction == 'backward' and i < v) else 1
        max_difference = max(max_difference, b + rhs_l1 * 2**u * 3**w)
    width = max_difference.bit_length()+2
    radix = 1 << width
    need(radix > 2*max_difference, 'Insufficient separation for signed digits')
    need(width < 128, 'Unexpectedly large packing; inspect before allocating')
    print(direction, 'columns', n, 'digit bits', width, 'bound bits', maxima, flush=True)
    units = [1 << (width*i) for i in range(n)]
    rows, _ = execute({('L', i): (units[i], 0, 0) for i in range(n)})
    for i in range(n):
        expected = units[i]
        if direction == 'forward' and v <= i < 2*v:
            expected += units[i-v]
        if direction == 'backward' and i < v:
            expected -= units[i+v]
        x, u, w = rows[('L', i)]
        need(x == expected * 2**u * 3**w, f'Wrong {direction} live row {i}')
    need(all(value[0] == 0 for role, value in rows.items() if role[0] != 'L'), 'Temporary not cleared')

    # A deterministic corruption must change the map. Check the complete packed
    # map again; selected impulse columns can miss a legitimate changed column.
    mutation = next(i for i, (phase, e) in enumerate(events)
                    if phase == 'main' and e[0] == 'add'
                    and e[1][0] == e[2][0] == 'L'
                    and (v <= e[1][1] < 2*v if direction == 'forward' else e[2][1] < 2*v and e[2][1] >= v))
    bad, _ = execute({('L', i): (units[i], 0, 0) for i in range(n)}, omit=mutation)
    detected = any(rows[r][0]*2**bad[r][1]*3**bad[r][2] != bad[r][0]*2**rows[r][1]*3**rows[r][2] for r in rows)
    need(detected, 'Omitted scalar addition was not detected by controls')
    return dict(direction=direction, columns=n, arbitrary_dirty=c['R'], live_rows=n,
                digit_bits=width, maximum_final_difference_majorant=max_difference,
                prefix_numerator_bits=maxima[0], max_denominator_powers=maxima[1:],
                live_shear_and_restoration=True, temporaries_cleared=True,
                omitted_addition_rejected=True, events=len(events),
                schedule_source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                certificate_sha256=hashlib.sha256(source.read_bytes()).hexdigest())


def main():
    need(not sys.flags.optimize, 'Run without -O')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    start = time.monotonic()
    results = [replay(args.package, direction) for direction in ('forward', 'backward')]
    result = dict(status='PASS exact complete scalar schedule', checks=results, seconds=time.monotonic()-start,
                  scope='All scalar columns and arbitrary dirty restoration only; recursive center operators are identity in this scalar projection. Address geometry and all-size transfer are separate obligations.')
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
