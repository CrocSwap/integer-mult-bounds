"""Literal retained primitive oracle and interval enumeration, independent of engine.

@woklerx, substantial OpenAI Codex assistance, Apache-2.0. Imports only the
credited/pinned Sagar Thakrar lowerer, never the new search/transform/replay code.
"""
from collections import defaultdict
from fractions import Fraction as F
import gzip,hashlib,importlib.util,json,random,tarfile
from pathlib import Path

P=Path(__file__).resolve().parent;R=P.parents[1]
def need(v,s):
    if not v:raise ValueError(s)
def sha(b):return hashlib.sha256(b).hexdigest()

def run():
    sources=json.loads((P/'SOURCES.json').read_bytes())
    for n,h in sources['files'].items():
        b=(R/n).read_bytes();need(sha(b if n.endswith('.gz') else b.replace(b'\r\n',b'\n'))==h,'source hash')
    # Deliberately read actual selected1094 provider bytes, not the1042 alias.
    with tarfile.open(R/'research/community-frontier1094-audit/selected-replay.tar.gz') as t:
        def obj(n):
            b=t.extractfile('candidate/strict/global8/base/providers/gauge44/'+n).read()
            need(sha(b)==sources['archive_members']['slots/local/'+n],'selected provider identity')
            return json.loads(gzip.decompress(b))
        word=obj('CANONICAL-WORD.json.gz');old=obj('LOCAL-PROGRAMS.json.gz')
    new=json.loads(gzip.decompress((P/'CANDIDATE-PROGRAMS.json.gz').read_bytes()))
    cert=json.loads((P/'CERTIFICATE.json').read_bytes())
    spec=importlib.util.spec_from_file_location('retained_lower',R/'research/complex-dyadic-lowering/lower.py')
    lib=importlib.util.module_from_spec(spec);spec.loader.exec_module(lib)
    need(len(lib.lower(['add',['L',0],['L',1],1,1]))==2,'unit shortcut')
    helpers=set(range(224,704))-set(word['centers'])
    need(sorted(helpers)==cert['helpers'] and len(helpers)==477,'complete helper domain')
    counts={};lattice=0;primitive_steps=0
    for orient in ('forward','backward'):
        previous=[e[1] for e in old[orient] if e[0]=='scalar']
        candidate=[e[1] for e in new[orient] if e[0]=='scalar']
        need([e for e in old[orient] if e[0]!='scalar']==[e for e in new[orient] if e[0]!='scalar'],'physical event stream')
        by=defaultdict(list)
        for g in previous:
            if g[0]=='add':
                for index,sign in ((1,1),(2,-1)):
                    if g[index][0]=='L':by[g[index][1]].append((g,sign))
        optima={row['helper']:row for row in cert['orientations'][orient]['optima']}
        for h in sorted(helpers):
            # Enumerate every integer between and beyond extreme coefficient
            # valuations; do not use the new engine's finite candidate list.
            gates=by[h];limits=[0]
            for g,sign in gates:
                x=abs(F(g[3],g[4]));e=0
                while x.denominator>1:x*=2;e-=1
                while x.numerator%2==0:x/=2;e+=1
                limits.append(-sign*e)
            original=sum(len(lib.lower(g)) for g,s in gates)
            costs=[]
            for k in range(min(limits)-2,max(limits)+3):
                total=2*abs(k)
                for g,s in gates:
                    q=F(g[3],g[4])*(F(2)**(s*k));t=g[:3]+[q.numerator,q.denominator]
                    total+=len(lib.lower(t))
                costs.append((total-original,abs(k),k));lattice+=1
            best=min(costs);row=optima[h]
            need((best[0],best[2])==(row['delta'],row['best_k']),'independent interval optimum')
            need(costs[0][0]-costs[1][0]==2+len(gates) and costs[-1][0]-costs[-2][0]==2+len(gates),'strict linear tails')
        oldops=[op for g in previous for op in lib.lower(g)]
        newops=[op for g in candidate for op in lib.lower(g)]
        need(len(oldops)-len(newops)==166,'full literal primitive saving')
        need(len(oldops)==cert['orientations'][orient]['prices']['copy-init']['before']['real_primitives'],'literal baseline count')
        need(len(newops)==cert['orientations'][orient]['prices']['copy-init']['after']['real_primitives'],'literal candidate count')
        # Three independent exact dirty input evaluations, including arbitrary W.
        rng=random.Random(3200+(orient=='backward'))
        registers=[('L',i) for i in range(704)]+[('C',i) for i in range(8)]+[('W',0)]
        for case in range(3):
            initial={r:F(rng.randrange(-10**5,10**5),2**rng.randrange(5)) for r in registers}
            if case==1:initial.update({('L',i):F((-1)**i*(i+1)**3,8) for i in range(224,704)})
            if case==2:initial.update({('L',i):F(0) for i in range(224)})
            expected=dict(initial)
            for i in range(112):
                if orient=='forward':expected['L',112+i]+=initial['L',i]
                else:expected['L',i]-=initial['L',112+i]
            for i in range(8):expected['C',i]=F(0)
            expected['W',0]=F(0)
            for ops in (oldops,newops):
                state=dict(initial)
                for op in ops:
                    tag,t=op[:2]
                    if tag=='clear':state[t]=F(0)
                    elif tag=='copy':state[t]=state[op[2]]
                    elif tag=='double':state[t]*=2
                    elif tag=='halve':state[t]/=2
                    elif tag=='negate':state[t]=-state[t]
                    elif tag=='add':state[t]+=state[op[2]]
                    elif tag=='subtract':state[t]-=state[op[2]]
                    else:raise ValueError('primitive tag')
                need(state==expected,'literal primitive arbitrary dirt oracle')
                primitive_steps+=len(ops)
        counts[orient]=dict(baseline_real=len(oldops),candidate_real=len(newops),saving_real=166)
    return dict(status='PASS_INDEPENDENT_LITERAL_LOWERING_AND_INTEGER_INTERVAL_ENUMERATION',helpers_per_orientation=477,integer_lattice_evaluations=lattice,exact_dirty_cases=6,baseline_and_candidate_primitive_steps=primitive_steps,counts=counts)

if __name__=='__main__':print(json.dumps(run(),sort_keys=True))
