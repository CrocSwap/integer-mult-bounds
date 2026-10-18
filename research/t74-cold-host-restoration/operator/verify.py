#!/usr/bin/env python3
"""Rebuild and audit a finite inverse-prelude fixture with the pinned grammar.

Python standard library only. Sources are authenticated before execution.
Every generated word and receipt lives in a TemporaryDirectory, never beside
this script. This proves a local operator/frame fact; native admission fails.
"""
import argparse
import copy
import gzip
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
PINS_SHA256 = 'e418bfb50633a20742ab3144d46500c2b234414dfd9df6c31738a8022e1ad796'
HOST, OP = 277, 73
FULL = [256, 128, 64, 32, 16, 8, 4, 2, 1]
PROFILE = {'1': 2381, '2': 650, '3': 266, '4': 128, '5': 26, '8': 8}
INVENTORY = {'4': 25, '5': 2, '7': 62, '8': 77, '9': 241}
RECOVERY = [
    ['add', HOST, 100, -1, 2, FULL],
    ['add', HOST, 226, -1, 1, FULL],
    ['add', HOST, 54, 1, 1, FULL],
    ['add', HOST, 67, 1, 1, FULL],
]


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def authenticate():
    data = (HERE / 'SOURCE-PINS.json').read_bytes()
    require(sha(data) == PINS_SHA256, 'altered SOURCE-PINS.json')
    pins = json.loads(data)
    for name, row in pins['sources'].items():
        data = (HERE / name).read_bytes()
        require(sha(data) == row['sha256'], 'source SHA256 mismatch: '+name)
        blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        require(blob == row['git_blob'], 'source Git blob mismatch: '+name)
        require(len(row['source_head']) == 40, 'missing pinned upstream head')
    invoice = (HERE / 'vendor/invoice_allcold_pr2745.py').read_bytes()
    require(b'adapters = 16*(macro_bound+warp_bound+children+n+centres+zero_buffers+2)+64*m' in invoice, 'pinned native routing formula changed')
    return pins


def basis(vs):
    pivots = {}
    for x in vs:
        for bit in sorted(pivots, reverse=True):
            if x >> bit & 1:
                x ^= pivots[bit]
        if x:
            bit = x.bit_length()-1
            for other in pivots:
                if pivots[other] >> bit & 1:
                    pivots[other] ^= x
            pivots[bit] = x
    return tuple(pivots[bit] for bit in sorted(pivots, reverse=True))


def derive_cleanup(w):
    v, n = w['report']['v'], 2*w['report']['v']+w['report']['R']
    restored = set(map(int, w['helper_final']))
    by_position = defaultdict(list)
    for op, record in enumerate(w['warps'], 1):
        by_position[record[0]].append(['warp', record[1], op])
    forward = list(w['A'][w['prelude_events']:])
    for pos in range(len(w['B'])+1):
        forward += by_position[pos]
        if pos < len(w['B']):
            forward.append(w['B'][pos])
    forward += w['restore']
    buffer = lambda r: r+n if r in restored else r
    out = []
    for g in reversed(forward):
        if g[0] != 'warp' and v <= g[1] < 2*v:
            continue
        if g[0] == 'warp':
            out.append(['warp', buffer(g[1]), -g[2], FULL])
        elif g[0] == 'add':
            out.append(['add', buffer(g[1]), buffer(g[2]), -g[3], g[4], FULL])
        else:
            require(g[0] == 'scale', 'unknown cleanup gate')
            out.append(['scale', buffer(g[1]), g[3], g[2], FULL])
    return out


def build(source):
    w = copy.deepcopy(source)
    require(str(HOST) not in w['start_extra'], 'host has a nonzero entrance')
    require(str(HOST) not in w['helper_final'], 'host already restored')
    require(w['warps'][OP-1][1] == HOST, 'operator/lender mismatch')
    require(sum(rec[1] == HOST for rec in w['warps']) == 1, 'earlier host operator')
    corrections = [c for c in w['initial_corrections'] if c['source'] == HOST]
    require(len(corrections) == 2 and all(c['operator_word'] == [OP] for c in corrections), 'new correction shape')
    # K^-1 changes these two K corrections into identity corrections. Push that
    # target vector through the preceding scalar wrapper to avoid an empty
    # operator_word (which the pinned grammar forbids).
    delta = defaultdict(Fraction)
    for c in corrections:
        delta[c['target']] += Fraction(c['coefficient'])
    for g in w['precondition']+w['compensation']:
        require(g[-1] == [] and 112 <= g[1] < 224, 'wrapper is not a zero-frame target write')
        if g[0] == 'add':
            delta[g[1]] += Fraction(g[3], g[4])*delta[g[2]]
        else:
            require(g[0] == 'scale', 'unknown wrapper gate')
            delta[g[1]] *= Fraction(g[2], g[3])
    reads = [['add', t, HOST, q.numerator, q.denominator, []] for t, q in sorted(delta.items()) if q]
    require(reads == [['add', 213, HOST, 1, 2, []]], 'transported correction changed')
    w['initial_corrections'] = [c for c in w['initial_corrections'] if c['source'] != HOST]
    w['A'] = reads + [['warp', HOST, -OP, [], []]] + w['A']
    w['prelude_events'] += 2
    require(not any(g[1] in {100, 226, 54, 67} for g in w['restore']), 'terminal recovery sources were changed')
    w['restore'] += copy.deepcopy(RECOVERY)
    w['helper_final'][str(HOST)] = list(FULL)
    w['cleanup'] = derive_cleanup(w)
    # Every original literal frame and profile remains byte-for-byte unchanged.
    require(w['A'][2:] == source['A'] and w['B'] == source['B'], 'changed original gate/frame')
    require(w['restore'][:-4] == source['restore'], 'changed original restoration')
    return w


def recount(w):
    """Literal GF(2) frame/rank accounting independent of the scalar replay."""
    v, h, n = w['report']['v'], w['report']['h'], 2*w['report']['v']+w['report']['R']
    live = set(range(n))-set(w['removed'])
    start = {r: basis([w['ports'][r]]) if r < v else () for r in live}
    start.update({int(r): basis(f) for r, f in w['start_extra'].items()})
    end = {r: basis(FULL) for r in live}
    for t, port in enumerate(w['ports']):
        end[v+t] = basis(x for x in range(1, 1 << h) if (x & port).bit_count() % 2 == 0)
    end.update({int(r): basis(f) for r, f in w['helper_final'].items()})
    current, paid = dict(start), Counter()
    def climb(r, frame):
        frame = basis(frame)
        old = current[r]
        require(basis(old+frame) == frame, 'nonmonotone literal frame')
        if old != frame:
            paid[len(frame)-len(old)] += 1
            current[r] = frame
    def gate(g):
        for r in ([g[1], g[2]] if g[0] == 'add' else [g[1]]):
            climb(r, g[-1])
    for g in w['A']:
        if g[0] == 'warp':
            require(current[g[1]] == basis(g[3]), 'literal A warp entrance')
            current[g[1]] = basis(g[4])
        else:
            gate(g)
    levels = {int(t): basis(f) for t, f in w['target_levels'].items()}
    require(all(current[v+t] == levels.get(t, ()) for t in range(v)), 'target center levels')
    for r, initial in zip(w['centers'], w['center_frames']):
        frame = basis(initial)
        require(current[r] == frame, 'center entrance frame')
        served = {levels.get(g[1]-v, ()) for g in w['cut'] if g[2] == r}
        for to in sorted(served, key=lambda x: -len(x)):
            require(basis(frame+to) == frame, 'center descent not nested')
            if to != frame:
                paid[len(frame)-len(to)] += 1
            frame = to
    by_position = defaultdict(list)
    for record in w['warps']:
        by_position[record[0]].append(record)
    for pos in range(len(w['B'])+1):
        for _, r, columns, frm, to in by_position[pos]:
            require(current[r] == basis(frm), 'literal B warp entrance')
            current[r] = basis(to)
        if pos < len(w['B']):
            gate(w['B'][pos])
    for g in w['restore']:
        gate(g)
    for r in sorted(live):
        climb(r, end[r])
    profile = {str(k): z for k, z in sorted(paid.items())}
    inventory = {str(k): z for k, z in sorted(Counter(len(end[r])-len(start[r]) for r in live if r >= 2*v).items())}
    require(profile == w['report']['local_profile'] == PROFILE, 'literal profile mismatch')
    require(inventory == w['report']['width_inventory'] == INVENTORY, 'literal inventory mismatch')
    return dict(local_profile=profile, local_mass=sum(k*z for k,z in paid.items()), width_inventory=inventory,
                independent_inputs=len(live), helpers=len(live)-2*v, zero_buffers=len(w['helper_final']))


def identity_form(minimal, source):
    w = copy.deepcopy(minimal)
    require(w['A'].pop(0) == ['add', 213, HOST, 1, 2, []], 'prelude read missing')
    w['prelude_events'] -= 1
    for c in source['initial_corrections']:
        if c['source'] == HOST:
            c = copy.deepcopy(c)
            c['operator_word'] = [OP, -OP]
            w['initial_corrections'].append(c)
    return w


def word_bytes(w):
    return json.dumps(w, sort_keys=True, separators=(',', ':')).encode()


def run_audit(w, name, tmp):
    p, receipt = tmp/(name+'.json.gz'), tmp/(name+'.audit.json')
    p.write_bytes(gzip.compress(word_bytes(w), mtime=0))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONOPTIMIZE', None)
    proc = subprocess.run([sys.executable, '-I', '-B', str(HERE/'vendor/audit_local_pr2679.py'), '--word', str(p), '--output', str(receipt)],
                          env=env, capture_output=True, text=True, timeout=60)
    diagnostic = (proc.stdout+proc.stderr).strip().splitlines()[-1]
    result = dict(returncode=proc.returncode, content_sha256=sha(word_bytes(w)), diagnostic=diagnostic)
    if proc.returncode == 0:
        audit = json.loads(receipt.read_text())
        require(audit['compressed_sha256'] == sha(p.read_bytes()), 'audit does not bind supplied bytes')
        require(audit['orientations'] == {'forward':'PASS','dual':'PASS'} and audit['checked_columns'] == 631, 'audit coverage')
        result['audit'] = {k: audit[k] for k in ('status','orientations','checked_columns','zero_buffers','corrections','local_profile','local_mass','width_inventory')}
    return p, result


def native_transport(p, name, tmp, should_pass):
    out = tmp/(name+'-native')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONOPTIMIZE', None)
    proc = subprocess.run([sys.executable, '-I', '-B', str(HERE/'vendor/bw_transport_pr2745.py'), str(p), str(out)],
                          env=env, capture_output=True, text=True, timeout=60)
    if should_pass:
        require(proc.returncode == 0, 'hosted native transport failed: '+proc.stderr[-2000:])
        receipt = json.loads((out/'SCALAR-FRAME-AUDIT.json').read_text())
        return {k:receipt[k] for k in ('status','live_columns_each_orientation','helpers','zero_buffers','warp_events','scalar_operations')}
    require(proc.returncode != 0 and 'assert all(len(frames[final[r]]) < h for r in zero_buffers)' in proc.stderr,
            'native did not reject the FULL buffer at its pinned admission rule: '+proc.stderr[-2000:])
    require(not out.exists(), 'native emitted an inadmissible fixture')
    return dict(status='EXPECTED_FULL_BUFFER_REJECTION', rule='all(len(frames[final[r]]) < h for r in zero_buffers)', host=HOST, end_rank=9)



def literal_events(w):
    """Count literal events before native center-copy/clear expansion.

    This is a structural count, not an admission or a uniform precision bound.
    The native positive controls independently bind its two event totals.
    """
    gates = [g for key in ('precondition','compensation','A','B','cut','restore','cleanup')
             for g in w[key] if g[0] != 'warp']
    for c in w['initial_corrections']:
        q = Fraction(c['coefficient'])
        gates.append(['add', c['target'], c['source'], q.numerator, q.denominator, []])
    primitives = 0
    for g in gates:
        q = Fraction(g[3], g[4]) if g[0] == 'add' else Fraction(g[2], g[3])
        a, b = abs(q.numerator), q.denominator
        require(b & (b-1) == 0, 'non-dyadic literal coefficient')
        if g[0] == 'add':
            primitives += 2*(3+a.bit_length()-1+a.bit_count()+b.bit_length()-1)
        else:
            require(a and a & (a-1) == 0, 'non-power-of-two scale')
            primitives += 2*(abs(a.bit_length()-b.bit_length())+int(q < 0))
    warps = (2*sum(len(c['operator_word']) for c in w['initial_corrections']) + len(w['warps'])
             + sum(g[0] == 'warp' for key in ('A','cleanup') for g in w[key]))
    return dict(scalar_operations=len(gates), warp_events=warps,
                scalar_real_primitives=primitives, zero_buffers=len(w['helper_final']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true', help='print the complete deterministic receipt')
    args = parser.parse_args()
    require(__debug__, 'assertions must remain enabled')
    pins = authenticate()
    result = dict(schema=1, source_pins_sha256=PINS_SHA256, cases={}, controls={})
    with tempfile.TemporaryDirectory(prefix='cold-host-operator-') as work:
        tmp = Path(work)
        for tag in ('b', 'e'):
            source = json.loads(gzip.decompress((HERE/f'inputs/hosted-{tag}-473-277.json.gz').read_bytes()))
            w = build(source)
            require(sha(word_bytes(w)) == pins['expected_minimal_fixtures'][tag]['content_sha256'], 'rebuilt fixture content changed')
            source_counts, counts = recount(source), recount(w)
            p, source_audit = run_audit(source, tag+'-source', tmp)
            require(source_audit['returncode'] == 0, 'source audit failed')
            native_source = native_transport(p, tag+'-source', tmp, True)
            p, positive = run_audit(w, tag+'-minimal', tmp)
            require(positive['returncode'] == 0, 'normalized fixture audit failed')
            native_fixture = native_transport(p, tag+'-minimal', tmp, False)
            before, after = literal_events(source), literal_events(w)
            require(all(before[k] == native_source[k] for k in ('scalar_operations','warp_events','zero_buffers')), 'literal event count disagrees with native control')
            change = {k: after[k]-before[k] for k in before}
            require(change == dict(scalar_operations=7,warp_events=-3,scalar_real_primitives=58,zero_buffers=1), 'literal resource delta changed')
            change['scalar_macros_including_buffer_clears'] = change['scalar_operations']+2*change['zero_buffers']
            change['real_primitives_including_buffer_clears'] = change['scalar_real_primitives']+4*change['zero_buffers']
            change['monomial_routing_reserve_units'] = 16*(change['scalar_macros_including_buffer_clears']+change['warp_events']+change['zero_buffers'])
            change['scope'] = 'Formal literal-event delta only; no native admission or uniform precision/physical invoice.'
            identity = identity_form(w, source)
            _, identity_audit = run_audit(identity, tag+'-identity', tmp)
            require(identity_audit['returncode'] == 0, 'equivalent nonempty identity correction failed')
            result['cases'][tag] = dict(source=source_audit, rebuilt=positive, equivalent_identity=identity_audit,
                                       source_recount=source_counts, recount=counts, native_source=native_source,
                                       native_fixture=native_fixture, literal_events_before=before, literal_events_after=after,
                                       formal_resource_delta=change)
            for mutant in ('omit-inverse','wrong-inverse-sign','omit-prelude-read','wrong-prelude-sign','omit-undo','empty-operator-word'):
                m = copy.deepcopy(w)
                if mutant == 'omit-inverse':
                    m['A'].pop(1); m['prelude_events'] -= 1
                elif mutant == 'wrong-inverse-sign':
                    m['A'][1][2] = OP
                elif mutant == 'omit-prelude-read':
                    m['A'].pop(0); m['prelude_events'] -= 1
                elif mutant == 'wrong-prelude-sign':
                    m['A'][0][3] = -1
                elif mutant == 'omit-undo':
                    m['restore'].pop(-4)
                    m['cleanup'] = derive_cleanup(m)
                else:
                    m = copy.deepcopy(identity)
                    for c in m['initial_corrections']:
                        if c['source'] == HOST:
                            c['operator_word'] = []
                _, control = run_audit(m, tag+'-'+mutant, tmp)
                reason = 'correction operator word' if mutant == 'empty-operator-word' else ('restored cold row' if mutant == 'omit-undo' else 'target map failed')
                require(control['returncode'] != 0 and reason in control['diagnostic'], 'control did not fail for the intended reason: '+mutant)
                result['controls'][tag+'-'+mutant] = control
    result['status'] = 'PASS_FINITE_CANCELLATION_AND_EXPECTED_NATIVE_EXCLUSION'
    result['native_admitted'] = False
    result['kappa_improvement'] = False
    result['scope'] = 'Both hosted words, both equivalent correction forms, every arbitrary input and both orientations pass exact scalar/frame checks; twelve controls reject. FULL-ended restored helper is forbidden by the pinned native buffer contract. No complete supplier, phase replay, physical invoice, or exponent claim.'
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result['status'])
        print('2 hosted inputs; 2 minimal fixtures; 2 equivalent identity forms; 12 rejected controls; 2 expected native FULL-buffer rejections.')
        print('631 arbitrary input columns, forward and inverse-transpose; paid profile and inventory unchanged. No kappa improvement.')


if __name__ == '__main__':
    main()
