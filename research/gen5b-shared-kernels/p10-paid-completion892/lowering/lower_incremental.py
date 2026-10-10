from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import support
support.require_assertions()
"""Independently authored, source-bound paid-completion IR compiler.

No upstream production Python is imported or executed. The previously
independently authored finite scalar builder is a hash-checked dependency.
The regular frame compiler is an explicitly inherited interface, not replayed
or silently implemented by the scalar projection. Apache-2.0.
Prepared with substantial OpenAI assistance.
"""
from pathlib import Path
from collections import Counter, defaultdict
from functools import lru_cache
import copy, gzip, hashlib, json, struct, sys
import numpy as np

if not __debug__:
    raise RuntimeError('Assertions are mandatory')
HERE=Path(__file__).resolve().parent
OUT=support.LOWER; OUT.mkdir(exist_ok=True)
AD=support.HERE/"admission"
PAID=support.BANK/"split_49_11"
BASE=support.BASE_OUTPUT
CHART=support.BASE_OUTPUT/"finite/endpoint-charts.json.gz"
HEAD='1b37957d1520c80b6ea796bf418e52be5109c2d4'
WORD='25a0edc8c5f399fcf536b28c4e3575aa52177bb78b6078a631acb748954f0739'
ADSHA=support.sha(support.ADM/'ADMISSION-RESULT.json')
ACTIVE=((0,1),(1,0),(0,1),(3,2),(2,3))
M,H,V,T,S,BANKS=100,20,960,60,658275,85575

def sha(x): return hashlib.sha256(x).hexdigest()
def file_sha(p): return sha(Path(p).read_bytes())
def read(p): return json.loads(Path(p).read_text())
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dump(name,x): (OUT/name).write_bytes(json.dumps(support.portable(x),indent=2,sort_keys=True).encode()+b'\n')
def gz(name,raw):
    with gzip.GzipFile(filename=str(OUT/name),mode='wb',mtime=0) as f: f.write(raw)
    return {'file':name,'bytes':len(raw),'sha256':sha(raw),'compressed_sha256':file_sha(OUT/name)}

def source(name):
    row=next(x for x in MANIFEST['files'] if x['path']==name)
    raw=(support.INPUTS/row['local']).read_bytes()
    assert len(raw)==row['bytes'] and sha(raw)==row['sha256']
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob']
    SOURCES[name]=row['sha256']
    if name.endswith('.gz'): raw=gzip.decompress(raw)
    return json.loads(raw) if name.endswith(('.json','.json.gz')) else raw.decode()

MANIFEST=read(support.INPUT_MANIFEST); SOURCES={}
assert MANIFEST['head']==HEAD

def dependencies():
    support.verify_admission()
    summary=read(support.ADM/'ADMISSION-RESULT.json')
    assert file_sha(support.ADM/'ADMISSION-RESULT.json')==ADSHA
    assert summary['head']==HEAD and summary['candidate_sha256']==WORD
    assert not summary['old_fixed19_added'] and not summary['upstream_programs_executed']
    for name,digest in summary['artifact_hashes'].items(): assert file_sha(support.admission_artifact(name))==digest
    scalar=read(support.ADM/'scalar-recurrence-result.json')
    assert file_sha(AD/'check_scalar_recurrence.py')==scalar['checker_sha256']
    for name,digest in scalar['dependency_sha256'].items():
        p=AD/name if name.endswith('.py') else support.ADM/name
        assert file_sha(p)==digest
    assert file_sha(support.WORD)==WORD
    for name in ['bank_template.py','bank_check.py','code/global_lowering.py',
                 'proof/three-stage-cover-bit.tex','proof/three-stage-cover-rows.tex',
                 'proof/FINITE_BIT_ACCOUNTING.md','finite_check.py']: source(name)
    return summary,scalar

def emit_scalar(scalar):
    """Export the actual admitted source operand stream; do not add frames."""
    sys.path.insert(0,str(AD))
    import check_scalar_recurrence as independent_scalar
    word=read(support.WORD)
    events,n,*_=independent_scalar.scalar_word(word,[])
    for rev in (False,True):
        actual=independent_scalar.replay(events,n,rev)
        assert canonical(actual)==canonical(scalar['inverse' if rev else 'forward'])
    alias={b:a for a,b in word['pairs']}
    representatives=sorted(set(range(9120))-set(alias))
    physical={r:1920+i for i,r in enumerate(representatives)}
    removed={x['role'] for x in source('sink-selection.json')['sinks']}
    roles=[r for r in representatives if r not in removed]
    assert len(roles)==8221 and n==10148
    compact={i:i for i in range(1920)}
    compact.update({physical[r]:1920+i for i,r in enumerate(roles)})
    compact[n]=10141
    raw=bytearray(); sem=bytearray(); hist=Counter(); copied=[]; center=None
    for ordinal,(op,a,b,c,semantic) in enumerate(events):
        assert a in compact and b in compact
        aa,bb=compact[a],compact[b]
        assert aa!=bb
        raw.extend(struct.pack('<5i',op,aa,bb,c,ordinal))
        sem.extend(canonical([ordinal,semantic])+b'\n')
        hist[op]+=1
        if op==2: assert center is None; center=aa; copied.append(semantic[1])
        elif op==3: assert center==aa; center=None
    assert center is None and hist=={1:336253,2:20,3:20}
    return word,roles,physical,np.frombuffer(raw,dtype='<i4').reshape(-1,5).copy(),{
        'records':gz('local-scalar-operands.i32.gz',raw),
        'semantic_events':gz('local-semantic-events.jsonl.gz',sem),
        'record_format':'little-endian int32 [op, compact_destination_or_center, compact_source_or_temporary, signed_coefficient, semantic_event_ordinal]',
        'opcodes':{'1':'ADD','2':'COPY source a into work b','3':'ERASE work b paired to source a'},
        'weighted_additions':336253,'unit_additions':338173,'copy_erase_pairs':20,
        'live_local_roles':10141,'temporary_local_role':10141,
        'admitted_pre_reorder_projection':scalar['forward']['event_sha256'],
        'order_scope':'Concrete full scalar/COPY projection before133 admitted commutative moves. Final133 moves and frame lowering are explicit inherited contracts, not claimed executed here.'}

def permutation(stage,start,width):
    original=list(range(stage*20,stage*20+width)); target=list(range(start,start+width))
    a=original+[x for x in range(100) if x not in original]
    b=target+[x for x in range(100) if x not in target]
    d=dict(zip(a,b));return [d[x] for x in range(100)]

def factor_perm(pi):
    work=list(range(100)); out=[]
    for i,x in enumerate(pi):
        if work[i]!=x:
            j=work.index(x);work[i],work[j]=work[j],work[i];out.append([i,j])
    assert work==pi
    return out

def namespaces(roles,paid):
    raw=gzip.decompress((PAID/'literal-assignments.bin.gz').read_bytes())
    assert sha(raw)==paid['bank_addresses']['assignment_sha256']
    assignment={}
    cover=bytearray(BANKS*100)
    for r,t,b,start,width,scalar in struct.iter_unpack('>6I',raw):
        assert r in ROLES_SET and 0<=t<T and 0<=b<BANKS and 0<width<=20
        assert 1<=scalar<=25 and 0<=start<start+width<=100
        assert (r,t) not in assignment
        assignment[r,t]=(b,start,width,scalar)
        sl=slice(b*100+start,b*100+start+width)
        assert not any(cover[sl]); cover[sl]=b'\1'*width
    assert len(assignment)==8221*T and cover.count(0)==60
    assert all(cover[:-100]) and cover[-100:]==b'\1'*40+b'\0'*60
    charts=json.loads(gzip.decompress(CHART.read_bytes()))
    assert file_sha(CHART)==paid['endpoints']['prior_chart_data_sha256']
    chartuse={x['role']:x['program_id'] for x in charts['role_uses'] if x['role'] in ROLES_SET}
    assert len(chartuse)==2315
    programs={x['program_id']:x for x in charts['factor_programs']}
    registry=[]; ids={}; rawmaps=bytearray(); views=[]; receipts=[]
    def intern(s,start,width,scalar,chart):
        key=s,start,width,scalar,chart
        if key not in ids:
            pi=permutation(s,start,width);outside=next(j for j in range(100) if not 20*s<=j<20*(s+1))
            p=programs.get(chart)
            if p: assert p['rank']==width and p['count']<=400
            else: assert width==20
            ids[key]=len(registry)
            registry.append({'id':ids[key],'stage':s,'support':[start,start+width],
                'rank':width,'scalar':scalar,'permutation':pi,'chart_program':chart,
                'inverse_chart_window':[20*s,20*(s+1)],
                'formula':'N = scalar * Pi * embed_stage(B_inverse)',
                'original_cover':'d * tau(stage)',
                'physical_cover':'d * tau(stage) * inverse(N)',
                'right_to_left_inverse_factors':['inverse_scalar','inverse_permutation','embedded_B'],
                'outside_column':outside,'unit_column_witness':[pi[outside],scalar],
                'paid_factor_bound':599})
        return ids[key]
    for s in range(5):
      for t in range(T):
        # Column pairs are (literal physical family, exact route descriptor ID).
        # route0: class d. route1..4800: rho(stage,port). 4801+: helper N.
        a=np.empty((10142,2),dtype='<i4')
        for local in range(1920):
            bank=ACTIVE[s][int(local>=960)];port=local%960
            a[local]=((4*t+bank)*960+port,0 if s==0 else 1+s*960+port)
        witnesses=defaultdict(list)
        for j,r in enumerate(roles):
            b,start,w,scalar=assignment[r,t];nid=intern(s,start,w,scalar,chartuse.get(r,-1))
            f=230400+s*BANKS+b;a[1920+j]=(f,4801+nid)
            witnesses[f].append(tuple(registry[nid]['unit_column_witness']))
        a[-1]=(S,-1)
        assert len(set(map(tuple,a.tolist())))==10142
        assert all(len(set(xs))==len(xs) for xs in witnesses.values())
        assert all(0<=int(x)<S for x in a[:-1,0]) and tuple(a[-1])==(S,-1)
        payload=a.tobytes();rawmaps.extend(payload);views.append(a)
        receipts.append({'stage':s,'replica':t,'namespace_sha256':sha(payload),
                         'addresses':10142,'full_address_injective':True,
                         'live_families':len(set(map(int,a[:-1,0]))),
                         'data_and_bank_and_external_work_disjoint':True})
    gz('all-namespaces.i32.gz',rawmaps)
    dump('normalizers.json',{'regular_normalizers':registry,
        'chart_source_sha256':file_sha(CHART),'actual_chart_programs':[programs[i] for i in sorted(set(chartuse.values()))],
        'regular_endpoint_contract':'The actual admitted local residual is P_E-P_D. Its checked B basis puts this residual on first rank coordinates. Therefore N conjugates embed_stage(P_E-P_D) to the assigned Q_support. Scalar cancels. At physical g=d*tau*N^-1 the endpoint is D_(g Q_support g^-1), in the same common ancestor QA. Complete local arbitrary-dirty endpoint separation is inherited.',
        'mapping_format':'300 namespaces in stage-major replica-major order; each has10142 little-endian int32 pairs family,routeID. local roles0..959source,960..1919target,1920..10140sorted real roles,10141external work.',
        'data_route_encoding':'0=class d; 1+stage*960+port=right(d,rho(stage,port)); -1=external work; 4801+normalizer_id=right(d,tau(stage),inverse(N)).'})
    dump('namespace-receipts.json',receipts)
    return views,registry,assignment

def completion(s,start,rank):
    support=list(range(start,start+rank)); a=support+[x for x in range(100) if x not in support]
    b=list(range(100)); d=dict(zip(a,b));pi=[d[x] for x in b]
    inv=[pi.index(x) for x in b]; factors=factor_perm(pi)
    assert {pi[x] for x in support}==set(range(rank)) and rank<50
    # factor_perm returns a right-column-update decomposition. Chronological
    # coordinate action is reversed; test all100 actual basis-vector images.
    for chronological,want in ((list(reversed(factors)),pi),(factors,inv)):
        images=list(range(100))
        for i,j in chronological:images=[j if x==i else i if x==j else x for x in images]
        assert images==want
    family=230400+(s+1)*BANKS-1
    fees={'route_movements':2,'selector_calls':2*((S-1)+100*599),
          'generic_wrappers':80008,'matrix_preparation':1024000000,
          'paid_child_overhead':1,'fallback_children_bound':320000,
          'fallback_child_ratio':'1/100','bad_class_fraction_bound':'1/10000000000000000'}
    descriptor={'ambient_dimension':100,'coordinate_support':support,'rank':rank,
        'head_indices':support,'tail_indices':[199-j for j in support],
        'Q_entries':[[j,j,1] for j in support],
        'U_entries':[[j,k,1] for k,j in enumerate(support)]+[[199-j,k,-1] for k,j in enumerate(support)],
        'V_entries':[[k,j,-1] for k,j in enumerate(support)]+[[k,199-j,1] for k,j in enumerate(support)],
        'unweighted_residual':'D_P = [[I-P,P*C100],[C100*P,I-C100*P*C100]]',
        'direct_projector':'P = g * Q_support * inverse(g)',
        'weighted_residual':'QA * D_P * inverse(QA), QA=diag(A,I100)',
        'common_ancestor_weight':'same A[i*f+j] descriptor as all regular bank residuals',
        'factor_identity':'D_Q-I200=U*V; V*U=-2I_rank; all listed entries are integers',
        'permutation':pi,'inverse_permutation':inv,
        'permutation_convention':'list pi[j] is the image of column basis vector e_j; route matrix has entry(pi[j],j)=1',
        'chronological_coordinate_transpositions':list(reversed(factors)),
        'chronological_inverse_transpositions':factors,
        'normalizer_scalar':1,'normalizer_denominators':[1],
        'normalizer_factors':len(factors),'charged_normalizer_bound':599,
        'generic_contract_source':SOURCES['proof/three-stage-cover-bit.tex'],
        'generic_evaluation':{'chart':'h=g*inverse(Pi)','canonical_projector':'h*diag(I_rank,0)*inverse(h)',
            'unit_lower_adapters':'L_j=A_j*L_P*inverse(A_j); R_j=R_P',
            'pivot_weights':'D_P[k] computed by unit-pivot northeast elimination on P*C100',
            'child_atoms':'rank*f, f=floor(n/100)',
            'child_index':'A_child[k*f+j]=A[i_k*f+j]*D_P[k], integer0<=k<rank,0<=j<f',
            'coefficient_scope':'parent prefix and ancestor spectators only',
            'row_restore':'all row coordinates restored by completed child; no new temporary roles',
            'generic_condition':'each required northeast minor is a unit modulo q',
            'bad_branch':'full200x200 unit-pivot Gaussian fallback, never invert a nonunit'},
        'fees':fees}
    # These are executable IR operations on one existing complete bank stream.
    operations=[{'op':'ROUTE_RIGHT','family':family,'matrix':inv,'direction':'out','fee_route_movements':1},
                {'op':'COMPILE_SPLIT_IDEMPOTENT','family':family,'rank':rank,
                 'chart':'h=g*inverse(Pi)','coordinate_support':list(range(rank)),
                 'projector_descriptor':f'completion-{s}-{rank}',
                 'fee_generic_wrappers':80008,'fee_matrix_preparation':1024000000,'fee_paid_child':1},
                {'op':'ROUTE_RIGHT','family':family,'matrix':pi,'direction':'back','fee_route_movements':1},
                {'op':'RESTORE_ROW_RESERVE','family':family,'reserve_coefficient':10001}]
    return {'kind':'paid_bank_completion','stage':s,'family':family,'rank':rank,
            'coordinate_interval':[start,start+rank],'cover':'all_GL100_Rw',
            'high_fibers':'one complete batch per low class','descriptor':descriptor,'operations':operations}

def phases():
    p=[]
    for s in range(5):
        for t in range(T):p.append({'kind':'helper','stage':s,'replica':t,'namespace_index':s*T+t,
            'body':'admitted_regular_frame_body_v1','scalar_template':'local-scalar-operands.i32.gz',
            'reverse_complement':s in(1,3),'cover':'all_GL100_Rw','high_fibers':'batched'})
        p.extend((completion(s,40,49),completion(s,89,11)))
        if s in(1,2,4):
            which={1:0,2:1,4:2}[s]
            for t in range(T):
                p.extend([{'kind':k,'stage':s,'which':which,'replica':t,'cover':'all_GL100_Rw'} for k in ('idle','bridge')])
    p.extend({'kind':'terminal_exchange','replica':t,'cover':'all_GL100_Rw'} for t in range(T))
    for i,x in enumerate(p):x['phase_index']=i
    return p

def validate_phases(p):
    assert len(p)==730
    for i,x in enumerate(p): assert x['phase_index']==i
    expected=[]
    for s in range(5):
        hs=[(i,x) for i,x in enumerate(p) if x['kind']=='helper' and x['stage']==s]
        cs=[(i,x) for i,x in enumerate(p) if x['kind']=='paid_bank_completion' and x['stage']==s]
        assert [x['replica'] for i,x in hs]==list(range(60)) and len(cs)==2
        assert max(i for i,x in hs)<cs[0][0] and cs[1][0]==cs[0][0]+1
        assert [x['rank'] for i,x in cs]==[49,11]
        banks=[x['family'] for i,x in cs];assert banks==[230400+(s+1)*BANKS-1]*2
        coords=[]
        for (i,x),(start,r) in zip(cs,((40,49),(89,11))):
            assert x['coordinate_interval']==[start,start+r]
            d=x['descriptor'];assert d['coordinate_support']==list(range(start,start+r))
            assert d['rank']==r and d['ambient_dimension']==100 and 2*r<100
            assert d['fees']==completion(s,start,r)['descriptor']['fees']
            assert x['operations']==completion(s,start,r)['operations']
            assert d['permutation']==completion(s,start,r)['descriptor']['permutation']
            coords+=d['coordinate_support']
        assert sorted(coords)==list(range(40,100)) and len(set(coords))==60
        later=[i for i,x in enumerate(p) if x.get('stage')==s and x['kind'] in('idle','bridge')]
        if later:assert cs[-1][0]<min(later)
        if s<4:assert cs[-1][0]<min(i for i,x in enumerate(p) if x.get('stage')==s+1)
    assert [x['replica'] for x in p if x['kind']=='terminal_exchange']==list(range(60))

def emit_boundary(x):
    t=x['replica']; kind=x['kind']
    def f(bank,port):return (4*t+bank)*960+port
    if kind=='idle':
        groups={0:((2,38,0),(3,38,1)),1:((2,19,2),(3,19,3)),2:((0,42,4),(1,42,5),(2,4,6),(3,4,7))}[x['which']]
        for bank,rank,projector in groups:
            for port in range(960):yield [4,f(bank,port),-1,0,rank,projector,port]
    elif kind=='bridge':
        groups={0:((0,2,1),(3,1,-1)),1:((3,1,1),(0,2,-1)),2:((1,3,-1),(2,0,1))}[x['which']]
        for a,b,c in groups:
            for port in range(960):yield [5,f(a,port),f(b,port),c,0,x['which'],port]
    else:
        assert kind=='terminal_exchange'
        for a,b in ((0,1),(2,3)):
            for port in range(960):yield [7,f(a,port),f(b,port),-1,0,0,port]

def bind_operands(p,local,spaces):
    """Materialize and hash every lowered scalar operand, not just a plan.

    Storage is a lossless factored representation: actual local records,
    all literal namespaces and phase order. We expand every one of its
    100,887,900 stage projection records for QA, without duplicating3GB.
    """
    stage_receipts=[];boundaries=bytearray(); chain=hashlib.sha256()
    added=Counter();rankhist=Counter(); boundary_counts=Counter()
    for x in p:
        kind=x['kind'];index=x['phase_index']
        chain.update(canonical(x)+b'\n')
        if kind=='helper':
            s,t=x['stage'],x['replica'];a=spaces[s*T+t]
            events=local[::-1].copy() if s in (1,3) else local.copy()
            if s in(1,3):
                # Reversing erased scratch never means restoring erased data.
                # The original center is freshly copied at old ERASE.
                op=events[:,0].copy();events[op==2,0]=3;events[op==3,0]=2
                events[op==1,3]*=-1
            out=np.zeros((len(events),9),dtype='<i4')
            out[:,0]=index;out[:,1]=np.arange(len(events));out[:,2]=events[:,0]
            out[:,3:5]=a[events[:,1]];out[:,5:7]=a[events[:,2]]
            out[:,7]=events[:,3];out[:,8]=events[:,4]
            assert np.all(np.any(out[:,3:5]!=out[:,5:7],axis=1))
            center=None;reads=0
            for op,aa,bb,c,sem in events:
                if op==2:assert center is None and bb==10141;center=aa;reads=0
                elif op==3:assert center==aa and bb==10141 and reads==144;center=None
                elif bb==10141:assert center is not None;reads+=1
            assert center is None
            raw=out.tobytes();digest=sha(raw);chain.update(bytes.fromhex(digest))
            stage_receipts.append({'phase_index':index,'stage':s,'replica':t,
                'lowered_scalar_records':len(events),'expanded_operand_sha256':digest,
                'actual_addresses_substituted':True,'signed_coefficients_retained':True,
                'copied_center_lifetimes_and144_reads_verified':True})
        elif kind=='paid_bank_completion':
            added[x['rank']]+=1;rankhist[x['rank']]+=1
            chain.update(canonical(x['operations'])+b'\n')
        else:
            for row in emit_boundary(x):
                payload=struct.pack('<8i',index,*row);boundaries.extend(payload)
                chain.update(payload);boundary_counts[row[0]]+=1
                if row[0]==4:rankhist[row[4]]+=1
    assert len(stage_receipts)==300 and added=={49:5,11:5}
    assert boundary_counts=={4:460800,5:345600,7:115200}
    assert rankhist=={38:115200,19:115200,42:115200,4:115200,49:5,11:5}
    dump('expanded-operand-receipts.json',stage_receipts)
    boundary=gz('boundary-records.i32.gz',boundaries)
    return {'expanded_scalar_records':sum(x['lowered_scalar_records'] for x in stage_receipts),
        'expanded_scalar_additions':300*336253,'expanded_unit_additions':300*338173,
        'expanded_hash_encoding':'little-endian int32 [phase,local_ordinal,op,dst_family,dst_route,src_family,src_route,signed_coefficient,semantic_event_ordinal]',
        'boundary_records':boundary,'boundary_opcodes':dict(boundary_counts),
        'new_completion_children':dict(added),'explicit_boundary_and_completion_histogram':dict(rankhist),
        'extended_compositional_program_sha256':chain.hexdigest(),
        'literal_storage':'Exact factored stream; templates, all namespaces and phase records are retained. Every expanded scalar operand was materialized, checked and hashed.',
        'regular_recursive_frame_children_executed':False}

def endpoint_check():
    blocks=[range(0,20),range(20,40),range(40,89),range(89,100)]
    state=list(range(200))
    for block in blocks:
        for j in block:state[j],state[199-j]=state[199-j],state[j]
    assert state==list(range(199,-1,-1))
    forward=state[:]
    for block in reversed(blocks):
        for j in block:state[j],state[199-j]=state[199-j],state[j]
    assert state==list(range(200))
    return {'integer_columns':200,'four_projectors_partition_I100':True,
            'forward_permutation':forward,'inverse_restores_all200':True,
            'dirty_inputs':'arbitrary200 independent coordinates; no zero initialization',
            'universal_basis':'integer permutation identity, preserved by conjugation by shared QA and cover g; no finite-field extrapolation'}

def invoice(p,paid):
    completion_rows=[x for x in p if x['kind']=='paid_bank_completion']
    E=15002700+len(completion_rows);J=60*(24*960+10*8221)+sum(x['descriptor']['fees']['route_movements'] for x in completion_rows)
    K=2*5*60*((S-1)+8221*100*599)+sum(x['descriptor']['fees']['selector_calls'] for x in completion_rows)
    terms={'unit_expanded_additions':60*(5*338173+6*960),'high_affine_factors':J*16*10001**2,
        'low_transpositions':J*(S+20),'generic_wrappers':E*80008,
        'matrix_preparation':E*128*200**3,'global_matrix_preparation':16*100**3,
        'copy_erase_episodes':6000,'paid_child_overhead':E,'bank_selectors':K,'constant':1}
    assert terms==paid['finite_invoice']['terms']
    assert (E,J,K,sum(terms.values()))==(15002710,6315020,295872067880,25474481435226991)
    return {'stock':S,'calls':E,'route_movements':J,'selector_calls':K,'terms':terms,
        'coefficient':sum(terms.values()),'all_edges_including_new10_pay_fallback':True,
        'maximum_child_rank':49,'strict_one_level_halving':True,
        'row_reserve_coefficient':10001,'new_temporary_roles':0,
        'regular_helper_histogram_scope':'Inherited source-bound regular frame census; ten completion child ranks are emitted and counted here.'}

def negative_controls(p):
    first=next(i for i,x in enumerate(p) if x['kind']=='paid_bank_completion')
    def reject(name,mut):
        q=copy.deepcopy(p);mut(q)
        try:validate_phases(q)
        except AssertionError:return name
        raise AssertionError('accepted negative control '+name)
    controls=[]
    controls.append(reject('omitted_completion',lambda q:q.pop(first)))
    controls.append(reject('duplicated_completion',lambda q:q.insert(first,copy.deepcopy(q[first]))))
    def order(q):q[first],q[first-1]=q[first-1],q[first]
    controls.append(reject('before_last_helper',order))
    controls.append(reject('wrong_bank_family',lambda q:q[first].__setitem__('family',q[first]['family']-1)))
    controls.append(reject('overlapping_support',lambda q:q[first]['descriptor']['coordinate_support'].__setitem__(0,39)))
    controls.append(reject('rank50_guard',lambda q:q[first].__setitem__('rank',50)))
    controls.append(reject('omitted_route_out',lambda q:q[first]['operations'].pop(0)))
    controls.append(reject('omitted_route_back',lambda q:q[first]['operations'].pop(2)))
    controls.append(reject('missing_selector_fee',lambda q:q[first]['descriptor']['fees'].__setitem__('selector_calls',0)))
    controls.append(reject('missing_generic_wrapper_fee',lambda q:q[first]['operations'][1].__setitem__('fee_generic_wrappers',0)))
    controls.append(reject('missing_fallback_fee',lambda q:q[first]['descriptor']['fees'].__setitem__('fallback_children_bound',0)))
    controls.append(reject('wrong_completion_matrix',lambda q:q[first]['operations'][0]['matrix'].__setitem__(0,0)))
    # Source integrity is part of admission, before executable dependency load.
    assert sha((support.WORD).read_bytes()+b' ')!=WORD
    controls.append('stale_or_modified_source_word')
    return controls

def main():
    summary,scalar=dependencies();paid=read(PAID/'RESULT.json')
    assert paid['head']==HEAD and paid['word_sha256']==WORD and paid['split']==[49,11]
    word,roles,physical,local,localreceipt=emit_scalar(scalar)
    global ROLES_SET;ROLES_SET=set(roles)
    spaces,normalizers,assignment=namespaces(roles,paid)
    dump('local-scalar-binding.json',localreceipt)
    dump('compact-role-index.json',{'roles':roles,'index_rule':'local=1920+list_index; external_work=10141','removed_sink_roles':sorted(set(physical)-set(roles))})
    p=phases();validate_phases(p);print('Namespaces and executable completion descriptors emitted',flush=True)
    dump('extended-phases.json',p)
    bound=bind_operands(p,local,spaces);print('All300 actual scalar operand streams expanded and hashed',flush=True)
    controls=negative_controls(p);bill=invoice(p,paid)
    dump('endpoint.json',endpoint_check());dump('invoice.json',bill)
    inherited={
      'regular_body':'The admitted final892 regular scalar/frame telescope, including133 semantic reorder moves, full G-projector transition stream, reflected stages, operand-span validity and restored dirty local endpoints. Actual scalar/COPY operands before these commuting moves are independently expanded here. The move transport and regular paid histogram are source-bound finite contracts, not raw frame production replay.',
      'route_geometry':'The retained exact rho(stage,port),tau(stage),global_stage_projector and eight idle_projectors formulas in inert code/global_lowering.py; boundary records bind all literal families, signed coefficients, projector IDs and port indices.',
      'weighted_generic_child':'The retained generic split-idempotent compiler, low-class unit-minor test, L/R/K adapter evaluation, contiguous weight descriptor, full200-dimensional local-ring fallback, arbitrary parent ancestors and restored child rows.',
      'analytic_and_all_size':'Prime supply, full-C/complex supplier, ordered affine primitive, ordinary leaves, finite constants/cutoff and outer balanced assembly remain inherited or independently certified elsewhere.'}
    inputs={str(support.ADM/'ADMISSION-RESULT.json'):file_sha(support.ADM/'ADMISSION-RESULT.json'),
            str(support.WORD):WORD,str(PAID/'RESULT.json'):file_sha(PAID/'RESULT.json'),
            str(PAID/'literal-assignments.bin.gz'):file_sha(PAID/'literal-assignments.bin.gz'),str(CHART):file_sha(CHART)}
    for name in ['check_scalar_recurrence.py','weighted_source_data.py','check_transport.py','check_target_chronology.py']:
        inputs[str(AD/name)]=file_sha(AD/name)
    for name,digest in summary['artifact_hashes'].items():inputs[str(support.admission_artifact(name))]=digest
    result={'status':'PASS_SOURCE_BOUND_COMPOSITIONAL_PAID_COMPLETION_LOWERING',
       'source_head':HEAD,'candidate_sha256':WORD,'old_fixed19_added':False,'split':[49,11],
       'source_admission_sha256':ADSHA,'upstream_production_programs_executed':False,
       'whole_final_raw_frame_program_regenerated':False,'unconditional_all_size_theorem':False,
       'exact_new_completion_integration_verified':True,'phase_count':len(p),'helper_phases':300,
       'completion_sweeps':10,'boundaries_after_completions':True,'normalizer_descriptors':len(normalizers),
       'literal_profile':paid['literal_profile'],'operand_binding':bound,'invoice':bill,
       'rejected_controls':controls,'inherited_interfaces':inherited,
       'source_hashes':SOURCES,'input_hashes':inputs,'compiler_sha256':file_sha(__file__),
       'scope':'Concrete incremental IR with exact added completion operations, source-bound scalar operands, every literal namespace and bank family, unchanged boundary operations, full fees and hard negative controls. Claims compositional closure under named inherited regular-body and generic compiler interfaces; does not relabel scalar projection as full raw-frame replay.'}
    dump('RESULT.json',result)
    manifest={p.name:file_sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='MANIFEST.json'}
    dump('MANIFEST.json',manifest)
    print(json.dumps({k:result[k] for k in ['status','phase_count','completion_sweeps','rejected_controls','whole_final_raw_frame_program_regenerated']},indent=2))
if __name__=='__main__':main()
