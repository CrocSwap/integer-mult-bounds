"""Replay one retimed four-field Type A host and the physical sign witnesses."""
from argparse import ArgumentParser
import ast
from fractions import Fraction as Q
from hashlib import sha1, sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from subprocess import run
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
FORWARD = "host_forward.py"
REVERSE = "host_reverse.py"


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def source(name):
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != name:
        raise ValueError(f"invalid source path {name}")
    return (ROOT/path).read_bytes()


def decode(raw):
    return loads(raw, object_pairs_hook=unique)


def read_json(name):
    return decode(source(name))


def digest(raw):
    return sha256(raw).hexdigest()


def authenticate():
    for name, expected in read_json("LOCAL-PINS.json").items():
        raw = source(name)
        if digest(raw) != expected:
            raise ValueError(f"changed package dependency {name}")
        if name.endswith(".json"):
            decode(raw)
    prov = read_json("PROVENANCE.json")
    for name, entry in prov["files"].items():
        raw = source(name)
        assert digest(raw) == entry["sha256"]
        assert sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest() == entry["git_blob"]
    price = prov["derived_inputs"]["inputs/R92-PRICE.json"]
    assert digest(source("inputs/R92-PRICE.json")) == read_json(price["receipt"])[price["key"]]
    signed = read_json("inputs/7113-SHA256.json")
    prefix = "replay/supplier7112/short-caller/"
    for name, original in (
        ("7113-application.py", prefix+"upstream_application.py"),
        ("7113-signed-child.py", prefix+"signed_child.py"),
        ("CALLER.json", "expected/ODD-TYPE-AB-CALLER.json"),
        ("PHYSICAL-BINDING.json", "expected/ODD-PHYSICAL-BINDING.json"),
    ):
        assert digest(source("inputs/"+name)) == signed[original]
    peer = read_json("inputs/PR7404-RESULT.json")
    assert peer["source_pins"] == prov["peer7404"]["exact_prior_source_pins"]
    assert peer["port"] == 0


def save(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def execute(script, *args, succeeds=True):
    result = run([sys.executable, "-I", "-B", str(script), *args], capture_output=True, timeout=12)
    if succeeds:
        if result.returncode:
            sys.stderr.write(result.stderr.decode(errors="replace"))
        result.check_returncode()
    else:
        assert result.returncode != 0 and b"AssertionError" in result.stderr
        assert not result.stdout
    return result.stdout


def physical_signs():
    child = ast.parse(source("inputs/7113-signed-child.py"))
    gate, = [ast.literal_eval(node.value) for node in child.body
             if isinstance(node, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == "C" for t in node.targets)]
    for vector, expected in (((1, 1), (2, 0)), ((1, -1), (0, 2))):
        for coeffs, sign in zip(gate, vector, strict=True):
            actual = tuple(sum(a[i]*v for a, v in zip(coeffs, vector, strict=True)) for i in range(2))
            assert actual == tuple(sign*x for x in expected)
    app = source("inputs/7113-application.py").decode()
    assert "fresh = [1 << (9+8*(stage-1)+j) for j in range(8)]" in app
    assert "need(transform(q) == q" in app
    assert "body = terms((1 << j, 1) for j in range(9+8*(stage-1), 9+8*stage))" in app
    binding = read_json("inputs/PHYSICAL-BINDING.json")
    assert binding["caller_sha256"] == digest(source("inputs/CALLER.json"))
    assert binding["source_reviewer_sha256"] == digest(source("inputs/7113-application.py"))
    caller = read_json("inputs/CALLER.json")
    assert binding["occurrence_and_geometry"]["ambient"] == caller["ambient_rank"] == 145
    assert caller["types"]["A"]["ports"][0] == 0
    stage = list(range(9+8*7, 9+8*8))
    central = read_json("inputs/PR7404-RESULT.json")["carrier_checks"]["central_axis"]
    assert central == 11 and central.bit_length() <= 9 and central.bit_count() % 2 == 1
    assert stage == list(range(65, 73))
    for j in stage:
        assert (central & (1 << j)) == 0
    # At f=2 a single central direction and each body axis have two
    # independent binary copies. Using exactly two minus Walsh factors
    # multiplies the relevant group by i^2 while leaving the other alone.
    def sign(minus_factors):
        return ((1, 0), (0, 1), (-1, 0), (0, -1))[minus_factors % 4]
    plus, minus = (1, 0), (-1, 0)
    observed = [(sign(q), sign(body)) for q, body in ((0, 0), (0, 2), (2, 0))]
    assert observed == [(plus, plus), (plus, minus), (minus, plus)]


def retiming_control(engine):
    f = run_path(str(engine))
    caller = read_json("inputs/CALLER.json")
    peer = read_json("inputs/PR7404-RESULT.json")
    events = caller["events"]
    indexed, before, after = f["retiming"](events, peer)
    old_clock = peer["hoisted_paid_idles"][0]["canceled_adds"][0]
    assert old_clock not in {i for i, _ in after}
    mutant = sorted(after+[(old_clock, events[old_clock])])
    body = Q(-1)
    orig = f["tape"](indexed, 1, body)
    j = f["tape"]([(1423, events[1423])], 1, body)
    prefix = f["multiply"](j, f["tape"](before, 1, body))
    assert f["multiply"](f["tape"](after, 1, body), prefix) == orig
    assert f["multiply"](f["tape"](mutant, 1, body), prefix) != orig


def replay(tmp, out):
    authenticate()
    for path in (ROOT/"inputs").iterdir():
        save(tmp/"inputs"/path.name, source("inputs/"+path.name))
    for engine in (FORWARD, REVERSE):
        save(tmp/engine, source("engines/"+engine))
    results = []
    for engine, receipt, args in (
        (FORWARD, "R174-PRICE.json", ("--price-only",)),
        (FORWARD, "R174-FORWARD.json", ()),
        (REVERSE, "R174-REVERSE.json", ()),
    ):
        raw = execute(tmp/engine, *args)
        assert raw == source("receipts/"+receipt), f"changed receipt {receipt}"
        results.append(decode(raw))
        if out:
            save(out/receipt, raw)
    price, forward, reverse = results
    assert forward["price"] == price["price"]
    assert forward["peer_head"] == price["peer_head"] == "aadd1de3e520cfd1e5b062729bd76f543dc879f4"
    assert forward["host"] == reverse["window_host"] == 1423
    assert forward["demote_queries"] == reverse["queries"] == [1580, 1659]
    assert forward["bound"] == reverse["host_roles"] == [8, 0, 18, 26]
    assert forward["price"]["roots"] == reverse["retired_roles"] == [0, 18]
    assert forward["caps"]["basis_columns"] == reverse["basis_columns"] == 36
    assert forward["body_minor"] == "16"
    assert forward["outside_nonzero_count"] == reverse["outside_nonzero_count"] == 320
    assert forward["first_outside_entries"] == reverse["first_outside_entries"]
    assert forward["first_outside_entries"][0] == [8, 1, "-2"]
    one, all_ports = (price["price"]["ports"][key] for key in ("1", "96"))
    assert Q("0.04231287836140672") < Q(one["complete_at_probe"][0])
    assert Q(one["gross_at_crossing_upper"][1]) < Q("0.04270044187346692") < 1
    assert Q(all_ports["gross_at_crossing_upper"][1]) < Q("4.099242419852824")
    physical_signs()
    retiming_control(tmp/FORWARD)
    caller = tmp/"inputs/CALLER.json"
    caller.write_bytes(caller.read_bytes()+b" ")
    execute(tmp/REVERSE, succeeds=False)
    print(dumps({"authenticated_receipts":3, "basis_columns":36,
                 "body_minor":"16", "physical_sector_count":3,
                 "outside_nonzero_count":320, "kappa_delta":"0",
                 "mutated_caller_and_retiming_rejected":True}, sort_keys=True))
    print("PASS_P104_RETIMED_TYPE_A_STAGE8_HOST_BOUND")


def main():
    if sys.implementation.name != "cpython" or sys.version_info[:2] != (3, 12) or not __debug__:
        raise SystemExit("CPython 3.12 with assertions is required")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    with TemporaryDirectory(prefix="p104-retimed-stage8-") as d:
        replay(Path(d), args.out)


if __name__ == "__main__":
    main()
