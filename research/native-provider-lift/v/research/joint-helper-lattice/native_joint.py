"""Joint entrance/exit/contact retiming, with literal and phase replay.

Apache-2.0. Substantial OpenAI assistance. Uses the credited native retiming
implementation of PR4441 and preserves PR4447's missing-span predecessor.
"""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import json,gzip,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'research/fresh-helper-boundary'))
import native as F
need=F.need

def construct(patch=None):
    c=F.read(F.BASE/'THREE-base-FULL-IDENTITY-CANONICAL.json.gz')
    original=F.read(F.BASE/'THREE-base-FULL-IDENTITY-NATIVE.json.gz')
    parent=F.read(F.HERE/'CHANGES.json')
    maps={d:F.gates(p) for d,p in original.items()}
    need(set(maps['forward'])==set(maps['backward']),'Same scalar contact inventory')
    for key in maps['forward']:
        f=original['forward'][maps['forward'][key]];b=original['backward'][maps['backward'][key]]
        need(b[1]==F.dual(f[1]) and b[2]==f[2],'Retained exact dual scalar words')
    for key,field in [('entrances','start'),('exits','final')]:
        for r,old,new in parent[key]:
            need(c[field][r]==old,'Parent boundary pin');c[field][r]=new
    for phase,ordinal,old,new in parent['gates']:
        for d,p in original.items():
            i=maps[d][phase,ordinal];need(p[i][2]==old,'Parent scalar pin');p[i][2]=new
    prior=F.read(ROOT/'research/missing-join-frame/PATCH.json')
    need(prior['phase']=='B' and prior['ordinal']==480,'Exact prior contact')
    prior_frame=len(c['frames']);c['frames'].append(prior['new_basis'])
    for d,p in original.items():
        i=maps[d]['B',480];need(p[i][2]==prior['old_frame'],'Missing-span parent pin');p[i][2]=prior_frame
    baseline=deepcopy(c)
    before={d:F.synthesize(c,p) for d,p in original.items()}
    patch=F.read(HERE/'PATCH.json') if patch is None else patch
    need(patch['source_head']=='322e0ec764aa7ef7801383feb1f656e460dd8bed','Pinned candidate head')
    labels={frozenset(F.span(b)):i for i,b in enumerate(c['frames'])}
    def label(b):
        s=frozenset(F.span(b));need(len(s)==2**len(b),'Independent binary basis')
        if s not in labels:labels[s]=len(c['frames']);c['frames'].append(b)
        return labels[s]
    seen=set();counts=Counter()
    for move in patch['changes']:
        phase,r=move['phase'],move['ordinal'];key=(phase,r)
        need(key not in seen,'No duplicate changed boundary/contact');seen.add(key)
        a,b=F.span(move['old']),F.span(move['new']);need(a!=b,'No unchanged patch entry')
        f=label(move['new']);counts[phase]+=1
        if phase in ('entrance','exit'):
            need(224<=r<632,'Only independent helper boundaries may change')
            field='start' if phase=='entrance' else 'final'
            need(F.span(c['frames'][c[field][r]])==a,'Current helper source pin')
            c[field][r]=f
        else:
            for d,p in original.items():
                i=maps[d][key];need(F.span(c['frames'][p[i][2]])==a,'Current scalar source pin');p[i][2]=f
    programs={d:F.synthesize(c,p) for d,p in original.items()}
    return c,programs,baseline,before,counts

def run(phase_check=True):
    c,programs,baseline,before,counts=construct()
    V=F.load(ROOT/'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py','joint_rows')
    X=F.load(ROOT/'research/kappa-rebuild/complex/native_extensions.py','joint_literal')
    checks={};profiles={}
    for d,p in programs.items():
        rows,rec=X.literal_replay(V,c,p,d=='backward')
        for r in range(632):need(rows['L',r]==V.expected(('L',r),[],d=='backward',False),'All 632 arbitrary-input endpoints')
        profiles[d]=Counter({int(k):v for k,v in rec['paid_profile'].items()})
        rebound=deepcopy(c);rebound['local_profile']=dict(profiles[d])
        rec['second_literal']=V.replay(p,rebound,[],d=='backward',False);checks[d]=rec
    need(profiles['forward']==profiles['backward'],'Both complete native rank tariffs')
    H=Counter()
    for r in range(224,632):
        a,b=c['start'][r],c['final'][r]
        need(F.span(c['frames'][a])<F.span(c['frames'][b]),'Strictly productive arbitrary helper')
        H[len(c['frames'][b])-len(c['frames'][a])]+=1
    need(sum(H.values())==408,'No discarded or duplicate helper input')
    edges=lambda p:{(e[3],e[4]) for e in p if e[0]=='climb'}
    new_edges=edges(programs['forward'])-edges(before['forward'])
    helper_edges={(c['start'][r],c['final'][r]) for r in range(224,632)}
    physical=[]
    if phase_check:
        ce=F.load(ROOT/'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py','joint_clifford')
        P=F.load(ROOT/'research/kappa-function-composition/complex/prune_native.py','joint_phase_decode')
        for a,b in sorted(new_edges|helper_edges):
            op=ce.canonical_frame(9,c['frames'][a]).adjoint().then(ce.canonical_frame(9,c['frames'][b]))
            rank=len(c['frames'][b])-len(c['frames'][a]);directions={}
            for d in ('forward','backward'):
                actual=P.conjugate(ce,op) if d=='backward' else op
                rec=X.N.lower_exact(P,ce,actual)
                need(rec['rank']==rank,'Exact rank, Clifford tableau and absolute phase')
                directions[d]=rec
            physical.append({'old':a,'new':b,'rank':rank,'recipes':directions})
    # A false emitted rank must be detected by the second literal interpreter.
    bad=deepcopy(programs['forward']);next(e for e in bad if e[0]=='climb')[5]+=1
    rejected=False
    try:
        rebound=deepcopy(c);rebound['local_profile']=dict(profiles['forward']);V.replay(bad,rebound,[],False,False)
    except (ValueError,AssertionError):rejected=True
    need(rejected,'Changed emitted rank rejected')
    return {'status':'PASS_JOINT_HELPER_LATTICE_632_COLUMNS_BOTH_ORIENTATIONS',
        'helpers':dict(sorted(H.items())),'paid':dict(sorted(profiles['forward'].items())),
        'changes':dict(sorted(counts.items())),'native':checks,
        'new_physical_edges_and_boundaries':physical,'new_edges':len(new_edges),
        'wrong_emitted_rank_rejected':rejected}

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--skip-phase',action='store_true');args=ap.parse_args()
    result=run(not args.skip_phase)
    if args.write:
        need(not args.skip_phase,'Complete phase receipt required')
        (HERE/'NATIVE.json.gz').write_bytes(gzip.compress((json.dumps(result,indent=2,sort_keys=True)+'\n').encode(),mtime=0))
    elif not args.skip_phase:need(json.loads(json.dumps(result))==F.read(HERE/'NATIVE.json.gz'),'Deterministic native receipt')
    print(json.dumps({k:v for k,v in result.items() if k not in ('native','new_physical_edges_and_boundaries')},sort_keys=True))
