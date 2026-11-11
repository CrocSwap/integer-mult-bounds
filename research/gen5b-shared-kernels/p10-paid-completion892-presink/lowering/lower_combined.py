from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import companion as packet
packet.require_assertions()
packet.verify_base()
packet.verify_sources()
"""Source-bound global IR for the isolated PR322+323 paid892 composition.

Consumes only independently admitted inert records and hash-bound selections.
Does not execute upstream production code or edit the fixed paid892 packet.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction as F
import gzip,hashlib,json,struct,copy,os
import numpy as np
assert packet.sha(packet.HERE/'lowering/retained_ir_helpers.py') == 'c6b2bd1d0419360b2c2bf0dc039bbe8a461915c6918e25eba19cd095aedf8bc5'
from retained_ir_helpers import stage_template,permutation,factor_perm,emit_boundary
if not __debug__:raise RuntimeError('Assertions required')
HERE=Path(__file__).resolve().parent
OUT=packet.LOWERING
LOCAL=packet.ADMISSION
PROPOSAL=packet.EXPERIMENT
OLD=packet.BASE_OUTPUT
OLDLOCAL=packet.BASE_FRAME
CHART=packet.BASE_OUTPUT/"baseline/finite/endpoint-charts.json.gz"
WORD='25a0edc8c5f399fcf536b28c4e3575aa52177bb78b6078a631acb748954f0739'
HEADS={'PR320':'1b37957d1520c80b6ea796bf418e52be5109c2d4',
       'PR322':'8ce22e5e487e9d1017c26702adc09d5646565d0c',
       'PR323':'e51f5ffee8ab574e5b8249a4612411b2ca5f100d'}
SELECTORS={'pr322-presink-selection.json':'166fa4ce7259d35a020c51682c6f18256f3fdad260473f8209e53114285c8934',
           'pr323-kernel2-selection.json':'bcfdc7ec8a61d49201961077fbc512f516dcbebac4281d5cd7d2350ced3ee9e0'}
S=658255;BANKS=85571;ROLES=8221;WORK=10141
ACTIVE=((0,1),(1,0),(0,1),(3,2),(2,3))
sha=lambda b:hashlib.sha256(b).hexdigest()
def fs(p):return sha(Path(p).read_bytes())
def read(p):
    p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b) if p.name.endswith('.gz') else b)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dump(name,x):
    raw=canonical(packet.portable(x))+b'\n';(OUT/name).write_bytes(gzip.compress(raw,mtime=0) if name.endswith('.gz') else raw)
def gz(name,raw):
    (OUT/name).write_bytes(gzip.compress(raw,mtime=0));return {'file':name,'sha256':sha(raw),'compressed_sha256':fs(OUT/name),'bytes':len(raw)}
def read_bound_inputs():
    for name,h in SELECTORS.items():assert fs(packet.INPUTS/name)==h
    proposal=read(PROPOSAL/'RESULT.json');bank=read(PROPOSAL/'BANK-RESULT.json')
    frozen=packet.verify_experiment()
    for name,h in frozen['artifacts'].items():assert fs(PROPOSAL/name)==h
    assert proposal['source_word_sha256']==WORD and proposal['source_heads']=={k:v for k,v in HEADS.items() if k!='PR320'}
    assert bank['composition_result_sha256']==fs(PROPOSAL/'RESULT.json')
    prior=read(packet.BASE_LOWER/'RESULT.json')
    assert fs(CHART)==prior['input_hashes']['$OUTPUT/baseline/finite/endpoint-charts.json.gz']
    packet.verify_base()
    local=read(LOCAL/'RESULT.json')
    assert local['status']=='PASS_PR322_PR323_COMPOSED_FULL_LOCAL_FRAME_WORD'
    assert local['candidate_sha256']==WORD and local['source_heads']==proposal['source_heads']
    assert local['base_frame_result_sha256']==fs(OLDLOCAL/'RESULT.json')
    assert (local['retimings'],local['new_kernels'],local['moves'],local['source_descent_entries'])==(4,3,133,480)
    for key in ('all133_actual_anchors_rechecked','all20_selected_physical_ports_rebound',
                'all_integer_operand_source_spans_contained','all_new_kernel_helper_integer_sources_restored',
                'independent_experiment_event_and_endpoint_agreement'):assert local[key]
    assert local['forward']['max_row_l1']==132195 and local['inverse']['max_row_l1']==1307808
    assert fs(packet.SOURCE_PROVENANCE)==local['source_provenance_sha256']
    # Local source admission must be complete before any global PASS is emitted.
    assert fs(packet.HERE/'admission/build_local.py')==local['checker_sha256']
    for name,h in local['artifacts'].items():assert fs(LOCAL/name)==h
    records=read(LOCAL/'local-records.json.gz');frames=read(LOCAL/'local-frames.json.gz');ep=read(LOCAL/'local-endpoints.json')
    roots={'base_word':WORD,'source_heads':HEADS,'selectors':SELECTORS,
           'prior_local_frame_result':fs(OLDLOCAL/'RESULT.json'),
           'prior_global_frame_result':fs(packet.BASE_FULL/'RESULT.json'),
           'retained_endpoint_chart_programs':fs(CHART),
           'current_local_record_bytes':fs(LOCAL/'local-records.json.gz')}
    return proposal,bank,local,records,frames,ep,roots

def verify_local(records,frames,ep):
    state={int(k):v for k,v in ep['initial'].items()};final={int(k):v for k,v in ep['final'].items()}
    assert set(state)==set(final)==set(range(WORK))
    rank=lambda f:frames[str(f)]['rank'];H=Counter();ops=Counter();coeff=Counter();tmp=None;reads=0
    for row in records:
        op,a,b,c,f,z=row;ops[op]+=1
        if op==0:
            assert state[a]==b and rank(c)-rank(b)==f and f>=0;state[a]=c
            if f:H[f]+=1
        elif op==1:
            assert a!=b and state[a]==state[b]==f and c%2;coeff[abs(c)]+=1
            if b==WORK:assert tmp is not None;reads+=1
        elif op==2:
            assert tmp is None and b==WORK and state[a]==c and rank(c)==z==18 and rank(f)==0
            tmp=(a,b,c,f);state[b]=f;H[z]+=1;reads=0
        else:
            assert op==3 and tmp==(a,b,c,f) and state[a]==c and state[b]==f and reads==144
            del state[b];tmp=None
    assert state==final and tmp is None and (ops[1],ops[2],ops[3])==(336239,20,20)
    assert coeff=={1:335279,3:960} and (sum(H.values()),sum(r*n for r,n in H.items()))==(48486,179458)
    return H,ops

def exact_endpoint_charts(roles,frames,ep,bank):
    old=read(CHART);programs={x['program_id']:x for x in old['factor_programs']}
    uses={x['role']:x['program_id'] for x in old['role_uses'] if x['role'] in set(roles)}
    for j,new in enumerate(bank['changed_endpoint_charts']):
        role=new['virtual_role'];assert roles[new['compact_pivot']-1920]==role and role not in uses
        pid=100000+j;uses[role]=pid
        programs[pid]={'program_id':pid,'rank':18,'donor_dimension':2,'recipient_dimension':20,
            'basis_columns':new['basis_columns'],'inverse':new['inverse'],
            'factors':new['factor_program'],'count':new['factor_count']}
        p=programs[pid];B=[list(map(F,row)) for row in zip(*p['basis_columns'])];I=[list(map(F,row)) for row in p['inverse']]
        for a,b in ((B,I),(I,B)):
            assert all(sum(x*y for x,y in zip(row,col))==int(i==j) for i,row in enumerate(a) for j,col in enumerate(zip(*b)))
        work=copy.deepcopy(B)
        for op,i,j,c in p['factors']:
            if op=='swap':work[i],work[j]=work[j],work[i]
            elif op=='scale':work[i]=[F(c)*x for x in work[i]]
            else:assert op=='add';work[i]=[x+F(c)*y for x,y in zip(work[i],work[j])]
        assert work==[[int(i==j) for j in range(20)] for i in range(20)]
        assert p['count']==21
    assert len(uses)==2318
    widths={};checked=set();chart_receipts=[]
    gram=lambda a,b:9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)
    for i,r in enumerate(roles):
        before=ep['initial'][str(1920+i)];after=ep['final'][str(1920+i)]
        A=frames[str(before)];B=frames[str(after)];widths[r]=B['rank']-A['rank']
        if r not in uses:assert (A['rank'],B['rank'])==(0,20);continue
        p=programs[uses[r]];w=widths[r]
        assert (p['donor_dimension'],p['recipient_dimension'],p['rank'])==(A['rank'],B['rank'],w)
        key=uses[r],before,after
        if key not in checked:
            cols=[list(map(F,row)) for row in p['basis_columns']];Ao=[list(map(F,row)) for row in A['annihilator']];An=[list(map(F,row)) for row in B['annihilator']]
            residual=cols[:w];src=cols[w:w+A['rank']];outside=cols[w+A['rank']:]
            assert all(sum(x*y for x,y in zip(a,b))==0 for a in Ao for b in src)
            assert all(sum(x*y for x,y in zip(a,b))==0 for a in An for b in residual+src)
            assert all(gram(a,b)==0 for a in residual for b in src)
            assert all(gram(a,b)==0 for a in outside for b in residual+src)
            checked.add(key)
        chart_receipts.append([r,uses[r],before,after,w])
    dump('actual-endpoint-chart-binding.json',{'uses':chart_receipts,'combinations':len(checked),'identity_endpoints':5903,'new21factor_charts':3,'all_actual_endpoints_bound':True})
    return widths,programs,uses

def namespaces(roles,widths,programs,uses,bank):
    raw=gzip.decompress((PROPOSAL/'new-bank-assignments.bin.gz').read_bytes());assert sha(raw)==bank['assignment_sha256']
    assign={};coverage=bytearray(BANKS*100)
    for r,t,b,o,w,sc in struct.iter_unpack('>6I',raw):
        assert r in widths and widths[r]==w and 0<=t<60 and 0<=b<BANKS and 0<=o<o+w<=100 and 1<=sc<=25
        assert (r,t) not in assign;assign[r,t]=(b,o,w,sc)
        sl=slice(b*100+o,b*100+o+w);assert not any(coverage[sl]);coverage[sl]=b'\1'*w
    assert len(assign)==493260 and all(coverage[:-100]) and coverage[-100:]==b'\1'*80+b'\0'*20
    ids={};normalizers=[];maps=np.empty((5,60,10142,2),dtype='<i4');hashes=[]
    for s in range(5):
      for t in range(60):
        a=maps[s,t]
        for i in range(1920):a[i]=((4*t+ACTIVE[s][int(i>=960)])*960+i%960,0 if s==0 else 1+s*960+i%960)
        witnesses=defaultdict(list)
        for j,r in enumerate(roles):
            b,o,w,sc=assign[r,t];pid=uses.get(r,-1);key=s,o,w,sc,pid
            if key not in ids:
                pi=permutation(s,o,w);outside=next(j for j in range(100) if not 20*s<=j<20*(s+1))
                ids[key]=len(normalizers);normalizers.append({'id':ids[key],'stage':s,'support':[o,o+w],
                    'rank':w,'scalar':sc,'permutation':pi,'chart_program':pid,
                    'formula':'N=scalar*Pi*embed_stage(B_inverse)',
                    'physical_cover':'g=d*tau_stage*N_inverse',
                    'outside_column':outside,'unit_column_witness':[pi[outside],sc],
                    'paid_factor_bound':599})
            n=ids[key];family=230400+s*BANKS+b;a[1920+j]=(family,4801+n);witnesses[family].append(tuple(normalizers[n]['unit_column_witness']))
        a[-1]=(S,-1)
        assert len(set(map(tuple,a.tolist())))==10142
        assert all(len(set(x))==len(x) for x in witnesses.values())
        assert all(0<=int(f)<S for f in a[:-1,0]) and tuple(a[-1])==(S,-1)
        hashes.append({'stage':s,'replica':t,'sha256':sha(a.tobytes()),'full_address_injective':True})
    gz('all-namespaces.i32.gz',maps.tobytes())
    dump('normalizers.json.gz',{'normalizers':normalizers,'chart_programs':[programs[i] for i in sorted(set(uses.values()))],
        'same_common_ancestor_chart':True,'data_route_encoding':'0=d;1+s*960+port=d*rho_s_port;-1=external_work;4801+n=d*tau_s*N_n_inverse',
        'exact_regular_endpoint':'Checked chart B identifies the actual E-D residual. N sends its embedded image to Q_support; scalar cancels. Every cover sweep permutes all g classes, so every assigned block occurs once.'})
    dump('namespace-hashes.json',hashes)
    return maps,len(normalizers)

def completion(s):
    support=list(range(80,100));d=dict(zip(support+list(range(80)),range(100)));pi=[d[x] for x in range(100)];inv=[pi.index(x) for x in range(100)];factors=factor_perm(pi)
    for seq,want in ((list(reversed(factors)),pi),(factors,inv)):
        images=list(range(100))
        for i,j in seq:images=[j if x==i else i if x==j else x for x in images]
        assert images==want
    family=230400+(s+1)*BANKS-1
    return {'kind':'paid_bank_completion','stage':s,'family':family,'rank':20,'support':[80,100],
        'cover':'all_GL100_Rw','high_fibers':'one complete batch per low class',
        'permutation':pi,'inverse_permutation':inv,'chronological_forward':list(reversed(factors)),'chronological_inverse':factors,
        'permutation_convention':'Pi e_j=e_pi[j]','normalizer_factor_bound':599,
        'Q_entries':[[j,j,1] for j in support],
        'U_entries':[[j,k,1] for k,j in enumerate(support)]+[[199-j,k,-1] for k,j in enumerate(support)],
        'V_entries':[[k,j,-1] for k,j in enumerate(support)]+[[k,199-j,1] for k,j in enumerate(support)],
        'weighted_residual':'QA*D_(g Q_support g_inverse)*QA_inverse, common QA=diag(A,I100)',
        'generic_contract':'unit northeast minors; unit lower L/R/K adapters; child A[k*f+j]=A_parent[i_k*f+j]*D_P[k], f=floor(n/100); all rows restored; badclasses use full200dimensional unitpivotfallback',
        'fees':{'route_movements':2,'selectors':2*((S-1)+100*599),'wrappers':80008,'matrix_preparation':1024000000,'paid_child':1,'all_edge_fallback':320000,'bad_fraction':'1/10^16'},
        'instructions':[{'op':'ROUTE_RIGHT','family':family,'matrix':inv},
            {'op':'COMPILE_SPLIT_IDEMPOTENT','family':family,'rank':20,'support':list(range(20)),'chart':'h=g*Pi_inverse','identity':'h Q_prefix h_inverse=g Q_support g_inverse'},
            {'op':'ROUTE_RIGHT','family':family,'matrix':pi},
            {'op':'RESTORE_ROW_RESERVE','family':family,'coefficient':10001}]}

def phases():
    out=[]
    for s in range(5):
        out.extend({'kind':'helper','stage':s,'replica':t,'cover':'all_GL100_Rw','reverse_complement':s in(1,3)} for t in range(60))
        out.append(completion(s))
        if s in(1,2,4):
            out.extend({'kind':k,'stage':s,'which':{1:0,2:1,4:2}[s],'replica':t,'cover':'all_GL100_Rw'} for t in range(60) for k in('idle','bridge'))
    out.extend({'kind':'terminal_exchange','replica':t,'cover':'all_GL100_Rw'} for t in range(60))
    for i,p in enumerate(out):p['phase_index']=i
    return out

def check_schedule(ps):
    assert len(ps)==725 and ps==phases()
    for s in range(5):
        h=[i for i,p in enumerate(ps) if p['kind']=='helper' and p['stage']==s]
        c=[i for i,p in enumerate(ps) if p['kind']=='paid_bank_completion' and p['stage']==s]
        assert len(h)==60 and len(c)==1 and max(h)<c[0]
        later=[i for i,p in enumerate(ps) if p.get('stage')==s and p['kind'] in('idle','bridge')]
        if later:assert c[0]<min(later)

def invoice(ps,hist,bank):
    E=sum(hist.values());J=60*(24*960+10*8221)+sum(p['fees']['route_movements'] for p in ps if p['kind']=='paid_bank_completion')
    K=2*5*60*((S-1)+8221*100*599)+sum(p['fees']['selectors'] for p in ps if p['kind']=='paid_bank_completion')
    terms={'unit_expanded_additions':60*(5*338159+6*960),'high_affine_factors':J*16*10001**2,'low_transpositions':J*(S+20),
        'generic_wrappers':E*80008,'matrix_preparation':E*128*200**3,'global_matrix_preparation':16*100**3,
        'copy_erase_episodes':6000,'paid_child_overhead':E,'bank_selectors':K,'constant':1}
    assert terms==bank['terms'] and (J,K,sum(terms.values()))==(6315010,295864873940,25478454083580596)
    return {'literal_stock':S,'children':E,'rank_mass':sum(r*n for r,n in hist.items()),'terms':terms,'coefficient':sum(terms.values()),
        'route_movements':J,'selector_calls':K,'all_edges_pay_fallback320000':True,'row_reserve':10001,'new_temporary_roles':0,'max_rank':max(hist)}

def controls(ps,records,frames,ep):
    rejected=[];at=next(i for i,p in enumerate(ps) if p['kind']=='paid_bank_completion')
    def reject(name,fn):
        bad=copy.deepcopy(ps);fn(bad)
        try:check_schedule(bad)
        except AssertionError:rejected.append(name)
        else:raise AssertionError('accepted mutation '+name)
    reject('omitted_completion',lambda x:x.pop(at))
    reject('wrong_bank',lambda x:x[at].__setitem__('family',x[at]['family']-1))
    reject('overlapping_support',lambda x:x[at].__setitem__('support',[79,99]))
    reject('missing_route_back',lambda x:x[at]['instructions'].pop(2))
    reject('missing_wrappers',lambda x:x[at]['fees'].__setitem__('wrappers',0))
    reject('missing_fallback',lambda x:x[at]['fees'].__setitem__('all_edge_fallback',0))
    reject('wrong_rank',lambda x:x[at].__setitem__('rank',49))
    def early(x):x[at],x[at-1]=x[at-1],x[at]
    reject('completion_before_last_helper',early)
    bad=copy.deepcopy(records);i=next(i for i,r in enumerate(bad) if r[0]==0 and r[4]>0);bad[i][4]+=1
    try:verify_local(bad,frames,ep)
    except AssertionError:rejected.append('wrong_MOVE_rank')
    else:raise AssertionError('rank accepted')
    return rejected

def main():
    proposal,bank,local,records,frames,ep,roots=read_bound_inputs();start_local=fs(LOCAL/'RESULT.json')
    roles=read(packet.BASE_LOWER/'compact-role-index.json')['roles'];assert len(roles)==8221
    H,ops=verify_local(records,frames,ep)
    assert H==Counter({int(k):v for k,v in proposal['one_stage_histogram'].items()})
    widths,programs,uses=exact_endpoint_charts(roles,frames,ep,bank)
    assert Counter(widths.values())==Counter({int(k):v for k,v in proposal['residual_census'].items()})
    maps,norms=namespaces(roles,widths,programs,uses,bank);print('All300 namespaces and actual endpoint charts bound',flush=True)
    ps=phases();check_schedule(ps);phase_ids={(p['stage'],p['replica']):p['phase_index'] for p in ps if p['kind']=='helper'}
    bindings=[];templates=[];copy_overrides=[];hist=Counter();program=hashlib.sha256();counts=Counter()
    for s in range(5):
        template=stage_template(s,records,frames)
        assert Counter(map(int,template[(template[:,0]==0)&(template[:,4]>0),4]))==H
        for ordinal,row in enumerate(template):
            op,a,b,c,f,z,stage,rev,source=map(int,row)
            if op!=0:continue
            signed=(frames[str(c)]['rank']-frames[str(b)]['rank'])*(-1 if rev else 1)
            orientation=-1 if a==WORK and not rev else 1;assert orientation*signed==f
            if a==WORK:
                assert f==18
                copy_overrides.append({'stage':s,'template_record':ordinal,'local_source_record':source,'family':S,
                    'old_frame':b,'new_frame':c,'complement':rev,'rank':18,'difference_orientation':orientation,
                    'positive_projector':'F(old,0)-F(new,0)' if not rev else 'F(new,1)-F(old,1)',
                    'meaning':'positive embedded center projector; D_P=D_P_inverse; never D_negativeP'})
        templates.append(gz(f'stage-{s}-template.i32.gz',template.tobytes()))
        for t in range(60):
            a=maps[s,t];data=np.zeros((len(template),12),dtype='<i4');data[:,0]=phase_ids[s,t];data[:,1]=template[:,0]
            data[:,2:4]=a[template[:,1]];data[:,4]=template[:,2];data[:,5]=-2
            mask=(template[:,0]==1)|(template[:,0]==2);data[mask,4:6]=a[template[mask,2]];data[:,6:]=template[:,3:]
            assert np.all(np.any(data[mask,2:4]!=data[mask,4:6],axis=1))
            digest=sha(data.tobytes());program.update(bytes.fromhex(digest));hist.update(H)
            bindings.append({'stage':s,'replica':t,'phase_index':phase_ids[s,t],'records':len(template),'sha256':digest})
        print('Materialized all60 full frame streams at stage',s,flush=True)
    boundary=bytearray()
    for p in ps:
        if p['kind']=='helper':p['template']=templates[p['stage']];p['local_record_sha256']=roots['current_local_record_bytes']
        elif p['kind']=='paid_bank_completion':hist[p['rank']]+=1
        else:
            for row in emit_boundary(p):
                boundary.extend(struct.pack('<8i',p['phase_index'],*row));counts[row[0]]+=1
                if row[0]==4:hist[row[4]]+=1
    assert counts=={4:460800,5:345600,7:115200}
    assert hist==Counter({int(k):v for k,v in proposal['literal_histogram'].items()})
    assert (sum(hist.values()),sum(r*n for r,n in hist.items()),max(hist))==(15006605,65703100,42)
    assert len(copy_overrides)==100
    # Integer column proof of the actual partialbank's full arbitrarydirty swap.
    blocks=[(0,20),(20,20)]+[(40+4*j,4) for j in range(10)]+[(80,20)]
    state=list(range(200))
    for off,width in blocks:
        for j in range(off,off+width):state[j],state[199-j]=state[199-j],state[j]
    assert state==list(range(199,-1,-1))
    dump('extended-phases.json',ps);dump('all-frame-bindings.json',bindings);dump('copied-work-projector-overrides.json',copy_overrides)
    gz('boundary-records.i32.gz',boundary)
    descriptors={'local_frames_sha256':fs(LOCAL/'local-frames.json.gz'),
        'P_frame':'B^t*(B*G*B^t)^-1*B*G; G=I20-J20/9; B from exact local frame registry',
        'F_stage':'diag(P_frame if not reflected else I20-P_frame,Kstar in windows 1..stage,0 later); Kstar=I20-qstar*qstar^t*G/2',
        'regular_MOVE':'positive F(new,rev)-F(old,rev), conjugated by invocation d and same ancestor QA',
        'copied_work_MOVE':'mandatory explicit positive projector overrides in copied-work-projector-overrides.json; forward source frame → ZERO uses old-minus-new',
        'copied_work_sha256':fs(OUT/'copied-work-projector-overrides.json'),
        'physical_to_invocation_chart':'helper g=d*tau*N_inverse hence d=g*N*tau_inverse; data d=g*rho_inverse',
        'boundary_projectors':'retained eight exact idle_projector formulas, literal port indices and bridge/exchange coefficients',
        'generic':'ambient 100 split-idempotent child, strict maximum 42 < 50; all child wrappers and all-edge fallback charged',
        'no_new_initialization':'all 200 bank columns arbitrary-dirty; completed child restores rows; unchanged fresh COPY primitive'}
    dump('projector-descriptors.json',descriptors)
    for name in ('extended-phases.json','copied-work-projector-overrides.json','projector-descriptors.json'):program.update((OUT/name).read_bytes())
    program.update(boundary)
    bill=invoice(ps,hist,bank);dump('invoice.json',bill)
    rejected=controls(phases(),records,frames,ep);rejected.append('negative_forward_copied_work_difference_rejected')
    assert fs(LOCAL/'RESULT.json')==start_local
    for name,h in local['artifacts'].items():assert fs(LOCAL/name)==h
    result={'status':'PASS_SOURCE_BOUND_PR322_PR323_PAID892_GLOBAL_FRAME_IR',
        'base_word_sha256':WORD,'source_heads':HEADS,'candidate_fingerprint':sha(canonical(roots)),
        'source_identity':roots,'local_result_sha256':start_local,'local_compiler_sha256':local['checker_sha256'],
        'compiler_sha256':fs(__file__),'retained_ir_helpers_sha256':fs(HERE/'retained_ir_helpers.py'),
        'composition_result_sha256':fs(PROPOSAL/'RESULT.json'),'bank_result_sha256':fs(PROPOSAL/'BANK-RESULT.json'),
        'actual_local_records':len(records),'local_opcodes':dict(ops),'local_histogram':dict(sorted(H.items())),
        'literal_histogram':dict(sorted(hist.items())),'literal_stock':S,'calls':sum(hist.values()),'rank_mass':sum(r*n for r,n in hist.items()),
        'max_rank':42,'normalizer_descriptors':norms,'phases':725,'completion_sweeps':5,'completion_rank':20,
        'expanded_frame_stage_records':sum(x['records'] for x in bindings),'full_program_sha256':program.hexdigest(),
        'copied_work_positive_projector_overrides':100,'invoice':bill,'rejected_controls':rejected,
        'upstream_production_code_executed':False,'previous_paid892_packet_modified':False,
        'attribution':'PR322 four exact retiming witnesses and PR323 three rank-two kernels are upstream selections, credited by immutable head and selector hashes; upstream authors/notices remain in the source admission packet. This is independent integration and verification, not a claim to original discovery.',
        'scope':'Explicit admitted local frame word, exact actual endpoint charts, all 300 literal namespaces, five new rank-20 completion sweeps and full signed boundary records are bound. The literal histogram comes from actual emitted records. Generic primitive, prime uniformity, ordinary leaves, complex supplier and all-size theorem interfaces remain inherited.'}
    dump('RESULT.json',result)
    dump('MANIFEST.json',{p.name:fs(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name not in ('MANIFEST.json','PROJECTOR-CONTROLS.json')})
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
