"""Exactly two bounded priority orders; no additional line or basis search.

Regenerate each result in memory and compare its integer construction against
its frozen candidate. Entropy numbers are diagnostic screening quantities.
"""
from pathlib import Path
from collections import Counter
import json
from search_expanded_lines import closure
from compose_screened_groups import members,ledger,dim,phi
from source_data import ROOT,OUTPUT

def resolve(primary,secondary,extra):
    entries=primary['entries']+extra['entries'];assert not members(primary['entries'])&members(extra['entries'])
    used=members(entries)
    remaining=[dict(pivot=e['virtual_pivot'],donors=e['virtual_donors'])for e in secondary['entries']if not members([e])&used]
    dimensions={r:dim(r)for e in remaining for r in[e['pivot']]+e['donors']}
    selected,profit=closure(remaining,dimensions,phi);before=len(selected);parity=None
    if len(selected)%2:
        counts=Counter(d for e in selected for d in e['donors'])
        def marginal(e):
            benefit=phi(dim(e['pivot']))-phi(dim(e['pivot'])-1)
            released=sum(phi(1)+phi(dim(d)-1)-phi(dim(d))for d in e['donors']if counts[d]==1)
            return round((benefit-released)*10**9),e['pivot']
        parity=min(selected,key=marginal);selected=[e for e in selected if e is not parity]
    keep={e['pivot']for e in selected};entries += [e for e in secondary['entries']if e['virtual_pivot']in keep]
    h,donors=ledger(entries)
    return dict(entries=entries,pivots=len(entries),distinct_donors=donors,
                local_histogram_delta=h,residual_family_delta={24:-len(entries),23:len(entries)},
                scalar_setup_pairs=sum(len(e['donors'])for e in entries),
                remaining_relations=len(remaining),selected_before_parity=before,
                selected_after_parity=len(selected),parity_omitted_pivot=parity['pivot']if parity else None,
                rounded_closure_profit_before_parity=profit)

def run():
    a=json.loads((ROOT/'candidate-line16-17.json').read_text());b=json.loads((ROOT/'candidate-line6-7.json').read_text());c=json.loads((ROOT/'candidate-line2-3.json').read_text())
    results=[]
    for label,primary,secondary,name in [('preserve136',a,b,'candidate-combined166-reclosed.json'),('preserve36',b,a,'candidate-combined48-reclosed-reverse.json')]:
        result=resolve(primary,secondary,c);frozen=json.loads((ROOT/name).read_text())
        for key in ('entries','pivots','distinct_donors','scalar_setup_pairs'):
            assert result[key]==frozen[key],(label,key)
        for key in ('local_histogram_delta','residual_family_delta'):
            assert result[key]=={int(k):v for k,v in frozen[key].items()},(label,key)
        results.append(dict(order=label,candidate=name,**{k:v for k,v in result.items()if k!='entries'}))
    return dict(status='PASS_TWO_FIXED_OVERLAP_RESOLUTIONS',orders=results,
                scope='Exactly two priority orders on the three positive groups from the declared276-line pass. Same rounded closure algorithm reused on surviving relations, then one deterministic parity trim. No claim of optimality over all conflict resolutions or bases.')

if __name__=='__main__':
    out=run();(OUTPUT/'overlap-resolution-receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
