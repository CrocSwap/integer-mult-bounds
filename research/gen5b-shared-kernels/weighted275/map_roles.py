"""Independent logical-to-physical audit; no upstream program is imported."""
from pathlib import Path
import gzip,json,hashlib
ROOT=Path(__file__).resolve().parent
from source_data import SOURCE,OUTPUT
FROZEN=ROOT.parent

def word(p):return json.loads(gzip.decompress(p.read_bytes()))
def layout(w):
    pairs=w['pairs'];assert all(len(z)==2 for z in pairs)
    recipient_to_donor={b:a for a,b in pairs};donors={a for a,b in pairs}
    assert len(recipient_to_donor)==len(donors)==len(pairs)
    assert not donors&recipient_to_donor.keys()
    regs=sorted(set(range(17160))-recipient_to_donor.keys())
    phys={r:3520+i for i,r in enumerate(regs)}
    return recipient_to_donor,donors,phys

def run():
    old=word(SOURCE/'prior299-word.json.gz');new=word(SOURCE/'gen5bit/selected/bit/word_p12.json.gz')
    old_alias,old_donors,oldphys=layout(old);alias,donors,phys=layout(new)
    assert len(old_alias)==1726 and len(alias)==1728
    assert {k for k in new if new[k]!=old[k]}=={'pairs','reads'}
    assert len(phys)==15432
    oldinv={s:r for r,s in oldphys.items()}
    kernels=json.loads((SOURCE/'kernel-selection.json').read_text())
    occupied={r for z in kernels['pairs']for r in (z['a'],z['b'])}|{r for z in kernels['families']for r in [z['pivot']]+z['donors']}
    def info(r):
        return dict(logical_role=r,old_stream=oldphys[old_alias.get(r,r)],new_stream=phys[alias.get(r,r)],
                    old_recipient=r in old_alias,new_recipient=r in alias,
                    old_reuse_donor=r in old_donors,new_reuse_donor=r in donors,
                    new_alias=alias.get(r,r),new_kernel_member=phys[alias.get(r,r)]in occupied)
    witness=json.loads((FROZEN/'kernel70-witness.json').read_text())['entries']
    remapped=[]
    for z in witness:
        p=info(z['virtual_pivot']);ds=[info(r)for r in z['virtual_donors']]
        remapped.append(dict(old_pivot=z['pivot'],pivot=p,donors=ds,basis=z['basis'],rank=z['rank']))
    member_ids={z['virtual_pivot']for z in witness}|{r for z in witness for r in z['virtual_donors']}
    members=[info(r)for r in sorted(member_ids)]
    core=json.loads((FROZEN/'certificates/coretime12/local.json').read_text())['candidates']
    core_rows=[]
    for z in core:
        row={k:info(z[k])for k in ('helper','donor','blocker')}
        row['old_restore_helper']=info(oldinv[z['old_restored_helper_stream']])
        row['old_restore_helper_stream']=z['old_restored_helper_stream']
        row['new_endpoint']=z['new_endpoint'];core_rows.append(row)
    reused_members=[m for m in members if m['new_reuse_donor']]
    recipient_members=[m for m in members if m['new_recipient']]
    occupied_members=[m for m in members if m['new_kernel_member']]
    core_recipients=[z['helper']for z in core_rows if z['helper']['new_recipient']]
    result=dict(status='PASS_EXACT_ROLE_MAPPING_ONLY',head='10b40041d4ab8a6610083e95bc571aee3468bca2',
                changed_word_fields=['pairs','reads'],old_reuse_pairs=1726,new_reuse_pairs=1728,
                all_virtual_roles=17160,new_independent_helpers_before_sinks=15432,new_all_columns_before_sinks=18952,
                expected_after_seven_sinks=15425,old_kernel_physical_members=len(occupied),
                kernel70_relation_count=len(remapped),kernel70_distinct_virtual_members=len(members),
                transported_recipient_members=recipient_members,transported_reuse_donor_members=reused_members,
                transported_occupied_kernel_members=occupied_members,final12_new_recipient_helpers=core_recipients,
                kernel70_relations=remapped,kernel70_members=members,final12_candidates=core_rows,
                scope='Exact alias/stream mapping and occupancy only. No response, common-cut, aliased frame, suffix, bank or finite-cost admission is asserted. Physical donor roles remain eligible for later full-path checking; recipient keys are excluded from new kernel pivots/donors.')
    (OUTPUT/'role-mapping.json').write_text(json.dumps(result,indent=2)+'\n')
    (OUTPUT/'all-role-map.json').write_text(json.dumps({str(r):phys[alias.get(r,r)]for r in range(17160)},separators=(',',':'))+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in ('kernel70_relations','kernel70_members','final12_candidates')},indent=2))
    return result

if __name__=='__main__':run()
