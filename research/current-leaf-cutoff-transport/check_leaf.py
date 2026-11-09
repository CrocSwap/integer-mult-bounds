"""One bounded actual selected rank-two leaf crosses the old cutoff seam.

The predecessor's unchanged Gaussian-character oracle is reused with credit.
This is a local f=t=1 descriptor, not a global t>=145 producer witness.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from hashlib import sha256
import json
from cutoff_sources import HERE,load,need
from cutoff_view import PaidService,S

H=load("cutoff_retained_numeric_fixture",S.root/"check_child.py")


def run(output=None):
    entries=S.catalog.catalog()[1]
    pc,triple=next((pc,t) for pc,t in entries.items() if t[1].rank==2)
    service=PaidService(triple[1])
    work=[H.HARDWARE.Tape(3+j%5) for j in range(service.port_count)]
    field,context=H.HARDWARE.Tape(9),H.HARDWARE.Tape(11)
    for tape in (*work,field,context):
        for j in range(tape.origin-1):tape.cells[j]=j%2
    service.bind(work,{service.owner:S.common.abi.CodedPort(field)},S.common.abi.BinaryContextPort(context))
    values,initial,expected=H.fixture("cutoff",2)
    bits=H.encode_header(values);H.put(field,initial);H.put(context,bits)
    tapes=(*work,field,context);ancestors=[bytes(t.cells[:t.origin]) for t in tapes]
    before=sum(t.actions() for t in tapes)
    service.run()
    need(H.body(field)==bytes(expected) and H.body(context)==bytes(bits),"complete rank-two result and unchanged original cutoff header")
    need(all(t.head==t.origin for t in tapes) and all(not H.body(t) for t in work),"all388 work ports physically retired")
    need(all(bytes(t.cells[:t.origin])==old for t,old in zip(tapes,ancestors)),"all caller ancestors preserved")
    need(not service.provider.view.active and not service.provider.native.pool.live
         and not service.provider.native.engine.pool.live,"complete child/view lifecycle closed")
    result=dict(source_event=pc,owner=service.owner,rank=2,parent_f=1,parent_cutoff=1,
                child_f=2,child_cutoff=2,records=4096,physical_bits=len(initial),
                parent_bits=len(bits),private_ports=len(work),physical_actions=sum(t.actions() for t in tapes)-before,
                endpoint_sha256=sha256(H.body(field)).hexdigest(),parent_sha256=sha256(H.body(context)).hexdigest(),
                private_materialized_extents=[len(t.cells)-t.origin for t in work],
                ordinary_invocations=0,global_t_ge_145_witness=False,complete_MOVE_claim=False,
                prefix_arithmetic_admitted=True)
    if output is not None:
        output.mkdir(parents=True,exist_ok=True)
        (output/"returned-field.bits").write_bytes(H.body(field))
        (output/"returned-parent.bits").write_bytes(H.body(context))
        (output/"RESULT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result


if __name__=="__main__":
    from argparse import ArgumentParser
    parser=ArgumentParser();parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    print("COMPLETE_CUTOFF_TRANSPORT_LEAF",json.dumps(run(args.output),sort_keys=True),flush=True)
