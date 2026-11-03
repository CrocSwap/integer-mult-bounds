"""Original data-only co-retiming admission checks, exact arithmetic over Q and Z.
This is a local surgery certificate conditional on the retained source-stage contracts.
"""
from pathlib import Path
from collections import defaultdict,Counter
import json,gzip,base64,hashlib
from check_rootcuts import rank,valid_witness
import check_rootcuts
import source_data as sd
HERE=Path(__file__).resolve().parent
def readz(n):return sd.read_json(n.replace('__','/').removesuffix('.base64'))
def contained(ann,basis):return all(sum(x*y for x,y in zip(a,b))==0 for a in ann for b in basis)
def sub(A,B): # ker A contained in ker B
    return rank(A+B)==rank(A)
def add(row,other,c):
    for j,x in other.items():
        row[j]=row.get(j,0)+c*x
        if not row[j]:del row[j]

def run(mutation=None, *, minimal=False):
    w=readz('gen5bit__selected__bit__word_p12.json.gz.base64')
    f={int(k):v for k,v in readz('gen5bit__selected__bit__frames_p12.json.gz.base64')['frames'].items()}
    g=sd.read_json('gen5bit/selected/bit/graph_p12.json');old=check_rootcuts.run()
    restore=sd.read_json('restore-selection.json')
    kernel=sd.read_json('kernel-selection.json')
    targets=sd.read_json('target-selection.json')
    removed={b for a,b in w['pairs']};regs=[s for s in range(17160)if s not in removed]
    assert len(regs)==15434
    stream={s:3520+i for i,s in enumerate(regs)}
    old_restore={z[k]:z for z in restore['entries']for k in('helper','donor')}
    km={z[k]for z in kernel['pairs']for k in('a','b')}|{s for z in kernel['families']for s in[z['pivot']]+z['donors']}
    kernel_entries=[dict(pivot=z['a'],donors=[z['b']],basis=z['basis'],rank=z['rank']) for z in kernel['pairs']]
    kernel_entries += [dict(pivot=z['pivot'],donors=z['donors'],basis=z['basis'],rank=z['rank']) for z in kernel['families']]
    owner={t:z for z in targets['groups']for t in z['targets']}
    gauge_by_t=defaultdict(list)
    for z in w['gauges']:
        for t in z['targets']:gauge_by_t[t].append(z)
    root_by_role=defaultdict(list)
    for i,s in enumerate(w['rootroles']):root_by_role[s].append(i)
    # Conservative UNION of all leaf dependencies, before any cancellations.
    supports=[]
    for i,args in enumerate(g['args']):
        if args is None:
            assert i<1760;supports.append(1<<i)
        else:
            u,v=args;assert u<i and v<i;supports.append(supports[u]|supports[v])
    candidates=[];used_c=set();lost={};rejected=[];kernel_donor_contracts=[];mutated_prefix=False
    for row in old['witnesses']:
        assert valid_witness(row)
        a,b=row['helper_role'],row['donor_role'];bi=row['donor_root_index'];ai=row['helper_root_index']
        assert len(g['roots'][bi]['targets'])==len(g['roots'][ai]['targets'])==1
        t=g['roots'][bi]['targets'][0]
        previous=[i for i,z in enumerate(g['roots'])if t in z['targets']and i<bi and f[w['root_frame'][i]]['dim']==22]
        assert len(previous)==1
        ki=previous[0];c=w['rootroles'][ki];J=row['write_annihilator'];B=row['donor_annihilator']
        assert ki<bi<ai and len(root_by_role[c])==1 and c not in dict(w['pairs'])
        assert stream[a]not in old_restore and stream[b]not in old_restore
        assert stream[c]in old_restore and stream[c]not in km
        prior=old_restore[stream[c]]
        assert prior['dims']==[20,22,22,23]
        assert not contained(B,prior['basis'])
        K=f[w['root_frame'][ki]]['a']
        assert rank(K)==2 and not sub(K,J) and sub(K,B)
        if c in used_c:
            rejected.append(dict(helper=a,reason='Shared K-source would need two distinct promoted target hyperplanes'))
            continue
        used_c.add(c);lost[prior['helper']]=prior
        # Every precursor before the K-event lies in J. The K-event itself is co-retimed.
        predecessors=[]
        for i,z in enumerate(g['roots']):
            if i<ki and t in z['targets']:
                A=f[w['root_frame'][i]]['a'];assert sub(A,J),(a,i)
                predecessors.append(i)
        assert predecessors and max(f[w['root_frame'][i]]['dim']for i in predecessors)==21
        for z in gauge_by_t[t]:assert sub(f[z['frame']]['a'],J)
        group=owner.get(t)
        if group:
            close_basis=group['close_basis']
            if mutation=='incompatible_prefix' and not mutated_prefix:
                coordinate=next(j for j in range(24)if any(a[j]for a in J))
                close_basis=close_basis+[[int(j==coordinate)for j in range(24)]];mutated_prefix=True
            assert group['close_rank']==21 and contained(J,close_basis),'Prefix closing frame outside common frame'
        # The kernel's frozen setup/entrance frames all precede ordinary use;
        # its inverse writes are appended after all original cleanup. Their
        # interval placement remains an explicitly imported stage contract.
        if stream[b] in km:
            entries=[e for e in kernel_entries if stream[b]==e['pivot']or stream[b]in e['donors']]
            assert entries and all(contained(J,e['basis'])for e in entries)
            assert all(stream[b]!=e['pivot']for e in entries),'Overlapping donor is a kernel pivot'
            kernel_donor_contracts.append(dict(donor=b,stream=stream[b],entries=len(entries),
               pivot_entries=sum(stream[b]==e['pivot']for e in entries),
               setup_entry_ranks=[e['rank']for e in entries],all_entry_frames_inside_J=True,
               interval_contract='Imported: setup before first ordinary use, restoration after complete original cleanup'))
        # Earlier delivery at J retains the entire (uncancelled) graph source span.
        bits=supports[g['roots'][bi]['node']];leaves=[s for s in range(1760)if bits>>s&1]
        assert len(leaves)==180
        assert all(not any(sum(z[j]for j in g['labels'][s])for z in J)for s in leaves)
        assert g['roots'][bi]['node']==g['roots'][ai]['node']
        # a has exactly one forward incidence and b is unchanged from that write to the roots.
        ai_ops=[(i,o)for i,o in enumerate(w['ops'])if a in o[:2]]
        assert len(ai_ops)==1 and ai_ops[0][1][:2]==[a,b]
        aop=ai_ops[0][0]
        assert not any(o[0]==b for o in w['ops'][aop+1:])
        candidates.append(dict(helper=a,donor=b,blocker=c,target=t,helper_root=ai,donor_root=bi,
          blocker_root=ki,old_restored_helper=regs[prior['helper']-3520],old_restored_helper_stream=prior['helper'],
          common_frame=row['write_frame_id'],new_endpoint=row['helper_frame_id'],promoted_blocker_frame=row['donor_frame_id'],
          target_precursor_roots=predecessors,prefix_group_present=bool(group),source_union_size=len(leaves)))
    if minimal:
        multiplicity=Counter(z['old_restored_helper_stream'] for z in candidates)
        candidates=[z for z in candidates if multiplicity[z['old_restored_helper_stream']]==2]
        retained={z['old_restored_helper_stream']for z in candidates}
        lost={h:z for h,z in lost.items()if h in retained}
    expected_candidates,expected_undo=(12,6)if minimal else(32,26)
    if mutation=='omit_old_restoration_undo':lost.pop(next(iter(lost)))
    if mutation=='shared_blocker':candidates[1]['blocker']=candidates[0]['blocker']
    if mutation=='wrong_promoted_frame':candidates[0]['promoted_blocker_frame']=candidates[0]['new_endpoint']
    assert {z['old_restored_helper_stream']for z in candidates}<=set(lost),'Missing old restoration undo'
    assert len({z['blocker']for z in candidates})==len(candidates),'Shared blocker'
    for z in candidates:
        promoted=f[z['promoted_blocker_frame']]['a'];cap=f[w['root_frame'][z['donor_root']]]['a']
        assert sub(promoted,cap),'Promoted delivery outside target cap'
    assert len(candidates)==expected_candidates and len(lost)==expected_undo and len(rejected)==2
    aa={z['helper']for z in candidates};bb={z['donor']for z in candidates};cc={z['blocker']for z in candidates}
    assert len(aa)==len(bb)==len(cc)==expected_candidates and not(aa&bb or aa&cc or bb&cc)
    kernel_donor_contracts=[z for z in kernel_donor_contracts if z['donor'] in bb]
    assert not (aa|bb|cc)&set(w['sources'].values()), 'A moved helper is a source carrier with possible partner-mix writes'
    # Construct the literal altered root schedule and compare its EXACT INTEGER
    # linear map on arbitrary independent helper registers and target contents.
    insert={z['blocker_root']:z for z in candidates};omit={z['donor_root']for z in candidates}
    finish={z['helper_root']:z for z in candidates}
    def root_events(i,exclude=None):
        z=g['roots'][i]
        return [(1760*10+t,w['rootroles'][i],z.get('coefficient',1))for t in z['targets']if t!=exclude]
    original=[];modified=[]
    for i,z in enumerate(g['roots']):
        original+=root_events(i)
        if i in insert:
            row=insert[i];modified+=root_events(row['donor_root'])
            # First deliver K-source to its unaffected target(s), then promote
            # that source and the affected target to B and deliver there.
            modified+=root_events(i,exclude=row['target'])
            modified += [(1760*10+row['target'],row['blocker'],z.get('coefficient',1))]
        elif i not in omit:modified+=root_events(i)
        if i in finish:
            row=finish[i];modified.append((row['helper'],row['donor'],-1))
    original += [(z['helper'],z['donor'],-1)for z in candidates]
    def evaluate(events):
        rows={}
        def get(i):return rows.setdefault(i,{i:1})
        for dest,src,coeff in events:add(get(dest),get(src),coeff)
        return {i:row for i,row in rows.items()if row!={i:1}}
    A=evaluate(original);C=evaluate(modified);assert A==C
    corrupted=modified[:];removed_restore=next(i for i,z in enumerate(corrupted)if z[0]in aa)
    del corrupted[removed_restore];assert evaluate(corrupted)!=A
    # Local role-path ledger. Unchanged target dimensions 21->22->23.
    # Per new surgery a loses 23->24; blocker changes 22->24 to 22->23->24.
    gross=Counter({1:len(candidates),2:-len(candidates)})
    gross.update({1:-3*len(lost),2:2*len(lost)})
    residual={2:len(candidates),3:-len(candidates)-len(lost),4:len(lost)}
    assert dict(gross)==({1:-6,2:0}if minimal else{1:-46,2:20})
    assert sum(r*n for r,n in gross.items())==-6
    assert sum(r*n for r,n in residual.items())==-6 and sum(residual.values())==0
    return dict(status='PASS_LOCAL_INTEGER_ROOT_SCHEDULE_CERTIFICATE',head=old['head'],
       selected=len(candidates),undone_old_restorations=len(lost),local_histogram_delta=dict(gross),
       residual_rank_count_delta=residual,literal_stock_delta=-15,unreplicated_stock_delta='-1/4',
       exact_integer_root_schedule_identity=True,missing_restoration_control_rejected=True,
       unchanged_root_read_coefficients=True,candidates=candidates,rejected=rejected,
       kernel_donor_contracts=kernel_donor_contracts,
       scope='Local source-data surgery certificate with exact integer root map, geometry/source-span conditions and net ledger. Full emitted postkernel word and global all-column replay have NOT been reconstructed. Existing valid monotone source-stage/target-prefix/sink contracts are retained assumptions; no certified new multiplication exponent is claimed.')

if __name__=='__main__':
    r=run();(HERE/'coretime-result.json').write_text(json.dumps(r,indent=2)+'\n')
    print(r['status'],r['selected'],'new restorations,',r['undone_old_restorations'],'old restorations undone, delta',r['local_histogram_delta'])
