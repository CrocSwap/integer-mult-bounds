"""Verify the fixed two-host Type A support obstruction on exact pinned inputs."""
from fractions import Fraction
from hashlib import sha1, sha256
from json import loads
from pathlib import Path
from subprocess import CalledProcessError, run
from tempfile import TemporaryDirectory
import sys

ROOT = Path(__file__).resolve().parent
HEAD, CALLER, PEER = (
    "aaeec8c0acf01e99a5f331ef363a698d9c084ace",
    "07a76c5e2738882c0cb322278e56f6cae3c9885d",
    "aadd1de3e520cfd1e5b062729bd76f543dc879f4",
)


def unique(items):
    out = dict(items)
    if len(out) != len(items):
        raise ValueError("duplicate dependency or receipt key")
    return out


def decode(raw):
    return loads(raw, object_pairs_hook=unique)


def source(name):
    p = Path(name)
    if p.is_absolute() or ".." in p.parts or p.as_posix() != name:
        raise ValueError("invalid relative path " + name)
    return (ROOT / p).read_bytes()


def digest(raw):
    return sha256(raw).hexdigest()


def replay(stage):
    pins = decode(source("LOCAL-PINS.json"))
    for name, expected in pins.items():
        if digest(source(name)) != expected:
            raise ValueError("changed package input " + name)
    provenance = decode(source("PROVENANCE.json"))
    for name, entry in provenance["files"].items():
        raw = source(name)
        assert digest(raw) == entry["sha256"] == pins[name]
        assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == entry["git_blob"]
    stock = decode(source("inputs/PR7362-SHA256.json"))
    assert stock["R92-PRICE.json"] == pins["inputs/R92-PRICE.json"]

    def copy(name, data):
        path = stage / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def launch(name, *args):
        return run(
            [sys.executable, "-I", "-B", "-X", f"pycache_prefix={stage / 'pycache'}", str(stage / name), *args],
            check=True, capture_output=True, timeout=35,
        ).stdout

    def record(file, data):
        assert digest(data) == pins["receipts/" + file], file
        return decode(data)

    for name in pins:
        if name.startswith("inputs/"):
            copy(name, source(name))
        elif name.startswith("engines/"):
            copy(Path(name).name, source(name))
    copy("inputs/retiming.py", source("engines/host_forward.py"))
    price = launch("host_forward.py", "--price-only")
    priced = record("R174-PRICE.json", price)
    assert (priced["native_head"], priced["caller_head"], priced["peer_head"]) == (HEAD, CALLER, PEER)
    assert Fraction(priced["price"]["ports"]["1"]["gross_at_crossing_upper"][0]) > 0
    copy("PRICE.json", price)
    copy("inputs/R174-PRICE.json", price)

    a = record("R182-SUPPORT.json", launch("dual_support.py"))
    b = record("R183-CORNER.json", launch("untouched_corner.py"))
    assert all((r["head"], r["caller"], r["peer"]) == (HEAD, CALLER, PEER) for r in (a, b))
    assert a["hosts"] == {"1423": [8, [8, 0, 18, 26]], "3058": [9, [9, 0, 18, 27]]}
    assert a["demoted"] == [1580, 1659] and a["retired"] == [0, 18]
    assert a["output_test"]["span_rank"] == a["input_test"]["span_rank"] == 7
    assert a["output_test"]["residual_rank"] == a["input_test"]["residual_rank"] == 3
    assert a["output_test"]["outside_count"] == 0 and a["input_test"]["outside_count"] == 2
    witness = a["input_test"]["violations"]["0"]
    assert witness == {"annihilator": {"0": "2", "1": "1"}, "generator_values": ["0"] * 8, "target_value": "2"}
    assert b["result"] == {"decision": "EXCLUDED untouched corner", "first": [19, 19, "4"]}
    assert not b["predecessor"]["decision"].startswith("EXCLUDED")

    copy("inputs/PR7404-RESULT.json", source("inputs/PR7404-RESULT.json") + b" ")
    try:
        launch("dual_support.py")
    except CalledProcessError as exc:
        assert exc.returncode == 1 and b"inputs/PR7404-RESULT.json" in exc.stderr
    else:
        raise AssertionError("altered retiming accepted")
    print("PASS_P104_TWO_HOST_QUERY_BOUND output_rank=7 input_exterior=2 untouched_corner=4 unresolved=0")


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12)
    with TemporaryDirectory() as tmp:
        replay(Path(tmp))


if __name__ == "__main__":
    main()
