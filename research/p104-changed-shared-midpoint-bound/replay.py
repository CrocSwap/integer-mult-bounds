"""Rebuild the changed-role shared-midpoint price, topology and exact exclusion."""
from argparse import ArgumentParser
from fractions import Fraction
from gzip import decompress
from hashlib import sha1,sha256
from json import dumps,loads
from pathlib import Path,PurePosixPath
from runpy import run_path
from shutil import copyfile
from subprocess import run
import sys
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parent
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"


def unique(items):
    result=dict(items)
    if len(result)!=len(items):
        raise ValueError("duplicate JSON key")
    return result


def decode(raw):
    return loads(raw,object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def relative(name):
    path=PurePosixPath(name)
    if path.is_absolute() or path.as_posix()!=name or ".." in path.parts:
        raise ValueError(f"invalid relative path: {name}")
    return path


def authenticate():
    pins=decode((ROOT/"LOCAL-PINS.json").read_bytes())
    for name,expected in pins.items():
        if digest((ROOT/relative(name)).read_bytes())!=expected:
            raise ValueError(f"changed package dependency: {name}")
    provenance=decode((ROOT/"PROVENANCE.json").read_bytes())
    for name,record in provenance["files"].items():
        raw=(ROOT/relative(name)).read_bytes()
        assert digest(raw)==record["sha256"]==pins[name]
        assert sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()==record["git_blob"]
    inputs={}
    for name,record in provenance["derived_gzip"].items():
        raw=decompress((ROOT/"inputs"/f"{name}.json.gz").read_bytes())
        published=decode((ROOT/relative(record["receipt"])).read_bytes())
        assert digest(raw)==published[record["key"]]
        inputs[name]=raw
    return inputs


def command(script,*args,timeout=25,check=True):
    response=run([sys.executable,"-I","-B",str(script),*map(str,args)],capture_output=True,timeout=timeout)
    if check and response.returncode:
        sys.stderr.write(response.stderr.decode(errors="replace"))
        response.check_returncode()
    return response


def compare_triad(lead,literal,exact,verify_script):
    assert lead["closed"] and not literal["blocked_roles"]
    assert lead["events"]==literal["progress"]["events_replayed"]==76466
    for x,y,r in zip(lead["fields"],literal["contacts"],literal["old_ranks"],strict=True):
        assert x["role"]==y["role"] and x["clocks"]==[y["contacts"][0][0],y["contacts"][-1][0]]
        assert x["middle"]==y["contacts"][1:-1] and x["ranks"]==r
    assert literal["old_ranks"]==[[3,2],[3,1],[3,2]]
    a,b,c=lead["results"][0],literal["positive_offsets"][0],exact["results"][0]
    assert len(lead["results"])==len(literal["positive_offsets"])==len(exact["results"])==1
    assert all(a[k]==b[k] for k in ("offset","rank","full_probe","paid_delta"))
    assert a["offset"]==c["offset"]==-2 and a["rank"]==c["rank"]==4
    assert a["status"]=="low union too large" and not c["abstract_feasible"]
    assert a["existing_charts"]==c["existing_chart_labels"]==[]
    span=run_path(str(verify_script))["vector_span"]
    assert sorted(span(a["low_union_basis"]))==exact["low_union_vectors"]
    assert sorted(span(a["high_intersection_basis"]))==exact["high_intersection_vectors"]
    assert (exact["low_union_rank"],exact["high_intersection_rank"])==(5,6)
    data=dict(head=lead["head"],matched_roles=3,matched_positive_offsets=1,dimension_interval=[5,6],
              rejected_rank=4,distinct_coframe_chronology=exact["distinct_coframe_chronology"])
    return (dumps(data,indent=2,sort_keys=True)+"\n").encode()


def copy(root,folder,files):
    for name,source in files.items():
        copyfile(root/relative(source),folder/relative(name))


def replay(scratch,out):
    inputs=authenticate()
    expected=decode((ROOT/"receipts/SHA256.json").read_bytes())
    produced={}

    def record(name,raw,path=None):
        assert digest(raw)==expected[name],("changed receipt",name)
        produced[name]=raw
        if path is not None:
            path.write_bytes(raw)
        return decode(raw)

    r100,r108,r111=(scratch/name for name in ("r100","r108","r111"))
    for root in (r100,r108,r111):
        for folder in ("inputs","lead","independent/inputs"):
            (root/folder).mkdir(parents=True)
    for root in (r108,r111):
        copy(ROOT,root,{"inputs/7334-WORD.json.gz":"inputs/7334-WORD.json.gz","inputs/pricing.py":"inputs/pricing.py"})
        for key in ("R100-PRICE","R92-PRICE"):
            (root/"inputs"/f"{key}.json").write_bytes(inputs[key])
    (r100/"lead/GEOMETRY.json").write_bytes(inputs["R100-GEOMETRY"])
    (r100/"lead/PRICE.json").write_bytes(inputs["R100-PRICE"])
    (r100/"inputs/R92-PRICE.json").write_bytes(inputs["R92-PRICE"])
    (r100/"inputs/7314-HELPERS.json").write_bytes(inputs["7314-HELPERS"])
    copyfile(ROOT/"inputs/pricing.py",r100/"inputs/pricing.py")
    stock=record("R106-STOCK.json",command(ROOT/"engines/stock.py","--r100",r100,
                 "--helpers",r100/"inputs/7314-HELPERS.json").stdout,r108/"inputs/STOCK.json")
    assert stock["head"]==HEAD and len(stock["midpoint_rank_tilt"]["anchors"])==10
    assert sum(r["positive_relaxed_profiles"]>0 for r in stock["midpoint_rank_tilt"]["anchors"])==8
    assert Fraction(stock["midpoint_rank_tilt"]["fixed_target_complete_upper"])<0

    copy(ROOT,r108,{"lead/routes.py":"engines/r108/routes.py","independent/reverse_routes.py":"engines/r108/reverse_routes.py",
                   "independent/compare.py":"engines/r108/compare.py"})
    for name in ("STOCK.json","7334-WORD.json.gz"):
        copyfile(r108/"inputs"/name,r108/"independent/inputs"/name)
    routes=record("R108-ROUTES.json",command(r108/"lead/routes.py").stdout,r108/"lead/ROUTES.json")
    rev=record("R108-REVERSE.json",command(r108/"independent/reverse_routes.py").stdout,r108/"independent/RESULT.json")
    agreement=record("R108-AGREEMENT.json",command(r108/"independent/compare.py",r108).stdout)
    assert produced["R108-AGREEMENT.json"]==(ROOT/"receipts/R108-AGREEMENT.json").read_bytes()
    assert routes["topology_counts"]=={"no four-MOVE topology":10} and not routes["price_counts"]
    assert rev["complete"] and rev["progress"]["events_replayed"]==76466 and not rev["unvisited"]
    assert agreement["matched"]==agreement["no_route"]==10 and agreement["actual_offset_count"]==agreement["remaining"]==0

    copy(ROOT,r111,{"lead/quote.py":"engines/r111/quote.py","lead/geometry.py":"engines/r111/geometry.py",
                   "independent/verify.py":"engines/r111/verify.py",
                   "independent/inputs/reverse_routes.py":"engines/r108/reverse_routes.py"})
    (r111/"inputs/R108-ROUTES.json").write_bytes(produced["R108-ROUTES.json"])
    price=record("R111-PRICE.json",command(r111/"lead/quote.py").stdout,r111/"lead/PRICE.json")
    assert price["old_paid"]==price["new_paid"]==110519 and price["productive"]==22461
    assert Fraction(price["complete_target_upper"])<0 and price["surplus"]==1424
    lead=record("R111-GEOMETRY.json",command(r111/"lead/geometry.py").stdout)
    for name in ("7334-WORD.json.gz","R100-PRICE.json","R108-ROUTES.json","R92-PRICE.json","pricing.py"):
        copyfile(r111/"inputs"/name,r111/"independent/inputs"/name)
    copyfile(r111/"lead/PRICE.json",r111/"independent/inputs/PRICE.json")
    verify=r111/"independent/verify.py"
    literal_path=r111/"LITERAL-PRICE.json"
    literal=record("R111-LITERAL-PRICE.json",command(verify,"literal-price").stdout,literal_path)
    exact=record("R111-REVERSE-GEOMETRY.json",command(verify,"geometry","--literal",literal_path,
                 "--literal-sha256",expected["R111-LITERAL-PRICE.json"]).stdout)
    comparison=record("R111-AGREEMENT.json",compare_triad(lead,literal,exact,verify))
    assert produced["R111-AGREEMENT.json"]==(ROOT/"receipts/R111-AGREEMENT.json").read_bytes()
    assert comparison["matched_positive_offsets"]==1 and comparison["rejected_rank"]==4

    for victim,script,args in (
        (r108/"independent/inputs/STOCK.json",r108/"independent/reverse_routes.py",()),
        (r111/"independent/inputs/PRICE.json",verify,("literal-price",)),
    ):
        victim.write_bytes(victim.read_bytes()+b"\n")
        failure=command(script,*args,check=False)
        assert failure.returncode==1 and not failure.stdout
        assert b"changed dependency:" in failure.stderr and victim.name.encode() in failure.stderr

    assert set(produced)==set(expected)
    if out is not None:
        out.mkdir(parents=True)
        for name,raw in produced.items():
            (out/relative(name)).write_bytes(raw)
    print("PASS_CHANGED_SHARED_MIDPOINT_BOUND pairs=10 missing_topology=10 closed_triads=1 positive_offsets=1 excluded=1 unresolved=0")


def main():
    assert __debug__ and sys.version_info[:2]==(3,12)
    p=ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,help="new directory for the nine regenerated receipts")
    args=p.parse_args()
    with TemporaryDirectory() as directory:
        replay(Path(directory),args.out)


if __name__=="__main__":
    main()
