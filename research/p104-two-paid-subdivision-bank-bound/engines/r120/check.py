"""Check exact support of the frozen virtual two-paid-subdivision bank."""
from collections import defaultdict
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "plan/PRICE.json": "b29ff21d96485317003db5d06d3332f71e7158de4fafbbc6b300a45fc5d5e3c6",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/donor_span.py": "4d5306e2c0b7e91c79d22c82e8e760aed2c311979298c558e631975d4d1ae5b1",
    "inputs/paired_support.py": "38c796cbe1a73f386177faf88cd53294d4b911f6cde7fd47cd9fcef3b558373f",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"


def checked(rel):
    data = (ROOT / rel).read_bytes()
    if sha256(data).hexdigest() != PINS[rel]:
        raise ValueError(f"changed dependency {rel}")
    return data


def unique(items):
    doc = dict(items)
    if len(doc) != len(items):
        raise ValueError("duplicate JSON key")
    return doc


def span(basis):
    out = {0}
    for row in basis:
        assert row not in out
        out |= {row ^ item for item in out}
    return out


def contacts(event, role):
    return role in event[1:3] if event[0] in ("ADD", "COPY") else event[1] == role


def geometry(word, price):
    program = word["program"]
    assert (len(program), word["public"], word["owned_fields"]) == (76466, 1501, 68)
    moves, claims = {}, {}
    for record in price["intervals"]:
        assert record["chart"] is None and [record["first"], record["last"]] == [42958, 42960]
        midway = span(record["basis"])
        assert len(midway) == 32 and all(midway != span(frame) for frame in word["frames"])
        claims[record["pair"]] = sorted(midway)
        for clock, role, first, last, low, high in (record["left"], record["right"]):
            assert program[clock] == ["MOVE", role, low, high, False]
            a, c = (span(word["frames"][index]) for index in (low, high))
            assert (len(a), len(c)) == (16, 64) and a < midway < c
            assert not any(contacts(event, role) for event in program[first:clock])
            assert not any(contacts(event, role) for event in program[clock + 1:last])
            assert contacts(program[first - 1], role) and contacts(program[last], role)
            assert [word["initial"][role], word["final"][role]] == [3, 127]
            moves[role] = [clock, program[clock], first, last]
    assert sorted(claims) == [22, 33, 44] and len({tuple(v) for v in claims.values()}) == 3
    return moves, claims


def witness(rows, cohort):
    a, b = ({i: v for i, v in row.items() if i not in cohort} for row in rows)
    axes = sorted(a.keys() | b.keys())
    if not axes:
        return None
    i = axes[0]
    for j in axes[1:]:
        sub = [[a.get(i, 0), a.get(j, 0)], [b.get(i, 0), b.get(j, 0)]]
        det = sub[0][0] * sub[1][1] - sub[0][1] * sub[1][0]
        if det:
            return {"axes": [i, j], "matrix": [list(map(str, row)) for row in sub],
                    "determinant": str(det)}
    return None


def stop(*_):
    raise TimeoutError("hard 25-second gate")


def main():
    assert __debug__
    assert witness([{1: Fraction(1, 2)}, {2: Fraction(-3)}], set())["determinant"] == "-3/2"
    assert witness([{1: Fraction(1, 2)}, {1: Fraction(-3)}], set()) is None
    signal(SIGALRM, stop)
    alarm(25)
    deadline = monotonic() + 23
    price = loads(checked("plan/PRICE.json"), object_pairs_hook=unique)
    raw = decompress(checked("inputs/7334-WORD.json.gz"))
    assert sha256(raw).hexdigest() == PAYLOAD
    word = loads(raw, object_pairs_hook=unique)
    prior = loads(checked("inputs/R92-PRICE.json"), object_pairs_hook=unique)
    cohort = set(prior["endpoint_cohort"])
    assert len(cohort) == 615
    checked("inputs/donor_span.py")
    checked("inputs/paired_support.py")
    snapshot = run_path(str(ROOT / "inputs/donor_span.py"))["snapshot"]
    roles = price["row"]["bank"]["public"]
    cuts = sorted({key[0] for key in price["raw_keys"]})
    assert roles == [572, 1255] and cuts == [42958, 42959, 42960]
    moves, spans = geometry(word, price)
    bank_requests = defaultdict(set)
    _, rows = snapshot(word, bank_requests, {t: set(roles) for t in cuts}, deadline)
    by_cut = {t: [rows[t, r] for r in roles] for t in cuts if all((t, r) in rows for r in roles)}
    assert not by_cut or all(v == next(iter(by_cut.values())) for v in by_cut.values())
    first = by_cut.get(cuts[0])
    proof = witness(first, cohort) if first is not None else None
    unresolved = [key for key in price["raw_keys"] if proof is None or key[0] not in by_cut]
    status = "prefix exclusion" if proof and not unresolved else "prefix rank drop" if first and not proof else "capped"
    if status == "prefix rank drop":
        pair = run_path(str(ROOT / "inputs/paired_support.py"))
        # Only literal prefix rows are transported into the virtual bank. The
        # two paid subpaths act as identities in normalized row coordinates.
        prefix_bank = dict(zip(roles, first, strict=True))
        _, in_basis = pair["pure_kernel"](prefix_bank, cohort, deadline)
        suffixes, _ = pair["suffix_rows"](word, {cuts[0]: prefix_bank}, deadline)
        if cuts[0] in suffixes:
            _, out_basis = pair["pure_kernel"](suffixes[cuts[0]], cohort, deadline)
            exact = pair["paired"](in_basis, out_basis, deadline)
            if exact is None and len(by_cut) == len(cuts):
                status, unresolved = "no rational unit pairing", []
            elif exact:
                status = "exact support survivor"
                proof = {name: {i: str(v) for i, v in row.items()} for name, row in exact.items()}
    alarm(0)
    print(dumps({
        "head": price["head"], "caller": price["caller"], "pins": PINS,
        "status": status, "moves": moves, "fresh_spans": spans,
        "cut_count": len(by_cut), "prefix_events": max(by_cut, default=0),
        "raw_keys": price["raw_keys"], "representative_keys": price["representative_keys"],
        "support_forms": 1, "rows_nnz": list(map(len, first)) if first else None,
        "proof": proof, "unresolved": unresolved,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
