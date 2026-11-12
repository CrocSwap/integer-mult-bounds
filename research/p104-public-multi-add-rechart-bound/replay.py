"""Rebuild and reconcile the exact closed public multi-ADD rechart gate."""

from argparse import ArgumentParser
from gzip import decompress
from hashlib import sha1, sha256
from json import loads
from pathlib import Path
from shutil import copyfile
from subprocess import run
from sys import executable
from tempfile import TemporaryDirectory

HERE=Path(__file__).resolve().parent
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
COUNTS={"high_intersection_too_small":11,"low_union_too_large":2}


def require(condition,message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    out=dict(pairs)
    require(len(out)==len(pairs),"duplicate JSON key")
    return out


def read(raw):
    return loads(raw,object_pairs_hook=unique)


def authenticate():
    pins=read((HERE/"LOCAL-PINS.json").read_bytes())
    for rel,pin in pins.items():
        path=(HERE/rel).resolve()
        require(path.is_relative_to(HERE) and sha256(path.read_bytes()).hexdigest()==pin,
                f"changed local dependency {rel}")
    provenance=read((HERE/"PROVENANCE.json").read_bytes())
    for rel,entry in provenance["files"].items():
        require(rel in pins,f"unpinned public source {rel}")
        raw=(HERE/rel).read_bytes()
        if entry["uncompress"]:
            raw=decompress(raw)
        blob=sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        require(sha256(raw).hexdigest()==entry["sha256"] and blob==entry["git_blob"],
                f"changed public source {rel}")
    for rel,entry in provenance["generated"].items():
        require(rel in pins and sha256(decompress((HERE/rel).read_bytes())).hexdigest()==entry["receipt_sha256"],
                f"changed predecessor receipt {rel}")


def replay(output):
    require(__debug__,"assertions must be enabled")
    authenticate()
    output.mkdir(parents=True,exist_ok=False)
    with TemporaryDirectory(prefix="public-multi-add-rechart-") as directory:
        root=Path(directory)
        inputs=root/"inputs"
        inputs.mkdir()
        for source in (HERE/"inputs").iterdir():
            if source.name=="7314-HELPERS.json.gz":
                (inputs/"7314-HELPERS.json").write_bytes(decompress(source.read_bytes()))
            else:
                copyfile(source,inputs/source.name)
        price_path=inputs/"PRICE.json"
        old_word=inputs/"7277-WORD.json.gz"
        current_word=inputs/"7334-WORD.json.gz"

        def stage(name,engine,*args):
            result=run([executable,"-I","-B",str(HERE/"engines"/engine),*map(str,args)],
                       cwd=root,check=True,capture_output=True,timeout=22)
            require(result.stdout==(HERE/"receipts"/name).read_bytes(),f"changed receipt {name}")
            (output/name).write_bytes(result.stdout)
            return result.stdout

        raw_price=stage("PRICE.json","quote.py",root)
        price_path.write_bytes(raw_price)
        raw_forward=stage("FORWARD.json","component_gate.py",root)
        reverse_args=["--price",price_path,"--old",old_word,"--current",current_word]
        raw_reverse=stage("REVERSE.json","reverse_components.py",*reverse_args)
        raw_compare=stage("COMPARE.json","compare.py",output/"FORWARD.json",output/"REVERSE.json")
        price,forward,reverse,compare=map(read,(raw_price,raw_forward,raw_reverse,raw_compare))
        require(price["head"]==forward["head"]==reverse["head"]==HEAD
                and forward["status"]==reverse["status"]=="EXHAUSTED","changed comparator or exhaustion")
        require(len(price["positive"])==13 and all(len(x["add_clocks"])>=2 and not x["scale_clocks"]
                for x in price["positive"]),"changed ADD-only key scope")
        require(forward["counts"]==reverse["counts"]==compare["counts"]==COUNTS
                and compare["exact_key_agreements"]==13 and compare["compatible_saving"]=="0",
                "incomplete exact comparison")
        require(not any(d[key] for d in (forward,reverse) for key in ("unvisited","unresolved","survivors")),
                "lost zero unresolved certificate")

        for path,engine,args,message in (
            (price_path,"reverse_components.py",reverse_args,b"changed dependency price"),
            (current_word,"component_gate.py",[root],b"changed dependency: inputs/7334-WORD.json.gz"),
        ):
            original=path.read_bytes()
            path.write_bytes(original+b"\n")
            reject=run([executable,"-I","-B",str(HERE/"engines"/engine),*map(str,args)],
                       cwd=root,capture_output=True,timeout=8)
            require(reject.returncode==1 and not reject.stdout and message in reject.stderr,
                    f"changed source accepted {path.name}")
            path.write_bytes(original)
    print("PASS_PUBLIC_MULTI_ADD_RECHART keys=13 high_excluded=11 low_excluded=2 unresolved=0 kappa_change=0")


def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    if args.out:
        replay(args.out.resolve())
    else:
        with TemporaryDirectory(prefix="public-multi-add-receipts-") as directory:
            replay(Path(directory)/"out")


if __name__=="__main__":
    main()
