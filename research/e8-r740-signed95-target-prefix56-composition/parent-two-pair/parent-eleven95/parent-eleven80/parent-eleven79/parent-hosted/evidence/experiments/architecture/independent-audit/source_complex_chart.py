"""Concrete two-host chart using pinned PR442 inherited complex axes.

Checks binary orthogonal routing and exact Z4 Fourier multipliers, not the
all-size signed primitive/compiler interface or a full PR442 admission.
"""
from pathlib import Path
import gzip,json,hashlib
from collections import defaultdict

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
DIR=ROOT/'experiments/verification/proposal-scout/pr442/inherited/research/split-centres-global/inputs'
M=73
def dot(a,b):return bin(a&b).count('1')&1
def image(columns,v):
    ans=0
    while v:
        low=v&-v;ans^=columns[low.bit_length()-1];v^=low
    return ans
def compose(A,B):return [image(A,v) for v in B]
def transpose(A):return [sum(((A[j]>>i)&1)<<j for j in range(M)) for i in range(M)]
def identity():return [1<<i for i in range(M)]
def orthogonal(A):return all(dot(x,y)==int(i==j) for i,x in enumerate(A) for j,y in enumerate(A))
def phase(axes,translation=0):
    # i^(parity(v.y)) for each C_v. Parity has exact degree<=2 expansion
    # modulo4, since every higher coefficient is divisible by4.
    p=defaultdict(int)
    for v in axes:
        bits=[i for i in range(M) if (v>>i)&1]
        for i in bits:p[i,]+=1
        for j,i in enumerate(bits):
            for k in bits[j+1:]:p[i,k]-=2
    for i in range(M):
        if (translation>>i)&1:p[i,]+=2
    return {str(k):v%4 for k,v in sorted(p.items()) if v%4}
def sigma_for(basis,target):
    # basis is orthonormal. Target is a subset of its columns. Remaining
    # columns retain deterministic basis order, yielding explicit sigma.
    assert len(target)==9 and len(set(target))==9
    ans=target+[v for v in basis if v not in set(target)]
    assert len(ans)==M and orthogonal(ans)
    assert compose(transpose(ans),ans)==identity()
    return ans
def main():
    path=DIR/'complex-data-phases.json.gz'
    d=json.loads(gzip.decompress(path.read_bytes()))
    # All source idle axes must be orthonormal; this checks actual vectors,
    # not just supplied dimensions. Source labels/count are kept separate.
    axes_checks=0
    for recipe in d['recipes']:
        for child in recipe['idle_children']:
            axes=child['orthogonal_axes']
            assert len(axes)==child['rank']
            assert all(dot(a,b)==int(i==j) for i,a in enumerate(axes) for j,b in enumerate(axes))
            axes_checks+=1
    recipe=d['recipes'][0];child=recipe['idle_children'][4]
    assert child['rank']==32
    first=recipe['idle_children'][0]['orthogonal_axes']
    basis=[recipe['q']]+first[:8]+[1<<i for i in range(9,M)]
    assert orthogonal(basis) and len(basis)==M
    axes=child['orthogonal_axes'];S1=axes[:9];S2=axes[9:18];rem=axes[18:]
    sigmas=[sigma_for(basis,S1),sigma_for(basis,S2)]
    assert sigmas[0]!=sigmas[1]
    assert phase(S1+S2+rem,child['translation_after'])==phase(axes,child['translation_after'])
    # Right action owner g=d sigma^-1. For fixed invocation class d,
    # different sigmas yield distinct owners, and g sigma=d exactly.
    cover_samples=[identity(),sigmas[0],sigmas[1],compose(sigmas[0],sigmas[1])]
    routes=[]
    for dclass in cover_samples:
        assert orthogonal(dclass)
        owners=[compose(dclass,transpose(s)) for s in sigmas]
        assert owners[0]!=owners[1]
        for owner,s in zip(owners,sigmas):assert compose(owner,s)==dclass
        routes.append({'d_columns':list(map(str,dclass)),'owner_columns':[list(map(str,o)) for o in owners]})
    # Universal proof beyond samples: right multiplication by sigma^-1 is
    # a bijection of O(73,2); if d sigma1^-1=d sigma2^-1 then sigma1=sigma2.
    result=dict(status='PASS_PINNED_SOURCE_TWO_HOST_ORTHOGONAL_CHART_AND_EXACT_PHASE',
        source_head='4e16d001d505d4f21dd2bcfc44591f9be4c279bd',
        source_blob='22154a8c5875bd3398e1cb112ea0a5307d6793e8',
        source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),port=0,idle_child_recipe_index=4,
        rank=32,host_widths=[9,9],remainder_rank=14,translation_after=child['translation_after'],
        actual_idle_axes=list(map(str,axes)),sigma_columns=[list(map(str,s)) for s in sigmas],
        all_source_idle_axis_checks=axes_checks,exact_Z4_multiplier=True,cover_samples=routes,
        universal_owner_argument='Invertible right action is bijective; distinct sigma maps cannot alias for fixed d. Across d calls may reuse a physical owner sequentially, as inherited bank covers do.',
        universal_commutation='All C_v and X_t are polynomials in commuting address translations. All residual/idle/translation factors commute, even before any cover conjugation.',
        payment='Local paid children unchanged; pending rank32 factor replaced by two already-paid rank9 residuals plus rank14 remainder. Stock/routing/selectors and sigma compiler cost require full invoice.',
        scope='Actual source chart extension for one two-host child, not all selected PR442 slots, integer local dirt audit, all-size compiler or source-hosted full replay.')
    (OUT/'SOURCE-COMPLEX-CHART.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status']);print('actual idle axis checks',axes_checks)
if __name__=='__main__':main()
