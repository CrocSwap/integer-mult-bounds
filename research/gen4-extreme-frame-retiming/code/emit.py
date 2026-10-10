#!/usr/bin/env python3
"""Apply one retiming pass to a COHORT249 word.

Each selected ADD keeps its operands, scalar and category; only its frame annotation changes, to an
exact new frame shipped with the pass. MOVE records are rewritten only for the operand roles of
changed gates: every other record keeps its position and bytes. For an affected role, the stale
MOVEs are dropped and one nested MOVE is emitted immediately before each use whose frame differs
from the role's current frame, and once at the end to reach its pinned final frame.
"""
import argparse, json, shutil, struct
from collections import Counter
from pathlib import Path

if not __debug__:
    raise SystemExit('assertions are required')


def load_frames(*paths):
    fs = {}
    for path in paths:
        data = json.loads(Path(path).read_text())
        fs.update({int(k): v for k, v in data.get('frames', data).items()})
    return fs


def histogram(records):
    h = Counter()
    for op, a, b, c, f, z in records:
        if op == 0 and f:
            h[f] += 1
        elif op == 2:
            h[z] += 1
    return h


def apply_pass(base_frames, word, step, out):
    word, out = Path(word), Path(out)
    new = {int(k): v for k, v in step['frames'].items()}
    fs = load_frames(base_frames, word / 'COHORT249-FRAMES.json')
    assert not set(new) & set(fs), 'new frame id collides'
    fs.update(new)
    initial = {int(k): f for k, f in json.loads((word / 'COHORT249-INITIAL.json').read_text()).items()}
    final = {int(k): f for k, f in json.loads((word / 'COHORT249-FINAL.json').read_text()).items()}
    raw = list(struct.iter_unpack('<6i', (word / 'COHORT249-RECORDS.bin').read_bytes()))
    mutation = {}
    for item in step['selection']:
        assert item['new_frame'] in new
        for g in item['gates']:
            assert g not in mutation and raw[g][0] == 1 and raw[g][4] == item['old_frame']
            mutation[g] = item['new_frame']
    affected = {raw[g][r] for g in mutation for r in (1, 2)}
    state = {r: initial[r] for r in affected}
    emitted = []

    def move(role, frame):
        old = state[role]
        if old != frame:
            rank = fs[frame]['dim'] - fs[old]['dim']
            assert rank >= 0
            emitted.append((0, role, old, frame, rank, 0))
            state[role] = frame

    for i, (op, a, b, c, f, z) in enumerate(raw):
        if op == 0:
            if a not in affected:
                emitted.append((op, a, b, c, f, z))
        elif op == 1:
            f = mutation.get(i, f)
            for role in (a, b):
                if role in affected:
                    move(role, f)
            emitted.append((op, a, b, c, f, z))
        elif op == 2:
            assert b not in affected
            if a in affected:
                move(a, c)
            emitted.append((op, a, b, c, f, z))
        else:
            emitted.append((op, a, b, c, f, z))
    for role in sorted(affected):
        move(role, final[role])
    assert [e for e in emitted if e[0]] == [e if i not in mutation else e[:4] + (mutation[i],) + e[5:]
                                           for i, e in enumerate(raw) if e[0]], 'non-MOVE stream changed'
    out.mkdir(parents=True, exist_ok=False)
    for name in ('COHORT249-INITIAL.json', 'COHORT249-FINAL.json'):
        shutil.copy2(word / name, out / name)
    frames = json.loads((word / 'COHORT249-FRAMES.json').read_text())
    frames.update({str(k): v for k, v in new.items()})
    (out / 'COHORT249-FRAMES.json').write_text(json.dumps(frames))
    (out / 'COHORT249-RECORDS.bin').write_bytes(b''.join(struct.pack('<6i', *e) for e in emitted))
    delta = histogram(emitted)
    delta.subtract(histogram(raw))
    return dict(changed_gates=len(mutation), affected_roles=len(affected), new_frames=len(new),
                records=[len(raw), len(emitted)], histogram_delta={str(k): v for k, v in sorted(delta.items()) if v})


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('base_frames'); ap.add_argument('word'); ap.add_argument('passes'); ap.add_argument('index', type=int); ap.add_argument('out')
    a = ap.parse_args()
    print(json.dumps(apply_pass(a.base_frames, a.word, json.loads(Path(a.passes).read_text())['passes'][a.index], a.out)))
