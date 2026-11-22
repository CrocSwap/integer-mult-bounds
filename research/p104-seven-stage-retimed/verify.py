"""Replay the pinned #8042 source and a bounded seven-stage overlay offline."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
from tempfile import TemporaryDirectory

HERE=Path(__file__).resolve().parent

def sha(data):
    return hashlib.sha256(data).hexdigest()

def blob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def checked_source(dest):
    manifest=json.loads((HERE/"SOURCE-8042.json").read_bytes())
    if manifest["head"] != "3d33cb0c8a523b66d91e8de8250b85d0a436eb35":
        raise ValueError("Unexpected retimed source head")
    raw=(HERE/"source-8042.tar.gz").read_bytes()
    if sha(raw)!=manifest["source_archive_sha256"]:
        raise ValueError("Retimed source archive changed")
    rows={x["path"]:x for x in manifest["files"]}
    if len(rows)!=len(manifest["files"]):
        raise ValueError("Duplicate source path")
    seen=set()
    with tarfile.open(HERE/"source-8042.tar.gz","r:gz") as pack:
        for item in pack:
            p=Path(item.name)
            if (not item.isfile() or item.name not in rows or item.name in seen
                or p.is_absolute() or ".." in p.parts or str(p)!=item.name):
                raise ValueError("Unexpected source archive member")
            data=pack.extractfile(item).read()
            pin=rows[item.name]
            if len(data)!=pin["size"] or sha(data)!=pin["sha256"] or blob(data)!=pin["git_blob"]:
                raise ValueError("Retimed source bytes differ: "+item.name)
            seen.add(item.name)
            path=dest/p
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(data)
    if seen!=set(rows):
        raise ValueError("Incomplete retimed source")
    pin=manifest["large_blob"]
    data=(HERE/"predecessor-8030.tar.gz").read_bytes()
    if sha(data)!=pin["sha256"] or blob(data)!=pin["git_blob"]:
        raise ValueError("Predecessor archive changed")
    path=dest/pin["path"]
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data)
    # Two independent single-byte corruption controls.
    assert sha(raw[:-1]+bytes((raw[-1]^1,))) != manifest["source_archive_sha256"]
    assert blob(data[:-1]+bytes((data[-1]^1,))) != pin["git_blob"]
    print("PASS_PINNED_8042_BYTES",len(rows),pin["git_blob"],flush=True)

def run(argv, *, capture=False):
    p=subprocess.run(argv,check=True,text=True,stdout=subprocess.PIPE if capture else None)
    return p.stdout

def original(source,mode):
    run([sys.executable,"-I","-B",str(source/"verify.py"),mode])

def extension(source,machine):
    spec=importlib.util.spec_from_file_location("pinned_8042_bootstrap",source/"bootstrap.py")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    machine.mkdir()
    module.install(machine)
    # Original #8042 verifier helpers normally live beside bootstrap. Put
    # their exact pinned bytes beside the reconstructed machine for -I.
    helpers=("activation.py","check_complete.py","ordinary_clock.py","outer_clock.py",
             "outer_budget.py","equal_rate.py","RESULT.json")
    for name in helpers:
        shutil.copyfile(source/name,machine/name)
    for name in ("check_seven.py","check_runtime.py"):
        shutil.copyfile(HERE/name,machine/name)
    target=machine/"activation.py"
    old=target.read_text()
    if old.count("assert 1<=m<=6")!=1:
        raise ValueError("The original stage guard does not match")
    target.write_text(old.replace("assert 1<=m<=6","assert 1<=m<=7"))
    target=machine/"installations.py"
    with target.open("a") as out:
        out.write("\nSEVEN_STAGE = Profile(tuple(10**12*16**i for i in range(7)), "
                  "36000, Q(39,10000), Q('.003890115286594460'), 10**20)\n")
        out.write("PROFILES['seven-stage'] = SEVEN_STAGE\n")

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode",choices=("price","runtime","schedule","physical","slabs","product"))
    mode=ap.parse_args().mode
    if sys.version_info[:2]!=(3,12) or not __debug__:
        raise RuntimeError("Use Python 3.12 with assertions enabled")
    with TemporaryDirectory(prefix="p104-seven-stage-") as tmp:
        root=Path(tmp);source=root/"source";source.mkdir()
        checked_source(source)
        if mode in ("schedule","physical","slabs"):
            original(source,mode)
        else:
            if mode=="price":
                original(source,"cost")
            machine=root/"machine"
            extension(source,machine)
            if mode=="price":
                result=json.loads(run([sys.executable,"-I","-B",str(machine/"check_seven.py")],capture=True))
                expected=json.loads((HERE/"RESULT.json").read_bytes())
                if result!=expected:
                    raise ArithmeticError("Seven-stage invoice changed")
                print("seven-stage",result["kappa"],"A",result["public_exponent_A"],
                      "log2 C <=",result["log2_C_le"],flush=True)
            else:
                argv=[sys.executable,"-I","-B",str(machine/"check_runtime.py")]
                if mode=="product":
                    argv.append("--signed-only")
                run(argv)
    print("PASS_SEVEN_STAGE_RETIMED",mode,flush=True)

if __name__=="__main__":
    main()
