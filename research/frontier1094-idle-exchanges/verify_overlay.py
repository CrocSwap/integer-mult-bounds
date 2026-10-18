#!/usr/bin/env python3
"""Independent checks for the #1094 idle-axis overlay."""
import argparse, gzip, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
OWNER_MAP = ROOT / 'research/complex-t16-rare-pattern-exchanges/OWNERS.json.gz'


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    data=Path(p).read_bytes()
    return json.loads(gzip.decompress(data) if str(p).endswith('.gz') else data)
def dot(a,b): return (int(a)&int(b)).bit_count()&1
def rank(vs):
    pivots={}
    for x in map(int,vs):
        while x:
            b=x.bit_length()-1
            if b in pivots: x^=pivots[b]
            else: pivots[b]=x;break
    return len(pivots)
def phase_poly(axes):
    linear=[0]*73; quad=Counter()
    for axis in map(int,axes):
        support=[i for i in range(73) if axis>>i&1]
        for i in support: linear[i]=(linear[i]+1)&3
        for q,i in enumerate(support):
            for j in support[q+1:]:quad[i,j]=(quad[i,j]-2)&3
    return linear,{k:v for k,v in quad.items() if v}

def transfer_possible(source,target,recipe):
    left=list(map(int,source['orthogonal_axes']))
    right=list(map(int,target['orthogonal_axes']))
    ys=[int(s[k]) for s in recipe['stage_alignment']
        for k in ('entry_Y','exit_Y')]+[int(recipe['terminal_Y_translation'])]
    xs=[int(s[k]) for s in recipe['stage_alignment']
        for k in ('entry_X','exit_X')]
    terminal=[int(recipe['idle_children'][c]['translation_after'])
              for c in (source['child'],target['child'])]
    moved=[v for v in left if all(dot(v,x)==0 for x in right+ys+xs+terminal)][:3]
    if len(moved)<3:return False
    return rank([v for v in left if v not in moved])==45 and rank(right+moved)==51

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay-root',type=Path,required=True,
        help='Extracted candidate/strict/global directory from selected-replay.tar.gz')
    parser.add_argument('--baseline-hosted-root',type=Path,
        help='Freshly emitted/audited baseline hosted directory; defaults to replay-root/hosted')
    args=parser.parse_args();replay=args.replay_root.resolve()
    base=replay/'base';hosted=(args.baseline_hosted_root or replay/'hosted').resolve()
    old_t=read(hosted/'GLOBAL-TEMPLATE.json.gz');new_t=read(OUT/'GLOBAL-TEMPLATE.json.gz')
    old_f=read(hosted/'IDLE-REMAINDER-FRAMES.json.gz');new_f=read(OUT/'IDLE-REMAINDER-FRAMES.json.gz')
    phases=read(base/'work/complex-nine-native/DATA-PHASES.json')
    owners=read(OWNER_MAP);overlay=read(OUT/'IDLE-PAIR-OVERLAY.json')
    assert overlay['source_template_sha256']==sha(hosted/'GLOBAL-TEMPLATE.json.gz')
    assert overlay['source_frames_sha256']==sha(hosted/'IDLE-REMAINDER-FRAMES.json.gz')
    assert overlay['source_phases_sha256']==sha(base/'work/complex-nine-native/DATA-PHASES.json')
    assert overlay['source_owner_map_sha256']==sha(OWNER_MAP)
    old={(r['replica'],r['port'],r['child']):r for r in old_f}
    new={(r['replica'],r['port'],r['child']):r for r in new_f}
    assert old.keys()==new.keys()
    roles={(r['owner_replica'],r['port'],r['child']) for r in owners}
    recipes={r['port']:r for r in phases['recipes']}
    edits=[];pairs=overlay['pairs'];used=set()
    for pair in pairs:
        rep,port=pair['replica'],pair['port']
        ka=(rep,port,pair['left_child']);kb=(rep,port,pair['right_child'])
        assert ka not in used and kb not in used;used.update((ka,kb))
        a,b=old[ka],old[kb];aa,bb=new[ka],new[kb]
        assert a['rank']==b['rank']==48 and a['hosted']==b['hosted']==0
        assert a['pending_offset']==b['pending_offset']==0
        assert ka not in roles and kb not in roles
        moved=list(map(int,pair['moved_axes']))
        olda=list(map(int,a['orthogonal_axes']));oldb=list(map(int,b['orthogonal_axes']))
        assert len(moved)==3 and olda==pair['old_axes_left'] and oldb==pair['old_axes_right']
        assert pair['new_axes_left']==[v for v in olda if v not in moved]
        assert pair['new_axes_right']==oldb+moved
        assert aa['rank']==45 and bb['rank']==51
        assert aa['orthogonal_axes']==pair['new_axes_left'] and bb['orthogonal_axes']==pair['new_axes_right']
        assert rank(aa['orthogonal_axes'])==45 and rank(bb['orthogonal_axes'])==51
        assert all(dot(x,y)==(i==j) for i,x in enumerate(aa['orthogonal_axes'])
                   for j,y in enumerate(aa['orthogonal_axes']))
        assert all(dot(x,y)==(i==j) for i,x in enumerate(bb['orthogonal_axes'])
                   for j,y in enumerate(bb['orthogonal_axes']))
        recipe=recipes[port]
        translations=[int(recipe['idle_children'][c]['translation_after']) for c in (a['child'],b['child'])]
        ys=[int(s[k]) for s in recipe['stage_alignment'] for k in ('entry_Y','exit_Y')]+[int(recipe['terminal_Y_translation'])]
        xs=[int(s[k]) for s in recipe['stage_alignment'] for k in ('entry_X','exit_X')]
        assert all(dot(x,y)==0 for x in moved for y in oldb+ys+xs+translations)
        assert phase_poly(olda+oldb)==phase_poly(aa['orthogonal_axes']+bb['orthogonal_axes'])
        edits.extend((ka,kb))
    assert len(pairs)==1825 and len(edits)==3650
    # Each replica/port family has at most four idle rank-48 children, so an
    # exhaustive bitmask matching proves this selected matching is maximal.
    free=defaultdict(list)
    for row in old_f:
        key=(row['replica'],row['port'],row['child'])
        if row['rank']==48 and row['hosted']==0 and row['pending_offset']==0 and key not in roles:
            free[row['replica'],row['port']].append(row)
    max_pairs=0
    for (rep,port),rows in free.items():
        n=len(rows); edge=set(); recipe=recipes[port]
        for i in range(n):
            for j in range(i+1,n):
                if transfer_possible(rows[i],rows[j],recipe) or transfer_possible(rows[j],rows[i],recipe):
                    edge.add((i,j))
        memo={}
        def best(mask):
            if not mask:return 0
            if mask in memo:return memo[mask]
            i=(mask&-mask).bit_length()-1
            value=best(mask&~(1<<i))
            for j in range(i+1,n):
                if mask>>j&1 and (i,j) in edge:
                    value=max(value,1+best(mask&~(1<<i)&~(1<<j)))
            memo[mask]=value;return value
        max_pairs+=best((1<<n)-1)
    assert max_pairs==len(pairs)==1825
    changed=[]
    for key in old:
        if old[key]!=new[key]:
            assert key in set(edits);changed.append(key)
        else: assert key not in set(edits)
    assert len(changed)==3650
    old_core,new_core=dict(old_t),dict(new_t)
    old_children=old_core.pop('idle_children');new_children=new_core.pop('idle_children')
    old_core.pop('version');new_core.pop('version');declaration=new_core.pop('idle_axis_overlay')
    assert old_core==new_core
    assert new_t['version']==old_t['version']+'+idle-48-pair-exchanges-v1'
    assert len(old_children)==len(new_children)
    oldc={(x['replica'],x['port'],x['child']):x for x in old_children}
    newc={(x['replica'],x['port'],x['child']):x for x in new_children}
    assert oldc.keys()==newc.keys()
    for k in oldc:
        x,y=oldc[k],newc[k]
        if x!=y:
            assert k in set(edits) and x['hosted']==0 and y['hosted']==0
            assert y['rank'] in (45,51) and x['rank']==48
            xx,yy=dict(x),dict(y);xx.pop('rank');yy.pop('rank');assert xx==yy
    audit_profile=read(replay/'audit/OWNERS-AND-PROFILE.json')['paid_profile']
    profile=Counter({int(k):v for k,v in audit_profile.items()})
    profile.subtract(x['rank'] for x in old_f)
    profile.update(x['rank'] for x in new_f)
    profile=+profile
    assert {str(k):v for k,v in sorted(profile.items())}==overlay['profile']
    hosted_record=read(OUT/'HOSTED.json')
    assert hosted_record['global_profile']==overlay['profile'] and hosted_record['template_sha256']==hashlib.sha256(
        json.dumps(new_t,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert hosted_record['idle_pair_overlay_sha256']==sha(OUT/'IDLE-PAIR-OVERLAY.json')
    assert hosted_record['idle_remainder_frames_sha256']==hashlib.sha256(
        gzip.decompress((OUT/'IDLE-REMAINDER-FRAMES.json.gz').read_bytes())).hexdigest()
    receipt=dict(status='PASS_INDEPENDENT_FRONTIER1094_IDLE_PAIR_OVERLAY',
        source_sha256=dict(template=sha(hosted/'GLOBAL-TEMPLATE.json.gz'),
          frames=sha(hosted/'IDLE-REMAINDER-FRAMES.json.gz'),
          phases=sha(base/'work/complex-nine-native/DATA-PHASES.json'),owner_map=sha(OWNER_MAP)),
        pairs=len(pairs),maximum_matching_pairs=max_pairs,changed_children=len(changed),profile=overlay['profile'],
        profile_delta={'45':1825,'48':-3650,'51':1825},rank_mass=sum(int(r)*n for r,n in overlay['profile'].items()),
        deficit=5120,halving_guard=[5329,5202],
        exact_pair_Z4_polynomial=True,each_child_axes_orthogonal=True,
        moved_axes_commute_with_stage_X_Y_and_both_terminal_translations=True,
        no_owner_roles_in_changed_slots=True,
        scope='Independent structural and exact local phase audit. Invoice and complete controller composition are separate.')
    (OUT/'OVERLAY-AUDIT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['status'],'pairs=1825 changed_children=3650')

if __name__=='__main__':main()
