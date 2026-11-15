#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Native helper-plan extractor (our NETCAUX lane; loader and requirement extraction from our REBUILDKIT lane, inlined).
Standard library only.  Reads a word and returns its helper layer as a plan: helper routes and stays, every
helper-involving event typed pickup / delivery / relay / scale, meetings (helper<->helper exchanges grouped per stay
pair), requirement blocks (maximal runs of helper->r deliveries on a non-helper r) linked to their deliveries, exact
pi-states (non-helper coordinates) at every stay entry and exit, and the requirement-space state basis (mod 2^61-1).
recost(plan) re-costs the helper layer from the routes alone (sum over helpers of f(end - birth) - sum f(steps),
f(x) = x ln x); reemit_check(plan, path) regenerates every helper-touching event from the plan and compares.
On #7546: recost 9,975.447669, 1,101 helpers, 3,427 interior stops, 70,714 helper events re-emitted identically,
state basis rank 253.
usage: python3 nativeplan.py WORD.json.gz     (prints the summary; the API returns the plan dict)
"""
import sys, os, json, gzip, collections, time, math, bisect
from fractions import Fraction as Q
P = 2 ** 61 - 1


def tomod(d):
    return {k: (v.numerator % P) * pow(v.denominator % P, P - 2, P) % P for k, v in d.items()}


def fcost(r):
    return r * math.log(r) if r > 0 else 0.0


def span(b):
    s = {0}
    for v in b:
        s |= {x ^ v for x in s}
    return frozenset(s)

class Word:
    def __init__(self, path):
        W=json.load(gzip.open(path,'rt')) if str(path).endswith('.gz') else json.load(open(path))
        self.W=W; n=W['public']; self.n=n; self.N=n+W['owned_fields']
        self.dim=[len(b) for b in W['frames']]; self.sp=[span(b) for b in W['frames']]
        live=W['live']; H=W['hosted']
        cls={}
        for r in live: cls[r]='X'; cls[r+112]='Y'
        for r in H['X2']: cls[r]='X2'
        for r in H['Y2']: cls[r]='Y2'
        for r in range(n): cls.setdefault(r,'h')
        for r in range(n,self.N): cls[r]='o'
        self.cls=cls
        # routes: list of (frame, t_enter) for public
        cur=list(W['initial'])+[None]*W['owned_fields']
        route={r:[(W['initial'][r],-1)] for r in range(n)}
        ops=[]  # (t, op, r, s, q, frame)
        olife=collections.defaultdict(list)
        for t,e in enumerate(W['program']):
            op=e[0]
            if op=='MOVE':
                r=e[1]; cur[r]=e[3]
                if r<n: route[r].append((e[3],t))
                else: olife[r][-1]['moves'].append((e[2],e[3],t))
            elif op=='INIT': cur[e[1]]=e[2]; olife[e[1]].append(dict(init=t,frame=e[2],moves=[]))
            elif op=='CLEAR': cur[e[1]]=None; olife[e[1]][-1]['clear']=t
            elif op=='SCALE': ops.append((t,'SCALE',e[1],None,e[2],e[3]))
            else: ops.append((t,op,e[1],e[2],e[3],e[4]))
        self.route=route; self.ops=ops; self.olife=olife; self.T=len(W['program'])
    def loss(self, r):
        rt=self.route[r]; d=[self.dim[fr] for fr,_ in rt]
        return fcost(d[-1]-d[0])-sum(fcost(d[i+1]-d[i]) for i in range(len(d)-1))


def extract(w, granular=(), ish=None):
    granular = set(granular)
    n=w.n; cls=w.cls
    if ish is None: ish=[cls[r]=='h' for r in range(n)]+[False]*(w.N-n)
    rows=[{r:Q(1)} if r<n else {} for r in range(w.N)]
    cur=list(w.W['initial'])+[None]*(w.N-n)
    def pi(R): return {k:v for k,v in R.items() if not ish[k]}
    blocks=[]; open_b={}
    traj={r:[(-1,cur[r],{r:Q(1)})] for r in range(n) if not ish[r]}
    def close(r):
        b=open_b.pop(r,None)
        if b is None: return
        d=pi(rows[r])
        for k,v in b.pop('pi0').items():
            nv=d.get(k,0)-v
            if nv: d[k]=nv
            else: d.pop(k,None)
        b['v']=d; blocks.append(b)
    for t,e in enumerate(w.W['program']):
        op=e[0]; r=e[1]
        if op=='MOVE':
            close(r); cur[r]=e[3]
            if not ish[r]: traj[r].append((t,cur[r],traj[r][-1][2]))
            continue
        if op=='INIT':
            close(r); rows[r]={}; cur[r]=e[2]; traj.setdefault(r,[]).append((t,cur[r],{})); continue
        if op=='CLEAR':
            close(r); rows[r]={}; cur[r]=None; traj[r].append((t,None,{})); continue
        if op=='SCALE':
            close(r); q=Q(e[2]); rows[r]={k:v*q for k,v in rows[r].items()}
        else:
            s=e[2]; q=Q(e[3])
            if not ish[r]:
                if ish[s]:
                    if r not in open_b: open_b[r]=dict(r=r,frame=e[4],t0=t,pi0=pi(rows[r]),nops=0)
                    open_b[r]['nops']+=1; open_b[r]['t1']=t
                else:
                    close(r); close(s)
            R=rows[r]
            for k,v in rows[s].items():
                nv=R.get(k,0)+q*v
                if nv: R[k]=nv
                else: R.pop(k,None)
        if not ish[r]: traj[r].append((t,cur[r],pi(rows[r])))
        if op in ('ADD','COPY') and r in granular and r in open_b: close(r)
    for r in list(open_b): close(r)
    return blocks, traj

def qstr(q):
    q = Q(q); return str(q.numerator) if q.denominator == 1 else '%d/%d' % (q.numerator, q.denominator)

class Echelon:
    """mod-P echelon basis with combination tracking; basis element k = k-th independent vector added."""
    def __init__(self): self.piv = {}; self.comb = {}; self.n = 0; self.src = []
    def _red(self, x, cx):
        while x:
            p = max(x)
            if p not in self.piv: return x, cx, p
            c = x[p]
            for k, v in self.piv[p].items():
                nv = (x.get(k, 0) - c * v) % P
                if nv: x[k] = nv
                else: x.pop(k, None)
            for k, v in self.comb[p].items():
                nv = (cx.get(k, 0) - c * v) % P
                if nv: cx[k] = nv
                else: cx.pop(k, None)
        return x, cx, None
    def add(self, u, tag=None):
        x, cx, p = self._red(dict(u), {self.n: 1})
        if not x: return None
        inv = pow(x[p], P - 2, P)
        self.piv[p] = {k: v * inv % P for k, v in x.items()}; self.comb[p] = {k: v * inv % P for k, v in cx.items()}
        self.n += 1; self.src.append(tag); return self.n - 1
    def coords(self, u):
        """(coeffs over basis elements as dict k->c mod P, residual vector dict). u = sum coeffs*basis + residual."""
        x, cx, p = self._red(dict(u), {})
        # u - sum(c_k b_k): _red subtracts multiples; cx accumulates -(...) of comb; sign: x = u + sum cx*basis(k)
        co = {k: (-v) % P for k, v in cx.items()}
        return co, x

def extract_plan(path, log=print):
    t0 = time.time()
    w = Word(path); W = w.W; n = w.n; cls = w.cls; dim = w.dim; N = w.N
    H = [r for r in range(n) if cls[r] == 'h']; Hs = set(H)
    Vd = max(dim); 
    blocks, traj = extract(w)
    log('reqx blocks', len(blocks), '%.0fs' % (time.time() - t0))
    prog = W['program']
    # exact replay tracking helper stays
    rows = [{r: Q(1)} if r < n else {} for r in range(N)]
    cur = list(W['initial']) + [None] * W['owned_fields']
    stay = {h: 0 for h in H}                                 # current stay index of helper
    ish = [r in Hs for r in range(n)] + [False] * (N - n)
    def pi(R): return {k: v for k, v in R.items() if not ish[k]}
    stays = {h: [dict(frame=W['initial'][h], t_in=-1, t_out=None, dim=dim[W['initial'][h]], pi_in={}, pi_out=None)] for h in H}
    for h in H: stays[h][0]['pi_in'] = {}  # born holding only own token (pi = 0)
    events = []            # helper-involving ADD/COPY/SCALE: dict
    for t, e in enumerate(prog):
        op = e[0]; r = e[1]
        if op == 'MOVE':
            if r in Hs:
                s = stays[r][-1]; s['t_out'] = t; s['pi_out'] = pi(rows[r])
                stays[r].append(dict(frame=e[3], t_in=t, t_out=None, dim=dim[e[3]], pi_in=pi(rows[r]), pi_out=None))
            cur[r] = e[3]; continue
        if op == 'INIT': rows[r] = {}; cur[r] = e[2]; continue
        if op == 'CLEAR': rows[r] = {}; cur[r] = None; continue
        if op == 'SCALE':
            q = Q(e[2]); rows[r] = {k: v * q for k, v in rows[r].items()}
            if r in Hs: events.append(dict(t=t, op='SCALE', dst=r, src=None, q=e[2], frame=e[3], kind='scale', dst_stay=len(stays[r]) - 1, src_stay=None))
            continue
        s = e[2]; q = Q(e[3])
        dh, sh = r in Hs, s in Hs
        if dh or sh:
            kind = 'relay' if (dh and sh) else 'pickup' if dh else 'delivery'
            events.append(dict(t=t, op=op, dst=r, src=s, q=e[3], frame=e[4], kind=kind,
                               dst_stay=len(stays[r]) - 1 if dh else None, src_stay=len(stays[s]) - 1 if sh else None))
        R = rows[r]
        for k, v in rows[s].items():
            nv = R.get(k, 0) + q * v
            if nv: R[k] = nv
            else: R.pop(k, None)
    for h in H:
        s = stays[h][-1]; s['t_out'] = None; s['pi_out'] = pi(rows[h])
    log('replay done %.0fs' % (time.time() - t0))
    # helper routes
    helpers = {}
    for h in H:
        rt = w.route[h]; d = [dim[f] for f, _ in rt]
        helpers[h] = dict(route=[(f, t) for f, t in rt], dims=d, birth_frame=rt[0][0], end_frame=rt[-1][0],
                          birth_dim=d[0], end_dim=d[-1], loss=w.loss(h), nstops=len(rt) - 2)
    # stay-level role + event index
    ev_by_stay = collections.defaultdict(list)
    for i, ev in enumerate(events):
        if ev['dst'] in Hs: ev_by_stay[(ev['dst'], ev['dst_stay'])].append(i)
        if ev['src'] in Hs and ev['kind'] != 'scale': ev_by_stay[(ev['src'], ev['src_stay'])].append(i)
    # meetings: helper<->helper exchanges grouped by unordered stay pair
    meet = collections.defaultdict(list)
    for i, ev in enumerate(events):
        if ev['kind'] == 'relay':
            a = (ev['dst'], ev['dst_stay']); b = (ev['src'], ev['src_stay']); meet[tuple(sorted((a, b)))].append(i)
    meetings = [dict(a=k[0], b=k[1], interior=any(0 < x[1] < len(stays[x[0]]) - 1 for x in k), frame=events[v[0]]['frame'], t0=events[v[0]]['t'], t1=events[v[-1]]['t'], events=v) for k, v in sorted(meet.items(), key=lambda kv: events[kv[1][0]]['t'])]
    # blocks <-> deliveries: for each reqx block (r, t0..t1) the helper->r delivery event indices
    dl = collections.defaultdict(list)
    for i, ev in enumerate(events):
        if ev['kind'] == 'delivery': dl[ev['dst']].append(i)
    bl = []
    for b in blocks:
        lst = dl[b['r']]; ts = [events[i]['t'] for i in lst]
        lo = bisect.bisect_left(ts, b['t0']); hi = bisect.bisect_right(ts, b['t1'])
        ids = [i for i in lst[lo:hi]]
        bl.append(dict(r=b['r'], frame=b['frame'], dim=dim[b['frame']], t0=b['t0'], t1=b['t1'], nops=b['nops'], v=b['v'],
                       deliveries=ids, helpers=sorted({(events[i]['src'], events[i]['src_stay']) for i in ids})))
    # state basis: independent interior requirement vectors (frames dim not in {0, V})
    E = Echelon()
    for i, b in enumerate(bl):
        if b['v'] and b['dim'] not in (0, Vd):
            E.add(tomod(b['v']), tag=i)
    log('state basis rank %d' % E.n)
    nbasis_hits = 0
    for h in H:
        for si, s in enumerate(stays[h]):
            for key in ('pi_in', 'pi_out'):
                v = s[key]
                if v is None: s[key + '_c'] = None; continue
                co, res = E.coords(tomod(v)) if v else ({}, {})
                s[key + '_c'] = dict(coef=co, in_span=not res, residual_support=len(res))
    inspan = sum(1 for h in H for s in stays[h] for key in ('pi_out_c',) if s[key] and s[key]['in_span'])
    log('stay-exit states in requirement span: %d / %d' % (inspan, sum(len(stays[h]) for h in H)))
    plan = dict(fmt='netcaux-plan/1', word=os.path.abspath(str(path)), n=n, N=N, V_dim=Vd,
                frames_dim=dim, helpers=helpers, stays=stays, events=events, meetings=meetings, blocks=bl,
                basis=dict(rank=E.n, block_ids=E.src), cls={r: cls[r] for r in range(n)}, owned=N - n)
    return plan

def recost(plan):
    """Re-cost from the plan's helper routes only (cost function f(x) = x ln x)."""
    tot = 0.0
    for h, H in plan['helpers'].items():
        d = H['dims']; tot += fcost(d[-1] - d[0]) - sum(fcost(d[i + 1] - d[i]) for i in range(len(d) - 1))
    return tot

def recost_from_stays(plan):
    tot = 0.0
    for h, ss in plan['stays'].items():
        d = [s['dim'] for s in ss]; tot += fcost(d[-1] - d[0]) - sum(fcost(d[i + 1] - d[i]) for i in range(len(d) - 1))
    return tot

def reemit_helper_events(plan):
    """Regenerate every helper-touching program event (MOVE of helpers, ADD/COPY/SCALE with a helper end) from the plan."""
    out = {}
    for h, H in plan['helpers'].items():
        rt = H['route']
        for i in range(1, len(rt)):
            out[rt[i][1]] = ['MOVE', h, rt[i - 1][0], rt[i][0], False]
    for ev in plan['events']:
        out[ev['t']] = ['SCALE', ev['dst'], ev['q'], ev['frame']] if ev['kind'] == 'scale' else [ev['op'], ev['dst'], ev['src'], ev['q'], ev['frame']]
    return out

def reemit_check(plan, path=None):
    w = Word(path or plan['word']); Hs = set(plan['helpers']); prog = w.W['program']; n = w.n
    want = {}
    for t, e in enumerate(prog):
        if e[0] == 'MOVE' and e[1] in Hs: want[t] = list(e)
        elif e[0] in ('ADD', 'COPY') and (e[1] in Hs or e[2] in Hs): want[t] = list(e)
        elif e[0] == 'SCALE' and e[1] in Hs: want[t] = list(e)
    got = reemit_helper_events(plan)
    return got == want, len(want)



def summary(plan):
    ev = collections.Counter(e['kind'] for e in plan['events'])
    return dict(recost=recost(plan), helpers=len(plan['helpers']), stops=sum(h['nstops'] for h in plan['helpers'].values()),
                events=dict(ev), meetings=len(plan['meetings']), blocks=len(plan['blocks']), basis_rank=plan['basis']['rank'])


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(2)
    plan = extract_plan(sys.argv[1], log=lambda *a: None)
    print(json.dumps(summary(plan)))
    ok, m = reemit_check(plan); print('re-emitted helper events identical:', ok, m)
