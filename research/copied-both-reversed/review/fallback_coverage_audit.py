"""Independent coverage/source audit and replay of every recorded fallback.
This does not rerun all four million primary cases; it binds the complete
reviewed execution receipt and independently recomputes its rescued cases.
All input paths are supplied explicitly; only Python standard library used.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
from math import gcd,isqrt
from pathlib import Path
import argparse,json,sys

REVIEWED_SOURCE_SHA256='8ea33ecedfad214e193aa0beb96f8597d1cdb372481a16a3c36f7f0f58247866'


def replay(left,right,prime):
    a,b,d=23,25,47
    R=list(range(a))+[22]+list(range(a));C=list(range(a))+[0]+list(range(a))
    order=[46]+[i+24 for i in range(1,22)]+[46-i for i in range(22,28)]+[i-26 for i in range(28,45)]+[1,0]
    x=[18*pow(31,-1,prime)%prime if i in left else -24*pow(5,-1,prime)%prime for i in range(a)]
    y=[39*pow(68,-1,prime)%prime if i in right else -26*pow(5,-1,prime)%prime for i in range(b)]
    matrix=[[(int(R[i]==C[j])*x[R[i]]+int(i%b==(j+3)%b)*y[i%b]-1)%prime for j in range(d)] for i in range(d)]
    available=set(range(d));nonzero=0;zeros=0;determinant=1
    for i,c in enumerate(order):
        assert c in available
        value=matrix[i][c]
        if not value:return dict(passed=False,row=i,col=c,nonzero_prefixes=nonzero)
        for j in available:
            if j>c:assert matrix[i][j]==0;zeros+=1
        determinant=determinant*value%prime;nonzero+=1;available.remove(c)
        for r in range(i+1,d):
            if matrix[r][c]:
                ratio=matrix[r][c]*pow(value,-1,prime)%prime
                for j in available:matrix[r][j]=(matrix[r][j]-ratio*matrix[i][j])%prime
                matrix[r][c]=0
    return dict(passed=True,nonzero_prefixes=nonzero,ordered_zeros=zeros,determinant=determinant)


def run(certificate,source,receipt=None):
    if sys.flags.optimize:raise RuntimeError('Run exact audit without -O')
    certificate,source=Path(certificate),Path(source)
    x=json.loads(certificate.read_text());source_hash=sha256(source.read_bytes()).hexdigest()
    assert source_hash==REVIEWED_SOURCE_SHA256,'Source changed after fallback-loop review'
    primes=x['primes'];assert primes==[1000003,2147483647,1000000007]
    for p in primes:
        assert p>2 and all(p%r for r in range(2,isqrt(p)+1))
        assert all(gcd(p,d)==1 for d in x['denominators'])
    left=list(combinations(range(23),3));right=list(combinations(range(25),3))
    pairs=len(left)*len(right)
    assert x['dimensions']==[23,25] and x['left_triples']==len(left) and x['right_triples']==len(right)
    assert x['pairs']==pairs==4073300 and x['nonzero_prefixes']==pairs*47
    assert x['ordered_zero_checks']==pairs*346 and x['unresolved_failures']==0
    fallbacks=x['fallbacks'];assert len(fallbacks)==x['primary_modular_failures']
    indices=[f['index'] for f in fallbacks]
    assert indices==sorted(set(indices)) and all(0<=i<pairs for i in indices)
    by_prime=Counter();checked=[]
    for f in fallbacks:
        i,j=divmod(f['index'],len(right))
        assert tuple(f['left'])==left[i] and tuple(f['right'])==right[j]
        assert f['successful_prime'] in primes[1:]
        first=replay(left[i],right[j],primes[0])
        assert not first['passed'] and [first['row'],first['col']]==f['primary_zero']
        passed=replay(left[i],right[j],f['successful_prime'])
        assert passed['passed'] and passed['nonzero_prefixes']==47 and passed['ordered_zeros']==346
        by_prime[f['successful_prime']]+=1
        checked.append(dict(index=f['index'],primary=first,complete_fallback=passed))
    assert x['successful_pairs_by_prime']==[pairs-len(fallbacks)]+[by_prime[p] for p in primes[1:]]
    artifact_hashes=dict(source=source_hash,certificate=sha256(certificate.read_bytes()).hexdigest())
    if receipt is not None:
        receipt=Path(receipt);r=json.loads(receipt.read_text())
        assert r['exit_code']==0 and r['source_sha256']==source_hash
        assert r['output_sha256']==artifact_hashes['certificate']
        for name in ['pairs','nonzero_prefixes','ordered_zero_checks','primary_modular_failures',
                     'unresolved_failures','successful_pairs_by_prime','primes','denominators']:
            assert r[name]==x[name]
        artifact_hashes['execution_receipt']=sha256(receipt.read_bytes()).hexdigest()
    return dict(status='PASS complete reviewed-source coverage and independent exact fallback replay',
        pairs=pairs,nonzero_prefixes=x['nonzero_prefixes'],ordered_zero_checks=x['ordered_zero_checks'],
        independently_replayed_fallbacks=checked,unresolved_failures=0,artifact_sha256=artifact_hashes,
        scope='Full primary coverage is the bound reviewed C++ run. This Python audit checks coverage/source binding '
              'and independently replays every fallback; universal zeros rely on inherited all-weight identities.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--certificate',type=Path,required=True);p.add_argument('--source',type=Path,required=True)
    p.add_argument('--receipt',type=Path);p.add_argument('--output',type=Path)
    a=p.parse_args();result=run(a.certificate,a.source,a.receipt)
    encoded=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if a.output:a.output.write_text(encoded)
    else:print(encoded,end='')

if __name__=='__main__':main()
