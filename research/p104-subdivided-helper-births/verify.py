"""Re-run one part of the pinned dual-supplier qualification."""
import argparse
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from prepare_sources import sources
from qualify_complex import digest, json_file, need


def run(script,*args):
    subprocess.run([sys.executable,"-I","-B",str(script),*map(str,args)],check=True)


def main(args):
    cache,out = args.cache.resolve(),args.out.resolve()
    out.mkdir(parents=True,exist_ok=True)
    sources(cache)
    source = cache / "source"
    supplier = source / "research/p104-dual-supplier-lift"
    peer = cache / "peer"
    claim = json_file(HERE / "CLAIM.json")
    binary, complex_ = HERE / "binary", HERE / "complex"
    if args.part == "binary":
        unpacked,finite,review = out/"native.json",out/"finite.json",out/"independent.json"
        run(binary/"replay.py","--source-root",source,"--write-json",unpacked)
        run(binary/"finite.py","--upstream",source,"--supplier",supplier,"--native-report",unpacked,"--out",finite)
        run(binary/"independent/verify.py","--source-root",source,"--word",binary/"WORD.json.gz","--out",review)
        need(json_file(unpacked)==json_file(binary/"REPLAY.json"),"archived complete binary native receipt")
        need(json_file(finite)==json_file(binary/"FINITE.json"),"archived finite binary receipt")
        independent = json_file(review)
        need(independent == json_file(HERE / "evidence/binary-independent.json"),
             "published independent binary operator and finite price")
        need(independent["finite"]["published_ordinary_admitted"] == json_file(finite)["ordinary_admitted"]
             == claim["binary_ordinary"], "same published two-stage ordinary BIT service")
        return
    if args.part == "construction":
        run(complex_/"birth_replay.py","--source-root",source,"--out",out)
        for name in ("WORD.json.gz","LAYOUT.json.gz"):
            need(digest(json_file(out/name))==digest(json_file(complex_/name)),"replayed pure birth "+name)
    intermediate = out / "intermediate.json.gz"
    run(complex_ / "overlay.py", complex_ / "WORD.json.gz", complex_ / "OVERLAY.json.gz", intermediate)
    frozen_parent = claim.get("free_birth_parent")
    candidate, candidate_layout = intermediate, complex_ / "LAYOUT.json.gz"
    extra = []
    if frozen_parent:
        need(digest(json_file(intermediate)) == frozen_parent, "fixed-boundary overlay pin")
        free = out / "free"
        run(complex_ / "final_birth.py", "--source-root", source, "--word", intermediate,
            "--layout", candidate_layout, "--out", free)
        candidate, candidate_layout = free / "WORD.json.gz", free / "LAYOUT.json.gz"
        extra = ["--free-parent", intermediate, "--free-parent-sha", frozen_parent,
                 "--free-split", claim["free_split"]]
    need(digest(json_file(candidate)) == claim["complex_word"], "final candidate")
    need(digest(json_file(candidate_layout)) == claim["layout"], "final layout and public owners")
    if args.part == "construction":
        return
    sys.path.insert(0,str(supplier/"complex"))
    import supplier as original
    graph,layout,_ = original.build()
    base,layout_path = out/"base.json.gz",out/"base-layout.json.gz"
    for path,item in ((base,graph),(layout_path,layout)):
        path.write_bytes(gzip.compress(original.encoded(item),mtime=0))
    common = ["--supplier",supplier,"--upstream",source,"--base-graph",base,"--base-layout",layout_path,
              "--candidate",candidate,"--layout",candidate_layout,"--sha",claim["complex_word"]]
    result=out/(args.part+".json")
    if args.part=="operator":
        run(complex_/"independent.py",*common,"--layout-sha",claim["layout"],"--out",result,*extra)
        need(json_file(result)==json_file(complex_/"INDEPENDENT.json"),"published independent operator receipt")
        return
    shard=["--chart",args.part[-1]] if args.part.startswith("charts-") else []
    run(HERE/"qualify_complex.py",*common,"--peer",peer,"--binary-finite",binary/"FINITE.json","--out",result,*shard)
    expected=HERE/"evidence"/(args.part+".json")
    replay = json_file(result)
    need(replay == json_file(expected), "published " + args.part + " receipt")
    if args.part == "application":
        for field, measured in (("conditional_lower", "finite_lower"), ("complex_raw_bracket", "complex_crossing"),
                                ("target", "target"), ("gain", "gain_above_upper"),
                                ("comparator_raw_joint_upper", "comparator_joint_upper")):
            need(claim[field] == replay[measured], "application and published claim agree on " + field)
        need(Fraction(replay["finite_lower"]) >= Fraction(replay["target"]), "finite application clears target")


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cache",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--part",choices=["binary","construction","operator","application","charts-0","charts-1","charts-2"],required=True)
    main(p.parse_args())
