#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Rebuild the changed native and replay the signed caller from exact sources."""
import argparse
from contextlib import contextmanager
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from construct import need

STAGES = {"early": "verify_early.py", "native": "verify_native.py", "caller": "verify.py"}
REPLAY = ("verify_early.py", "verify_native.py", "verify.py", "price.py", "adapt.py",
          "derive_grid.py", "support.py")


@contextmanager
def predecessor():
    pin = json.loads((HERE/"INPUTS.json").read_bytes())
    archive = HERE/pin["archive"]
    need(pin["source_head"] == "215f67247f395c0e15f5ea3980f6a3e4aed155af", "Exact #7244 head")
    need(sha256(archive.read_bytes()).hexdigest() == pin["archive_sha256"], "Exact #7244 archive")
    files = {r["path"]:r for r in pin["files"]}
    need(len(files)==len(pin["files"]), "Unique archive paths")
    with TemporaryDirectory(prefix="p104-shorter-source-") as tmp, tarfile.open(archive) as tar:
        root = Path(tmp)
        seen = set()
        for member in tar:
            if member.isdir():
                continue
            name = member.name
            target = root/name
            need(member.isfile() and name in files and name not in seen and
                 target.resolve().is_relative_to(root), "Exact regular source inventory")
            raw = tar.extractfile(member).read()
            row = files[name]
            blob = sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
            need((len(raw),sha256(raw).hexdigest(),blob)==(row["size"],row["sha256"],row["git_blob"]),
                 "Exact frozen source member "+name)
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(raw)
            seen.add(name)
        need(seen==set(files), "Every frozen source path")
        yield root/pin["prefix"]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name,path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def adapt(work, old):
    old.adapt(work)  # first apply the exact published #7244 adapter

    def patch(name, before, after, count=1):
        path = work/name
        text = path.read_text()
        need(text.count(before)==count, "Exact successor adapter anchor in "+name+": "+before)
        path.write_text(text.replace(before,after))

    path = work/"source.py"
    raw = (old.HERE/"sources.py").read_text()
    start,end = raw.index("def reference():"),raw.index("@contextmanager\ndef sources():")
    path.write_text(raw[:start] + """def reference():
    root = Path((HERE / "INCUMBENT-DIRECTORY.txt").read_text().strip())
    word = read(root / "WORD.json.gz")
    need(sha256(canonical(word)).hexdigest() == "56e1a5e60cecf14991b3169b4575f0b7388d48fa39f261d7a20c7627a8d9e540",
         "Exact #7244 incumbent word")
    return root, word


""" + raw[end:])

    early,native,caller = (STAGES[k] for k in ("early","native","caller"))
    patch(early,"construct(old,read(HERE/'WITNESS.json'))","construct(old)")
    patch(early,"before['lifetimes']+4 and new['owned_fields']==old['owned_fields']+4",
          "before['lifetimes'] and new['owned_fields']==old['owned_fields']")
    patch(early,"'Two explicit added owned lifetimes and labels'","'Unchanged owned lifetimes and labels'")
    patch(native,"needed=changed|{(3,1091),(1091,127),(3,245),(245,127),(3,127)}",
          "needed=changed|{(1091,127),(1091,245),(245,127),(3,245),(3,127)}")
    patch(native,"hit=read(HERE/'WITNESS.json');new=construct(old,hit)",
          "hit={'pivots':[991], 'frames':[245]};new=construct(old)")
    patch(native,"['native']['helpers'].values())+2","['native']['helpers'].values())")
    patch(native,"oldN['lifetimes']+4==70","oldN['lifetimes']==70")
    patch(native,"'Two explicit added owned lifetimes, exact peak and unchanged ascent'",
          "'Unchanged owned lifetimes, exact peak and unchanged ascent'")
    patch(native,"old['owned_fields']+4==67","old['owned_fields']==67")
    patch(native,"'Two explicit added owned labels'","'Unchanged owned labels'")
    patch(native,"=={1:1,4:1,5:1,8:-1} and delta(N['paid'],oldN['paid'])=={1:2}",
          "=={8:1,9:-1} and delta(N['paid'],oldN['paid'])=={4:1,5:-1}")
    patch(native,"len(old['program'])+95 and new['public']==old['public']+2==1501",
          "len(old['program']) and new['public']==old['public']==1501")
    patch(native,"        from certificate import controls as temporal_controls, vectors, check\n"
          "        snapshots=vectors(old,hit);timed_certificate=check(old,hit,snapshots)\n"
          "        controls=temporal_controls(old,hit,snapshots)",
          "        from certificate import check\n"
          "        timed_certificate,controls=check(old,new)\n"
          "        c=next(i for i,e in enumerate(new['program']) if e==['ADD',991,1499,'-8',245])\n"
          "        controls['omitted_early_991_correction']=bool(I.native(new,mutant=c)['bad_inputs'])")
    patch(native,"A=new['public']+old['owned_fields']","A=new['public']+old['owned_fields']-1")
    patch(native,"PASS_TWO_CUT_FUNDED_NATIVE","PASS_FUNDED_SHORTER_RETURN_NATIVE")
    patch(caller,"PASS_TWO_CUT_FUNDED_CALLER","PASS_FUNDED_SHORTER_RETURN_CALLER")
    patch("price.py","Entire reconstructed #7161 invoice","Entire reconstructed #7244 invoice")


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("stage",choices=STAGES)
    cli.add_argument("--out",type=Path)
    args = cli.parse_args()
    out = args.out.resolve() if args.out else None
    need(__debug__, "Assertions are proof obligations")
    need(out is None or not out.exists(), "Keep prior receipts immutable")
    with predecessor() as exact, TemporaryDirectory(prefix="p104-shorter-stage-") as tmp:
        old = load("pr7244_stage_adapter",exact/"verify.py")
        with old.parent_archive() as parent:
            work = Path(tmp)
            for f in REPLAY:
                shutil.copyfile(parent/f,work/f)
            for f in ("REFERENCE.json","INPUTS.json","construct.py","certificate.py",
                      "WORD.json.gz","EARLY-RESULT.json","NATIVE-RESULT.json","RESULT.json"):
                if (HERE/f).is_file():
                    shutil.copyfile(HERE/f,work/f)
            shutil.copyfile(exact/"packing_reference.py",work/"packing_reference.py")
            (work/"INCUMBENT-DIRECTORY.txt").write_text(str(exact)+"\n")
            (work/"PARENT-DIRECTORY.txt").write_text(str(parent)+"\n")
            adapt(work,old)
            cmd = [sys.executable,"-I","-B",str(work/STAGES[args.stage])]
            if out is not None:
                cmd.extend(("--out",str(out)))
            subprocess.run(cmd,cwd=work,check=True)


if __name__=="__main__":
    main()
