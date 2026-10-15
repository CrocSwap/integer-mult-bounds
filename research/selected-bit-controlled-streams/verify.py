"""Source binding and registered replay for selected controlled stream ADDs."""
import argparse
import gzip
from hashlib import sha1,sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from controlled_normalizer import need,schedule
from check_controlled import build_result

BASE="research/community-hyperplane599-audit/pr589/bit589/v9/hosted/"
EXPECTED="research/e8-bit-p111-tuned/tune/EXPECTED.json"
ASSEMBLY="research/community-frontier1094-audit/ASSEMBLY.json"


def source_object():
    data={}
    for pin in json.loads((HERE/"SOURCES.json").read_text())["files"]:
        if pin["usage"]!="input":continue
        raw=(ROOT/pin["path"]).read_bytes()
        need(sha256(raw).hexdigest()==pin["sha256"],"source pin: "+pin["path"])
        data[pin["path"]]=raw
    assembly=json.loads(data[ASSEMBLY]);expected=json.loads(data[EXPECTED])
    blob=sha1(b"blob "+str(len(data[EXPECTED])).encode()+b"\0"+data[EXPECTED]).hexdigest()
    need(assembly["bit_supplier"]["git_blob_sha1"]==blob and assembly["bit_supplier"]["pr"]==589,"selected supplier citation")
    payload=gzip.decompress(data[BASE+"GLOBAL-TEMPLATE.json.gz"])
    template=json.loads(payload);receipt=json.loads(data[BASE+"GLOBAL.json"])
    need(sha256(payload).hexdigest()==receipt["template_sha256"],"decoded template binding")
    need(receipt["word_sha256"]==expected["word"]["file_sha256"],"selected word binding")
    need((template["m"],template["h"],template["stages"],template["replicas"],template["live"])==(64,8,9,32,28416),"selected parameters")
    child=template["schedule"][21]
    need(child=={"idx":6,"kind":"idle","pair":0,"rank":42,"source_level":2,"target_level":8},"selected idle child")
    slots=[slot for slot in template["hosting"]["slots"] if slot[0]==6]
    bycopy={copy:[] for copy in range(222)}
    for _,copy,offset,width,_,_ in slots:bycopy[copy].extend(range(offset,offset+width))
    need(all(sorted(bycopy[c])==list(range(40)) for c in range(213)),"hosted forty-axis prefixes")
    need(all(not bycopy[c] for c in range(213,222)),"nine unhosted rank42 copies")
    need(template["hosting"]["remainders"]["6"]=={"2":213,"42":9},"retained remainder histogram")
    need(sum(int(v.get("42",0)) for v in template["hosting"]["remainders"].values())*32
         ==expected["nine"]["profile"]["42"]==288,"all selected rank42 children")
    axes=list(range(8+7*child["source_level"],8+7*child["target_level"]))
    need(axes==list(range(22,64)),"selected coordinate projector")
    return {"child":6,"copy":213,"replica":0,"pair":0,"side":1,"port":102,
            "physical_family":213,"rank":42,"axes":axes,"template_cover":template["cover"]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-schedule",action="store_true")
    args=parser.parse_args();selected=source_object()
    if args.emit_schedule:
        before,after=schedule(64,42,1)
        print(json.dumps({"selected":selected,"forward":before,"child":{"head":[0,42],"tail":[86,128],"weighted_reversal":True},"inverse":after},indent=2))
        return
    out=build_result();out["selected_object"]=selected
    need(out["address_cases"]==45 and out["dense_address_cases"]==6,"registered case inventory")
    need(out["nested_payload"]["weight_at_42"]==16,"two-level ancestor binding")
    print(json.dumps(out,indent=2))


if __name__=="__main__":main()
