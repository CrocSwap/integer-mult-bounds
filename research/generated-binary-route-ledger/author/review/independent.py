"""Independent column-action audit of generated right-word certificates.

Never imports the author's generator, factorization or verifier modules.
Dense rational formulas and input-source reconstruction supply the oracle.
"""
from fractions import Fraction as F
from pathlib import Path
from hashlib import sha1,sha256
from itertools import product
from math import prod
import argparse,gzip,json,sys

PROOF='8c9d8e631325f6b67e8a0863eda8602ff51095d3488c95de5e714d1cd4100a6d'
INPUTS='c2016699a49bbd2b255dc4ca68f6060b6ccd023343e0f62ea54a1707c6b17666'
PRODUCTION='404b0e801bae868679250df82e4cd602239170a07c75682c462636127fa1a238'
FIELDS=('swaps','adds','upper','scales','atoms')
def need(ok,why):
    if not ok:raise ValueError(why)
def matrix(a):return [[F(x) for x in r] for r in a]
def eye(n):return [[F(i==j) for j in range(n)] for i in range(n)]
def transpose(a):return [list(r) for r in zip(*a)]
def multiply(a,b):
    c=[[F(0) for _ in b[0]] for _ in a]
    for i in range(len(a)):
        for k in range(len(b)):
            if a[i][k]:
                for j in range(len(b[0])):c[i][j]+=a[i][k]*b[k][j]
    return c
def inverse(a):
    n=len(a);x=[list(r)+s for r,s in zip(a,eye(n))]
    for j in range(n):
        k=next((i for i in reversed(range(j,n)) if x[i][j]),None)
        need(k is not None,'Singular complete matrix')
        x[j],x[k]=x[k],x[j];v=x[j][j];x[j]=[z/v for z in x[j]]
        for i in range(n):
            if i!=j:
                v=x[i][j];x[i]=[a-v*b for a,b in zip(x[i],x[j])]
    return [r[n:] for r in x]
def plus(a,b,sign=1):return [[x+sign*y for x,y in zip(r,s)] for r,s in zip(a,b)]
def tensor(a,b):return [[x*y for x in ar for y in br] for ar in a for br in b]
def direct_sum(a,b):
    n,m=len(a),len(b)
    return [list(r)+[F(0)]*m for r in a]+[[F(0)]*n+list(r) for r in b]
def permutation(order):
    n=len(order);need(sorted(order)==list(range(n)),'Incomplete coordinate permutation')
    return [[F(i==order[j]) for j in range(n)] for i in range(n)]
def full_order(selected,n):
    need(len(set(selected))==len(selected) and all(0<=i<n for i in selected),'Bad active tuple')
    return list(selected)+[i for i in range(n) if i not in selected]
def perm_length(order):
    seen=set();cycles=0
    for i in range(len(order)):
        if i in seen:continue
        cycles+=1
        while i not in seen:seen.add(i);i=order[i]
    return len(order)-cycles
def power_two(a):return a>0 and not(a&(a-1))
def dyadic(x):return power_two(F(x).denominator)
def unit(x):
    x=abs(F(x));return bool(x) and power_two(x.numerator) and power_two(x.denominator)
def atoms(x):
    x=F(x);need(unit(x),'Nonunit scale')
    exponent=abs(x.numerator).bit_length()-x.denominator.bit_length()
    return max(abs(exponent),int(x<0))
def recount(word,n):
    c=dict.fromkeys(FIELDS,0)
    for op in word:
        kind,i=op[:2];need(type(i) is int and 0<=i<n,'Bad target')
        if kind=='swap':
            need(len(op)==3 and type(op[2]) is int and 0<=op[2]<n and i!=op[2],'Bad swap');c['swaps']+=1
        elif kind=='add':
            j=op[2];need(len(op)==4 and type(j) is int and 0<=j<n and i!=j and dyadic(op[3]),'Bad dyadic addition')
            c['adds']+=1;c['upper']+=i<j
        elif kind=='scale':
            need(len(op)==3 and unit(op[2]),'Forbidden-prime scale');c['scales']+=1;c['atoms']+=atoms(op[2])
        else:raise ValueError('Unknown elementary instruction')
    return c
def word_matrix(word,n):
    # Right multiplication updates COLUMNS, directly yielding M rather than M^t.
    a=eye(n)
    for op in word:
        kind,i=op[:2]
        if kind=='swap':
            j=op[2]
            for r in a:r[i],r[j]=r[j],r[i]
        elif kind=='add':
            j,c=op[2],F(op[3])
            for r in a:r[i]+=c*r[j]
        else:
            c=F(op[2])
            for r in a:r[i]*=c
    return a
def invert_word(word):
    out=[]
    for op in reversed(word):
        if op[0]=='swap':out.append(list(op))
        elif op[0]=='add':out.append(['add',op[1],op[2],str(-F(op[3]))])
        else:out.append(['scale',op[1],str(1/F(op[2]))])
    return out
def lower_word(word):
    out=[]
    for op in word:
        if op[0]=='add' and op[1]<op[2]:
            _,i,j,c=op;out.extend([['swap',i,j],['add',j,i,c],['swap',i,j]])
        else:out.append(list(op))
    return out
def cadd(*terms):return {k:sum(t[k] for t in terms) for k in FIELDS}
def cmul(x,c):return {k:x*c[k] for k in FIELDS}
def bill(c,n):return {'ordinary_swaps':n*(c['swaps']+2*c['upper']),
    'ordered_shifts_including_carry':n*c['adds']+n*n,'fixed_scalings':n*c['scales'],
    'signed_scale_atoms':n*c['atoms'],'carry_slots':n*n}

def source_data(root):
    for name,pin in [('PROOF.md',PROOF),('INPUTS.json',INPUTS),('PRODUCTION.json',PRODUCTION)]:
        need(sha256((root/name).read_bytes()).hexdigest()==pin,'Frozen author file changed '+name)
    manifest=json.loads((root/'INPUTS.json').read_text())
    for r in manifest['files']:
        b=(root/r['path']).read_bytes()
        need(len(b)==r['bytes'] and sha256(b).hexdigest()==r['sha256'] and
             sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==r['git_blob'],'Changed retained input '+r['path'])
    produced=json.loads((root/'PRODUCTION.json').read_text())
    for f,d in produced['files'].items():need(sha256((root/f).read_bytes()).hexdigest()==d,'Changed certificate '+f)
    native=json.loads(gzip.decompress((root/'retained/native.json.gz').read_bytes()))
    caller=json.loads(gzip.decompress((root/'retained/EFREE-CALLER.json.gz').read_bytes()))
    bases=json.loads((root/'retained/bases.json').read_text());references={}
    for r in bases:references.setdefault(r['rank'],r)
    raw={int(k):transpose(matrix(v['B']+v['A'])) for k,v in native['frames'].items()}
    ports={}
    for i in range(caller['ports']):
        a,b=native['start'][i],native['final'][caller['ports']+i]
        ports[i]=transpose(matrix(native['frames'][str(a)]['B']+native['frames'][str(b)]['B']))
    return produced,native,caller,bases,references,raw,ports

def seeds_and_bases(root,native,bases,references,raw,ports):
    document=json.loads((root/'SEEDS.json').read_text());entries=document['seeds']
    need(document['source_seed_count']==755 and len(entries)==758,'Seed inventory')
    matrices={};counts={};words={};seen={'raw_frame':set(),'reference_basis':set(),'port_basis':set(),'control':set()}
    controls={'control/nonorthogonal':matrix([[1,F(1,2)],[0,1]]),
              'control/diagonal':matrix([[2,0],[0,F(1,2)]]),
              'control/short_repair_failure':matrix([[7,17],[2,5]])}
    for row in entries:
        s=row['source'];kind=s['kind'];label=row['label']
        if kind=='raw_frame':
            key=s['id'];expected=raw[key]
            need(label==f'raw/{key}' and s['rank']==native['frames'][str(key)]['dim'],'Raw frame label/rank')
        elif kind=='reference_basis':
            key=s['rank'];expected=matrix(references[key]['alternative_basis'])
            need(label==f'reference/{key}' and s['pair']==references[key]['pair'],'Reference selection')
        elif kind=='port_basis':
            key=s['port'];expected=ports[key]
            need(label==f'port/{key}' and s['input_frame']==native['start'][key] and s['output_frame']==native['final'][111+key],'Original coupled port changed')
        else:key=label;expected=controls[label]
        need(key not in seen[kind],'Duplicate seed');seen[kind].add(key)
        actual=matrix(row['matrix']);n=len(actual);c=recount(row['word'],n)
        need(actual==expected and word_matrix(row['word'],n)==expected,'Seed right-word endpoint '+label)
        need(c==row['count'],'Seed literal count '+label)
        inv=word_matrix(invert_word(row['word']),n)
        need(multiply(actual,inv)==eye(n),'Seed inverse '+label)
        matrices[label]=actual;counts[label]=c;words[label]=row['word']
    need(seen['raw_frame']==set(raw) and len(raw)==636,'Raw seed coverage')
    need(seen['reference_basis']==set(range(1,9)) and seen['port_basis']==set(range(111)),'Missing reference/port seed')
    bypair={tuple(b['pair']):b for b in bases}
    relative={tuple(r['pair']):r for r in json.loads((root/'retained/ROUTE-CATALOGUE.json').read_text())['routes']}
    derived=json.loads((root/'DERIVED-BASES.json').read_text())
    need(len(derived)==len(bases)==513,'Derived complete-basis count')
    for r in derived:
        pair=tuple(r['pair']);br=bypair[pair];b=matrix(br['alternative_basis']);rank=br['rank'];name=f'reference/{rank}'
        rel=invert_word(relative[pair]['elimination_word'])
        need(word_matrix(r['word'],8)==b and r['rank']==rank,'Complete derived basis')
        need(recount(r['word'],8)==r['count']==cadd(recount(rel,8),counts[name]),'Reference-word charge omitted')
        need(multiply(word_matrix(rel,8),matrices[name])==b,'Relative to complete seed orientation')
        matrices['basis/'+','.join(map(str,pair))]=b
        matrices['relative/'+','.join(map(str,pair))]=word_matrix(rel,8)
    return matrices,counts,words,bypair

def semantic(spec,matrices,ports):
    kind=spec['kind']
    if kind=='seed':return matrices[spec['label']]
    if kind in ('basis','relative'):return matrices[kind+'/'+','.join(map(str,spec['pair']))]
    if kind=='permutation':return permutation(spec['order'])
    if kind=='inverse':return inverse(semantic(spec['child'],matrices,ports))
    if kind=='extend':
        x=semantic(spec['child'],matrices,ports);return direct_sum(x,eye(spec['n']-len(x)))
    if kind=='split_basis':
        x=semantic(spec['child'],matrices,ports)
        need(all(i<spec['rank'] for i in spec['selected']),'Split used old kernel column')
        return multiply(x,permutation(full_order(spec['selected'],len(x))))
    if kind=='placed_basis':
        x=semantic(spec['child'],matrices,ports)
        need(len(spec['axes'])==len(x),'Placement omitted complete basis')
        return multiply(permutation(full_order(spec['axes'],spec['n'])),direct_sum(x,eye(spec['n']-len(x))))
    if kind=='port_route':
        x=direct_sum(ports[spec['port']],eye(7));order=list(range(15))
        for i in range(1,8):order[i],order[i+7]=order[i+7],order[i]
        return multiply(multiply(x,permutation(order)),inverse(x))
    children=[semantic(s,matrices,ports) for s in spec['children']]
    if kind=='multiply':
        out=eye(len(children[0]))
        for x in children:out=multiply(out,x)
        return out
    a,b=children;n,m=len(a),len(b)
    if kind=='direct_sum':return direct_sum(a,b)
    if kind=='tensor':return tensor(a,b)
    if kind=='conjugate':return multiply(multiply(a,b),inverse(a))
    if kind=='guard':
        k=spec['rank'];need(0<=k<=m,'Bad sector rank')
        diag=[[F(i==j and i<k) for j in range(m)] for i in range(m)]
        e=multiply(multiply(b,diag),inverse(b));need(multiply(e,e)==e,'Sector not idempotent')
        return plus(tensor(a,e),tensor(eye(n),plus(eye(m),e,-1)))
    if kind=='tagged_sum_basis':
        r,s=spec['ranks'];active=list(range(r))+list(range(n,n+s))
        return multiply(direct_sum(a,b),permutation(full_order(active,n+m)))
    if kind=='tagged_tensor_basis':
        r,s=spec['ranks'];active=[i*m+j for i in range(r) for j in range(s)]
        return multiply(tensor(a,b),permutation(full_order(active,n*m)))
    raise ValueError('Unknown semantic constructor '+kind)

def recipe_count(recipe):
    kind=recipe['kind'];n=recipe['n'];children=recipe['children'];data=recipe['data']
    cc=[recipe_count(c) for c in children]
    if kind in ('multiply','conjugate','inverse'):
        need(all(c['n']==n for c in children),'Wrong complete product dimension')
    elif kind=='extend':need(children[0]['n']<=n,'Negative spectator extension')
    elif kind=='direct_sum':need(n==sum(c['n'] for c in children),'Wrong direct sum dimension')
    elif kind in ('tensor','guard'):need(n==prod(c['n'] for c in children),'Wrong tensor/guard dimension')
    if kind=='guard':need(0<=data['rank']<=children[1]['n'],'Invalid guarded sector rank')
    if kind=='literal':out=recount(data['ops'],n)
    elif kind=='permutation':
        out=recount(data['ops'],n);p=perm_length(data['order'])
        need(out==dict(zip(FIELDS,(p,0,0,0,0))) and word_matrix(data['ops'],n)==permutation(data['order']),'Complete permutation word')
    elif kind in ('inverse','extend'):out=cc[0]
    elif kind in ('multiply','direct_sum'):out=cadd(*cc)
    elif kind=='conjugate':out=cadd(cmul(2,cc[0]),cc[1])
    elif kind=='tensor':out=cadd(cmul(children[1]['n'],cc[0]),cmul(children[0]['n'],cc[1]))
    elif kind=='guard':out=cadd(cmul(2*children[0]['n'],cc[1]),cmul(data['rank'],cc[0]))
    else:raise ValueError('Unknown count constructor '+kind)
    need(out==recipe['count'],'Declared structural recurrence differs')
    return out

def caller_counts(root,caller,ports,counts,words):
    ledger=json.loads((root/'CALLER-LEDGER.json').read_text())
    need(ledger['distinct_stage_symbols']==111*18==1998,'Port-stage symbol count')
    local=sum(e[0]=='LOCAL' for e in caller['events'])
    need(local==36 and ledger['directed_raw_port_occurrences']==4*local*111==15984,'Coupled directed chronology')
    need(len(ledger['stage_counts'])==111,'Port ledger coverage')
    for row in ledger['stage_counts']:
        i=row['port'];expected=cadd(cmul(2,counts[f'port/{i}']),dict(zip(FIELDS,(7,0,0,0,0))))
        need(row['per_stage_count']==expected and row['physical_per_direction_134']==bill(expected,134),'Full 134-dimensional stage invoice')
        # Independently retain the exact original U_i, with seven physical swaps.
        swaps=[['swap',j,j+7] for j in range(1,8)]
        word=words[f'port/{i}']+swaps+invert_word(words[f'port/{i}'])
        need(word_matrix(word,15)==semantic({'kind':'port_route','port':i},{},ports),'Original coupled route endpoint')
    targets=ledger['target_counts'];need(len(targets)==111*38==4218,'Complete caller-target coverage')
    pairs=set()
    for row in targets:
        i,t=row['port'],row['target'];need((i,t) not in pairs,'Duplicate caller target');pairs.add((i,t))
        source=caller['diagonal'][t];need(source['q'] in (0,1),'Unadmitted target coefficient')
        # Source stage labels 1..18 name fresh spaces AFTER the central body 1..7.
        active=([0] if source['q'] else [])+[1+7*s+j for s in source['stages'] for j in range(7)]
        order=full_order(active,134);p=perm_length(order)
        expected=cadd(counts[f'port/{i}'],dict(zip(FIELDS,(p,0,0,0,0))))
        need(row['rank']==len(active) and row['count']==expected,'Caller complete-basis permutation count')
    need(pairs==set(product(range(111),range(38))),'Caller target holes')
    first=caller['diagonal'][0]
    correct=([0] if first['q'] else [])+[1+7*s+j for s in first['stages'] for j in range(7)]
    wrong=([0] if first['q'] else [])+[1+7*(s-1)+j for s in first['stages'] for j in range(7)]
    need(full_order(correct,134)!=full_order(wrong,134) and perm_length(full_order(correct,134))!=perm_length(full_order(wrong,134)),
         'Omitted central-body spectator offset was not detected')
    return {'original_port_endpoints':111,'distinct_stage_symbols':1998,'directed_raw_port_uses':15984,'complete_target_bases':4218,
            'central_body_spectator_offset_control':True}

def mod(x,m):
    x=F(x);return x.numerator*pow(x.denominator,-1,m)%m
def run_row(word,row,m):
    a=list(row)
    for op in word:
        kind,i=op[:2]
        if kind=='swap':j=op[2];a[i],a[j]=a[j],a[i]
        elif kind=='add':a[i]=(a[i]+mod(op[3],m)*a[op[2]])%m
        else:a[i]=a[i]*mod(op[2],m)%m
    return a
def low_matrix(n,q,seed):
    a=[[int(i==j) for j in range(n)] for i in range(n)]
    for k in range(2*n+1):
        i=(k+seed)%n;j=(i+1+k%(n-1))%n;c=(k*k+seed)%q
        a[i]=[(x+c*y)%q for x,y in zip(a[i],a[j])]
    return a
def affine_map(low,high,s,word,q,w):
    raw=multiply(low,s);h=[[mod(x,q) for x in r] for r in raw]
    carry=[[(x-y)/q for x,y in zip(r,t)] for r,t in zip(raw,h)]
    need(all(dyadic(x) for r in carry for x in r),'Carry outside dyadic localization')
    m=q**(w-1)
    if w==1:return h,[[0]*len(s) for _ in s],carry
    y=[[(a+mod(c,m))%m for a,c in zip(run_row(word,r,m),cr)] for r,cr in zip(high,carry)]
    return h,y,carry
def case_checks(root,matrices,ports):
    cases=json.loads((root/'CASES.json').read_text());need(len(cases)==25,'Constructor certificate count')
    modular=coordinates=0;ordered_sites=0;noncommuting=False;wrong_guard=False;cube=[]
    for row in cases:
        n=row['n'];expected=semantic(row['expected'],matrices,ports)
        need(len(expected)==n and all(len(r)==n for r in expected),'Declared complete dimension')
        c=recount(row['word'],n)
        need(c==row['count']==recipe_count(row['recipe']),'Concrete/structural count disagreement '+row['label'])
        need(word_matrix(row['word'],n)==expected,'Independent matrix constructor '+row['label'])
        inv=invert_word(row['word']);actual_inv=word_matrix(row['inverse_word'],n)
        need(recount(inv,n)==c and actual_inv==inverse(expected) and multiply(expected,actual_inv)==eye(n),'Inverse constructor scope')
        ordered=lower_word(row['word'])
        need(all(op[0]!='add' or op[1]>op[2] for op in row['ordered_word']),'Unpaid earlier target')
        need(word_matrix(ordered,n)==word_matrix(row['ordered_word'],n)==expected,'Lowering changed endpoint')
        need(recount(ordered,n)['swaps']==c['swaps']+2*c['upper'],'Upper swaps missing')
        need(row['physical_per_direction']==bill(c,n),'Full-field invoice changed')
        ordered_sites+=c['upper']
        if row['label']=='noncommuting_product':
            a,b=[semantic(x,matrices,ports) for x in row['expected']['children']]
            noncommuting=multiply(b,a)!=expected
        if row['label']=='nonorthogonal_guard':
            child=row['expected']['children'];s=semantic(child[0],matrices,ports);cbase=semantic(child[1],matrices,ports)
            k=row['expected']['rank'];m=len(cbase);diag=[[F(i==j and i<k) for j in range(m)] for i in range(m)]
            badsector=multiply(multiply(inverse(cbase),diag),cbase)
            badinverse=plus(tensor(inverse(s),badsector),tensor(eye(len(s)),plus(eye(m),badsector,-1)))
            wrong_guard=badinverse!=actual_inv
        for q,w,seed in product((3,5,11),(1,2,3),(0,1)):
            low=low_matrix(n,q,seed);m=q**(w-1);wholemod=q**w
            high=[[(7*i+11*j+seed*(i+2)*(j+1))%m for j in range(n)] for i in range(n)]
            h,y,carry=affine_map(low,high,expected,ordered,q,w)
            whole=[[a+q*x for a,x in zip(r,t)] for r,t in zip(low,high)]
            direct=[[mod(x,wholemod) for x in r] for r in multiply(whole,expected)]
            need([[a+q*x for a,x in zip(r,t)] for r,t in zip(h,y)]==direct,'Generated full low/high reconstruction')
            returned,xback,ci=affine_map(h,y,actual_inv,lower_word(inv),q,w)
            need(returned==low and xback==high,'Generated same-owner inverse return')
            need(ci==[[-x for x in r] for r in multiply(carry,actual_inv)],'Generated exact inverse cocycle')
            modular+=1;coordinates+=n*n
        if n==2:
            # Complete high-row cube, extended by exterior prefixes and suffixes.
            side=3;images={}
            for x in product(range(side),repeat=n):
                y=tuple(run_row(ordered,x,side));need(y not in images,'Generated word collision');images[y]=x
            records={(p,x,z):bytes((p,*x,z,0,255)) for p,x,z in product(range(2),images.values(),range(3))}
            moved={(p,tuple(run_row(ordered,x,side)),z):payload for (p,x,z),payload in records.items()}
            returned={(p,tuple(run_row(inv,y,side)),z):payload for (p,y,z),payload in moved.items()}
            need(returned==records,'Generated opaque record/spectator return');cube.append(len(records))
    need(noncommuting and wrong_guard,'Orientation controls were vacuous')
    # Non-idempotent sectors do not preserve products.
    a=matrices['control/diagonal'];e=matrix([[2,0],[0,0]])
    functor=lambda s:plus(tensor(s,e),tensor(eye(2),plus(eye(2),e,-1)))
    need(multiply(e,e)!=e and multiply(functor(a),functor(a))!=functor(multiply(a,a)),'Non-idempotent rejection control')
    # These are exactly the entries of the short-repair failure's reduction column.
    entries=(7,17)
    need(not any(unit(x) for x in entries) and not any(unit(a+c*b) for a,b in (entries,entries[::-1]) for c in (1,-1,2,-2)),'False universal short pivot control')
    # Source alphabet closed under elementary inversion, not under dense entry multiplication.
    return {'constructor_cases':len(cases),'full_prime_power_maps':modular,'full_address_coordinates':coordinates,
            'opaque_spectator_records':sum(cube),'earlier_target_sites':ordered_sites,
            'controls':{'wrong_product_order':noncommuting,'wrong_inverse_sector_basis':wrong_guard,
                        'non_idempotent_sector':True,'false_short_pivot_rule':True}}

def alphabet_check(root):
    expected=json.loads((root/'ALPHABET.json').read_text());adds=set();scales=set()
    rows=json.loads((root/'SEEDS.json').read_text())['seeds']+json.loads((root/'DERIVED-BASES.json').read_text())
    for row in rows:
        for op in row['word']:
            if op[0]=='add':adds|={F(op[3]),-F(op[3])}
            elif op[0]=='scale':scales|={F(op[2]),1/F(op[2])}
    need(adds==set(map(F,expected['addition_coefficients'])) and scales==set(map(F,expected['scale_coefficients'])),'Incomplete inversion-closed linear alphabet')
    need(len(adds)==94 and len(scales)==15,'Alphabet size changed')
    return {'addition_alphabet':len(adds),'scale_alphabet':len(scales)}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--author',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    root=args.author.resolve();produced,native,caller,bases,refs,raw,ports=source_data(root)
    matrices,counts,words,bypair=seeds_and_bases(root,native,bases,refs,raw,ports)
    result={'status':'PASS_INDEPENDENT_GENERATED_ROUTE_LEDGER','proof_sha256':PROOF,
        'source_seeds':755,'controls_separate_from_sources':3,'derived_complete_bases':513,
        **caller_counts(root,caller,ports,counts,words),**case_checks(root,matrices,ports),**alphabet_check(root),
        'python':sys.version.split()[0],
        'method':'independent right-column matrix actions; direct dense semantic constructors; no author module import',
        'scope':'fixed finite generated-word grammar and exact paid interface; no literal route machine, growing outer or full selected compiler execution'}
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
