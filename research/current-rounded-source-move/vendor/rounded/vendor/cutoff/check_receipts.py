"""Validate one retained complete leaf and re-execute the old cutoff reject.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from hashlib import sha256
import json
from cutoff_sources import HERE,load,need
from cutoff_view import S


def check():
    H=load("cutoff_receipt_fixture",S.root/"check_child.py")
    root=HERE/"receipts"
    execution=json.loads((root/"EXECUTION.json").read_text())
    result=json.loads((root/"RESULT.json").read_text())
    need(execution["exit_code"]==0 and 0<execution["elapsed_seconds"]<execution["cap_seconds"]==120,
         "one completed bounded positive child witness")
    records=[json.loads(x.split(" ",1)[1]) for x in (root/"execution.log").read_text().splitlines()
             if x.startswith("COMPLETE_CUTOFF_TRANSPORT_LEAF ")]
    need(records==[result],"one exact completed manual log receipt")
    header,initial,expected=H.fixture("cutoff",2)
    parent=H.encode_header(header)
    body=(root/"returned-field.bits").read_bytes(); context=(root/"returned-parent.bits").read_bytes()
    need(body==bytes(expected) and context==bytes(parent),"complete saved numerical output and original parent")
    need(result["endpoint_sha256"]==sha256(body).hexdigest()
         and result["parent_sha256"]==sha256(context).hexdigest(),"actual complete returned byte hashes")
    need(result["source_event"]==9934 and result["owner"]==76 and result["rank"]==2
         and (result["parent_f"],result["parent_cutoff"],result["child_f"],result["child_cutoff"])==(1,1,2,2)
         and result["records"]==4096 and result["physical_bits"]==73728
         and result["private_ports"]==388 and result["physical_actions"]==481525381,
         "exact actual selected translated leaf witness")
    need(result["ordinary_invocations"]==0 and result["global_t_ge_145_witness"] is False
         and result["complete_MOVE_claim"] is False and result["prefix_arithmetic_admitted"] is True,
         "bounded local witness does not claim a global producer or full MOVE")
    need(len(result["private_materialized_extents"])==388
         and all(type(x) is int and x>=1 for x in result["private_materialized_extents"]),
         "all numerical role histories retained as materialized extents")
    # This genuine old-provider call rejects before numerical import or axes.
    old=H.run("cutoff",2)
    need(old["rejection"]=="elementary PAID branch f <= cutoff"
         and old["endpoint_sha256"]==sha256(bytes(initial)).hexdigest(),
         "unchanged old f-only view rejects same local threshold and preserves input")
    corrupted=bytearray(body);corrupted[0]^=1
    need(bytes(corrupted)!=bytes(expected),"complete-byte oracle detects altered physical bit")
    return dict(manual_complete=True,physical_actions=result["physical_actions"],
                legacy_rejection_actions=old["physical_actions"],saved_output_bytes=len(body),
                saved_parent_bytes=len(context),old_cutoff_reject_reexecuted=True,
                byte_mutant_detected=True,global_producer_claim=False,
                scope="One actual positive child; saved success evidence audited, not numerically rerun.")
