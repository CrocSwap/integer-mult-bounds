"""Source-bound retained-backing audit for PR5188's literal interchange.

Hiroki KUMAZAKI (@kumagi), substantial OpenAI Codex assistance. Apache-2.0.
Geometry, capacity arithmetic and endpoint oracles are observers only.
"""
from __future__ import annotations

import argparse
import hashlib
from itertools import permutations, product
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = 'research/literal-elementary-interchange/'
NUMERIC = ('PRE', 'GAP', 'TAIL', 'SCAN', 'REMAIN', 'OUTER', 'BETWEEN', 'BITS')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def load(name, filename, raw):
    module = types.ModuleType(name)
    module.__file__ = str(filename)
    sys.modules[name] = module
    exec(compile(raw, str(filename), 'exec'), module.__dict__)
    return module


def authenticate():
    captured = {}
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] != 'input':
            continue
        raw = (ROOT/row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256 mismatch: '+row['path'])
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'],
             'source Git blob mismatch: '+row['path'])
        captured[row['path']] = raw
    need(len(captured) == 6, 'six declared source inputs')
    return captured


def volume(shape):
    h, a, g, s = shape
    need(type(h) is int and h >= 0 and all(type(v) is int and v >= 1 for v in (a, g, s)),
         'admitted geometry')
    return a*4**h*g*s


def caps(shape):
    """Exact largest written index plus one, from a fresh blank private bank."""
    h, a, g, s = shape
    v, d = volume(shape), max(h-1, 0)
    widths = dict(zip(('PRE', 'GAP', 'TAIL'), (x.bit_length()+d+2 for x in (a, g, s))))
    result = dict(widths)
    result.update(SCAN=max(1, h.bit_length())+2, REMAIN=max(1, h.bit_length())+2)
    result.update({counter: widths[word] if h else 1
                   for counter, word in zip(('OUTER', 'BETWEEN', 'BITS'), ('PRE', 'GAP', 'TAIL'))})
    result.update({r: 1+v//4 if h else 1 for r in ('Q00', 'Q01', 'Q10', 'Q11')})
    result.update(B0=v+1 if h else 1, B1=v+1 if h > 1 else 1, OUTPUT=v+1)
    return result


def grant(v):
    need(type(v) is int and v >= 1, 'positive historical maximum')
    return 4*v+8*v.bit_length()+23


class BoundedArray(bytearray):
    """Observer guard: the original machine alone performs all tape writes."""
    def extend(self, data):
        data = bytes(data)
        need(len(self)+len(data) <= self.limit, 'private capacity exceeded')
        super().extend(data)


class Heads(dict):
    def __init__(self, values):
        super().__init__(values)
        self.peak = dict(values)

    def __setitem__(self, key, value):
        need(value >= 0, 'head crossed origin')
        self.peak[key] = max(self.peak.get(key, 0), value)
        super().__setitem__(key, value)


def borrowed(shape, program, salt=0):
    h, a, g, s = shape
    bits = [((i*13) ^ (i//3) ^ (i//7) ^ salt) & 1 for i in range(volume(shape))]
    result = {'SOURCE': bytearray([program.LEFT]+bits)}
    for name, value in zip(('H', 'A', 'G', 'S'), shape):
        result[name] = bytearray([program.LEFT]+[int(x) for x in reversed(bin(value)[2:])]+[program.RIGHT])
    return result, bits


def endpoint(bits, shape):
    h, a, g, s = shape
    n = 1 << h
    # Independent direct coordinate gather; no digit pass or queue construction.
    return bytearray(bits[((((prefix*n+y)*g+middle)*n+x)*s+tail)]
                     for prefix in range(a) for x in range(n) for middle in range(g)
                     for y in range(n) for tail in range(s))


def run_history(program, machine, code, entries, shapes, initial=None, install=False, undergrant=None):
    initial = initial or {r: 1 for r in program.PRIVATE}
    tapes = {r: BoundedArray([program.BLANK]*initial[r]) for r in program.PRIVATE}
    expected = {r: max(1, initial[r]) for r in program.PRIVATE}
    for r in program.PRIVATE:
        tapes[r].limit = expected[r]
    heads = Heads({r: 0 for r in program.PRIVATE})
    events, records = [], []

    def invoke(name):
        row = machine.execute(code, tapes, heads, entries[name], max_steps=30000000)
        need(row['status'] == {'init':'initialized','run':'returned','consume':'consumed',
                              'install':'installed','close':'closed'}[name], 'entry '+name)
        events.append(row)

    def empty(closed=False):
        for r in program.PRIVATE:
            need(heads[r] == 1 and tapes[r][0] == (program.BLANK if closed else program.LEFT)
                 and all(x == program.BLANK for x in tapes[r][1:]), 'private cleanup '+r)

    invoke('init')
    vmax = 0
    for ordinal, shape in enumerate(shapes):
        inputs, bits = borrowed(shape, program, ordinal)
        for r, cells in inputs.items():
            tapes[r] = cells
            heads[r] = 1
        before = {r: bytes(tapes[r]) for r in program.BORROWED}
        call_caps = caps(shape)
        expected = {r: max(expected[r], call_caps[r]) for r in program.PRIVATE}
        for r in program.PRIVATE:
            tapes[r].limit = expected[r] - (r == undergrant)
        invoke('run')
        answer = endpoint(bits, shape)
        need(tapes['OUTPUT'][1:1+len(bits)] == answer, 'actual output endpoint')
        need(all(x == program.BLANK for x in tapes['OUTPUT'][1+len(bits):]), 'output blank tail')
        need(all(bytes(tapes[r]) == before[r] and heads[r] == 1 for r in program.BORROWED),
             'borrowed bytes and heads')
        invoke('install' if install else 'consume')
        if install:
            need(tapes['SOURCE'][1:] == answer and heads['SOURCE'] == 1, 'paid source installation')
        empty()
        actual = {r: len(tapes[r]) for r in program.PRIVATE}
        need(actual == expected, 'exact rolewise history identity')
        touched = {r: heads.peak[r]+1 for r in program.PRIVATE}
        need(all(touched[r] <= expected[r]+1 for r in program.PRIVATE), 'one boundary cell visit allowance')
        vmax = max(vmax, volume(shape))
        warm_grant = sum(max(1, initial[r])-1 for r in program.PRIVATE)+grant(vmax)
        need(sum(actual.values()) <= warm_grant, 'complete maximum-volume grant')
        records.append({'shape':shape,'volume':volume(shape),'retained':actual,
                        'retained_total':sum(actual.values()),'visited_span_total':sum(touched.values()),
                        'grant':warm_grant,'output_sha256':hashlib.sha256(answer).hexdigest()})
    invoke('close')
    empty(True)
    need({r:len(tapes[r]) for r in program.PRIVATE} == expected, 'close does not release backing')
    return {'initial':initial,'install':install,'calls':records,'final_retained':expected,
            'steps':sum(r['steps'] for r in events),'entries':len(events)}


def accounting_controls(program, machine, code, entries, witness, shrinking, warm):
    rows = witness['calls']
    standalone = [sum(caps(tuple(r['shape'])).values()) for r in rows]
    need(standalone == [811]*3 and [r['retained_total'] for r in rows] == [811,823,835],
         'fixed-volume history discriminator')
    need(rows[-1]['retained_total'] > max(standalone), 'max standalone total wrongly accepted')
    need(rows[-1]['retained_total'] > len(program.PRIVATE), 'erased nonblank-only count wrongly accepted')
    last = shrinking['calls'][-1]
    need(last['retained_total'] > grant(last['volume']), 'current-volume-only grant wrongly accepted')
    last = warm['calls'][-1]
    need(last['retained_total'] > grant(last['volume']), 'fresh grant ignored initial backing')
    try:
        run_history(program,machine,code,entries,[(0,1,1,1)],undergrant='OUTPUT')
    except ValueError as exc:
        need('private capacity exceeded' in str(exc), 'actual undergrant failure reason')
    else:
        raise ValueError('actual machine accepted omitted OUTPUT marker capacity')
    try:
        a = BoundedArray([program.BLANK]);a.limit = 1;a.extend([program.BLANK])
    except ValueError as exc:
        need('capacity exceeded' in str(exc), 'capacity guard failure reason')
    else:
        raise ValueError('capacity guard inactive')
    need(canonical({'n':1}) != canonical({'n':True}) != canonical({'n':1.0}), 'typed receipt control')
    return {'max_standalone_total':811,'actual_history_total':835,'missing_cells':24,
            'erased_content_only_rejected':True,'current_volume_only_rejected':True,
            'ignored_initial_backing_rejected':True,'omitted_marker_rejected':True,
            'allocation_guard_rejected':True,'typed_receipt_checked':True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    captured = authenticate()
    p = load('program', ROOT/(PARENT+'program.py'), captured[PARENT+'program.py'])
    m = load('retained_source_machine', ROOT/(PARENT+'machine.py'), captured[PARENT+'machine.py'])
    code, entries = p.assemble()
    need(len(code) == 4589 and m.validate(code,entries) == 3, 'pinned finite program')
    source_result = json.loads(captured[PARENT+'RESULT.json'])
    need(hashlib.sha256(canonical((code,entries)).encode()).hexdigest() == source_result['program_sha256'],
         'source program receipt')
    fixtures = [run_history(p,m,code,entries,[(h,a,g,s)]) for h,a,g,s in product(range(4),range(1,4),range(1,4),range(1,4))]
    fixtures.extend(run_history(p,m,code,entries,[shape]) for shape in ((4,1,1,1),(5,1,1,1)))
    varied = ((1,64,1,1),(1,1,64,1),(1,1,1,64))
    histories = [run_history(p,m,code,entries,list(order),install=(i % 2 == 1))
                 for i,order in enumerate(permutations(varied))]
    shrinking = run_history(p,m,code,entries,[(0,1024,1,1),(2,1,1,1),(1,1,1,1),(0,1,1,1)])
    initial = {r:1 for r in p.PRIVATE};initial['B1']=4096;initial['OUTER']=73
    warm = run_history(p,m,code,entries,[(0,1,1,1),(1,2,1,1)],initial=initial)
    controls = accounting_controls(p,m,code,entries,histories[0],shrinking,warm)
    actual = (2,1,1024,12)
    result = {'status':'PASS_INTERCHANGE_RETAINED_BACKING','authenticated_inputs':len(captured),
              'program_sha256':source_result['program_sha256'],'single_call_cases':len(fixtures),
              'single_call_bits':sum(x['calls'][0]['volume'] for x in fixtures),
              'single_call_receipt_sha256':hashlib.sha256(canonical(fixtures).encode()).hexdigest(),
              'varying_histories':histories,'shrinking_history':shrinking,'warm_history':warm,
              'controls':controls,'actual_caller_derived_not_executed':{'shape':actual,'volume':volume(actual),
                  'per_role':caps(actual),'total':sum(caps(actual).values()),'uniform_grant':grant(volume(actual))}}
    # The separately authored sparse interpreter checks the same unchanged instruction table.
    independent = load('independent_backing_check', HERE/'independent_check.py', (HERE/'independent_check.py').read_bytes())
    result['independent'] = independent.run_checks(code,entries,m.execute,p.ROLES,p.PRIVATE,p.BORROWED,
        [{k:bytes(v) for k,v in borrowed(shape,p,i)[0].items()} for i,shape in enumerate(varied)], initial)
    encoded = json.dumps(result,indent=2,sort_keys=True)+'\n'
    receipt = HERE/'RESULT.json'
    if args.write_result:
        receipt.write_text(encoded)
    else:
        need(receipt.read_text() == encoded, 'frozen RESULT.json differs; nothing rewritten')
    print(result['status'])
    print('110 fresh geometries; six fixed-volume mixed histories; shrinking and warm-owner controls')
    print('811 -> 823 -> 835 retained cells; source-sized 786497-cell cap derived, not replayed')


if __name__ == '__main__':
    main()
