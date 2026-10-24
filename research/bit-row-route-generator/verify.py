"""Source authentication, independent endpoint oracle and destructive checks."""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
from copy import deepcopy
import argparse,gzip,json,sys,time
from collections import Counter
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from generator import generate
from interpreter import run


def need(ok,msg):
    if not ok:raise ValueError(msg)


def authenticate():
    pins=json.loads((HERE/'SOURCES.json').read_text())['files']
    for row in pins:
        if row['usage']=='input':need(sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source hash mismatch: '+row['path'])
    frames=json.loads((ROOT/'research/kappa-rebuild/bit/sources/pr589-regenerated/records/frames.json').read_text())
    word=json.loads(gzip.decompress((ROOT/'research/bit-compact-carrier-retirement/provider/inputs/WORD.json.gz').read_bytes()))
    need(word['start'][462]==0 and word['final'][462]==506 and word['start'][461]==0,'actual original owner/frame binding')
    frame=frames['frames']['506'];need(frame['dim']==4,'source rank four')
    return frame


def mm(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def tr(a):return [list(x) for x in zip(*a)]
def inv(a):
    # Independent augmented rational solve, never uses generator elimination.
    n=len(a);work=[[F(x) for x in row]+[F(i==j) for j in range(n)] for i,row in enumerate(a)]
    for col in range(n):
        p=next(i for i in range(col,n) if work[i][col]);work[col],work[p]=work[p],work[col]
        d=work[col][col];work[col]=[x/d for x in work[col]]
        for i in range(n):
            if i!=col:
                d=work[i][col];work[i]=[x-d*y for x,y in zip(work[i],work[col])]
    return [r[n:] for r in work]
def mod(a,m):return [[int(F(x).numerator*pow(F(x).denominator,-1,m))%m for x in row] for row in a]
def lift(a,f):return [[a[i//f][j//f]*int(i%f==j%f) for j in range(len(a)*f)] for i in range(len(a)*f)]


def source_matrices(frame,f):
    b=[[F(v) for v in row] for row in frame['B']]
    p=mm(mm(tr(b),inv(mm(b,tr(b)))),b)
    s=tr([[F(v) for v in row] for row in frame['B']+frame['A']])
    return lift(p,f),lift(s,f)


def check_rational_routes(frame):
    # Reconstruct the emitted row-zero word, not generator.factors().
    p,s=source_matrices(frame,1);identity=[[F(i==j) for j in range(8)] for i in range(8)]
    canonical=[[F(i==j and i<4) for j in range(8)] for i in range(8)]
    need(mm(p,p)==p,'exact source projector idempotence')
    need(mm(mm(s,canonical),inv(s))==p,'exact source projector conjugation')
    program=encoded(frame,1,5,2);products={1:deepcopy(identity),-1:deepcopy(identity)};counts={1:0,-1:0};direction=None
    for step in program['steps']:
        if step['op']=='route_enter':direction=step['direction']
        op=step['op'];addresses=step['addresses']
        if op not in ('older_full_swap','unit_scale','ordered_shift') or any(a>=8 for a in addresses):continue
        elementary=deepcopy(identity);a=addresses[0];z=F(*step['coefficient'])
        if op=='older_full_swap':
            b=addresses[1];elementary[a][a]=elementary[b][b]=F(0);elementary[a][b]=elementary[b][a]=F(1)
        elif op=='unit_scale':elementary[a][a]=z
        else:elementary[addresses[1]][a]=z
        products[direction]=mm(products[direction],elementary);counts[direction]+=1
    need(products[1]==s and products[-1]==inv(s),'exact actual emitted right-factor products')
    need(counts=={1:24,-1:24},'complete actual factor words')
    return dict(projector_idempotence=True,source_conjugation=True,emitted_forward_and_inverse_factors=48)


def state_for(program,seed=1,body_column=None,high_column=None):
    n=program['f']*8;q=program['q'];w=program['w'];r=q**(w-1);m=q**w
    low=[int(i==j) for i in range(n) for j in range(n)]
    # Nontrivial invertible low row, so a dropped carry is observable.
    low[1]=1;low[n+2]=q-1
    high=[((i+1)*seed+3*i*i)%r for i in range(n*n)]
    if high_column is not None:high=[int(i==high_column) for i in range(n*n)]
    h=[(3*i+seed)%m for i in range(n)];d=[(7*i+5*seed)%m for i in range(n)]
    if body_column is not None:
        h=[int(i==body_column) for i in range(n)];d=[int(i+n==body_column) for i in range(n)]
    return dict(slots={'462':7,'461':11},owners={'462':dict(low=low,high=high,h=h,d=d,outer=[91+seed,13,5],z=[-17,3,seed],tape_head=9),'461':dict(arbitrary=[seed,-12,999,0],tape_head=4)})


def check_action(program,state,frame,return_output=False):
    out,trace=run(program,state);n=8*program['f'];q=program['q'];m=q**program['w'];p,s=source_matrices(frame,program['f'])
    old=state['owners']['462'];new=out['owners']['462'];g=[[old['low'][i*n+j]+q*old['high'][i*n+j] for j in range(n)] for i in range(n)]
    # Rational inversion followed by valid local-ring reduction is independent
    # of the interpreter's modular row solver and generated elementary word.
    request=mod(mm(mm(g,p),inv(g)),m);forward=mod(mm(g,s),m)
    ph=[sum(x*y for x,y in zip(row,old['h']))%m for row in request]
    pd=[sum(x*y for x,y in zip(row,reversed(old['d'])))%m for row in request]
    expected_h=[(v-a+b)%m for v,a,b in zip(old['h'],ph,pd)]
    expected_d=[(v+a-b)%m for v,a,b in zip(old['d'],reversed(ph),reversed(pd))]
    need(new['h']==expected_h and new['d']==expected_d,'independent source projector endpoint')
    need(trace['route_returns'][0]==sum(forward,[]) and trace['route_returns'][1]==sum(g,[]),'independent full cover route and inverse')
    need(new['low']==old['low'] and new['high']==old['high'],'all fresh ROW coordinates restored')
    need(new['outer']==old['outer'] and new['z']==old['z'] and new['tape_head']==old['tape_head'] and out['owners']['461']==state['owners']['461'],'all original spectator owners preserved')
    need(trace['calls']==program['ledger']['primitive_calls'],'exact generated primitive ledger')
    need(trace['peak_owned_low_cells']==n*n,'owned cache extent')
    return (out,trace) if return_output else trace


def reject(action,label):
    try:action()
    except (ValueError,IndexError,KeyError,ZeroDivisionError):return label
    raise ValueError('control accepted: '+label)


def recount(program):
    program['ledger']['primitive_calls']=dict(Counter(s['op'] for s in program['steps']))
    return program

def controls(frame,program):
    rows=[];state=state_for(program)
    rows.append(reject(lambda:generate(frame,1,15,4),'composite generator radix'))
    bad=deepcopy(program);bad['q']=15;rows.append(reject(lambda:run(bad,state),'composite serialized-program radix'))
    wrong_frame=deepcopy(frame);wrong_frame['B'][0][0]=1
    rows.append(reject(lambda:generate(wrong_frame,1,5,4),'wrong source frame'))
    rows.append(reject(lambda:generate(frame,1,5,4,owners=(462,462)),'duplicate source owner'))
    rows.append(reject(lambda:generate(frame,1,5,4,reserve=6),'insufficient current argument reserve'))
    bad=deepcopy(state);bad['slots']['461']=bad['slots']['462'];rows.append(reject(lambda:run(program,bad),'physical owner alias'))
    bad=deepcopy(state);bad['owners']['461']=bad['owners']['462'];rows.append(reject(lambda:run(program,bad),'owner object alias'))
    bad=deepcopy(program);next(s for s in bad['steps'] if s['op']=='ordered_shift')['addresses'][0]=8*program['f']*8*program['f'];rows.append(reject(lambda:run(bad,state),'out of owner address'))
    n=8*program['f'];q=program['q'];m=q**program['w'];r=m//q
    sm=mod(source_matrices(frame,program['f'])[1],m);low=state['owners']['462']['low']
    carries=[sum(low[row*n+j]*sm[j][col] for j in range(n))//q%r for row in range(n) for col in range(n)]
    cell=next(i for i,c in enumerate(carries) if c)
    bad=deepcopy(program);bad['steps'].remove(next(s for s in bad['steps'] if s['op']=='carry_shift' and s['addresses']==[cell]));rows.append(reject(lambda:check_action(recount(bad),state,frame),'omitted nonzero carry cell '+str(cell)))
    bad=deepcopy(program);bad['steps'].remove(next(s for s in bad['steps'] if s['op']=='ordered_shift'));rows.append(reject(lambda:check_action(recount(bad),state,frame),'omitted elementary route'))
    bad=deepcopy(program);bad['steps'].remove(next(s for s in bad['steps'] if s['op']=='inner_return'));rows.append(reject(lambda:run(bad,state),'premature ROW unpad'))
    bad=deepcopy(program);bad['steps'].remove(next(s for s in bad['steps'] if s['op']=='cache_clear'));rows.append(reject(lambda:run(bad,state),'uncleared owned cache'))
    rows.append(reject(lambda:run(program,state,'borrowed_row_write'),'current inner ROW corruption'))
    rows.append(reject(lambda:run(program,state,'outer_row_write'),'outer ROW corruption'))
    bad=deepcopy(program);s=next(s for s in bad['steps'] if s['op']=='older_high_swap');s['op']='older_full_swap';rows.append(reject(lambda:check_action(recount(bad),state,frame),'wrong post-return high interchange'))
    return rows


def encoded(frame,f,q,w):return json.loads(json.dumps(generate(frame,f,q,w).export()))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--probe',action='store_true');args=ap.parse_args();frame=authenticate();start=time.monotonic()
    example=encoded(frame,1,5,4);check_action(example,state_for(example),frame)
    if args.probe:print('PASS_PROBE',round(time.monotonic()-start,3));return
    rational_checks=check_rational_routes(frame);traces=[];basis=high_basis=dirty=0
    for f,q,w in ((1,5,2),(1,5,4),(2,7,4)):
        program=encoded(frame,f,q,w);n=8*f
        for column in range(2*n):
            trace=check_action(program,state_for(program,body_column=column),frame);basis+=1
        if f==1 and w==2:
            check_action(program,state_for(program,high_column=-1),frame)
            for column in range(n*n):check_action(program,state_for(program,high_column=column),frame);high_basis+=1
        for seed in (2,7):check_action(program,state_for(program,seed),frame);dirty+=1
        traces.append(dict(f=f,q=q,w=w,steps=len(program['steps']),ledger=program['ledger'],borrowed_rows_returned=trace['borrowed_rows_returned']))
    result=dict(status='SCOPED_SOURCE_ROUTE_OWNER_SCHEDULE',source_helper=462,source_frame=506,body_basis_columns=basis,high_matrix_basis_columns=high_basis,high_matrix_zero_cases=1,dirty_cases=dirty,
                rational_checks=rational_checks,controls=controls(frame,example),examples=traces,example_program_sha256=sha256(json.dumps(example,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                full_primitive_API_admitted=False,P3_closed=False,uniform_compiler_materialized=False,new_kappa=False)
    artifact=HERE/'PROGRAM.json.gz';canonical=json.dumps(example,sort_keys=True,separators=(',',':')).encode()
    if args.write:
        artifact.write_bytes(gzip.compress(canonical,mtime=0));(HERE/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:
        need(gzip.decompress(artifact.read_bytes())==canonical,'literal emitted program receipt')
        need(result==json.loads((HERE/'RESULT.json').read_text()),'deterministic result receipt')
    authenticate();print(json.dumps(result,sort_keys=True,indent=2));print('elapsed_seconds',round(time.monotonic()-start,3),file=sys.stderr)

if __name__=='__main__':main()
