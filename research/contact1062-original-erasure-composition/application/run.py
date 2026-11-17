# SPDX-License-Identifier: Apache-2.0
"""Serial, offline full signed application on a frozen #7643/#7644 composition."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from math import fsum
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
DATA = HERE / "source"
A = runpy.run_path(str(HERE / "adapt.py"))
PINS = {
    "build.py":"5617ec65ecc66a197934b0caf9101c7b986a7fe98d00dd994dbdf0dcec397327",
    "application/word_checks.py":"fc5aca6f73282271b21d828eec6ab92884e6458c99868df22516e47db0a81c13",
    "receipts/FINAL.json":"f930ae55b1c7669f550c6af44b7d5e430f4364cb7ef8b59eb201a23b02d26572",
}
SOURCE_MANIFEST = "20b8d1a726ca3fadb9f08dff07436236e3b8b7eef94451373890fb2fc00e844b"


def digest(data):
    return sha256(data).hexdigest()


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def write(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",",":")).encode()


def authenticate(source):
    for name, pin in PINS.items():
        assert digest((source/name).read_bytes())==pin, name
    assert digest((HERE/"SOURCE-SHA256.json").read_bytes())==SOURCE_MANIFEST
    for name,pin in read(HERE/"SOURCE-SHA256.json").items():
        assert digest((DATA/name).read_bytes())==pin, name
    return runpy.run_path(str(source/"build.py"))["build"]()


def translate_edits(base, contact, edits):
    """Recover the original #7605 event behind each surviving #7643 clock."""
    main46=read(DATA/"7610-EDITS.json")
    insert={clock+5 if clock else 0:events for clock,events in main46["insert_before"]}
    remove={clock+5:event for clock,event in main46["delete"]}
    tagged=[]
    for clock,event in enumerate(base["program"]):
        tagged.extend((None,added) for added in insert.get(clock,()))
        if clock in remove:
            assert remove[clock]==event
        else:
            tagged.append((clock,event))
    assert read(DATA/"7642-WORD.json.gz")==dict(base,program=[e for _,e in tagged])
    plan=read(DATA/"7612-CONTACT.json")
    contact_edits={int(k):v for k,v in plan["proposed_events"].items()}
    assert all(tagged[int(k)][1]==v for k,v in plan["old_events"].items())
    tagged=[(old,contact_edits.get(i,event)) for i,(old,event) in enumerate(tagged) if contact_edits.get(i,event) is not None]
    assert contact==dict(base,program=[e for _,e in tagged])
    remap={old:i for i,(old,_) in enumerate(tagged) if old is not None}
    out={"base_events":len(tagged),"append":[]}
    for key in ("delete","insert_before"):
        out[key]=[[remap[clock],value] for clock,value in edits[key]]
    return out


def price_check(source, frozen, claim, probes):
    engine=runpy.run_path(str(source/"retained/pr7605/retained/pricing/evaluate_recursive_power.py"))
    results={}
    for label,filename,kappa,sign in probes:
        invoice,_=engine["load_invoice"](frozen/filename)
        zero=dict(invoice,paid={},targets={})
        result=engine["evaluate"](zero,invoice,1-Q(kappa),bits=256)
        assert result["classification"]==sign, label
        results[label]={"kappa":str(kappa),"interval":result}
    return results


def recount(source, frozen, before, candidate, other):
    rc=runpy.run_path(str(DATA/"recount.py"))
    caller=read(source/"data/caller.json")
    raw=[rc["invoice"](word,caller) for word in (before,candidate,other)]
    old,new,inc=raw
    for original,data in ((old,read(DATA/"7643-invoice-new.json")), (inc,read(source/"data/invoice.json"))):
        for key in ("paid","targets"):
            assert original[key]=={int(k):v for k,v in data[key].items()}
    for row in raw:
        assert row["calls"]==17 and row["life"]==74 and row["peak"]==50
    for key in ("targets","native_targets","owned_rise","caller_paid","caller_targets"):
        assert old[key]==new[key]==inc[key]
    diff=rc["difference"]
    assert diff(new["events"],old["events"])=={"ADD":17,"MOVE":-2}
    assert diff(new["native_paid"],old["native_paid"])=={1:-1,2:-2,5:1}
    assert diff(new["paid"],old["paid"])=={1:-17,2:-34,5:17}
    assert sum(new["paid"].values())==110298 and sum(new["targets"].values())==22461
    ordinary=read(DATA/"7643-FINAL.json")["ordinary_bound"]+17*(new["scalar_upper"]-old["scalar_upper"]-2000)
    ordinary44=read(source/"receipts/FINAL.json")["ordinary_bound"]+17*(new["scalar_upper"]-inc["scalar_upper"]+1000*(new["events"]["MOVE"]-inc["events"]["MOVE"]))
    assert ordinary==ordinary44<10**9
    bill={**read(source/"data/invoice.json"),"paid":dict(new["paid"]),"targets":dict(new["targets"])}
    write(frozen/"CANDIDATE-INVOICE.json",bill)
    h=Counter(new["targets"])
    h.subtract(new["paid"])
    # The approximate bisection only proposes a conservative decimal. Directed
    # integer comparisons below and the signed application's own engine prove it.
    lo,hi=0.,.01
    for _ in range(60):
        mid=(lo+hi)/2
        if fsum(n*r**(1-mid) for r,n in h.items())>0:
            lo=mid
        else:
            hi=mid
    ticks=int(lo*10**13)-1
    claim=f"{ticks//10**13}.{ticks%10**13:013d}"
    kappa=Q(claim)
    assert kappa>max(Q(read(DATA/"7643-FINAL.json")["raw_crossing"][1]),Q(read(source/"receipts/FINAL.json")["raw_crossing"][1]))
    probes=[("7643_rejects","7643-INVOICE.json",kappa,"new_cost_higher"),("7644_rejects","7644-INVOICE.json",kappa,"new_cost_higher"),("combined_accepts","CANDIDATE-INVOICE.json",kappa,"new_cost_lower"),("combined_guard","CANDIDATE-INVOICE.json",kappa+Q(7,10**14),"new_cost_lower")]
    return claim,ordinary,price_check(source,frozen,kappa,probes)


def prepare(work,source,word_path):
    other=authenticate(source)
    base=source/"retained/pr7605"
    ancestor=base/"retained/role902"
    p43=read(DATA/"7643-WORD.json.gz")
    candidate=read(word_path)
    candidate_sha=digest(canonical(candidate))
    assert digest(canonical(p43))==A["CONTACT"]
    support=runpy.run_path(str(source/"application/word_checks.py"))
    edit=translate_edits(read(base/"data/word.json.gz"),p43,read(source/"data/edits.json"))
    assert candidate==dict(p43,program=[e for _,e in support["reconstruct"](p43,edit)])
    work.mkdir()
    frozen=work/"frozen-composition"
    frozen.mkdir()
    (work/"isolated").mkdir()
    shutil.copytree(ancestor/"upstream/inputs",work/"inputs")
    files={
        "7481-WORD.json.gz":ancestor/"bench/7481-WORD.json.gz",
        "7546-WORD.json.gz":ancestor/"expected/role902-WORD.json.gz",
        "7546-NATIVE.json":ancestor/"expected/NATIVE.json","7546-SIGNED.json":ancestor/"expected/SIGNED.json",
        "7604-WORD.json.gz":base/"retained/pr7604/word.json.gz","7604-INVOICE.json":base/"retained/pr7604/invoice-new.json",
        "7605-WORD.json.gz":base/"data/word.json.gz","7605-NATIVE.json":base/"data/NATIVE.json","7605-SIGNED.json":base/"data/SIGNED.json",
        "7643-INVOICE.json":DATA/"7643-invoice-new.json","7644-INVOICE.json":source/"data/invoice.json",
        "7644-FINAL.json":source/"receipts/FINAL.json","CANDIDATE-WORD.json.gz":word_path,
    }
    for name in ("7610-EDITS.json","7612-CONTACT.json","7642-WORD.json.gz","7642-NATIVE.json","7642-SIGNED.json","7643-WORD.json.gz","7643-NATIVE.json","7643-SIGNED.json","7643-FINAL.json"):
        files[name]=DATA/name
    for name,path in files.items():
        shutil.copyfile(path,frozen/name)
    write(frozen/"EDITS.json",edit)
    claim,ordinary,intervals=recount(source,frozen,p43,candidate,other)
    write(work/"DIRECTED-PRICE.json",intervals)
    for stage in ("validation_native","validation_signed","reroute"):
        (work/"producer54"/stage).mkdir(parents=True)
    shutil.copyfile(source/"application/word_checks.py",work/"word_checks.py")
    shutil.copyfile(ancestor/"engines/7481-EMISSION.json",work/"producer54/reroute/RESULT.json")
    shutil.copyfile(word_path,work/"producer54/reroute/WORD.json.gz")
    for stage,generated in (("native",A["native"](candidate_sha)),("signed",A["signed"](candidate_sha,claim))):
        (work/f"producer54/validation_{stage}/run.py").write_text(generated)
    (work/"final_application.py").write_text(A["final"]())
    pins={p.relative_to(work).as_posix():digest(p.read_bytes()) for p in sorted(work.rglob("*")) if p.is_file()}
    write(work/"PREPARED.json",{"candidate":candidate_sha,"claim":claim,"ordinary":ordinary,"source_pins":pins})
    print("PASS_COMBINED_PREPARED",candidate_sha,claim,ordinary,flush=True)


def run_stage(stage,work,source):
    info=read(work/"PREPARED.json")
    for name,pin in info["source_pins"].items():
        assert digest((work/name).read_bytes())==pin, name
    if stage=="signed":
        native=work/"producer54/validation_native/NATIVE-RESULT.json"
        previous=read(work/"native-exit.json")
        assert previous["exit"]==0 and previous["candidate"]==info["candidate"] and previous["result_sha256"]==digest(native.read_bytes())
    environment=dict(os.environ,TMPDIR=str(work/"isolated"),OPENBLAS_NUM_THREADS="1",MKL_NUM_THREADS="1",OMP_NUM_THREADS="1",VECLIB_MAXIMUM_THREADS="1")
    cmd=[sys.executable,"-I","-B","-X","pycache_prefix="+str(work/"isolated/pycache"),str(work/f"producer54/validation_{stage}/run.py")]
    started=datetime.now(timezone.utc).isoformat()
    tick=time.monotonic()
    with (work/f"{stage}.stdout").open("x") as out,(work/f"{stage}.stderr").open("x") as err:
        proc=subprocess.Popen(cmd,cwd=work,env=environment,stdout=out,stderr=err)
        exitcode=proc.wait()
    receipt={"stage":stage,"candidate":info["candidate"],"started_utc":started,"ended_utc":datetime.now(timezone.utc).isoformat(),"seconds":time.monotonic()-tick,"exit":exitcode,"pid":proc.pid}
    if exitcode==0:
        result=work/f"producer54/validation_{stage}"/("NATIVE-RESULT.json" if stage=="native" else "RESULT.json")
        receipt["result_sha256"]=digest(result.read_bytes())
    write(work/f"{stage}-exit.json",receipt)
    if exitcode:
        print((work/f"{stage}.stderr").read_text(),file=sys.stderr)
        raise SystemExit(exitcode)
    if stage=="signed":
        source_fn=work/"final_application.py"
        ns={"read":read,"canonical":canonical,"digest":digest,"Q":Q,"PUBLIC_CLAIM":info["claim"],"NATIVE_MARKER":A["NATIVE"],"SIGNED_MARKER":A["SIGNED"]}
        exec(compile(source_fn.read_text(),str(source_fn),"exec"),ns)
        final=ns["final_application"](work)
        lo,hi=map(Q,final["raw_crossing"])
        intervals=price_check(source,work/"frozen-composition",Q(info["claim"]),[("raw_lower","CANDIDATE-INVOICE.json",lo,"new_cost_lower"),("raw_upper","CANDIDATE-INVOICE.json",hi,"new_cost_higher")])
        write(work/"DIRECTED-CROSSING.json",intervals)
        write(work/"FINAL.json",final)
        print(json.dumps(final,sort_keys=True))
    print("PASS_COMBINED_"+stage.upper(),flush=True)


def main():
    assert sys.implementation.name=="cpython" and sys.version_info[:2]==(3,12) and __debug__ and sys.dont_write_bytecode
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage",choices=("prepare","native","signed"))
    parser.add_argument("--source",type=Path,required=True,help="Exact #7644 research/chart1062-original-erasures directory")
    parser.add_argument("--work",type=Path,required=True)
    parser.add_argument("--word",type=Path,help="Frozen combined canonical JSON word in gzip transport")
    args=parser.parse_args()
    if args.stage=="prepare":
        assert args.word
        prepare(args.work.resolve(),args.source.resolve(),args.word.resolve())
    else:
        run_stage(args.stage,args.work.resolve(),args.source.resolve())


if __name__=="__main__":
    main()
