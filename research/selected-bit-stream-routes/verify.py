"""Pinned selected-route compilation and bounded physical payload regressions."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import route_catalog as R
from qadic_streams import need
from check_qadic_streams import check_primitives
from check_gl_packet import check_packets


def authenticated_inputs():
    source=json.loads((HERE/"SOURCES.json").read_text());data={}
    for entry in source["files"]:
        if entry["usage"]!="input":continue
        raw=(ROOT/entry["path"]).read_bytes()
        need(sha256(raw).hexdigest()==entry["sha256"],"source pin: "+entry["path"])
        data[entry["path"]]=raw
    return data


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-catalog",action="store_true",help="print the exact executable column IR and bills")
    args=parser.parse_args()
    catalogue,receipt=R.compile_catalog(authenticated_inputs())
    need(receipt["catalogue_sha256"]=="63d467f79e7e13fffd1f3de277dd5c6372cdac87f3fcd24b36a69149d300f81f","full catalogue regression")
    need(receipt["data_census_sha256"]=="03e87cbec874fcc453fb6e1ef6330c90bccf08d1216a37c069633b1893b7e1ab","data census regression")
    need((receipt["max_data_ordinary"],receipt["max_hosted_ordinary"])==(3520,1664),"route ordinary maxima")
    need(receipt["hosted_occurrence_total"]["ordinary"]==76197888,"hosted occurrence bill")
    if args.emit_catalog:
        print(json.dumps(catalogue,indent=2));return
    # Detect composition errors that an involution-only data test could miss.
    record=catalogue["host:1,2,3,4,5,6,7,8:8"]
    word=[(k,i,j,R.F(c)) for k,i,j,c in record["word"]]
    need(R.replay(word)!=R.replay(word[1:]+word[:1]),"host order mutant must differ")
    need(R.replay(word)!=R.replay(word[1:]),"omitted support swap mutant must differ")
    out={"status":"PASS_SELECTED_BIT_STREAM_ROUTES","catalogue":receipt,
         "primitive_payloads":check_primitives(),"complete_packets":check_packets(),
         "host_order_control":"REJECT","missing_support_swap_control":"REJECT",
         "scope":"Conditional fixed-header reduction to completed ordinary swaps and ordered stream passes; no full supplier or new exponent."}
    print(json.dumps(out,indent=2))


if __name__=="__main__":main()
