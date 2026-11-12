"""Git-free chart-118 pairing replay and inherited prefix coverage."""
from argparse import ArgumentParser
from fractions import Fraction
from gzip import decompress
from hashlib import sha1,sha256
from json import dumps,loads
from pathlib import Path,PurePosixPath
from shutil import copyfile
from subprocess import run
import sys
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parent


def unique(pairs):
    obj=dict(pairs)
    if len(obj)!=len(pairs):
        raise ValueError("duplicate JSON key")
    return obj


def decode(raw):
    return loads(raw,object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def relative(name):
    path=PurePosixPath(name)
    if path.is_absolute() or path.as_posix()!=name or ".." in path.parts:
        raise ValueError("invalid relative path "+name)
    return path


def source(name):
    return (ROOT/relative(name)).read_bytes()


def authenticate():
    pins=decode(source("LOCAL-PINS.json"))
    for name,expected in pins.items():
        if digest(source(name))!=expected:
            raise ValueError("changed package dependency "+name)
    prov=decode(source("PROVENANCE.json"))
    for name,r in prov["files"].items():
        raw=source(name)
        assert digest(raw)==r["sha256"]==pins[name]
        assert sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()==r["git_blob"]
    assert digest(source(prov["historical_control"]["path"]))==prov["historical_control"]["sha256"]
    manifest=decode(source(prov["derived_manifest"]))
    result={}
    for name,key in prov["derived_payloads"].items():
        raw=decompress(source("inputs/"+name+".gz"))
        assert digest(raw)==manifest[key]
        result[name]=raw
    return result


def command(path,check=True):
    p=run([sys.executable,"-I","-B",str(path)],capture_output=True,timeout=37)
    if check and p.returncode:
        sys.stderr.write(p.stderr.decode(errors="replace"))
        p.check_returncode()
    return p


def reject(file,script):
    data=file.read_bytes()
    file.write_bytes(data+b"\n")
    result=command(script,check=False)
    assert result.returncode==1 and not result.stdout
    assert b"changed dependency" in result.stderr and file.name.encode() in result.stderr
    file.write_bytes(data)


def inherited_coverage(inputs,price,agreement):
    r87=decode(inputs["R87-PREFIX.json"])
    pair=decode(inputs["R89-PAIR.json"])
    assert r87["head"]==pair["head"]==price["head"]==agreement["head"]
    assert r87["events_processed"]==76466 and not r87["unvisited"]
    assert r87["prime"]==65521
    selects=lambda r:r["key"][1]==118 and 635 in r["pivots"]
    old={tuple(r["key"]):r for r in r87["results"] if selects(r)}
    paired={tuple(r["key"]) for r in pair["results"] if selects(r)}
    exact={tuple(key) for key in agreement["matches"]}
    assert len(old)==81 and len(exact)==74 and paired==exact
    assert {key for key,r in old.items() if r["disposition"]=="rank drop"}==exact
    prior=[]
    cohort=set(price["endpoint_cohort"])
    assert len(cohort)==615 and 635 in cohort
    for key in sorted(old.keys()-exact):
        r=old[key]
        assert r["disposition"]=="excluded" and not r["owned"]
        assert r["exterior_rank"]==len(r["public"])==len(set(r["columns"]))
        assert set(r["columns"]).isdisjoint(cohort)
        assert 0<r["determinant"]<r87["prime"]
        prior.append({k:r[k] for k in ("key","public","exterior_rank","columns","determinant")})
    assert len(prior)==7
    return dict(head=price["head"],caller=price["caller"],chart=118,pivot=635,
        prior_prefix_prime=r87["prime"],authenticated_prior_prefix_failures=prior,
        exact_pairing_keys=sorted(exact),total_frozen_keys=len(old),unresolved=0)


def replay(root,out):
    inputs=authenticate()
    expected=decode(source("receipts/SHA256.json"))
    outputs={}
    def record(name,path,target=None):
        raw=command(path).stdout
        assert digest(raw)==expected[name],("changed receipt",name)
        outputs[name]=raw
        if target:
            target.write_bytes(raw)
        return decode(raw)

    r128,r129=root/"r128",root/"r129"
    for d in ("r128/lead","r128/inputs","r129/lead","r129/inputs","r129/independent/inputs"):
        (root/d).mkdir(parents=True)
    for dst in (r128/"inputs",r129/"inputs",r129/"independent/inputs"):
        for name in ("7334-WORD.json.gz","OLD-WITNESS.json"):
            copyfile(ROOT/"inputs"/name,dst/name)
        (dst/"R89-PAIR.json").write_bytes(inputs["R89-PAIR.json"])
    for dst in (r128/"inputs",r129/"inputs"):
        for name in ("paired_rank.py","paired_support.py","pricing.py"):
            copyfile(ROOT/"inputs"/name,dst/name)
        (dst/"R89-PRICE.json").write_bytes(inputs["R89-PRICE.json"])
    for name in ("quote.py","two_keys.py"):
        copyfile(ROOT/"engines/r128"/name,r128/"lead"/name)
    for name in ("freeze.py","residual.py"):
        copyfile(ROOT/"engines/r129"/name,r129/"lead"/name)
    for name in ("chart118.py","compare.py"):
        copyfile(ROOT/"engines/r129"/name,r129/"independent"/name)
    for dst in (r129/"inputs",r129/"independent/inputs"):
        copyfile(ROOT/"engines/r128/two_keys.py",dst/"R128-two_keys.py")

    price=record("r128/PRICE.json",r128/"lead/quote.py",r128/"lead/PRICE.json")
    first=record("r128/RESULT.json",r128/"lead/two_keys.py",r128/"lead/RESULT.json")
    assert [r["key"] for r in first["results"]]==[[39701,118],[40853,118]]
    assert not first["selected_unvisited"] and first["timeout"] is None
    assert price["target_delta"]=={"4":17,"5":17,"9":-17} and not price["paid_delta"]
    assert (price["complete_paid"],price["complete_productive"],price["surplus"])==(110519,22478,1424)
    assert Fraction(price["complete_probe"][0])>0>Fraction(price["complete_at_fixed_target"][1])
    assert Fraction(price["extra_rank_one_at_crossing_lower"][1])<0
    for dst in (r129/"inputs",r129/"independent/inputs"):
        (dst/"R128-PRICE.json").write_bytes(outputs["r128/PRICE.json"])
        (dst/"R128-RESULT.json").write_bytes(outputs["r128/RESULT.json"])
    record("r129/FROZEN.json",r129/"lead/freeze.py",r129/"lead/FROZEN.json")
    lead=record("r129/LEAD.json",r129/"lead/residual.py",r129/"lead/RESULT.json")
    (r129/"independent/inputs/R129-RESULT.json").write_bytes(outputs["r129/LEAD.json"])
    independent=record("r129/INDEPENDENT.json",r129/"independent/chart118.py",r129/"independent/RESULT.json")
    agreement=record("r129/AGREEMENT.json",r129/"independent/compare.py")
    assert outputs["r129/AGREEMENT.json"]==source("receipts/AGREEMENT.json")
    assert lead["counts"]=={"no exact unit pairing":72} and not lead["provisional"]
    assert independent["representative_count"]==2 and agreement["alias_counts"]==[73,1]
    assert independent["excluded"]==agreement["count"]==74 and agreement["unresolved"]==0
    coverage=inherited_coverage(inputs,price,agreement)
    raw=(dumps(coverage,indent=2,sort_keys=True)+"\n").encode()
    outputs["COVERAGE.json"]=raw
    assert raw==source("receipts/COVERAGE.json")

    assert set(outputs)-{"COVERAGE.json"}==set(expected)

    reject(r128/"inputs/OLD-WITNESS.json",r128/"lead/quote.py")
    reject(r129/"lead/FROZEN.json",r129/"lead/residual.py")
    (r129/"independent/inputs/7334-WORD.json.gz").unlink()
    reject(r129/"independent/inputs/R128-PRICE.json",r129/"independent/chart118.py")
    if out is not None:
        out.mkdir(parents=True)
        for name,data in outputs.items():
            path=out/relative(name)
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(data)
    print("PASS_P104_CHART118_PIVOT635_BOUND prior_prefix=7 exact_pairing=74 total=81 unresolved=0")


def main():
    assert __debug__ and sys.version_info[:2]==(3,12)
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__=="__main__":
    main()
