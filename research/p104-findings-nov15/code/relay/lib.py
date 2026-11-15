"""BIG-RELAY lib (own code): load #7615, helper/fixed split, frame dims, per-frame event index."""
import gzip, json, collections, math
BASE = 'inputs/ATTACK/COURIER226/hit_c226_1.json.gz'
def load(p=BASE): return json.load(gzip.open(p))
f = lambda r: r * math.log(r) if r > 0 else 0.0
def setup(W):
    NP = W['public']; live = W['live']; H = W['hosted']
    mains = set(live) | {r + 112 for r in live} | set(H['X2']) | set(H['Y2'])
    fixed = lambda r: r >= NP or r in mains
    dim = [len(b) for b in W['frames']]
    return NP, mains, fixed, dim
def chains(W):
    ch = {r: [(W['initial'][r], -1)] for r in range(W['public'])}
    for i, e in enumerate(W['program']):
        if e[0] == 'MOVE' and e[1] < W['public']: ch[e[1]].append((e[3], i))
    return ch
def evframe(e):
    if e[0] in ('ADD', 'COPY'): return e[4]
    if e[0] == 'SCALE': return e[3]
    if e[0] in ('INIT', 'CLEAR'): return e[2]
    return None
def hcost(dims): return f(dims[-1] - dims[0]) - sum(f(dims[i + 1] - dims[i]) for i in range(len(dims) - 1))
