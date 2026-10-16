"""Exact calls-only scalar endpoint experiment; ywz65, with OpenAI Codex.

The projection follows Adam Gall PR1918 and thakrarsagar PR2199. Frame maps
are identities. Bridges/idle sweeps are omitted, not claimed to be identities.
"""
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
MEMBERS = {
    'global': ('candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz', '2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760'),
    'program': ('candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz', '241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a'),
    'word': ('candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz', '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219'),
}
IDENTITIES = {'climb', 'adapter', 'residual_adapter'}

def require(ok, message):
    if not ok:
        raise ValueError(message)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def load():
    sources = json.loads((PACKAGE/'SOURCES.json').read_text())
    for entry in sources['files']:
        if entry['usage'] != 'input': continue
        raw = (ROOT/entry['path']).read_bytes()
        require(digest(raw) == entry['sha256'], 'source hash mismatch: '+entry['path'])
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        require(blob == entry['git_blob'], 'source blob mismatch: '+entry['path'])
    with tarfile.open(ROOT/ARCHIVE) as archive:
        data = {}
        for key, (name, pin) in MEMBERS.items():
            raw = archive.extractfile(name).read()
            require(digest(raw) == pin, 'member hash mismatch: '+key)
            data[key] = json.loads(gzip.decompress(raw))
    return data

def plus(row, source, scale=Q(1)):
    for k, v in source.items():
        result = row.get(k, Q(0)) + scale*v
        if result:
            row[k] = result
        else:
            row.pop(k, None)

def rank(rows):
    pivots = {}
    for source in rows:
        row = dict(source)
        while row:
            key = min(row)
            if key not in pivots:
                scale = row[key]
                pivots[key] = {k:v/scale for k,v in row.items()}
                break
            plus(row, pivots[key], -row[key])
    return len(pivots), list(pivots)

def inverse(matrix):
    n = len(matrix)
    a = [[Q(v) for v in row]+[Q(i==j) for j in range(n)] for i,row in enumerate(matrix)]
    determinant = Q(1)
    for k in range(n):
        p = next((i for i in range(k,n) if a[i][k]), None)
        require(p is not None, 'singular minor')
        if p != k:
            a[k],a[p] = a[p],a[k]
            determinant = -determinant
        pivot = a[k][k]
        determinant *= pivot
        a[k] = [v/pivot for v in a[k]]
        for i in range(n):
            if i != k:
                q = a[i][k]
                a[i] = [x-q*y for x,y in zip(a[i],a[k])]
    return [row[n:] for row in a], determinant

def evaluate(form, states):
    out = {}
    for role, q in form.items():
        plus(out, states[role], q)
    return out

def local(program, mute=False):
    """Return exact 704-role endpoint and source/scatter cuts.

    Ablation sets C_k=0 precisely at each rank-eight center event. No scalar
    operation, preparation, continuation, or cleanup is removed.
    """
    states = {('L',i):{i:Q(1)} for i in range(704)}
    cuts, scatter, bill = {}, {}, Counter()
    phase = None
    for event in program:
        tag = event[0]
        if tag == 'phase':
            phase = event[1]
        elif tag == 'scalar':
            op = event[1]
            name,dst = op[0],tuple(op[1])
            if phase == 'centers': bill[name] += 1
            if name == 'clear': states[dst] = {}
            elif name == 'copy': states[dst] = dict(states[tuple(op[2])])
            elif name == 'scale': states[dst] = {k:v*Q(op[2],op[3]) for k,v in states[dst].items()}
            elif name == 'add':
                src = tuple(op[2]); q = Q(op[3],op[4])
                require(dst != src, 'self-add not supported')
                plus(states[dst], states[src], q)
                if phase == 'centers' and src[0] == 'C':
                    require(dst[0] == 'L', 'unexpected scatter target')
                    plus(scatter.setdefault(dst[1],{}), {src[1]:q})
            else: raise ValueError('unknown scalar opcode')
        elif tag == 'center':
            k = event[1]
            require(phase == 'centers' and event[4] == 8 and k not in cuts, 'centre event drift')
            cuts[k] = dict(states['C',k]); bill['rank8'] += 1
            if mute: states['C',k] = {}
        else: require(tag in IDENTITIES, 'unknown projected opcode')
    require(set(cuts) == set(range(8)), 'centre count')
    require(all(not v for k,v in states.items() if k[0] != 'L'), 'private exit not clear')
    return ({i:states['L',i] for i in range(704) if states['L',i] != {i:Q(1)}},
            [cuts[i] for i in range(8)], scatter, dict(sorted(bill.items())))

def setup(data):
    key = lambda x:(x['time'],x['replica'],x['stage'],x['provider_id'])
    callmap = {key(x):x for x in data['global']['calls']}
    events = data['global']['execution_schedule']
    pairs = [(i,callmap[key(e)]) for i,e in enumerate(events) if e['kind']=='local_cover_sweep']
    require([c['time'] for _,c in pairs[:11]] == list(range(11)), 'chronological prefix')
    positions, calls = zip(*pairs[:11])
    require([(calls[i]['stage'],calls[i]['replica'],calls[i]['orientation']) for i in (0,4,10)] ==
            [(0,0,'forward'),(1,0,'backward'),(2,0,'forward')], 'selected pair/continuation changed')
    owners = [[entry[0] for entry in call['owners']] for call in calls]
    for call,ow in zip(calls,owners):
        require(len(ow)==len(set(ow))==704, 'noninjective owner map')
        raw=json.dumps(data['program'][call['orientation']],sort_keys=True,separators=(',',':')).encode()
        require(digest(raw)==call['local_program_sha256'], 'program binding mismatch')
    normal = {o:local(data['program'][o]) for o in ('forward','backward')}
    muted = {o:local(data['program'][o],True) for o in ('forward','backward')}
    for o, (_,cuts,scatter,bill) in normal.items():
        expected = ({i:{i:Q(1),i-112:Q(1)} for i in range(112,224)} if o=='forward' else
                    {i:{i:Q(1),i+112:Q(-1)} for i in range(112)})
        require(normal[o][0] == expected, 'ordinary local endpoint mismatch')
    return calls,owners,positions,normal,muted

def run(calls, owners, normal, muted, columns, mutes=(), omit=()):
    universe = set().union(*map(set,owners))
    state={j:({j:Q(1)} if j in columns else {}) for j in universe}
    cuts={}
    for i,(call,ow) in enumerate(zip(calls,owners)):
        if i in omit: continue
        local_state={r:state[o] for r,o in enumerate(ow)}
        cuts[i]=[evaluate(row,local_state) for row in normal[call['orientation']][1]]
        endpoint=(muted if i in mutes else normal)[call['orientation']][0]
        new={r:evaluate(row,local_state) for r,row in endpoint.items()}
        for r,row in new.items(): state[ow[r]]=row
    return state,cuts

def difference(a,b):
    out={}
    for key in a:
        row=dict(a[key]);plus(row,b[key],-1)
        if row:out[key]=row
    return out

def encode(rows):
    return {str(i):{str(j):str(q) for j,q in sorted(row.items())} for i,row in sorted(rows.items())}
