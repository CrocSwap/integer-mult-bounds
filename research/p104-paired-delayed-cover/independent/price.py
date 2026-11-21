"""Reprice one authenticated 768-factor cover using independent interval and rational arithmetic."""
from argparse import ArgumentParser
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import tarfile

PINS = {
    "APPLICATION.json":"587ece477179606eed6fd9a334ac6d6e27f0067f82c3d6281993736e0570a76f",
    "APPLICATION-SOURCES.tar.gz":"d85d011ca74e8592c21c1e4db91a1a9021af26dcebc4dfdc2af7251f9c1bf968",
    "verify_application.py":"f774304804e705ac576459cca725b348f09e67e6020fe6165df9b7d39c605c54",
    "BINARY-CANDIDATE.json.gz":"74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326",
    "WORD.json.gz":"731246c085638706bdb97e7e88618f8923e27ee4ce8eb4869f0847f8f4699f7c",
}
MEMBERS = {
    "recipient/binary/finite.py":"c780cea060f4a9efef064b239636162a7e8e84e40369abc1a1c4679dfbeb3041",
    "parent/binary/independent/price.py":"d720df6f3f7a22554e83d0c29243af3ee04fa036073404926bab7bc2f2687e1b",
    "parent/qualify_complex.py":"236988674f4efe96134de83a224f9c5f4508f6049237415bc24a18669cf5ad67",
    "source/research/paired-query-only-bit/retained/inputs/credited_trim.py":"fcff17fdd3108be68761fbde0fcbfe218be166cf518c99f7163e60d53ab785d9",
    "recipient/continuation/audit_expanded.py":"0316153c1822724e1a3d08066aec9601a891073b0209954eaf302ffa014bf5ac",
    "source/research/p104-dual-supplier-lift/complex/supplier_gate.py":"3796b2e5a27f3caa142d16364154788e60d0099f1e24a8dcd028e4fbd35a84ca",
}
BRIDGE = "9731b93026717f5fa15851e3633cbb4bdc76eba2bffb9d6b4a3b69f7dd502443"

def need(ok, message):
    if not ok:
        raise ValueError(message)

def moment(profile, exponent):
    # Decimal exp and ln are correctly rounded nearest. Enclose each transcendental and
    # each arithmetic operation separately. Negative counts reverse interval endpoints.
    with localcontext() as ctx:
        ctx.prec = 70
        lo = hi = Decimal(0)
        t = Decimal(1) - Decimal(exponent)
        for r, count in sorted(profile.items()):
            if not count:
                continue
            log_r = Decimal(r).ln()
            zlo = (t * log_r.next_minus()).next_minus().exp().next_minus()
            zhi = (t * log_r.next_plus()).next_plus().exp().next_plus()
            if count < 0:
                zlo, zhi = zhi, zlo
            lo = (lo + (count*zlo).next_minus()).next_minus()
            hi = (hi + (count*zhi).next_plus()).next_plus()
        return lo, hi

def stages(covered):
    old = F("0.00385248")
    rho = F(1,250)
    rows = []
    for _ in range(4):
        envelope = (1-rho)*covered + rho*old
        value = F(envelope * 10**15 // 1 - 1, 10**15)
        margin = min(rho-value,1-rho-value,envelope-value)
        need(margin > 0 and value > old, "strict three-term stage")
        rows.append(dict(old=str(old), new=str(value), bound=str(envelope), margin=str(margin)))
        old = value
    return old, rows

def dec(q, places):
    scale = 10**places
    need((q*scale).denominator == 1, "inexact decimal output")
    return f"0.{int(q*scale):0{places}d}"

def main():
    ap = ArgumentParser()
    for field in ("peer","bridge","out"):
        ap.add_argument("--"+field,type=Path,required=True)
    a = ap.parse_args()
    for name, expected in PINS.items():
        need(sha256((a.peer/name).read_bytes()).hexdigest()==expected,name)
    with tarfile.open(a.peer/"APPLICATION-SOURCES.tar.gz") as t:
        names=t.getnames()
        need(len(names)==len(set(names)), "duplicate archive path")
        for name, expected in MEMBERS.items():
            need(sha256(t.extractfile(name).read()).hexdigest()==expected,name)
    need(sha256(a.bridge.read_bytes()).hexdigest()==BRIDGE, "cover theorem bytes")
    app = json.loads((a.peer/"APPLICATION.json").read_text())
    native = app["binary_native"]
    profile=Counter({int(k):v for k,v in native["productive_all"].items()})
    profile.subtract({int(k):v for k,v in native["paid_all"].items()})
    raw=app["binary_raw"]
    need(raw==["0.003890115286594","0.003890115286595"],"endpoint pins")
    signed=[moment(profile,k) for k in raw]
    need(signed[0][0] > 0 > signed[1][1], "opposite directed signs")
    h=app["binary_H"]; need(h==299610000000000,"original H")
    gap=F(1,10**10); trial=F(raw[0])-F(1,10**11)
    d=F(1,h*2**38)
    excess_upper=F(64,2**45)
    growth_lower=h*d/2
    need(growth_lower==excess_upper and d>0, "strict exp/log lower and strict prime upper meet")
    need(0 < excess_upper and gap/4 > excess_upper and not excess_upper < d/4, "zero debit and stale shortcut controls")
    need(native["calls"]==36 and native["ordinary"]["ordinary_records"]==896869203600 and
         native["ordinary"]["owned_backing"]==6994188,"stock control")
    old_cap, old_rows=stages(trial-2*gap)
    cap, rows=stages(trial-gap-d)
    need(old_cap==F(app["binary_ordinary"]), "known-good four-stage control")
    qtick=10**14
    def grid(cap):
        return F(min(int(F(app["rational_raw"][0])*qtick),int(cap*qtick))-8,qtick)
    old=grid(old_cap); candidate=grid(cap); tested=candidate+F(7,qtick)
    need(old==F(app["claim"]) and candidate>old and tested<cap,"candidate grid")
    ceiling=F(raw[1])-2*gap
    need(candidate>ceiling,"strict separation even before charging the old seven ticks")
    result=dict(source_pins=PINS,member_pins=MEMBERS,bridge_sha256=BRIDGE,raw=raw,
        signed_intervals=[[str(x) for x in s] for s in signed],H=h,trial=str(trial),
        uniform_loss=str(gap),delayed_cover_loss=str(d),surcharge_upper_strict=str(excess_upper),
        power_growth_lower_strict=str(growth_lower),old_rows=old_rows,new_rows=rows,
        old_cap=dec(old_cap,15),cap=dec(cap,15),old_claim=dec(old,14),candidate=dec(candidate,14),
        tested=dec(tested,14),gain=str(candidate-old),percent_gain=str(100*(candidate-old)/old),
        relaxed_old_ceiling=str(ceiling),separation=str(candidate-ceiling),signed_status="requires fresh full signed compiler and independent expansion")
    with a.out.open("x") as stream:
        json.dump(result,stream,indent=2,sort_keys=True);stream.write("\n")
    print("PASS",result["cap"],result["candidate"],result["tested"],result["gain"],result["percent_gain"])
if __name__=="__main__":
    main()
