"""Independent chronological frame-path recount of every affected stream."""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import json,time
from check_complete_suffix import build,read,HERE,V,CANDIDATE_FILE
from exact_geometry import echelon

def nullspace(B):
    rows,piv=echelon(B);free=[j for j in range(24)if j not in piv]
    out=[]
    for j in free:
        v=[Q(0)]*24;v[j]=1
        for i,k in enumerate(piv):v[k]=-rows[i][j]
        out.append(v)
    return out

def run(mutation=None):
    start=time.monotonic();n,old,new,scalar=build()
    w=read('gen5bit__selected__bit__word_p12.json.gz.base64')
    ff=read('gen5bit__selected__bit__frames_p12.json.gz.base64')['frames'];g=read('graph.json')
    sel=read(CANDIDATE_FILE)['candidates'];restore=read('restore-selection.json')['entries']
    partner=read('gen5bit__selected__bit__kchron_p12.json')['entries']
    aliases={b:a for a,b in w['pairs']};regs=sorted(set(range(17160))-set(aliases));ids={s:3520+i for i,s in enumerate(regs)}
    sid=lambda s:ids[aliases.get(s,s)]
    undo={z['old_restored_helper_stream']for z in sel};oldr={z['helper']:z for z in restore}
    bynew={z['helper']:z for z in sel};bydonor={z['donor_root']:z for z in sel};byblocker={z['blocker_root']:z for z in sel}
    affected={sid(z[k])for z in sel for k in ('helper','donor','blocker')}
    affected|={oldr[h][k]for h in undo for k in ('helper','donor')}
    affected|={V+z['target']for z in sel}
    partner_by_root={e['deliver_after_root']:e for e in partner}
    assert len(partner_by_root)==len(partner)
    affected|={partner_by_root[z['blocker_root']]['carrier']for z in sel}
    descent=read('descent-selection.json')['entries']
    affected_helpers={s for s in affected if s>=3520}
    assert not [e for e in descent if set(e['scalar'][:2])&affected_helpers]
    # Canonical annihilator matrices; exact containment uses row-span inclusion.
    cache={'FULL':[], 'ZERO':[[Q(i==j)for j in range(24)]for i in range(24)]}
    dims={'FULL':24,'ZERO':0}
    def ann(key):
        if key not in cache:
            if isinstance(key,int):
                d=ff[str(key)];cache[key]=d.get('a') if 'a'in d else nullspace(d['b']);dims[key]=d['dim']
            elif key.startswith('REST:'):
                z=oldr[int(key[5:])];cache[key]=nullspace(z['basis']);dims[key]=z['rank']
            elif key.startswith('CAP:'):
                t=int(key[4:]);S=set(g['labels'][t]);cache[key]=[[3*int(j in S)-1 for j in range(24)]];dims[key]=23
            else:raise ValueError(key)
        return cache[key]
    containment={}
    def sub(a,b):
        if (a,b)not in containment:
            A,B=ann(a),ann(b)
            containment[a,b]=len(echelon(A+B)[1])==len(A)
        return containment[a,b]
    setup_frames={}
    for z in sel:
        e=partner_by_root[z['blocker_root']]
        selected=[d for d in descent if d['scalar'][:3]==[e['carrier'],e['passive'],1]]
        assert len(selected)==1 and selected[0]['old_dimension']==2 and selected[0]['new_dimension']==22
        d=selected[0];A=ann(e['deliver_frame'])
        assert len(echelon(d['new_basis'])[1])==22
        assert all(sum(x*y for x,y in zip(a,b))==0 for a in A for b in d['new_basis'])
        setup_frames[z['blocker_root']]=e['deliver_frame']
    phase=set(w['phase1']);order=w['phase1']+[i for i in range(len(w['ops']))if i not in phase]
    initial={x:'ZERO'for x in affected}
    for x in affected:
        if x<V:initial[x]=w['source_frame'][x]
    for i in order:
        for s in w['ops'][i][:2]:
            x=sid(s)
            if x in affected:initial[x]=w['op_frame'][i]
    # Derive each actual helper prefix endpoint; do not assume all are22.
    for x in affected:
        if x>=3520:ann(initial[x]);assert dims[initial[x]]<=22,(x,initial[x],dims[initial[x]])
    def frame(tag,changed):
        if tag.startswith('root:'):
            _,ii,tt=tag.split(':');i,t=int(ii),int(tt)
            if changed and i in bydonor:return bydonor[i]['common_frame']
            if changed and i in byblocker and t==byblocker[i]['target']:return byblocker[i]['promoted_blocker_frame']
            return w['root_frame'][i]
        if tag.startswith('new_restore:'):return bynew[int(tag.split(':')[1])]['new_endpoint']
        if tag.startswith('old_restore:'):return 'REST:'+tag.split(':')[1]
        if tag.startswith('partner_setup:'):
            i=int(tag.split(':')[1]);return setup_frames.get(i,partner_by_root[i]['mix_frame'])
        if tag.startswith('partner_delivery:'):
            _,ii,tt=tag.split(':');i,t=int(ii),int(tt)
            if changed and mutation!='omit_partner_promotion' and i in byblocker and t==byblocker[i]['target']:return byblocker[i]['promoted_blocker_frame']
            return partner_by_root[i]['deliver_frame']
        return 'FULL'
    def check(events,changed):
        state=dict(initial);hist=Counter();paths={x:[initial[x]]for x in affected}
        def move(x,f):
            if x not in affected:return
            a=state[x];assert sub(a,f),('nonnested',changed,x,a,f)
            ann(f);delta=dims[f]-dims[a]
            if delta:hist[delta]+=1;paths[x].append(f)
            state[x]=f
        for a,b,c,tag in events:
            f=frame(tag,changed);move(a,f);move(b,f)
        for x in affected:
            endpoint='FULL'if x<1760 or x>=3520 else 'CAP:'+str(x-V)
            if x in oldr and not(changed and x in undo and mutation!='omit_old_undo'):endpoint='REST:'+str(x)
            if changed:
                match=next((z for z in sel if sid(z['helper'])==x),None)
                if match:endpoint=match['new_endpoint']
            move(x,endpoint)
        return hist,paths
    oldH,oldP=check(old,False);newH,newP=check(new,True)
    delta=Counter(newH);delta.subtract(oldH);delta={r:c for r,c in delta.items()if c}
    assert delta=={1:18,2:-12},delta
    byrole=[]
    for x in sorted(affected):
        if oldP[x]!=newP[x]:
            byrole.append(dict(stream=x,before_frames=oldP[x],after_frames=newP[x],
                before_dimensions=[dims[f]for f in oldP[x]],after_dimensions=[dims[f]for f in newP[x]]))
    return dict(status='PASS_MEASURED_AFFECTED_SUFFIX_FRAME_LEDGER',source_head='5f6bd3fbc0e6796dd31263cef1f06dc968186f64',
        affected_streams=len(affected),changed_paths=len(byrole),exact_rational_containment_checks=len(containment),
        affected_helper_descent_overlaps=0,partner_setup_descent_replacements_applied=len(setup_frames),
        old_histogram=dict(oldH),new_histogram=dict(newH),local_histogram_delta=delta,
        both_reflected_ledgers=True,reflected_justification='For each nested frame pair A⊂B, the annihilator inclusion reverses and the codimension drop equals the dimension gain.',
        paths=byrole,seconds=time.monotonic()-start,
        scope='Chronological required-frame census of all affected helper, source-carrier and target streams. Targets start at ZERO for this difference census; their unchanged prior prefixes terminate within the checked first unchanged precursor frame, under retained source admission. Helper prefix frames are read from the actual base forward word and no affected helper overlaps descent changes; all 12 selected partner setups use their verified post-descent rank-22 frames. No global finite/compiler replay is claimed.')

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    r=run()
    print(json.dumps({k:v for k,v in r.items()if k!='paths'},indent=2))
