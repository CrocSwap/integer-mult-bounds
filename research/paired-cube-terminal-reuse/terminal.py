#!/usr/bin/env python3
"""Execute and certify target-accumulating disjoint sinks on PR168's word.

Compiler identity and independent local checker: jamesyc, PR166, following
Dumas--Grenet. Formal packed replay: Chafik Boukhalfa, PR163/164, as adapted
and corrected in PR171. This module integrates the transformed executor,
recomputes its coefficient bound and checks every rational formal column.
Prepared by huxint with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('retained_complex_formal',HERE/'references/pr171_formal_complex.py')
retained=importlib.util.module_from_spec(spec)
spec.loader.exec_module(retained)


def independent_plan(g,witness,word,row,profile,frames,pairs):
    """Run PR166's unchanged checker on freshly reconstructed, hashed inputs."""
    data=dict(graph=g,word=word,frames=witness,
              **{'physical-frames':frames,'physical-pairs':pairs,'profile-before':row,'profile':profile})
    with tempfile.TemporaryDirectory(prefix='paired-terminal-') as temporary:
        work=Path(temporary);pins={}
        for name,value in data.items():
            name+='.json.gz'
            content=gzip.compress((json.dumps(value,separators=(',',':'))+'\n').encode(),mtime=0)
            # Python 3.11/3.12 delegate mtime=0 headers to zlib (OS=3 on
            # Linux); Python 3.13+ emits OS=255. Normalize only this metadata.
            content=content[:9]+b'\xff'+content[10:]
            (work/name).write_bytes(content);pins[name]=sha256(content).hexdigest()
        (work/'result.json').write_text(json.dumps(dict(pins=pins)))
        out=work/'checked.json'
        command=[sys.executable,'-B',str(HERE/'references/pr166_check_sink_accumulator.py'),
                 '--candidate',str(work),'--output',str(out)]
        result=subprocess.run(command,text=True,capture_output=True)
        if result.returncode:
            raise ValueError('Independent terminal compiler rejected the word:\n'+result.stderr)
        plan=json.loads(out.read_text())
    for key in ('seconds','rss_kib'):plan.pop(key,None)
    return plan


class TerminalFormal(retained.Formal):
    def __init__(self,g,word,row,pairs,D,sinks):
        self.sinks=sinks
        self.removed={s['role'] for s in sinks}
        self.by_write={i:s for s in sinks for i in s['writes']}
        self.after={s['writes'][-1]:s for s in sinks}
        # The parent constructs the inherited virtual/physical binding. Our
        # coefficient-bound override starts after we remove the sink slots.
        super().__init__(g,word,row,pairs,D)

    def coefficient_bound(self):
        self.live=[s for s in self.live if s not in self.removed]
        self.slot={s:i for i,s in enumerate(self.live)}
        self.phys=[self.slot.get(self.merge.get(s,s),-1) for s in range(self.R)]
        assert all(s not in self.merge and s not in self.merge.values() and s not in self.deferred for s in self.removed)
        assert all(a not in self.removed and b not in self.removed for i,(a,b,_) in enumerate(self.ops) if i not in self.by_write)
        old=[int(s not in self.deferred and s not in self.merge and s not in self.removed) for s in range(self.R)]
        for (a,b,_),(ca,cb) in zip(self.ops,self.coef):old[a]=abs(ca)*old[a]+abs(cb)*old[b]
        y=[6]*self.v
        for root,s,cs in zip(self.g['roots'],self.word['rootroles'],self.cnum):
            for t,c in zip(root['targets'],cs):y[t]+=abs(c)*old[s]
        b=[1]*len(self.live);top=max([6*x for x in old]+y);done=[]
        def gate(i):
            nonlocal top
            (a,c,_),(ca,cb)=self.ops[i],self.coef[i]
            a,c=self.phys[a],self.phys[c]
            assert a>=0 and c>=0
            b[a]=abs(ca)*b[a]+abs(cb)*b[c];top=max(top,6*b[a]);done.append(i)
        def read(s):
            for t,c in self.D[s].items():y[t]+=abs(c)*b[self.phys[s]]
        def decode(kind):
            for root,s,cs in zip(self.g['roots'],self.word['rootroles'],self.cnum):
                if root['kind']!=kind or s in self.removed:continue
                for t,c in zip(root['targets'],cs):y[t]+=abs(c)*b[self.phys[s]]
        for node,s in self.sources.items():b[self.phys[s]]+=1
        for i in self.phase:gate(i)
        decode('center')
        for item in self.sinks:
            pivot=item['pivot']
            for t in item['targets']:
                if t!=pivot:y[t]+=y[pivot]
        for s in reversed(self.selected):
            if self.deadline.get(s) is None:read(s)
        for i in self.rest:
            for s in self.at.get(i,[]):read(s)
            if i in self.by_write:
                item=self.by_write[i];a,c,_=self.ops[i];ca,cb=self.coef[i]
                assert ca==1 and a==item['role'] and c not in self.removed
                y[item['pivot']]+=3*abs(cb)*b[self.phys[c]]
            else:gate(i)
            if i in self.after:
                item=self.after[i];pivot=item['pivot']
                for t in item['targets']:
                    if t!=pivot:y[t]+=y[pivot]
        decode('side')
        y=[x+12+12 for x in y];top=max(top,max(y))
        for i in reversed(done):
            (a,c,_),(ca,cb)=self.ops[i],self.coef[i];a,c=self.phys[a],self.phys[c]
            b[a]=abs(ca)*b[a]+abs(ca*cb)*b[c];top=max(top,6*b[a])
        for node,s in self.sources.items():b[self.phys[s]]+=1
        return max(top,max(6*(x+1) for x in b))

    def run(self,direction,mutation=None):
        v,R,w=self.v,self.R,self.width
        X=[6<<(w*i) for i in range(v)]
        Y0=[6<<(w*(v+i)) for i in range(v)]
        Z=[6<<(w*(2*v+i)) for i in range(len(self.live))]
        old=[Z[self.phys[s]] if s not in self.deferred and s not in self.merge and s not in self.removed else 0 for s in range(R)]
        # Retain original response columns, including retained ancestors'
        # contributions through the removed roots.
        for (a,b,_),(ca,cb) in zip(self.ops,self.coef):old[a]=ca*old[a]+cb*old[b]
        old=self.decode(old);y=[a-direction*b for a,b in zip(Y0,old)]
        del old
        z=Z[:];done=[]
        def read(s):
            if mutation=='missing-compensation' and s==self.selected[0]:return
            value=z[self.phys[s]];assert value%6==0
            for t,c in self.D[s].items():y[t]-=direction*c*(value//6)
        def gate(i):
            (a,b,_),(ca,cb)=self.ops[i],self.coef[i];a,b=self.phys[a],self.phys[b]
            assert a>=0 and b>=0 and a!=b
            z[a]=ca*z[a]+cb*z[b];done.append(i)
        def decode_current(kind):
            for root,s,cs in zip(self.g['roots'],self.word['rootroles'],self.cnum):
                if root['kind']!=kind or s in self.removed:continue
                value=z[self.phys[s]];assert value%6==0
                for t,c in zip(root['targets'],cs):y[t]+=direction*c*(value//6)
        for node,s in self.sources.items():z[self.phys[s]]+=X[node-1]
        for i in self.phase:gate(i)
        decode_current('center')
        for k,item in enumerate(self.sinks):
            if mutation=='missing-pre-shear' and k==0:continue
            pivot=item['pivot']
            for t in item['targets']:
                if t!=pivot:y[t]-=y[pivot]
        for s in reversed(self.selected):
            if self.deadline.get(s) is None:read(s)
        first=self.sinks[0]['writes'][0] if self.sinks else None
        for i in self.rest:
            for s in self.at.get(i,[]):read(s)
            if i in self.by_write:
                item=self.by_write[i];a,b,_=self.ops[i];ca,cb=self.coef[i]
                assert ca==1 and a==item['role'] and z[self.phys[b]]%2==0
                if not (mutation=='missing-accumulation' and i==first):
                    y[item['pivot']]+=direction*cb*(z[self.phys[b]]//2)
            else:gate(i)
            if i in self.after:
                item=self.after[i];pivot=item['pivot']
                if mutation=='missing-post-shear' and item==self.sinks[0]:continue
                for t in item['targets']:
                    if t!=pivot:y[t]+=y[pivot]
        decode_current('side')
        def K(xs):
            out=[]
            for start in range(0,v,8):
                qs=self.g['inputs'][start:start+8];values=xs[start:start+8]
                for q in qs:
                    value=sum((1 if (q^r).bit_count()==6 else -1 if (q^r).bit_count()==2 else 0)*x for r,x in zip(qs,values))
                    assert value%2==0;out.append(value//2)
            return out
        mixed=K(X);assert K(mixed)==X
        for t,x in enumerate(mixed):y[t]+=direction*x
        assert y==[a+direction*b for a,b in zip(Y0,X)],'every rational target coefficient after terminal accumulation'
        for i in reversed(done):
            (a,b,_),(ca,cb)=self.ops[i],self.coef[i];a,b=self.phys[a],self.phys[b]
            z[a]=ca*(z[a]-cb*z[b])
        for node,s in self.sources.items():z[self.phys[s]]-=X[node-1]
        assert z==Z,'every retained physical dirty column restored'
        return dict(direction=direction,source_columns=v,target_columns=v,dirty_columns=len(self.live),
                    every_formal_column=True,all_original_target_values_preserved=True,
                    retained_original_dirty_response_columns=True,all_dirty_slots_restored=True)


def certify(g,witness,word,row,profile,frames,pairs):
    plan=independent_plan(g,witness,word,row,profile,frames,pairs)
    assert plan['eligible_count']>0
    D,receipt=retained.adjoint(g,word,row['R'])
    formal=TerminalFormal(g,word,row,pairs,D,plan['sinks'])
    columns=[formal.run(d) for d in (1,-1)]
    controls=[]
    for mutation in ('missing-pre-shear','missing-accumulation','missing-post-shear','missing-compensation'):
        try:formal.run(1,mutation)
        except AssertionError:controls.append(mutation)
        else:raise ValueError('Terminal formal mutation accepted: '+mutation)
    output=dict(profile)
    output.pop('scalar_replay',None)
    output.update(physical_R=plan['new_physical_R'],W_per_vertex=plan['new_W'],
                  rank_per_vertex=plan['new_rank'],child_histogram=plan['child_histogram'],
                  local_histogram=plan['local_histogram'],target_data_histogram=plan['target_histogram'],
                  removed_terminal_roles=plan['eligible_count'])
    output['checks']=dict(output['checks'],terminal_target_events_checked=True,
                          every_rational_column_checked=True,
                          original_dirty_response_columns_retained=True)
    output['scalar_replay']=dict(field='Q',both_shear_directions=True,
                                all_formal_columns=True,slots=len(formal.live),
                                controls=controls)
    return dict(profile=output,plan=plan,adjoint=receipt,columns=columns,controls=controls,
                coefficient_bound=formal.bound,packed_digit_bits=formal.width,
                base_exceeds_twice_bound=formal.base>2*formal.bound)
