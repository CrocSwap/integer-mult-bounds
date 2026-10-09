#!/usr/bin/env python3
"""Complete formal check of the retained PR161 partner-pair bit word.

The supplied frozen inputs are source-pinned. This never runs their producer.
The Z check is of the defining integer decoder; only its F2 reduction is I.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
from collections import Counter, defaultdict
import importlib.util
import json
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / 'research/paired-cube-bit'
P = 12
if sys.flags.optimize: raise SystemExit('refusing -O')


def need(ok, msg):
    if not ok:
        raise ValueError(msg)

class Candidate:
    def __init__(self, pairs):
        spec = importlib.util.spec_from_file_location('paired_checker', BASE / 'check_paired_cube_bit.py')
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        self.C = C = module.Checker(BASE / 'out', P)
        self.module = module
        C.frames()
        self.h, self.v, self.R = C.h, C.v, C.prof['R']
        self.w, self.g, self.k = C.w, C.g, C.k
        self.ops = C.w['ops']; self.nf = {int(k): v for k, v in C.w['node_frame'].items()}
        self.source = {int(k): v for k, v in C.w['sources'].items()}
        self.gauge = {z['role']: z for z in C.w['gauges']}
        self.opframe = [self.nf[x] for a,b,x in self.ops]
        self.changed_frames = []
        if (HERE/'descent.json').exists():
            descent = json.loads((HERE/'descent.json').read_text())
            need(descent['p'] == P, 'descent parameter')
            for i, B in descent['frames']:
                f = self.register(B)
                need(C.sub(f,self.opframe[i]), 'new operation frame descends')
                self.opframe[i] = f; self.changed_frames.append(i)
        self.order = [z['role'] for z in reversed(C.w['gauges'])]
        phase1 = set(C.w['phase1'])
        self.phase1 = [i for i in range(len(self.ops)) if i in phase1]
        self.rest = [i for i in range(len(self.ops)) if i not in phase1]
        pos = {i: j for j, i in enumerate(self.rest)}
        self.first, self.last, self.endframe = {}, {}, {}
        for i, (a, b, x) in enumerate(self.ops):
            for s in (a, b):
                self.first.setdefault(s, pos.get(i, -1))
                self.last[s] = pos.get(i, -1)
                self.endframe[s] = self.opframe[i]
        self.readtime = {}; next_target = {}
        for b in reversed(self.order):
            targets = self.gauge[b]['targets']
            f = self.gauge[b]['frame']
            latest = min([self.first[b]] + [next_target[t][1] for t in targets if t in next_target and not C.sub(next_target[t][0],f)])
            self.readtime[b] = latest
            for t in targets:
                if t not in next_target or not C.sub(next_target[t][0],f):next_target[t] = (f,latest)
        need(all(t >= 0 for t in self.readtime.values()), 'gauges untouched in phase one')
        target_frames={}
        for b in sorted(self.order,key=lambda b:self.readtime[b]):
            f=self.gauge[b]['frame']
            for t in self.gauge[b]['targets']:
                need(t not in target_frames or C.sub(target_frames[t],f),'actual target read frame chronology')
                target_frames[t]=f
        self.rootroles = set(self.w['rootroles'])
        self.pairs = [list(p) for p in pairs]
        self.donor = dict(pairs)
        need(len(self.donor) == len(pairs), 'one donor per recipient')
        need(len(set(self.donor.values())) == len(pairs), 'one recipient per donor')
        need(set(self.donor) <= set(self.gauge), 'recipient has entrance gauge')
        need(not (set(self.donor.values()) & self.rootroles), 'root roles stay live through readout')
        for b, d in pairs:
            need(d != b and self.last[d] < self.readtime[b], 'donor dies before recipient read')
        self.phys = {}
        for s in range(self.R):
            r = s; seen = set()
            while r in self.donor:
                need(r not in seen, 'physical alias cycle'); seen.add(r); r = self.donor[r]
            self.phys[s] = r
        need(len(set(self.phys.values())) == self.R-len(pairs), 'physical register count')

    def exact_frames(self):
        C = self.C
        C.decoder(); C.geometry()
        for i in self.changed_frames:
            f = self.opframe[i]; x = self.ops[i][2]; bits = C.sup[x]
            need(C.nondeg(f), 'descended operation frame nondegenerate')
            while bits:
                low = bits&-bits; s=low.bit_length()-1; bits-=low
                need(C.in_frame(C.chi[s],f), 'value span in descended operation frame')
        for b, d in self.pairs:
            need(C.sub(self.endframe[d], self.gauge[b]['frame']), 'exact Q donor-to-birth containment')
            need(C.nondeg(self.endframe[d]) and C.nondeg(self.gauge[b]['frame']), 'handoff endpoints nondegenerate')

    def register(self, rows):
        C = self.C
        B,_ = self.module.reduce_rows(rows,self.h if hasattr(self,'h') else C.h)
        B = tuple(sorted(map(tuple,B),key=lambda r:next(i for i,x in enumerate(r) if x)))
        if not hasattr(self,'frame_ids'):
            self.frame_ids = {}
        if B in self.frame_ids: return self.frame_ids[B]
        f=max(C.B)+1; A,_=self.module.kernel(B,C.h)
        C.B[f],C.A[f],C.dimf[f]=B,A,len(B);self.frame_ids[B]=f
        return f


    def row(self):
        C, h, v = self.C, self.h, self.v
        oldH, Y, src, R = C.chains()
        H=Counter(); seq=defaultdict(list)
        for i,(a,b,x) in enumerate(self.ops):
            seq[a].append(self.opframe[i]);seq[b].append(self.opframe[i])
        for j,s in enumerate(self.w['rootroles']):seq[s].append(self.w['root_frame'][j])
        start={b:self.w['source_frame'][s] for s,b in self.source.items()}
        start.update({b:z['frame'] for b,z in self.gauge.items()})
        for s in range(self.R):
            prev=start.get(s);dp=0 if prev is None else C.dimf[prev]
            if s in self.source.values():H[1]+=1
            for f in seq[s]+[self.w['full_frame']]:
                need(prev is None or C.sub(prev,f),'physical role chain nested')
                d=C.dimf[f]
                if d>dp:H[d-dp]+=1
                prev,dp=f,d
        for j,r in enumerate(self.g['roots']):
            if r['kind']=='center':H[C.dimf[self.w['root_frame'][j]]]+=1
        initial = Counter()
        for part in (H, Y, src):
            for r, n in part.items():
                if r and n: initial[r] += 3*n
        for z in self.w['gauges']: initial[3*z['dim']] += 1
        initial[2] += 2*v
        need(sum(r*n for r,n in H.items()) == sum(r*n for r,n in oldH.items()), 'frame descent preserves mass')
        hist = Counter(initial); zero = 0
        for b, d in self.pairs:
            dd, f = C.dimf[self.endframe[d]], self.gauge[b]['dim']
            hist[3*f] -= 1
            if h-dd: hist[h-dd] -= 3
            if f-dd: hist[f-dd] += 3
            else: zero += 1
        hist = {r:n for r,n in sorted(hist.items()) if n}
        need(all(r > 0 and n > 0 for r,n in hist.items()), 'positive child bins')
        R -= len(self.pairs); W = 2*v+R; mass = sum(r*n for r,n in hist.items()); m = 3*h
        need(W*m-mass == C.prof['deficit_per_vertex'], 'reuse preserves telescoping deficit')
        return dict(h=h,v=v,R=R,virtual_R=self.R,reused_registers=len(self.pairs),W_per_vertex=W,m=m,
                    loss=C.prof['loss'],rank_per_vertex=mass,deficit_per_vertex=W*m-mass,
                    child_histogram=hist,maxchild=max(hist),selected_roles=len(self.gauge)-len(self.pairs),
                    selected_rank_histogram=dict(Counter(z['dim'] for b,z in self.gauge.items() if b not in self.donor)),
                    zero_rank_handoffs=zero,changed_operation_frames=len(self.changed_frames),foreign_producer_replays=0)

    def adjoint(self):
        adj = [dict() for _ in range(self.R)]
        for r,s in zip(self.g['roots'], self.w['rootroles']):
            for t in r['targets']: adj[s][t] = adj[s].get(t,0)+1
        for a,b,_ in reversed(self.ops):
            for t,c in adj[a].items(): adj[b][t] = adj[b].get(t,0)+c
        return adj

    def formal(self, ring, tamper=None):
        """All source, target and dirty-register columns; no random sampling."""
        v, phys = self.v, self.phys
        regs = sorted(set(phys.values())); index = {r:2*v+j for j,r in enumerate(regs)}
        if ring == 2:
            unit = lambda i: 1<<i
            def accum(dst,val,c): return dst ^ val if c&1 else dst
        else:
            unit = lambda i: {i:1}
            def accum(dst,val,c):
                out = dict(dst)
                for i,z in val.items():
                    k = out.get(i,0)+c*z
                    if k: out[i]=k
                    else: out.pop(i,None)
                return out
        x = [unit(s) for s in range(v)]; y = [unit(v+t) for t in range(v)]
        a = {r:unit(index[r]) for r in regs}
        adj = self.adjoint()
        at = defaultdict(list)
        for b in self.order: at[self.readtime[b]].append(b)
        done = []
        stale_used = False
        def read(b):
            nonlocal stale_used
            if tamper == 'omit_compensation' and b == self.order[0]: return
            value = a[phys[b]]
            if tamper == 'stale' and b in self.donor and not stale_used:
                value = unit(index[phys[b]]); stale_used = True
            for t,c in adj[b].items(): y[t] = accum(y[t],value,-c)
        def op(i,sign):
            b,d,_ = self.ops[i]
            a[phys[b]] = accum(a[phys[b]],a[phys[d]],sign)
        for b in range(self.R):
            if b not in self.gauge: read(b)
        for s,b in self.source.items(): a[phys[b]] = accum(a[phys[b]],x[s],1)
        for i in self.phase1: op(i,1); done.append(i)
        for r,b in zip(self.g['roots'],self.w['rootroles']):
            if r['kind']=='center':
                for t in r['targets']:y[t]=accum(y[t],a[phys[b]],1)
        for j,i in enumerate(self.rest):
            for b in at[j]: read(b)
            op(i,1); done.append(i)
        for b in at[len(self.rest)]: read(b)
        deliveries=defaultdict(list)
        for e in self.k['entries']:deliveries[e['deliver_after_root']].append(e)
        broken=False
        for j,(r,b) in enumerate(zip(self.g['roots'],self.w['rootroles'])):
            if r['kind']!='center':
                for t in r['targets']: y[t] = accum(y[t],a[phys[b]],1)
            for e in deliveries[j]:
                c,d = e['carrier'],e['passive']
                x[c] = accum(x[c],x[d],1)
                for t in e['receivers']:
                    if tamper == 'missing_partner' and not broken: broken=True;continue
                    y[t] = accum(y[t],x[c],1)
        for e in self.k['entries']:
            x[e['carrier']] = accum(x[e['carrier']],x[e['passive']],-1)
        for i in reversed(done): op(i,-1)
        for s,b in self.source.items(): a[phys[b]] = accum(a[phys[b]],x[s],-1)
        need(all(a[r] == unit(index[r]) for r in regs), 'all dirty register columns restored')
        need(all(x[s] == unit(s) for s in range(v)), 'all source columns restored')
        if ring == 2:
            want = [accum(unit(v+t),unit(t),1) for t in range(v)]
        else:
            # Integer lift: the exact defining decoder, whose reduction is I over F2.
            support = [{s:1} for s in range(v)]
            for aa,bb in self.g['args'][v:]: support.append(accum(support[aa],support[bb],1))
            want = [unit(v+t) for t in range(v)]
            for r in self.g['roots']:
                for t in r['targets']: want[t] = accum(want[t],support[r['node']],1)
            for e in self.k['entries']:
                for t in e['receivers']:
                    want[t] = accum(want[t],unit(e['carrier']),1)
                    want[t] = accum(want[t],unit(e['passive']),1)
        need(y == want, 'all target columns equal defining decoder')
        return dict(ring=str(ring),formal_variables=2*v+len(regs),identity=True)
