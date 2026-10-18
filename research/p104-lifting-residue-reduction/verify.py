"""Scoped residue-reduction verification. Tekalign/Codex, Apache-2.0."""
import argparse
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import random
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def loads(raw):
    def pairs(items):
        out = {}
        for k, v in items:
            need(k not in out, 'duplicate JSON key')
            out[k] = v
        return out
    return json.loads(raw, object_pairs_hook=pairs)


def module(raw, name):
    result = types.ModuleType(name)
    exec(compile(raw, name, 'exec'), result.__dict__)
    return result


def authenticate(raw, pin):
    need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source SHA256')
    need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
         == pin['git_blob'], 'source blob')


def inputs(root=ROOT, here=HERE):
    data = {}
    for pin in loads((here/'SOURCES.json').read_bytes())['files']:
        if pin['usage'] == 'input':
            raw = (root/pin['path']).read_bytes()
            authenticate(raw, pin)
            data[pin['path']] = raw
    pin = loads((here/'PREDECESSOR.json').read_bytes())
    raw = (here/pin['local']).read_bytes()
    authenticate(raw, pin)  # authenticate before compile; no pyc is consulted
    lift = module(raw, 'authenticated_lifting')
    split = module((here/'split.py').read_bytes(), 'residue_split')
    word = loads(data['research/p104-rounded-collector/inputs/WORD.json'])
    native = loads(gzip.decompress(data['research/p104-rounded-collector/inputs/NATIVE.json.gz']))
    recipes = bind(word, native)
    return lift, split, [(lift.plan(r['left']), lift.plan(r['right'])) for r in recipes]


def bind(word, native):
    """Occurrence binding adapted from PR2999; no native theorem presumed."""
    need(len(word['program']) == 5398, 'word length')
    local = word['program'][2025:2040]
    frame = local[0][2]
    names = ['D31', 'D30', 'D29', 'D28', 'D27']
    need(local[0] == ['zero', 'C', frame] and len(frame) == 8, 'allocation')
    need(local[1:6] == [['add', 'C', s, 1, frame] for s in names], 'gather')
    need(local[7] == ['add', 'Q7', 'C', '1', local[6][3]], 'query update')
    need(local[9:14] == [['add', 'C', s, '-1', frame] for s in reversed(names)], 'ungather')
    need(local[14] == ['erase', 'C', frame], 'erase')
    frames = dict(word['initial_frames'])
    for event in word['program'][:2025]:
        op, reg = event[:2]
        if op == 'transport':
            need(frames[reg] == event[2], 'prefix frame')
            need(event[4] == abs(len(event[2])-len(event[3])), 'prefix rank')
            frames[reg] = event[3]
        elif op == 'add':
            need(reg != event[2] and frames[reg] == frames[event[2]] == event[4], 'prefix ADD')
        elif op == 'sign':
            need(frames[reg] == event[3] and int(event[2]) in (-1, 1), 'prefix sign')
        else:
            raise ValueError('prefix not invertible')
    need(all(frames[s] == frame for s in names) and frames['Q7'] == local[6][3], 'cut frames')
    recipes = []
    for index in (2031, 2033):
        records = [t for t in native['transports'] if index in t['events']]
        need(len(records) == 1, 'unique native occurrence')
        t = records[0]
        need(word['program'][index] == ['transport', 'C', t['old'], t['new'], 7], 'native binding')
        need(t['recipe']['rank'] == 7, 'native rank')
        recipes.append(t['recipe'])
    need(local[6][2:4] == list(reversed(local[8][2:4])), 'return endpoints')
    return recipes



def scale(value, k):
    return [(a*k, b*k) for a, b in value]


def add(a, b):
    return [(x+u, y+v) for (x,y),(u,v) in zip(a,b)]


def identity(n):
    return [(x, 0) for x in range(n)]


def exact_inverse(lift, value, rank, left, right):
    # Conjugate the independent rational numerator, with adjoint wrappers.
    value = lift.permute(value, lift.inverse_plan(left))
    value = [(a,-b) for a,b in value]
    value = lift.exact(value, rank, identity(len(value)), identity(len(value)))
    value = [(a,-b) for a,b in value]
    return lift.permute(value, lift.inverse_plan(right))


def linear_check(lift, split, value, rank, left, right, inverse):
    g = rank//2+1
    actual = split.linear(list(value), rank, left, right, inverse)
    numerator = (exact_inverse(lift, value, rank, left, right) if inverse
                 else lift.exact(value, rank, left, right))
    need(scale(actual, 1 << rank) == scale(numerator, 1 << g), 'exact linear backend')
    return actual


def check_case(lift, split, value, rank, left, right, inverse=False):
    snapshots = []
    actual = split.kernel(list(value), rank, left, right, lift, inverse,
                          observer=lambda q,s: snapshots.append((list(q),list(s))))
    expected = lift.kernel(list(value), rank, left, right, inverse=inverse)
    need(actual == expected, 'identical nonlinear map')
    need(len(snapshots) == 1 and all(z == (0,0) for a in snapshots[0] for z in a),
         'owned scratch reset')
    return actual


def generic_checks(lift, split):
    rng = random.Random(53)
    cases = 0
    h = hashlib.sha256()
    for rank in range(1,11):
        n = 1 << rank
        plan = identity(n)
        for inverse in (False,True):
            x = [(rng.randrange(-100000,100000),rng.randrange(-100000,100000)) for _ in range(n)]
            z = [(rng.randrange(-99,100),rng.randrange(-99,100)) for _ in range(n)]
            base = check_case(lift,split,x,rank,plan,plan,inverse)
            translated = check_case(lift,split,add(x,scale(z,1 << (rank//2+1))),rank,plan,plan,inverse)
            exact = linear_check(lift,split,z,rank,plan,plan,inverse)
            need(translated == add(base,exact), 'translation law')
            h.update(json.dumps(translated,separators=(',',':')).encode())
            cases += 1
    # All two-coordinate residue pairs, signed translations, both directions.
    exhaustive = 0
    for coords in itertools.product(range(2),repeat=4):
        for shifts in itertools.product(range(-1,2),repeat=4):
            x = [tuple(coords[:2]),tuple(coords[2:])]
            z = [tuple(shifts[:2]),tuple(shifts[2:])]
            for inverse in (False,True):
                base = check_case(lift,split,x,1,identity(2),identity(2),inverse)
                out = check_case(lift,split,add(x,scale(z,2)),1,identity(2),identity(2),inverse)
                exact = linear_check(lift,split,z,1,identity(2),identity(2),inverse)
                need(out == add(base,exact), 'exhaustive signed translation')
                exhaustive += 1
    return dict(random_rank_direction_cases=cases,exhaustive_pair_cases=exhaustive,
                sha256=h.hexdigest())


def sharpness(lift):
    result = []
    for rank in range(1,11):
        n = 1 << rank
        x = [(0,0)]*n
        x[0] = (1,0)
        m = rank//2
        a = lift.kernel(list(x),rank,identity(n),identity(n))
        b = lift.kernel(scale(x,1+(1<<m)),rank,identity(n),identity(n))
        diff = [(u-a,v-b) for (u,v),(a,b) in zip(b,a)]
        target = lift.exact(scale(x,1<<m),rank,identity(n),identity(n))
        failures = sum(v != t for v,t in zip(scale(diff,1<<rank),target))
        need(failures == (2 if rank%2==0 else n), 'one-bit-short control')
        result.append(dict(rank=rank,insufficient_guard=m,failing_coordinates=failures))
    return result


def native_checks(lift, split, plans):
    h = hashlib.sha256()
    left,right = plans[0]
    vleft,vright = plans[1]
    for col in range(512):
        basis = [(0,0)]*512
        basis[col] = (1,0)
        forward = linear_check(lift,split,basis,7,left,right,False)
        inverse = linear_check(lift,split,basis,7,left,right,True)
        need(scale(inverse,128) == scale(lift.exact(basis,7,vleft,vright),16),
             'literal native return binding')
        h.update(json.dumps([forward,inverse],separators=(',',':')).encode())
    rng = random.Random(53)
    for width in (1,4,17,130,4096):
        value = [(rng.randrange(-(1<<width),1<<width),rng.randrange(-(1<<width),1<<width)) for _ in range(512)]
        sent = check_case(lift,split,value,7,left,right)
        returned = check_case(lift,split,sent,7,left,right,True)
        need(returned == value, 'literal paired return')
    return dict(columns_each_direction=512,paired_widths=[1,4,17,130,4096],sha256=h.hexdigest())


def collector_checks(lift, split, plans):
    # Run byte-identical predecessor collector with only its kernel substituted.
    direct = lift.kernel
    rng = random.Random(53)
    results = []
    left,right = plans[0]
    for width,f,b in ((2,0,0),(17,19,8),(130,300,64),(4096,19,32)):
        arrays = [[(rng.randrange(-(1<<width),1<<width),rng.randrange(-(1<<width),1<<width)) for _ in range(512)] for _ in range(6)]
        before = json.dumps(arrays)
        old = lift.collector(arrays[:5],arrays[5],f,b,left,right)
        adapter = types.SimpleNamespace(kernel=direct)
        def replace(value,rank,left,right,inverse=False,meter=None):
            # Logical predecessor meter is suppressed: the new invoice is distinct.
            return split.kernel(value,rank,left,right,adapter,inverse)
        lift.kernel = replace
        try:
            new = lift.collector(arrays[:5],arrays[5],f,b,left,right)
        finally:
            lift.kernel = direct
        for key in ('query','grid','entrance','sent','returned','private'):
            need(new[key] == old[key], 'collector equality: '+key)
        need(before == json.dumps(arrays), 'dirty inputs unchanged')
        need(all(z == (0,0) for z in new['private']), 'collector private zero')
        results.append(dict(width=width,f=f,b=b,grid=new['grid'],
                            query_sha256=hashlib.sha256(json.dumps(new['query']).encode()).hexdigest()))
    return results


def run(root=ROOT, here=HERE):
    lift,split,plans = inputs(root,here)
    return dict(status='PASS_P104_LIFTING_RESIDUE_REDUCTION',
                generic=generic_checks(lift,split),sharpness_controls=sharpness(lift),
                native=native_checks(lift,split,plans),collector=collector_checks(lift,split,plans),
                transport_invoice=split.invoice(512,7,sum(len(lift.cycles(p)) for p in plans[0])))


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit',action='store_true')
    args = parser.parse_args()
    result = run()
    if args.emit:
        print(json.dumps(result,indent=2))
    else:
        need(canonical(result) == canonical(loads((HERE/'RESULT.json').read_bytes())), 'typed receipt mismatch')
        print(result['status'])


if __name__ == '__main__':
    main()
