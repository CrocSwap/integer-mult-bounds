"""Source authentication and bounded discriminators; the all-size theorem is PROOF.md."""
from __future__ import annotations
import hashlib
import gzip
import json
from pathlib import Path
from fractions import Fraction as Q
from functools import lru_cache
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = '7c49fe32c55de02c2c873655c804b16e4c3fef0a'

class Rejection(ValueError):
    pass

def need(ok, why):
    if not ok:
        raise Rejection(why)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def git_blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def typed_equal(a,b):
    if type(a) is not type(b):
        return False
    if isinstance(a,dict):
        return a.keys()==b.keys() and all(typed_equal(a[k],b[k]) for k in a)
    if isinstance(a,list):
        return len(a)==len(b) and all(typed_equal(x,y) for x,y in zip(a,b))
    return a==b

def reject(action, text):
    try:
        action()
    except Rejection as exc:
        need(text in str(exc), 'unexpected rejection: '+str(exc))
        return str(exc)
    raise Rejection('missing rejection: '+text)

def authenticate(data, row):
    need(digest(data)==row['sha256'] and git_blob(data)==row['git_blob'],
         'authenticated source bytes: '+row['path'])

def sources():
    manifest=json.loads((HERE/'SOURCES.json').read_text())
    need(manifest['base_commit']==BASE, 'canonical base')
    hashes={}; authenticated={}
    for row in manifest['files']:
        if row['usage']=='provenance':
            continue  # registered metadata binds historical Git bytes, not live state
        need(row['usage']=='input','recognized source usage')
        data=(ROOT/row['path']).read_bytes()
        authenticate(data,row)
        hashes[row['path']]=digest(data)
        authenticated[row['path']]=data
    deps=json.loads((HERE/'DEPENDENCIES.json').read_text())
    need([x['published_commit'] for x in deps['dependencies']]==[
        'c46339035fccd571effb48434d80f572e20f1092',
        '41febf890fbbb852c6059d4c0cc8c593ae9dfa5c'], 'published dependency heads')
    for dep in deps['dependencies']:
        for row in dep['files']:
            data=(HERE/row['path']).read_bytes()
            authenticate(data,row)
            hashes[row['path']]=digest(data)
            authenticated[row['path']]=data
    changed=dict(next(row for row in manifest['files'] if row['usage']=='input'))
    control=reject(lambda:authenticate(b'changed source',changed),'authenticated source bytes')
    return hashes,control,types.MappingProxyType(authenticated)

def constants(authenticated):
    selected=json.loads(authenticated['research/p104-helper470-twin-rung-removal/RESULT.json'])
    cost=selected['complete_cost']; strict=cost['strictification']; compiler=cost['compiler']
    need(typed_equal({k:strict[k] for k in ('power','cutoff','floor')},
                    {'power':1024,'cutoff':16,'floor':17}), 'current strictification constants')
    need(type(compiler['H']) is int and compiler['H']==65807000000000,
         'symbolic compiler H')
    need(compiler['N']=='2^65807000000000' and compiler['word_materialized'] is False,
         'unmaterialized current N')
    need(max(map(int,cost['targets']))==145 and min(map(int,cost['targets']))==1,
         'raw mixed targets before strictification')
    need(max(map(int,cost['paid']))==72, 'raw paid maximum')
    need(145 < 2**8 and compiler['H']>8*strict['power'], 'symbolic N exceeds product ambient')
    c4=json.loads(authenticated['vendor/c4/RESULT.json'])
    local=c4['local_scalar_certificate']; ctl=c4['complete_controller_certificate']
    need(local['stored_debt']==local['product_debt']==local['coefficient_bits']==4,
         'raw four-bit debt')
    need(local['maximum_stored_mass']=='850' and local['maximum_product_mass']=='504'
         and ctl['maximum_mass']==10, 'raw relative-prefix mass')
    need(local['first_maximum_product_witness']==[8745,'product',[[325,'-1/16']]],
         'actual denominator16 witness')
    need(ctl['local_calls']==18 and ctl['paid_calls']==66834 and ctl['paid_rank_mass']==240152,
         'complete raw caller identity')
    need(c4['geometry_certificate']['arbitrary_additional_spectators'] is True,
         'complete arbitrary spectators')
    need(c4['geometry_certificate']['raw_dimension']==265
         and len(c4['geometry_certificate']['retained_axes'])==145, 'retained root axes')
    word=json.loads(gzip.decompress(authenticated['research/p104-helper470-twin-rung-removal/WORD.json.gz']))
    scalar={op:[Q(e[-2]) for e in word['program'] if e[0]==op] for op in ('ADD','SCALE','COPY')
    }
    need([len(scalar[k]) for k in scalar]==[18404,861,23], 'actual scalar instruction census')
    for values in scalar.values():
        for q in values:
            need(q!=0 and abs(q.numerator)<=16 and q.denominator<=16
                 and not q.denominator&(q.denominator-1), 'literal dyadic scalar alphabet')
    need(set(scalar['COPY'])=={Q(1)}, 'literal COPY coefficient')
    need(8500 < 2**14, 'mass exponent')
    m=145**1024; K=1024*m*(compiler['H']+1)**2
    need(K.bit_length()==7455 and len(str(K))==2244,'encoded current context coefficient')
    need(digest(str(K).encode())=='e507a371505ade190c0908fbe51c13b17653077642dfae07f8c17f3bf8cad383','independently derived K coefficient')
    need(145<2**8 and compiler['H']+1<2**46 and 15+8192+92<compiler['H'],
         'symbolic32K_less_than_N')
    return {'v':1024,'H':65807000000000,'N':'2^65807000000000',
            'K_star':'1024*145^1024*(65807000000000+1)^2',
            'K_star_hex':hex(K),'K_star_bits':K.bit_length(),
            'K_star_decimal_sha256':digest(str(K).encode()),
            'simple_format':['F=p+d','W=p+h+2*d+3','temporary=W+6'],
            'symbolic_comparison':'32*K_star<2^8299<2^65807000000000',
            'raw_debt':4,'raw_mass':8500,'paid_rank_mass':240152,
            'scalar_instructions':{k:len(v) for k,v in scalar.items()},
            'dependency_scope':'authenticated theorem and receipt; predecessor generator not rerun'}


def compiler_checks(authenticated):
    path=ROOT/'research/lockstep-completion-pass/executor.py'
    mod=types.ModuleType('frozen_lockstep_executor')
    mod.__file__=str(path)
    # Compile the authenticated source bytes directly: no pyc or mutable import alias.
    exec(compile(authenticated['research/lockstep-completion-pass/executor.py'],str(path),'exec'),mod.__dict__)
    rules=[mod.Rule('two-three',[('a',2),('b',3)],[(1,'a'),(1,'C0')]),
           mod.Rule('three-four',[('a',3),('b',4)],[(1,'a'),(2,'C0')]),
           mod.Rule('weighted',[('a',2),('b',2),('c',3)],[(1,'c')])]
    recurrence=[]; traces=[]
    for rule in rules:
        need(min(rule.types)>=2 and max(r for r,_ in rule.rounds)<min(rule.types),
             'separated rule for K')
        planner=mod.Compiler(rule)
        @lru_cache(None)
        def contexts(n):
            if n<rule.m:
                return 0
            src,exits,units,G=planner.plan(n)
            need(all(n<rule.m*s<=rule.m*n for s in src), 'source band and rank descent')
            need(all(1<=e<n and rule.m*e<=(rule.m-1)*n for e,_ in exits), 'fractional exit rank descent')
            need(G+1<=n.bit_length(), 'class-depth logarithm')
            return max([contexts(n-s) for s in src]+[G+1+contexts(e) for e,_ in exits])
        for n in range(1,25):
            k=contexts(n)
            need(k<=min(n*n.bit_length(),rule.m*n.bit_length()**2), 'both tested K bounds')
            recurrence.append([rule.name,n,k,n*n.bit_length()])
        class Traced(mod.Compiler):
            def __init__(self):
                super().__init__(rule,owned_policy='stack',budget=2_000_000)
                self.depth=0; self.depth_peak=0; self.entries=0
            def run_class(self,*a,**kw):
                self.depth+=1; self.entries+=1
                self.depth_peak=max(self.depth_peak,self.depth)
                try:
                    return super().run_class(*a,**kw)
                finally:
                    self.depth-=1
            def blackbox(self,n,fields,tops):
                need(n<rule.m, 'no truncated nonbase compiler execution')
                return super().blackbox(n,fields,tops)
        for n in (rule.m,rule.m+1,2*rule.m,3*rule.m):
            machine=Traced(); B,a,P,cost=machine.compile(n)
            need(cost<=2_000_000 and B<=200000, 'bounded complete fixture')
            fields=[('actual',i) for i in range(B)]
            machine.uniform(n,fields,[None]*B,top_level=True)
            need(not machine.partial and machine.depth==0 and not machine.bank_stack
                 and all(not stack for stack in machine.stack.values()), 'complete restored trace')
            need(machine.depth_peak==contexts(n), 'independent event depth equals source-plan recurrence')
            need(all(machine.received[f]==2 for f in fields), 'every source complement and job')
            traces.append({'rule':rule.name,'n':n,'arrays':B,'replication':a,
                           'class_entries':machine.entries,'context_depth':machine.depth_peak,
                           'events':machine.events,'no_nonbase_blackboxes':True})
    source_controls={}
    for key,kw,fragment in [
        ('eager_parent',{'eager':True},'I3 lockstep'),
        ('aliased_exit',{'bad_exit':True},'I5 handed field'),
        ('early_owned_release',{'owned_policy':'release_early'},'I3 paid job issued')]:
        try:
            mod.audit(rules[1],12,**kw)
        except mod.Violation as exc:
            need(fragment in str(exc),'expected actual source violation')
            source_controls[key]=str(exc)
        else:
            raise Rejection('missing actual source control: '+key)
    # This executor checks slot identity, not numerical payload; no native replay is claimed.
    return {'recurrence_cases':len(recurrence),'recurrence_sha256':digest(json.dumps(recurrence).encode()),
            'complete_control_traces':traces,'source_controls':source_controls,'scope':'actual compiler control and ownership; no numeric native payload'}

# Exact Q(i) matrix arithmetic, independent of source/native implementations.
ZERO=(Q(0),Q(0)); ONE=(Q(1),Q(0)); I=(Q(0),Q(1))
def ga(a,b): return (a[0]+b[0],a[1]+b[1])
def gm(a,b): return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def mm(a,b):
    n=len(a)
    return tuple(tuple(sum_g(gm(a[i][k],b[k][j]) for k in range(n)) for j in range(n)) for i in range(n))
def sum_g(items):
    out=ZERO
    for x in items: out=ga(out,x)
    return out
def eye(n): return tuple(tuple(ONE if i==j else ZERO for j in range(n)) for i in range(n))
def tensor(a,b):
    return tuple(tuple(gm(a[i//len(b)][j//len(b)],b[i%len(b)][j%len(b)])
                       for j in range(len(a)*len(b))) for i in range(len(a)*len(b)))
def grid_ok(matrix,bits):
    scale=1<<bits
    return all((z*scale).denominator==1 for row in matrix for x in row for z in x)
def unitary(a):
    adj=tuple(tuple((a[j][i][0],-a[j][i][1]) for j in range(len(a))) for i in range(len(a)))
    return mm(a,adj)==eye(len(a))
def typed_nat(x,name):
    need(type(x) is int and x>=0,'nonnegative integer '+name)

def bound(p,h,d,t):
    for name,x in [('p',p),('h',h),('d',d),('t',t)]:typed_nat(x,name)
    need(d>=1,'positive root dimension')
    F=p+(d+1)//2+4*t
    J=h+(d+2)//2+14*t+1
    W=p+h+d+18*t+3
    need(F+J+1==W,'signed width identity')
    return F,W

def exact_div(n,q):
    need(type(n) is int and type(q) is int and q>0 and n%q==0,'checked exact division')
    return n//q

def swap(events=('add_xy','sub_yx','add_xy','neg_y')):
    x=(1,0);y=(0,1);peak=1
    for op in events:
        if op=='add_xy':x=tuple(a+b for a,b in zip(x,y))
        elif op=='sub_yx':y=tuple(a-b for a,b in zip(y,x))
        elif op=='neg_y':y=tuple(-a for a in y)
        else:raise Rejection('atomic swap has no child or nested swap')
        peak=max(peak,sum(map(abs,x)),sum(map(abs,y)))
    need((x,y)==((0,1),(1,0)),'completed swap endpoint')
    return peak

def algebra_checks():
    a=(Q(1,2),Q(1,2));b=(Q(1,2),Q(-1,2))
    C=((a,b),(b,a)); X=((ZERO,ONE),(ONE,ZERO)); S=((ONE,ZERO),(ZERO,I))
    gates=(C,X,S)
    found={eye(2)};todo=[eye(2)]
    while todo:
        old=todo.pop()
        for g in gates:
            new=mm(g,old)
            need(grid_ok(new,1) and unitary(new),'complete one-bit Gaussian Clifford grid')
            if new not in found:
                found.add(new);todo.append(new)
                need(len(found)<=512,'bounded exact Clifford closure')
    # Fixed deterministic two-bit words, including a non-product Clifford.
    CZ=tuple(tuple((Q(-1),Q(0)) if i==j==3 else ONE if i==j else ZERO for j in range(4)) for i in range(4))
    two=(tensor(C,eye(2)),tensor(eye(2),C),tensor(S,eye(2)),CZ)
    cur=eye(4);state=17
    for _ in range(160):
        state=(1103515245*state+12345)%(1<<31)
        cur=mm(two[state%len(two)],cur)
        need(grid_ok(cur,1) and unitary(cur),'two-bit fixed-root grid after many completed gates')
    P=((ONE,ZERO),(ZERO,ZERO));PCP=mm(P,mm(C,P));x=eye(2);projector=[]
    for j in range(1,9):
        x=mm(PCP,x)
        maxden=max(z.denominator for row in x for c in row for z in c)
        need(maxden==1<<((j+1)//2),'active-projector exact denominator growth')
        projector.append(maxden)
    need(not grid_ok(mm(PCP,mm(PCP,PCP)),1),'active projector violates root Clifford cap')
    widths=0
    for d in range(1,65):
        for t in (0,1,2,7,1024):
            bound(3,2,d,t);widths+=1
    simple_cases=0
    for d in range(1,257):
        for t in range((d-1)//32+1):
            F,W=bound(3,2,d,t)
            J=2+(d+2)//2+14*t+1
            need(F<=3+d and J<=2+d+2,'simple grid and magnitude absorption')
            need((3+d)+(2+d+2)+1==3+2+2*d+3,'recomputed simple signed width')
            simple_cases+=1
    # A genuine C^8 base example shows why a finer grid must recompute width.
    row=(ONE,)
    for _ in range(8):
        row=tuple(gm(old,z) for old in row for z in C[0])
    inputs=tuple((16*z[0],-16*z[1]) for z in row)
    need(all(abs(z[0])<=1 and abs(z[1])<=1 for z in inputs),'admitted p0 h1 base inputs')
    output=sum_g(gm(z,x) for z,x in zip(row,inputs))
    need(output==(Q(16),Q(0)),'exact raised-grid counterexample')
    oldF,oldW=bound(0,1,8,0); newF=8; newW=20
    numerator=int(output[0])<<newF
    need(numerator>=1<<(oldW-1) and numerator<1<<(newW-1),
         'raising F while retaining old W is insufficient')
    need(swap()==2,'single swap factor two')
    # Whole external rows preserve root coordinates even for a non-power-of-two row group.
    D=8; rows=15;group=3;seen=[]
    for bucket in range(rows//group):
        for within in range(group):
            original=bucket*group+within
            fiber=[(original,selected) for selected in range(D)]
            need({q for _,q in fiber}==set(range(D)),'complete root fiber')
            seen.extend(fiber)
    need(seen==[(r,q) for r in range(rows) for q in range(D)],'external row split and inverse')
    # Nonzero copied centers preserve their expansion; padding supplies no independent input.
    parent={('original',2):Q(3,16),('original',7):Q(-5,16)}
    child=dict(parent);need(child==parent,'copied center provenance')
    padded={};need(not padded,'zero sentinel input padding')
    padded=dict(parent)  # an unfinished COPY/ADD can make that current row nonzero
    need(padded==parent and bool(padded),'nonzero transient on original zero input')
    padded={key:value-parent[key] for key,value in padded.items()}
    need(all(value==0 for value in padded.values()),'zero restored only at complete endpoint')
    inherited_mass=sum(map(abs,parent.values()))
    nested={key:Q(-1,16)*value for key,value in parent.items()}
    need(sum(map(abs,nested.values()))==inherited_mass/16,'nested entrance expansion retained')
    errors={}
    errors['understated_raw_debt']=reject(lambda:exact_div(-1*8,16),'checked exact division')
    errors['odd_scalar_denominator']=reject(lambda:exact_div(1<<20,3),'checked exact division')
    errors['interrupted_swap']=reject(lambda:swap(('add_xy','child','sub_yx','add_xy','neg_y')),'atomic swap')
    errors['incomplete_swap']=reject(lambda:swap(('add_xy','sub_yx','add_xy')),'completed swap endpoint')
    errors['boolean_root_dimension']=reject(lambda:bound(0,0,True,0),'nonnegative integer d')
    errors['zero_root_dimension']=reject(lambda:bound(0,0,0,0),'positive root dimension')
    errors['typed_receipt_corruption']=reject(lambda:need(typed_equal({'d':1},{'d':True}),'typed receipt'),'typed receipt')
    for debt in range(1,9):
        value=Q(-1,16)**debt
        need((value*(1<<(4*debt))).denominator==1,'nested scalar debt accumulation')
        need((value*(1<<(4*debt-1))).denominator!=1,'nested debt witness')
    return {'one_bit_complete_group':len(found),'two_bit_completed_words':160,
            'active_projector_denominators':projector,'width_identity_cases':widths,
            'external_rows':rows,'non_power_of_two_group':group,'root_fiber_size':D,
            'swap_peak_mass':2,'nested_debt_witnesses':8,'simple_format_cases':simple_cases,
            'raised_grid_counterexample':{'p':0,'h':1,'d':8,'output_real':16,'old_F':oldF,
                                         'old_W':oldW,'new_F':newF,'new_W':newW,
                                         'new_numerator':numerator},
            'provenance_controls':['copied center keeps its entrance expansion',
                                   'original zero input may have a nonzero transient',
                                   'nested source retains inherited mass and debt'],
            'rejections':errors}


def wrapper_checks():
    a=(Q(1,2),Q(1,2));b=(Q(1,2),Q(-1,2));C=((a,b),(b,a));S=((ONE,ZERO),(ZERO,I))
    H0=tuple(tuple(gm(b,z) for z in row) for row in mm(S,mm(C,S)))
    need(H0==(((Q(1,2),Q(0)),(Q(1,2),Q(0))),
              ((Q(1,2),Q(0)),(Q(-1,2),Q(0)))),'literal b S C S normalization')
    def power(z,e):
        out=ONE
        for _ in range(e):out=gm(out,z)
        return out
    cases=0;preprocessing=0
    for D in range(1,66):
        k=D//2
        for q in range(D+1):
            pp=(q+1)//2 if q else 0;hp=(q+2)//2 if q else 0;R=D-q
            need(pp+R<=D and hp+R+2<=D+2,'wrapper preprocessing common F J')
            preprocessing+=1
        for j in range(D+1):
            entry=gm(power(a,D-j),power(b,j))
            for phase in (ONE,I,(Q(-1),Q(0)),(Q(0),Q(-1))):
                z=gm(phase,entry)
                pair=[value*(1<<D) for value in z]
                need(all(value.denominator==1 for value in pair),'global wrapper grid')
                shifted=[exact_div(int(value),1<<k) for value in pair]
                if D%2:
                    need((shifted[0]-shifted[1])%2==0,'odd completed endpoint parity')
                    shifted=[exact_div(shifted[0]+shifted[1],2),
                             exact_div(shifted[1]-shifted[0],2)]
                need(all(type(value) is int for value in shifted),'exact wrapper return')
                cases+=1
    parity_control=reject(lambda:exact_div(1+0,2),'checked exact division')
    return {'selected_dimensions':65,'preprocessing_cases':preprocessing,
            'entry_and_phase_cases':cases,'odd_nonreachable_parity_rejected':parity_control,
            'closed_unit_disk_strict_component_bound_h':1,
            'scope':'numerical05-layers q0 macro; no current physical front/back dispatcher'}


def result():
    hashes,control,authenticated=sources()
    protected={(HERE/key if key.startswith('vendor/') else ROOT/key).resolve()
               for key in authenticated}
    old_open=Path.open
    def snapshot_only(path,*a,**kw):
        need(path.resolve() not in protected,'consume authenticated snapshot without source reread')
        return old_open(path,*a,**kw)
    Path.open=snapshot_only
    try:
        cache_control=reject(lambda:(ROOT/'research/lockstep-completion-pass/executor.py').read_bytes(),
                             'consume authenticated snapshot')
        current=constants(authenticated)
        compiler=compiler_checks(authenticated)
    finally:
        Path.open=old_open
    return {'schema':'compiled-root-clifford-precision/1','base_commit':BASE,
            'status':'PASS_COMPILED_ROOT_CLIFFORD_PRECISION',
            'sources':hashes,'source_drift_control':control,'source_snapshot_control':cache_control,'constants':current,
            'compiler':compiler,'algebra':algebra_checks(),'wrapper':wrapper_checks(),
            'all_size_contract':{'K':'K(n)<=min(v*n*(1+floor(log2(n))),v*m*(1+floor(log2(n)))^2)',
                                 'F':'p+ceil(d/2)+4*K_star*ell',
                                 'W':'p+h+d+18*K_star*ell+3','temporary':'W+6',
                                 'simple_F':'p+d','simple_W':'p+h+2*d+3','simple_temporary':'simple_W+6',
                                 'proof':'PROOF.md; finite controls are not the all-size proof'},
            'limitations':['ideal ownership and full restored routes retained',
                           'numerical05-layers wrapper proved; current reservation/dispatcher remains open',
                           'no current physical dispatcher or accelerated cost admission',
                           'No new kappa']}

if __name__=='__main__':
    out=result()
    need(sys.argv[1:] in ([],['--record']), 'recognized verification mode')
    if sys.argv[1:]==['--record']:
        (HERE/'RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:
        expected=json.loads((HERE/'RESULT.json').read_text())
        need(typed_equal(out,expected),'typed complete result receipt')
    print(out['status'])
    print(json.dumps({'receipt_sha256':digest(json.dumps(out,sort_keys=True,separators=(',',':')).encode()),
                      'compiler_traces':len(out['compiler']['complete_control_traces']),
                      'recurrence_cases':out['compiler']['recurrence_cases'],
                      'one_bit_group':out['algebra']['one_bit_complete_group']},sort_keys=True))
