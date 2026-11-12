"""Replay the fixed-native port-conversion and independent body-price exclusions."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha1, sha256
from json import dumps, loads
from pathlib import Path
from subprocess import run
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
ENGINES = ("port_price.py", "contact.py", "body_dimensions.py", "body_cost.py")
INPUTS = ("CALLER.json", "WORD.json.gz", "R92-PRICE.json", "pricing.py", "independent.py",
          "upstream_application.py", "check_odd_physical_binding.py")


def unique(pairs):
    value = dict(pairs)
    if len(value) != len(pairs):
        raise ValueError("duplicate JSON key")
    return value


def source(name):
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != name:
        raise ValueError(f"invalid source path {name}")
    return (ROOT/path).read_bytes()


def decode(raw):
    return loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def authenticate():
    for name, expected in decode(source("LOCAL-PINS.json")).items():
        if digest(source(name)) != expected:
            raise ValueError(f"changed package dependency {name}")
    prov = decode(source("PROVENANCE.json"))
    for name, entry in prov["files"].items():
        raw = source(name)
        assert digest(raw) == entry["sha256"]
        assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == entry["git_blob"]
    for name, entry in prov["derived_inputs"].items():
        assert digest(source(name)) == decode(source(entry["receipt"]))[entry["key"]]
    admitted = decode(source("inputs/ADMITTED.json"))
    assert admitted["head"] == "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert admitted["caller"] == "07a76c5e2738882c0cb322278e56f6cae3c9885d"
    assert admitted["caller_sha256"] == digest(source("inputs/CALLER.json"))
    assert admitted["inputs"]["WORD.json.gz"] == digest(source("inputs/WORD.json.gz"))
    assert admitted["exit"] == 0 and admitted["kappa"] == "0.00364665195644"
    assert set(admitted["stages"]) == {"native", "early", "caller", "frontier"}


def save(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def execute(script, *args, succeeds=True):
    result = run([sys.executable, "-I", "-B", str(script), *map(str,args)], capture_output=True, timeout=17)
    if succeeds:
        if result.returncode:
            sys.stderr.write(result.stderr.decode(errors="replace"))
        result.check_returncode()
    else:
        assert result.returncode == 1 and not result.stdout and b"AssertionError" in result.stderr
    return result.stdout


def replay(tmp, out):
    authenticate()
    for name in ENGINES:
        save(tmp/name, source("engines/"+name))
    for name in INPUTS:
        save(tmp/"inputs"/name, source("inputs/"+name))
    receipts = {}

    def record(name, engine, *args):
        raw = execute(tmp/engine,*args)
        assert raw == source("receipts/"+name), f"changed receipt {name}"
        save(tmp/name, raw)
        receipts[name] = raw
        return decode(raw)

    price = record("R170-PRICE.json", "port_price.py")
    contact = record("R170-CONTACT.json", "contact.py")
    dimensions = record("R171-DIMENSIONS.json", "body_dimensions.py")
    cost = record("R171-COST.json", "body_cost.py", tmp/"R170-CONTACT.json",
                  tmp/"inputs/pricing.py",tmp/"inputs/R92-PRICE.json")
    cp = contact["price"]
    assert price["minimum_lost_rank_one_credits_per_port"] == cp["optimistic_lost_rank_one_helpers_per_port"] == 34
    for kind in ("A","B"):
        assert price["per_port"][kind+"_paid"] == cp["per_port_paid"][kind]
        assert price["per_port"][kind+"_targets"] == cp["per_port_target"][kind]
    old = cp["quoted"]["old_crossing_upper"]
    for lead, indep in zip(price["cases"],old["multiplicities"],strict=True):
        assert lead["ports"] == indep["ports"]
        assert list(map(Q,lead["optimistic_full_margin"])) == list(map(Q,indep["complete_margin"]))
    b = contact["signed_contact"]
    assert (b["port_index"],b["caller_J_clock"],b["specialized_phases"]) == (15,43,[1,-1])
    assert b["B_relative_minus_I_squared"] == [["0","-2"],["2","0"]]
    assert b["A_relative_minus_I_squared"] == [["0"]*4 for _ in range(4)]
    assert dimensions["stage_body_dimensions"] == [8]*34
    assert dimensions["charged_signed_delta_per_port"] == cost["charged_signed_delta_upper"] == {"1":-4,"8":-4,"9":4}
    exact = cost["quote"]["old_crossing_upper"]["one_port_optimistic_relaxation_bounds"]
    assert list(map(Q,dimensions["gain_interval_per_port"])) == list(map(Q,exact))
    assert Q(exact[1]) < Q("-0.04555967541857277")

    caller = tmp/"inputs/CALLER.json"
    caller.write_bytes(caller.read_bytes()+b" ")
    execute(tmp/"contact.py",succeeds=False)
    if out:
        for name, data in receipts.items():
            save(out/name,data)
    print(dumps({"authenticated_receipts":len(receipts),"corrupted_caller_rejected":True,
                 "extra_independent_body_returns":34,"fixed_contacts_excluded":1,
                 "priced_multiplicities":8,"kappa_delta":"0"},sort_keys=True))
    print("PASS_P104_FIXED_CONTACT_PORT_CONVERSION_BOUND")


def main():
    if sys.implementation.name != "cpython" or sys.version_info[:2] != (3,12) or not __debug__:
        raise SystemExit("CPython 3.12 with assertions is required")
    p=ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    with TemporaryDirectory(prefix="p104-port-conversion-") as d:
        replay(Path(d),args.out)


if __name__ == "__main__":
    main()
