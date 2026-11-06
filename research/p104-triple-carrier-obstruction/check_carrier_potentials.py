"""Independent scalar-adjoint audit of the 42 rational carrier separators.

Imports no primary or predecessor code. Uses literal program cuts, rather than
the certificate's vector residence inventory or its rank computation.
Jerry Chen / @CubeJerry, substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from pathlib import Path
import gzip
import hashlib
import json
import sys

PIN = 'e8c7a9d54d98a4cfa27e15593016b3908afed303e0f480076ed3f596192e5a4d'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def probe(word, record, power):
    """Probe deterministic old-input data to prove the held row is nonzero."""
    n = word['public']
    role = record['role']
    initial = [Q((r + 1) ** power) for r in range(n)]
    state = initial + [Q(0)] * word['owned_fields']
    pivot = None
    values = {}
    exports = set(record['exports'])
    for t, op in enumerate(word['program']):
        if t == record['first']:
            pivot = state[role]
            if pivot == 0:
                return None
        if t in exports:
            need(op[0] == 'ADD' and op[2] == role, 'Deleted export is an ADD')
            values[t] = state[role]
        if record['lo'] <= t < record['hi'] and op[1] == role:
            need(op[0] in ('MOVE', 'SCALE'), 'Feedback invalidates linear superposition')
        kind, dst = op[:2]
        if kind in ('INIT', 'CLEAR'):
            state[dst] = Q(0)
        elif kind == 'SCALE':
            need(Q(op[2]) != 0, 'Source scaling must be nonzero')
            state[dst] *= Q(op[2])
        elif kind in ('ADD', 'COPY'):
            if kind == 'COPY':
                need(state[dst] == 0, 'Scalar COPY-zero condition')
            state[dst] += Q(op[3]) * state[op[2]]
        else:
            need(kind == 'MOVE', 'Unknown scalar operation')
    expected = initial + [Q(0)] * word['owned_fields']
    for r in word['live']:
        expected[r + 112] += initial[r]
    need(state == expected, 'Whole-word scalar endpoint')
    need(pivot is not None and set(values) == exports, 'Complete old-export probes')
    return {t: value / pivot for t, value in values.items()}


def audit(word, record, witness, ratios, all_frames=False):
    n = word['public']
    size = n + word['owned_fields']
    dual = {int(k): Q(v) for k, v in witness['dual']}
    need(sum(dual.get(int(k), 0) * Q(v) for k, v in record['target']) == 1,
         'Certificate target normalization')
    frames = word['final'][:] + [None] * word['owned_fields']
    h = [dual.get(r, Q(0)) if r < n and frames[r] != 127 else Q(0)
         for r in range(size)]
    indices = range(5) if all_frames else witness['retained_frame_indices']
    allowed = {record['frames'][i] for i in indices}
    role = record['role']
    bad = {r for r in range(size) if r != role and frames[r] in allowed and h[r]}
    checked_cuts = 0
    contraction = Q(0)
    monitor = 0

    def cut(t):
        nonlocal checked_cuts
        if record['lo'] <= t <= record['hi']:
            need(not bad, 'A permitted literal-cut recipient has nonzero dual response')
            checked_cuts += 1

    cut(len(word['program']))
    for t in range(len(word['program']) - 1, -1, -1):
        op = word['program'][t]
        kind, dst = op[:2]
        if t in ratios:
            contraction += Q(op[3]) * ratios[t] * h[dst]
        changed = {dst}
        if kind in ('ADD', 'COPY'):
            src = op[2]
            need(src != dst, 'No self ADD/COPY in source')
            h[src] += Q(op[3]) * h[dst]
            changed.add(src)
            if kind == 'COPY':
                h[dst] += dual.get(n + monitor, Q(0))
                monitor += 1
        elif kind == 'SCALE':
            h[dst] *= Q(op[2])
        elif kind == 'MOVE':
            need(frames[dst] == op[3], 'Reverse MOVE residence')
            frames[dst] = op[2]
        elif kind == 'INIT':
            need(frames[dst] == op[2], 'Reverse INIT residence')
            h[dst], frames[dst] = Q(0), None
        elif kind == 'CLEAR':
            need(frames[dst] is None, 'Reverse CLEAR residence')
            h[dst], frames[dst] = Q(0), op[2]
        else:
            raise ValueError('Unknown adjoint operation')
        for r in changed:
            if r != role and frames[r] in allowed and h[r]:
                bad.add(r)
            else:
                bad.discard(r)
        cut(t)
    need(frames == word['initial'] + [None] * word['owned_fields'], 'Initial residence')
    need(contraction == 1, 'Independent source-derived target contraction')
    need(checked_cuts == record['hi'] - record['lo'] + 1, 'Every literal cut checked')
    return checked_cuts


def check(root):
    raw = (root / 'inputs/PR6702-WORD.json.gz').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PIN, 'Native source byte pin')
    word = json.loads(gzip.decompress(raw))
    cert = json.loads((root / 'CERTIFICATE.json').read_text())
    need(cert['source_sha256'] == PIN and len(cert['triples']) == 14, 'Certificate binding')
    cuts = controls = count = 0
    for record in cert['triples']:
        ratios = None
        for power in range(word['public']):
            ratios = probe(word, record, power)
            if ratios is not None:
                break
        need(ratios is not None, 'Vandermonde probes must witness a nonzero held row')
        need(len(record['witnesses']) == 3, 'Three maximal omissions')
        for witness in record['witnesses']:
            cuts += audit(word, record, witness, ratios)
            count += 1
            try:
                audit(word, record, witness, ratios, all_frames=True)
            except ValueError as error:
                need('permitted literal-cut recipient' in str(error), 'Full-inventory control specificity')
                controls += 1
            else:
                raise ValueError('Original full-frame reinsertion must invalidate the separator')
        mutated = dict(record['witnesses'][0])
        mutated['dual'] = [[k, str(-Q(v))] for k, v in mutated['dual']]
        try:
            audit(word, record, mutated, ratios)
        except ValueError as error:
            need('target normalization' in str(error), 'Sign mutation specificity')
            controls += 1
        else:
            raise ValueError('Sign-corrupted witness accepted')
    need(count == 42 and controls == 56, 'Complete separator/control count')
    return {'source_sha256': PIN, 'old_input_probes': 14, 'separators': count,
            'literal_cut_checks': cuts, 'controls': controls, 'primary_imports': 0}


if __name__ == '__main__':
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
    print('PASS_INDEPENDENT_SCALAR_ADJOINT', json.dumps(check(root), sort_keys=True))
