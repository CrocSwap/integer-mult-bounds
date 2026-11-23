"""Rebuild the frozen frame-price projection from either authenticated ToikY package."""

from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import gzip
import json
import runpy
import subprocess
import sys


HERE=Path(__file__).resolve().parent
WORD="38d2b3a2311a9ba5fee091cc7aa204c7ed95651aec95d75184b2391df090cbfb"
LAYOUT="0ce3f9e383fc4bfdd22612b9e34fc9759d97204215937b82d23aec2cedd9b8ee"
PINS={
    "8072":("10362de3ceaa651cde5b71c6599fd4683d9f1f4d76cc252178e915b43a098fee",
            "76f9d4c6bfd880ee49f6ba5bde9138cf0856d669edb4d525e48ca71a9094eec3"),
    "8073":("9443a8ca39b9f0366305b67ba218875050c1574710b0d4ca4465cf8270f53119",
            "c6a7037712bc56a22b879c8ea94e57e210ca66402e367bb196f02d1a22b72a8a"),
}


def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":")).encode()


def projection(runtime):
    sys.path.insert(0,str(runtime))
    from upstream import install
    install()
    from strong_complex import digest,load_changed,word
    from grades import WEIGHTS,SCALES,SPLITS
    graph,layout=load_changed(runtime/"inputs")
    if digest(graph)!=WORD or digest(layout)!=LAYOUT:
        raise ValueError("Gaussian word or owner layout differs")
    receiver=word(graph,layout)
    paid=Counter(p.rank for p in receiver.paid)
    productive=Counter(p.rank for p in receiver.targets)
    main=set(layout["live"])|{k+112 for k in layout["live"]}|set(layout["hosted"]["X2"])|set(layout["hosted"]["Y2"])
    moves={k:(a,b) for k,a,b in graph["moves"]}
    dims=list(map(len,graph["frames"]))
    for a,b in moves.values():
        paid[abs(dims[a]-dims[b])]-=48
    for i,(a,b) in enumerate(zip(graph["initial"],graph["final"])):
        if i not in main:
            productive[dims[b]-dims[a]]-=48
    if any(n<0 for n in list(paid.values())+list(productive.values())):
        raise ValueError("A derived caller count is negative")
    return {**{key:graph[key] for key in ("frames","initial","final","moves")},
            "paid_schedule":[k for k in graph["schedule"] if k in moves],
            "main_roles":sorted(main),"native_calls":48,"weights":WEIGHTS,"scales":SCALES,
            "splits":SPLITS,"complete_word_sha256":WORD,"complete_layout_sha256":LAYOUT,
            "fixed_paid":sorted((r,n) for r,n in paid.items() if n),
            "fixed_productive":sorted((r,n) for r,n in productive.items() if n)}


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("source_package",type=Path)
    parser.add_argument("--pr",required=True,choices=PINS)
    args=parser.parse_args()
    p=args.source_package.resolve()
    for filename,pin in zip(("verify.py","prepare.py"),PINS[args.pr]):
        if sha256((p/filename).read_bytes()).hexdigest()!=pin:
            raise ValueError(f"The source driver differs at {filename}")
    with TemporaryDirectory(prefix="frame-price-rebuild-") as tmp:
        work=Path(tmp)
        peer=runpy.run_path(str(p/"verify.py"))["restore"](work)
        runpy.run_path(str(p/"prepare.py"))["materialize"](peer)
        runtime=work/"runtime"
        subprocess.run([sys.executable,"-I","-B",str(peer/"bootstrap.py"),str(runtime)],check=True)
        rebuilt=canonical(projection(runtime))
    if rebuilt!=gzip.decompress((HERE/"source-projection.json.gz").read_bytes()):
        raise ValueError("Pinned source projection differs")
    print("PASS_SOURCE_PROJECTION",args.pr,sha256(rebuilt).hexdigest())


if __name__=="__main__":
    main()
