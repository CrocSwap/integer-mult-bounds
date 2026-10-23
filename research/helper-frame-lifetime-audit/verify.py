#!/usr/bin/env python3
"""Independent finite helper-lifetime audit using enumerated F2 subspaces.

No constructor, transport, wrapper, or linear-algebra engine is imported.
This checks a bounded frame schedule, not scalar endpoints or a full theorem.
Prepared for sk1-j with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path('research/community-k492-audit/pr626/replay/mixed-global/base/providers')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value):
    return type(value) is int


def check_word(word):
    """Check persistent helper frames through A, B, tail, and final climbs.

    Center cut excursions restore their entry frame and are outside this audit.
    Subspaces are enumerated, so equivalent ordered bases compare identically.
    """
    h, v, helpers = (word.get(k) for k in ('h', 'v', 'R'))
    require(integer(h) and 1 <= h <= 12, 'Audit supports ambient dimensions 1..12')
    require(integer(v) and v > 0 and integer(helpers) and helpers > 0, 'Invalid geometry')
    n = 2 * v + helpers
    frames = word.get('frames')
    require(isinstance(frames, list) and len(frames) >= 2, 'Missing frames')
    spans = []
    for fid, frame in enumerate(frames):
        require(isinstance(frame, list) and len(frame) <= h, f'Invalid frame {fid}')
        span = {0}
        for vector in frame:
            require(integer(vector) and 0 < vector < 1 << h, f'Invalid vector in frame {fid}')
            require(vector not in span, f'Dependent basis in frame {fid}')
            span |= {x ^ vector for x in span}
        spans.append(frozenset(span))
    require(spans[0] == {0} and len(spans[1]) == 1 << h, 'Frames 0/1 must be BOTTOM/FULL')

    def frame_id(fid):
        require(integer(fid) and 0 <= fid < len(spans), 'Invalid frame index')

    for field in ('start', 'final'):
        require(isinstance(word.get(field), list) and len(word[field]) == n, f'Invalid {field} inventory')
        for fid in word[field]:
            frame_id(fid)

    def gate_data(gate, where):
        require(isinstance(gate, list) and gate, f'Malformed gate in {where}')
        op = gate[0]
        require(op in ('add', 'scale'), f'Unknown gate in {where}')
        require(len(gate) == (6 if op == 'add' else 5), f'Malformed {op} in {where}')
        touched = gate[1:3] if op == 'add' else gate[1:2]
        require(all(integer(r) and 0 <= r < n for r in touched), f'Invalid register in {where}')
        require(len(set(touched)) == len(touched), f'Self-add in {where}')
        numerator, denominator = gate[-3:-1]
        require(integer(numerator) and integer(denominator) and denominator != 0,
                f'Invalid rational coefficient in {where}')
        require(op != 'scale' or numerator != 0, f'Zero scale in {where}')
        frame_id(gate[-1])
        return touched, gate[-1]

    helper_ids = set(range(2 * v, n))
    early = {r for r in helper_ids if spans[word['final'][r]] != spans[1]}
    entering = {r for r in helper_ids if spans[word['start'][r]] != spans[0]}
    protected = early | entering
    gates = {}
    for part in ('precondition', 'compensation', 'A', 'B', 'tail', 'cleanup'):
        require(isinstance(word.get(part), list), f'Missing gate section {part}')
        gates[part] = [gate_data(g, f'{part}[{i}]') for i, g in enumerate(word[part])]
    for part in ('precondition', 'compensation'):
        for touched, _ in gates[part]:
            require(not protected.intersection(touched), f'{part} touches a helper before its entry wrapper')

    current = word['start'].copy()
    last_tail = {}
    touches = 0
    for part in ('A', 'B', 'tail'):
        for index, (touched, frame) in enumerate(gates[part]):
            for r in helper_ids.intersection(touched):
                require(spans[current[r]] <= spans[frame],
                        f'Nonmonotone helper {r} at {part}[{index}]: frame {current[r]} -> {frame}')
                current[r] = frame
                touches += 1
                if part == 'tail':
                    last_tail[r] = frame
    for r in helper_ids:
        require(spans[current[r]] <= spans[word['final'][r]], f'Nonmonotone final climb for helper {r}')
    for r in early:
        require(r in last_tail and spans[last_tail[r]] == spans[word['final'][r]],
                f'Last tail touch does not reach terminal frame for helper {r}')
    for touched, _ in gates['cleanup']:
        require(all(spans[word['final'][r]] == spans[1] for r in touched),
                'Cleanup touches a register with a non-FULL terminal frame')
    return dict(helpers=helpers, early_helpers=len(early),
                entering_early_helpers=len(early & entering), cold_early_helpers=len(early - entering),
                frames=len(frames), helper_touches=touches, tail_gates=len(gates['tail']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('words', nargs='*', type=Path, help='Canonical .json or .json.gz words; defaults to frozen PR626 ck/jp8')
    parser.add_argument('--out', type=Path, help='Optional JSON receipt (no source artifacts are regenerated)')
    args = parser.parse_args()
    paths = args.words or [ROOT / FIXTURE / pid / 'CANONICAL-WORD.json.gz' for pid in ('ck', 'jp8')]
    instances = []
    for path in paths:
        raw = path.read_bytes()
        payload = gzip.decompress(raw) if path.suffix == '.gz' else raw
        result = check_word(json.loads(payload))
        label = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
        instances.append(dict(word=label, payload_sha256=hashlib.sha256(payload).hexdigest(), **result))
        print(f'PASS {path.parent.name}: {result["helpers"]} helpers, {result["early_helpers"]} early ends')
    receipt = dict(status='PASS_FINITE_HELPER_FRAME_LIFETIMES', instances=instances,
                   scope='Enumerated F2 helper-frame inclusions and prefix/cleanup exclusions only. '
                         'No scalar endpoint, wrapper identity, cut excursion, cost, hosting, or full theorem proof.')
    if args.out:
        args.out.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
