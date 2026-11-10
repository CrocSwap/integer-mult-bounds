"""Run the pinned rounded C0 call inside complete spectator rows.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The native arithmetic is from JoyboyBrian / PR5485. The sparse planner and
exposure maps are from zxv / PR6070. Their source files are not changed.
"""
from hashlib import sha256
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


for pin in json.loads((HERE / 'SOURCES.json').read_text())['files']:
    if pin['usage'] == 'input':
        need(sha256((ROOT / pin['path']).read_bytes()).hexdigest() == pin['sha256'],
             'Source mismatch: ' + pin['path'])
NATIVE = runpy.run_path(str(ROOT / 'research/native-rounded-butterfly-contract/rounded.py'))
WRAPPER = runpy.run_path(str(ROOT / 'research/spectator-row-reservoir/verify.py'))


def offsets(positions, width):
    return [sum(((value >> j) & 1) << (width - 1 - position)
                for j, position in enumerate(positions))
            for value in range(1 << len(positions))]


def execute(values, n, selected, K, G, Q, P, H, cycle=1):
    """Return grid integers, a cost receipt and the source plan."""
    need(type(P) is int and P >= 0 and type(H) is int and H >= 0, 'Precision and magnitude')
    p = WRAPPER['plan'](n, selected, K, G, Q)
    f, R = p['h'], p['R']
    g = P + (f + 1) // 2 + 1
    width = H + g + 2 * f + (f + 1) // 2 + 9
    need(len(values) == 1 << n, 'Complete input rectangle')
    need(all(len(z) == 2 and all(type(a) is int for a in z)
             and z[0] * z[0] + z[1] * z[1] <= 1 << (2 * (H + g))
             for z in values), 'Stored input and complex magnitude')
    data = WRAPPER['permute'](values, p['mapping'], n)
    m, row_size = n - R, 1 << (n - R)
    rows = [data[i * row_size:(i + 1) * row_size] for i in range(p['rows'])]
    rows.extend([[(0, 0)] * row_size for _ in range(p['padded_rows'] - p['rows'])])
    active = [position - R for position in p['target'][::K]]
    passive = [position for position in range(m) if position not in active]
    need(len(passive) >= 2 * f, 'Two passive bits for each native triple')
    positions = [position for j in range(f)
                 for position in (active[j], passive[2 * j], passive[2 * j + 1])]
    kernel = offsets(positions, m)
    blocks = offsets(passive[2 * f:], m)
    need(len(kernel) * len(blocks) == row_size, 'Complete disjoint block cover')
    shift = cycle % len(rows)
    rows = rows[shift:] + rows[:shift]
    trace = {}
    calls = 0
    for row in rows:
        for base in blocks:
            vector = [row[base | offset] for offset in kernel]
            NATIVE['call'](vector, f, 0, width, trace=trace)
            calls += 1
            for offset, value in zip(kernel, vector):
                row[base | offset] = value
    if shift:
        rows = rows[-shift:] + rows[:-shift]
    padded = rows[p['rows']:]
    need(all(value == (0, 0) for row in padded for value in row), 'Exact padded-row return')
    data = [value for row in rows[:p['rows']] for value in row]
    output = WRAPPER['permute'](data, p['inverse'], n)
    volume = p['padded_rows'] * row_size
    need(trace['butterflies'] == f * volume // 2, 'All padded butterflies are charged')
    return output, {'grid_bits': g, 'signed_width': width, 'padded_volume': volume,
                    'kernel_calls': calls, 'butterflies': trace['butterflies'],
                    'native_integer_operations': 28 * trace['butterflies'],
                    'native_real_reads': 4 * trace['butterflies'],
                    'native_real_writes': 4 * trace['butterflies'],
                    'rounding_events': trace['rounding_events'],
                    'peak_numerator': trace['peak_numerator'],
                    'padded_coordinates_checked_zero': len(padded) * row_size}, p
