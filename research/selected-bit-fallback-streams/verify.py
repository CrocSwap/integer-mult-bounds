"""Authenticate sources, then replay the mixed fallback and its controls."""
import argparse
import gzip
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(condition,message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result={}
    for key,value in pairs:
        need(key not in result,"duplicate JSON key: "+key)
        result[key]=value
    return result


def read_json(raw):
    return json.loads(raw,object_pairs_hook=unique_object)


def source_checks():
    sources=read_json((HERE/"SOURCES.json").read_bytes())
    data={}
    for item in sources["files"]:
        if item["usage"]=="input":
            raw=(ROOT/item["path"]).read_bytes()
            need(sha256(raw).hexdigest()==item["sha256"],"source pin: "+item["path"])
            data[item["path"]]=raw
    for item in sources["vendor"]:
        need(sha256((HERE/item["path"]).read_bytes()).hexdigest()==item["sha256"],
             "predecessor byte pin: "+item["path"])
    hosted="research/community-hyperplane599-audit/pr589/bit589/v9/hosted/"
    payload=gzip.decompress(data[hosted+"GLOBAL-TEMPLATE.json.gz"])
    template=read_json(payload);receipt=read_json(data[hosted+"GLOBAL.json"])
    expected_raw=data["research/e8-bit-p111-tuned/tune/EXPECTED.json"]
    expected=read_json(expected_raw)
    assembly=read_json(data["research/community-frontier1094-audit/ASSEMBLY.json"])
    expected_blob=sha1(b"blob "+str(len(expected_raw)).encode()+b"\0"+expected_raw).hexdigest()
    need(assembly["bit_supplier"]["pr"]==589 and
         assembly["bit_supplier"]["git_blob_sha1"]==expected_blob,"selected BIT source binding")
    need(sha256(payload).hexdigest()==receipt["template_sha256"] and
         receipt["word_sha256"]==expected["word"]["file_sha256"],"template and word receipt binding")
    need((template["m"],template["live"],template["private_centre_reserve"])==(64,28416,9),
         "selected width and live/private inventory")
    idle=[x for x in template["schedule"] if x["kind"]=="idle" and x["idx"]==6]
    need(idle==[{"idx":6,"kind":"idle","pair":0,"rank":42,"source_level":2,"target_level":8}],
         "selected idle residual")
    need(not any(x[0]==6 and x[1]==213 for x in template["hosting"]["slots"]),
         "selected unhosted copy213")
    need(expected["nine"]["profile"]["42"]==288,"selected rank42 multiplicity")
    episodes={}
    for name,events in template["local_programs"].items():
        opened=False;copies=adds=moves=0
        for event in events:
            if event[0]==2:
                need(not opened,"one open private COPY");opened=True;copies+=1
            elif event[0]==3:
                need(opened,"matching private ERASE");opened=False
            elif opened and event[0]==0:
                moves+=1
            elif opened and event[0]==1:
                adds+=1
        need(not opened and (copies,adds,moves)==(9,527,0),"selected private lifetime inventory")
        episodes[name]={"COPY_episodes":copies,"interior_ADDs":adds,"interior_MOVEs":moves}
    return {"selected_idle":6,"unhosted_copy":213,"rank":42,"axes":list(range(22,64)),
            "private_lifetimes":episodes,"vendor_files_authenticated":len(sources["vendor"])}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit",action="store_true",help="Print a fresh receipt without reading RESULT.json.")
    args=parser.parse_args()
    sources=source_checks()
    sys.path[:0]=[str(HERE),str(HERE/"vendor")]
    from check_fallback import build_result
    result=build_result();result["sources"]=sources
    if not args.emit:
        need(json.loads(json.dumps(result))==read_json((HERE/"RESULT.json").read_bytes()),"saved receipt equality")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
