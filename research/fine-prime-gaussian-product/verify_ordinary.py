"""Check the source-bound compact catalogue in the physical controller's namespace."""

from collections import Counter
from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from compact_ordinary import Q, load_cohort, open_source, source_at


def check(packet):
    load_cohort()
    from control import LocalState
    from macro_binding import SelectedBinding
    from residual_blocks import Cursor
    catalogue,topology,specs=open_source(packet,Q,check_only=True)
    checked=Counter()
    for i in range(9):
        call=topology.call(i,0)
        state=LocalState(call)
        for position,event in enumerate(call.events):
            op,role=state.accept(position)
            if op in (0,2):
                ident=call.requests[position]
                r=catalogue.requests[ident]
                if (r.position,r.role,r.base.rank)!=(position,role,event[-2]):
                    raise ArithmeticError("stage references another residual")
            checked[op]+=1
        state.finish()
        last=topology.call(i,31)
        if any(b.family-a.family!=31*888 or b.chart!=a.chart
               for a,b in zip(call.owners,last.owners,strict=True)):
            raise ArithmeticError("replica family layout")
    binding=SelectedBinding(specs)
    identity=tuple(tuple(int(i==j) for j in range(64)) for i in range(64))
    selected={}
    for i,r in enumerate(catalogue.requests):
        if r.kind=="MOVE" and r.role==114 and r.old_frame==0 and r.new_frame==528:
            selected.setdefault("MOVE",i)
        if r.kind=="IDLE" and r.base.rank==42:
            selected.setdefault("IDLE",i)
        if r.kind=="COPY":
            selected.setdefault("COPY",i)
    if len(selected)!=3:
        raise ArithmeticError("compact source witnesses")
    for label,i in selected.items():
        job=binding.residual(i,label!="IDLE",identity,0)
        cursor=Cursor(job.plan)
        costs=Counter()
        while not cursor.done:
            costs[cursor.take()[0]]+=1
        if not costs:
            raise ArithmeticError("empty physical residual word")
    w=28416
    def up(rank):
        # Enclose (rank/64)^(573/574) by an exact integer bisection.
        unit=1<<150
        l,h=0,unit
        target=rank**573*unit**574
        while h-l>1:
            m=(h+l)//2
            if m**574*64**573<=target:
                l=m
            else:
                h=m
        return Fraction(h,unit)
    fallback=Fraction(32*64**2*900416,10**16)
    moment=(sum(h*up(int(k)) for k,h in catalogue.profile.items())+fallback*up(1))/w
    head=(sum(h*int(k) for k,h in catalogue.profile.items())+fallback)/(64*w)
    if head>=Fraction(995,1000) or moment>=Fraction(9999999,10000000):
        raise ArithmeticError("compact ordinary moment shortfall")
    B=Fraction(573,574**2)
    if B<=Fraction(1737,10**6) or Fraction(997,1000)*Fraction(1737,10**6)<=Fraction("0.00173097911567079247276057"):
        raise ArithmeticError("outer transfer shortfall")
    return dict(canonical_requests=len(catalogue.requests),paid=sum(catalogue.profile.values()),
                bases=len(catalogue.bases),charts=len(catalogue.charts),erasures=len(catalogue.erase_guards),
                checked_events=sum(checked.values()),sampled_operators=sorted(selected),
                rate=str(B),head_lt=".995",width_moment_lt=".9999999",
                bad_classes="charged",binding=catalogue.receipt()["binding_sha256"])


if __name__=="__main__":
    import json
    import subprocess
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as temp:
        if sys.argv[1:]:
            packet=Path(sys.argv[1])
        else:
            packet=Path(temp)/"compact.gz"
            source_at(packet)
        print(json.dumps(check(packet),sort_keys=True),flush=True)
        subprocess.run([sys.executable,"-I","-O","-B",str(Path(__file__).with_name("verify_compact_control.py")),
                        "--source",str(packet),"--physical"],check=True)
        subprocess.run([sys.executable,"-I","-O","-B",str(Path(__file__).with_name("verify_compact_outer.py"))],
                       check=True)
