"""Independent selected complex source geometry/window/payment audit."""
from pathlib import Path
from collections import Counter,defaultdict
import json,gzip,hashlib,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
spec=importlib.util.spec_from_file_location('phase_audit',P/'source_complex_chart.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
BASE=ROOT/'experiments/stage-search/pr441-signed75-hosting/complex-hosted';OLD=ROOT/'experiments/stage-search/pr433-split/full/split-centres'
rd=lambda p:json.loads(p.read_text());gz=lambda p:json.loads(gzip.decompress(p.read_bytes()))
def main():
    t=gz(BASE/'GLOBAL-TEMPLATE.json.gz');old=gz(OLD/'GLOBAL-TEMPLATE.json.gz');r=rd(BASE/'HOSTED-SIGMA.json');g=rd(BASE/'HOSTED.json')
    ph=gz(a.DIR/'complex-data-phases.json.gz');assert t['local_programs']==old['local_programs']
    stagepair={e['stage']:e['pair'] for e in t['recipe'] if e['kind']=='local'}
    sched=t['execution_schedule'];loc={e['stage']:pos for pos,e in enumerate(sched) if e['kind']=='local_cover_sweep'}
    targets={ch:(pos,e) for pos,e in enumerate(sched) if e['kind']=='idle_cover_sweep' for ch in e['child_indices']}
    slots={tuple(x) for x in t['hosting']['slots']};used=defaultdict(list);distinct=defaultdict(set);checks=0
    mapping={}
    for ch,p,off,w,s,h,B,translation in r['selected_sigma_columns_and_phase']:
        assert (ch,p,off,w,s,h) in slots and w==9
        child=ph['recipes'][p]['idle_children'][ch];sel=child['orthogonal_axes'][off:off+w]
        assert B[:9]==sel and len(B)==73 and a.orthogonal(B)
        assert a.compose(a.transpose(B),B)==a.identity()
        assert translation==child['translation_after']
        assert not set(sel)&set(used[ch,p]);used[ch,p]+=sel
        pair=int(t['hosting']['pairs'][str(ch)]);side=int(t['hosting']['sides'][str(ch)])
        key=(s,pair,side,p);assert tuple(B) not in distinct[key];distinct[key].add(tuple(B))
        start=loc[s];stop,e=targets[ch];assert start<stop and stagepair[s]!=pair
        for ev in sched[start+1:stop]:
            if ev['kind']=='local_cover_sweep':assert stagepair[ev['stage']]!=pair
            elif ev['kind']=='bridge':assert pair not in (ev['src'],ev['dst'])
            elif ev['kind']=='idle_cover_sweep':assert ev['pair']!=pair
            else:raise AssertionError('unknown intervening event')
        # Reflection preserves this exact no-touch open interval; C/X phases
        # commute independently even if simultaneous other-member idle exists.
        assert list(reversed(sched[start+1:stop]))==list(reversed(sched))[len(sched)-stop:len(sched)-1-start]
        mapping[s,h]=(ch,p,off,pair,side);checks+=1
    assert checks==len(slots)==4320
    remainder={};phase_checks=0
    for recipe in ph['recipes']:
        port=recipe['port']
        for ch,child in enumerate(recipe['idle_children']):
            host=used[ch,port];axes=child['orthogonal_axes'];rest=[v for v in axes if v not in host]
            assert Counter(host)+Counter(rest)==Counter(axes)
            assert a.phase(host+rest,child['translation_after'])==a.phase(axes,child['translation_after'])
            remainder[ch,port]=len(rest);phase_checks+=1
    bank=defaultdict(set)
    for c0,c in zip(old['calls'],t['calls']):
        assert c0['owners'][:240]==c['owners'][:240]
        for h,(f,route) in enumerate(c['owners'][240:]):
            if (c['stage'],h) in mapping:
                ch,p,off,pair,side=mapping[c['stage'],h]
                assert route==[3,ch,off] and f==c['replica']*960+(2*pair+side)*120+p
            else:
                assert route[0]==2 and route[1] not in bank[f];bank[f].add(route[1])
    assert sorted(bank)==list(range(7680,t['live']))
    ci=rd(OLD/'INTEGRATION.json');H=Counter()
    for c in t['calls']:
        for rk,n in ci['local_program_checks'][c['orientation']]['paid_profile'].items():H[int(rk)]+=n
    for (ch,port),rk in remainder.items():
        if rk:H[rk]+=8
    for f,usedslots in bank.items():H[73-9*len(usedslots)]+=1
    assert dict(H)=={int(k):v for k,v in g['global_profile'].items()}
    assert 73*t['live']-sum(k*v for k,v in H.items())==2496
    out=dict(status='PASS_INDEPENDENT_ALL_SELECTED_COMPLEX_GEOMETRY_PHASE_WINDOWS_REFLECTION_PAYMENT',selected_slots=checks,actual_phase_checks=phase_checks,live=t['live'],deficit=2496,profile=dict(H),
        sigma_artifact_sha256=hashlib.sha256((BASE/'HOSTED-SIGMA.json').read_bytes()).hexdigest(),
        template_sha256=hashlib.sha256((BASE/'GLOBAL-TEMPLATE.json.gz').read_bytes()).hexdigest(),
        scope='Full selected finite orthogonal axes, exact phase including translations, actual windows/reflection, owner links, bank pads and profile. Literal signed local theorem inherited from unchanged independently admitted own433; all-size/compiler/invoice separate.')
    (P/'COMPLEX-ASSIGNMENT.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
if __name__=='__main__':main()
