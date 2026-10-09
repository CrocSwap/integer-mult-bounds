#!/usr/bin/env python3
"""Fresh h25 coarse-bit profile, exact projector audit and full dirty replay.

Apache-2.0. Thomas DiFiore with OpenAI Codex assistance. Reuses the frozen
merged-span physical word and its credited compiler/storage lineage. The
whole-rank opposite-bank/stopped interface is icekylinx's PR104; see bit-proof.md.
Only the standard library is needed here. The isolated replay imports the frozen
inherited checker and its source-pinned standard-library helpers.
"""
import sys
if not __debug__:raise RuntimeError('Assertions required; run without -O')
sys.dont_write_bytecode=True
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import argparse,copy,gzip,importlib.util,json,os,subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT=ROOT/'research/merged-span-frames'
WORD_SHA='555e16849cae04c68565f421b0266c8129f2266298aba6c1ccaaeaac08eafdf5'

def digest(raw):return sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,indent=2)+'\n'

def replay_only(word,output):
    """A separate interpreter keeps inherited generic module names isolated."""
    assert digest(word.read_bytes())==WORD_SHA
    sys.path.insert(0,str(PARENT))
    spec=importlib.util.spec_from_file_location('frozen_merged_bit_check',PARENT/'check.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    strict=module.strict_word(json.loads(gzip.decompress(word.read_bytes())))
    result=json.loads(json.dumps(module.replay(word)))
    expected=json.loads((PARENT/'replay-25.json').read_text())
    assert result==expected,'Fresh full dirty replay differs from frozen witness'
    output.write_text(canonical(dict(strict_word=strict,replay=result)))
    print('PASS inherited strict scatter/index checks and full arbitrary-dirty basis replay h25')

def projector_classes(h,frames):
    classes=Counter()
    for c,u in frames:
        assert type(c)is int and type(u)is int and 0<c<=u<(1<<h)and not c&~u
        k=c.bit_count();assert k in(1,2,3)
        r=1 if c==u else u.bit_count()-k
        if k==3:assert c==u and r==1
        else:assert c!=u and r>=1
        classes[k,r]+=1
    assert h!=9
    checked={}
    for k,r in sorted(classes):
        if k==3:
            V=[tuple(int(j<3)for j in range(h))];G=[[Q(18)]];Gi=[[Q(1,18)]]
        else:
            a=3-k;V=[tuple(int(j<k)+a*int(j==k+i)for j in range(h))for i in range(r)]
            G=[[Q(9*(a*a*int(i==j)+k-1))for j in range(r)]for i in range(r)]
            denom=a*a+(k-1)*r
            Gi=[[Q(int(i==j),9*a*a)-Q(k-1,9*a*a*denom)for j in range(r)]for i in range(r)]
        actual=[[Q(9*sum(a*b for a,b in zip(x,y))-sum(x)*sum(y))for y in V]for x in V]
        assert actual==G
        assert all(sum(G[i][z]*Gi[z][j]for z in range(r))==int(i==j)for i in range(r)for j in range(r))
        checked[f'{k}:{r}']=dict(count=classes[k,r],rank=r,gram_inverse_exact=True,
            positive_gram_eigenvalues=[18]if k==3 else[9*(3-k)**2,9*((3-k)**2+(k-1)*r)])
    return checked

def validate_paid(parts,h,v,R):
    assert set(parts)=={'literal_incidences','side_growth_and_lines','copied_centers','retirements'}
    assert parts['side_growth_and_lines']==Counter({2:3*v,1:3*v}),'Side hyperplane growth must be rank2 plus rank1'
    assert parts['copied_centers']==Counter({h-1:h,1:h}),'Retained rank h-1 copy and rank1 cleanup must both be paid'
    H=Counter()
    for part in parts.values():
        assert all(type(r)is int and 0<=r<=h and type(c)is int and c>=0 for r,c in part.items())
        H.update(part)
    assert sum(r*c for r,c in H.items())==h*R+h*(h-1),'Complete local rank mass'
    return H

def negative_controls(parts,h,v,R):
    tests={}
    def reject(name,change):
        bad=copy.deepcopy(parts);change(bad)
        try:validate_paid(bad,h,v,R)
        except AssertionError:tests[name]=True
        else:raise AssertionError('Corruption accepted: '+name)
    reject('omitted_rank2_side_call',lambda p:p['side_growth_and_lines'].subtract({2:1}))
    def split(p):
        n=p['side_growth_and_lines'].pop(2);p['side_growth_and_lines'][1]+=2*n
    reject('rank_preserving_singleton_split_of_side_call',split)
    reject('omitted_retained_center_copy',lambda p:p['copied_centers'].subtract({h-1:1}))
    def old_cleanup(p):p['copied_centers'][1]-=h;p['copied_centers'][h]+=h
    reject('uncopied_center_cleanup_substitution',old_cleanup)
    reject('negative_multiplicity',lambda p:p['retirements'].update({0:-1}))
    return tests

def derive(word):
    raw=word.read_bytes();assert digest(raw)==WORD_SHA
    assert raw==(PARENT/'word-25.json.gz').read_bytes(),'Fresh word differs from frozen physical witness'
    d=json.loads(gzip.decompress(raw));h,v,R=d['h'],d['v'],d['R'];assert(h,v,R)==(25,2300,34749)
    F=d['frames'];classes=projector_classes(h,F);ranks=[1 if c==u else u.bit_count()-c.bit_count()for c,u in F]
    state=[None]*R;event=Counter();initial=nested=0
    for s,a,b in d['events']:
        assert type(s)is int and 0<=s<R and type(a)is int and -1<=a<len(F)and type(b)is int and 0<=b<len(F)
        assert state[s]==(None if a==-1 else a)
        if a==-1:initial+=1
        else:
            c,u=F[a];cc,uu=F[b];assert not cc&~c and not u&~uu;nested+=1
        if a!=b:event[s,a,b]+=1
        state[s]=b
    assert initial==R and all(x is not None for x in state)
    physical=[None]*R;actual=Counter();parts={name:Counter()for name in('literal_incidences','side_growth_and_lines','copied_centers','retirements')}
    def incidence(s,g):
        assert type(s)is int and 0<=s<R and type(g)is int and 0<=g<len(F)
        a=physical[s]
        if a is not None:
            c,u=F[a];cc,uu=F[g];assert not cc&~c and not u&~uu
        if a!=g:actual[s,-1 if a is None else a,g]+=1
        delta=ranks[g]-(0 if a is None else ranks[a]);assert 0<=delta<h
        parts['literal_incidences'][delta]+=1;physical[s]=g
    lookup={tuple(f):j for j,f in enumerate(F)};assert len(lookup)==len(F)
    triples=list(combinations(range(h),3));assert len(triples)==v
    assert set(d['sources'])=={str(j)for j in range(v)}and len(set(d['sources'].values()))==v
    for j,s in d['sources'].items():
        bits=sum(1<<i for i in triples[int(j)]);incidence(s,lookup[bits,bits])
    for a,b,g in d['ops']:assert a!=b;incidence(a,g);incidence(b,g)
    for s,g,c,T in d['outputs']:incidence(s,g)
    assert actual==event and physical==state,'Nonidentity frame incidence multisets differ'
    out=set();output_labels=set();centers=side=0
    for s,g,c,T in d['outputs']:
        assert s not in out and physical[s]==g;out.add(s);core,cover=F[g];r=ranks[g]
        label=(c,tuple(T));assert label not in output_labels;output_labels.add(label)
        assert core==1<<c
        if len(T)==1:
            assert T==[c]and cover==(1<<h)-1 and r==h-1
            parts['copied_centers'][r]+=1;parts['copied_centers'][h-r]+=1;centers+=1
        else:
            assert len(T)==len(set(T))==3 and c in T and T==sorted(T)
            assert cover==((1<<h)-1)^sum(1<<j for j in T if j!=c)
            assert all(9*(int(c in T)+2*int(i in T))-9==0 for i in range(h)if cover>>i&1 and i!=c)
            assert h-1-r==2
            parts['side_growth_and_lines'][2]+=1;parts['side_growth_and_lines'][1]+=1;side+=1
    assert output_labels=={(c,T)for T in triples for c in T}|{(c,(c,))for c in range(h)}
    assert centers==h and side==3*v
    for s,g in enumerate(physical):
        assert g is not None
        if s not in out:parts['retirements'][h-ranks[g]]+=1
    H=validate_paid(parts,h,v,R);controls=negative_controls(parts,h,v,R)
    copied=[H[r]for r in range(h+1)];unmixed=copied[:];unmixed[1]-=h;unmixed[h]+=h;assert min(unmixed)>=0
    # The axis schema uses PR104's pre-copy histogram convention. Its documented
    # H_h-=h,H_1+=h replacement returns exactly the physically paid H' above.
    row=dict(h=h,v=v,R=R,loss=h*(h-1),histogram=unmixed,
        literal_shear_operations=len(d['ops']),output_ports=len(d['outputs']),
        source_word_sha256=WORD_SHA,producer_kind='Frozen joint-frame physical word; complete literal rank ledger under the whole-rank stopped interface')
    audit=dict(h=h,v=v,R=R,source_word_sha256=WORD_SHA,frame_classes=classes,
        all_frame_gram_inverses_exact=True,ambient_metric='9 I - J',ambient_metric_eigenvalues=[9,9-h],
        initial_roles=initial,nested_event_incidences=nested,nonidentity_label_events_match_actual_word=True,
        all_side_hyperplane_inclusions_exact=True,side_growth_calls=side,retained_center_copies=centers,
        copied_rank_histogram=copied,paid_components={key:dict(sorted(value.items()))for key,value in parts.items()},
        rank_mass=sum(r*n for r,n in H.items()),rank_mass_identity='h R + h(h-1)',
        projector_reason='Exact nondegenerate H-orthogonal frame classes and every nested inclusion imply commuting projectors; nested differences are idempotent. Side hyperplane, complements, tensor products and orthogonal exteriors are projectors. Every nonzero ambient rank is below h^2.',
        both_orientations='Complementing endpoints and reversing a nested edge gives the same difference projector. Both reflected boundary families are included before choosing the common rational basis.',
        negative_controls=controls,
        scope='Fresh inherited full dirty-word replay plus independently reconstructed complete paid local rank ledger and exact projector-family hypotheses. Finite arithmetic/three-stock assembly is separate. PR104 common-basis/opposite-bank, atom streaming, stopped ordinary interface, old leaf, prime and retained all-size analytic/tape hypotheses remain explicit dependencies.')
    return row,audit

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--work',type=Path);parser.add_argument('--record',action='store_true');parser.add_argument('--replay-only',type=Path);parser.add_argument('--replay-output',type=Path);args=parser.parse_args()
    if args.replay_only:
        assert args.replay_output is not None;replay_only(args.replay_only,args.replay_output);return
    assert args.work is not None,'--work required';work=args.work.resolve();word=work/'bit/word-25.json.gz';replay=work/'bit-dirty-replay.json'
    assert digest((PARENT/'word-25.json.gz').read_bytes())==WORD_SHA
    subprocess.run([sys.executable,str(Path(__file__).resolve()),'--replay-only',str(word),'--replay-output',str(replay)],check=True,cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
    row,audit=derive(word);audit.update(full_inherited_dirty_replay_equal=True,
        dirty_replay_sha256=digest(replay.read_bytes()),frozen_replay_sha256=digest((PARENT/'replay-25.json').read_bytes()),
        inherited_strict_checker_sha256=digest((PARENT/'check.py').read_bytes()),checker_sha256=digest(Path(__file__).read_bytes()))
    for name,value in [('bit-axis.json',row),('bit-audit.json',audit)]:
        text=canonical(value);(work/name).write_text(text)
        if args.record:(HERE/name).write_text(text)
        else:assert (HERE/name).read_text()==text,'Fresh '+name+' differs'
    print('PASS fresh h25 dirty replay, exact projector hypotheses and complete whole-rank paid bit ledger')

if __name__=='__main__':main()
