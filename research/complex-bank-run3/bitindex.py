#!/usr/bin/env python3
"""The two declaration bodies of the bit drop: B1's `index.json.gz` and B3's `charts.index.json.gz`.

The word bodies and the physical bodies in `exports-bit/` are the supplier's own artifacts, published
verbatim and anchored to the digests the certificates already carried.  What they do *not* do is
declare the counts the contract holds them to: the terminal column geometry lives in the PR200
certificate, the colouring statistics in PR205's, and neither is inside the bodies.  This derives
those declarations -- from the real bodies where they are countable (`used_frames` out of the
witness table, the selected gauge roles and their distinct frames out of the word), from the pinned
certificates where the certificate is the published source, and from the recomputed physical block
for the colouring -- and writes them as the export's own index bodies.  Nothing here is typed in by
hand, and `--check` re-derives and compares.

    python3 -B bitindex.py           # write the two index bodies
    python3 -B bitindex.py --check   # re-derive and compare with what is in the drop
"""
import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DROP = HERE / 'exports-bit'
BIT = HERE / 'references' / 'pr219-run1' / 'references' / 'pr200-bit.certificate.json'
PACK = HERE / 'references' / 'pr219-run1' / 'references' / 'pr205-packed.certificate.json'
REBUILT = HERE / 'exports-bit' / 'physical.rebuilt.json'      # the packer's recomputed physical block
Q_BOUND = 2 ** 80                                             # PR200's rule: every q > 2^80
sys.dont_write_bytecode = True
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)


def load(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def dump(path, payload):
    """Deterministic bytes: sorted keys, one trailing newline, gzip without a timestamp."""
    raw = json.dumps(payload, indent=1, sort_keys=True).encode('utf-8') + b'\n'
    Path(path).write_bytes(gzip.compress(raw, mtime=0) if str(path).endswith('.gz') else raw)


def build():
    word = load(DROP / 'word.json.gz')
    frames = load(DROP / 'frames.json.gz')['frames']
    witnesses = load(DROP / 'prime-witnesses.json.gz')
    bit = json.loads(BIT.read_text())['bit']
    pack = json.loads(PACK.read_text())['physical']
    physical = json.loads(REBUILT.read_text())

    # --- counted from the bodies themselves ------------------------------------
    used = witnesses['frame_witnesses']
    assert len(used) == witnesses['total_used_frames'] == bit['prime_witnesses']['total_used_frames']
    assert len({row['basis_sha256'] for row in used}) == len(used) == witnesses['unique_used_bases']
    recipients = {b for _a, b in word['pairs']}
    gauges = {z['role']: z for z in word['gauges']}
    selected = {role: z for role, z in gauges.items() if role not in recipients}
    assert len(selected) == pack['gauge_roles'] == bit['profile']['selected_roles'] == 2200
    assert {z['dim'] for z in selected.values()} == {20}, 'the selected family is rank 20'
    gauge_frames = sorted({z['frame'] for z in selected.values()})
    assert len(gauge_frames) == pack['distinct_gauges'] == 220, 'distinct gauge frames'
    order = {int(frame_id): i for i, frame_id in enumerate(sorted(frames))}
    assert all(str(f) in frames for f in gauge_frames)

    # --- the pinned terminal geometry and the recomputed physical block --------
    terminal = bit['terminal']['formal'][0]
    index = {
        'export': 'B1',
        'reading': 'the word bodies, declared: what each sibling hashes to, the terminal column '
                   'geometry the PR200 certificate published, and the selected gauge family the '
                   'packer asserts from this very word',
        'bodies': {'word.json.gz': anchors('word.json.gz'),
                   'frames.json.gz': anchors('frames.json.gz'),
                   'graph.json': anchors('graph.json'),
                   'kchron.json': anchors('kchron.json'),
                   'profile.json': anchors('profile.json')},
        'input_sha256': witnesses['input_sha256'],
        'formal_columns': terminal['formal_columns'],
        'dirty_columns': terminal['dirty_columns'],
        'source_columns': terminal['source_columns'],
        'target_columns': terminal['target_columns'],
        'changed_operation_frames': bit['profile']['changed_operation_frames'],
        'used_frames': len(used),
        'selected_roles': len(selected),
        'gauge_frames': len(gauge_frames),
        'frames': len(frames),
        'foreign_producer_replays': bit['foreign_producer_replays'],
        'gauge_frame_map': {str(frame): order[int(frame)] for frame in gauge_frames},
        'provenance': {'selected_roles': 'word.json.gz gauges minus the 1,760 recipient registers',
                       'used_frames': 'prime-witnesses.json.gz frame_witnesses',
                       'terminal_geometry': 'PR200 certificate bit.terminal.formal[0]',
                       'distinct_gauges': 'PR205 certificate physical.distinct_gauges'}}

    charts = {
        'export': 'B3',
        'reading': 'the chart and incidence streams are PR205\'s published digests, reproduced from '
                   'these very word bodies; this index declares the colouring and chart statistics '
                   'that the streams carry but do not name, and the witness table A7 is held to',
        'streams': {'charts.json': anchors('charts.json'),
                    'incidence.json': anchors('incidence.json'),
                    'prime-witnesses.json.gz': anchors('prime-witnesses.json.gz')},
        'used_frames': len(used),
        'physical_roles': physical['physical_roles'],
        'gauge_roles': physical['gauge_roles'],
        'distinct_gauges': physical['distinct_gauges'],
        'incidences': physical['incidences'],
        'banks': physical['banks'],
        'W': physical['W'],
        'm': physical['m'],
        'rank_mass': physical['rank_mass'],
        'deficit': physical['deficit'],
        'copies': physical['copies'],
        'terminal_sinks': physical['terminal_sinks'],
        'interior_splices': physical['interior_splices'],
        'max_chart_factors': physical['max_chart_factors'],
        'max_denominator': physical['max_den'],
        'max_abs_numerator': physical['max_num'],
        'swaps': physical['color_stats']['swaps'],
        'longest_swapped_path': physical['color_stats']['longest_swapped_path'],
        'color_stats': physical['color_stats'],
        'conflicting_assignment_rejected': physical['conflicting_assignment_rejected'],
        'patterns': physical['patterns'],
        'q_bound': Q_BOUND,
        'prime_witnesses': [{'witness': row['basis_sha256'], 'residual_factor': row['remaining_factor']}
                            for row in used],
        'provenance': {'streams': 'PR205 packed-diagonal-bit packing.py run on exports-bit/word.json.gz, '
                                  'frames.json.gz (canonical streams, digests reproduced)',
                       'prime_witnesses': 'prime-witnesses.json.gz frame_witnesses[].basis_sha256 and '
                                          'remaining_factor',
                       'q_bound': 'PR200 bit.prime_witnesses.rule: every q > 2^80'}}
    return {'index.json.gz': index, 'charts.index.json.gz': charts}


def anchors(name):
    raw = (DROP / name).read_bytes()
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


def main():
    check = '--check' in sys.argv
    derived = build()
    if check:
        for name, payload in derived.items():
            assert load(DROP / name) == payload, '%s differs from a fresh derivation' % name
        print('the two index bodies re-derive exactly: '
              + ', '.join('%s (%d witnesses)' % (name, len(p.get('prime_witnesses', [])) or len(p))
                          for name, p in derived.items()))
        return
    for name, payload in derived.items():
        dump(DROP / name, payload)
        print('wrote %s/%s (%d bytes)' % (DROP.name, name, (DROP / name).stat().st_size))


if __name__ == '__main__':
    main()
