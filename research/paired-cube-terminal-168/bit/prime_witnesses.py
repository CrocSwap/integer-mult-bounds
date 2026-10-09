"""Exact finite prime exclusions for the selected new rational bit frames.

For integer basis B and G=I-J/9, det(9 B G B^t) is a nonzero integer.
Excluding its prime divisors and 2,3,5 makes the reduced frame nondegenerate
over every odd local ring Z/q^w. Projector denominators divide this determinant
times fixed powers of 3. Retained frames retain their old exclusion witnesses.
The selected q is an arbitrarily large fixed prime chosen after this finite
set; this is not verification at a preselected numeric q.
"""
from pathlib import Path
import argparse,gzip,hashlib,json,sys

HERE=Path(__file__).resolve().parent

def det(A):
    A=[list(r) for r in A];n=len(A)
    if not n:return 1
    sign=1;previous=1
    for k in range(n-1):
        pivot=next((i for i in range(k,n) if A[i][k]),None)
        if pivot is None:return 0
        if pivot!=k:A[k],A[pivot]=A[pivot],A[k];sign=-sign
        p=A[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                v=A[i][j]*p-A[i][k]*A[k][j]
                assert v%previous==0
                A[i][j]=v//previous
            A[i][k]=0
        previous=p
    return sign*A[-1][-1]

PRIMES=(2,3,5,7,11,13,17,19,23,29,31)

def factor_witness(determinant):
    assert type(determinant) is int and determinant != 0
    residual=abs(determinant);powers={}
    for prime in PRIMES:
        power=0
        while residual%prime==0:residual//=prime;power+=1
        powers[str(prime)]=power
    validate_factor(determinant,powers,residual)
    return powers,residual

def validate_factor(determinant,powers,residual):
    assert type(determinant) is int and determinant != 0
    assert set(powers)==set(map(str,PRIMES))
    assert all(type(x) is int and x>=0 for x in powers.values())
    assert type(residual) is int and 0<residual<2**80
    reconstructed=residual
    for p in PRIMES:reconstructed*=p**powers[str(p)]
    assert reconstructed==abs(determinant)

def certificate(word=None):
    if word is None:
        from word import Candidate
        word=Candidate()
    C=word.C;h=word.h
    used=set(word.opframe)|set(word.w['source_frame'])|set(word.w['root_frame'])|{word.w['full_frame']}
    used.update(z['frame'] for z in word.w['gauges'])
    for e in word.k['entries']:used.update((e['mix_frame'],e['deliver_frame']))
    groups={}
    for frame in sorted(used):
        B=C.B[frame]
        key=json.dumps(B,separators=(',',':'));groups.setdefault(key,[]).append(frame)
    records=[]
    for key,frames in sorted(groups.items()):
        B=json.loads(key);s=list(map(sum,B))
        gram=[[9*sum(a*b for a,b in zip(x,y))-s[i]*s[j] for j,y in enumerate(B)] for i,x in enumerate(B)]
        determinant=det(gram);powers,residual=factor_witness(determinant)
        records.append(dict(basis_sha256=hashlib.sha256(key.encode()).hexdigest(),
            frame_ids=frames,dimension=len(B),cleared_gram_determinant=determinant,
            small_prime_powers=powers,remaining_factor=residual,gram_denominator_power_of_9=len(B)))
    controls=[];zeros={str(p):0 for p in PRIMES}
    for name,args in (('zero determinant',(0,zeros,1)),('incorrect factor identity',(15,zeros,1)),
        ('residual above retained prime lower bound',(2**80+7,zeros,2**80+7))):
        try:validate_factor(*args)
        except AssertionError:controls.append(name)
        else:raise ValueError('Invalid prime witness accepted: '+name)
    return dict(status='PASS exact prime witnesses for every used physical frame',h=h,
        source_commit='fd25adb7fbaa12ee761d02c733c54d1d2a7687ee',
        input_sha256={str(p.relative_to(HERE.parents[2])):hashlib.sha256(p.read_bytes()).hexdigest() for p in word.input_paths},
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        stripped_primes=list(PRIMES),frame_witnesses=records,unique_used_bases=len(records),
        total_used_frames=len(used),total_operation_frames=len(word.changed_frames),
        maximum_determinant_bits=max(abs(z['cleared_gram_determinant']).bit_length() for z in records),
        all_remaining_factors_below_retained_prime_lower_bound=True,adverse_controls=controls,
        rule='Every q>2^80 avoids every nonzero used-frame determinant, so the original prime range is unchanged.',
        scope='Exact integer cleared-Gram factors for all physical frames including every changed operation, gauge, source, root, partner-mix, delivery and ambient frame. Uniform split-rank and fallback arguments remain the retained local-ring interface.')

def main():
    assert not sys.flags.optimize
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    record=certificate();target=HERE/'prime-witnesses.json.gz'
    if args.write:target.write_bytes(gzip.compress((json.dumps(record,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
    else:assert record==json.loads(gzip.decompress(target.read_bytes())),'Exact prime witnesses changed'
    print(json.dumps({k:v for k,v in record.items() if k!='frame_witnesses'}))

if __name__=='__main__':main()
