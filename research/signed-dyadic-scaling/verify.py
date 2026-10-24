# SPDX-License-Identifier: Apache-2.0
"""Actual finite-table execution and independent coordinate-scatter checks."""
import argparse
import ast
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from loader import authenticate, load_modules, need
from kernel import SCALES, WORK, build_program


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def export(program):
    return json.loads(json.dumps(dict(tapes=program.tapes, entry=program.entry,
                                     instructions=program.instructions)))


def key(coefficient, inplace):
    return str(coefficient[0]) + '/' + str(coefficient[1]) + ':' + str(inplace)


def fixture(i, shape, payload, inplace, translated=True):
    p, q, s = shape
    need(all(type(v) is int and v > 0 for v in shape), 'positive extents')
    need(len(payload) == p*q*s and all(type(v) is int and v in (0,1) for v in payload),
         'complete Boolean stream')
    origins = [3*t-17 if translated else 0 for t in range(14)]
    bank = [({}, origin) for origin in origins]
    bank[0] = i.marked([i.ONE if x else i.ZERO for x in payload], origins[0])
    for tape, value in ((4,p),(5,q),(7,s)):
        bank[tape] = i.marked([i.ONE if value >> bit & 1 else i.ZERO
                               for bit in range(value.bit_length())], origins[tape])
    for tape in ((1,6) if inplace else (6,)):
        bank[tape] = i.marked([i.ONE,i.ZERO,i.ONE], origins[tape]+5)
    return bank


def oracle(shape, coefficient, payload):
    p, q, s = shape
    n, d = coefficient
    c = n * pow(d, -1, q) % q if q > 1 else 0
    out = [None] * len(payload)
    for prefix in range(p):
        for x in range(q):
            for z in range(s):
                src = (prefix*q+x)*s+z
                dst = (prefix*q+(c*x)%q)*s+z
                need(out[dst] is None, 'coordinate oracle bijection')
                out[dst] = payload[src]
    need(all(v is not None for v in out), 'complete coordinate image')
    return out


def observe(i, result, bank, shape, coefficient, payload, inplace):
    tapes, steps = result['tapes'], result['steps']
    target = 0 if inplace else 1
    origin = bank[target][1]-1 if inplace else bank[target][1]
    cells, head = i.marked([i.ONE if x else i.ZERO for x in oracle(shape,coefficient,payload)], origin)
    need(tapes[target].snapshot() == cells and tapes[target].head == head,
         'scaled original owner/output and record order')
    for tape in range(14):
        if tape in WORK:
            need(not tapes[tape].snapshot() and tapes[tape].head == bank[tape][1],
                 'entire private tape/head return')
        elif tape != target:
            need(tapes[tape].snapshot() == bank[tape][0] and tapes[tape].head == bank[tape][1],
                 'source/descriptor/spectator preservation')
    volume = len(payload)
    span = sum(t.high-t.low+1 for t in tapes)
    need(steps <= 2048*volume and span <= 64*volume, 'complete uniform physical bill')
    return steps, span


def primary_execute(m, program, bank, cap):
    run = m.Machine(program, [m.Tape(cells,head) for cells,head in bank]).run(cap)
    class View:
        def __init__(self, tape, visits):
            self.head = tape.head
            self.cells = tape.cells
            self.low = min(visits or {tape.head})
            self.high = max(visits or {tape.head})
        def snapshot(self):
            return dict(self.cells)
    return {'tapes':[View(t,v) for t,v in zip(run.tapes,run.visits)],'steps':run.steps}


def cases():
    for q in range(1,12,2):
        for p,s in ((1,1),(2,3)):
            for seed in (0,3):
                yield (p,q,s), [((x*x+3*x+seed)^(x>>1))&1 for x in range(p*q*s)], seed==3
    for j in range(30):
        yield (2,5,3), [int(x==j) for x in range(30)], True
    for q in (17,33):
        yield (2,q,2), [((x*7)^(x>>2))&1 for x in range(4*q)], True


def source_binding(contents):
    program = json.loads(gzip.decompress(contents['research/bit-row-route-generator/PROGRAM.json.gz']))
    sites = [s for s in program['steps'] if s['op']=='unit_scale']
    counts = Counter(tuple(s['coefficient']) for s in sites)
    need(dict(counts)=={(2,1):24,(1,2):24,(-1,1):16,(-2,1):8,(-1,2):8}, 'all actual scale leaves')
    tree = ast.parse(contents['research/bit-row-route-generator/interpreter.py'])
    assignment = ast.parse("data['high'][a]=data['high'][a]*z%R").body[0]
    need(sum(ast.dump(n)==ast.dump(assignment) for n in ast.walk(tree))==1,
         'actual source scaling coordinate/direction')
    return {'actual_f1_sites':len(sites),'coefficients':{str(k):v for k,v in sorted(counts.items())},
            'uniform_sites':'80*f^2','whole_route_admitted':False,'P3_admitted':False,
            'original_owner_installation':'literal gather-before-overwrite and consumed-bucket erasure'}


def replay(modules, programs, saved, mode):
    i, m = modules['independent_check'], modules['machine']
    digest = hashlib.sha256()
    count = volume = max_steps = max_span = 0
    for shape,payload,translated in cases():
        for coefficient in SCALES:
            for inplace in (False,True):
                bank = fixture(i,shape,payload,inplace,translated)
                label = key(coefficient,inplace)
                run = (primary_execute(m,programs[label],bank,2048*len(payload)+1) if mode=='primary'
                       else i.execute(saved[label],bank,2048*len(payload)+1))
                steps,span = observe(i,run,bank,shape,coefficient,payload,inplace)
                digest.update(canonical([shape,coefficient,inplace,steps,span,
                                         oracle(shape,coefficient,payload)]))
                count += 1
                volume += len(payload)
                max_steps = max(max_steps,steps)
                max_span = max(max_span,span)
    return {'cases':count,'payload_bits':volume,'maximum_steps':max_steps,
            'maximum_visited_span':max_span,'transcript_sha256':digest.hexdigest(),
            'transitions_per_bit_bound':2048,'visited_cells_per_bit_bound':64,
            'tapes':14,'symbols':7}


def source_sites_and_roundtrips(modules, saved, contents):
    i = modules['independent_check']
    source = json.loads(gzip.decompress(contents['research/bit-row-route-generator/PROGRAM.json.gz']))
    sites = [s for s in source['steps'] if s['op']=='unit_scale']
    q = source['q'] ** (source['w']-1)
    digest = hashlib.sha256()
    for number, site in enumerate(sites):
        address = site['addresses'][0]
        shape = (1 + address % 2, q, 1 + address % 3)
        payload = [((x*5+number)^(x>>2))&1 for x in range(shape[0]*q*shape[2])]
        coefficient = tuple(site['coefficient'])
        bank = fixture(i,shape,payload,True)
        run = i.execute(saved[key(coefficient,True)],bank,2048*len(payload)+1)
        steps,span = observe(i,run,bank,shape,coefficient,payload,True)
        digest.update(canonical([number,address,coefficient,steps,span]))
    inverse = {(2,1):(1,2),(1,2):(2,1),(-1,1):(-1,1),(-2,1):(-1,2),(-1,2):(-2,1)}
    trips = 0
    for q in range(1,12,2):
        shape = (2,q,3)
        payload = [((x*3)^(x>>1))&1 for x in range(6*q)]
        for coefficient in SCALES:
            bank = fixture(i,shape,payload,True)
            first = i.execute(saved[key(coefficient,True)],bank,2048*len(payload)+1)
            observe(i,first,bank,shape,coefficient,payload,True)
            middle = [(t.snapshot(),t.head) for t in first['tapes']]
            second = i.execute(saved[key(inverse[coefficient],True)],middle,2048*len(payload)+1)
            need(all(t.snapshot()==cells and t.head==head for t,(cells,head) in zip(second['tapes'],bank)),
                 'literal in-place inverse and every physical owner/descriptor/private return')
            trips += 1
    return {'actual_coefficient_sites':len(sites),'actual_Q':source['q']**(source['w']-1),
            'spectator_dimensions':'compressed fixtures; complete source P/S not materialized',
            'site_transcript_sha256':digest.hexdigest(),'full_inplace_roundtrips':trips}


def expect_reject(call, text):
    try:
        call()
    except (ValueError,RuntimeError):
        return
    raise ValueError('accepted control: '+text)


def controls(modules, saved, contents):
    i = modules['independent_check']
    shape,payload=(2,5,3),[int(j==7) for j in range(30)]
    base = saved[key((2,1),True)]
    groups = []
    for tape,value in ((4,0),(5,0),(5,2),(5,6),(7,0)):
        bank=fixture(i,shape,payload,True)
        bank[tape]=i.marked([i.ONE if value>>j&1 else i.ZERO for j in range(value.bit_length())],0)
        expect_reject(lambda:i.execute(base,bank,100000),'invalid extent/parity');groups.append('extent_'+str(tape)+'_'+str(value))
    bank=fixture(i,shape,payload,True);bank[5]=i.marked([i.ONE,i.ZERO],0)
    expect_reject(lambda:i.execute(base,bank,100000),'noncanonical Q');groups.append('noncanonical')
    bank=fixture(i,shape,payload,True);bank[2]=({0:i.ONE},0)
    expect_reject(lambda:i.execute(base,bank,100000),'occupied private');groups.append('occupied_work')
    bank=fixture(i,shape,payload,True)
    wrong=i.execute(saved[key((1,2),True)],bank,100000)
    expect_reject(lambda:observe(i,wrong,bank,shape,(2,1),payload,True),'half versus double');groups.append('wrong_coefficient')
    wrong=i.execute(saved[key((-1,1),True)],bank,100000)
    expect_reject(lambda:observe(i,wrong,bank,shape,(-2,1),payload,True),'missing signed doubling');groups.append('missing_stage')
    bad=json.loads(json.dumps(base))
    position=next(j for j,row in enumerate(bad['instructions']) if row[0]=='move')
    bad['instructions'][position][2]=2
    expect_reject(lambda:i.validate_program(bad),'nonlocal move');groups.append('nonlocal_move')
    bad=json.loads(json.dumps(base))
    for row in bad['instructions']:
        if row==['write',0,i.ONE]:row[2]=i.ZERO
    wrong=i.execute(bad,bank,100000)
    expect_reject(lambda:observe(i,wrong,bank,shape,(2,1),payload,True),'corrupted output');groups.append('output_corruption')
    bad=json.loads(json.dumps(base))
    for row in bad['instructions']:
        if row==['write',2,i.BLANK]:row[2]=i.ONE
    wrong=i.execute(bad,bank,100000)
    expect_reject(lambda:observe(i,wrong,bank,shape,(2,1),payload,True),'uncleared bucket');groups.append('work_retirement')
    path=next(iter(contents))
    expect_reject(lambda:authenticate({path:contents[path]+b'\n'}),'source drift');groups.append('source_hash')
    bad=json.loads(json.dumps(base));halt=next(j for j,r in enumerate(bad['instructions']) if r[0]=='halt')
    bad['instructions'][halt]=['goto',len(bad['instructions'])]
    bad['instructions'] += [['move',0,1],['move',0,-1],['halt']]
    good=i.execute(base,bank,100000);extra=i.execute(bad,bank,100000)
    need(all(t.snapshot()==u.snapshot() and t.head==u.head for t,u in zip(good['tapes'],extra['tapes'])), 'cost-only mutation endpoint')
    need(extra['steps']==good['steps']+3,'literal extra work charged');groups.append('unbilled_work')
    return groups


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true')
    parser.add_argument('--mode',choices=('primary','independent'),default='independent');args=parser.parse_args()
    contents=authenticate();modules=load_modules(contents)
    programs={key(c,p):build_program(modules,c,p) for c in SCALES for p in (False,True)}
    tables={label:export(program) for label,program in programs.items()}
    path=HERE/'TABLE.json.gz'
    if args.write:path.write_bytes(gzip.compress(canonical(tables),mtime=0))
    saved=json.loads(gzip.decompress(path.read_bytes()));need(canonical(saved)==canonical(tables),'exact complete tables')
    result={'binding':source_binding(contents),'physical':replay(modules,programs,saved,args.mode),
            'controls':controls(modules,saved,contents),'source_sites':source_sites_and_roundtrips(modules,saved,contents),'instructions':{k:len(p.instructions) for k,p in programs.items()},
            'outcome':'complete signed-dyadic primitive inventory; whole route/P3 remain unknown','new_kappa':False}
    receipt=HERE/'RESULT.json'
    if args.write:receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    need(canonical(result)==canonical(json.loads(receipt.read_text())),'complete typed receipt')
    print('PASS_SIGNED_DYADIC_SCALING',args.mode,json.dumps(result['physical'],sort_keys=True))


if __name__=='__main__':main()
