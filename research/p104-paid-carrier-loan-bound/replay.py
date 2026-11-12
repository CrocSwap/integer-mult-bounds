"""Replay the fixed-route and nested P104 paid carrier exclusions."""
from argparse import ArgumentParser
from gzip import decompress
from hashlib import sha1,sha256
from json import dumps,loads
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
import sys

ROOT=Path(__file__).resolve().parent


def unique(items):
    out=dict(items)
    if len(out)!=len(items):
        raise ValueError('duplicate JSON key')
    return out


def decode(raw):
    return loads(raw,object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def source(name):
    path=Path(name)
    if path.is_absolute() or '..' in path.parts or path.as_posix()!=name:
        raise ValueError('invalid package-relative path '+name)
    return (ROOT/path).read_bytes()


def load_inputs():
    pins=decode(source('LOCAL-PINS.json'))
    for name,expected in pins.items():
        if digest(source(name))!=expected:
            raise ValueError('changed package dependency '+name)
    p=decode(source('PROVENANCE.json'))
    for name,entry in p['files'].items():
        raw=source(name)
        assert digest(raw)==entry['sha256']==pins[name]
        assert sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==entry['git_blob']
    old=decompress(source('inputs/R92-PRICE.json.gz'))
    assert digest(old)==decode(source('inputs/PR7362-SHA256.json'))['R92-PRICE.json']
    a=decode(source('inputs/ADMITTED.json'))
    assert a['head']=='aaeec8c0acf01e99a5f331ef363a698d9c084ace'
    assert a['kappa']=='0.00364665195644'
    return old


def call(script,*args,expect_success=True):
    p=run([sys.executable,'-I','-B',str(script),*args],capture_output=True,timeout=40)
    if expect_success and p.returncode:
        sys.stderr.write(p.stderr.decode(errors='replace'))
        p.check_returncode()
    return p


def write(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(raw)


def reconcile(raw_word,predecessor,exact,exact_reverse,nested,nested_reverse,lead,reverse):
    word=decode(decompress(raw_word))
    anchors={r["move_clock"]:r for r in predecessor["records"]}
    tape=word["program"]
    frames=word["frames"]
    assert len(anchors)==exact["anchors"]==47 and len(tape)==exact["events"]==76466
    assert not (exact["topology_keys"] or exact["unvisited"] or exact["support_unresolved"]
                or exact_reverse["eligible"])
    counts={r[0]:r[1:] for r in exact_reverse["counts"]}
    assert counts.keys()==anchors.keys()
    assert {k:v for k,v in counts.items() if v!=[0,0]}=={45647:[1,1]}
    erow=anchors[45647]
    incidences=lambda e: e[1:3] if e[0] in ("ADD","COPY") else e[1:2]
    previous=next(t for t in range(45646,-1,-1) if erow["role"] in incidences(tape[t]))
    routes=[(t,e[1]) for t in range(previous+1,45647)
            if (e:=tape[t])[0]=="MOVE" and e[2:4]==[erow["chart_from"],erow["chart_to"]]]
    assert len(routes)==1
    clock,carrier=routes[0]
    blocked=next(t for t in range(clock+1,45648) if carrier in incidences(tape[t]))

    forward={r["anchor"]:r for r in nested["anchors"]}
    backward={r["anchor"]:r for r in nested_reverse["anchors"]}
    assert forward.keys()==backward.keys()==anchors.keys()
    split={}
    for clock_h,h in anchors.items():
        f,b=forward[clock_h],backward[clock_h]
        a,c=h["chart_from"],h["chart_to"]
        assert (f["owner"],f["charts"],f["last_contact"])==(b["h"],[a,c],b["previous"][0])
        assert b["strict_chain"]==f["nested_keys"]
        if len(frames[a])<len(frames[c]):
            assert f["source_moves"]==b["source_moves"]
        else:
            assert len(frames[c])<len(frames[a]) and f["source_moves"]==b["strict_chain"]==0
        if b["source_moves"]:
            split[clock_h]=["ascending" if len(frames[a])<len(frames[c]) else "descending",
                            f["source_moves"],b["source_moves"]]
    assert split=={30581:["ascending",1,1],35434:["descending",0,3],39811:["descending",0,1],
                   44235:["ascending",1,1],45647:["ascending",4,4]}
    assert nested["first_unvisited_event"] is None
    assert not (nested["unresolved_anchors"] or nested["unresolved_keys"] or nested_reverse["unresolved"])
    assert len(nested["prioritized"])==len(nested_reverse["geometry"])==1
    f,b=nested["prioritized"][0],nested_reverse["geometry"][0]
    for fk,bk in (("anchor","anchor"),("owner","h"),("carrier","f"),
                  ("carrier_move","carrier"),("carrier_owned","carrier_owned"),
                  ("charts","charts"),("ranks","ranks"),("public_bank","donor_public"),
                  ("owned_bank","donor_owned"),("price_upper","gross_upper")):
        assert f[fk]==b[bk]
    assert reverse["geometry"]==b and lead["bank_roles"]==b["donor_public"]==[628,630]
    assert lead["key"]==[b["anchor"],b["h"],b["carrier"],b["f"],b["charts"][1]]
    assert lead["source"]==reverse["rows"][str(b["f"])]
    assert lead["result"]["separator"]==reverse["dual"]=={"4":"1"}
    assert lead["result"]["separator_value"]==reverse["value"]=="-1/2"
    assert all("4" not in reverse["rows"][str(r)] for r in b["donor_public"])
    return dict(head=exact["head"],anchored_cases=len(anchors),exact_route_nominal=[45647,clock,carrier],
        exact_route_blocker=[blocked,tape[blocked]],source_incidences=split,forward_ascending=6,
        reverse_all=10,reverse_descending=4,nested_geometry=b,separator={"4":"1"},
        separator_value="-1/2",unresolved=[])


def replay(root,out):
    old=load_inputs()
    expected=decode(source("receipts/SHA256.json"))
    receipts={}
    def record(label,script,*args):
        raw=call(script,*args).stdout
        assert digest(raw)==expected[label],("changed deterministic receipt",label)
        receipts[label]=raw
        return decode(raw)
    def install(target,items):
        for rel,raw in items.items():
            write(target/rel,raw)
    def engine(target,source_name,dest=None):
        path=target/(dest or source_name)
        write(path,source("engines/"+source_name))
        return path

    closure,reverse=root/"lead-root",root/"reverse-root"
    native=source("inputs/7334-WORD.json.gz")
    prior=decompress(source("inputs/R137-RESULT.json.gz"))
    prior_price=source("inputs/R139-PRICE.json")
    assert digest(prior)==decode(source("PROVENANCE.json"))["derived_inputs"]["inputs/R137-RESULT.json.gz"]["decompressed_sha256"]
    install(closure,{"inputs/"+name:data for name,data in (
        ("7334-WORD.json.gz",native),("R137-RESULT.json",prior),("R139-PRICE.json",prior_price),
        ("aggregate.py",source("inputs/aggregate.py")),("donor_span.py",source("inputs/donor_span.py")))})
    lead=engine(closure,"loan.py","lead/loan.py")
    record("R141-PRICE.json",lead,"--price-only")
    write(closure/"lead/PRICE.json",receipts["R141-PRICE.json"])
    exact=record("R141-GEOMETRY.json",lead)
    exact_reverse=record("R141-INDEPENDENT.json",engine(closure,"reverse_audit.py","lead/reverse_audit.py"))
    install(closure,{"next/inputs/R92-PRICE.json":old,"next/inputs/pricing.py":source("inputs/pricing.py")})
    record("R142-PRICE.json",engine(closure,"quote.py","next/quote.py"))
    write(closure/"next/PRICE.json",receipts["R142-PRICE.json"])
    nested=record("R142-GEOMETRY.json",engine(closure,"nested.py","lead/nested.py"))
    support=record("R142-SUPPORT.json",engine(closure,"support.py","lead/support.py"))

    install(reverse,{"inputs/"+name:data for name,data in (
        ("7334-WORD.json.gz",native),("R137-RESULT.json",prior),("R139-PRICE.json",prior_price),
        ("R142-PRICE.json",receipts["R142-PRICE.json"]),("R142-PLAN.md",source("inputs/R142-PLAN.md")))})
    rev_geometry=engine(reverse,"reverse_geometry.py")
    nested_reverse=record("R142-INDEPENDENT-GEOMETRY.json",rev_geometry)
    write(reverse/"GEOMETRY.json",receipts["R142-INDEPENDENT-GEOMETRY.json"])
    rev_span=engine(reverse,"verify_span.py")
    span_reverse=record("R142-INDEPENDENT-SPAN.json",rev_span)
    immediate=engine(closure,"immediate.py","lead/immediate.py")
    for d in (closure,reverse):
        write(d/"inputs/R137-PRICE.json",source("inputs/R137-PRICE.json"))
        write(d/"inputs/R141-REVERSE.json",receipts["R141-INDEPENDENT.json"])
    immediate_price=record("R145-PRICE.json",immediate,"--price-only")
    assert immediate_price["one"]["gross"]==["17","17"]
    assert immediate_price["one"]["paid_delta"]=={"1":-17}
    lead_immediate=record("R145-LEAD.json",immediate)
    write(reverse/"inputs/R145-PLAN.md",source("inputs/R145-PLAN.md"))
    write(reverse/"inputs/R145-PRICE.json",receipts["R145-PRICE.json"])
    engine(reverse,"verify_span.py","inputs/reverse_covectors.py")
    rev_immediate=engine(reverse,"immediate_reverse.py")
    immediate_args=("--price-sha",expected["R145-PRICE.json"])
    independent_immediate=record("R145-INDEPENDENT.json",rev_immediate,*immediate_args)
    assert not independent_immediate["unresolved"]
    assert lead_immediate["source"]==independent_immediate["rows"]["988"]
    assert len(lead_immediate["source"])==137
    assert lead_immediate["bank_roles"]==independent_immediate["donor_public"]+independent_immediate["donor_owned"]
    assert len(independent_immediate["donor_public"])==14 and independent_immediate["donor_owned"]==[1511,1529,1564]
    lead_result=lead_immediate["result"]
    assert lead_result["rank"]==15
    assert lead_result["decision"]==independent_immediate["decision"]=="outside donor span"
    assert lead_result["separator"]==independent_immediate["dual"]=={"2":"-3/2","230":"-3/2","382":"-1","397":"1"}
    assert lead_result["separator_value"]==independent_immediate["value"]=="-2"
    assert set(receipts)==set(expected)
    report=reconcile(native,decode(prior),exact,exact_reverse,nested,nested_reverse,support,span_reverse)
    report_bytes=(dumps(report,indent=2,sort_keys=True)+"\n").encode()
    assert report_bytes==source("receipts/AGREEMENT.json")

    (reverse/"inputs/7334-WORD.json.gz").unlink()
    for path,script,args in ((reverse/"inputs/R142-PRICE.json",rev_geometry,()),
                             (reverse/"GEOMETRY.json",rev_span,()),
                             (reverse/"inputs/R145-PRICE.json",rev_immediate,immediate_args)):
        path.write_bytes(path.read_bytes()+b" ")
        check=call(script,*args,expect_success=False)
        assert check.returncode==1 and b"changed dependency" in check.stderr

    if out is not None:
        out.mkdir(parents=True)
        for name,raw in receipts.items():
            write(out/name,raw)
        write(out/"AGREEMENT.json",report_bytes)
    print("PASS_P104_PAID_CARRIER_LOAN_BOUND anchors=47 exact=0 nested=1 immediate=1 separated=2 unresolved=0")


def main():
    assert __debug__ and sys.version_info[:2]==(3,12)
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__=="__main__":
    main()
