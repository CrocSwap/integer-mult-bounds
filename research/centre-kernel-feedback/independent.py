#!/usr/bin/env python3
"""Literal rational replay, without importing the block-factor verifier.
Tekalign with substantial OpenAI Codex assistance; Apache-2.0.
"""
import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
F = Fraction


def check(condition, why):
    if not condition:
        raise ValueError(why)


def plus(left, right, coefficient=1):
    out = dict(left)
    for k in right:
        out[k] = out.get(k, 0)+coefficient*right[k]
        if not out[k]: del out[k]
    return out


def times(row, q):
    return {k: v*q for k, v in row.items() if v*q}


def source():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for pin in pins['files']:
        if pin['usage'] == 'input':
            raw = (ROOT/pin['path']).read_bytes()
            check(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'archive bytes')
    reference_pin = next(p for p in pins['references'] if p['local'].startswith('pr2799'))
    raw = gzip.decompress((HERE/reference_pin['local']).read_bytes())
    check(hashlib.sha256(raw).hexdigest() == reference_pin['sha256'], 'reference bytes')
    reference = json.loads(raw)
    data = {}
    with tarfile.open(ROOT/'research/community-frontier1094-audit/selected-replay.tar.gz') as tar:
        for key in ('global', 'program'):
            pin = pins['archive_members'][key]
            entries = [m for m in tar.getmembers() if m.name == pin['path']]
            check(len(entries) == 1 and entries[0].isfile(), 'unique input')
            raw = tar.extractfile(entries[0]).read()
            check(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'member bytes')
            data[key] = json.loads(gzip.decompress(raw))
    return data, reference


def digest(rows):
    return hashlib.sha256(json.dumps([
        {str(k): str(q) for k, q in sorted(row.items())} for row in rows
    ], separators=(',', ':')).encode()).hexdigest()


def operator(site):
    # Invertible, noncommuting 2x2 matrices. No native or unitary claim.
    options = (((1, 1), (0, 1)), ((1, 0), (1, 1)), ((0, -1), (1, 0)),
               ((2, 0), (0, F(1, 2))), ((1, 0), (0, 1)))
    return options[site % len(options)]


def apply_matrix(matrix, vector):
    return [plus(times(vector[0], row[0]), times(vector[1], row[1])) for row in matrix]


def tensor(row):
    return [{2*k+component: q for k, q in row.items()} for component in range(2)]


def repair_check(current, injection, feedback, matrix, wrong_sign=False):
    raw = tensor(current)
    hz = apply_matrix(matrix, tensor(feedback))
    difference = [plus(hz[k], tensor(feedback)[k], -1) for k in range(2)]
    corrected = [plus(tensor(injection)[k], difference[k], 1 if wrong_sign else -1)
                 for k in range(2)]
    applied = apply_matrix(matrix, raw)
    result = [plus(applied[k], corrected[k]) for k in range(2)]
    expected = [plus(raw[k], tensor(injection)[k]) for k in range(2)]
    return result == expected


def run():
    data, ref = source()
    receipt = json.loads((HERE/'RESULT.json').read_text())
    correction = json.loads((HERE/'CORRECTION.json').read_text())
    basis = [{j: F(1)} for j in ref['readouts']['Y']['zero_columns']]
    basis += [{int(j): F(q) for j, q in row.items()}
              for row in ref['readouts']['Y']['noncoordinate_kernel_basis']]
    injections = [{} for _ in range(1152)]
    for k, row in enumerate(basis):
        for j, q in row.items(): injections[j][k] = q
    expected_feedback = [{int(k)+128: F(q) for k, q in correction.get(str(j), {}).items()}
                         for j in range(1152)]
    state = [{} for _ in range(14336)]
    # Separate literal dual number propagation for one complete witness.
    slope = [F(0) for _ in state]
    calls = {(c['time'], c['replica'], c['stage'], c['provider_id']): c
             for c in data['global']['calls']}
    scalar_count = call_count = repairs = wrong_sign_detections = 0
    observed = []
    for event in data['global']['execution_schedule']:
        kind = event['kind']
        if kind == 'local_cover_sweep':
            key = tuple(event[k] for k in ('time', 'replica', 'stage', 'provider_id'))
            c = calls[key]
            owners = [row[0] for row in c['owners']]
            values = {('L', i): dict(state[owner]) for i, owner in enumerate(owners)}
            dual = {('L', i): slope[owner] for i, owner in enumerate(owners)}
            # Initial private differences are arbitrary and must be literally cleared.
            values.update({('C', i): {149: F(17+i, 3)} for i in range(8)})
            dual.update({('C', i): F(23+i, 5) for i in range(8)})
            for instruction in data['program'][c['orientation']]:
                tag = instruction[0]
                if tag == 'scalar':
                    scalar_count += 1
                    op = instruction[1]
                    name, target = op[0], tuple(op[1])
                    if name == 'add':
                        origin = tuple(op[2]);q = F(op[3], op[4])
                        values[target] = plus(values[target], values[origin], q)
                        dual[target] += q*dual[origin]
                    elif name == 'copy':
                        origin = tuple(op[2]);values[target] = dict(values[origin]);dual[target] = dual[origin]
                    elif name == 'clear':
                        values[target] = {};dual[target] = F(0)
                    elif name == 'scale':
                        q = F(op[2], op[3]);values[target] = times(values[target], q);dual[target] *= q
                    else: raise ValueError('unknown literal scalar')
                elif tag == 'center':
                    k = instruction[1];j = 8*call_count+k;row = values['C', k]
                    check(row == expected_feedback[j], 'literal chronological feedback at '+str(j))
                    observed.append(dict(row))
                    check(repair_check(row, injections[j], expected_feedback[j], operator(j)),
                          'noncommuting operator compensation')
                    repairs += 1
                    wrong_sign_detections += not repair_check(row, injections[j], expected_feedback[j],
                                                              operator(j), wrong_sign=True)
                    dual['C', k] += (1 if c['orientation'] == 'forward' else -1)*row.get(128, 0)
                    values['C', k] = plus(row, injections[j])
                else:
                    check(tag in {'phase', 'climb', 'adapter', 'residual_adapter'}, 'unknown local tag')
            check(all(not values['C', i] and dual['C', i] == 0 for i in range(8)), 'literal private exit')
            for i, owner in enumerate(owners):state[owner] = values['L', i];slope[owner] = dual['L', i]
            call_count += 1
        elif kind == 'bridge':
            start = 896*event['replica'];s = start+224*event['src'];d = start+224*event['dst'];q = event['coefficient']
            for i in range(112):
                state[d+i] = plus(state[d+i], state[s+i], q)
                state[s+112+i] = plus(state[s+112+i], state[d+112+i], -q)
                slope[d+i] += q*slope[s+i];slope[s+112+i] -= q*slope[d+112+i]
        elif kind == 'terminal':
            for pair in range(4):
                for i in range(112):
                    x = 896*event['replica']+224*pair+i
                    state[x], state[x+112] = state[x+112], times(state[x], -1)
                    slope[x], slope[x+112] = slope[x+112], -slope[x]
        else:
            check(kind in {'idle_cover_sweep', 'terminal_Y_translations',
                           'bank_padding_cover_sweep', 'translate_every_live_family'}, 'unknown global tag')
    check(call_count == 144 and repairs == 1152 and scalar_count == 2835792, 'literal coverage')
    check(all(not row for i, row in enumerate(state) if i % 224 >= 112), 'literal final Y')
    check(all(149 not in row for row in state), 'arbitrary private dirt erased')
    check(digest(observed) == receipt['feedback_sha256'], 'all feedback coefficients')
    check(wrong_sign_detections > 0, 'wrong correction sign detected')
    nonzero = {i: str(q) for i, q in enumerate(slope) if i % 224 >= 112 and q}
    check(len(nonzero) == receipt['witness_tangent_Y_nonzero'], 'literal derivative support')
    check({str(i): q for i, q in list(nonzero.items())[:16]} == receipt['witness_tangent_Y_first16'],
          'literal derivative values')
    # Authenticate every derivative coefficient, not just the displayed sample.
    raw = [{i: F(q) for i, q in nonzero.items()}]
    check(digest(raw) == receipt['witness_tangent_Y_sha256'], 'entire literal derivative witness')
    print('PASS_LITERAL_KERNEL_FEEDBACK', 'scalar_instructions='+str(scalar_count),
          'operator_repairs='+str(repairs), 'wrong_sign_rejections='+str(wrong_sign_detections))


if __name__ == '__main__': run()
