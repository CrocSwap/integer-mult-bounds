#!/usr/bin/env python3
"""Reusable independent formal checks for a physical partner-pair bit word.

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
    def exact_frames(self):
        C = self.C
        C.decoder(); C.geometry()
        for i in self.changed_frames:
            f = self.opframe[i]; x = self.ops[i][2]; bits = C.sup[x]
            need(C.nondeg(f), 'replacement operation frame nondegenerate')
            while bits:
                low = bits&-bits; s=low.bit_length()-1; bits-=low
                need(C.in_frame(C.chi[s],f), 'value span in replacement operation frame')
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
        C,h,v=self.C,self.h,self.v
        _,baseline_Y,src,_=C.chains()
        seq=defaultdict(list)
        for i,(a,b,x) in enumerate(self.ops):
            seq[a].append(self.opframe[i]);seq[b].append(self.opframe[i])
        for j,s in enumerate(self.w['rootroles']):seq[s].append(self.w['root_frame'][j])
        start={b:self.w['source_frame'][x] for x,b in self.source.items()}
        start.update({b:z['frame'] for b,z in self.gauge.items()})
        recipient={d:b for b,d in self.pairs}
        H=Counter()
        for s in range(self.R):
            if s in self.donor:continue
            chain=list(seq[s])
            if s in recipient:
                b=recipient[s];chain += [self.gauge[b]['frame']]+seq[b]
            chain.append(self.w['full_frame'])
            prev=start.get(s);dp=0 if prev is None else C.dimf[prev]
            if s in self.source.values():H[1]+=1
            for f in chain:
                need(prev is None or C.sub(prev,f),'physical role chain nested')
                d=C.dimf[f]
                if d>dp:H[d-dp]+=1
                prev,dp=f,d
        for j,r in enumerate(self.g['roots']):
            if r['kind']=='center':H[C.dimf[self.w['root_frame'][j]]]+=1
        Y=Counter();current=[None]*v
        def read(t,f):
            old=current[t];d=0 if old is None else C.dimf[old]
            need(old is None or C.sub(old,f),'actual target frame chronology')
            if C.dimf[f]>d:Y[C.dimf[f]-d]+=1
            current[t]=f
        for b in sorted(self.order,key=lambda b:self.readtime[b]):
            for t in self.gauge[b]['targets']:read(t,self.gauge[b]['frame'])
        deliveries=defaultdict(list)
        for e in self.k['entries']:deliveries[e['deliver_after_root']].append(e)
        for j,r in enumerate(self.g['roots']):
            if r['kind']!='center':
                for t in r['targets']:read(t,self.w['root_frame'][j])
            for e in deliveries[j]:
                for t in e['receivers']:read(t,e['deliver_frame'])
        for t,f in enumerate(current):
            need(f is not None and all(self.module.dot(C.cov[t],b)==0 for b in C.B[f]),'final target cap')
            gap=h-1-C.dimf[f]
            if gap:Y[gap]+=1
        need(sum(r*n for r,n in Y.items())==v*(h-1),'target rank mass')
        hist=Counter()
        for part in (H,Y,src):
            for r,n in part.items():
                if r and n:hist[r]+=3*n
        for b,z in self.gauge.items():
            if b not in self.donor:hist[3*z['dim']]+=1
        hist[2]+=2*v
        hist={r:n for r,n in sorted(hist.items()) if n}
        need(all(0<r<3*h and n>0 for r,n in hist.items()),'positive proper child bins')
        R=self.R-len(self.pairs);W=2*v+R;mass=sum(r*n for r,n in hist.items());m=3*h
        need(W*m-mass==C.prof['deficit_per_vertex'],'reuse preserves telescoping deficit')
        return dict(h=h,v=v,R=R,virtual_R=self.R,reused_registers=len(self.pairs),W_per_vertex=W,m=m,
            loss=C.prof['loss'],rank_per_vertex=mass,deficit_per_vertex=W*m-mass,
            child_histogram=hist,maxchild=max(hist),selected_roles=len(self.gauge)-len(self.pairs),
            selected_rank_histogram=dict(Counter(z['dim'] for b,z in self.gauge.items() if b not in self.donor)),
            changed_operation_frames=len(self.changed_frames),
            frames_not_contained_in_original=sum(not C.sub(self.opframe[i],self.original_opframe[i]) for i in self.changed_frames),
            physical_target_histogram=dict(Y),physical_internal_histogram=dict(H),
            foreign_producer_replays=0)

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
        return dict(ring=str(ring),formal_variables=2*v+len(regs),
            target_contract='F2 identity' if ring==2 else 'integer defining decoder',
            identity=ring==2,defining_decoder=True,all_dirty_and_source_columns_restored=True)
