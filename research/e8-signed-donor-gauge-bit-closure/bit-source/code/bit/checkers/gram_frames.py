"""Exact nondegeneracy and PR #315's prime-witness rule for every frame of a PR249-format word, with the ambient Gram
matrix as a parameter.  Generalizes PR #346's exactnd_h.py and prime_new.py (Dylan Crow, with Anthropic Claude assistance).
  --gram triple9 : the paired-cube form G = I - J/9, integer Gram 9 B G B^t = 9 B B^t - s s^t  (exactnd_h/prime_new, verbatim)
  --gram e8ham   : the E8 form <x,y>/2 in Construction-A (Hamming) coordinates, integer Gram 2 B G B^t = B B^t
Checks per frame: rank(B) = dim, A.B = 0 and |A| + dim = h (when A given), det(integer Gram) != 0 (exact Bareiss), and
the prime witness: |det| = residual * prod p^e over PR #315's allowed primes with 0 < residual < 2^80.  With --new BASE
only frames absent from BASE are checked (prime_new.py's scope); otherwise every frame.
usage: python3 gram_frames.py WORDDIR --gram {triple9,e8ham} --h H [--new BASEDIR] [--positive]"""
import json, sys, argparse, importlib.util, os, collections
ap=argparse.ArgumentParser(); ap.add_argument('word'); ap.add_argument('--gram',required=True); ap.add_argument('--h',type=int,required=True)
ap.add_argument('--new'); ap.add_argument('--positive',action='store_true'); a=ap.parse_args()
HERE=os.path.dirname(os.path.abspath(__file__))
s=importlib.util.spec_from_file_location('pw',os.path.join(HERE,'..','..','pricing','prime_witnesses.py')); pw=importlib.util.module_from_spec(s); s.loader.exec_module(pw)
def validate_record(row, dimension, determinant, allowed_primes):   # PR #315 prime_check.validate_record, verbatim logic
    assert type(row['dimension']) is int and type(row['determinant']) is int and type(row['residual']) is int, 'exact integer witness fields'
    assert row['dimension'] == dimension and row['determinant'] == determinant != 0, 'exact determinant mismatch or singular basis'
    assert 0 < row['residual'] < 2**80, 'retained prime lower bound'
    product = row['residual']
    for prime, exponent in row['factors'].items():
        q = int(prime); assert q in allowed_primes and type(exponent) is int and exponent > 0, 'factor shape'; product *= q**exponent
    assert product == abs(determinant), 'factor identity'
def gram(B):
    if a.gram=='triple9':
        s_=list(map(sum,B)); return [[9*sum(x*y for x,y in zip(B[i],B[j]))-s_[i]*s_[j] for j in range(len(B))] for i in range(len(B))]
    if a.gram=='e8ham':
        return [[sum(x*y for x,y in zip(B[i],B[j])) for j in range(len(B))] for i in range(len(B))]
    raise SystemExit('unknown gram')
def rank_int(B):
    M=[r[:] for r in B]; r=0
    for c in range(len(M[0]) if M else 0):
        p=next((i for i in range(r,len(M)) if M[i][c]!=0),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]
        for i in range(len(M)):
            if i!=r and M[i][c]!=0: x,y=M[r][c],M[i][c]; M[i]=[u*x-w*y for u,w in zip(M[i],M[r])]
        r+=1
    return r
fr=json.load(open(a.word+'/frames.json'))['frames']
old=json.load(open(a.new+'/frames.json'))['frames'] if a.new else {}
keys=[k for k in fr if k not in old]
stats=collections.Counter(); primes=set(); bits=0; nonpos=0
for k in keys:
    B=fr[k]['B']; A=fr[k].get('A',[]); d=len(B); assert fr[k]['dim']==d
    assert d==0 or rank_int(B)==d,('basis rank',k)
    if A: assert all(sum(x*y for x,y in zip(r,b))==0 for r in A for b in B) and len(A)+d==a.h,('annihilator',k)
    M=gram(B) if d else []; det=pw.det(M); assert det!=0,('degenerate frame',k)
    if a.positive:   # positive-definite ambient form: every leading principal minor positive
        for j in range(1,d+1):
            if pw.det([r[:j] for r in M[:j]])<=0: nonpos+=1; break
    powers,residual=pw.factor_witness(det); row=dict(dimension=d,determinant=det,residual=residual,factors={p:e for p,e in powers.items() if e})
    validate_record(row,d,det,pw.PRIMES); primes.update(map(int,row['factors'])); bits=max(bits,abs(det).bit_length()); stats[d]+=1
assert nonpos==0
print('PASS %s Gram: %d frames checked, all nondegenerate%s; prime witnesses valid; max determinant bits %d; primes %s; by dim %s'%(
    a.gram,sum(stats.values()),' and positive definite' if a.positive else '',bits,sorted(primes),dict(sorted(stats.items()))))
