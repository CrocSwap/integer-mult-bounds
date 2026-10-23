"""Independent exact finite invoice and exhaustive direct dependency binding.
External checkers remain inert text/data here. Only independently authored
modules and the standard library execute. No fixed 19-relation closure is included.
"""
from collections import Counter,defaultdict
from fractions import Fraction as F
from pathlib import Path
import gzip,json,hashlib,struct
import context as c

def clean(x):return {int(k):v for k,v in x.items()if v}
def hashraw(raw):return hashlib.sha256(raw).hexdigest()
def bill(stock,calls,weighted,units,R=8223,chart_max=400):
    m=100;N=200;d=10000;T=60;v=960;h=20
    E=T*calls;J=T*(24*v+10*R);normalizer=chart_max+99+100;K=2*5*T*((stock-1)+R*m*normalizer)
    terms=dict(unit_expanded_additions=T*(5*units+6*v),high_affine_factors=J*16*(d+1)**2,low_transpositions=J*(stock+h),generic_wrappers=E*(8*m*m+8),matrix_preparation=E*128*N**3,global_matrix_preparation=16*m**3,copy_erase_episodes=5*h*T,paid_child_overhead=E,bank_selectors=K,constant=1)
    return dict(m=m,N=N,d=d,h=h,v=v,replicas=T,R=R,stock=stock,banked_calls=calls,literal_paid_children=E,local_weighted_additions=weighted,local_unit_additions=units,weighted_additions=T*(5*weighted+6*v),route_families=J,chart_factor_bound=chart_max,normalizer_factor_bound=normalizer,coefficient_terms=terms,coefficient=sum(terms.values()),fallback_per_child=32*m*m,fallback_generic_count=6*N*(N-1)+3*N+6*(N-1),internal_row_coefficient=d+1,external_complex_row_coefficient=20161)

def paths():
    A=c.ADMISSION_OUTPUT;B=c.ARITHMETIC;M=c.MATCHING;O=c.OUTPUT;H=c.HERE;P=c.BASE
    out=dict(word=c.WORD,matching=M/'matching-result.json',matching_optimality=M/'matching-optimality-certificate.json',matching_audit=M/'audit-result.json',path_delta=M/'weighted890-delta.json',price=B/'weighted890-price.json',baseline=B/'baseline-receipt.json',arithmetic_result=B/'arithmetic-result.json',second_moment=B/'second-moment-result.json',transport=A/'transport-result.json',kernel_paths=A/'kernel-path-receipts.json',kernels=A/'rebound-kernel-entries.json',later_selections=A/'rebound-later-selections.json',role_map=A/'virtual-physical-map.json',targets=A/'target-chronology-result.json',norms=A/'scalar-recurrence-result.json',reorder=A/'reorder-transport-result.json',chart_summary=O/'chart-receipt.json',endpoint_charts=O/'endpoint-charts.json.gz',seam_charts=O/'seam-charts.json.gz',banks=O/'bank-receipt.json',bank_table=O/'bank-addresses.bin.gz',source_manifest=c.MANIFEST,admission_manifest=c.MANIFEST,matching_graph=M/'postdescent_graph.json')
    for name in ('check_transport.py','check_target_chronology.py','check_scalar_recurrence.py','check_reorder_transport.py','weighted_source_data.py','admission_config.py'):out['admission/'+name]=c.ADMISSION/name
    for name in ('context.py','check_charts.py','check_banks.py','bind_finite.py'):out['finite/'+name]=H/name
    out['finite/chart_rational.py']=c.RATIONAL
    out['finite/chart_loader.py']=H/'chart_rational.py'
    for name in ('select_matching.py','census_matching.py','audit_matching.py'):out['matching/'+name]=P/'matching'/name
    for name in ('price.py','reproduce_p10.py','price_candidate.py','check_second_moment.py'):out['arithmetic/'+name]=P/'arithmetic'/name
    out['support.py']=P/'support.py'
    for name in ('exact_intervals.py','assembly_arithmetic.py'):out['authored/'+name]=P.parent/name
    out['authored/price_candidate.py']=P.parent/'p10/arithmetic/price_candidate.py'
    return out

def load_bundle():
    ps=paths();raw={k:p.read_bytes()for k,p in ps.items()};hashes={k:hashraw(v)for k,v in raw.items()}
    data={k:json.loads(gzip.decompress(v)if ps[k].name.endswith('.gz')else v)for k,v in raw.items()if ps[k].name.endswith(('.json','.json.gz'))}
    return ps,raw,hashes,data

def bindings(h,d):
    assert h['word']==c.WORD_SHA
    for name in ('matching','transport','targets','norms','reorder'):
        r=d[name];assert r['head']==c.HEAD
        assert r.get('overlay_sha256',r.get('candidate_sha256'))==h['word']
    checker={'matching':'matching/select_matching.py','transport':'admission/check_transport.py','targets':'admission/check_target_chronology.py','norms':'admission/check_scalar_recurrence.py','reorder':'admission/check_reorder_transport.py'}
    for name,key in checker.items():assert d[name]['checker_sha256']==h[key],('stale checker',name)
    assert d['matching']['graph_sha256']==h['matching_graph']
    assert d['transport']['source_loader_sha256']==h['admission/weighted_source_data.py']
    deps={Path(k).name:v for k,v in h.items()if k.startswith('admission/')};deps['target-chronology-result.json']=h['targets']
    for name in ('targets','norms'):
        for dep,value in d[name]['dependency_sha256'].items():assert deps[dep]==value,('stale receipt dependency',dep)
    assert d['source_manifest']['head']==d['admission_manifest']['head']==c.HEAD
    src={r['path']:(r['sha256'],r['git_blob'],r['bytes'])for r in d['source_manifest']['files']}
    assert src=={r['path']:(r['sha256'],r['git_blob'],r['bytes'])for r in d['admission_manifest']['files']}
    for name in ('endpoint_charts','seam_charts','banks'):
        r=d[name];assert r['head']==c.HEAD and r['word_sha256']==h['word']
        assert r['source_manifest_sha256']==h['source_manifest'] and r['context_sha256']==h['finite/context.py']
        assert r['checker_sha256']==h['finite/check_banks.py'if name=='banks'else 'finite/check_charts.py']
    assert d['endpoint_charts']['rational_checker_sha256']==h['finite/chart_rational.py']
    for name,key in [('endpoint-charts.json.gz','endpoint_charts'),('seam-charts.json.gz','seam_charts')]:assert d['chart_summary']['outputs'][name]==h[key]
    assert d['banks']['pricing_sha256']==h['price'] and d['banks']['compressed_table_sha256']==h['bank_table']
    for path,expected in d['arithmetic_result']['source_sha256'].items():assert h[path]==expected
    audit=d['matching_audit'];assert audit['status']=='PASS_INDEPENDENT_BOUNDED_MATCHING_AUDIT' and audit['source_head']==c.HEAD
    assert audit['checker_sha256']==h['matching/audit_matching.py'] and audit['graph_sha256']==h['matching_graph']
    witness=audit['witnesses']['unrestricted'];assert witness['candidate_sha256']==h['word'] and witness['certificate_sha256']==h['matching_optimality']
    assert witness['retained_original_exact_pairs']==827 and witness['changed_pairs']==63 and all(audit['negative_controls'].values())
    second=d['second_moment'];assert second['checker_sha256']==h['arithmetic/check_second_moment.py']
    assert second['status']=='PASS_TWO_ROOTS_SECOND_EXACT_ENGINE' and len(second['cases'])==2
    for case in second['cases']:
        assert case['strict_signs'] and case['independent_engine_intervals_overlap']
        assert case['sha256']==h['baseline' if case['name']=='baseline-receipt' else 'price']
    assert d['path_delta']['candidate_sha256']==h['word']
    for name in ('price','baseline','arithmetic_result'):assert d[name]['head']==c.HEAD


def replay_chart(p):
    cols=p['basis_columns'];B=[[F(x)for x in row]for row in zip(*cols)];inv=[[F(x)for x in row]for row in p['inverse']]
    assert len(B)==20 and all(len(x)==20 for x in B)
    # A second factor replay, independent from the factor constructor.
    A=[row[:]for row in B];maxnum=maxden=1;det_multiplier=F(1)
    assert len(p['factors'])==p['count']<=400
    for kind,i,j,q in p['factors']:
        q=F(q);maxnum=max(maxnum,abs(q.numerator));maxden=max(maxden,q.denominator)
        if kind=='swap':A[i],A[j]=A[j],A[i];det_multiplier*=-1
        elif kind=='scale':A[i]=[x*q for x in A[i]];det_multiplier*=q
        elif kind=='add':A[i]=[x+q*y for x,y in zip(A[i],A[j])]
        else:raise AssertionError('unknown factor')
    assert A==[[F(i==j)for j in range(20)]for i in range(20)]
    assert F(p['determinant'])*det_multiplier==1
    assert all(abs(x.numerator)<2**80 and x.denominator<2**80 for row in inv for x in row)
    assert maxnum==p['max_numerator'] and maxden==p['max_denominator'] and max(maxnum,maxden)<2**80
    for L,R in((B,inv),(inv,B)):
        C=list(zip(*R));assert all(sum(x*y for x,y in zip(row,col))==int(i==j)for i,row in enumerate(L)for j,col in enumerate(C))
    return len(p['factors']),maxnum,maxden

def geometry(p,D,E):
    """Independent exact source-frame membership and split-projector identification."""
    import chart_rational as rat
    cols=[[F(x)for x in col]for col in p['basis_columns']]
    r=p['rank'];de=p['donor_dimension'];df=p['recipient_dimension']
    assert de==D['dim'] and df==(20 if E is None else E['dim']) and r==df-de>=0
    AD=D['a']if'a'in D else rat.nullspace(D['b'])
    AE=[]if E is None else E['a']if'a'in E else rat.nullspace(E['b'])
    residual=cols[:r];donor=cols[r:r+de];outside=cols[r+de:]
    assert len(outside)==20-df
    assert all(sum(x*y for x,y in zip(a,b))==0 for a in AD for b in donor)
    assert all(sum(x*y for x,y in zip(a,b))==0 for a in AE for b in residual+donor)
    def gram(a,b):return 9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)
    assert all(gram(a,b)==0 for a in residual for b in donor)
    assert all(gram(a,b)==0 for a in outside for b in residual+donor)
    # replay_chart separately verifies the full basis invertible, so these
    # ranks/membership/orthogonality equations identify the unique projector.


def verify_bank(raw,widths,r):
    table=gzip.decompress(raw);assert hashraw(table)==r['one_stage_table_uncompressed_sha256']
    rows=list(struct.iter_unpack('>IIIII',table));assert len(rows)==493380
    used=bytearray(9120*60);last=0;end=0
    for role,replica,bank,offset,width in rows:
        assert role in widths and 0<=replica<60 and widths[role]==width
        if bank!=last:assert bank==last+1 and end==100;last=bank;end=0
        assert offset==end and end+width<=100;end+=width
        key=role*60+replica;assert not used[key];used[key]=1
    assert end==100 and last+1==r['banks_per_stage']==85578
    assert sum(used)==len(widths)*60 and all(used[60*role+i]for role in widths for i in range(60))
    five=hashlib.sha256()
    for stage in range(5):
        for role,replica,b,offset,width in rows:five.update(struct.pack('>IIIIII',stage,role,replica,stage*85578+b,offset,width))
    assert five.hexdigest()==r['five_stage_assignment_sha256'] and r['total_assignments']==2466900
    assert r['literal_stock']==60*4*960+5*85578==658290


def helper_census(word,frames,seams):
    gauges={x['role']:x for x in word['gauges']};sources={r:int(n)for n,r in word['sources'].items()};reuse=dict(word['pairs']);removed=set(reuse.values());visits=defaultdict(list)
    ps=set(word['phase1']);order=word['phase1']+[i for i in range(len(word['ops']))if i not in ps]
    for i in order:
        for role in word['ops'][i][:2]:visits[role].append(word['op_frame'][i])
    for role,frame in zip(word['rootroles'],word['root_frame']):visits[role].append(frame)
    H=Counter();paid_seams={};requested={(x['donor'],x['recipient']):x for x in seams}
    for role in sorted(set(range(9120))-removed):
        initial=gauges[role]['frame']if role in gauges else word['source_frame'][sources[role]]if role in sources else None
        prev=0 if initial is None else frames[initial]['dim'];fs=list(visits[role]);seam_index=None
        if role in reuse:
            recipient=reuse[role];seam_index=len(fs);fs+=[gauges[recipient]['frame']]+visits[recipient]
        for index,frame in enumerate(fs+[word['full_frame']]):
            dim=frames[frame]['dim'];delta=dim-prev;assert delta>=0
            if delta:H[delta]+=1
            if index==seam_index and(role,reuse[role])in requested:
                row=requested[role,reuse[role]];assert delta==row['rank'] and frame==row['recipient_gauge_frame'] and fs[index-1]==row['donor_end_frame'];paid_seams[role,reuse[role]]=delta
            prev=dim
        if role in sources:H[1]+=1
    assert set(paid_seams)==set(requested)
    graph=c.source('bitword/selected/bit/graph_p10.json');chron=c.source('bitword/selected/bit/kchron_p10.json')
    for i,root in enumerate(graph['roots']):
        if root['kind']=='center':H[frames[word['root_frame'][i]]['dim']]+=1
    for row in chron['entries']:
        for k in ('carrier_chain','passive_chain'):
            for a,b in zip(row[k],row[k][1:]):
                delta=frames[b]['dim']-frames[a]['dim'];assert delta>=0
                if delta:H[delta]+=1
    target=[[]for _ in range(960)]
    for row in sorted(word['gauges'],key=lambda r:(r['first'],r['role'])):
        for t in row['targets']:target[t].append(row['frame'])
    deliveries=defaultdict(list)
    for row in chron['entries']:deliveries[row['deliver_after_root']].append(row)
    for i,root in enumerate(graph['roots']):
        if root['kind']=='side':
            for t in root['targets']:target[t].append(word['root_frame'][i])
        for row in deliveries[i]:
            for t in row['receivers']:target[t].append(row['deliver_frame'])
    for fs in target:
        ds=[0]+[frames[x]['dim']for x in fs]+[19]
        for a,b in zip(ds,ds[1:]):
            assert b>=a
            if b>a:H[b-a]+=1
    return H,Counter(paid_seams.values())


def run():
    c.verify();ps,raw,h,d=load_bundle();bindings(h,d)
    word,frames,roles,physical,entrance,ends,widths,origin=c.inventory();banks=d['banks'];price=d['price'];baseline=d['baseline'];transport=d['transport'];norm=d['norms'];targets=d['targets'];reorder=d['reorder']
    assert transport['kernel_entries_rebound']==1047 and transport['kernel_relations_and_cut_triples_exact'] and transport['kernel_entries_touching_changed_roles']==60
    assert transport['kernel_delta_old']==transport['kernel_delta_new'] and transport['complete_old_paths_checked']==transport['complete_new_paths_checked']==8230
    assert transport['preserved_pairs']==827 and all(not x for x in transport['direct_role_overlaps'].values())
    assert targets['all120_literal_target_relations']==120 and targets['all480_group_members_checked_at_close'] and targets['all_gauge_target_paths_nested'] and targets['negative_controls']
    assert targets['compressed_target_state_containment_checks']==5640
    assert targets['group119']['new_close']==328527<min(targets['new_late_gauge_records'].values())
    assert reorder['moves']==133 and reorder['moved_ports']==266 and reorder['all_anchors_survive'] and reorder['all_noncommuting_traces_equal']
    assert len(reorder['receipts'])==133 and all(r['all_anchor_candidates_semantically_preserved']and r['noncommuting_trace_and_relative_position_identical']for r in reorder['receipts'])
    assert norm['all_kernel_setup_and_restore_omission_controls_rejected'] and norm['setup_counts']=={'old':3188}
    for name in('baseline_forward','baseline_inverse','forward','inverse'):
        r=norm[name];assert r['all_columns']and r['columns']==10150 and r['weighted_additions']==336253 and r['literal_unit_additions']==338173
        assert sum(int(k)*v for k,v in r['coefficient_histogram'].items())==338173
    assert(norm['baseline_forward']['max_row_l1'],norm['baseline_inverse']['max_row_l1'])==(120183,1267036)
    forward=norm['forward']['max_row_l1'];inverse=norm['inverse']['max_row_l1'];payload=64*forward**3*inverse**2
    assert(forward,inverse)==(131967,1307800)and payload==norm['payload_bound']and payload.bit_length()==norm['payload_bits']==98 and payload<2**104
    # Replay each provided chart program and bind every endpoint use to the source inventory.
    endpoint=d['endpoint_charts'];seam=d['seam_charts'];maxima={}
    for name,receipt in(('endpoints',endpoint),('seams',seam)):
        got=[replay_chart(p)for p in receipt['factor_programs']];maxima[name]=[max(x[i]for x in got)for i in range(3)]
        assert maxima[name]==[receipt['max_factors'],receipt['max_numerator'],receipt['max_denominator']]
    assert maxima=={'endpoints':[136,7,12],'seams':[155,21,36]}
    endpoint_programs={p['program_id']:p for p in endpoint['factor_programs']};used=set()
    def gram(a,b):return 9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)
    for row in endpoint['role_uses']:
        role=row['role'];assert role not in used;used.add(role)
        assert row['physical']==physical[role]and row['rank']==widths[role]and row['origin']==origin[role]
        p=endpoint_programs[row['program_id']];assert p['rank']==widths[role]
        geometry(p,entrance[role],ends[role])
    assert used=={r for r in roles if entrance[r]is not None}and len(used)==2317
    assert endpoint['normalizer_bound']==599 and endpoint['retained_chart_bound']==400
    seam_programs={p['program_id']:p for p in seam['factor_programs']}
    for p in seam_programs.values():geometry(p,frames[p['donor_end_frame']],frames[p['recipient_gauge_frame']])
    for row in seam['role_uses']:
        p=seam_programs[row['program_id']]
        assert row['rank']==p['rank'] and row['donor_end_frame']==p['donor_end_frame'] and row['recipient_gauge_frame']==p['recipient_gauge_frame']
        assert row['physical_stream']==physical[row['donor']]==physical[row['recipient']]
    H,paid_seams=helper_census(word,frames,seam['role_uses'])
    assert clean(H)=={int(k):v for k,v in d['path_delta']['new_helper'].items()}
    assert dict(paid_seams)=={int(k):v for k,v in seam['rank_census'].items()}and paid_seams[0]==30 and sum(paid_seams.values())==63
    for stage in baseline['profile']['stages'].values():H.update({int(k):v for k,v in stage['delta'].items()})
    assert clean(H)=={int(k):v for k,v in price['final_helper_histogram'].items()}
    paid=Counter({k:5*v for k,v in H.items()if v});paid.update({r:1920 for r in(38,19,42,4)})
    assert clean(paid)=={int(k):v for k,v in price['banked_histogram'].items()}
    assert sum(paid.values())==250045 and sum(k*v for k,v in paid.items())==1095110
    assert Counter(widths.values())==Counter({int(k):v for k,v in price['residual_census'].items()})
    verify_bank(raw['bank_table'],widths,banks)
    assert F(price['assembly']['kappa'])==F(769997773182046,10**18)and price['assembly']['strict_constraint_count']==47
    # Source text is pinned and inspected only; never executed.
    finite=c.source('finite_check.py');bank=c.source('bank_check.py');proof=c.source('proof/FINITE_BIT_ACCOUNTING.md');cover=c.source('proof/three-stage-cover-bit.tex')
    assert 'coefficient=unit+J*high+J*(stock+h)+E*good+E*(128*N**3)+16*m**3+5*h*T+E+K+1'in finite
    assert 'factors=maxops+(m-1)+m;K=2*5*T*((plan.live_families-1)+len(context[\'regs\'])*m*factors)'in bank
    assert 'Per good edge, pay at most 8m^2+8 elementary'in proof and 'Allocate 128N^3 ring operations per edge per low class'in proof
    assert 'For a split idempotent $P$'in cover and 'of split rank $r$ relative to $I$'in cover
    baseline_bill=bill(658290,250195,336253,338173);invoice=bill(658290,250045,336253,338173)
    assert baseline_bill['coefficient']==c.source('word-pins.json')['finite_coefficient']==25485577221183401
    assert invoice['coefficient']==25476360501102401 and invoice['coefficient']<2**80 and invoice['coefficient_terms']['bank_selectors']<2**40
    assert invoice['fallback_generic_count']<invoice['fallback_per_child']
    positive=sum(v for k,v in paid_seams.items()if k);occurrences=positive*5*60
    assert occurrences==9900<=invoice['literal_paid_children']
    report=dict(status='PASS_RECEIPT_BOUND_UPDATED_HEAD_WEIGHTED890_FINITE_ARITHMETIC',head=c.HEAD,word_sha256=c.WORD_SHA,checker_sha256=c.sha(__file__),physical_admission=False,all_size_theorem=False,
        inputs={k:dict(path=str(ps[k]),sha256=h[k],bytes=len(raw[k]))for k in ps},source_dependencies=[dict(path=r['path'],local=str(c.INPUTS/r['local']),sha256=r['sha256'],git_blob=r['git_blob'],bytes=r['bytes'],url=r['url'])for r in c.manifest()['files']],
        direct_dependency_count=len(ps),source_dependency_count=len(c.manifest()['files']),admission=dict(kernel_entries=1047,affected_kernel_entries=60,paths=8230,targets=120,target_members=480,target_containment_checks=5640,semantic_reorders=133,raw_reorders_inherited=True),
        pricing=dict(kappa=price['assembly']['kappa'],kappa_decimal=price['assembly']['kappa_decimal'],baseline_kappa=baseline['assembly']['kappa'],banked_calls=250045,banked_rank_mass=1095110,stock=658290,banks_per_stage=85578,physical_R=8223,strict_constraints=47),
        endpoint_geometry=dict(programs=760,nontrivial_role_uses=2317,identity_role_uses=5906,max_factors=136,max_numerator=7,max_denominator=12,retained_chart_factor_bound=400,endpoint_normalizer_bound=599,canonical_basis_note='The full matching has 760 endpoint keys versus 759 in the baseline: new surviving gauge roles 9101/frame 14536 and 9103/frame 14539 replace roles 9118 and 9119 sharing frame 14583. All actual endpoint uses are freshly bound; residual widths are unchanged.'),
        bank_binding=dict(assignments_per_stage=493380,total_assignments=2466900,banks_per_stage=85578,stock=658290,independently_checked=True,all_blocks_full=True),
        scalar_payload=dict(forward=forward,inverse=inverse,bound=payload,bits=98,retained_cap_bits=104,columns=10150,final_compact_columns=10143,local_weighted=336253,local_units=338173),
        seam_cost_contract=dict(changed_seams=63,positive_rank_seams=33,zero_rank_seams=30,programs=47,max_chart_factors=155,max_numerator=21,max_denominator=36,rank_census=dict(sorted(paid_seams.items())),positive_occurrences_all_replicas_stages=occurrences,generic_wrapper_per_paid_child=80008,matrix_preparation_per_paid_child=1024000000,already_paid_wrapper_subset=occurrences*80008,already_paid_matrix_subset=occurrences*1024000000,incremental_surcharge=0,explanation='Every positive changed seam is a literal dimension-path child and is included in E. Generic split-projector wrapper and matrix preparation terms pay these children once. The400/599 endpoint-normalizer bound is separate. Rank-zero equal-frame seams add no recursive child; scalar/descriptors stay paid.'),
        finite_invoice=invoice,baseline_finite_invoice=baseline_bill,coefficient_delta=invoice['coefficient']-baseline_bill['coefficient'],coefficient_term_deltas={k:v-baseline_bill['coefficient_terms'][k]for k,v in invoice['coefficient_terms'].items()},
        remaining_conditions=['Complete final production raw-record/frame/hash regeneration is not performed. The fresh133 semantic anchor/noncommuting traces transport the inherited raw crossing proof.','All rational charts have exact inverse programs and factors below2^80. Prime supply must avoid their determinant/denominator factors; no blanket characteristic>5 assertion is made.','The inherited weighted compiler, common ancestor chart, row restoration, downstream address substitution, descriptor/precision/recovery, complex correctness and analytic interfaces remain hypotheses.','The displayed coefficient is the complete instantiated ring/recipe formula. C_full must also absorb inherited primitive, wrapper and prior ordinary-level constants; no numerical all-size cutoff or unconditional all-size theorem is claimed.'])
    for key,path in ps.items():assert c.sha(path)==h[key],('concurrent input changed',key)
    (c.OUTPUT/'finite-invoice-bound.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k]for k in('status','direct_dependency_count','source_dependency_count','pricing','endpoint_geometry','bank_binding','scalar_payload','coefficient_delta')},indent=2));return report
if __name__=='__main__':run()
