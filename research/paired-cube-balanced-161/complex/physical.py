#!/usr/bin/env python3
"""Exact audit of the fused PR161 complex physical word, including every input.

Chafik Boukhalfa with OpenAI Codex assistance. Apache-2.0.
The scalar signed graph, binary frames and original compiler are credited to
icekylinx (PR144); searched modules and physical reuse baseline to eumemic
(PR157 and PR161), with the lineage retained there. New checks independently execute
all physical aliases, deadline reads and inverse cleanup on an injective
packed formal basis, using a separately derived absolute coefficient bound.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import defaultdict,Counter
from hashlib import sha256
import argparse,gzip,json,sys,time,copy,gc,resource


def adjoint(g,word,R):
    D=[{} for _ in range(R)]
    for root,s in zip(g['roots'],word['rootroles']):
        for t,c in zip(root['targets'],root['coefficients']):
            c=Q(c)*6;assert c.denominator==1;D[s][t]=D[s].get(t,0)+int(c)
    for (a,b,_),(ca,cb) in zip(reversed(word['ops']),reversed(word['opcoeff'])):
        for t,c in D[a].items():D[b][t]=D[b].get(t,0)+cb*c
        if ca<0:D[a]={t:-c for t,c in D[a].items()}
    D=[{t:c for t,c in row.items() if c} for row in D]
    for z in word['selected']:assert set(D[z['role']])<=set(z['targets'])
    receipt=dict(nonzeros=sum(map(len,D)),max_numerator_over_6=max(abs(c) for row in D for c in row.values()),L1=sum(abs(c) for row in D for c in row.values()),gauge_supports_contained=True)
    selected={z['role']:D[z['role']] for z in word['selected']}
    return selected,receipt

class Formal:
    def __init__(self,g,word,row,pairs,D):
        self.g,self.word,self.row,self.D=g,word,row,D;self.v=g['v'];self.R=row['R']
        self.merge={b:a for a,b,t in pairs};assert len(self.merge)==len(pairs)==len(set(self.merge.values()))
        assert not set(self.merge)&set(self.merge.values())
        self.live=[s for s in range(self.R) if s not in self.merge];self.slot={s:i for i,s in enumerate(self.live)}
        self.phys=[self.slot[self.merge.get(s,s)] for s in range(self.R)]
        self.sources={int(x):s for x,s in word['sources'].items()}
        self.selected=[z['role'] for z in word['selected']];self.deferred=set(self.selected)
        self.phase=sorted(word['phase1']);pset=set(self.phase);self.rest=[i for i in range(len(word['ops'])) if i not in pset]
        self.deadline={b:t for a,b,t in pairs};self.at=defaultdict(list)
        for b,t in self.deadline.items():
            if t is not None:self.at[t].append(b)
        self.ops=[tuple(x) for x in word['ops']];self.coef=[tuple(x) for x in word['opcoeff']]
        assert all(a in (-1,1) and b in (-1,1) for a,b in self.coef)
        assert all(self.phys[a]!=self.phys[b] for a,b,x in self.ops)
        self.cnum=[[int(6*Q(c)) for c in r['coefficients']] for r in g['roots']]
        self.bound=self.coefficient_bound()
        self.width=8*((self.bound.bit_length()+2+7)//8);self.base=1<<self.width
        assert self.base>2*self.bound
    def coefficient_bound(self):
        # Unscaled formal variables: a physical slot has coefficients bounded
        # by its absolute row sum b. Actual packed slots use 6 times the basis.
        g,word,v,R=self.g,self.word,self.v,self.R
        old=[int(s not in self.deferred and s not in self.merge) for s in range(R)]
        for (a,b,_),(ca,cb) in zip(self.ops,self.coef):old[a]=abs(ca)*old[a]+abs(cb)*old[b]
        y=[6]*v
        for root,s,cs in zip(g['roots'],word['rootroles'],self.cnum):
            for t,c in zip(root['targets'],cs):y[t]+=abs(c)*old[s]
        b=[1]*len(self.live);top=max([6*x for x in old]+y)
        for node,s in self.sources.items():b[self.phys[s]]+=1
        done=[]
        def gate(i):
            nonlocal top
            (a,c,_),(ca,cb)=self.ops[i],self.coef[i];a,c=self.phys[a],self.phys[c]
            b[a]=abs(ca)*b[a]+abs(cb)*b[c];top=max(top,6*b[a]);done.append(i)
        def read(s):
            for t,c in self.D[s].items():y[t]+=abs(c)*b[self.phys[s]]
        for i in self.phase:gate(i)
        # All root/center positive readouts may be safely bounded by their
        # value after the complete M: centers are closed in phase one.
        for s in reversed(self.selected):
            if self.deadline.get(s) is None:read(s)
        for i in self.rest:
            for s in self.at.get(i,[]):read(s)
            gate(i)
        for root,s,cs in zip(g['roots'],word['rootroles'],self.cnum):
            for t,c in zip(root['targets'],cs):y[t]+=abs(c)*b[self.phys[s]]
        # K has four +/-1/2 source contributions in every output row.
        y=[x+12+6 for x in y];top=max(top,max(y))
        for i in reversed(done):
            (a,c,_),(ca,cb)=self.ops[i],self.coef[i];a,c=self.phys[a],self.phys[c]
            b[a]=abs(ca)*b[a]+abs(ca*cb)*b[c];top=max(top,6*b[a])
        for node,s in self.sources.items():b[self.phys[s]]+=1;top=max(top,6*b[self.phys[s]])
        return top
    def decode(self,z,kind=None):
        out=[0]*self.v
        for root,s,cs in zip(self.g['roots'],self.word['rootroles'],self.cnum):
            if kind is not None and root['kind']!=kind:continue
            for t,c in zip(root['targets'],cs):out[t]+=c*z[s]
        assert all(x%6==0 for x in out);return [x//6 for x in out]
    def run(self,direction,mutation=None):
        v,R,w=self.v,self.R,self.width
        X=[6<<(w*i) for i in range(v)];Y0=[6<<(w*(v+i)) for i in range(v)];Z=[6<<(w*(2*v+i)) for i in range(len(self.live))]
        # Compute precisely the initial reads D[s]z_s without expanding
        # nongauged D: exact transposition identity D=JM gives this cheaper
        # independent algebraic evaluation. All late physical reads below
        # use the explicitly computed integer adjoint rows.
        old=[Z[self.phys[s]] if s not in self.deferred and s not in self.merge else 0 for s in range(R)]
        for (a,b,_),(ca,cb) in zip(self.ops,self.coef):old[a]=ca*old[a]+cb*old[b]
        old=self.decode(old);y=[y-direction*z for y,z in zip(Y0,old)];del old;gc.collect()
        z=Z[:];done=[]
        def read(s):
            if mutation=='missing-read' and s==self.selected[0]:return
            value=z[self.phys[s]];assert value%6==0
            for t,c in self.D[s].items():y[t]-=direction*c*(value//6)
        def gate(i):
            (a,b,_),(ca,cb)=self.ops[i],self.coef[i];a,b=self.phys[a],self.phys[b]
            z[a]=ca*z[a]+cb*z[b];done.append(i)
        for node,s in self.sources.items():z[self.phys[s]]+=X[node-1]
        for i in self.phase:gate(i)
        physical_virtual=[z[self.phys[s]] for s in range(R)]
        center=self.decode(physical_virtual,'center');del physical_virtual
        for t,c in enumerate(center):y[t]+=direction*c
        del center
        late=[b for b,t in self.deadline.items() if t is not None];early=late[-1] if mutation=='early-read' and late else None
        for s in reversed(self.selected):
            if self.deadline.get(s) is None or s==early:read(s)
        for i in self.rest:
            for s in self.at.get(i,[]):
                if s!=early:read(s)
            gate(i)
        physical_virtual=[z[self.phys[s]] for s in range(R)]
        side=self.decode(physical_virtual,'side');del physical_virtual
        for t,c in enumerate(side):y[t]+=direction*c
        del side
        def K(xs):
            out=[]
            for a in range(0,v,8):
                block=xs[a:a+8];qs=self.g['inputs'][a:a+8]
                for q in qs:
                    value=sum((1 if (q^r).bit_count()==6 else -1 if (q^r).bit_count()==2 else 0)*x for r,x in zip(qs,block));assert value%2==0;out.append(value//2)
            return out
        mixed=K(X);assert K(mixed)==X
        for t,x in enumerate(mixed):y[t]+=direction*x
        assert y==[y+direction*x for y,x in zip(Y0,X)],'full formal output map'
        for i in reversed(done):
            (a,b,_),(ca,cb)=self.ops[i],self.coef[i];a,b=self.phys[a],self.phys[b]
            z[a]=ca*(z[a]-cb*z[b])
        for node,s in self.sources.items():z[self.phys[s]]-=X[node-1]
        assert z==Z,'all physical dirty columns restored'
        return dict(direction=direction,every_formal_column=True,source_columns=v,target_columns=v,dirty_columns=len(self.live),K_and_inverse=True,all_aliases_and_deadline_reads=True,all_physical_dirty_slots_restored=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--source',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.source/'scripts'))
    from verify_fused import verify
    from paired_cube_physical import physical
    start=time.time();pins=json.loads((a.candidate/'result.json').read_text())['pins'];data={}
    for name in ['graph','baseline','frames','word','profile-before','physical-frames','physical-pairs','profile']:
        p=a.candidate/(name+'.json.gz');assert sha256(p.read_bytes()).hexdigest()==pins[p.name];data[name]=json.loads(gzip.decompress(p.read_bytes()))
    g,b,w,word,row=[data[n] for n in ['graph','baseline','frames','word','profile-before']]
    finite=verify(g,b,w,word,row);print('PASS exact signed scalar pairs and pre-reuse complete physical frame word',flush=True)
    actual=physical(g,w,word,row,data['physical-frames'],data['physical-pairs']);assert json.loads(json.dumps(actual))==data['profile'];print('PASS all descended frames, nested chains, aliases and target read chronology',flush=True)
    D,adj=adjoint(g,word,row['R']);formal=Formal(g,word,row,data['physical-pairs'],D);print('PASS exact adjoint; formal coefficient bound',formal.bound,'digit bits',formal.width,flush=True)
    columns=[formal.run(d) for d in (1,-1)];print('PASS every formal column under both shear signs',flush=True)
    mutations={}
    for tag in ['missing-read','early-read']:
        try:formal.run(1,tag)
        except AssertionError:mutations[tag]='REJECTED'
        else:raise AssertionError('accepted mutation '+tag)
    cs=[Q(c) for r in g['roots'] for c in r['coefficients']]
    assert set(cs)<={Q(1,2),Q(-1,2),Q(1,3),Q(-1,6)} and 3*row['q']<2**15
    local=4*(row['c']+row['v'])+10*row['v']+4*row['h']*row['v']+4*row['h']**2+8*row['h']+8+2*row['h']+8*row['R']*row['v']*(row['total_M_operations']+16)+32*row['v']
    scalar=dict(c=row['c'],q=row['q'],M_operations=row['total_M_operations'],logical_R=row['R'],physical_R=actual['physical_R'],handoffs=actual['pairs'],scalar_denominators_divide=6,fixed_odd_divisor=3,gate_and_inverse_coefficients=[-1,1],decoder_coefficients=sorted(map(str,set(cs))),three_q_less_than_2pow15=True,binary_dirty_read_bits=row['total_M_operations']+16,local_group_upper=local,scope='Conservative inherited virtual-word bill retained after aliasing, including all compensated reads. Alias and frame route choices are finite permutations/Clifford adapters; their separate global movement bill remains an assembly obligation.')
    result=dict(status='PASS exact fused physical candidate, all formal source/target/dirty columns',source_sha256={str(p):sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(__file__).with_name('verify_fused.py'),a.source/'scripts/paired_cube_physical.py',a.source/'scripts/paired_cube/frames.py',a.source/'notes/general-clifford-frames.tex']},input_sha256=pins,pre_reuse_finite=finite,physical=actual,exact_adjoint=adj,formal=dict(columns=columns,absolute_coefficient_bound=formal.bound,packed_digit_bits=formal.width,base_exceeds_twice_bound=True),mutations=mutations,scalar_bound=scalar,seconds=time.time()-start,maxrss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,foreign_producer_replays=0,scope='Finite candidate audit only. General exact Clifford and shared cover contracts, analytic supplier bridge, and paid global multiplication assembly remain separate obligations.')
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({k:result[k] for k in ['status','seconds','maxrss','scalar_bound']}),flush=True)
if __name__=='__main__':main()
