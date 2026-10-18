"""Default-precision false brackets and a fail-closed repair. Apache-2.0."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
from fractions import Fraction as F
P=Path(__file__).resolve().parent;R=P.parents[1];sys.path.insert(0,str(P))
from repair import bracket,classify,profile_oracle,need
BASE='ce7ad1b6ab09452c3478723a2e96ed5ff212dc08'
COMMIT='07730cd8302c378607259a9ad0efb73e0b57a2f2'
REQUIRED={'docs/research/community-batch1099-review.md','research/community-batch1099-audit/pr1048-metadata.json','research/community-batch1099-audit/logs/batch1099-1048-finding.json','research/community-batch1099-audit/check_pr1048_counterexample.py'}
LOCAL={'vendor/bitprof.py','vendor/NOTICE.md','vendor/LICENSE','BASE-SELECTED.json'}

def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def normalized(p):return p.read_bytes().replace(b'\r\n',b'\n')
def sources(m=None):
    if m is None:m=json.loads((P/'SOURCES.json').read_bytes())
    need(m['base']==BASE and m['original_commit']==COMMIT,'base/head binding')
    need(set(m['repository_files'])==REQUIRED and set(m['package_files'])==LOCAL,'mandatory inventory')
    for base,files in ((R,m['repository_files']),(P,m['package_files'])):
        for name,h in files.items():need(sha(normalized(base/name))==h,'source pin '+name)
    selected=json.loads((P/'BASE-SELECTED.json').read_bytes())
    need(selected['kappa']=='836330098538459/500000000000000000','frozen selected kappa')
    metadata=json.loads((R/'research/community-batch1099-audit/pr1048-metadata.json').read_bytes())
    need(COMMIT in [c['oid'] for c in metadata['commits']],'frozen reviewed PR1048 commit')
    spec=importlib.util.spec_from_file_location('original_bitprof',P/'vendor/bitprof.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def iroot(value,degree):
    lo=0;hi=1<<((value.bit_length()+degree-1)//degree)
    while hi-lo>1:
        mid=(lo+hi)//2
        if mid**degree<=value:lo=mid
        else:hi=mid
    return lo

def fixture(surcharge):
    m=9;W=10**64;factor=F(1)+F(32*m*m,10**16) if surcharge else F(1)
    A=(m*W*factor.denominator)**10;B=3*factor.numerator**10
    N=iroot(A//B,10)
    need(B*N**10<A<B*(N+1)**10,'strict algebraic floor')
    return m,W,N,factor

def compact(lo,hi,normalizer):
    # Outward rational decimal enclosure: small, reviewable and exact.
    scale=10**80;lo=lo/normalizer*scale;hi=hi/normalizer*scale
    return [str(F(lo.numerator//lo.denominator,scale)),str(F(-(-hi.numerator//hi.denominator),scale))]

def check_repaired(result,oracle,expected):
    need(result['status']=='CERTIFIED','repair did not certify')
    need(list(map(F,result['certified_bracket']))==expected,'wrong repaired bracket')
    for side,q,terms in zip((-1,1),expected,result['endpoint_terms']):
        need(classify(*oracle(q,terms))==side,'final endpoint independently rechecked')

def legacy_nomination(original,n,m,W,surcharge):
    # Repeat only the unchanged source's floating nomination to separate the
    # undecided-sign failure from any possible nomination coverage failure.
    D=original.profile_deficit(n,m,W);lo,hi=0.0,0.1
    for _ in range(100 if surcharge else 80):
        mid=(lo+hi)/2;value=original.fee_float(n,m,mid)
        if surcharge:value+=original.surcharge_num(n,m)*(m**mid)/original.SURCHARGE_DEN
        if value<D:lo=mid
        else:hi=mid
    scale=10**24;span=10**18
    return [F(max(0,int(lo*scale)-span),scale),F(min(scale//10,int(hi*scale)+span),scale)]

def compute():
    original=sources();rows=[];a0=F(1,20);tick=F(1,10**24)
    for surcharge in (False,True):
        m,W,N,factor=fixture(surcharge)
        for offset in (0,1):
            count=N+offset;n={1:count};oldfn=original.certify_c_bad if surcharge else original.certify_c
            oldlo,oldhi,D=oldfn(n,m,W) # defaults: digits24, terms34; no monkeypatch.
            need((oldlo,oldhi)==(a0-tick,a0),'recorded legacy bracket')
            oracle=profile_oracle(original,n,m,W,surcharge)
            need(classify(*oracle(F(0),34))==-1 and classify(*oracle(F(1,10),34))==1,'original initial sign assertions hold')
            undecided=oracle(a0,34);need(classify(*undecided)==0,'actual ambiguous midpoint')
            result=bracket(oracle,max_terms=136)
            expected=[a0,a0+tick] if offset==0 else [a0-tick,a0]
            check_repaired(result,oracle,expected)
            nomination=legacy_nomination(original,n,m,W,surcharge)
            need(nomination[0]<a0-tick and nomination[1]>a0+tick,'legacy nomination contains both neighboring true brackets')
            need(count*tick>1,'independent neighboring-grid separation')
            rows.append(dict(surcharge=surcharge,offset=offset,m=m,W=W,n={1:count},factor=str(factor),legacy_bracket=[str(oldlo),str(oldhi)],legacy_nomination_bracket=list(map(str,nomination)),legacy_bracket_excludes_root=(offset==0),known_root_side_of_1_over_20='above' if offset==0 else 'below',initial_signs_certified=True,normalized_residual_at_grid_terms34=compact(*undecided,m*W),repair=result))
    # Ordinary small-profile control: the original bracket is already strict.
    n={2:15};m=8;W=4;lo,hi,D=original.certify_c(n,m,W)
    oracle=profile_oracle(original,n,m,W);ordinary=bracket(oracle)
    check_repaired(ordinary,oracle,[lo,hi])
    # A capped undecided calculation must preserve its wider proven bracket.
    m,W,N,_=fixture(False);oracle=profile_oracle(original,{1:N},m,W)
    capped=bracket(oracle,max_terms=34)
    need(capped['status']=='UNRESOLVED_INTERIOR_SIGN','capped ambiguity status')
    l,h=map(F,capped['certified_bracket']);need(l<a0<h,'retained safe bracket contains boundary')
    return dict(status='PASS_DEFAULT_PRECISION_FALSE_BRACKETS_AND_CERTIFIED_REPAIR',base=BASE,original_commit=COMMIT,default_terms=34,default_digits=24,false_brackets=2,neighbor_controls=2,fixtures=rows,ordinary_control=ordinary,capped_control=capped,scope='Abstract rank-profile arithmetic only; no realizable supplier or selected-bound counterexample; PR1048 search and ordering claims remain deferred.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();result=compute()
    if a.write:(P/'EXPECTED.json').write_bytes(enc(result)+b'\n')
    else:need(enc(json.loads((P/'EXPECTED.json').read_bytes()))==enc(json.loads(enc(result))),'typed certificate mismatch')
    print(result['status']);print('false_brackets=2 neighbor_controls=2 original_defaults=34/24')
if __name__=='__main__':main()
