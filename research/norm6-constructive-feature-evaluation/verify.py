"""Independent polynomial certificates and complete actual-Gram feature evaluation."""
import hashlib,json,sys
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations,product
sys.path.insert(0,str(Path(__file__).resolve().parent))
import model
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]


def need(ok,message):
    if not ok: raise ValueError(message)


def add(poly,key,value):
    poly[key]=poly.get(key,Q(0))+value
    if not poly[key]:del poly[key]


def expansion(key):
    kind,*a=key
    if kind=='f':return {(a[0],)*3:Q(1,3),(a[0],):Q(-1,3)}
    if kind=='l':return {(a[0],):Q(1)}
    if kind=='s':return {tuple(sorted((a[0],a[0],a[1]))):Q(1)}
    return {tuple(a):Q(1)}


def check_relation(pivot,row,g,expand=expansion):
    polynomial=expand(pivot)
    for key,c in row.items():
        for monomial,value in expand(key).items():add(polynomial,monomial,-c*value)
    quotient={key[0]:-value/6 for key,value in polynomial.items() if len(key)==1}
    expected={}
    for i,c in quotient.items():
        add(expected,(i,),-6*c)
        for j in range(48):
            for k in range(48):add(expected,tuple(sorted((i,j,k))),c*g[j][k])
    need(polynomial==expected,'independent complete polynomial ideal identity')
    return len(polynomial),len(quotient)


def source_fixture(g):
    out=[]
    for weight in (1,2):
        for indices in combinations(range(48),weight):
            for tail in product((-1,1),repeat=weight-1):
                x=[0]*48
                for i,v in zip(indices,(1,)+tail):x[i]=v
                if sum(x[i]*g[i][j]*x[j] for i in indices for j in indices)==6:out.append(x)
    return out


def rejects(fn):
    try:fn()
    except ValueError:return
    raise ValueError('mutant accepted')


def run():
    manifest=json.loads((HERE/'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage']=='input':
            need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'input source hash')
    g=json.loads((ROOT/'research/norm6-dyadic-decoder/sources/P48p-GRAM.json').read_text())
    compiled=model.compile_features(g);old,keep,solved,anchor=compiled
    identities=[check_relation(p,row,g) for p,row in solved.items()]
    # Independent triangle sums bind coefficient height and each target accumulator.
    masses={k:4 for k in keep};scaled=[]
    for row in solved.values():
        for k,c in row.items():
            need((4*c).denominator==1,'quarter-integral coefficient')
            masses[k]+=abs(4*c);scaled.append(abs(4*c))
    need(max(scaled)==48 and max(masses.values())==52,'actual transform coefficient bounds')
    shell=source_fixture(g);need(len(shell)==26,'original actual Gram fixture')
    source_rows=[[(k,model.source_value(k,x)) for k in keep if model.source_value(k,x)] for x in shell]
    ys=shell+[[((i+3)*(seed+7)%11)-5 for i in range(48)] for seed in range(12)]
    pairs=0;max_value=0
    for y in ys:
        target=model.evaluate(g,compiled,y)
        v=[sum(g[i][j]*y[j] for j in range(48)) for i in range(48)]
        vmax=max(1,max(map(abs,v)))
        need(max(map(abs,target.values()))<=104*vmax**3,'computed accumulator height')
        for x,sparse in zip(shell,source_rows):
            got=Q(sum(value*target[k] for k,value in sparse),256)
            t=sum(x[i]*g[i][j]*y[j] for i in range(48) for j in range(48))
            need(got==Q(t**3-4*t,192),'complete compressed feature pairing')
            pairs+=1;max_value=max(max_value,abs(got))
    pivot=next(iter(solved));damaged=dict(solved[pivot]);k=next(iter(damaged));damaged[k]+=Q(1,4)
    rejects(lambda:check_relation(pivot,damaged,g))
    # Replacing exact integer-valued cubic by the homogeneous cube loses its linear correction.
    def bad_cubic(key):
        if key[0]=='f':return {(key[1],)*3:Q(1,3)}
        return expansion(key)
    rejects(lambda:check_relation(pivot,solved[pivot],g,bad_cubic))
    outside=[0]*48;outside[anchor]=1
    p=('l',anchor);need(model.source_value(p,outside)!=sum(c*model.source_value(k,outside) for k,c in solved[p].items()),'outside norm6 restriction')
    target=model.evaluate(g,compiled,shell[0]);x=shell[0]
    numerator=sum(model.source_value(k,x)*target[k] for k in keep)
    need(numerator==256 and Q(numerator,64)!=1,'quarter-grid normalization control')
    altered=[row[:] for row in g];altered[0][0]=7
    rejects(lambda:model.compile_features(altered))
    # Rational linear elimination x_i=(x_i G x)/6 is not a dyadic feature compiler.
    need(Q(1,6).denominator & (Q(1,6).denominator-1)!=0,'odd-denominator shortcut control')
    serial=[[list(p),[[list(k),str(v)] for k,v in sorted(row.items())]] for p,row in sorted(solved.items())]
    return {'status':'PASS_NORM6_CONSTRUCTIVE_FEATURES','bounds':model.bounds(g,compiled),
            'polynomial_relations':len(identities),'expanded_nonzeros':sum(a for a,b in identities),
            'maximum_relation_quotient_support':max(b for a,b in identities),'shell_vectors':len(shell),
            'complete_pairings':pairs,'transform_sha256':hashlib.sha256(json.dumps(serial,separators=(',',':')).encode()).hexdigest(),
            'controls':6,'full_shell_enumerated':False,'physical_supplier':False}


if __name__=='__main__':
    result=run()
    if '--record' in sys.argv:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:need(json.dumps(result,sort_keys=True)==json.dumps(json.loads((HERE/'RESULT.json').read_text()),sort_keys=True),'typed frozen result equality')
    print(json.dumps(result,sort_keys=True))
