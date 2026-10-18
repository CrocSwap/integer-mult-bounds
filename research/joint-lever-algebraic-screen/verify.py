"""Algebraic target screen; Apache-2.0, woklerx / OpenAI Codex assistance."""
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
from pathlib import Path

P=Path(__file__).resolve().parent
ROOT=P.parents[1]
SCALE=1 << 96
M=73; W=Q(896,9); LOCAL=5522; IDLE=1646


def require(ok,why):
    if not ok: raise ValueError(why)


@lru_cache(None)
def child(r):
    # x=(r/73)^(98/99). Binary search integer y=floor(2^96*x).
    numerator=r**98*SCALE**99; denominator=M**98
    lo,hi=0,SCALE
    while hi-lo>1:
        mid=(lo+hi)//2
        if mid**99*denominator<=numerator: lo=mid
        else: hi=mid
    require(lo**99*denominator<=numerator<(lo+1)**99*denominator,'root bracket')
    return Q(lo,SCALE),Q(lo+1,SCALE)


def moment(rank,centre):
    lo=hi=Q(0)
    for r,n in ((rank,Q(LOCAL,rank)),(8,Q(centre,8)),(51,Q(IDLE,51))):
        a,b=child(r);lo+=n*a;hi+=n*b
    return lo/W,hi/W


def main():
    for pin in json.loads((P/'SOURCES.json').read_text())['files']:
        if pin['usage']=='input': require(hashlib.sha256((ROOT/pin['path']).read_bytes()).hexdigest()==pin['sha256'],'source pin')
    word={1:2412,2:418,3:432,4:142,5:82,8:8}
    require(sum(r*n for r,n in word.items())-64==LOCAL,'selected noncentral mass')
    require((M-1)*W-LOCAL==IDLE,'fixed idle mass')
    require(2*51**2<M**2<=2*52**2,'halving cap')
    rows=[]; decisions=0
    for rank in range(1,52):
        passed=[]
        for centre in range(65):
            a,b=moment(rank,centre)
            require(b<1 or a>1,'unresolved exact sign')
            if b<1:passed.append(centre)
            decisions+=1
        require(passed==list(range(len(passed))),'centre monotonicity')
        maximum=max(passed,default=None)
        boundary=None
        if maximum is not None:
            boundary=dict(centre=maximum,upper_slack=str(1-moment(rank,maximum)[1]))
            if maximum<64: boundary['next_lower_excess']=str(moment(rank,maximum+1)[0]-1)
        rows.append(dict(rank=rank,max_integer_centre=maximum,
                         max_whole_rank8_calls=(maximum//8 if maximum is not None else None),boundary=boundary))
    first=min(row['rank'] for row in rows if row['max_integer_centre'] is not None)
    # Every individual ideal lever in levers.py still misses a=1/99.
    def invoice(entries):
        lo=hi=Q(0)
        for r,n in entries:
            a,b=child(r);lo+=n*a;hi+=n*b
        return lo/W,hi/W
    centre_free=invoice([(r,Q(n)) for r,n in word.items() if r!=8]+[(51,Q(IDLE,51))])
    rank16_only=invoice([(16,Q(LOCAL+64,16)),(51,Q(IDLE,51))])
    require(centre_free[0]>1 and rank16_only[0]>1,'one-lever controls')
    require(moment(16,0)[1]<1,'joint positive control')
    # Charging omitted centre work must remove a false positive somewhere.
    require(moment(first,0)[1]<1<moment(first,64)[0],'omitted-centre control')
    require(moment(16,0)[1] < moment(15,0)[0],'rank direction control')
    roots={str(r):[str(a),str(b)] for r in range(1,52) for a,b in [child(r)]}
    result=dict(status='PASS_JOINT_LEVER_ALGEBRAIC_SCREEN',target_a='1/99',
                width=M,families_per_call=str(W),noncentral_mass=LOCAL,idle_mass=IDLE,
                decisions=decisions,minimum_rank_with_free_centre=first,
                rank16_max_integer_centre=rows[15]['max_integer_centre'],
                rank16_max_whole_rank8_calls=rows[15]['max_whole_rank8_calls'],
                rows=rows,root_intervals=roots,
                controls=['both individual levers reject','combined rank16/freecentre accepts',
                          'omitted centre produces false positive','rank direction'],
                scope='Fractional mass relaxation at1/99 only; no decoder,physical packing,bit budget or new kappa.')
    if (P/'EXPECTED.json').exists():require(json.loads((P/'EXPECTED.json').read_text())==result,'receipt drift')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
