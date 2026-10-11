"""Independent changed-K5 decoder algebra, paid masses and target probes."""
from fractions import Fraction as Q
from math import comb
from collections import Counter
from pathlib import Path
import json,hashlib,importlib.util
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;D=ROOT/'experiments/architecture/k5-dual'
E=ROOT/'experiments/bit-search/pr433/source/research/split-centres-global/vendor/engines/base_two_moment.py'
spec=importlib.util.spec_from_file_location('k5_second',E);M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
def main():
    a=json.loads((D/'RESULT.json').read_text());pricing=json.loads((D/'PRICING.json').read_text());results=[]
    # Decoder entries depend solely on intersection size; this proves all
    # source-column coefficients, including inaccessible overlaps for tiny h.
    decoder=[]
    for j in range(6):
        phi=(j-1)*(j-3)
        bit=j-int(j%2==1 and j!=5)
        complex_central=Q(comb(j,2),16)-Q(3*j*(5-j),32)+Q(3,8)
        assert complex_central==Q(phi,8)
        clean=complex_central-(Q(phi,8) if j%2==0 else 0)
        assert bit%2==int(j==5) and clean==int(j==5)
        assert 2*comb(j,2)-3*j+3==phi
        decoder.append(dict(overlap=j,bit_signed_coefficient=bit,complex_signed_coefficient=str(clean)))
    for h in range(13,31):
        v=comb(h,5)
        for mode in ['bit','complex']:
            d=comb(h,2) if mode=='bit' else h;c=h if mode=='bit' else comb(h,2)+1
            allowed=[1,3] if mode=='bit' else [0,2,4]
            z=sum(comb(5,j)*comb(h-5,5-j) for j in allowed)
            R=v*z+c;m=5*d;W=4*v+R
            H=Counter()
            for rk,cnt in [(d-1,2*v),(1,2*v*z),(d-2,v*z),(d,2*c)]:H[rk]+=5*cnt
            for rk in [2*d-2,d-1,2*d+2,4]:H[rk]+=2*v
            deficit=m*W-sum(rk*n for rk,n in H.items());assert deficit==4*v-5*d*c>0
            source=next(x for x in a['prices'] if (x['h'],x['mode'])==(h,mode))
            assert H==Counter({int(k):n for k,n in source['profile'].items()}) and deficit==source['deficit']
            pr=next(x for x in pricing['results'] if (x['h'],x['mode'])==(h,mode));rate=Q(pr['saving_lower'])
            Ecount=sum(H.values());lo,hi=M.moment(m,W,list(H.items()),rate);bl,bh=M.moment(m,W,[(1,32*m*m*Ecount)],rate)
            assert hi+bh/10**16<1
            lo2,hi2=M.moment(m,W,list(H.items()),rate+Q(1,10**24));bl2,bh2=M.moment(m,W,[(1,32*m*m*Ecount)],rate+Q(1,10**24))
            assert lo2+bl2/10**16>1
            data=Counter({d-1:10*v})
            for rk in [2*d-2,d-1,2*d+2,4]:data[rk]+=2*v
            dl,dh=M.moment(m,1,list(data.items()),Q(1,99));data_mass=sum(rk*n for rk,n in data.items());uplift=(m*dl-data_mass)/v
            if mode=='bit':assert uplift>4
            # A meaningful full supplier needs a suitable metric/port chart;
            # the bit pair feature form is nonsingular but indefinite here.
            eigen=[Q(3*h*h-78*h+475,200),Q(38-3*h,16),Q(2)]
            assert all(eigen) and eigen[1]<0
            results.append(dict(h=h,mode=mode,deficit=deficit,rate=str(rate),data_uplift_lower=str(uplift),pair_form_eigenvalues=list(map(str,eigen)),pair_form_indefinite=True))
    out=dict(status='PASS_INDEPENDENT_K5_DECODER_ALGEBRA_PROFILE_DEFICITS_AND_BOTH_ENDPOINTS',decoder=decoder,profiles_checked=len(results),results=results,
        source_sha256={n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in ['check.py','RESULT.json','price.py','PRICING.json']},
        tiny_network_scope='Producer tiny signed/dyadic literal programs demonstrate algebra and dirt restoration; this audit independently checks general closed decoder identities and prospective counts, not new common-frame primitive geometry.',
        metric_boundary='Bit rational pair feature form has negative standard eigenvalue for every h13..30. This does not refute the motif: original upstream03-motifs explicitly permits indefinite nondegenerate I-J/9. It prevents importing existing Euclidean E8 charts by labels alone; concrete generalized rational/finite-field charts and common-prime restrictions require verification. Rescaling M/4 makes port norm2, preserving orthogonality. Complex odd F2 labels use another ambient form.',
        target_scope='Bit data alone exceeds4v maximum deficit at1/99 in each h13..30 tested fixedfive-stage interface, even granting free helper entropy/copycost. Not globalK5/newdecoder or allh impossibility.')
    (OUT/'K5-AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
if __name__=='__main__':main()
