"""Separate exact oracle for emitted data; no factor_words/build import."""
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256,sha1
import argparse,gzip,importlib.util,json,sys
HERE=Path(__file__).resolve().parent
def need(ok,msg):
    if not ok:raise ValueError(msg)
def matrix(a):return [[Q(x) for x in row] for row in a]
def eye(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def transpose(a):return [list(row) for row in zip(*a)]
def mul(a,b):
    z=[[Q(0) for _ in b[0]] for _ in a]
    for i,row in enumerate(a):
        for k,x in enumerate(row):
            if x:
                for j,y in enumerate(b[k]):
                    if y:z[i][j]+=x*y
    return z
def inverse(a):
    n=len(a);need(n and all(len(r)==n for r in a),'square full inverse');a=[list(r)+eye(n)[i] for i,r in enumerate(a)]
    for j in range(n):
        candidates=[i for i in range(j,n) if a[i][j]];need(candidates,'singular inverse');k=candidates[-1];a[j],a[k]=a[k],a[j]
        x=a[j][j];a[j]=[t/x for t in a[j]]
        for i in range(n):
            if i!=j and a[i][j]:
                x=a[i][j];a[i]=[u-x*v for u,v in zip(a[i],a[j])]
    return [row[n:] for row in a]
def direct(a,b):return [r+[Q(0)]*len(b) for r in a]+[[Q(0)]*len(a)+r for r in b]
def kron(a,b):return [[x*y for x in ar for y in br] for ar in a for br in b]
def perm(order):return [[Q(i==order[j]) for j in range(len(order))] for i in range(len(order))]
def projection(b,rank):return mul([[x if j<rank else Q(0) for j,x in enumerate(row)] for row in b],inverse(b))
def add(a,b,s=1):return [[x+s*y for x,y in zip(r,t)] for r,t in zip(a,b)]
def replay(n,word):
    a=eye(n)
    for op in word:
        kind=op[0];i=op[1];need(0<=i<n,'word coordinate')
        if kind=='swap':j=op[2];need(0<=j<n and j!=i,'swap coordinate');a[i],a[j]=a[j],a[i]
        elif kind=='add':
            j=op[2];c=Q(op[3]);need(0<=j<n and i!=j and c.denominator.bit_count()==1,'addition domain');a[i]=[x+c*y for x,y in zip(a[i],a[j])]
        elif kind=='scale':
            c=Q(op[2]);need(c and abs(c.numerator).bit_count()==1 and c.denominator.bit_count()==1,'dyadic-unit scale');a[i]=[c*x for x in a[i]]
        else:raise ValueError('unknown operation')
    return transpose(a)
KEYS=('swaps','adds','upper','scales','atoms')
def tally(word):
    c=dict.fromkeys(KEYS,0)
    for op in word:
        if op[0]=='swap':c['swaps']+=1
        elif op[0]=='add':c['adds']+=1;c['upper']+=op[1]<op[2]
        elif op[0]=='scale':
            x=Q(op[2]);c['scales']+=1;c['atoms']+=max(abs(abs(x.numerator).bit_length()-x.denominator.bit_length()),int(x<0))
    return c
def plus(a,b):return {k:a[k]+b[k] for k in KEYS}
def times(a,n):return {k:v*n for k,v in a.items()}
def recurrence(r):
    k=r['kind'];children=r['children'];cc=[recurrence(c) for c in children]
    if k=='identity':out=dict.fromkeys(KEYS,0)
    elif k in ('literal','permutation'):out=tally(r['data']['ops'])
    elif k in ('inverse','extend'):out=cc[0]
    elif k in ('multiply','direct_sum'):out=plus(*cc)
    elif k=='tensor':out=plus(times(cc[0],children[1]['n']),times(cc[1],children[0]['n']))
    elif k=='conjugate':out=plus(times(cc[0],2),cc[1])
    elif k=='guard':out=plus(times(cc[1],2*children[0]['n']),times(cc[0],r['data']['rank']))
    else:raise ValueError('unknown constructor')
    need(out==r['count'],'stored recurrence differs from independent recurrence');return out

def semantic(node,seeds,bases,refs,ports):
    k=node['kind']
    def ev(x):return semantic(x,seeds,bases,refs,ports)
    if k=='seed':return seeds[node['label']]
    if k=='basis':return bases[tuple(node['pair'])]
    if k=='relative':return mul(bases[tuple(node['pair'])],inverse(bases[refs[tuple(node['pair'])]]))
    if k=='permutation':return perm(node['order'])
    if k=='inverse':return inverse(ev(node['child']))
    if k=='extend':
        a=ev(node['child']);return direct(a,eye(node['n']-len(a))) if len(a)<node['n'] else a
    if k=='port_route':
        u=direct(ports[node['port']],eye(7));return mul(mul(u,perm([0,*range(8,15),*range(1,8)])),inverse(u))
    if k=='placed_basis':
        a=ev(node['child']);axes=node['axes'];order=axes+[j for j in range(node['n']) if j not in set(axes)]
        return mul(perm(order),direct(a,eye(node['n']-len(a))))
    if k=='split_basis':
        a=ev(node['child']);j=node['selected'];return mul(a,perm(j+[i for i in range(len(a)) if i not in set(j)]))
    a,b=[ev(x) for x in node['children']]
    if k=='multiply':return mul(a,b)
    if k=='direct_sum':return direct(a,b)
    if k=='tensor':return kron(a,b)
    if k=='conjugate':return mul(mul(a,b),inverse(a))
    if k=='guard':
        e=projection(b,node['rank']);return add(kron(a,e),kron(eye(len(a)),add(eye(len(b)),e,-1)))
    if k in ('tagged_sum_basis','tagged_tensor_basis'):
        r,s=node['ranks'];n,m=len(a),len(b)
        if k=='tagged_sum_basis':full=direct(a,b);active=list(range(r))+list(range(n,n+s));p=direct(projection(a,r),projection(b,s));rank=r+s
        else:full=kron(a,b);active=[i*m+j for i in range(r) for j in range(s)];p=kron(projection(a,r),projection(b,s));rank=r*s
        out=mul(full,perm(active+[j for j in range(len(full)) if j not in set(active)]));need(projection(out,rank)==p,'image-first full-kernel normalization');return out
    raise ValueError('unknown semantic node '+k)

def reduced(x,m):
    if m==1:return 0
    x=Q(x);return x.numerator*pow(x.denominator,-1,m)%m
def numeric(rows,word,m):
    a=[list(r) for r in rows]
    for op in word:
        i=op[1]
        if op[0]=='swap':
            j=op[2]
            for row in a:row[i],row[j]=row[j],row[i]
        elif op[0]=='add':
            j=op[2];c=reduced(op[3],m)
            for row in a:row[i]=(row[i]+c*row[j])%m
        else:
            c=reduced(op[2],m)
            for row in a:row[i]=row[i]*c%m
    return a
def route(g,x,s,word,q,w):
    exact=mul(g,s);h=[[reduced(t,q) for t in row] for row in exact]
    carry=[[(v-z)/q for v,z in zip(row,hr)] for row,hr in zip(exact,h)]
    need(all(t.denominator.bit_count()==1 for row in carry for t in row),'carry leaves dyadic localization')
    m=q**(w-1);y=numeric(x,word,m);y=[[(v+reduced(c,m))%m for v,c in zip(row,cr)] for row,cr in zip(y,carry)]
    return h,y
def carry_checks(s,word,back):
    n=len(s);si=inverse(s);count=0
    for q in (3,5):
        g=[[int(i==j) if i>=j else (i+2*j+1)%q for j in range(n)] for i in range(n)]
        for w in (1,2,3):
            x=[[(3*i+j+i*j+1)%q**(w-1) for j in range(n)] for i in range(n)]
            h,y=route(g,x,s,word,q,w);gb,xb=route(h,y,si,back,q,w)
            need(gb==g and xb==x,'generated full carry inverse fails')
            full=[[v+q*z for v,z in zip(row,xr)] for row,xr in zip(g,x)];want=[[reduced(v,q**w) for v in row] for row in mul(full,s)]
            need(want==[[v+q*z for v,z in zip(row,yr)] for row,yr in zip(h,y)],'generated full carry reconstruction fails');count+=1
    return count,n*n*count

def controls():
    def unit(x):x=Q(x);return bool(x) and abs(x.numerator).bit_count()==1 and x.denominator.bit_count()==1
    need(not any(unit(x) for x in (7,17)) and not any(unit(x+c*y) for x,y in ((7,17),(17,7)) for c in (1,-1,2,-2)),'short-pivot counterexample lost')
    s=matrix([[2,0],[0,1]]);bad=matrix([[Q(1,2),0],[0,0]]);i=eye(2)
    l=add(kron(s,bad),kron(i,add(i,bad,-1)));li=add(kron(inverse(s),bad),kron(i,add(i,bad,-1)))
    need(mul(l,li)!=eye(4),'non-idempotent sector does not fail')
    c=matrix([[1,Q(1,2)],[0,1]]);e=projection(c,1);need(e!=transpose(e) and mul(e,e)==e,'valid nonorthogonal sector lost')
    p=kron(eye(2),matrix([[1,0],[0,0]]));need(p!=matrix([[1,0,0,0],[0,1,0,0],[0,0,0,0],[0,0,0,0]]),'missing tensor image shuffle not detected')
    return dict(universal_short_repair_rejected=True,nonidempotent_guard_rejected=True,nonorthogonal_sector_accepted=True,missing_image_shuffle_rejected=True)

def source_trace():
    def load(name):
        spec=importlib.util.spec_from_file_location(name,HERE/'retained'/f'{name}.py');module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
    schedule=load('schedule');product=load('product')
    def raw_run(machine,owners,columns):
        need(len(owners)==2 and columns>0,'mock normalized callback shape')
        yield owners[0],tuple(reversed(range(columns)))
        yield owners[1],tuple(range(2*columns))
    raw=product.Native(2,(1,2),(1,2),raw_run);word,native=product.specialize(raw,{1:1,2:1},1)
    class Trace:
        def __init__(self):self.n=8;self.next_owner=1000;self.live=set();self.stacks={};self.moves=self.leaves=self.opens=self.closes=self.calls=self.maxdepth=self.nonidentity=0
        def zero(self):
            x=self.next_owner;self.next_owner+=1;self.live.add(x);self.opens+=1;return x
        def retire_zero(self,x):
            need(x in self.live and not self.stacks.get(x),'abstract zero-role ownership/adapter return');self.live.remove(x);self.closes+=1
        def move(self,x,order,inverted):
            need(sorted(order)==list(range(self.n)),'source move dropped spectators');stack=self.stacks.setdefault(x,[])
            if inverted:need(stack and stack.pop()==order,'source inverse placement mismatched')
            else:stack.append(order)
            self.moves+=1;self.nonidentity+=tuple(order)!=tuple(range(self.n));self.maxdepth=max(self.maxdepth,len(stack))
        def leaf(self,x,axis):need(0<=axis<self.n,'source leaf axis');self.leaves+=1
        def native(self,owners,columns):self.calls+=1;yield from native(self,owners,columns)
    trace=Trace();schedule.expand(word,trace.n,list(range(word.root_width(trace.n))),trace)
    need(not trace.live and all(not s for s in trace.stacks.values()) and trace.opens==trace.closes,'source complete return')
    need(trace.nonidentity and trace.maxdepth>=2 and trace.leaves,'source fixture missing nested/permuted activity')
    return dict(semantics='literal compiler syntax with a normalized mock callback; no new raw-native or erasure theorem',moves=trace.moves,leaf_requests=trace.leaves,native_calls=trace.calls,zero_roles=trace.opens,retired_zero_roles=trace.closes,max_adapter_depth=trace.maxdepth,nonidentity_moves=trace.nonidentity)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);args=ap.parse_args()
    inputs=json.loads((HERE/'INPUTS.json').read_text());production=json.loads((HERE/'PRODUCTION.json').read_text())
    for item in inputs['files']:
        b=(HERE/item['path']).read_bytes();need(len(b)==item['bytes'] and sha256(b).hexdigest()==item['sha256'],'input hash/length')
        need(sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==item['git_blob'],'input blob')
    for name,digest in production['files'].items():need(sha256((HERE/name).read_bytes()).hexdigest()==digest,'certificate hash '+name)
    native=json.loads(gzip.decompress((HERE/'retained/native.json.gz').read_bytes()));original=json.loads((HERE/'retained/EFREE-RESULT.json').read_text())
    basis_rows=json.loads((HERE/'retained/bases.json').read_text());bases={tuple(r['pair']):matrix(r['alternative_basis']) for r in basis_rows}
    finite=json.loads((HERE/'retained/ROUTE-CATALOGUE.json').read_text())['routes'];refs={tuple(r['pair']):tuple(r['reference_pair']) for r in finite}
    byrank={r['rank']:tuple(r['reference_pair']) for r in finite};ports={r['port']:matrix(r['basis']) for r in original['source']['charts']}
    raw={int(k):transpose(matrix(v['B']+v['A'])) for k,v in native['frames'].items()}
    source_expected={'raw/'+str(k):m for k,m in raw.items()}|{'port/'+str(k):m for k,m in ports.items()}|{'reference/'+str(k):bases[pair] for k,pair in byrank.items()}
    expected=source_expected|{'control/nonorthogonal':matrix([[1,Q(1,2)],[0,1]]),'control/diagonal':matrix([[2,0],[0,Q(1,2)]]),'control/short_repair_failure':matrix([[7,17],[2,5]])}
    seedfile=json.loads((HERE/'SEEDS.json').read_text());seeds={};seedcounts={};seedops=0
    need(seedfile['source_seed_count']==755 and len(source_expected)==755,'primitive inventory changed')
    for row in seedfile['seeds']:
        label=row['label'];m=matrix(row['matrix']);need(label in expected and label not in seeds and m==expected[label],'seed source binding')
        need(replay(len(m),row['word'])==m,'seed elementary endpoint');c=tally(row['word']);need(c==row['count'],'seed count')
        seeds[label]=m;seedcounts[label]=c;seedops+=len(row['word'])
    need(set(seeds)==set(expected),'missing primitive seed')
    for chart in original['source']['charts']:
        u=ports[chart['port']];f=native['frames'][str(chart['input_frame'])];p=projection(raw[chart['input_frame']],f['dim'])
        need(projection(u,1)==p,'coupled U_i head changed');f=native['frames'][str(chart['output_frame'])]
        need(add(eye(8),p,-1)==projection(raw[chart['output_frame']],f['dim']),'coupled U_i body changed')
    derived=json.loads((HERE/'DERIVED-BASES.json').read_text());need(len(derived)==513,'derived basis inventory')
    for row in derived:
        need(replay(8,row['word'])==bases[tuple(row['pair'])],'relative plus reference does not give full basis')
        need(tally(row['word'])==row['count'],'derived basis count')
    cases=json.loads((HERE/'CASES.json').read_text());modular=cells=ops=upper=0;orders=0
    for row in cases:
        s=semantic(row['expected'],seeds,bases,refs,ports);n=row['n'];need(len(s)==n,'constructor dimension')
        need(replay(n,row['word'])==s and replay(n,row['inverse_word'])==inverse(s),'constructor endpoint/inverse')
        need(replay(n,row['ordered_word'])==s,'ordered/signed lowering endpoint')
        c=tally(row['word']);need(c==row['count']==tally(row['inverse_word'])==recurrence(row['recipe']),'constructor/inverse/recurrent counts')
        ec=tally(row['ordered_word']);need(ec['upper']==0 and ec['swaps']==c['swaps']+2*c['upper'] and ec['adds']==c['adds'] and ec['scales']==c['atoms'],'earlier-target/scaling expansion bill')
        expected_bill=dict(ordinary_swaps=n*(c['swaps']+2*c['upper']),ordered_shifts_including_carry=n*c['adds']+n*n,fixed_scalings=n*c['scales'],signed_scale_atoms=n*c['atoms'],carry_slots=n*n)
        need(expected_bill==row['physical_per_direction'],'full-row high/carry invoice')
        m,v=carry_checks(s,row['word'],row['inverse_word']);modular+=m;cells+=v;ops+=len(row['word']);upper+=c['upper']
        orders+=replay(n,list(reversed(row['word'])))!=s
    need(orders and upper,'fixtures fail to distinguish chronology/upper brackets')
    caller=json.loads(gzip.decompress((HERE/'retained/EFREE-CALLER.json.gz').read_bytes()));ledger=json.loads((HERE/'CALLER-LEDGER.json').read_text())
    for row in ledger['stage_counts']:
        c=times(seedcounts['port/'+str(row['port'])],2);c['swaps']+=7;need(c==row['per_stage_count'],'actual coupled stage count')
        n=134;want=dict(ordinary_swaps=n*(c['swaps']+2*c['upper']),ordered_shifts_including_carry=n*c['adds']+n*n,fixed_scalings=n*c['scales'],signed_scale_atoms=n*c['atoms'],carry_slots=n*n)
        need(want==row['physical_per_direction_134'],'port route was billed at wrong ambient')
    def swap_count(order):
        unseen=set(range(len(order)));cycles=0
        while unseen:
            cycles+=1;j=next(iter(unseen))
            while j in unseen:unseen.remove(j);j=order[j]
        return len(order)-cycles
    for row in ledger['target_counts']:
        target=caller['diagonal'][row['target']];need(target['q'] in (0,1),'unexpected caller head coefficient')
        active=([0] if target['q'] else [])+[8+7*(j-1)+k for j in target['stages'] for k in range(7)]
        order=active+[j for j in range(134) if j not in set(active)];need(len(order)==134 and len(set(order))==134,'caller complete target basis')
        c=dict(seedcounts['port/'+str(row['port'])]);c['swaps']+=swap_count(order)
        need(c==row['count'] and len(active)==row['rank'],'caller target count/rank')
    need(len(ledger['stage_counts'])==111 and len(ledger['target_counts'])==4218 and ledger['distinct_stage_symbols']==1998 and ledger['directed_raw_port_occurrences']==15984,'source port/target coverage')
    additions=set();scalings=set()
    words=[r['word'] for r in seedfile['seeds'] if r['label'] in source_expected]+[r['elimination_word'] for r in finite]
    for word in words:
        for op in word:
            if op[0]=='add':additions.update((str(Q(op[3])),str(-Q(op[3]))))
            elif op[0]=='scale':scalings.update((str(Q(op[2])),str(1/Q(op[2]))))
    alphabet=json.loads((HERE/'ALPHABET.json').read_text());need(sorted(additions,key=Q)==alphabet['addition_coefficients'] and sorted(scalings,key=Q)==alphabet['scale_coefficients'],'finite linear alphabet')
    result=dict(status='PASS_GENERATED_ROUTE_LEDGER',source_seed_words=755,control_seed_words=3,seed_elementary_operations=seedops,derived_complete_bases=len(derived),constructor_cases=len(cases),constructor_word_operations=ops,earlier_target_additions=upper,reversal_rejection_witnesses=orders,full_prime_power_routes=modular,high_coordinate_checks=cells,actual_port_bases=111,distinct_port_stage_symbols=1998,caller_target_bases=4218,source_addition_alphabet=len(additions),source_scale_alphabet=len(scalings),controls=controls(),literal_source_trace=source_trace(),certificate_hashes=production['files'],proof_sha256=sha256((HERE/'PROOF.md').read_bytes()).hexdigest(),verification_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    text=json.dumps(result,indent=2)+'\n'
    if args.output:args.output.write_text(text)
    print(text,end='')
if __name__=='__main__':main()
