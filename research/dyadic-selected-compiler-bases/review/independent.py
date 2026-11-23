"""Independent exact oracle: finite quotient groups, complete modular bases,
and full GL elimination. Never imports the author's localized.py/checker.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha1, sha256
from itertools import product
from math import lcm
from pathlib import Path
import argparse
import gzip
import json
import sys
import time

PROOF_SHA = '080be9adb3d9a6f2bd58be334881d7ce7c3be691b49c7fb451705917d92a1283'


def require(ok, why):
    if not ok: raise AssertionError(why)


def ident(n): return [[F(i==j) for j in range(n)] for i in range(n)]
def transpose(a): return [list(c) for c in zip(*a)]
def sub(a,b): return [[x-y for x,y in zip(r,s)] for r,s in zip(a,b)]
def mm(a,b):
    bt = transpose(b)
    return [[sum(x*y for x,y in zip(r,c)) for c in bt] for r in a]
def diag(n, selected):
    selected=set(selected)
    return [[F(i==j and i in selected) for j in range(n)] for i in range(n)]
def tag(a): return tuple(tuple(r) for r in a)
def kron(a,b): return [[x*y for x in r for y in s] for r in a for s in b]
def plus(a,b): return [[x+y for x,y in zip(r,s)] for r,s in zip(a,b)]


def inverse(a):
    n=len(a)
    require(all(len(r)==n for r in a), 'inverse requires a complete square basis')
    rows=[[F(x) for x in r]+ident(n)[i] for i,r in enumerate(a)]
    for col in range(n):
        candidates=[i for i in range(col,n) if rows[i][col]]
        require(candidates,'singular complete basis')
        # Reverse pivot selection intentionally differs from the author's engine.
        p=candidates[-1];rows[col],rows[p]=rows[p],rows[col]
        value=rows[col][col];rows[col]=[x/value for x in rows[col]]
        for i in range(n):
            if i!=col:
                value=rows[i][col]
                rows[i]=[x-value*y for x,y in zip(rows[i],rows[col])]
    return [r[n:] for r in rows]


def determinant(a):
    n=len(a)
    require(all(len(r)==n for r in a),'determinant requires square matrix')
    if not n:return F(1)
    scale=lcm(*(F(x).denominator for r in a for x in r))
    m=[[int(F(x)*scale) for x in r] for r in a]
    sign,previous=1,1
    for k in range(n-1):
        p=next((i for i in range(k,n) if m[i][k]),None)
        if p is None:return F(0)
        if p!=k:m[k],m[p]=m[p],m[k];sign=-sign
        pivot=m[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                value=m[i][j]*pivot-m[i][k]*m[k][j]
                require(value%previous==0,'Bareiss division failed')
                m[i][j]=value//previous
            m[i][k]=0
        previous=pivot
    return F(sign*m[-1][-1],scale**n)


def power_two(n): return n>0 and n&(n-1)==0
def dyadic(x):return power_two(F(x).denominator)
def unit(x):return bool(x) and dyadic(x) and power_two(abs(F(x).numerator))


def gram_columns(a, order):
    """Independent basis selection by rational Gram-Schmidt, not lattice reduction."""
    original=transpose(a);orthogonal=[];chosen=[]
    for j in order:
        v=list(original[j])
        for w in orthogonal:
            ratio=sum(x*y for x,y in zip(v,w))/sum(x*x for x in w)
            v=[x-ratio*y for x,y in zip(v,w)]
        if any(v):
            chosen.append(j);orthogonal.append(v)
    return [[r[j] for j in chosen] for r in a],chosen


def complete_basis(p, reverse=False):
    n=len(p);order=tuple(reversed(range(n))) if reverse else tuple(range(n))
    x,ix=gram_columns(p,order);y,iy=gram_columns(sub(ident(n),p),order)
    return [a+b for a,b in zip(x,y)],len(ix),(ix,iy)


def quotient_index(p):
    """Compute [Z^n:im(sP)+im(s(I-P))] by exact finite subgroup enumeration.

    Since sI is in that lattice, its index is s^n / |L mod s|. Modulo s,
    the complementary columns are negatives of the sP columns. No basis
    construction or Euclidean lattice algorithm is involved.
    """
    n=len(p);s=lcm(*(F(x).denominator for row in p for x in row))
    generators=[tuple(int(s*x)%s for x in col) for col in transpose(p)]
    group={tuple([0]*n)}
    for g in generators:
        group={tuple((x+k*y)%s for x,y in zip(h,g)) for h in group for k in range(s)}
    require(s**n%len(group)==0,'finite quotient order does not divide s^n')
    return s,s**n//len(group),len(group)


def mod(a,m):return [[F(x).numerator*pow(F(x).denominator,-1,m)%m for x in r] for r in a]
def mproduct(a,b,m):return [[x%m for x in r] for r in mm(a,b)]


def unit_eliminate(a,q,w):
    """Gauss-Jordan over Z/q^w using only actual q-unit pivots."""
    modulus=q**w;n=len(a);a=mod(a,modulus);ops=[]
    for k in range(n):
        candidates=[i for i in range(k,n) if a[i][k]%q]
        require(candidates,'invertible local-ring block has no unit pivot')
        p=candidates[-1]
        if p!=k:a[p],a[k]=a[k],a[p];ops.append(('swap',p,k))
        scale=pow(a[k][k],-1,modulus)
        a[k]=[x*scale%modulus for x in a[k]];ops.append(('scale',k,scale))
        for i in range(n):
            if i!=k and a[i][k]:
                c=-a[i][k]%modulus
                a[i]=[(x+c*y)%modulus for x,y in zip(a[i],a[k])]
                ops.append(('add',i,k,c))
    require(a==mod(ident(n),modulus),'local-ring elimination endpoint differs')
    return ops


def source_catalogue(source):
    native=json.loads(gzip.decompress((source/'retained/BIT-NATIVE-WORD.json.gz').read_bytes()))
    receipt=json.loads((source/'retained/EFREE-RESULT.json').read_text())
    frames={};raw_det=Counter()
    for label,row in native['frames'].items():
        g=transpose(row['B']+row['A']);gi=inverse(g);d=determinant(g)
        require(unit(d) and mm(g,gi)==ident(8),'raw complete frame is not dyadic invertible')
        p=mm(mm(g,diag(8,range(row['dim']))),gi)
        require(mm(p,p)==p and p==transpose(p),'raw projector identity failed')
        frames[int(label)]=(p,row['dim']);raw_det[str(d)]+=1
    moves=[tuple(e[2:]) for e in native['program'] if e[0]=='MOVE']
    helpers=[(native['start'][i],native['final'][i]) for i in range(222,native['public'])]
    differences={};pair_count=0
    for a,b in sorted(set(moves+helpers)):
        a,b=sorted((a,b),key=lambda i:frames[i][1]);q,r=frames[a];p,s=frames[b]
        require(mm(p,q)==q and mm(q,p)==q,'selected source difference is not nested')
        d=sub(p,q);require(mm(d,d)==d,'nested difference failed idempotence')
        require(mm(d,q)==mm(q,d)==[[F(0)]*8 for _ in range(8)],'smaller image missing from kernel')
        differences.setdefault(tag(d),{'matrix':d,'pair':(a,b),'rank':s-r})
        pair_count+=1
    # Independent bitset scalar-circuit replay, retaining every public owner.
    # The selected raw CLEAR contract permits nonzero owned erasure. It is
    # explicitly retained by #7840, Section 2, and is not a zero-retirement claim.
    fields={i:1<<i for i in range(native['public'])}
    charts=dict(enumerate(native['start']))
    private=set();clear_count=0;nonzero_clears=0
    for e in native['program']:
        op,*args=e
        if op=='ADD':
            a,b,c=args
            require(a in fields and b in fields and charts[a]==charts[b]==c,
                    'ADD does not join the advertised current charts')
            fields[a]^=fields[b]
        elif op=='SWAP':
            a,b=args
            require(a in fields and b in fields,'SWAP requires two live fields')
            fields[a],fields[b]=fields[b],fields[a]
            charts[a],charts[b]=charts[b],charts[a]
        elif op=='INIT':
            a,c=args
            require(a not in fields and a>=native['public'],'raw owner alias')
            fields[a]=0;charts[a]=c;private.add(a)
        elif op=='CLEAR':
            a,c=args
            require(a in private and charts[a]==c,'CLEAR does not own its current field')
            clear_count+=1;nonzero_clears+=bool(fields[a])
            del fields[a];del charts[a];private.remove(a)
        elif op=='MOVE':
            a,b,c=args
            require(a in fields and charts[a]==b,'MOVE loses its incoming chart')
            charts[a]=c
        else:raise AssertionError('unclassified raw instruction')
    require(not private and set(fields)==set(range(native['public'])),
            'raw program leaked owned fields or retired a public field')
    require(tuple(charts[i] for i in range(native['public']))==tuple(native['final']),
            'raw final chart differs')
    require(clear_count==nonzero_clears==native['owned_fields']==237,
            'retained nonzero owned erasure census changed')
    for i in range(native['public']):
        expected=(1<<i)^((1<<(i-111)) if 111<=i<222 else 0)
        require(fields[i]==expected,'source coupled scalar support changed')
    return native,receipt,frames,list(differences.values()),dict(raw_det),pair_count,nonzero_clears


def route_controls():
    q=3;m=9
    rows=[((a,b),(c,d)) for a,b,c,d in product(range(q),repeat=4) if (a*d-b*c)%q]
    s=[[1,1],[0,1]];si=mod(inverse(s),q)
    seen={tag(g):i for i,g in enumerate(rows)}
    same=0;different=None
    for g in rows:
        h=mproduct(g,s,q);back=mproduct(h,si,q)
        require(tag(back)==tag(g),'whole-cover inverse failed')
        # A coupled ADD reads X at the same old row only when both routes agree.
        require(tag(mproduct(mproduct(g,s,q),si,q))==tag(g),'same coupled route failed')
        same+=1
        if tag(h)!=tag(g) and different is None:
            different={'parent_row':g,'wrong_source_row':h,
                       'parent_payload':seen[tag(g)],'wrong_payload':seen[tag(h)]}
    require(different is not None,'unequal coupled routes were not detected')
    restricted=[[1,3],[0,1]]
    unit_eliminate(restricted,3,2)
    # A lower/P/lower first row has second entry either zero or a unit.
    units=[x for x in range(m) if x%3]
    possible={0}|{a*b%m for a in units for b in units}
    require(3 not in possible,'ordered-shear obstruction disappeared')
    pivot=[[3,1],[2,1]]
    ops=unit_eliminate(pivot,3,2)
    require(ops[0][0]=='swap','nonunit prescribed pivot was not replaced')
    return {'same_coupled_rows':same,'different_route_witness':different,
            'ordered_shear_mod9_forbidden_top_right':3,'full_GL_restricted_matrix_passed':True,
            'fixed_pivot_control_operations':ops}


def sector_controls():
    b=[[1,1],[0,1]];e=mm(mm(b,diag(2,[0])),inverse(b))
    s=[[2,F(1,2)],[0,1]];t=[[1,0],[3,1]]
    def embed(x,sector):return plus(kron(x,sector),kron(ident(2),sub(ident(2),sector)))
    ls,lt=embed(s,e),embed(t,e)
    require(mm(ls,lt)==embed(mm(s,t),e),'nonorthogonal restricted-sector multiplication failed')
    require(mm(ls,embed(inverse(s),e))==ident(4),'restricted-sector inverse failed')
    require(unit(determinant(ls)),'restricted-sector determinant has an odd divisor')
    bad=[[1,1],[1,0]]
    require(mm(embed(s,bad),embed(inverse(s),bad))!=ident(4),
            'non-idempotent sector control did not fail')
    return {'nonorthogonal_idempotent':e,'determinant':determinant(ls),
            'non_idempotent_sector_rejected':True}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();source=args.source.resolve();started=time.monotonic()
    require(sha256((source/'PROOF.md').read_bytes()).hexdigest()==PROOF_SHA,'frozen author proof moved')
    origins=json.loads((source/'ORIGINS.json').read_text())
    for row in origins['files']:
        data=(source/row['local']).read_bytes()
        require(sha256(data).hexdigest()==row['sha256'],'source SHA mismatch')
        require(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],
                'source Git blob mismatch')
    native,receipt,frames,diffs,raw_det,pairs,nonzero_clears=source_catalogue(source)
    expected=json.loads((source/'EVIDENCE.json').read_text())
    index_hist=Counter();alternate_det=Counter();modular=0;max_group=0;reverse_failures=[]
    records=[];by_rank={};port_count=0
    for item in diffs:
        p,r=item['matrix'],item['rank'];s,index,group=quotient_index(p)
        index_hist[str(index)]+=1;max_group=max(max_group,group)
        require(power_two(index),'finite quotient produced odd lattice index')
        b,rank,selection=complete_basis(p)
        bi=inverse(b);d=determinant(b)
        require(rank==r and unit(d),'independent source basis not dyadic-complete')
        require(mm(mm(bi,p),b)==diag(8,range(r)),'both complete source summands failed')
        alternate_det[str(d)]+=1
        br,_,_=complete_basis(p,reverse=True);dr=determinant(br)
        if not unit(dr):reverse_failures.append({'pair':item['pair'],'determinant':dr})
        for q in (3,5,7,11):
            for w in (1,2,3):
                m=q**w;bp,bip,pp=mod(b,m),mod(bi,m),mod(p,m)
                require(mproduct(bp,bip,m)==mod(ident(8),m),'modular complete inverse failed')
                require(mproduct(mproduct(bip,pp,m),bp,m)==mod(diag(8,range(r)),m),
                        'prime-power both-summands identity failed')
                unit_eliminate(b,q,w);modular+=1
        by_rank.setdefault(r,b)
        other=by_rank[r];matcher=mm(b,inverse(other));mi=inverse(matcher)
        target=mm(mm(other,diag(8,range(r))),inverse(other))
        require(mm(mm(matcher,target),mi)==p,'complete equal-rank matcher failed')
        require(mm(mm(matcher,sub(ident(8),target)),mi)==sub(ident(8),p),'matcher lost kernel')
        # Include a non-prefix image split and all newly inactive image columns.
        selected=tuple(range(r-1,-1,-2));order=selected+tuple(i for i in range(8) if i not in selected)
        child=mm(mm(b,diag(8,selected)),bi);bc=[[row[i] for i in order] for row in b]
        require(mm(mm(inverse(bc),child),bc)==diag(8,range(len(selected))),'carried child kernel failed')
        records.append({'pair':item['pair'],'rank':r,'scale':s,'lattice_index':index,
                        'quotient_image_order':group,'alternative_basis':b,'basis_determinant':d})
    advertised=Counter()
    for det,count in expected['localized_basis_determinants'].items():advertised[str(abs(int(det)))]+=count
    require(index_hist==advertised,'independent finite-group lattice indices differ from author determinants')
    for chart in receipt['source']['charts']:
        u=[[F(x) for x in row] for row in chart['basis']];ui=inverse(u)
        require(unit(determinant(u)),'port chart lost dyadic invertibility')
        head=mm(mm(u,diag(8,[0])),ui)
        require(head==frames[chart['input_frame']][0],'actual port head differs')
        require(sub(ident(8),head)==frames[chart['output_frame']][0],'actual port body differs')
        # Essential 8+7 block, using the actual port basis and its inverse.
        ex=[row+[F(0)]*7 for row in u]+[[F(0)]*8+row for row in ident(7)]
        order=(0,*range(8,15),*range(1,8));pi=[[F(i==order[j]) for j in range(15)] for i in range(15)]
        route=mm(mm(ex,pi),inverse(ex));body=mm(mm(ex,diag(15,range(1,8))),inverse(ex))
        require(mm(route,route)==ident(15),'actual port route not involutive')
        require(mm(mm(route,body),route)==diag(15,range(8,15)),'actual whole body route failed')
        port_count+=1
    p=sub(frames[270][0],frames[2][0]);b,r,_=complete_basis(p)
    bad=[row[:] for row in b]
    for row in bad:row[r]*=3
    require(mm(mm(inverse(bad),p),bad)==diag(8,range(r)),'bad complete basis no longer a rational basis')
    require(not unit(determinant(bad)) and determinant(bad).numerator%3==0,
            'odd-rescaled kernel control did not create a bad prime')
    require(frames[270][1]-frames[2][1]==r and 8-r>8-frames[270][1],
            'smaller image was not needed in difference kernel')
    controls={'actual_pair_odd_kernel_rescaling':{'pair':[2,270],'rank':r,'determinant':determinant(bad),
              'difference_kernel_dimension':8-r,'larger_projector_kernel_dimension':8-frames[270][1]},
              'routes':route_controls(),'sector':sector_controls()}
    require(sha256((source/'PROOF.md').read_bytes()).hexdigest()==PROOF_SHA,'author proof changed during review')
    def encode(x):
        if isinstance(x,F):return str(x)
        if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
        if isinstance(x,(list,tuple)):return [encode(v) for v in x]
        return x
    args.output.parent.mkdir(parents=True,exist_ok=True)
    catalogue=args.output.parent/'INDEPENDENT-BASES.json'
    catalogue.write_text(json.dumps(encode(records),indent=2)+'\n')
    result={'status':'PASS_INDEPENDENT_DYADIC_REVIEW','author_proof_sha256':PROOF_SHA,
            'raw_frames':len(frames),'unique_source_pairs':pairs,'nested_differences':len(diffs),
            'raw_frame_determinants':raw_det,'finite_group_lattice_indices':dict(index_hist),
            'maximum_enumerated_quotient_image':max_group,'prime_power_cases':modular,
            'independent_basis_determinants':dict(alternate_det),'reversed_column_failures':reverse_failures,
            'actual_port_routes':port_count,'source_scalar_coupled_pairs':111,
            'retained_nonzero_owned_clear_sites':nonzero_clears,
            'negative_controls':controls,'basis_catalogue_sha256':sha256(catalogue.read_bytes()).hexdigest(),
            'engine':'stdlib Fraction/Bareiss/Gram-Schmidt plus finite subgroup enumeration; no author lattice imports'}
    args.output.write_text(json.dumps(encode(result),indent=2)+'\n')
    print(json.dumps({**{k:result[k] for k in ('status','raw_frames','nested_differences','prime_power_cases')},
                      'seconds':time.monotonic()-started}))


if __name__=='__main__':main()
