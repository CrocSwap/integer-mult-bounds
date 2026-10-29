"""Read-only source binding and finite-state/error controls. Standard library."""
import gzip,hashlib,importlib.util,itertools,json,random,shutil,subprocess,sys,tempfile,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import lattice as l
import bits
import circuit
P=Path(__file__).resolve().parent
def need(x,m):
    if not x:raise ValueError(m)
def check():
    t=time.monotonic(); manifest=json.loads((P/'FROZEN-SOURCES.json').read_text())
    for r in manifest:need(hashlib.sha256((P/r['path']).read_bytes()).hexdigest()==r['sha256'],'source hash '+r['path'])
    item=json.loads((P/'MACRO.json').read_text());rec=item['recipe']
    need(item in json.loads((P/'frozen/RECIPES.json').read_text())['items'],'macro copied from pinned recipe')
    need(item['entrance']==[]and item['terminal']==[388,74,40,26,1]and rec['rank']==5,'actual macro interface')
    spec=importlib.util.spec_from_file_location('credited_phase_oracle',P/'frozen/exact_phase.py')
    oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
    oracle.check_item(item) # Credited PR3987 direct canonical-frame versus recipe, all512 columns.
    for name in ['base','extra']:
        w=json.loads(gzip.decompress((P/'frozen'/('WORD-'+name+'.json.gz')).read_bytes()))
        need(w['helper_final']['277']==item['terminal']and w['start_extra'].get('277',[])==[],'actual helper277 binding')
    half_cases=0
    for b in [2,3,4]:
        n=1<<b
        for a,c,d,y in itertools.product(range(n),range(n),range(2*n),range(n)):
            for sub in [False,True]:
                out,dr=l.half_accumulate(y,a,c,d,b,sub)
                expected=(y+(l.signed(a,b)+(-1 if sub else 1)*l.signed(c,b))//2)%n
                need((out,dr)==(expected,d),'half accumulator arithmetic/dirty identity')
                need(l.half_accumulate(out,a,c,dr,b,sub,True)==(y,d),'half accumulator inverse')
                half_cases+=1
    pair_cases=0
    for b in [2,3]:
        n=1<<b
        for a,c,e,f,d in itertools.product(range(n),range(n),range(n),range(n),range(2*n)):
            x,y,dr=l.pair((a,c),(e,f),d,b)
            need(dr==d,'pair dirty return')
            need(l.pair(x,y,dr,b,True)==((a,c),(e,f),d),'full finite-state pair inverse')
            pair_cases+=1
    bit_half_cases=0;bit_pair_cases=0
    for b in [2,3]:
        n=1<<b
        for a,c,d,y in itertools.product(range(n),range(n),range(2*n),range(n)):
            for sub in [False,True]:
                z=bits.half(y,a,c,d,b,sub)
                need(z[:2]==l.half_accumulate(y,a,c,d,b,sub),'literal bit half circuit')
                need(z[2]==3*b*b+9*b+4,'literal bit half gate bill')
                bit_half_cases+=1
    for a,c,e,f,d in itertools.product(range(4),range(4),range(4),range(4),range(8)):
        z=bits.pair((a,c),(e,f),d,2)
        need(z[:3]==l.pair((a,c),(e,f),d,2)and z[3]==90,'literal bit pair')
        need(bits.pair(z[0],z[1],z[2],2,True)[:3]==((a,c),(e,f),d),'bit pair inverse')
        clean=bits.pair((a,c),(e,f),0,2,clean=True)
        need(clean[:3]==l.pair((a,c),(e,f),0,2)and clean[3]==76,'constructed clean comparison')
        bit_pair_cases+=1
    ladder_cases=0
    for n in range(3,8):
        g=(tuple((i,1)for i in range(n)),n);low=circuit.lower(g,2*n-1)
        need(len(low)==4*n-8,'Barenco dirty-ladder count')
        for state in range(1<<(2*n-1)):
            need(circuit.apply(state,low)==circuit.apply(state,[g]),'dirty-ladder full state equality')
            ladder_cases+=1
    elementary_cases=0
    for b in [1,2]:
        gates=circuit.pair_gates(b);low=[x for g in gates for x in circuit.lower(g,5*b+1)]
        need(all(len(cs)<=2 and all(v==1 for c,v in cs)for cs,t in low),'literal X/CNOT/Toffoli alphabet')
        need(len(low)==sum(circuit.bill(gates)[k]for k in ['X','CNOT','Toffoli']),'elementary bill exact')
        mask=(1<<b)-1
        for state in range(1<<(5*b+1)):
            x=(state&mask,(state>>b)&mask);y=((state>>(2*b))&mask,(state>>(3*b))&mask);d=state>>(4*b)
            a,z,dd=l.pair(x,y,d,b)
            expected=a[0]|(a[1]<<b)|(z[0]<<(2*b))|(z[1]<<(3*b))|(dd<<(4*b))
            need(circuit.apply(state,low)==expected,'complete bounded-fanin pair and internal borrowed-bit restoration')
            elementary_cases+=1
    # Defect-free state permutation must not be mistaken for a linear map.
    b=20;n=1<<b;z=[(0,0)]*512;z[0]=(1,0)
    q,_=l.macro(z,7,b,rec);z2=[(2*a,2*c)for a,c in z];q2,_=l.macro(z2,7,b,rec)
    nonlinear=[(i,(l.signed(a,b)-2*l.signed(c,b),l.signed(e,b)-2*l.signed(f,b)))for i,((a,e),(c,f))in enumerate(zip(q2,q))if ((a-2*c)%n,(e-2*f)%n)!=(0,0)]
    need(nonlinear,'rank5 nonlinear witness must exist')
    # Actual dirty-helper increment: Q(h+s)-Q(h) differs from Q(s), with h=s=e0.
    need(any(v!=(0,0)for _,v in nonlinear),'interleaved helper additivity failure')
    rng=random.Random(3994);max_error_squared=0;full_cases=0
    for k in range(24):
        signed=[(rng.randrange(-60,61),rng.randrange(-60,61))for _ in range(512)]
        v=[(a%n,c%n)for a,c in signed];dirty=rng.randrange(2*n)
        out,dr=l.macro(v,dirty,b,rec)
        need(dr==dirty and l.macro(out,dr,b,rec,True)==(v,dirty),'full rank5 inverse and dirty identity')
        need(l.macro(v,dirty^1,b,rec)[0]==out,'scratch independence')
        exact=l.exact_macro(signed,rec)
        err=sum((32*l.signed(a,b)-c)**2+(32*l.signed(e,b)-f)**2 for (a,e),(c,f)in zip(out,exact))
        need(err<=80**2*32**2,'completed rank5 absolute bound')
        max_error_squared=max(max_error_squared,err);full_cases+=1
    # Mutants exercise the claimed new implementation, not a hash predicate.
    need(l.half_accumulate(0,1,0,1,3,omit_carry=True)!=(0,1),'omitted parity correction rejected')
    orig=bits.parity_decrement
    try:
        bits.parity_decrement=lambda y,a,c,d,b,reverse=False:(y,2*b)
        need(bits.half(0,1,0,1,3)[:2]!=(0,1),'literal parity omission rejected')
    finally:bits.parity_decrement=orig
    orig=bits.add
    try:
        bits.add=lambda y,x,b,width=None,extend=False,inverse=False:orig(y,x,b,width,False,inverse)
        need(bits.half(0,7,0,0,3)[:2]!=(7,0),'missing signed-extension rejected')
    finally:bits.add=orig
    orig=bits.negate
    try:
        bits.negate=lambda x,b:(x,2*b)
        need(bits.pair((1,0),(0,1),0,3)[:3]!=l.pair((1,0),(0,1),0,3),'quarterturn phase omission rejected')
    finally:bits.negate=orig
    g=(((0,1),(1,1),(2,1)),3);low=circuit.lower(g,5)
    need(any(circuit.apply(s,low[:-1])!=circuit.apply(s,[g])for s in range(32)),'omitted final dirty-ladder uncompute rejected')
    # Destructive component-flooring of exact C followed by exact C* and floor.
    def destructive(x,y,sign):
        a,b=x;c,d=y
        return ((a-sign*b+c+sign*d)//2,(b+sign*a+d-sign*c)//2),((c-sign*d+a+sign*b)//2,(d+sign*c+b-sign*a)//2)
    naive=destructive(*destructive((1,0),(0,0),1),-1)
    need(naive!=((1,0),(0,0)),'destructive rounding inverse counterexample')
    bills={s:l.routing_bill(rec[s])for s in ['left','right']}
    result={'half_exhaustive_cases':half_cases,'pair_exhaustive_cases':pair_cases,'literal_bit_half_cases':bit_half_cases,'literal_bit_pair_cases':bit_pair_cases,'credited_exact_canonical_recipe_columns':512,'rank5_full_cases':full_cases,'rank5_max_error_squared_numerator_over_1024':max_error_squared,'nonlinear_witness_input':'h=s=e0 real one grid unit','nonlinear_witness_first':nonlinear[:8],'nonlinear_nonzero_coordinates':len(nonlinear),'naive_roundtrip':naive,'routing':bills,'pair_count_per_spectator':1280,'real_word_add_primitives_per_spectator':23040,'clean_comparison_word_add_primitives':17920,'total_real_negations_per_spectator':2304,'total_real_swaps_per_spectator':3792,'dirty_gate_polynomial_coefficients':[10240,41584,10240],'clean_gate_polynomial_coefficients':[8960,35184,10240],'dirty_scratch_bits':'b+1, restored; reused serially across all spectator lanes','error_bound':'80 sqrt(f) grid units for f spectator lanes','status':'PASS_FINITE_MACRO_NOT_PROVIDER_REPLACEMENT'}
    result.update({'dirty_ladder_full_states':ladder_cases,'elementary_full_pair_states':elementary_cases,'elementary_bill_per_spectator':{str(b):{'dirty':circuit.macro_bill(b),'constructed_clean':circuit.macro_bill(b,True)}for b in [8,32,64]},'bounded_fanin_upper_bound':'(6b+4)(10240b^2+41584b+10240)f elementary gates; no additional workspace'})
    result=json.loads(json.dumps(result))
    expected=json.loads((P/'RESULT.json').read_text()) if (P/'RESULT.json').exists() else None
    if '--print-result' in sys.argv:
        print(json.dumps(result,indent=2));return
    else:need(result==expected,'result mismatch')
    with tempfile.TemporaryDirectory(prefix='staged544-source-rejection-')as tmp:
        dst=Path(tmp)
        for name in ['verify.py','lattice.py','bits.py','circuit.py','FROZEN-SOURCES.json']:shutil.copyfile(P/name,dst/name)
        first=manifest[0]['path'];(dst/first).parent.mkdir(parents=True,exist_ok=True)
        (dst/first).write_bytes((P/first).read_bytes()+b' ')
        failed=subprocess.run([sys.executable,'-O','-B',str(dst/'verify.py')],capture_output=True,text=True)
        need(failed.returncode!=0 and 'source hash '+first in failed.stderr and not failed.stdout,'production source corruption rejects before science')
    print(json.dumps({'status':result['status'],'seconds':round(time.monotonic()-t,3),'half_cases':half_cases,'pair_cases':pair_cases,'full_cases':full_cases}))
if __name__=='__main__':check()
