"""Shared loader: seed67 auditor geometry, bin model, pinned-engine pricing.
Env: R = tree with the seed67 auditor, selected PR1094 data and engines; MAIN = tree with
research/frontier1094-idle-star-ceiling. Both default to this repository checkout."""
import os, sys, json, gzip, hashlib, importlib.util, math
from pathlib import Path
from collections import Counter, defaultdict
from fractions import Fraction as Q
ROOT = Path(__file__).resolve().parents[3]
R = Path(os.environ.get('R', ROOT)); MAIN = Path(os.environ.get('MAIN', ROOT))
def load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def read(p):
    p = Path(p); b = p.read_bytes(); return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)
a = load('owners', R/'research/t16-owner-audit-seed67/verify.py')
pins = read(R/'research/t16-owner-audit-seed67/SOURCES.json')['inputs']
assert hashlib.sha256((R/a.TEMPLATE).read_bytes()).hexdigest() == pins['template_sha256']
assert hashlib.sha256((R/a.PHASES).read_bytes()).hexdigest() == pins['data_phases_sha256']
assert hashlib.sha256(gzip.decompress(a.WORD.read_bytes())).hexdigest() == pins['word_content_sha256']
w = read(a.WORD); geo = a.geometry(read(R/a.TEMPLATE), read(R/a.PHASES)); widths = a.word_widths(w)
local = a.as_profile(w['report']['local_profile'])
SEL = R/'research/complex-t16-rare-pattern-exchanges/data'
selplan = read(SEL/'PLAN.json'); selspec = read(SEL/'SPEC.json'); selroles = read(SEL/'OWNERS.json.gz')
order = [tuple(x) for x in selplan['order']]
span, callpos = a.windows(geo, order)

def idle_of(roles):
    used = Counter()
    for z in roles: used[z['owner_replica'], z['child'], z['port']] += z['width']
    idle = Counter()
    for (o, c) in span:
        for p in range(a.V):
            f = geo['rank'][c] - used[o, c, p]
            if f: idle[f] += 1
    return idle

def audit(roles, plan=selplan, controls=False):
    idle = idle_of(roles)
    r = a.audit(geo, widths, local, roles, plan, idle, 16)
    if controls: r['controls'] = len(a.controls(geo, widths, local, roles, plan, idle, 16))
    return r

_eng = None
def price(profile, bad=False):
    global _eng
    st = load('idlestar', MAIN/'research/frontier1094-idle-star-ceiling/analyze.py')
    st.ROOT = R; st.ENGINE_ROOT = R/'research/complex-k492-owner-repair/vendor/multicold/engines'
    if _eng is None: _eng = (st, tuple(st.load_engine(n) for n in ('moment', 'base_two_moment', 'outer')))
    baseline = json.loads((R/'research/community-frontier1094-audit/ASSEMBLY.json').read_text())
    return _eng[0].price(Counter({int(k): v for k, v in profile.items()}), bad, baseline, _eng[1])

def compact(roles):
    """Re-serialize offsets as a prefix per bin, preserving within-bin order by old offset."""
    out = [dict(z) for z in roles]; byb = defaultdict(list)
    for i, z in enumerate(out): byb[z['owner_replica'], z['child'], z['port']].append(i)
    for k, v in byb.items():
        off = 0
        for i in sorted(v, key=lambda i: out[i]['offset']):
            out[i]['offset'] = off; off += out[i]['width']
    return out

def relocate(z, owner, child, port):
    pair, side = geo['place'][child]
    return dict(z, owner_replica=owner, child=child, port=port, copy=owner*a.V+port,
                family=owner*a.FAMILIES_PER_REPLICA+(2*pair+side)*a.V+port)

class Model:
    """Bins (owner, child, port); legal-move oracle mirroring R3-R6."""
    def __init__(self, roles):
        self.roles = [dict(z) for z in roles]
        self.cap = {}; self.allowed = {}; self.fam = {}
        for (o, c), (lo, hi) in span.items():
            pair, side = geo['place'][c]
            calls = {t for t, key in enumerate(order) if lo < callpos[key] < hi and (o, pair) != (key[1], geo['stage_pair'][key[0]])}
            for p in range(a.V):
                k = (o, c, p); self.cap[k] = geo['rank'][c]; self.allowed[k] = calls
                self.fam[k] = o*a.FAMILIES_PER_REPLICA+(2*pair+side)*a.V+p
        self.members = defaultdict(set); self.used = Counter(); self.occ = defaultdict(set)
        for i, z in enumerate(self.roles):
            k = (z['owner_replica'], z['child'], z['port']); self.members[k].add(i); self.used[k] += z['width']
            assert self.fam[k] not in self.occ[z['time']]; self.occ[z['time']].add(self.fam[k])
    def bin(self, i): z = self.roles[i]; return (z['owner_replica'], z['child'], z['port'])
    def free(self, k): return self.cap[k] - self.used[k]
    def can(self, i, k, also_free=0):
        z = self.roles[i]; t = z['time']
        return k != self.bin(i) and self.free(k) + also_free >= z['width'] and t in self.allowed[k] and self.fam[k] not in self.occ[t]
    def move(self, i, k):
        z = self.roles[i]; old = self.bin(i); t = z['time']
        self.members[old].discard(i); self.used[old] -= z['width']; self.occ[t].discard(self.fam[old])
        self.members[k].add(i); self.used[k] += z['width']; self.occ[t].add(self.fam[k])
        self.roles[i] = relocate(z, *k); self.roles[i]['offset'] = 10**6  # placeholder; compact() fixes
    def E(self):
        return sum(f*math.log(f) for k in self.cap if (f := self.free(k)) > 1)

def g(f): return f*math.log(f) if f > 1 else 0.0

class Limbo(Model):
    def lift(self, i):
        z = self.roles[i]; k = self.bin(i); t = z['time']
        self.members[k].discard(i); self.used[k] -= z['width']; self.occ[t].discard(self.fam[k]); self._out.add(i)
    def put(self, i, k):
        z = self.roles[i]; t = z['time']
        if not (self.free(k) >= z['width'] and t in self.allowed[k] and self.fam[k] not in self.occ[t]): return False
        self.members[k].add(i); self.used[k] += z['width']; self.occ[t].add(self.fam[k]); self._out.discard(i)
        self.roles[i] = relocate(z, *k); return True
