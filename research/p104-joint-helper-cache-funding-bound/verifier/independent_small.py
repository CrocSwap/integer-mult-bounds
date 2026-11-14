"""Independent max-pivot check of all 89 small-component funding cases.

Callable only: run(replay_doc, structure_doc, local_doc). No file access,
source mutation, primary-engine import, price import, or saved-row dependency.
This ports Jerry Chen / CubeJerry's independent wave44 exact-Q reconstruction;
its original pinned author work is preserved in worker-b/integer-price-0038.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json

WORD_SHA256='acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9'
CAPS={(39875,39884):{5:1,1:1,6:-1},(42500,):{1:1,3:1,4:-1},(41646,):{6:1,4:-1}}
SMALL_KEYS={(30593,),(36358,),(30581,),(36346,),(39875,39884),(44253,),(42500,),(41646,)}

def _need(ok,label):
    if not ok:raise ValueError('independent small: '+label)
def _row(row):return {int(h):Q(a) for h,a in row.items() if a}
def _rows(rows):return [_row(r) for r in (rows.values() if isinstance(rows,dict) else rows)]
def _add(a,b,q):
    for h,v in b.items():
        z=a.get(h,0)+q*v
        if z:a[h]=z
        else:a.pop(h,None)
def _normal(row,basis):
    v=row.copy()
    for p in sorted(basis,reverse=True):
        if v.get(p):_add(v,basis[p],-v[p])
    return v
def _echelon(rows):
    b={}
    for row in rows:
        v=_normal(row,b)
        if v:
            p=max(v);b[p]={h:a/v[p] for h,a in v.items()}
    return b
def _helper_extension(history,target,mains):
    image={};helper={}
    for row in list(history.values())+[target]:
        full=row.copy();v={h:a for h,a in row.items() if h in mains}
        for p in sorted(image,reverse=True):
            if v.get(p):
                q=v[p];_add(v,image[p][0],-q);_add(full,image[p][1],-q)
        if v:
            p=max(v);q=1/v[p]
            image[p]=({h:a*q for h,a in v.items()},{h:a*q for h,a in full.items()})
        else:helper=_echelon(list(helper.values())+[full])
    _need(len(helper)+len(image)==len(history)+1,'helper-intersection rank-nullity')
    return helper
def _prefix(rows,targets):
    p=[len(_echelon({h:a for h,a in row.items() if targets[h]<=k} for row in rows)) for k in range(10)]
    _need(p[0]==0 and all(a<=b for a,b in zip(p,p[1:])),'prefix ranks')
    return p
def _profile(p):return {k:p[k]-p[k-1] for k in range(1,10) if p[k]!=p[k-1]}
def _counts(profile):return {int(k):v for k,v in profile.items() if v}
def _digest(value):return sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def run(replay_doc,structure_doc,local_doc):
    """Rebuild all small obligations and prove their nine-generator ceilings."""
    _need(replay_doc['receipt']['source_sha256']==structure_doc['receipt']['source_sha256']==local_doc['source_sha256']==WORD_SHA256,'source binding')
    _need(_normal({9:Q(1),4:Q(3)},{4:{4:Q(1),2:Q(2)}})=={9:Q(1),2:Q(-6)},'all-pivot quotient trap')
    word=replay_doc['word'];mains=set(replay_doc['main_coordinates']);helpers=set(replay_doc['helper_coordinates'])
    actual_mains=set(word['live'])|{h+112 for h in word['live']}|set(word['hosted']['X2'])|set(word['hosted']['Y2'])
    _need(mains==actual_mains and helpers==set(range(word['public']))-actual_mains,'actual main/helper coordinate split')
    targets={h:abs(len(word['frames'][word['final'][h]])-len(word['frames'][word['initial'][h]])) for h in helpers}
    _need(targets==replay_doc['helper_target_ranks'] and len(helpers)==1101 and len(mains)==400,'original target coordinates/ranks')
    _need(all(1<=r<=9 for r in targets.values()),'target rank domain')
    zeros={r['event']:r for r in replay_doc['mainfree_moves']}
    _need(len(zeros)==len(replay_doc['mainfree_moves'])==468,'unique complete zero-row collection')
    selected=[c for c in structure_doc['cache_components'] if len(c['zero_events'])<=4]
    primary={tuple(c['cache_sites']):c for c in local_doc['eight_small_components']}
    _need(len(selected)==len(primary)==len(local_doc['eight_small_components'])==8 and {tuple(c['cache_sites']) for c in selected}==set(primary)==SMALL_KEYS,'eight small component identities')
    components=[];all_profiles=[];all_proofs=[];case_count=subset_count=obligation_count=0
    for component in sorted(selected,key=lambda c:tuple(c['cache_sites'])):
        events=tuple(component['cache_sites']);zevents=component['zero_events'];cap=CAPS.get(events,{})
        rc=primary[events]
        _need(rc['zero_events']==zevents and rc['subset_count']==len(rc['subsets'])==1<<len(zevents),'component zero subset coverage')
        raw=[]
        for e in zevents:
            z=zeros[e];ins=word['program'][e]
            _need(ins[0]=='MOVE' and ins[1]==z['owner'] and bool(ins[4])==z['owned'],'actual zero MOVE identity')
            _need(z['rank']==abs(len(word['frames'][ins[2]])-len(word['frames'][ins[3]])),'actual zero MOVE paid rank')
            row=_row(z['row']);_need(row and set(row)<=helpers,'main-free nonzero row');raw.append(row)
        sites={}
        for e in events:
            s=replay_doc['sites'][e]
            _need(word['program'][e]==['MOVE',s['owner'],s['source'],s['destination'],True],'actual owned cache MOVE')
            _need(s['target_rank']==abs(len(word['frames'][s['source']])-len(word['frames'][s['destination']])),'actual owned cache paid rank')
            H=_echelon(_rows(s['history_basis']));target=_row(s['target'])
            _need(len(H)==s['strict_history_rank'] and _normal(target,H),'history rank and original miss')
            L=_helper_extension(H,target,mains);other=_echelon(_rows(s['L_basis']))
            _need(len(L)==len(other)==s['L_dimension'] and all(not _normal(r,L) for r in other.values()),'independently reconstructed L')
            _need(all(set(r)<=helpers for r in L.values()),'L helper-only support')
            sites[e]={'H':H,'L':L,'t':_normal(target,H),'z':[_normal(z,H) for z in raw],'rank':s['target_rank']}
        local_cases=0;local_profiles=[];local_proofs=[];cone_min=None
        for mask in range(1<<len(raw)):
            inds=[i for i in range(len(raw)) if mask>>i&1];Z=[raw[i] for i in inds]
            prefix=_prefix(Z,targets);beta=_profile(prefix)
            enabled=[e for e in events if not _normal(sites[e]['t'],_echelon(sites[e]['z'][i] for i in inds))]
            remaining=[e for e in events if e not in enabled]
            sr=rc['subsets'][mask]
            _need(sr['mask']==mask and sr['zero_events']==[zevents[i] for i in inds],'subset mask and zero events')
            _need(sr['beta_prefix_ranks']==prefix and _counts(sr['beta_profile'])==beta,'independent beta profile')
            _need(sr['enabled_sites']==enabled and sr['new_sites']==remaining,'quotient eligibility')
            gamma={}
            for e in remaining:
                union=_prefix(Z+list(sites[e]['L'].values()),targets)
                gp=[min(prefix[k]+1,union[k]) for k in range(10)]
                _need(gp[0]==0 and gp[-1]==prefix[-1]+1 and all(a<=b for a,b in zip(gp,gp[1:])),'generic new witness ranks')
                gamma[e]=_profile(gp)
            _need({int(e):_counts(p) for e,p in sr['gamma_profiles'].items()}==gamma,'independent gamma profiles')
            cases={tuple(c['newly_granted']):c for c in sr['cases']}
            _need(len(cases)==len(sr['cases'])==1<<len(remaining),'complete unique grant-case coverage')
            for nm in range(1<<len(remaining)):
                new=tuple(e for j,e in enumerate(remaining) if nm>>j&1)
                expected=cases[new];_need(expected['mask']==mask,'grant mask')
                credits=Counter(zeros[zevents[i]]['rank'] for i in inds)
                credits.update(sites[e]['rank'] for e in enabled+list(new))
                obligations=[(e,gamma[e]) for e in new] if new else [(None,beta)]
                actual=expected['all_necessary_obligations'];proof=None;profiles=[]
                _need([o['witness'] for o in actual]==[e for e,p in obligations],'complete obligation witnesses')
                for o,(e,debit) in zip(actual,obligations):
                    delta=credits.copy();delta.subtract(debit);delta={r:n for r,n in delta.items() if n}
                    _need(_counts(o['signed_profile'])==delta,'independent signed obligation invoice')
                    diff=Counter(cap);diff.subtract(delta)
                    margins=[sum(n*min(r,k) for r,n in diff.items()) for k in range(1,10)]
                    if min(margins)>=0 and proof is None:proof={'witness':e,'nine_generator_margins':margins}
                    profiles.append({'witness':e,'profile':delta});obligation_count+=1
                _need(proof is not None,'one necessary obligation proves component ceiling')
                cone_min=min(proof['nine_generator_margins']) if cone_min is None else min(cone_min,*proof['nine_generator_margins'])
                local_profiles.append({'mask':mask,'new':new,'profiles':profiles});local_proofs.append({'mask':mask,'new':new,**proof})
                local_cases+=1;case_count+=1
            subset_count+=1
        _need(local_cases==rc['case_count'],'component case count')
        components.append({'cache_sites':list(events),'zero_events':zevents.copy(),'subsets':1<<len(raw),'cases':local_cases,'ceiling_profile':dict(sorted(cap.items())),'minimum_generator_margin':cone_min,'profiles_sha256':_digest(local_profiles),'ceiling_proofs_sha256':_digest(local_proofs)})
        all_profiles.append({'cache_sites':list(events),'cases':local_profiles});all_proofs.append({'cache_sites':list(events),'cases':local_proofs})
    _need(case_count==89 and subset_count==43 and obligation_count==91,'all 43 subsets,89 cases,91 obligations')
    total=Counter()
    for c in components:total.update(c['ceiling_profile'])
    total={r:n for r,n in total.items() if n}
    _need(total=={5:1,3:1,1:2,4:-2},'exceptional ceiling sum')
    return {'status':'PASS_INDEPENDENT_MAX_PIVOT_89_SMALL_CASES','source_sha256':WORD_SHA256,'fresh_source_rows_sha256':replay_doc['receipt']['source_rows_sha256'],'components':components,'zero_subsets':subset_count,'grant_cases':case_count,'obligation_profiles':obligation_count,'nine_generator_inequalities':9*case_count,'ceiling_profile':dict(sorted(total.items())),'all_profiles_sha256':_digest(all_profiles),'all_ceiling_proofs_sha256':_digest(all_proofs),'all_pivot_quotient_control':True,'method':'Independent maximum-pivot rational history intersections, all-pivot quotient eligibility, exact rank prefixes and nine increasing-concave generators min(r,k). No price module or saved matrices imported.','scope':'The eight small components only. Fixed original whole helper targets and source histories. Global decomposition, other components, complete prices and physical admission remain separate.'}
