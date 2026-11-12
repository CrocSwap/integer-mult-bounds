"""Authenticate the frozen four-role prefix representatives."""
from gzip import decompress
from hashlib import sha256
from json import loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "lead/PREFIX.json": "6525f616502fe23c155e5c96138e85142401c8fdfddc266c6aa1ced64299da8d",
    "lead/GEOMETRY.json": "a089e2663b2069b39d4971670dc980f38ed3d3411fdabed3a4ac24167ae12239",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
FIXED = {"533": "1", "1481": "1"}
CAP = 25


def unique(pairs):
    out = dict(pairs)
    if len(out) != len(pairs):
        raise ValueError("duplicate JSON key")
    return out


def load(raw):
    return loads(raw, object_pairs_hook=unique)


def start():
    def stop(*_):
        raise TimeoutError("25-second replay cap")

    signal(SIGALRM, stop)
    alarm(CAP)


def inputs(archived=False):
    files = {}
    for path, digest in PINS.items():
        raw = (ROOT / path).read_bytes()
        if sha256(raw).hexdigest() != digest:
            raise ValueError(f"changed dependency {path}")
        files[path] = raw
    old = load(files["lead/PREFIX.json"])
    keys = [tuple(k) for k in old["selected" if archived else "unvisited"]]
    assert len(keys) == len(set(keys)) == (8 if archived else 7)
    assert old["counts"] == {"exact_rank_exclusion": 8}
    witnesses = [row["proof"]["separating_covector"] for row in old["rows"]]
    assert witnesses.count(FIXED) == 7
    geo = load(files["lead/GEOMETRY.json"])
    assert (geo["head"], geo["caller"]) == (HEAD, CALLER)
    cuts = {}
    for x in geo["unresolved"]:
        first_role, last_role, chart, lo, hi = x["range"]
        assert (lo, hi) == (x["segment"]["first"], x["segment"]["last"])
        key = (first_role, last_role, 1454, 1251, chart, hi)
        assert key not in cuts
        cuts[key] = (lo, hi)
    cuts = {key: cuts[key] for key in keys}
    assert sum(hi - lo + 1 for lo, hi in cuts.values()) == (16016 if archived else 478)
    raw = decompress(files["inputs/7334-WORD.json.gz"])
    assert sha256(raw).hexdigest() == PAYLOAD
    word = load(raw)
    assert (word["public"], word["owned_fields"], len(word["program"])) == (1501, 68, 76466)
    for key, (lo, hi) in cuts.items():
        roles = set(key[:4])
        for op, dst, *args in word["program"][lo:hi]:
            # A cut is before its event. The event at hi belongs to the next state.
            assert dst not in roles
            assert op not in ("ADD", "COPY") or args[0] not in roles
    return keys, cuts, word
