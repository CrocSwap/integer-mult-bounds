"""Source-pinned local gauge repair with paid inverse frame moves.

Not a replacement for the monotone source-word grammar or full supplier.
"""
from pathlib import Path
from fractions import Fraction as Q
import json,gzip,hashlib
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
SRC=ROOT/'experiments/stage-search/pr441-signed-retime/signed'
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def DE(v):
    v=list(v);v[0],v[8]=v[8],v[0];return v
def Dcap(q,v):
    # Pcap=I-qqT/4 on Q8; Dcap swaps its two doubled orthogonal components.
    a,b=v[:8],v[8:];qa=dot(q,a)/4;qb=dot(q,b)/4
    return [b[i]+q[i]*(qa-qb) for i in range(8)]+[a[i]+q[i]*(qb-qa) for i in range(8)]
def main():
    base=json.loads((SRC/'baseline.json').read_text());word=json.loads(gzip.decompress((SRC/'word.json.gz').read_bytes()))
    # Independent column propagation for pivot788, donors748/830 only.
    scalar={h:[int(i==h) for i in range(980)] for h in [788,748,830]}
    for h,vals in scalar.items():
        for frame,d,ss in base['A']:vals[d]+=sum(vals[s] for s in ss)
        ret=[vals[r] for r in base['ret']]
        for t,ks in enumerate(base['scatter']):vals[120+t]+=sum(ret[k] for k in ks)
        for frame,d,ss in base['B']:vals[d]+=sum(vals[s] for s in ss)
    defect=[scalar[788][120+i]+scalar[748][120+i]-scalar[830][120+i] for i in range(120)]
    assert {i:x for i,x in enumerate(defect) if x}=={94:2,95:2}
    E=word['lines'][0];qs=[word['lines'][i] for i in [94,95]]
    assert E==[2,0,0,0,0,0,0,0] and all(dot(E,q)==0 and dot(q,q)==4 for q in qs)
    # Three arbitrary physical input roles: positive helper p in DE chart,
    # and targets at ZERO. Test all48 address-vector basis columns.
    # Repair y: DE(y), then add-2 physicalp, then DE inverse. This changes
    # normalizedZERO y by-2DE(p), exactly the normalized positive defect.
    for col in range(48):
        x=[Q(int(i==col)) for i in range(48)];p=x[:16];ys=[x[16:32],x[32:48]]
        barp=DE(p)
        for q,y in zip(qs,ys):
            lifted=DE(y);corrected=[a-2*b for a,b in zip(lifted,p)];returned=DE(corrected)
            assert returned==[a-2*b for a,b in zip(y,barp)]
            after_raw=[a+2*b for a,b in zip(returned,barp)]
            assert Dcap(q,after_raw)==Dcap(q,y)
            # Literal inverse of correction: lift again, add+2p, return.
            inverse=DE([a+2*b for a,b in zip(DE(returned),p)])
            assert inverse==y
            assert Dcap(q,Dcap(q,y))==y
        assert DE(DE(p))==p
    relevant=set(base['scatter'][94])|set(base['scatter'][95])
    assert len(relevant)==8
    out=dict(status='PASS_SOURCE_DEFECT_AND_PAID_POSITIVE_GAUGE_REPAIR_ALL48_ADDRESS_COLUMNS',
        source_sha256={n:hashlib.sha256((SRC/n).read_bytes()).hexdigest() for n in ['baseline.json','word.json.gz']},
        pivot=788,donor_relation=[[748,-1],[830,1]],entrance=[0],defect={94:2,95:2},minimal_response_frame_rank=1,
        repair_word_per_target=['MOVE ZERO->E (rank1)','ADD-2 positivehelper at E (2units)','inverseMOVE E->ZERO (rank1)'],
        targets=[94,95],paid_frame_rank=4,paid_unit_additions=4,helper_entrance_rank=1,
        arbitrary_correlated_inputs=True,exact_gauge_inverse=True,source_caps_contain_E=True,
        alternative_canonical_scatter_repair_centres=sorted(relevant),alternative_selective_work_paid_rank=16,
        pricing_boundary='Four extra rank1 paid children per local invocation. Entrance rank1 reduces helper climb/stock together; it is not a free new deficit gain. Complete new paid H and physical stock must be recomputed, especially under hosted packing.',
        grammar_boundary='InverseMOVE E->ZERO is outside retained monotone local word grammar. DE here is an explicit symmetric integer address swap, so finite gauge repair exists; admission needs new source-bound weighted inverse/address and precision/tape accounting. No all-size compiler proof or full native112/114 signed supplier claim.')
    (OUT/'POSITIVE-FRAME-REPAIR.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
if __name__=='__main__':main()
