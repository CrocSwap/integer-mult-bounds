"""Selected PR589 local-ring packet integration; reuse the pinned PR1627 audit."""
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from ring_algebra import need,ring_certificate
from fibre_streams import alias_control,physical_fibre_check
from owner_packets import owner_certificate,global_endpoint,data_chart_boundaries,row_layout

PREDECESSOR="research/pr589-five-helper-hosting/"


def canonical(value):return json.dumps(value,sort_keys=True,separators=(",",":"))


def inputs():
    manifest=json.loads((HERE/"SOURCES.json").read_text())
    for item in manifest["files"]:
        if item["usage"]=="input":
            raw=(ROOT/item["path"]).read_bytes()
            need(sha256(raw).hexdigest()==item["sha256"],"source pin: "+item["path"])
    spec=importlib.util.spec_from_file_location("pr1627_retained",ROOT/(PREDECESSOR+"verify.py"))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_result():
    old=inputs()
    inherited=old.run()
    receipt=json.loads((ROOT/(PREDECESSOR+"RESULT.json")).read_text())
    need(json.loads(json.dumps(inherited))==receipt,"fresh predecessor receipt")
    word,template,geometry=old.read(old.WORD),old.read(old.HOST),old.read(old.GEO)
    need(template["m"]==64 and max(map(int,inherited["profile"]))==42,"selected coarse width and maximum child rank")
    frame_rows=[old.projection([word["lines"][i] for i in f]) for f in word["frames"]]
    projectors=[p for p,_ in frame_rows];dims=[r for _,r in frame_rows]
    rings=ring_certificate(projectors,dims,template["local_programs"],word)
    basis=rings.pop("basis_choices")
    rings["basis_choice_sha256"]=sha256(canonical(basis).encode()).hexdigest()
    bad=dict(template);bad_call=dict(template["calls"][0])
    bad_call["owners"]=list(bad_call["owners"])
    bad_call["owners"][244]=bad_call["owners"][243]
    bad["calls"]=[bad_call]+template["calls"][1:]
    try:owner_certificate(bad,geometry)
    except ValueError as error:
        need(str(error)=="separation witness for complete low packets","specific aliased-owner rejection")
    else:raise ValueError("aliased selected owners accepted")
    return {"status":"PASS_SELECTED_LOCAL_RING_SWEEPS",
            "inherited_PR1627":{"status":inherited["status"],"receipt_sha256":sha256(canonical(receipt).encode()).hexdigest(),
                "local":inherited["local"],"rank_mass":inherited["rank_mass"],
                "rank_deficit":inherited["rank_deficit"],
                "credit":"alephnan; the existing finite-field whole-call proof and literal replay are reused, not claimed as new."},
            "local_ring":rings,"owner_packets":owner_certificate(template,geometry),
            "selected_owner_mutation":"REJECT_EQUAL_SUPPORT_PACKET_ALIAS",
            "data_chart_boundaries":data_chart_boundaries(geometry),
            "global_endpoint":global_endpoint(template,word,projectors),
            "packet_alias_control":alias_control(),"restricted_fibre_XOR":physical_fibre_check(),
            "compatible_row_layout":row_layout(template),
            "scope":"Selected local-ring exact-stream integration and explicit live-row layout, conditional on completed address callees and the stated work/stock contracts; no finite-invoice admission or new exponent."}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit",action="store_true",help="Print a fresh receipt without comparing the saved RESULT.json.")
    args=parser.parse_args();result=build_result()
    if not args.emit:
        need(json.loads(canonical(result))==json.loads((HERE/"RESULT.json").read_text()),"saved receipt equality")
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()
