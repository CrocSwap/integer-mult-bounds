"""Integer-lift orbit audit. Apache-2.0; woklerx with OpenAI Codex assistance."""
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def require(ok, why):
    if not ok:
        raise ValueError(why)


def packed(bits, stride):
    return sum(bit << (i*stride) for i,bit in enumerate(bits))


def digits(x, n, stride):
    return [(x >> (i*stride)) % (1 << stride) for i in range(n)]


def lifted(z, y, t, n, K, G):
    controls = digits(z,n,1)
    y += packed([2*a*b for a,b in zip(controls,digits(t,n,G))],K)
    t = (t+packed([(y >> (i*K)) & 1 for i in range(n)],G)) % (1 << (n*G))
    y += packed([a*(1-2*b) for a,b in zip(controls,digits(t,n,G))],K)
    t = (t-packed([((y >> (i*K)) & 1)^controls[i] for i in range(n)],G)) % (1 << (n*G))
    return y,t


def late_lift(c,y,t,u,n,K,G):
    parity=lambda x:packed([v%2 for v in digits(x,n,G)],1)
    y,t=lifted(parity(u),y,t,n,K,G)
    u1=(u+packed(digits(c,n,1),G)) % (1 << (n*G))
    return lifted(parity(u1),y,t,n,K,G)


def quotient_false_positive(defect, observed_width, target_width):
    return defect % (1 << observed_width) == 0 and defect % (1 << target_width) != 0


def literal(z,y,t,n,K,G,rho,mutate=False):
    # Direct modular packed instructions, separate from the integer lift.
    wm=2**((n+1)*K); tm=2**(n*G)
    for phase in range(4):
        if phase in (0,2):
            amount=0
            for i in range(n):
                if z & (1 << i):
                    d=(t//2**(i*G)) % 2**G
                    amount+=(2*d if phase == 0 else 1-2*d)*2**(rho+i*K)
            y=(y+amount)%wm
        else:
            amount=0
            for i in range(n):
                bit=(y//2**(rho+i*K))%2
                if phase == 3: bit ^= (z//2**i)%2
                amount+=bit*2**(i*G)
            t=(t+(amount if phase == 1 or mutate else -amount))%tm
    return y,t


def main():
    upstream=json.loads((P/'UPSTREAM.json').read_text())
    for f in upstream['files']:
        b=(P/f['path']).read_bytes()
        require(hashlib.sha256(b).hexdigest()==f['sha256'],'upstream SHA256')
        require(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==f['git_blob'],'upstream Git blob')
    for f in json.loads((P/'SOURCES.json').read_text())['files']:
        if f['usage']=='input': require(hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'],'source pin')
    expected=json.loads((P/'inputs/RESULT.json').read_text())['cells']
    hist={}; reduced=0; output=[]
    for cell in expected:
        n,K,G,rho=(cell[k] for k in ('n','K','G','rho'))
        order=cell['order']; key=(n,K,G,order)
        L=(n-1)*K+1; width=(n+1)*K-rho
        if key not in hist:
            errors=Counter(); ct=1 << (n*G)
            for t,c,y in product(range(ct),range(1 << n),range(1 << L)):
                ideal=y^packed(digits(c,n,1),K)
                for u in (range(ct) if order=='late' else (0,)):
                    yy,tt=late_lift(c,y,t,u,n,K,G) if order=='late' else lifted(c,y,t,n,K,G)
                    if tt==t: errors[yy-ideal]+=1
                    reduced+=1
            hist[key]=errors
        copies=1 << (width-L)
        ag=copies*sum(v for d,v in hist[key].items() if d % (1 << width)==0)
        require(ag==cell['ag'],'raw agreement mismatch '+str((key,rho)))
        false_positives=sum(v for d,v in hist[key].items() if quotient_false_positive(d,L,width))
        output.append(dict(n=n,K=K,G=G,rho=rho,order=order,ag=ag,total=cell['total'],orbit_multiplicity=copies,
                           quotient_only_false_positive_representatives=false_positives))
    # Full direct small cases include every discarded high/low target bit.
    direct=0; mutation=False
    n,K,G=2,3,1
    for rho in (0,2):
        for z,y,t in product(range(4),range(1 << 9),range(4)):
            actual=literal(z,y,t,n,K,G,rho)
            low=y % (1 << rho); quotient=y >> rho
            yy,tt=lifted(z,quotient,t,n,K,G)
            require(actual==(((yy << rho)+low) % (1 << 9),tt),'literal/orbit mismatch')
            direct+=1
            if not mutation and literal(z,y,t,n,K,G,rho,True)!=actual: mutation=True
    require(mutation,'unload-sign control')
    # Count per source cell: a nonzero integer defect can still wrap to zero
    # at that cell's full target modulus, so nonzero alone is not a failure.
    spurious=sum(cell['quotient_only_false_positive_representatives'] for cell in output)
    require(spurious>0,'missing carry-defect control')
    # Six representatives have D=128 in this histogram. They are genuine
    # agreements when rho=2 gives q=7, but false positives when rho=1 gives q=8.
    require(hist[(2,3,2,'late')][128]==6,'full-modulus regression multiplicity')
    yy,tt=late_lift(3,11,15,7,2,3,2)
    ideal=11^packed(digits(3,2,1),3)
    require((yy,tt,ideal)==(130,15,2),'full-modulus regression witness')
    require(not quotient_false_positive(yy-ideal,4,7),'valid wrap misclassified')
    require(quotient_false_positive(yy-ideal,4,8),'nonwrapping defect accepted')
    actual=literal(3,11 << 2,15,2,3,2,2)
    actual=literal(2,actual[0],actual[1],2,3,2,2)
    require(actual==(ideal << 2,15),'literal full-modulus wrap regression')
    result=dict(status='PASS_COMPACT_AGREEMENT_ORBIT_AUDIT',upstream_head=upstream['commit'],
                cells=output,source_total=sum(x['total'] for x in output),
                raw_agreements=sum(x['ag'] for x in output),reduced_states=reduced,
                full_literal_cases=direct,quotient_only_false_positive_cell_representatives=spurious,
                full_modulus_wrap_regression=dict(integer_defect=128,observed_width=4,target_width=7,valid_representatives=6),
                controls=['unload sign changed','carry defect omitted','nonzero defect valid at full modulus'],
                scope='Raw agreement counts and universal target-translation lemma only; no new guard or supplier admission.')
    if (P/'EXPECTED.json').exists(): require(json.loads((P/'EXPECTED.json').read_text())==result,'receipt drift')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
