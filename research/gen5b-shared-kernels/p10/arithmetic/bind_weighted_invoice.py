"""Fresh weighted892/fixed19 finite arithmetic and cross-receipt binding.
All supplied checkers remain inert. This module executes only original arithmetic
modules and the two hash-guarded prior arithmetic engines.
"""
from collections import Counter,defaultdict
from fractions import Fraction as F
from pathlib import Path
import gzip,hashlib,json,struct
import reproduce_p10 as b
import price_candidate as pricing
from finite_invoice import bill
import check_seam_contract as seam_check
import check_scalar_counts as scalar_check
support=b.support
HERE=support.out('arithmetic','placeholder').parent
PARAM=support.OUTPUT/'matching'
BRIDGE=support.OUTPUT/'weighted'
CERT=support.OUTPUT/'certificates'
CLOSURE=support.HERE/'witnesses'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def run():
    paths=dict(word=PARAM/'word_weighted892.json',base=PARAM/'scalar_and_seams892.json',census=PARAM/'full_path_census892.json',candidate=BRIDGE/'rebound-candidate19.json',original_candidate=CLOSURE/'candidate19-residue4.json',transport=BRIDGE/'transport-result.json',targets=BRIDGE/'target-chronology-result.json',target_checker=support.HERE/'weighted/check_target_chronology.py',norms=BRIDGE/'scalar-recurrence-result.json',norm_checker=support.HERE/'weighted/check_scalar_recurrence.py',charts=CERT/'rebound-candidate19-charts.json',seam_charts=CERT/'weighted892-seam-charts.json',banks=CERT/'weighted892-candidate19-bank-receipt.json',bank_table=CERT/'weighted892-candidate19-bank-addresses.bin.gz',prior_price=HERE/'provisional892-candidate19-pricing.json')
    paths.update(transport_checker=(support.HERE/'weighted')/'check_transport.py',source_loader=(support.HERE/'weighted')/'weighted_source_data.py',reorder=BRIDGE/'reorder-transport-result.json',reorder_checker=(support.HERE/'weighted')/'check_reorder_transport.py')
    raw={k:p.read_bytes() for k,p in paths.items()};hashes={k:sha(x) for k,x in raw.items()};data={k:json.loads(x) for k,x in raw.items() if not k.endswith('checker') and k not in ('source_loader','bank_table')}
    word=data['word'];candidate=data['candidate'];transport=data['transport'];targets=data['targets'];norm=data['norms'];charts=data['charts'];banks=data['banks']
    assert candidate['source_head']==transport['head']==targets['head']==norm['head']==charts['source_head']==banks['source_head']==b.HEAD
    assert candidate['overlay_sha256']==transport['overlay_sha256']==targets['overlay_sha256']==norm['overlay_sha256']==charts['candidate_word_sha256']==banks['candidate_word_sha256']==hashes['word']
    assert norm['rebound_candidate_sha256']==charts['candidate_sha256']==banks['candidate_sha256']==hashes['candidate']
    assert transport['original_candidate_sha256']==norm['original_candidate_sha256']==hashes['original_candidate']
    assert transport['rebound_candidate_sha256']==hashes['candidate']
    assert transport['checker_sha256']==hashes['transport_checker'] and transport['source_loader_sha256']==hashes['source_loader']
    dependencies={paths[k].name:hashes[k] for k in ('transport_checker','source_loader','target_checker','norm_checker','targets','candidate')}
    for receipt in (targets,norm):
        assert receipt['dependency_sha256']
        for name,value in receipt['dependency_sha256'].items():assert dependencies[name]==value,('stale dependency',name)
    reorder=data['reorder']
    assert reorder['head']==b.HEAD and reorder['overlay_sha256']==hashes['word'] and reorder['rebound_candidate_sha256']==hashes['candidate']
    assert reorder['checker_sha256']==hashes['reorder_checker']
    assert reorder['moves']==133 and reorder['moved_ports']==266 and reorder['all_anchors_survive'] and reorder['all_noncommuting_traces_equal']
    assert len(reorder['receipts'])==133 and all(r['all_anchor_candidates_semantically_preserved'] and r['noncommuting_trace_and_relative_position_identical'] for r in reorder['receipts'])
    assert data['original_candidate']['entries']==candidate['entries']
    assert norm['checker_sha256']==hashes['norm_checker'] and targets['checker_sha256']==hashes['target_checker']
    assert charts['bridge_receipt_sha256']==hashes['transport'] and charts['geometry_receipt_bound']
    assert transport['kernel_entries_rebound']==775 and transport['kernel_relations_and_cut_triples_exact']
    assert transport['kernel_delta_old']==transport['kernel_delta_new'] and transport['complete_new_paths_checked']==8228
    assert transport['candidate19_all_column_f2_identity_forward_reverse'] and transport['candidate19_omission_controls_rejected']
    assert all(not values for values in transport['direct_role_overlaps'].values())
    assert targets['all120_literal_target_relations']==120 and targets['all480_group_members_checked_at_close']
    assert targets['all_gauge_target_paths_nested'] and targets['compressed_target_state_containment_checks']>=480 and targets['negative_controls']
    assert targets['group119']['new_close']==328527 and min(targets['new_late_gauge_records'].values())>328527
    seam=seam_check.run();counts=scalar_check.run()
    assert seam['inputs']['word']['sha256']==counts['candidate_word_sha256']==hashes['word']
    assert counts['rebound_candidate_sha256']==hashes['candidate']
    assert norm['removed_initial_reads']==dict(old=23140,old_units=23140,new=188,new_units=188)
    assert norm['setup_counts']==dict(old=1157,new=58)
    assert norm['all_setup_and_restore_omission_controls_rejected']
    for direction,expected in [('baseline_forward',31433),('baseline_inverse',966260)]:
        r=norm[direction];assert r['all_columns'] and r['columns']==10150 and r['weighted_additions']==334655 and r['literal_unit_additions']==336575 and r['max_row_l1']==expected
    for direction in ('forward','inverse'):
        r=norm[direction];assert r['all_columns'] and r['columns']==10148 and r['weighted_additions']==counts['post_fixed19_weighted_ADDs']==334583 and r['literal_unit_additions']==counts['post_fixed19_unit_ADDs']==336503
        assert sum(int(k)*v for k,v in r['coefficient_histogram'].items())==336503
    forward=norm['forward']['max_row_l1'];inverse=norm['inverse']['max_row_l1'];payload=64*forward**3*inverse**2
    assert (forward,inverse)==(33129,984792) and payload==norm['payload_bound'] and payload.bit_length()==norm['payload_bits']==91 and payload<2**104 and norm['retained_payload_cap_2_to104']
    # Reprice from independently measured path deltas and rebound witness.
    hd=Counter({int(k):v for k,v in data['census']['helper_delta'].items()});hd.update({int(k):v for k,v in candidate['local_histogram_delta'].items()})
    rd=Counter({int(k):v for k,v in data['census']['residual_delta'].items()});rd.update({int(k):v for k,v in candidate['residual_family_delta'].items()})
    result=pricing.price(dict(hd),dict(rd),label='Receipt-bound weighted892 plus fixed19; inherited compiler/full-C conditions remain')
    assert result['literal_stock']==658905 and result['banked_calls']==249085 and result['banked_rank_mass']==1096135 and result['physical_R']==8221
    assert result['assembly']['kappa']==F(769661484777339,10**18)
    for key in ('literal_stock','banked_calls','banked_rank_mass','physical_R','banks_per_stage','residual_census'):
        assert json.loads(json.dumps(b.ae.serial(result[key])))==data['prior_price'][key]
    # Fresh endpoint and first-quotient factor program replay and role binding.
    programs={r['program_id']:r for r in charts['factor_programs']};assert len(programs)==47
    frame_data=b.read('bitword/selected/bit/frames_p10.json.gz')['frames'];maxops=maxnum=maxden=0
    for program in programs.values():
        columns=program['basis_columns'];mat=[[F(x) for x in row] for row in zip(*columns)]
        assert len(mat)==20 and all(len(row)==20 for row in mat)
        assert len(program['factors'])==program['count'];maxops=max(maxops,len(program['factors']))
        for kind,i,j,c in program['factors']:
            q=F(c);maxnum=max(maxnum,abs(q.numerator));maxden=max(maxden,q.denominator)
            if kind=='swap':mat[i],mat[j]=mat[j],mat[i]
            elif kind=='scale':mat[i]=[q*x for x in mat[i]]
            elif kind=='add':mat[i]=[x+q*y for x,y in zip(mat[i],mat[j])]
            else:raise AssertionError('unknown factor')
        assert mat==[[F(int(i==j)) for j in range(20)] for i in range(20)]
        assert 0<abs(int(program['determinant']))<2**80
    assert (maxops,maxnum,maxden)==(331,220,297) and charts['normalizer_bound']==599==max(400,maxops)+99+100
    selected={r['role']:r for r in transport['selected_paths']};assert len(selected)==41
    lines={};pivots={e['virtual_pivot'] for e in candidate['entries']}
    for e in candidate['entries']:
        for role in [e['virtual_pivot']]+e['virtual_donors']:
            assert role not in lines or lines[role]==e['basis'][0];lines[role]=e['basis'][0]
    seen=defaultdict(set)
    for use in charts['role_uses']:
        role=use['role'];path=selected[role];line=lines[role];kind=use['kind'];assert kind not in seen[role];seen[role].add(kind)
        assert use['stream']==path['physical'];program=programs[use['program_id']];columns=program['basis_columns'];rank=program['residual_rank'];assert rank==use['rank']
        if kind=='first_frame_quotient':
            assert use['frame']==path['frames'][0] and rank==path['dimension']-1 and columns[rank]==line
            assert all(seam_check.belongs(c,frame_data[str(use['frame'])]) for c in columns[:rank+1])
            assert all(seam_check.gram(c,line)==0 for c in columns[:rank])
        elif kind=='pivot_residual':assert role in pivots and rank==19 and columns[19]==line and all(seam_check.gram(c,line)==0 for c in columns[:19])
        elif kind=='donor_line_entrance':assert role not in pivots and rank==1 and columns[0]==line
        else:raise AssertionError('unknown chart role use')
    assert len(charts['role_uses'])==82 and set(seen)==set(selected)
    for role,kinds in seen.items():assert kinds=={'first_frame_quotient','pivot_residual' if role in pivots else 'donor_line_entrance'}
    # Reconstruct exact new role widths, then validate the supplied binary table.
    removed={recipient for donor,recipient in word['pairs']};roles0=sorted(set(range(9120))-removed);inv={1920+i:r for i,r in enumerate(roles0)}
    roles=set(roles0)-{r['role'] for r in b.read('sink-selection.json')['sinks']};entrances={r:0 for r in roles};ends={r:20 for r in roles}
    for row in word['gauges']:
        if row['role'] in roles:entrances[row['role']]=row['dim']
    kernel=b.read('kernel-selection.json')
    for row in kernel['pairs']+kernel['families']:entrances[inv[row.get('pivot',row.get('a'))]]=row['rank']
    for row in b.read('restore-selection.json')['entries']:ends[inv[row['helper']]]=row['rank']
    for e in candidate['entries']:
        role=inv[e['pivot']];assert role==e['virtual_pivot'] and entrances[role]==0 and ends[role]==20;entrances[role]=1
    widths={r:ends[r]-entrances[r] for r in roles};assert len(widths)==8221
    assert Counter(widths.values())==Counter(result['residual_census'])
    assert banks['pricing_sha256']==hashes['prior_price'] and banks['compressed_table_sha256']==hashes['bank_table']
    table=gzip.decompress(raw['bank_table']);assert sha(table)==banks['one_stage_table_uncompressed_sha256']
    assert len(table)==493260*20;rows=list(struct.iter_unpack('>IIIII',table));used=bytearray(9120*60);lastbank=0;offset_end=0
    for role,replica,bank,offset,width in rows:
        assert role in widths and 0<=replica<60 and width==widths[role]
        if bank!=lastbank:assert bank==lastbank+1 and offset_end==100;lastbank=bank;offset_end=0
        assert offset==offset_end and offset+width<=100;offset_end+=width
        idx=60*role+replica;assert not used[idx];used[idx]=1
    assert lastbank+1==banks['banks_per_stage']==85701 and offset_end==100 and sum(used)==493260
    assert all(used[60*r+i] for r in roles for i in range(60))
    digest=hashlib.sha256()
    for stage in range(5):
        for role,replica,bank,offset,width in rows:digest.update(struct.pack('>IIIIII',stage,role,replica,stage*85701+bank,offset,width))
    assert digest.hexdigest()==banks['five_stage_assignment_sha256'] and banks['total_assignments']==2466300
    assert banks['literal_stock']==60*4*960+5*85701==result['literal_stock']
    charge=bill(result['literal_stock'],result['banked_calls'],counts['conservative_invoice_weighted_ADDs'],counts['conservative_invoice_unit_ADDs'],R=8221)
    exact=bill(result['literal_stock'],result['banked_calls'],counts['post_fixed19_weighted_ADDs'],counts['post_fixed19_unit_ADDs'],R=8221)
    assert charge['coefficient']==25415456130362201 and charge['coefficient']-exact['coefficient']==188*5*60==56400
    assert charge['coefficient']<2**80 and charge['coefficient_terms']['bank_selectors']<2**40
    report=dict(status='PASS_RECEIPT_BOUND_WEIGHTED892_FIXED19_FINITE_ARITHMETIC',physical_admission=False,all_size_theorem=False,head=b.HEAD,
        inputs={k:dict(path=str(paths[k]),bytes=len(raw[k]),sha256=hashes[k]) for k in paths},pricing=result,scalar_count_contract=counts,seam_cost_contract=seam,
        bound_target_chronology=dict(groups=120,group_members=480,close_containment_checks=targets['compressed_target_state_containment_checks'],group119_close=328527,new_late_gauge_records=targets['new_late_gauge_records'],negative_controls=targets['negative_controls']),
        bound_reorder_transport=dict(moves=133,moved_ports=266,all_anchors_survive=True,all_noncommuting_traces_equal=True,receipt_sha256=hashes['reorder']),
        candidate_geometry=dict(programs=47,chart_uses=82,selected_roles=41,max_factors=331,max_numerator=220,max_denominator=297,retained_global_chart_bound=400,normalizer_bound=599,programs_and_role_uses_independently_replayed=True),
        bank_binding=dict(assignments_per_stage=493260,total_assignments=2466300,banks_per_stage=85701,stock=658905,independently_checked=True),
        scalar_payload=dict(forward=forward,inverse=inverse,bound=payload,bits=91,retained_cap=104,all_columns_before_reorder=10148,scalar_recurrence_and_baseline_crosscheck_bound=True),
        finite_invoice=charge,unused_removed_read_credit=56400,exact_count_variant_coefficient=exact['coefficient'],interior_seam_incremental_surcharge=0,
        remaining_conditions=['All133 moved semantic anchor-incidence and noncommuting traces are freshly compared; application of the unchanged local identity still uses the inherited raw crossing proof. No final raw-record/hash regeneration is claimed.','Full final production raw-record/hash regeneration remains distinct from these finite arithmetic and semantic certificates.','Inherited weighted compiler, common ancestor chart, row restoration, prime supply, descriptor/precision/recovery and complex/analytic interfaces remain hypotheses.','The full C constant, including primitive, wrapper and prior ordinary-level constants, is not instantiated. The displayed coefficient is a ring/recipe count, not a measured Turing-machine constant or unconditional all-size theorem.'])
    for k,path in paths.items():assert sha(path.read_bytes())==hashes[k],('concurrent source changed',k)
    snapshots=HERE/'weighted-bound-inputs';snapshots.mkdir(exist_ok=True)
    for k,blob in raw.items():
        suffix='.bin.gz' if k=='bank_table' else '.py.txt' if k.endswith('checker') or k=='source_loader' else '.json';(snapshots/(k+suffix)).write_bytes(blob)
    return report
if __name__=='__main__':
    r=run();(HERE/'weighted892-finite-invoice-bound.json').write_text(json.dumps(b.ae.serial(r),indent=2)+'\n');print(json.dumps(dict(status=r['status'],coefficient=r['finite_invoice']['coefficient'],payload=r['scalar_payload'],banks=r['bank_binding'],kappa=r['pricing']['assembly']['kappa_decimal']),indent=2))
