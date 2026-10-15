"""Selected rank42 high-dependent coefficients and opaque stream tests."""
from dataclasses import replace
from hashlib import sha256
from itertools import product
import json
from controlled_normalizer import (ParentPrefix,prepare,schedule,coefficient,execute_addresses,
                                    child_weights,eye,need,GoodWeightChain,prepare_good_chain)
from controlled_stream import Meter,Tape,controlled_add


def prefix_fixture(q,width,t,f=1,weighted=False,active=0):
    """g=B_t Pi for actual P0=diag(0_22,I42), B_t on axes0,42."""
    m=q**width;c=q*t%m;block=eye(64)
    need(0<=active<42,"active chart coordinate")
    for i,j,value in ((active,active,1),(active,42,1),(42,active,c),(42,42,1+c)):block[i][j]=value%m
    axes=list(range(22,64))+list(range(22));g=[[0]*64 for _ in range(64)]
    for i in range(64):
        for j in range(64):g[i][axes[j]]=block[i][j]
    weights=tuple((1+i%(q-1)+q*(3*i+2))%m if weighted else 1 for i in range(64*f))
    return ParentPrefix(q,width,tuple(tuple(x%q for x in row) for row in g),
                        tuple(tuple(x//q for x in row) for row in g),weights,f)


def evaluator(parent,low_only=False,zero_arm=False):
    prepared=prepare(parent,list(range(22,64)),low_only)
    row,col=(21,0) if zero_arm else (63,42)
    slot=("cross",64+row,col,row*64+col,0,1)
    return coefficient(prepared,slot),prepared.arithmetic


def dense_fixture(q,width,f,seed):
    """Independent block identity for a dense good chart with full high entries."""
    modulus=q**width;r,s=42,22
    b=[[(i*i+3*i*j+7*j+seed)%modulus for j in range(s)] for i in range(r)]
    c=[[q*(i*i+5*i*j+3*j+seed)%modulus for j in range(r)] for i in range(s)]
    bc=[[sum(b[i][k]*c[k][j] for k in range(s))%modulus for j in range(r)] for i in range(r)]
    cb=[[sum(c[i][k]*b[k][j] for k in range(r))%modulus for j in range(s)] for i in range(s)]
    top=[[int(i==j)+bc[i][j] for j in range(r)]+[-x for x in b[i]] for i in range(r)]
    bottom=[[sum(c[i][k]*top[k][j] for k in range(r)) for j in range(r+s)] for i in range(s)]
    oracle=[[x%modulus for x in row] for row in top+bottom]
    block=[row+b[i] for i,row in enumerate(eye(r))]+[
        c[i]+[(int(i==j)+cb[i][j])%modulus for j in range(s)] for i in range(s)]
    axes=list(range(22,64))+list(range(22));g=[[0]*64 for _ in range(64)]
    for i in range(64):
        for j in range(64):g[i][axes[j]]=block[i][j]
    weights=prefix_fixture(q,width,0,f,True).ancestor_weights
    prefix=ParentPrefix(q,width,tuple(tuple(x%q for x in row) for row in g),
                        tuple(tuple(x//q for x in row) for row in g),weights,f)
    return prefix,oracle


def direct_residual(prepared,head,tail):
    """Direct D_P formula; does not read emitted factors or cross shear."""
    p,a,f,m=prepared.projector,prepared.weights,prepared.f,prepared.modulus
    n=prepared.n;aihead=[x*pow(unit,-1,m)%m for x,unit in zip(head,a)]
    reverse=tail[::-1];newh=[0]*len(head);newr=[0]*len(head)
    for i in range(n):
        for j in range(f):
            ph=sum(p[i][k]*aihead[k*f+j] for k in range(n))%m
            pd=sum(p[i][k]*reverse[k*f+j] for k in range(n))%m
            idx=i*f+j
            newh[idx]=(head[idx]+a[idx]*(pd-ph))%m
            newr[idx]=(reverse[idx]+ph-pd)%m
    return newh,newr[::-1]


def full_operator_check(form):
    need(form.f==1,"basis check dimension")
    matrix=eye(2*form.n);before,after=schedule(form.n,form.rank,1)
    def add_slots(slots):
        for slot in slots:
            _,target,source,_,_,_=slot;c=coefficient(form,slot)
            matrix[target]=[(x+c*y)%form.modulus for x,y in zip(matrix[target],matrix[source])]
    add_slots(before)
    for i,weight in enumerate(child_weights(form)):
        j=2*form.n-1-i;a,b=matrix[i][:],matrix[j][:]
        matrix[i]=[weight*x%form.modulus for x in b]
        inverse=pow(weight,-1,form.modulus)
        matrix[j]=[inverse*x%form.modulus for x in a]
    add_slots(after)
    for column in range(2*form.n):
        h,d=direct_residual(form,[int(i==column) for i in range(form.n)],
                           [int(form.n+i==column) for i in range(form.n)])
        need([row[column] for row in matrix]==h+d,"every column of the dense weighted operator")
    return sha256(json.dumps(matrix,separators=(",",":")).encode()).hexdigest()


def address_checks():
    cases=0;schedules=set()
    for q,width in ((5,1),(5,2),(3,3)):
        for t in range(q**(width-1)):
            for f in (1,2,3):
                prefix=prefix_fixture(q,width,t,f,True);form=prepare(prefix,list(range(22,64)))
                c=q*t%form.modulus;p=(1+c)%form.modulus
                expected=[[0]*64 for _ in range(64)]
                expected[21][0]=c;expected[63][42]=pow(p,-1,form.modulus)
                need(form.cross==expected,"nonconstant selected K formula")
                need(form.pivots==(p,)+(1,)*41,"full parent pivot formula")
                before,after=schedule(64,42,f)
                need(len(before)==len(after)==7666*f,"common zero-padded adapter count")
                schedules.add(sha256(json.dumps((before,after)).encode()).hexdigest())
                head=[(7*i*i+3*i+1)%form.modulus for i in range(64*f)]
                tail=[(3*i*i+5*i+2)%form.modulus for i in range(64*f)]
                need(execute_addresses(form,head,tail)==direct_residual(form,head,tail),"full weighted normalizer endpoint")
                need(child_weights(form)==tuple(form.weights[k*f+j]*form.pivots[k]%form.modulus
                     for k in range(42) for j in range(f)),"contiguous child weight order")
                cases+=1
    dense=0;operator_hash=None
    for q,width,seed in ((5,2,1),(7,2,3)):
        for f in (1,2,3):
            prefix,oracle=dense_fixture(q,width,f,seed)
            form=prepare(prefix,list(range(22,64)))
            need(form.projector==oracle,"independent dense block-projector formula")
            head=[(11*i+7)%form.modulus for i in range(64*f)]
            tail=[(i*i+3*i)%form.modulus for i in range(64*f)]
            need(execute_addresses(form,head,tail)==direct_residual(form,head,tail),"dense normalizer endpoint")
            if (q,width,f)==(5,2,1):operator_hash=full_operator_check(form)
            before,after=schedule(64,42,f)
            schedules.add(sha256(json.dumps((before,after)).encode()).hexdigest())
            dense+=1
    need(len(schedules)==3,"schedule independent of high matrix and ancestor weights")
    prefix=prefix_fixture(5,2,1);form=prepare(prefix,list(range(22,64)))
    low=prepare(prefix,list(range(22,64)),low_only=True)
    head=[int(i==42) for i in range(64)];tail=[0]*64
    right=execute_addresses(form,head,tail)
    wrong=execute_addresses(replace(form,cross=low.cross),head,tail)
    need((right[0][0],wrong[0][0],right[1][21],wrong[1][21])==(1,6,20,0),"full endpoint low-only K control")
    return {"address_cases":cases,"dense_address_cases":dense,"low_only_K_endpoint_control":"REJECT",
            "full_dense_operator_columns":128,"full_dense_operator_sha256":operator_hash,
            "common_schedule_adds_per_f":15332,"weighted_children":1,
            "child_width_per_f":42,"ordinary_adapter_calls":0}


def payload_case(q,width,weighted=False,zero_arm=False):
    parents=tuple(prefix_fixture(q,width,t,weighted=weighted) for t in range(q**(width-1)))
    need(len({p.low for p in parents})==1,"one complete low chart")
    before=parents;modulus=q**width;unused,middle,suffix=3,2,17
    size=len(parents)*unused*modulus*middle*modulus
    raw=[(index>>(bit%suffix))&1 for index in range(size) for bit in range(suffix)]
    meter=Meter();actual=controlled_add(Tape(meter,raw),parents,unused,modulus,middle,suffix,
                                       lambda p:evaluator(p,zero_arm=zero_arm))
    expected=[None]*len(raw)
    expected_coefficients=[]
    for h,parent in enumerate(parents):
        c=q*h%modulus
        value=(c if zero_arm else pow(1+c,-1,modulus))
        value=value*pow(parent.ancestor_weights[0 if zero_arm else 42],-1,modulus)%modulus
        expected_coefficients.append(value)
        for stock,x,z,y in product(range(unused),range(modulus),range(middle),range(modulus)):
            src=((((h*unused+stock)*modulus+x)*middle+z)*modulus+y)*suffix
            dst=((((h*unused+stock)*modulus+x)*middle+z)*modulus+(y+value*x)%modulus)*suffix
            expected[dst:dst+suffix]=raw[src:src+suffix]
    need(actual.bits==expected,"opaque parent-controlled payload permutation")
    need(parents==before and meter.ordinary_calls==0,"unchanged parents and zero ordinary calls")
    need(meter.preparation_calls==2*len(parents),"two explicit preparations per header")
    need(meter.payload_reads+meter.payload_writes+meter.head_moves+meter.scratch_erases<=16*len(raw),"linear measured payload movement")
    if not zero_arm:need(actual.bits!=raw,"width-one and higher atom shifts remain nontrivial")
    control=None
    if width>1 and not zero_arm:
        wrong=controlled_add(Tape(Meter(),raw),parents,unused,modulus,middle,suffix,
                             lambda p:evaluator(p,low_only=True))
        need(wrong.bits!=expected,"low-only descriptor must move payload incorrectly")
        control="REJECT"
    return {"q":q,"width":width,"weighted":weighted,"zero_arm":zero_arm,
            "parent_high_parameters":len(parents),"payload_bits":len(raw),
            "coefficients":expected_coefficients,"ordinary_calls":meter.ordinary_calls,
            "prefix_cells_read":meter.prefix_cells,"preparation_calls":meter.preparation_calls,
            "ring_operations":dict(meter.preparation),"low_only_control":control}


def nested_payload():
    q,width,modulus=5,2,25;axes=tuple(range(22,64));root_unit=1
    # Root n=256 -> child168; next f=2 -> child84; current f=1 fits64.
    older=prefix_fixture(q,width,1,f=4,active=10)
    nearer=prefix_fixture(q,width,2,f=2,active=21)
    controls=tuple(GoodWeightChain(prefix_fixture(q,width,t),((older,axes),(nearer,axes)),root_unit)
                   for t in range(5))
    unused,middle,suffix=3,2,17
    size=5*unused*modulus*middle*modulus
    raw=[(index>>bit)&1 for index in range(size) for bit in range(suffix)]
    def evaluate(control,low_ancestors=False):
        form=prepare_good_chain(control,axes,low_only_ancestors=low_ancestors)
        value=coefficient(form,("cross",127,42,63*64+42,0,1))
        return value,form.arithmetic
    meter=Meter();actual=controlled_add(Tape(meter,raw),controls,unused,modulus,middle,suffix,evaluate)
    # Independent two-level index substitution:42//4=10,42//2=21.
    expected_weight=root_unit*6*11%25
    need(expected_weight%5!=0,"nested unit weight")
    expected=[None]*len(raw);coefficients=[]
    for t in range(5):
        c=pow((1+5*t)*expected_weight,-1,25);coefficients.append(c)
        for stock,x,z,y in product(range(unused),range(25),range(middle),range(25)):
            src=((((t*unused+stock)*25+x)*middle+z)*25+y)*suffix
            dst=((((t*unused+stock)*25+x)*middle+z)*25+(y+c*x)%25)*suffix
            expected[dst:dst+suffix]=raw[src:src+suffix]
    need(actual.bits==expected,"nested full-ancestor payload operation")
    wrong=controlled_add(Tape(Meter(),raw),controls,unused,modulus,middle,suffix,
                         lambda p:evaluate(p,True))
    need(wrong.bits!=expected,"low-only ancestor descriptor control")
    # A changed ancestor divisor must not pass the retained coarse-width rule.
    bad_nearer=replace(nearer,atom_columns=4,ancestor_weights=(1,)*256)
    bad_control=replace(controls[0],ancestors=((older,axes),(bad_nearer,axes)))
    try:prepare_good_chain(bad_control,axes)
    except ValueError as error:
        need(str(error)=="successive coarse child width","specific ancestor-width rejection")
    else:raise ValueError("wrong ancestor divisor accepted")
    need(meter.ordinary_calls==0 and meter.preparation_calls==10,"nested preparation/call bill")
    return {"depth":2,"ancestor_atom_columns":[4,2],"current_atom_columns":1,
            "weight_at_42":expected_weight,"coefficients":coefficients,"payload_bits":len(raw),
            "ordinary_calls":0,"preparation_calls":meter.preparation_calls,
            "prefix_cells_read":meter.prefix_cells,"ring_operations":dict(meter.preparation),
            "low_only_ancestor_control":"REJECT","ancestor_width_control":"REJECT"}


def build_result():
    out=address_checks()
    out["payload_cases"]=[payload_case(5,1),payload_case(5,2),payload_case(5,2,True),payload_case(5,2,zero_arm=True)]
    out["nested_payload"]=nested_payload()
    out["status"]="PASS_SELECTED_CONTROLLED_STREAMS"
    return out


if __name__=="__main__":print(json.dumps(build_result(),indent=2))
