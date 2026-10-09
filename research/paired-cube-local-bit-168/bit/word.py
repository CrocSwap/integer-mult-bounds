"""Independent complete formal admission of the PR168-v4 physical bit word with 556 frame overrides and 34 terminal sinks.

Retains eumemic's exact integer linear algebra and original decoder/geometry
predicates. Physical chains, chronological formal columns and paid moments
use our separate verifier. No producer or foreign aggregate checker runs.
"""
from pathlib import Path
from collections import Counter,defaultdict
from hashlib import sha256
import gzip,importlib.util,json,sys,time
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parents[2]
PKG=HERE.parent
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def read(p):
    raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
old=module('own_frozen_word',PKG/'bit/base_word.py');need=old.need

class Candidate(old.Candidate):
    def __init__(self):
        self.module=backend=module('exact_integer_backend',SOURCE/'research/paired-cube-bit/check_paired_cube_bit.py')
        C=backend.Checker.__new__(backend.Checker);self.C=C;C.mut=None
        B=SOURCE/'research/paired-cube-bit/out';F=SOURCE/'references/paired-cube/bit-physical'
        self.input_paths=[B/'graph_p12.json',B/'profile_p12.json',F/'word_p12.json.gz',F/'frames_p12.json.gz',F/'kchron_p12.json']
        C.g,C.prof,C.w,C.fr,C.k=map(read,self.input_paths)
        C.h=C.g['h'];C.v=C.g['v'];C.frames()
        self.h,self.v,self.R=C.h,C.v,C.prof['R'];self.w,self.g,self.k=C.w,C.g,C.k
        self.ops=self.w['ops'];self.nf={int(n):f for n,f in self.w['node_frame'].items()}
        self.source={int(n):s for n,s in self.w['sources'].items()};self.gauge={z['role']:z for z in self.w['gauges']}
        need(len(self.gauge)==len(self.w['gauges']),'unique gauge roles')
        self.original_opframe=tuple(self.nf[n] for a,b,n in self.ops);self.opframe=self.w['op_frame'][:]
        need(len(self.opframe)==len(self.ops),'complete operation frame vector')
        self.changed_frames=[i for i,(a,b) in enumerate(zip(self.original_opframe,self.opframe)) if a!=b]
        self.phase1=sorted(self.w['phase1']);phase=set(self.phase1)
        self.rest=[i for i in range(len(self.ops)) if i not in phase];order=self.phase1+self.rest
        self.position={i:p for p,i in enumerate(order)};pos={i:p for p,i in enumerate(self.rest)}
        self.order=[z['role'] for z in reversed(self.w['gauges'])]
        self.role_ops=defaultdict(list)
        for i in order:
            for s in self.ops[i][:2]:self.role_ops[s].append(i)
        need(all(xs==sorted(xs) for xs in self.role_ops.values()),'execution order preserves every role chronology')
        self.first={s:pos.get(xs[0],-1) for s,xs in self.role_ops.items()}
        self.last={s:pos.get(xs[-1],-1) for s,xs in self.role_ops.items()}
        self.endframe={s:self.opframe[xs[-1]] for s,xs in self.role_ops.items()}
        self.rootroles=set(self.w['rootroles']);self.rootkind={s:r['kind'] for s,r in zip(self.w['rootroles'],self.g['roots'])}
        need(len(self.rootroles)==len(self.w['rootroles']),'unique root roles')
        reads={int(s):p for s,p in self.w['reads'].items()}
        need(set(reads)<=set(self.gauge),'only gauges have explicit reads')
        self.readtime={s:reads.get(s,len(self.phase1))-len(self.phase1) for s in self.order}
        need(all(0<=self.readtime[s]<=self.first[s] for s in self.order),'all gauge reads after centre phase and before first use')
        self.pairs=[[b,a] for a,b in self.w['pairs']];self.donor=dict(self.pairs)
        need(len(self.donor)==len(self.pairs)==len(set(self.donor.values())),'one-to-one aliases')
        need(not set(self.donor)&set(self.donor.values()),'disjoint donor recipient sets')
        for b,d in self.pairs:
            need(d not in self.gauge and d not in self.rootroles and b in self.gauge,'ungauged non-root donor and gauged recipient')
            need(self.last[d]<self.readtime[b],'donor dead before recipient read')
        self.phys={s:self.donor.get(s,s) for s in range(self.R)}
        need(len(set(self.phys.values()))==self.R-len(self.pairs),'physical slot count')
        need(all(self.phys[a]!=self.phys[b] for a,b,n in self.ops),'distinct physical gate ports')
        C.chains=self.base_chains
        self.baseline_opframe=tuple(self.opframe)
        proposal=PKG/'selected/bit/overrides.json'
        changes=read(proposal)
        need(changes['source_head']=='4a3c769e5c5430e7114c4d3e099ff34664677f17','proposal commit pin')
        need(changes['source_word_sha256']==sha256((F/'word_p12.json.gz').read_bytes()).hexdigest(),'proposal physical word pin')
        seen=set()
        for i,B in changes['frames']:
            need(type(i) is int and 0<=i<len(self.ops) and i not in seen,'unique operation override')
            f=self.register(B)
            need(not(C.sub(f,self.opframe[i]) and C.sub(self.opframe[i],f)),'override is an actual changed subspace')
            self.opframe[i]=f;seen.add(i)
        need(len(seen)==556,'selected changed operation count')
        self.endframe={s:self.opframe[xs[-1]] for s,xs in self.role_ops.items()}
        self.changed_frames=[i for i,(a,b) in enumerate(zip(self.original_opframe,self.opframe)) if a!=b]
        self.input_paths.append(proposal)

    def base_chains(self):
        """Reconstruct phase/gauge/source contracts; row() counts physical paths."""
        C,w,h,v=self.C,self.w,self.h,self.v
        order=self.phase1+self.rest
        roleprev={};pred=[]
        for i,(a,b,n) in enumerate(self.ops):
            pred.append((roleprev.get(a,-1),roleprev.get(b,-1)));roleprev[a]=roleprev[b]=i
        pending=[roleprev[s] for s in self.rootroles if self.rootkind[s]=='center' and s in roleprev];closure=set()
        while pending:
            i=pending.pop()
            if i not in closure:closure.add(i);pending.extend(j for j in pred[i] if j>=0)
        need(closure==set(self.phase1),'phase one is exactly centre closure')
        content=[0]*self.R
        for n,s in self.source.items():content[s]=1<<n
        for i in order:
            a,b,n=self.ops[i];args=self.g['args'][n]
            if content[a]:need(args is not None and {content[a],content[b]}=={C.sup[t] for t in args},'actual addition operands')
            else:need(content[b]==C.sup[n],'actual copied node value')
            content[a]|=content[b]
        co=[set() for _ in range(self.R)]
        for r,s in zip(self.g['roots'],w['rootroles']):co[s].update(r['targets'])
        for i in reversed(order):
            a,b,n=self.ops[i];co[b].update(co[a])
        touched={s for i in self.phase1 for s in self.ops[i][:2]}
        for s,z in self.gauge.items():
            need(s not in self.source.values() and s not in touched,'gauge untouched in phase one and source injection')
            need(set(z['targets'])==co[s] and C.dimf[z['frame']]==z['dim']>0,'gauge dimension and complete response support')
        src=Counter();members=Counter();labels=list(map(set,self.g['labels']))
        for e in self.k['entries']:
            c,d,f,cap=e['carrier'],e['passive'],e['mix_frame'],e['deliver_frame']
            need(len(labels[c]&labels[d])==1,'orthogonal partner pair')
            need(C.dimf[f]==2 and C.in_frame(C.chi[c],f) and C.in_frame(C.chi[d],f),'partner mix span')
            need(C.sub(f,cap) and all(self.module.dot(C.cov[t],u)==0 for t in e['receivers'] for u in C.B[cap]),'partner mix delivery cap')
            need(e['carrier_chain']==[w['source_frame'][c],f,cap,w['full_frame']] and e['passive_chain']==[w['source_frame'][d],f,w['full_frame']],'exact partner chains')
            root=self.g['roots'][e['deliver_after_root']]
            need(root['kind']=='side' and sorted(e['receivers'])==sorted(root['targets']),'partner delivery at own receiver root')
            for chain in (e['carrier_chain'],e['passive_chain']):
                for a,b in zip(chain,chain[1:]):
                    need(C.sub(a,b),'nested source chronology');src[C.dimf[b]-C.dimf[a]]+=1
            members[c]+=1;members[d]+=1
        need(all(members[s]==1 for s in range(v)),'every source in one partner pair')
        return Counter(),Counter(),src,self.R
