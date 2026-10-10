"""Bind supplied independent bridge/norm/chart results to the candidate15 invoice.
Only JSON and inert source bytes are read. No supplied checker code is executed.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter,defaultdict
from fractions import Fraction as F
from pathlib import Path
import gzip,hashlib,json,struct
import reproduce_p10 as b
import finite_invoice
support=b.support
HERE=support.out('arithmetic','placeholder').parent
BRIDGE=support.OUTPUT/'bridge15'
CLOSURE=support.HERE/'witnesses'
CERT=support.OUTPUT/'certificates'

def sha(data):return hashlib.sha256(data).hexdigest()
def run():
    paths={'candidate':CLOSURE/'candidate15.json','bridge':BRIDGE/'bridge-result.json','norm':BRIDGE/'scalar-bounds-result.json','charts':CERT/'candidate15-charts.json','bridge_checker':support.HERE/'bridge15/check_bridge.py','norm_checker':support.HERE/'bridge15/check_scalar_bounds.py','banks':CERT/'candidate15-bank-receipt.json','bank_table':CERT/'candidate15-bank-addresses.bin.gz','pricing':HERE/'candidate15-pricing.json','source_pins':support.HERE/'inputs.json'}
    raw={k:p.read_bytes() for k,p in paths.items()};records={k:json.loads(raw[k]) for k in ('candidate','bridge','norm','charts','banks','pricing')};hashes={k:sha(v) for k,v in raw.items()}
    cand,bridge,norm,charts=[records[k] for k in ('candidate','bridge','norm','charts')]
    for k in ('bridge','norm','charts','banks'):assert records[k]['candidate_sha256']==hashes['candidate'],('candidate mismatch',k)
    assert cand['source_head']==bridge['head']==norm['head']==charts['source_head']==b.HEAD
    assert bridge['source_pins_sha256']==hashes['source_pins'],'source pin catalog mismatch'
    assert bridge['checker_sha256']==hashes['bridge_checker'],'stale bridge checker receipt'
    assert norm['checker_sha256']==hashes['norm_checker'],'stale norm checker receipt'
    assert norm['bridge_checker_sha256']==hashes['bridge_checker'],'stale norm-to-bridge checker binding'
    assert charts['bridge_receipt_sha256']==hashes['bridge'],'stale chart-to-bridge receipt binding'
    assert charts['geometry_receipt_bound']
    assert bridge['all_column_formal_composition_forward_inverse'] and bridge['omitted_setup_and_restore_rejected']
    assert bridge['final_full_endpoints_checked'] and bridge['reorder_transport']['all_new_scalar_edits_outside_intervals']
    edges=[(d,e['pivot']) for e in cand['entries'] for d in e['donors']]
    assert len(cand['entries'])==15 and len(edges)==40==bridge['setup_adds']==bridge['restore_adds']==norm['setup_restore_pairs']
    assert len({x for edge in edges for x in edge})==32
    assert {e['pivot'] for e in cand['entries']}.isdisjoint({d for e in cand['entries'] for d in e['donors']})
    assert all(len(e['basis'])==e['rank']==1 for e in cand['entries'])
    assert bridge['local_histogram_delta']=={'1':17,'2':30,'3':-30,'4':2,'5':-2}
    assert bridge['residual_family_delta']=={'20':-15,'19':15}
    # The published construction's scalar ADD edges have coefficient +1;
    # its inverse layer has coefficient -1. Confirm that this is what the
    # supplied norm checker majorizes, without executing that checker.
    norm_text=raw['norm_checker'].decode()
    assert "newsetup=[(d,z['pivot'],1)for z in witness for d in z['donors']]" in norm_text
    assert 'for e in reversed(newsetup):add(new,e)' in norm_text
    source_frames=b.read('bitword/selected/bit/frames_p10.json.gz')['frames']
    programs={r['program_id']:r for r in charts['factor_programs']}
    assert len(programs)==38==charts['charts']
    maxnum=maxden=maxfactors=0;determinant_primes=set()
    for program in programs.values():
        columns=program['basis_columns'];assert len(columns)==20 and all(len(c)==20 for c in columns)
        mat=[[F(x) for x in row] for row in zip(*columns)]
        assert len(program['factors'])==program['count']
        maxfactors=max(maxfactors,len(program['factors']))
        for kind,i,j,c in program['factors']:
            q=F(c);maxnum=max(maxnum,abs(q.numerator));maxden=max(maxden,q.denominator)
            if kind=='swap':mat[i],mat[j]=mat[j],mat[i]
            elif kind=='scale':mat[i]=[q*x for x in mat[i]]
            elif kind=='add':mat[i]=[x+q*y for x,y in zip(mat[i],mat[j])]
            else:raise AssertionError('unknown rational factor')
        assert mat==[[F(int(i==j)) for j in range(20)] for i in range(20)]
        remaining=abs(int(program['determinant']));assert remaining>0
        for prime in (2,3,11):
            while remaining%prime==0:determinant_primes.add(prime);remaining//=prime
        assert remaining==1,('unexpected determinant factor',remaining)
    assert (maxfactors,maxnum,maxden)==(331,99,297)==(charts['max_factors'],charts['max_numerator'],charts['max_denominator'])
    assert maxfactors<=400 and maxnum<2**80 and maxden<2**80
    assert charts['normalizer_bound']==599==max(400,maxfactors)+99+100
    assert charts['dimension']==20 and charts['metric']=='9I-J' and charts['exterior_formula']=='11*a-sum(a)'
    paths_by_role={r['role']:r for r in bridge['selected_paths']};uses=defaultdict(dict)
    assert len(paths_by_role)==32
    def gram(a,c):return 9*sum(x*y for x,y in zip(a,c))-sum(a)*sum(c)
    for use in charts['role_uses']:
        role=use['role'];assert use['kind'] not in uses[role];uses[role][use['kind']]=use
        path=paths_by_role[role];assert use['stream']==path['stream'];line=path['entrance_basis'][0]
        program=programs[use['program_id']];columns=program['basis_columns'];rank=program['residual_rank'];assert rank==use['rank']
        if use['kind']=='first_frame_quotient':
            assert use['frame']==path['first_frame'] and rank==path['first_dimension']-1
            assert columns[rank]==line
            assert all(gram(c,line)==0 for c in columns[:rank])
            frame=source_frames[str(path['first_frame'])]
            if 'a' in frame:
                assert all(sum(x*y for x,y in zip(a,c))==0 for a in frame['a'] for c in columns[:rank+1])
            else:
                pivots={}
                for vec in frame['b']:
                    row=list(map(F,vec))
                    for j,pivot in sorted(pivots.items()):
                        q=row[j];row=[x-q*y for x,y in zip(row,pivot)]
                    nz=next((i for i,x in enumerate(row) if x),None)
                    if nz is not None:
                        q=row[nz];pivots[nz]=[x/q for x in row]
                assert len(pivots)==path['first_dimension']
                for vec in columns[:rank+1]:
                    row=list(map(F,vec))
                    for j,pivot in sorted(pivots.items()):
                        q=row[j];row=[x-q*y for x,y in zip(row,pivot)]
                    assert not any(row)

        elif use['kind']=='pivot_residual':
            assert path['kernel_kind']=='pivot' and rank==19 and columns[19]==line
            assert all(gram(c,line)==0 for c in columns[:19])
        elif use['kind']=='donor_line_entrance':
            assert path['kernel_kind']=='donor' and rank==1 and columns[0]==line
        else:raise AssertionError('unknown chart use')
    assert len(charts['role_uses'])==64 and set(uses)==set(paths_by_role)
    for role,path in paths_by_role.items():assert set(uses[role])=={'first_frame_quotient','pivot_residual' if path['kernel_kind']=='pivot' else 'donor_line_entrance'}
    forward=norm['forward']['certified_new_bound'];inverse=norm['inverse']['certified_new_bound']
    assert forward==norm['forward']['inherited_bound']+norm['forward']['max_added_majorant']==49937
    assert inverse==norm['inverse']['inherited_bound']+norm['inverse']['max_added_majorant']==1194200
    payload=64*forward**3*inverse**2
    assert payload==norm['payload_bound'] and payload.bit_length()==norm['payload_bits']==94
    assert payload<2**104 and norm['retained_payload_cap_2_to104']
    banks=records['banks'];pricing=records['pricing']
    assert banks['source_head']==b.HEAD and banks['pricing_sha256']==hashes['pricing']
    assert banks['compressed_table_sha256']==hashes['bank_table']
    table=gzip.decompress(raw['bank_table']);assert sha(table)==banks['one_stage_table_uncompressed_sha256']
    assert banks['all_blocks_full'] and banks['all_role_replica_pairs_exactly_once'] and banks['stage_bank_ranges_disjoint']
    assert len(table)==20*493380 and banks['total_assignments']==5*493380==2466900
    word=b.read('bitword/selected/bit/word_p10.json.gz')
    removed={z for a,z in word['pairs']};original_roles=sorted(set(range(9120))-removed)
    stream_to_role={1920+i:r for i,r in enumerate(original_roles)}
    roles=set(original_roles)-{r['role'] for r in b.read('sink-selection.json')['sinks']}
    entrances={r:0 for r in roles};endpoints={r:20 for r in roles}
    for row in word['gauges']:
        if row['role'] in roles:entrances[row['role']]=row['dim']
    kernel=b.read('kernel-selection.json')
    for row in kernel['pairs']+kernel['families']:entrances[stream_to_role[row.get('pivot',row.get('a'))]]=row['rank']
    for row in b.read('restore-selection.json')['entries']:endpoints[stream_to_role[row['helper']]]=row['rank']
    for row in cand['entries']:
        role=stream_to_role[row['pivot']];assert role==row['virtual_pivot'] and entrances[role]==0 and endpoints[role]==20;entrances[role]=1
    widths={r:endpoints[r]-entrances[r] for r in roles};assert len(widths)==8223
    census=Counter(widths.values());assert dict(census)=={int(k):v for k,v in pricing['residual_census'].items()}=={int(k):v for k,v in banks['residual_census'].items()}
    rows=list(struct.iter_unpack('>IIIII',table));seen=bytearray(9120*60);last_bank=0;end=0
    for role,replica,bank,offset,width in rows:
        assert role in widths and 0<=replica<60 and width==widths[role]
        if bank!=last_bank:
            assert bank==last_bank+1 and end==100;last_bank=bank;end=0
        assert offset==end and end+width<=100;end+=width
        key=60*role+replica;assert not seen[key];seen[key]=1
    assert last_bank+1==banks['banks_per_stage']==pricing['banks_per_stage']==85707 and end==100
    assert sum(seen)==493380 and all(seen[60*r+i] for r in roles for i in range(60))
    digest=hashlib.sha256()
    for stage in range(5):
        for role,replica,bank,offset,width in rows:digest.update(struct.pack('>IIIIII',stage,role,replica,stage*85707+bank,offset,width))
    assert digest.hexdigest()==banks['five_stage_assignment_sha256']
    assert banks['literal_stock']==pricing['literal_stock']==60*4*960+5*85707==658935
    invoice=finite_invoice.run()
    invoice['inherited_payload_envelope']['replaced_by_candidate_payload_envelope']=True
    invoice.update(status='PASS_CANDIDATE15_RECEIPT_BOUND_FINITE_ARITHMETIC',
        candidate_changed_stage_checks_bound=True,physical_admission=False,
        bound_receipts={k:dict(path=str(paths[k]),sha256=hashes[k],bytes=len(raw[k])) for k in paths},
        verified_changed_stage=dict(gross_added_unit_ADDs=80,setup_pairs=40,selected_roles=32,all_column_dimension=bridge['all_column_dimension'],chart_programs=38,chart_uses=64,chart_programs_independently_replayed=True,chart_role_uses_independently_bound=True,max_chart_factors=331,max_factor_numerator=99,max_factor_denominator=297,retained_global_chart_bound=400,normalizer_bound=599,new_chart_determinant_prime_support=sorted(determinant_primes),removed_unit_reads_verified_but_not_credited=bridge['removed_initial_unit_additions']),
        scalar_event_accounting=dict(added_unit_ADDs=80,removed_initial_unit_ADDs=bridge['removed_initial_unit_additions'],net_local_ADD_delta=80-bridge['removed_initial_unit_additions'],conservative_unused_credit_all_stages_and_replicas=5*60*bridge['removed_initial_unit_additions'],invoice_credits_removed_reads=False),
        bank_binding=dict(assignments_per_stage=493380,total_assignments=2466900,banks_per_stage=85707,literal_stock=658935,role_widths_independently_rebuilt=True,table_independently_checked=True,all_blocks_full=True,all_role_replica_pairs_exactly_once=True,stage_ranges_disjoint=True),
        candidate_payload_envelope=dict(forward_row_l1=forward,inverse_row_l1=inverse,payload_bound=payload,payload_bits=94,retained_strict_upper='2^104',validated_against_bound_receipt=True),
        pending_obligations=[
            'Inherited full physical decoder correctness, frozen-stage replays and raw 133-crossing reorder admission remain hypotheses; the changed-stage bridge transports them and does not rerun every raw crossing.',
            'All 2,466,900 role/replica/stage bank addresses and changed chart uses are independently bound. Their use throughout a fully generated downstream production word remains under the checked bridge and inherited bank/compiler interfaces; no upstream production verifier was executed.',
            'Inherited prime supply must avoid the required denominator/determinant primes, including2,3,11 for these changed charts. No all-characteristics-greater-than5 assertion is made.',
            'Inherited weighted compiler, common ancestor chart, restored row reserve, routing, precision/recovery, complex correctness and analytic reduction interfaces remain conditional.',
            'The full absorbed constant C_full is not instantiated: it must include this displayed coefficient times inherited primitive, wrapper and preceding ordinary-level constants. No numerical all-size cutoff or unconditional theorem is claimed.'
        ],scope='Independent exact finite-formula arithmetic bound to matching candidate, changed-stage bridge, scalar majorant and freshly replayed chart receipts. Inherited full compiler/decoder/constants and all-size hypotheses remain explicit.')
    for k,path in paths.items():assert sha(path.read_bytes())==hashes[k],('concurrent input changed',k)
    target=HERE/'bound-receipt-inputs';target.mkdir(exist_ok=True)
    for k,data in raw.items():(target/(k+('.py.txt' if k.endswith('checker') else '.bin.gz' if k=='bank_table' else '.json'))).write_bytes(data)
    return invoice
if __name__=='__main__':
    r=run();encoded=json.dumps(b.ae.serial(r),indent=2)+'\n';(HERE/'candidate15-finite-invoice-bound.json').write_text(encoded);(HERE/'candidate15-finite-invoice.json').write_text(encoded);print(json.dumps({k:r[k] for k in ('status','verified_changed_stage','candidate_payload_envelope')},indent=2))
