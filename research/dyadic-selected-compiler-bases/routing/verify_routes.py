"""Independent reader/checker of explicit finite route certificates.

No import of the descriptor producer or earlier scientific engines.
This is not a Turing-machine interpreter or production-cover materialization.
"""
from fractions import Fraction as F
from pathlib import Path
from hashlib import sha1,sha256
from itertools import product
import gzip,json,sys

HERE=Path(__file__).resolve().parent
N=8

def require(ok,why):
    if not ok:raise ValueError(why)
def identity(n):return [[F(int(i==j)) for j in range(n)] for i in range(n)]
def mat(a):return [[F(x) for x in r] for r in a]
def transpose(a):return [list(c) for c in zip(*a)]
def multiply(a,b):
    out=[[F(0) for _ in b[0]] for _ in a]
    for i in range(len(a)):
        for k in range(len(b)):
            if a[i][k]:
                for j in range(len(b[0])):out[i][j]+=a[i][k]*b[k][j]
    return out
def minus(a,b):return [[x-y for x,y in zip(r,s)] for r,s in zip(a,b)]
def invert(a):
    n=len(a);a=[list(r)+e for r,e in zip(a,identity(n))]
    for j in range(n):
        k=next((i for i in reversed(range(j,n)) if a[i][j]),None)
        require(k is not None,'Complete basis is singular')
        a[k],a[j]=a[j],a[k];v=a[j][j];a[j]=[x/v for x in a[j]]
        for i in range(n):
            if i!=j:
                c=a[i][j];a[i]=[x-c*y for x,y in zip(a[i],a[j])]
    return [r[n:] for r in a]
def key(a):return tuple(tuple(r) for r in a)
def dyadic(x):
    q=F(x).denominator;return q&(q-1)==0
def dyadic_unit(x):
    x=abs(F(x));return bool(x) and dyadic(x) and x.numerator&(x.numerator-1)==0
def reduce_value(x,m):
    x=F(x);return x.numerator*pow(x.denominator,-1,m)%m if m>1 else 0
def reduce_matrix(a,m):return [[reduce_value(x,m) for x in r] for r in a]
def multiply_mod(a,b,m):
    return [[sum(x*y for x,y in zip(r,c))%m for c in zip(*b)] for r in a]
def reverse_word(word):
    answer=[]
    for op in reversed(word):
        if op[0]=='swap':answer.append(list(op))
        elif op[0]=='add':answer.append(['add',op[1],op[2],str(-F(op[3]))])
        else:answer.append(['scale',op[1],str(1/F(op[2]))])
    return answer
def lower_word(word):
    answer=[]
    for op in word:
        if op[0]=='add' and op[1]<op[2]:
            _,i,j,c=op;answer.extend([['swap',i,j],['add',j,i,c],['swap',i,j]])
        else:answer.append(list(op))
    require(all(op[0]!='add' or op[1]>op[2] for op in answer),'Unlowered earlier-target update')
    return answer
def word_matrix(word):
    a=identity(N)
    for op in word:
        kind,i=op[:2];require(type(i) is int and 0<=i<N,'Bad target coordinate')
        if kind=='swap':
            j=op[2];require(type(j) is int and 0<=j<N and i!=j,'Bad swap')
            a[i],a[j]=a[j],a[i]
        elif kind=='add':
            j,c=op[2],F(op[3]);require(type(j) is int and 0<=j<N and i!=j and dyadic(c),'Bad addition')
            a[i]=[x+c*y for x,y in zip(a[i],a[j])]
        elif kind=='scale':
            c=F(op[2]);require(dyadic_unit(c),'A scale introduces an odd forbidden prime')
            a[i]=[c*x for x in a[i]]
        else:raise ValueError('Unknown route operation')
    return a
def run_vector(word,vector,modulus):
    a=list(vector)
    for op in word:
        if op[0]=='swap':a[op[1]],a[op[2]]=a[op[2]],a[op[1]]
        elif op[0]=='add':a[op[1]]=(a[op[1]]+reduce_value(op[3],modulus)*a[op[2]])%modulus
        else:a[op[1]]=reduce_value(op[2],modulus)*a[op[1]]%modulus
    return a
def source_catalogue():
    native=json.loads(gzip.decompress((HERE/'retained/native.json.gz').read_bytes()))
    frames={};ranks={}
    for label,frame in native['frames'].items():
        u=transpose(mat(frame['B']+frame['A']));ui=invert(u);r=frame['dim']
        require(multiply(u,ui)==identity(N),'Raw complete inverse')
        projected=[[x if j<r else F(0) for j,x in enumerate(row)] for row in u]
        frames[int(label)]=multiply(projected,ui);ranks[int(label)]=r
    raw_pairs=[tuple(e[2:]) for e in native['program'] if e[0]=='MOVE']
    raw_pairs += [(native['start'][i],native['final'][i]) for i in range(222,native['public'])]
    different={}
    for a,b in sorted(set(raw_pairs)):
        a,b=sorted((a,b),key=lambda x:ranks[x]);p=minus(frames[b],frames[a])
        different.setdefault(key(p),(a,b,ranks[b]-ranks[a],p))
    require(len(different)==513,'Actual selected difference coverage')
    return frames,ranks,list(different.values()),len(set(raw_pairs))
def scalar_atom_count(c):
    c=F(c);require(dyadic_unit(c),'Non-dyadic scale expansion')
    k=abs(c.numerator).bit_length()-c.denominator.bit_length()
    return max(int(c<0),abs(k))
def route(low,high,s,forward,q,w):
    modulus=q**(w-1);low_product=multiply(low,s);h=reduce_matrix(low_product,q)
    carry=[[(x-y)/q for x,y in zip(r,t)] for r,t in zip(low_product,h)]
    require(all(dyadic(x) for r in carry for x in r),'Representative carry was not q-integral dyadic')
    if w==1:return h,[[0]*N for _ in range(N)],carry,0
    y=[]
    for x,c in zip(high,carry):
        linear=run_vector(forward,x,modulus)
        y.append([(a+reduce_value(b,modulus))%modulus for a,b in zip(linear,c)])
    return h,y,carry,N*len(forward)+N*N
def low_matrix(q,seed):
    a=[[int(i==j) for j in range(N)] for i in range(N)]
    for k in range(2*N+seed%7):
        i=(3*k+seed)%N;j=(i+1+k%(N-1))%N;c=(k*k+seed+1)%q
        a[i]=[(x+c*y)%q for x,y in zip(a[i],a[j])]
    a[seed%N],a[(seed+1)%N]=a[(seed+1)%N],a[seed%N]
    return a

def main():
    inputs=json.loads((HERE/'INPUTS.json').read_text())
    for row in inputs['files']:
        data=(HERE/row['path']).read_bytes()
        require(len(data)==row['bytes'] and sha256(data).hexdigest()==row['sha256']
                and sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],
                'Source bytes changed: '+row['path'])
    frames,ranks,differences,pairs=source_catalogue()
    bases=json.loads((HERE/'retained/bases.json').read_text())
    cat=json.loads((HERE/'CATALOGUE.json').read_text());rows=cat['routes']
    require(len(rows)==len(bases)==513 and cat['catalogue_entries']==513,'Complete certificate count')
    references={};checked=[];nonraw=0;maxima={};modular=0;repair_count=0
    rawkeys={key(x) for x in frames.values()}
    for (a,b,rank,p),br,row in zip(differences,bases,rows):
        require(br['pair']==row['pair']==[a,b] and br['rank']==row['rank']==rank,'Source pair order/rank changed')
        basis=mat(br['alternative_basis']);bi=invert(basis)
        expected=[[x if j<rank else F(0) for j,x in enumerate(r)] for r in basis]
        require(multiply(p,basis)==expected and multiply(basis,bi)==identity(N),'Both complete image/kernel summands')
        require(all(dyadic(x) for r in basis+bi for x in r),'Complete basis is not dyadic')
        rp,ref=references.setdefault(rank,([a,b],basis));s=mat(row['matrix'])
        require(row['reference_pair']==rp and multiply(s,ref)==basis,'Actual whole-job matcher differs')
        forward=reverse_word(row['elimination_word']);inverse_word=row['elimination_word']
        fm=word_matrix(forward);im=word_matrix(inverse_word)
        require(fm==transpose(s) and multiply(fm,im)==identity(N),'Exact rational descriptor endpoint/inverse')
        lowered=lower_word(forward);back=lower_word(inverse_word)
        require(word_matrix(lowered)==fm and word_matrix(back)==im,'Paid upper-update lowering changed the action')
        counts={kind:sum(op[0]==kind for op in inverse_word) for kind in ('swap','scale','add')}
        counts['earlier_target']=sum(op[0]=='add' and op[1]<op[2] for op in inverse_word)
        counts['signed_dyadic_scale_atoms']=sum(scalar_atom_count(op[2]) for op in inverse_word if op[0]=='scale')
        counts['full_ordinary_swaps']=N*sum(op[0]=='swap' for op in lowered)
        counts['full_ordered_shifts_with_carry']=N*sum(op[0]=='add' for op in lowered)+N*N
        counts['full_fixed_scalings']=N*counts['scale']
        counts['full_signed_dyadic_scale_atoms']=N*counts['signed_dyadic_scale_atoms']
        require(counts==row['counts'],'Source tariff census changed')
        require(counts['full_ordinary_swaps']<=2*N**3 and counts['full_ordered_shifts_with_carry']<=N**3
                and counts['full_fixed_scalings']<=N*N,'Existing source route tariff exceeded')
        for name,v in counts.items():maxima[name]=max(maxima.get(name,0),v)
        for q,w in ((3,1),(3,2),(3,3),(5,2),(7,2)):
            m=q**w;sm=reduce_matrix(s,m)
            for i in range(N):
                vector=[int(i==j) for j in range(N)]
                require(run_vector(lowered,vector,m)==sm[i],'Modular forward basis row')
                require(run_vector(back,run_vector(lowered,vector,m),m)==vector,'Same-owner modular inverse return')
                modular+=1
        repair_count+=len(row['short_repairs']);nonraw+=key(p) not in rawkeys
        checked.append((row,s,transpose(im),lowered,back))
    row,s,si,forward,back=next(x for x in checked if x[0]['pair']==[11,266])
    require(key(minus(frames[266],frames[11])) not in rawkeys,'Witness must be a non-raw difference')
    require(any(v[2]=='3/4' for v in row['nonunit_first_pivots']),'Actual nonunit fixed pivot missing')
    first_two=multiply(word_matrix(row['elimination_word'][:4]),transpose(s))
    require(all(first_two[i][j]==F(i==j) for i in range(N) for j in range(2))
            and first_two[2][2]==F(3,4) and first_two[6][2]==F(-1,4),
            'Actual third-column bad pivot and dyadic replacement')
    require(reduce_value(F(3,4),3)==0,'Fixed rational pivot must fail at q=3')
    fractional_carry=(F(1,2)-reduce_value(F(1,2),3))/3
    require(fractional_carry==F(-1,2) and dyadic(fractional_carry),
            'Representative carry is dyadic, not necessarily an integer')
    require(reduce_value(fractional_carry,3)!=int(fractional_carry//1)%3,
            'Integer-floor carry control must fail')
    carry_cases=0;omitted=None;wrong_return=None
    for q in (3,5,7,11):
        for w in (1,2,3,4):
            m=q**(w-1);full=q**w
            for seed in range(12):
                low=low_matrix(q,seed)
                high=[[(13*i+7*j+seed*(i+1)*(j+2))%m for j in range(N)] for i in range(N)]
                h,y,c,operations=route(low,high,s,forward,q,w)
                whole=[[a+q*x for a,x in zip(r,t)] for r,t in zip(low,high)]
                direct=multiply_mod(whole,reduce_matrix(s,full),full)
                require([[a+q*x for a,x in zip(r,t)] for r,t in zip(h,y)]==direct,'Full 64-field carry oracle')
                old,returned,ci,_=route(h,y,si,back,q,w)
                require(old==low and returned==high,'Whole-job forward/inverse return')
                require(ci==[[-x for x in r] for r in multiply(c,si)],'Inverse carry transport identity')
                if w==1:require(operations==0,'Zero-width high cube must call no primitive')
                if w>1 and omitted is None:
                    no=[run_vector(forward,r,m) for r in high]
                    if no!=y:omitted={'q':q,'w':w,'seed':seed}
                if w>1 and wrong_return is None:
                    bl,bh,_,_=route(h,y,s,forward,q,w)
                    if bl!=low or bh!=high:wrong_return={'q':q,'w':w,'seed':seed}
                carry_cases+=1
    require(omitted is not None and wrong_return is not None,'Carry/inverse controls did not discriminate')
    modulus=3;cube=list(product(range(modulus),repeat=N));images={};carry=[2,1,0,1,2,0,2,1]
    for x in cube:
        linear=run_vector(forward,x,modulus);y=tuple((v+c)%modulus for v,c in zip(linear,carry))
        require(y not in images,'Actual row route collided');images[y]=x
        returned=run_vector(back,[(v-c)%modulus for v,c in zip(y,carry)],modulus)
        require(tuple(returned)==x,'Row cube same-owner return')
    original={};moved={};returned_records={}
    for prefix in range(2):
        for suffix in range(3):
            for y,x in images.items():
                # Opaque records have dirty guards, zero/nonzero payload bytes,
                # and an internal gap. Their content never controls the route.
                payload=(b'left\xff',bytes((sum(x)%256,0,255,suffix)),b'gap\x00\xfe',x,b'right\x80')
                original[prefix,x,suffix]=payload
                moved[prefix,y,suffix]=payload
    require(len(moved)==len(original),'Spectator-carrying record route collided')
    for (prefix,y,suffix),payload in moved.items():
        old=tuple(run_vector(back,[(v-c)%modulus for v,c in zip(y,carry)],modulus))
        returned_records[prefix,old,suffix]=payload
    require(returned_records==original,'Complete opaque records or exterior spectators changed on return')
    collapsed={(y,suffix):payload for (prefix,y,suffix),payload in moved.items()}
    require(len(collapsed)<len(moved),'Dropping an exterior prefix must be detected')
    corrupted=dict(returned_records);some=next(iter(corrupted));p=corrupted[some]
    corrupted[some]=(p[0],bytes(len(p[1])),*p[2:])
    require(corrupted!=original,'A zero-test cannot substitute for arbitrary payload preservation')
    records=len(original)
    require(N*row['counts']['swap']<row['counts']['full_ordinary_swaps'],'Ignored earlier-target swaps must undercount')
    report={'status':'PASS_SOURCE_DYADIC_ROUTE_CERTIFICATES','catalogue_entries':len(rows),'source_pairs':pairs,
        'distinct_nonraw_differences':nonraw,'short_pivot_repairs':repair_count,'maxima_per_directed_full_route':maxima,
        'modular_basis_row_cases':modular,'full_64_field_carry_cases':carry_cases,'complete_one_row_high_cube':len(cube),
        'opaque_payload_records_with_spectators':records,
        'witness':{'pair':row['pair'],'reference_pair':row['reference_pair'],'rank':row['rank'],
                   'nonunit_first_pivots':row['nonunit_first_pivots'],'counts':row['counts']},
        'controls':{'omit_carry':omitted,'wrong_inverse':wrong_return,'fixed_pivot':'3/4=0 mod3',
                    'fractional_carry':'S=1/2,q=3,g0=1 gives C=-1/2; floor is rejected',
                    'spectators':'dropping exterior prefix collides',
                    'opaque_payload':'zeroing an arbitrary record does not return the input',
                    'ordinary_bill':'earlier-target updates require two paid swaps'},
        'catalogue_sha256':sha256((HERE/'CATALOGUE.json').read_bytes()).hexdigest(),
        'scope':'Exact finite words and all-q,w algebraic/tariff interface; not a machine interpreter or global production cover',
        'python_version':sys.version.split()[0]}
    (HERE/'EVIDENCE.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:report[k] for k in ('status','catalogue_entries','short_pivot_repairs','modular_basis_row_cases',
        'full_64_field_carry_cases','opaque_payload_records_with_spectators')},sort_keys=True))

if __name__=='__main__':main()
