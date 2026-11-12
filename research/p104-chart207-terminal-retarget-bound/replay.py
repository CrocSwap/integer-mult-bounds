"""Replay the four exact chart-207 terminal exclusion scopes."""
from argparse import ArgumentParser
from fractions import Fraction
from gzip import decompress
from hashlib import sha1, sha256
from json import loads
from pathlib import Path, PurePosixPath
from shutil import copyfile
from subprocess import run
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate JSON key")
    return result


def decode(raw):
    return loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def relative(name):
    path = PurePosixPath(name)
    if path.is_absolute() or path.as_posix() != name or ".." in path.parts:
        raise ValueError(f"invalid relative path {name}")
    return path


def authenticate():
    pins = decode((ROOT / "LOCAL-PINS.json").read_bytes())
    for name, expected in pins.items():
        if digest((ROOT / relative(name)).read_bytes()) != expected:
            raise ValueError(f"changed package dependency {name}")
    source = decode((ROOT / "PROVENANCE.json").read_bytes())
    for name, record in source["files"].items():
        raw = (ROOT / relative(name)).read_bytes()
        assert digest(raw) == record["sha256"] == pins[name]
        assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == record["git_blob"]
    result = {}
    for name, record in source["derived_payloads"].items():
        raw = decompress((ROOT / "inputs" / (name + ".gz")).read_bytes())
        manifest = decode((ROOT / relative(record["manifest"])).read_bytes())
        assert digest(raw) == manifest[record["key"]]
        result[name] = raw
    return result


def command(root, script, *args, check=True):
    answer = run([sys.executable, "-I", "-B", str(root / script), *map(str,args)],
                 capture_output=True, timeout=27)
    if check and answer.returncode:
        sys.stderr.write(answer.stderr.decode(errors="replace"))
        answer.check_returncode()
    return answer


def setup(root, folder, script, payloads):
    (root / folder).mkdir(parents=True)
    copyfile(ROOT / "engines" / script, root / folder / script)
    (root / "inputs").mkdir(exist_ok=True)
    copyfile(ROOT / "inputs/7334-WORD.json.gz", root / "inputs/7334-WORD.json.gz")
    for name, raw in payloads.items():
        (root / "inputs" / name).write_bytes(raw)


def reject(root, name, script, *args):
    path = root / relative(name)
    before = path.read_bytes()
    path.write_bytes(before + b"\n")
    changed = command(root, script, *args, check=False)
    assert changed.returncode == 1 and not changed.stdout
    assert (b"changed input" in changed.stderr or b"changed dependency" in changed.stderr)
    assert path.name.encode() in changed.stderr
    path.write_bytes(before)


def replay(root, out):
    source = authenticate()
    expected = decode((ROOT / "receipts/SHA256.json").read_bytes())
    receipts = {}

    def record(key, work, script, *args, target=None):
        data = command(work, script, *args).stdout
        assert digest(data) == expected[key], ("changed receipt", key)
        receipts[key] = data
        if target is not None:
            (work / target).write_bytes(data)
        return decode(data)

    direct = root / "direct"
    direct_inputs = source | {"pricing.py": (ROOT / "inputs/pricing.py").read_bytes()}
    setup(direct, "lead", "terminal.py", direct_inputs)
    price = record("r132/PRICE.json", direct, "lead/terminal.py", "price", "--inputs", direct/"inputs",
                   target="lead/PRICE.json")
    lead = record("r132/LEAD.json", direct, "lead/terminal.py", "support", "--inputs", direct/"inputs",
                  "--price-sha", expected["r132/PRICE.json"])
    direct_ind = root / "direct-independent"
    setup(direct_ind, ".", "terminal_reverse.py", {"PRICE.json":receipts["r132/PRICE.json"],
          "LEAD.json":receipts["r132/LEAD.json"],"R92-PRICE.json":source["R92-PRICE.json"]})
    reverse = record("r132/INDEPENDENT.json", direct_ind, "terminal_reverse.py")
    assert reverse["excluded"] == 6 and not reverse["unresolved"]
    assert reverse["dispositions"] == lead["dispositions"]
    assert reverse["first_binary_at_move_plus_one"] == 5 and not reverse["owner_contacts"]
    assert sum(r["binary_contacts"] for r in reverse["dispositions"].values()) == 203
    assert [reverse[x] for x in ("old_productive_rank","new_productive_rank","removed_paid_rank")] == [9,8,1]
    assert Fraction(price["quotes"]["probe"]["one_edit_margin"][0]) > 0
    assert Fraction(price["quotes"]["old_crossing_upper"]["six_edit_gross"][1]) < Fraction("1.161771723173607")
    reject(direct, "inputs/R92-PRICE.json", "lead/terminal.py", "price", "--inputs", direct/"inputs")

    retime = root / "retime"
    setup(retime, "lead", "two_add.py", {
        "R100-GEOMETRY.json":source["R100-GEOMETRY.json"],
        "R130-retime.py":(ROOT/"inputs/R130-retime.py").read_bytes(),
        "R132-PRICE.json":receipts["r132/PRICE.json"],"R132-RESULT.json":receipts["r132/LEAD.json"],
    })
    quote = record("r134/PRICE.json", retime, "lead/two_add.py", "price", target="lead/PRICE.json")
    result = record("r134/LEAD.json", retime, "lead/two_add.py", "support", "--price-sha",
                    expected["r134/PRICE.json"])
    retime_ind = root / "retime-independent"
    setup(retime_ind, ".", "occupancy.py", {"PRICE.json":receipts["r134/PRICE.json"],
          "LEAD.json":receipts["r134/LEAD.json"]})
    other = record("r134/INDEPENDENT.json", retime_ind, "occupancy.py")
    assert other["excluded"] == 2 and not other["unresolved"]
    assert result["typed_cuts"] == other["typed_cuts"] == 5084
    assert result["commutator_steps"] == 17391
    assert set(other["partner_histories"]) == {"1","232","363","773"}
    assert all(not p["global_chart207_cuts"] for r in other["results"] for p in r["placements"])
    assert Fraction(quote["quotes"]["old_crossing_upper"]["whole_two_gross_upper"]) < Fraction("0.387257241057869")
    (retime_ind/"inputs/7334-WORD.json.gz").unlink()
    reject(retime_ind, "inputs/PRICE.json", "occupancy.py")

    aggregate = root / "aggregate"
    earlier = {
        "R132-PRICE.json":receipts["r132/PRICE.json"],"R132-RESULT.json":receipts["r132/LEAD.json"],
        "R134-PRICE.json":receipts["r134/PRICE.json"],"R134-RESULT.json":receipts["r134/LEAD.json"],
    }
    support = {name:(ROOT/"inputs"/name).read_bytes() for name in ("aggregate.py","donor_span.py")}
    setup(aggregate, "lead", "timed_aggregate.py", earlier | support)
    priced = record("r135/PRICE.json", aggregate, "lead/timed_aggregate.py", "--price-only", target="lead/PRICE.json")
    timed = record("r135/LEAD.json", aggregate, "lead/timed_aggregate.py")
    aggregate_ind = root / "aggregate-independent"
    setup(aggregate_ind, ".", "terminal_dual.py", earlier | {
        "R135-PRICE.json":receipts["r135/PRICE.json"],"R135-LEAD-RESULT.json":receipts["r135/LEAD.json"],
    })
    dual = record("r135/INDEPENDENT.json", aggregate_ind, "terminal_dual.py")
    assert priced["compatible_cap"] == 1 and priced["paid_delta"] == {"1":-17}
    assert priced["productive_delta"] == {"8":17,"9":-17}
    assert Fraction(priced["probe"][0]) > 0 > Fraction(priced["fixed_target"][1])
    assert timed["cuts"] == [44613,46018] and timed["last_contact"][0] == 44612
    assert timed["cut_count"] == 1406 and timed["cut_role_pairs"] == 13732
    assert timed["distinct_role_rows"] == 17 and timed["disposition"]["rank"] == 12
    assert len(timed["aggregate"]) == 23 and dual["aggregate"] == timed["aggregate"]
    assert dual["coverage"] == {"cut_count":1406,"cut_role_pairs":13732,"first_last_cuts":[44613,46018]}
    assert dual["separator"] == timed["disposition"]["separator"] == {"2":"1","3":"-1/2","27":"-1","28":"1"}
    assert dual["separator_verified"] and dual["separator_on_aggregate"] == "1" and not dual["nonzero_donors"]
    assert not timed["unvisited_cuts"] and not dual["unresolved_cuts"]
    (aggregate_ind/"inputs/7334-WORD.json.gz").unlink()
    reject(aggregate_ind, "inputs/R135-PRICE.json", "terminal_dual.py")

    closure = root / "closure"
    cohort_inputs = {"R92-PRICE.json":source["R92-PRICE.json"],
                     "R132-PRICE.json":receipts["r132/PRICE.json"]}
    setup(closure, "lead", "coframe.py", cohort_inputs)
    cohort = record("r136/PRICE.json", closure, "lead/coframe.py", "--price-only")
    full = record("r136/LEAD.json", closure, "lead/coframe.py")
    closure_ind = root / "closure-independent"
    setup(closure_ind, ".", "reverse_closure.py", cohort_inputs | {
        "R136-PRICE.json":receipts["r136/PRICE.json"],
        "R136-PLAN.md":(ROOT/"inputs/R136-PLAN.md").read_bytes(),
    })
    copyfile(ROOT/"engines/compare.py", closure_ind/"compare.py")
    (closure_ind/"inputs/R136-LEAD-RESULT.json").write_bytes(receipts["r136/LEAD.json"])
    closed = record("r136/INDEPENDENT.json", closure_ind, "reverse_closure.py", target="RESULT.json")
    agreement = record("r136/AGREEMENT.json", closure_ind, "compare.py")
    assert receipts["r136/AGREEMENT.json"] == (ROOT/"receipts/R136-AGREEMENT.json").read_bytes()
    assert len(cohort["roles"]) == agreement["roles"] == closed["roles_visited"] == 615
    assert Fraction(cohort["whole_gross_upper"]) == 615*Fraction(cohort["one_gross"][1])
    assert Fraction(cohort["fixed_target_complete_upper"]) < 0
    assert full["anchors"] == closed["anchors"] == price["anchors"] and agreement["terminal_anchors"] == 6
    assert full["edges"] == closed["edges"] == []
    assert agreement["external_contacts"] == len(closed["external_contacts"]) == 203
    assert all(len(g["roles"]) == 1 and g["first_exterior"] for g in closed["groups"])
    assert closed["unary"] == [[49151,1081,"1/2"]]
    assert closed["protected_role319_last_move"] == [44623,1089,127]
    assert full["survivors"] == closed["survivors"] == full["unresolved"] == closed["unresolved"] == []
    (closure_ind/"inputs/7334-WORD.json.gz").unlink()
    reject(closure_ind, "inputs/R136-PLAN.md", "reverse_closure.py")

    assert set(receipts) == set(expected)
    if out is not None:
        out.mkdir(parents=True)
        for name,raw in receipts.items():
            path = out / relative(name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
    print("PASS_CHART207_TERMINAL_RETARGET_BOUND direct=6 retime=2 partner_absences=4 aggregate_pairs=13732 cohort=615 exterior=203 internal=0 unresolved=0")


def main():
    assert __debug__ and sys.version_info[:2] == (3,12)
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="new directory for all thirteen regenerated receipts")
    args = parser.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp), args.out)


if __name__ == "__main__":
    main()
