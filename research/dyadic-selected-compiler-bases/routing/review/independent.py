"""Independent descriptor interpreter; never imports route_words or author verifier."""
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256,sha1
import argparse,gzip,json,time

def require(ok,message):
    if not ok:raise ValueError(message)
def identity(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def transpose(a):return [list(c) for c in zip(*a)]
def product(a,b):
    out=[[Q(0) for _ in b[0]] for _ in a]
    for i,row in enumerate(a):
        for k,x in enumerate(row):
            if x:
                for j,y in enumerate(b[k]):
                    if y:out[i][j]+=x*y
    return out
def invert(matrix):
    n=len(matrix);a=[list(row)+identity(n)[i] for i,row in enumerate(matrix)]
    for j in range(n):
        pivots=[k for k in range(j,n) if a[k][j]];require(pivots,'singular matrix')
        k=pivots[-1];a[j],a[k]=a[k],a[j];x=a[j][j];a[j]=[v/x for v in a[j]]
        for k in range(n):
            if k!=j and a[k][j]:
                x=a[k][j];a[k]=[u-x*v for u,v in zip(a[k],a[j])]
    return [row[n:] for row in a]
def binary_power(n):return n>0 and n.bit_count()==1
def dyadic(x):return binary_power(Q(x).denominator)
def dyadic_unit(x):
    x=Q(x);return binary_power(abs(x.numerator)) and binary_power(x.denominator)
def reduce_q(x,m):
    x=Q(x)
    if m==1:return 0
    require(x.denominator%m!=0,'denominator cannot be inverted')
    return x.numerator*pow(x.denominator,-1,m)%m
def negate_operation(op):
    if op[0]=='swap':return list(op)
    if op[0]=='scale':return ['scale',op[1],str(1/Q(op[2]))]
    require(op[0]=='add','unknown operation');return ['add',op[1],op[2],str(-Q(op[3]))]
def apply_matrix(a,ops):
    a=[row[:] for row in a]
    for op in ops:
        kind=op[0]
        if kind=='swap':i,j=op[1:];a[i],a[j]=a[j],a[i]
        elif kind=='scale':i=op[1];c=Q(op[2]);a[i]=[c*x for x in a[i]]
        elif kind=='add':i,j=op[1:3];c=Q(op[3]);a[i]=[x+c*y for x,y in zip(a[i],a[j])]
        else:raise ValueError('unknown operation')
    return a
def expand_scale(c):
    c=Q(c);require(dyadic_unit(c),'non-dyadic scale rejected');out=[]
    if c<0:out.append(Q(-1));c=-c
    while c>1:out.append(Q(2));c/=2
    while c<1:out.append(Q(1,2));c*=2
    # A negative sign may share its first factor, as in the admitted signed alphabet.
    if len(out)>1 and out[0]==-1:out=([-out[1]]+out[2:])
    return out
def lower(ops):
    out=[]
    for op in ops:
        if op[0]=='add' and op[1]<op[2]:
            i,j=op[1:3];out.extend([['swap',i,j],['add',j,i,op[3]],['swap',i,j]])
        elif op[0]=='scale':out.extend([['scale',op[1],str(c)] for c in expand_scale(op[2])])
        else:out.append(list(op))
    require(all(op[0]!='add' or op[1]>op[2] for op in out),'lowered shift uses later control')
    return out
def numeric_rows(rows,ops,modulus):
    a=[list(row) for row in rows]
    for op in ops:
        if op[0]=='swap':
            i,j=op[1:]
            for row in a:row[i],row[j]=row[j],row[i]
        elif op[0]=='scale':
            i=op[1];c=reduce_q(op[2],modulus)
            for row in a:row[i]=row[i]*c%modulus
        else:
            i,j=op[1:3];c=reduce_q(op[3],modulus)
            for row in a:row[i]=(row[i]+c*row[j])%modulus
    return a

def modular_product(a,b,m):
    bb=[[reduce_q(x,m) for x in row] for row in b]
    return [[sum(int(x)*bb[k][j] for k,x in enumerate(row))%m for j in range(len(bb[0]))] for row in a]
def carry_parts(g,s,q):
    exact=product(g,s);h=[[reduce_q(x,q) for x in row] for row in exact]
    c=[[(x-z)/q for x,z in zip(row,hrow)] for row,hrow in zip(exact,h)]
    require(all(dyadic(x) for row in c for x in row),'carry acquired an odd denominator')
    return h,c
def carry_route(g,x,s,ops,q,w):
    h,c=carry_parts(g,s,q);m=q**(w-1);z=numeric_rows(x,ops,m)
    return h,[[(v+reduce_q(t,m))%m for v,t in zip(row,cr)] for row,cr in zip(z,c)],c

def verify_words(catalogue,basis_rows):
    bases={tuple(r['pair']):[[Q(x) for x in row] for row in r['alternative_basis']] for r in basis_rows}
    ranks={tuple(r['pair']):r['rank'] for r in basis_rows};routes=catalogue['routes']
    require(len(routes)==len(bases)==513,'catalogue completeness count')
    require([r['pair'] for r in routes]==[r['pair'] for r in basis_rows],'catalogue changed accepted order or membership')
    prepared=[];totals={};maxima={};repairs=0;wrong_order=0
    for r in routes:
        pair,reference=tuple(r['pair']),tuple(r['reference_pair']);rank=r['rank'];require(rank==ranks[pair]==ranks[reference],'reference rank mismatch')
        s=product(bases[pair],invert(bases[reference]));require(s==[[Q(x) for x in row] for row in r['matrix']],'route matrix not derived from accepted complete bases')
        word=r['elimination_word'];forward=[negate_operation(op) for op in reversed(word)];si=invert(s)
        require(apply_matrix(transpose(s),word)==identity(8),'recorded reduction does not reach identity')
        require(apply_matrix(identity(8),forward)==transpose(s),'forward operation chronology wrong')
        require(apply_matrix(identity(8),word)==transpose(si),'inverse chronology wrong')
        ff,ii=lower(forward),lower(word)
        require(apply_matrix(identity(8),ff)==transpose(s),'lowered forward endpoint wrong')
        require(apply_matrix(identity(8),ii)==transpose(si),'lowered inverse endpoint wrong')
        require(all(dyadic(op[3]) for op in word if op[0]=='add'),'odd addition denominator')
        require(all(dyadic_unit(op[2]) for op in word if op[0]=='scale'),'nonunit scaling')
        for expanded in (ff,ii):
            require(all(Q(op[2]) in (Q(-1),Q(2),Q(-2),Q(1,2),Q(-1,2)) for op in expanded if op[0]=='scale'),'nonprimitive signed scaling')
        counts={k:sum(op[0]==k for op in word) for k in ('swap','scale','add')}
        counts['earlier_target']=sum(op[0]=='add' and op[1]<op[2] for op in word)
        counts['signed_dyadic_scale_atoms']=sum(op[0]=='scale' for op in ff)
        counts['full_ordinary_swaps']=8*sum(op[0]=='swap' for op in ff)
        counts['full_ordered_shifts_with_carry']=8*sum(op[0]=='add' for op in ff)+64
        counts['full_fixed_scalings']=8*counts['scale'];counts['full_signed_dyadic_scale_atoms']=8*counts['signed_dyadic_scale_atoms']
        require(counts==r['counts'],'claimed lowering ledger differs from expanded execution')
        require(sum(op[0]=='swap' for op in ii)*8==counts['full_ordinary_swaps'],'inverse swap ledger differs')
        require(sum(op[0]=='scale' for op in ii)*8==counts['full_signed_dyadic_scale_atoms'],'inverse scaling ledger differs')
        a=transpose(s);pending=list(r['short_repairs'])
        for op in word:
            if pending and op[0]=='add':
                rep=pending[0];j=rep['column'];i,k=op[1:3]
                if (i,k,Q(op[3]))==(rep['target'],rep['source'],Q(rep['coefficient'])) and a[i][j]==Q(rep['old_target']) and a[k][j]==Q(rep['old_source']):
                    require(not any(dyadic_unit(a[t][j]) for t in range(j,8)),'repair claimed where a unit pivot already exists')
                    require(dyadic_unit(a[i][j]+Q(op[3])*a[k][j]),'advertised repair does not create a unit');pending.pop(0);repairs+=1
            a=apply_matrix(a,[op])
        require(not pending,'repair trace not witnessed')
        wrong_order+=apply_matrix(identity(8),[negate_operation(op) for op in word])!=transpose(s)
        for k,v in counts.items():totals[k]=totals.get(k,0)+v;maxima[k]=max(maxima.get(k,0),v)
        prepared.append((r,s,si,ff,ii))
    require(wrong_order>0,'chronology reversal not distinguished')
    return prepared,dict(routes=len(routes),short_pivot_repairs=repairs,reversed_chronology_witnesses=wrong_order,totals=totals,maxima=maxima)

def source_membership(native,basis_rows):
    frames={};ranks={}
    def tag(a):return tuple(tuple(row) for row in a)
    for name,f in native['frames'].items():
        g=transpose([[Q(x) for x in row] for row in f['B']+f['A']]);gi=invert(g);r=f['dim']
        image=[[x if j<r else Q(0) for j,x in enumerate(row)] for row in g]
        frames[int(name)]=product(image,gi);ranks[int(name)]=r
    raw={tag(p) for p in frames.values()};pairs={tuple(e[2:]) for e in native['program'] if e[0]=='MOVE'}
    pairs|={(native['start'][i],native['final'][i]) for i in range(222,native['public'])}
    differences=set()
    for a,b in pairs:
        a,b=sorted((a,b),key=lambda k:ranks[k]);differences.add(tag([[x-y for x,y in zip(r,s)] for r,s in zip(frames[b],frames[a])]))
    accepted=set()
    for row in basis_rows:
        a,b=row['pair'];p=[[x-y for x,y in zip(r,s)] for r,s in zip(frames[b],frames[a])];basis=[[Q(x) for x in r] for r in row['alternative_basis']]
        require(ranks[b]-ranks[a]==row['rank'],'accepted difference rank mismatch')
        expected=[[x if j<row['rank'] else Q(0) for j,x in enumerate(r)] for r in basis]
        require(product(p,basis)==expected,'complete basis fails image/full-kernel source identity');accepted.add(tag(p))
    require(accepted==differences and len(accepted)==513,'accepted catalogue does not equal actual source differences')
    require(len(pairs)==2380 and len(differences-raw)==135,'source pair/nonraw count changed')
    return dict(raw_frames=len(frames),distinct_source_pairs=len(pairs),normalized_differences=len(differences),nonraw_differences=len(differences-raw))

def verify_carries(prepared):
    cases=0;noninteger=0;nonzero=0;composition=0;all_cells=0
    for index,(r,s,si,forward,backward) in enumerate(prepared):
        for q in (3,5,7,11):
            g=[[int(i==j) if i>=j else (index+i+2*j+1)%q for j in range(8)] for i in range(8)]
            h,c=carry_parts(g,s,q);noninteger+=any(x.denominator>1 for row in c for x in row);nonzero+=any(x for row in c for x in row)
            for w in (1,2,3):
                m=q**(w-1);x=[[(index+3*i+5*j+i*j)%m for j in range(8)] for i in range(8)]
                h,y,_=carry_route(g,x,s,forward,q,w)
                gback,xback,_=carry_route(h,y,si,backward,q,w)
                require(gback==g and xback==x,'complete low/high inverse did not restore all 64 fields')
                full=[[a+q*b for a,b in zip(row,xrow)] for row,xrow in zip(g,x)]
                direct=modular_product(full,s,q**w);reconstructed=[[a+q*b for a,b in zip(row,yrow)] for row,yrow in zip(h,y)]
                require(reconstructed==direct,'carry route disagrees with whole matrix multiplication')
                require(numeric_rows(x,forward,m)==modular_product(x,s,m),'lowered high-row word disagrees with direct map')
                cases+=1;all_cells+=64
            t=prepared[(index+1)%len(prepared)][1];st=product(s,t);ht,ct=carry_parts(h,t,q);hst,cst=carry_parts(g,st,q)
            cs_t=product(c,t);combined=[[a+b for a,b in zip(row,tr)] for row,tr in zip(cs_t,ct)]
            require(ht==hst and combined==cst,'exact localized carry cocycle failed');composition+=1
    require(noninteger and nonzero,'carry fixture did not exercise localized/nonzero carries')
    return dict(complete_modular_routes=cases,address_cells=all_cells,prime_powers={'q':[3,5,7,11],'w':[1,2,3]},localized_noninteger_carry_cases=noninteger,nonzero_carry_cases=nonzero,exact_composition_identities=composition,w1_singleton_routes=len(prepared)*4)

def scaling_controls():
    cases=0;records=0
    for q in (3,5,7,11):
        for w in range(4):
            m=q**w;original=[('prefix',x,('payload',x*x+7),'gap','suffix') for x in range(m)]
            buckets=[[record for x,record in enumerate(original) if (2*x)//m==b] for b in (0,1)];pos=[0,0];out=[]
            for y in range(m):
                b=y%2;record=buckets[b][pos[b]];pos[b]+=1;require((2*record[1])%m==y,'binary scale bucket/interleave wrong');out.append(record)
            recovered=[out[(2*x)%m] for x in range(m)]
            require(recovered==original,'inverse scale loses full record');cases+=1;records+=m
    return dict(odd_moduli=cases,complete_records=records,includes_singleton_modulus=True)

def negative_controls(prepared):
    column=[Q(7),Q(17)];require(7*5-2*17==1,'unimodular counterexample malformed')
    require(not any(dyadic_unit(x) for x in column),'counterexample has a unit pivot')
    require(not any(dyadic_unit(column[i]+c*column[1-i]) for i in (0,1) for c in (1,-1,2,-2)),'counterexample admits a short repair')
    g=[[1]];s=[[Q(1,2)]];x=[[1]];h,c=carry_parts(g,s,3);require(c==[[Q(-1,2)]],'localized scalar carry witness changed')
    correct=modular_product([[4]],s,9)[0][0];omit=(h[0][0]+3*reduce_q(Q(1,2),3))%9;floor=(h[0][0]+3*reduce_q(Q(1,2)+(c[0][0].numerator//c[0][0].denominator),3))%9
    require(correct!=omit and correct!=floor,'wrong carry handling not distinguished')
    rejected=False
    try:reduce_q(Q(1,2),2)
    except ValueError:rejected=True
    require(rejected,'prime two not rejected for dyadic denominator')
    fixture=next(t for t in prepared if t[0]['pair']==[11,266]);a=transpose(fixture[1]);pivot=None
    # Follow the deliberately wrong fixed-row policy until its first nonunit pivot.
    for j in range(8):
        if a[j][j] and not dyadic_unit(a[j][j]):pivot=(j,a[j][j]);break
        if not a[j][j]:
            k=next(k for k in range(j+1,8) if a[k][j]);a[j],a[k]=a[k],a[j]
        z=a[j][j];a[j]=[v/z for v in a[j]]
        for k in range(8):
            if k!=j:
                z=a[k][j];a[k]=[u-z*v for u,v in zip(a[k],a[j])]
    require(pivot==(2,Q(3,4)),'fixed-pivot control changed')
    require(reduce_q(pivot[1],3)==0,'fixed third pivot should fail at prime three')
    return dict(outside_catalogue_short_repair_failure={'matrix':[[7,2],[17,5]],'determinant':1,'first_column':[7,17],'tested_coefficients':[1,-1,2,-2]},localized_scalar_carry={'q':3,'S':'1/2','g0':1,'X':1,'carry':'-1/2','correct_mod9':correct,'omitted_carry_result':omit,'floor_carry_result':floor},prime_two_rejected=True,fixed_pivot={'pair':[11,266],'reference_pair':[2,270],'column':2,'value':'3/4','fails_q':3})

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();start=time.monotonic();src=args.source.resolve()
    fixed={'retained/native.json.gz':'51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78','retained/bases.json':'0ea69bbed0979ccbd8f9c2c53b6f74726281bb003c4707abc27fc3015e9c6975','retained/PR7840-PROOF.md':'ddd485f0223cbe69d0319bece17cd7d9034e1aca5ef8535bfba43c034873a88a','CATALOGUE.json':'fd605374cfeb851d3306e6e1778afffc51de508f32658a3d58c523bf066b5054'}
    fixed['PROOF.md']='0fefb696f20f4e30ecf4f8ccefe564f70aaeee5498803877a8965e2534731e3d'
    fixed['retained/PR5052-PROOF.md']='f53db166a3bc3865c08426cf520b402028e34e1e9da2262ae19afa0b157a1c55'
    inputs=json.loads((src/'INPUTS.json').read_text())
    for name,digest in fixed.items():require(sha256((src/name).read_bytes()).hexdigest()==digest,'fixed input changed: '+name)
    for item in inputs['files']:
        data=(src/item['path']).read_bytes();require(len(data)==item['bytes'],'input byte count changed');require(sha256(data).hexdigest()==item['sha256'],'input SHA changed');require(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==item['git_blob'],'input Git blob changed')
    catalogue=json.loads((src/'CATALOGUE.json').read_text());bases=json.loads((src/'retained/bases.json').read_text());prepared,word_report=verify_words(catalogue,bases)
    result={'status':'PASS_INDEPENDENT_FINITE_DYADIC_ROUTING','canonical_base':inputs['canonical_base'],'pinned_inputs':fixed,'method':'Separate exact emitted-word interpreter, independent matrix inversion, expanded directed shifts and signed scales, all 64 localized carry coordinates; no author scientific module imported.','word_checks':word_report,'carry_checks':verify_carries(prepared),'scale_record_checks':scaling_controls(),'negative_controls':negative_controls(prepared)}
    result['source_membership']=source_membership(json.loads(gzip.decompress((src/'retained/native.json.gz').read_bytes())),bases)
    for name,digest in fixed.items():require(sha256((src/name).read_bytes()).hexdigest()==digest,'input changed during review')
    result['seconds']=round(time.monotonic()-start,3);args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'routes':word_report['routes'],'modular_routes':result['carry_checks']['complete_modular_routes'],'seconds':result['seconds']}))
if __name__=='__main__':main()
