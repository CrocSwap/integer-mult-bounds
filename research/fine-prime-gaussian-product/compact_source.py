"""Export the fixed compact436 word, chart operators and calls from its producer."""

import gzip
import json
from pathlib import Path
import sys


def sparse(matrix):
    return [(i,j,str(x)) for i,row in enumerate(matrix) for j,x in enumerate(row) if x]


def write_source(output):
    here=Path(__file__).resolve().parent
    provider=here.parent/"bit-compact-carrier-retirement"/"provider"
    sys.path.insert(0,str(provider))
    from caller import build_provider
    # All exported matrices and instructions are rational or integral. The
    # physical consumer sets the prime when it compiles the finite low classes.
    cat,_,_=build_provider(3)
    topo=cat._recursive_caller_topology
    chart_set=sorted(cat.charts,key=lambda value:value.key)
    charts={x.key:i for i,x in enumerate(chart_set)}
    bases=sorted(cat.bases.values(),key=lambda b:b.key)
    bid={b.key:i for i,b in enumerate(bases)}
    requests=[[r.kind,r.stage,r.position,r.role,r.family,r.old_frame,r.new_frame,bid[r.base.key],
               charts[r.chart.key],r.header_space,charts[r.source_chart.key] if r.source_chart else None]
              for r in cat.requests]
    stages=[]
    for stage in range(9):
        call=topo.call(stage,0)
        stages.append([call.reverse,[[o.family,charts[o.chart.key]] for o in call.owners],
                       call.requests])
    matrices=[]
    for chart in chart_set:
        matrices.append(sparse(cat.chart_matrix(chart)))
        cat.chart_matrix.cache_clear()
    packet=dict(private=cat.private,request_digest=cat.receipt()["binding_sha256"],
                start=cat.word["start"],end=cat.word["final"],schedule=topo.schedule,
                programs=cat.programs,stages=stages,requests=requests,erasures=cat.erase_guards,
                bases=[[b.kind,b.rank,sparse(b.data) if b.kind=="local" else b.data] for b in bases],
                chart_keys=[c.key for c in chart_set],chart_matrices=matrices)
    raw=json.dumps(packet,separators=(",",":")).encode("utf8")
    Path(output).write_bytes(gzip.compress(raw,mtime=0))


if __name__=="__main__":
    write_source(sys.argv[1])
