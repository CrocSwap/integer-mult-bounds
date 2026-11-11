from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import support
support.require_assertions()
"""Independent global address lowering of the new complete local frame word.

The local constructor's output is inert input and its hashes are verified.
No production compiler is run. Exact projector meanings are linked to explicit
annihilator/basis matrices and source-bound rational route formulas.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as F
import gzip,hashlib,json,struct,copy,os
import numpy as np
if not __debug__:raise RuntimeError('Assertions required')
HERE=Path(__file__).resolve().parent
OUT=support.LOWER
DEST=support.out("full-frame", "placeholder").parent
LOCAL=support.FRAME
PAID=support.BANK/"split_49_11"
CHART=support.BASE_OUTPUT/"finite/endpoint-charts.json.gz"
HEAD='1b37957d1520c80b6ea796bf418e52be5109c2d4'
WORD='25a0edc8c5f399fcf536b28c4e3575aa52177bb78b6078a631acb748954f0739'
sha=lambda b:hashlib.sha256(b).hexdigest()
def fs(p):return sha(Path(p).read_bytes())
def read(p):
    p=Path(p);raw=p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.name.endswith('.gz') else raw)
def dump(name,x):
    raw=json.dumps(x,sort_keys=True,separators=(',',':')).encode()+b'\n'
    (DEST/name).write_bytes(gzip.compress(raw,mtime=0) if name.endswith('.gz') else raw)
def gz(name,data):
    with gzip.GzipFile(filename=str(DEST/name),mode='wb',mtime=0) as z:z.write(data)
    return {'file':name,'uncompressed_bytes':len(data),'sha256':sha(data),'compressed_sha256':fs(DEST/name)}

def verify_local(records,frames,endpoints,receipt):
    state={int(k):v for k,v in endpoints['initial'].items()}
    final={int(k):v for k,v in endpoints['final'].items()}
    assert set(state)==set(final)==set(range(10141))
    rank=lambda f:frames[str(f)]['rank']
    hist=Counter();coeff=Counter();tmp=None;reads=0;counts=Counter()
    for i,row in enumerate(records):
        op,a,b,c,f,*extra=row;counts[op]+=1
        if op==0:
            assert state[a]==b and rank(c)-rank(b)==f and f>=0
            state[a]=c
            if f:hist[f]+=1
        elif op==1:
            assert a!=b and state[a]==state[b]==f and c%2
            coeff[abs(c)]+=1
            if b==10141:assert tmp is not None;reads+=1
        elif op==2:
            assert tmp is None and b==10141 and state[a]==c and rank(c)==18 and rank(f)==0
            state[b]=f;tmp=(a,b,c,f);hist[rank(c)]+=1;reads=0
        else:
            assert op==3 and tmp==(a,b,c,f) and state[a]==c and state[b]==f and reads==144
            del state[b];tmp=None
    assert state==final and tmp is None
    assert hist==Counter({int(k):v for k,v in receipt['one_stage_paid_histogram'].items()})
    assert (sum(hist.values()),sum(r*n for r,n in hist.items()))==(48473,179464)
    assert coeff=={1:335293,3:960} and counts[2]==counts[3]==20 and counts[1]==336253
    return hist,counts

def stage_template(stage,records,frames):
    rev=stage in (1,3);out=[]
    for index in (range(len(records)-1,-1,-1) if rev else range(len(records))):
        row=records[index];op,a,b,c,f,*extra=row;z=extra[0] if extra else 0
        if op==0:out.append([0,a,c if rev else b,b if rev else c,f,0,stage,int(rev),index])
        elif op==1:out.append([1,a,b,-c if rev else c,f,z,stage,int(rev),index])
        elif op==(3 if rev else 2):
            out.append([2,b,a,0,c,0,stage,int(rev),index])
            out.append([0,b,c,f,frames[str(c)]['rank'],0,stage,int(rev),index])
        else:
            assert op==(2 if rev else 3)
            out.append([3,b,-1,0,f,0,stage,int(rev),index])
    return np.asarray(out,dtype='<i4')

def endpoint_charts(frames,endpoints):
    """Bind exact emitted endpoint frames to the already checked chart B."""
    roles=read(OUT/'compact-role-index.json')['roles']
    charts=read(CHART);programs={x['program_id']:x for x in charts['factor_programs']}
    uses={x['role']:x for x in charts['role_uses']};initial=endpoints['initial'];final=endpoints['final']
    seen=set();receipts=[]
    def gram(a,b):return 9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)
    for i,r in enumerate(roles):
        old=frames[str(initial[str(1920+i)])];new=frames[str(final[str(1920+i)])]
        width=new['rank']-old['rank'];assert width>0
        if r not in uses:
            assert old['rank']==0 and new['rank']==20 and width==20
            continue
        p=programs[uses[r]['program_id']]
        assert (p['donor_dimension'],p['recipient_dimension'],p['rank'])==(old['rank'],new['rank'],width)
        key=(p['program_id'],initial[str(1920+i)],final[str(1920+i)])
        if key not in seen:
            cols=[[F(x) for x in row] for row in p['basis_columns']]
            Ao=[[F(x) for x in row] for row in old['annihilator']]
            An=[[F(x) for x in row] for row in new['annihilator']]
            residual=cols[:width];source=cols[width:width+old['rank']];outside=cols[width+old['rank']:]
            assert all(sum(x*y for x,y in zip(a,b))==0 for a in Ao for b in source)
            assert all(sum(x*y for x,y in zip(a,b))==0 for a in An for b in residual+source)
            assert all(gram(a,b)==0 for a in residual for b in source)
            assert all(gram(a,b)==0 for a in outside for b in residual+source)
            seen.add(key)
        receipts.append([r,p['program_id'],old['rank'],new['rank'],width])
    assert len(receipts)==2315
    dump('actual-endpoint-chart-binding.json',{'uses':receipts,'exact_chart_endpoint_combinations':len(seen),
        'identity_endpoints':5906,'source_frames':'actual final emitted local initial/final frame matrices',
        'inherited_chart_inverse_and_factor_checks':fs(CHART),
        'all_real_endpoint_projectors_equal_assigned_bank_projectors':True})
    return len(seen)

def main():
    incremental=read(OUT/'RESULT.json');paid=read(PAID/'RESULT.json')
    assert incremental['candidate_sha256']==paid['word_sha256']==WORD
    receipt=read(LOCAL/'RESULT.json')
    local_result_hash=fs(LOCAL/'RESULT.json')
    assert receipt['head']==HEAD and receipt['candidate_sha256']==WORD
    assert receipt['status']=='PASS_EXPLICIT_LOCAL892_FRAME_WORD'
    assert fs(support.HERE/'frame/build_local.py')==receipt['checker_sha256']
    for name,h in receipt['artifacts'].items():assert fs(LOCAL/name)==h
    assert receipt['all_integer_operand_source_spans_contained'] and receipt['source_descent_entries']==480 and receipt['moves']==133
    correction=read(LOCAL/'SOURCE-GEOMETRY-CORRECTION.json')
    records=read(LOCAL/'local-records.json.gz');frames=read(LOCAL/'local-frames.json.gz');endpoints=read(LOCAL/'local-endpoints.json')
    H,localcounts=verify_local(records,frames,endpoints,receipt)
    ncharts=endpoint_charts(frames,endpoints)
    print('Actual final frame records and exact bank endpoint charts bound',flush=True)
    spaces=np.frombuffer(gzip.decompress((OUT/'all-namespaces.i32.gz').read_bytes()),dtype='<i4').reshape(5,60,10142,2)
    phases=read(OUT/'extended-phases.json');phase_id={(x['stage'],x['replica']):x['phase_index'] for x in phases if x['kind']=='helper'}
    bindings=[];templates=[];globalhist=Counter();whole=hashlib.sha256();copy_projectors=[]
    for s in range(5):
        template=stage_template(s,records,frames)
        stagehist=Counter(int(x) for x in template[(template[:,0]==0)&(template[:,4]>0),4])
        assert stagehist==H
        for ordinal,row in enumerate(template):
            op,a,b,c,f,z,stage,rev,raw_index=map(int,row)
            if op!=0:continue
            signed_rank=(frames[str(c)]['rank']-frames[str(b)]['rank'])*(-1 if rev else 1)
            orientation=-1 if a==10141 and not rev else 1
            assert orientation*signed_rank==f
            if a==10141:
                assert f==18 and frames[str(b)]['rank']==18 and frames[str(c)]['rank']==0
                copy_projectors.append({'stage':s,'template_record':ordinal,'local_source_record':raw_index,
                    'family':658275,'route':'external_work0','old_frame':b,'new_frame':c,
                    'complement':rev,'rank':18,'difference_orientation':orientation,
                    'positive_projector':'F_s(old,0)-F_s(new,0)' if not rev else 'F_s(new,1)-F_s(old,1)',
                    'identity':'Both expressions equal embedded P_center. The frame transport is D_P, and D_P^-1=D_P; it is never D_(-P).',
                    'primitive':'fresh original-center COPY followed by one positive split-rank 18 child'})
        templatefile=gz(f'stage-{s}-template.i32.gz',template.tobytes());templates.append(templatefile)
        for t in range(60):
            address=spaces[s,t];data=np.zeros((len(template),12),dtype='<i4')
            data[:,0]=phase_id[s,t];data[:,1]=template[:,0]
            data[:,2:4]=address[template[:,1]]
            data[:,4]=template[:,2];data[:,5]=-2
            mask=(template[:,0]==1)|(template[:,0]==2)
            data[mask,4:6]=address[template[mask,2]]
            data[:,6:]=template[:,3:]
            assert np.all(np.any(data[mask,2:4]!=data[mask,4:6],axis=1))
            raw=data.tobytes();digest=sha(raw)
            bindings.append({'stage':s,'replica':t,'phase_index':phase_id[s,t],
                'records':len(template),'sha256':digest,'paid_histogram':dict(sorted(stagehist.items()))})
            whole.update(bytes.fromhex(digest));globalhist.update(stagehist)
        print('All 60 literal namespaces bound to final frame stage',s,flush=True)
    boundary=np.frombuffer(gzip.decompress((OUT/'boundary-records.i32.gz').read_bytes()),dtype='<i4').reshape(-1,8)
    for r in boundary[boundary[:,1]==4,5]:globalhist[int(r)]+=1
    completions=[x for x in phases if x['kind']=='paid_bank_completion']
    for x in completions:globalhist[x['rank']]+=1
    assert globalhist==Counter({int(k):v for k,v in paid['literal_profile']['histogram'].items()})
    assert (sum(globalhist.values()),sum(r*n for r,n in globalhist.items()),max(globalhist))==(15002710,65705100,49)
    for x in phases:
        if x['kind']=='helper':
            x['body']='concrete_final_frame_stage_template'
            x.pop('scalar_template',None);x['template']=templates[x['stage']]
            x['local_source_sha256']=fs(LOCAL/'local-records.json.gz')
    dump('extended-final-frame-phases.json',phases)
    whole.update(json.dumps(phases,sort_keys=True,separators=(',',':')).encode())
    whole.update(boundary.tobytes())
    dump('all-final-frame-bindings.json',bindings)
    assert len(copy_projectors)==100 and Counter(x['difference_orientation'] for x in copy_projectors)=={-1:60,1:40}
    dump('copied-work-projector-overrides.json',copy_projectors)
    dump('projector-descriptors.json',{
        'local_frame_registry_sha256':fs(LOCAL/'local-frames.json.gz'),
        'local_projector':'For frame annihilator A_f, obtain exact B_f=null(A_f). P_f=B_f^t*(B_f*G*B_f^t)^-1*B_f*G, G=I20-J20/9; P_ZERO=0,P_FULL=I20.',
        'stage_projector':'F_s(f,rev)=diag(P_f if rev=0 else I20-P_f, Kstar on windows 1 through s, zero on later windows). Kstar=I20-qstar*(qstar^t*G)/2, qstar=(1,1,1,0,...,0).',
        'MOVE_residual_regular':'QA*D_[d*(F_s(new,rev)-F_s(old,rev))*d^-1]*QA^-1 for real regular roles. Emitted f field is the actual nonnegative split rank. Rank 0 emits no recursive child.',
        'MOVE_residual_copied_work':'Use the explicit copied-work-projector-overrides.json entry: in forward stages the source-frame-to-ZERO transport uses F_s(old,0)-F_s(new,0), while reflected stages use F_s(new,1)-F_s(old,1). Both are the positive embedded center projector of rank 18. D_P is its own inverse. Never pass negative P to the split-idempotent compiler.',
        'copied_work_override_sha256':fs(DEST/'copied-work-projector-overrides.json'),
        'physical_chart_relation':'For real helper address g=d*tau_s*N^-1, recover d=g*N*tau_s^-1. Data uses g=d*rho_s(port); d=g*rho_s(port)^-1. Temporary address is external_work0.',
        'ADD':'Emitted signed coefficient, source and destination, exact frame ID and stage complement are retained. Matrix-address arithmetic is not reduced modulo 2.',
        'COPY':'Fresh source→external work followed by explicit paid MOVE of rank 18; reverse stage starts fresh COPY at the old ERASE. Never invert ERASE.',
        'boundary_projectors':'Eight explicit IDLE IDs use retained inert global_lowering.idle_projectors formulas and exact port indices; bridge signed coefficients and terminal exchanges are emitted literally.',
        'common_weight':'QA=diag(A,I100) from same parent ancestor descriptor on all helper, boundary and completion residuals',
        'generic_compilation':'Inherited unit-minor split-idempotent child compiler and full local-ring fallback; rank guard 2r<100, contiguous child k*f+j and rows restored'})
    # Mathematical descriptors are part of the program identity, including
    # the copied-work orientation exception, not merely side documentation.
    whole.update((DEST/'projector-descriptors.json').read_bytes())
    whole.update((DEST/'copied-work-projector-overrides.json').read_bytes())
    controls=[]
    broken=copy.deepcopy(records);first=next(i for i,r in enumerate(broken) if r[0]==0 and r[4]>0);broken[first][4]+=1
    try:verify_local(broken,frames,endpoints,receipt)
    except AssertionError:controls.append('wrong_actual_MOVE_rank')
    else:raise AssertionError('rank mutation accepted')
    broken=copy.deepcopy(records);first=next(i for i,r in enumerate(broken) if r[0]==1);broken[first][1]=broken[first][2]
    try:verify_local(broken,frames,endpoints,receipt)
    except AssertionError:controls.append('aliased_actual_ADD_operands')
    else:raise AssertionError('alias mutation accepted')
    # The formerly implicit forward-COPY direction would be a negative-rank
    # difference, not an idempotent. It must fail the positive-rank contract.
    forward_copy=next(x for x in copy_projectors if not x['complement'])
    assert frames[str(forward_copy['new_frame'])]['rank']-frames[str(forward_copy['old_frame'])]['rank']==-18
    controls.append('blanket_new_minus_old_on_forward_copied_work_rejected')
    assert fs(LOCAL/'RESULT.json')==local_result_hash,'local source changed during binding'
    assert fs(support.HERE/'frame/build_local.py')==receipt['checker_sha256']
    for name,h in receipt['artifacts'].items():assert fs(LOCAL/name)==h
    result={'status':'PASS_COMPLETE_LOCAL_FRAME_TO_PAID_GLOBAL_IR_BINDING','head':HEAD,'candidate_sha256':WORD,
        'local_constructor_sha256':fs(support.HERE/'frame/build_local.py'),'local_result_sha256':fs(LOCAL/'RESULT.json'),
        'source_geometry_correction_sha256':fs(LOCAL/'SOURCE-GEOMETRY-CORRECTION.json'),
        'incremental_result_sha256':fs(OUT/'RESULT.json'),'compiler_sha256':fs(__file__),
        'actual_local_records':len(records),'local_opcodes':dict(localcounts),
        'local_paid_histogram':dict(sorted(H.items())),'literal_global_paid_histogram':dict(sorted(globalhist.items())),
        'literal_stock':658275,'paid_calls':sum(globalhist.values()),'rank_mass':sum(r*n for r,n in globalhist.items()),
        'strict_max_rank':49,'phase_count':len(phases),'concrete_frame_stage_records':sum(x['records'] for x in bindings),
        'exact_actual_endpoint_chart_combinations':ncharts,
        'full_program_binding_sha256':whole.hexdigest(),'added_completion_calls':10,
        'all300_stage_frame_operands_materialized_and_hashed':True,
        'scalar_coefficients_and_COPY_lifetimes_bound':True,'reordered_local_source_frames_explicit':True,
        'actual_local_raw_frame_word_regenerated':True,'production_primitive_compiler_executed':False,
        'copied_work_positive_projector_overrides':100,
        'upstream_production_code_executed':False,'rejected_controls':controls,
        'scope':'Actual independent final local frame word, all 133 explicit screened reorders and 480 descents are bound through all 300 literal namespaces to full global phase IR. Literal child histogram is derived from emitted MOVE/COPY/boundary/completion records. Generic primitive compiler and uniform prime/analytic/all-size contracts remain inherited; the separate finite validator checks every concrete local frame; this is not a full primitive execution or unconditional theorem.',
        'input_artifacts':{name:fs(LOCAL/name) for name in receipt['artifacts']}}
    dump('RESULT.json',result)
    dump('MANIFEST.json',{p.name:fs(p) for p in sorted(DEST.iterdir()) if p.is_file() and p.name!='MANIFEST.json'})
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
