"""Replay the exact paid-phase census and comparator evidence from a fresh root."""

from argparse import ArgumentParser
import gzip
from hashlib import sha1, sha256
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
PEER = "9d0119eb12fbd9fa534b48cd37b68e7099757b91"
STAGES = ("early","native","caller","frontier")


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("Duplicate JSON key")
    return result


def read(path):
    return json.loads(path.read_bytes(),object_pairs_hook=unique)


def relative(root,key):
    name = PurePosixPath(key)
    if name.is_absolute() or ".." in name.parts or name.as_posix() != key:
        raise ValueError(f"Invalid relative path {key}")
    return root / name


def digest(raw):
    return sha256(raw).hexdigest()


def verify_pins():
    pins = read(HERE/"LOCAL-PINS.json")
    for key,pin in pins.items():
        if digest(relative(HERE,key).read_bytes()) != pin:
            raise ValueError(f"Changed replay input {key}")
    prov = read(HERE/"PROVENANCE.json")["files"]
    for key,pin in prov.items():
        assert key in pins
        raw = relative(HERE,key).read_bytes()
        if pin["uncompress"]:
            raw = gzip.decompress(raw)
        assert digest(raw) == pin["sha256"], key
        assert sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest() == pin["git_blob"], key
    return pins


def admission():
    root = HERE/"admission"
    doc = read(root/"ADMITTED.json")
    anchor = read(root/"ANCHORED.json")
    assert doc["head"] == anchor["head"] == PEER
    assert doc["status"] == "independently_reproduced_comparable"
    assert set(doc["stages"]) == set(STAGES)
    assert anchor["base_ancestry"] == "verified"
    assert anchor["stock_full_history_wrapper"] == doc["source_history"]["stock_wrapper"]
    for item in anchor["evidence"]:
        assert digest(relative(root,item["path"]).read_bytes()) == item["sha256"]
    transcript = digest((root/"REGISTERED.stdout").read_bytes())
    for stage in STAGES:
        pin = doc["stages"][stage]
        receipt = relative(root,pin["path"]).read_bytes()
        assert pin["exit"] == 0 and digest(receipt) == pin["sha256"]
        item = json.loads(receipt,object_pairs_hook=unique)
        assert item["head"] == PEER and item["stage"] == stage and item["exit"] == 0
        assert item["registered_stdout_sha256"] == transcript
        frozen = item["verified_frozen_receipt"]
        name = PurePosixPath(frozen["path"]).name
        path = (HERE/"dependencies/7314"/name) if stage == "early" else root/"peer-source"/(name+".gz")
        raw = path.read_bytes()
        if stage != "early":
            raw = gzip.decompress(raw)
        assert digest(raw) == frozen["sha256"]
    assert digest((root/"ANCHORED.json").read_bytes()) == doc["source_history"]["evidence"]["sha256"]
    return root/"ADMITTED.json"


def materialize(out):
    mapping = read(HERE/"MATERIALIZE.json")
    assert len(set(mapping.values())) == len(mapping)
    for source,target in mapping.items():
        raw = relative(HERE,source).read_bytes()
        if source.endswith(".gz") and not target.endswith(".gz"):
            raw = gzip.decompress(raw)
        path = relative(out,target)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(raw)


def run(script,*args,check=True):
    return subprocess.run([sys.executable,"-I","-B",str(HERE/"engines"/script),*map(str,args)],
                          check=check,capture_output=True,timeout=25)


def replay(out):
    pins = verify_pins()
    admitted = admission()
    summary = read(HERE/"receipts/SUMMARY.json")
    assert summary["comparator"] == PEER and summary["kappa_change"] == "0"
    assert summary["admission_sha256"] == digest(admitted.read_bytes())
    with TemporaryDirectory(prefix="p104-central-transfer-") as directory:
        work = Path(directory)
        inputs,results = work/"inputs",work/"results"
        materialize(inputs)
        common = ("--inputs",inputs,"--comparator","7314","--admission",admitted,
                  "--admission-sha",summary["admission_sha256"])
        run("screen.py",*common,"--out",results,"--price-only")
        run("screen.py",*common,"--out",results,"--support")
        (results/"EXACT.json").write_bytes(run("transfer.py",inputs/"7113/CALLER.json").stdout)
        args = [results/f"{name}.json" for name in ("PRICE","BODY1","EXACT")]
        (results/"COMPARE.json").write_bytes(run("compare.py",*args).stdout)
        (results/"CONTROLS.json").write_bytes(run("screen.py","--inputs",inputs,"--controls-only").stdout)
        for name in ("PRICE","BODY1","EXACT","COMPARE","CONTROLS"):
            path = results/f"{name}.json"
            assert digest(path.read_bytes()) == pins[f"receipts/{name}.json"], name
        price,body,exact,compare = [read(results/f"{name}.json") for name in ("PRICE","BODY1","EXACT","COMPARE")]
        assert sum(price["complete_paid"].values()) == summary["paid"] == 110536
        assert sum(price["complete_targets"].values()) == summary["productive"] == 22461
        assert price["whole_compatible_optimistic_upper"] == summary["pre_support_compatible_upper"]
        assert price["paid_multistage_odd_binding"] == "unproved"
        assert body["scope"] == body["visited"] == body["exclusions"] == exact["tested"] == compare["matched_pairs"] == summary["pairs"] == 104
        assert compare["disjoint_stage_masks"] == summary["disjoint_stage_masks"] == 52
        assert not body["unvisited"] and not body["survivors"]
        assert compare["unresolved"] == summary["unresolved"] == 0
        assert compare["survivors"] == summary["support_survivors"] == 0
        assert summary["support_saving_upper"] == "0"
        caller = inputs/"7113/CALLER.json"
        raw = caller.read_bytes()
        caller.write_bytes(bytes((raw[0]^1,))+raw[1:])
        denied = run("screen.py",*common,"--out",work/"mutation","--price-only",check=False)
        assert denied.returncode == summary["mutation_exit"] == 1
        assert b"Changed SHA-256 for CALLER.json" in denied.stderr
        assert not (work/"mutation/PRICE.json").exists()
        if out is not None:
            out.mkdir(parents=True,exist_ok=False)
            for path in results.iterdir():
                shutil.copyfile(path,out/path.name)
        print("PASS_TYPE_B_CENTRAL_PHASE_TRANSFER pairs=104 disjoint_masks=52 survivors=0 unresolved=0 saving_upper=0 kappa_change=0")


if __name__ == "__main__":
    assert __debug__ and sys.version_info[:2] == (3,12)
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,help="fresh directory for four receipts and controls")
    replay(parser.parse_args().out)
