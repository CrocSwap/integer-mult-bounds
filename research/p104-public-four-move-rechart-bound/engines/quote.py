"""Preprice one shared public ADD chart on the sealed #7277 ancestry stock."""

from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/ADMITTED.json": "c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13",
    "inputs/READBACK.json": "337668788fb39ec9575887f9c5faf438a880471f78d936357dabf7deeac5de82",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "inputs/7314-HELPERS.json": "bf353b3e05d0bf5fe3e49c15673c4cb9203251329bd594009303541cf7fecc09",
    "inputs/7334-CHANGED.json": "f4d3f6ca2d87f8cd68c01ac9f77b69bd5a796f92bd567cea8afe3ac7c72e8e4b",
    "inputs/7277-SUPPORT.json.gz": "a63d766dce9ccc5b7a97057fb298350617cbf78833f0ebc5bb488dec00e71159",
}
SUPPORT_PAYLOAD = "32d05c4efa4c3f6e3cf08fc9dd21478e0fb5218a38556e290966e64193fe2d80"
COMPARATOR = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
PREDECESSOR = "ed090b57ed88f8859e5ff4643645099e6ba856ea"


def unique(rows):
    data = dict(rows)
    if len(rows) != len(data):
        raise ValueError("duplicate input key")
    return data


def interval(x):
    return list(map(str, x))


def matching(rows, point):
    # Price variants of one contact share all four old paid clocks.
    moves = [set(k for row in r["operands"] for k in row["moves"]) for r in rows]
    forbidden = [sum(1 << j for j, right in enumerate(moves) if left & right) for left in moves]
    weights = [Q(r[point][1]) for r in rows]

    @cache
    def best(remaining):
        if not remaining:
            return Q(0), ()
        low = remaining & -remaining
        index = low.bit_length() - 1
        value, chosen = best(remaining & ~forbidden[index])
        return max(best(remaining ^ low), (value + weights[index], (index, *chosen)))

    upper, indexes = best((1 << len(rows)) - 1)
    return {"directed_upper": str(upper), "maximizing_keys": [rows[i]["key"] for i in indexes]}


def main():
    assert __debug__
    raw = {}
    for name, pin in PINS.items():
        raw[name] = (ROOT / name).read_bytes()
        if sha256(raw[name]).hexdigest() != pin:
            raise ValueError(f"changed dependency {name}")

    def read(name):
        return loads(raw[f"inputs/{name}.json"], object_pairs_hook=unique)

    base, admission = read("READBACK"), read("ADMITTED")
    helper, changed = read("7314-HELPERS"), read("7334-CHANGED")
    assert base["head"] == admission["head"] == COMPARATOR
    assert admission["exit"] == 0 and admission["status"] == "independently_reproduced_comparable"
    assert base["caller_head"] == admission["caller"]
    assert helper["complete"] and len(helper["rows"]) == 1101 and len(changed["roles"]) == 14
    helpers = {r["role"] for r in helper["rows"]}
    protected = set(changed["roles"]) | {863,1355,1531,1567,1568}
    assert 319 in protected and len(helpers) == 1101
    support = decompress(raw["inputs/7277-SUPPORT.json.gz"])
    assert sha256(support).hexdigest() == SUPPORT_PAYLOAD
    inherited = loads(support, object_pairs_hook=unique)
    assert inherited["head"] == PREDECESSOR and inherited["scope_exhausted"]
    assert len(inherited["records"]) == 4732

    paired = defaultdict(list)
    for row in inherited["records"]:
        if len(row["contacts"]) == 1 and row["scalar_evidence"] == [[row["contacts"][0], "nonzero_add_source"]]:
            paired[row["contacts"][0]].append(row)
    assert max(map(len, paired.values())) == 2
    paired = {clock:rows for clock,rows in paired.items() if len(rows) == 2}
    assert len(paired) == 184

    def histogram(x):
        return Counter({int(rank): n for rank,n in x.items()})

    paid, targets = histogram(base["paid"]), histogram(base["targets"])
    old = targets.copy()
    old.subtract(paid)
    assert base["copies"] == 17
    assert (sum(paid.values()),sum(targets.values()),sum(r*n for r,n in old.items())) == (110519,22461,1424)
    assert base["empty_root_credits"] == 0
    cost = run_path(str(ROOT / "inputs/pricing.py"))["cost"]
    at = Q(base["new_raw_interval"][1])
    probe = at + Q(1,10**9)
    target = Q("0.0040075385047236")
    assert cost(old, at)[1] < 0

    eligible = positive_legacy = 0
    out, unresolved = [], []
    for clock, operands in sorted(paired.items()):
        operands = sorted(operands, key=lambda x:x["role"])
        roles = {x["role"] for x in operands}
        assert len(roles) == 2 and operands[0]["charts"][1] == operands[1]["charts"][1]
        assert len({t for x in operands for t in x["moves"]}) == 4
        allowed = roles <= helpers and not roles & protected
        eligible += allowed
        old_left = [x["ranks"][0] for x in operands]
        old_right = [x["ranks"][1] for x in operands]
        for offset in range(1-min(old_left), min(old_right)):
            if not offset:
                continue
            rank_shift = Counter()
            for p,q in zip(old_left, old_right, strict=True):
                rank_shift[p+offset] += 17
                rank_shift[q-offset] += 17
                rank_shift[p] -= 17
                rank_shift[q] -= 17
            assert sum(rank_shift.values()) == sum(r*n for r,n in rank_shift.items()) == 0
            paid_delta = {r:n for r,n in sorted(rank_shift.items()) if n}
            if not paid_delta:
                continue
            credit = {r:-n for r,n in paid_delta.items()}
            saving = cost(credit, at)
            if saving[1] <= 0:
                continue
            if saving[0] <= 0:
                unresolved.append([clock,offset])
                continue
            positive_legacy += 1
            if not allowed:
                continue
            new = old.copy()
            new.subtract(paid_delta)
            assert cost(new,probe)[0] > 0
            out.append({
                "key":[clock,offset],
                "operands":[{k:x[k] for k in ("role","moves","charts","ranks")} for x in operands],
                "paid_delta":paid_delta, "target_delta":{}, "delta_midpoint_rank":offset,
                "gross_at_incumbent":interval(saving), "gross_at_moonshot":interval(cost(credit,target)),
                "complete_margin_at_incumbent":interval(cost(new,at)),
                "complete_margin_at_probe":interval(cost(new,probe)),
            })
    assert positive_legacy == 20 and 0 < len(out) <= positive_legacy and not unresolved
    out.sort(key=lambda r:(-Q(r["gross_at_incumbent"][0]),r["key"]))
    current_whole = matching(out,"gross_at_incumbent")
    target_whole = matching(out,"gross_at_moonshot")
    margin_at_target = cost(old,target)[1] + Q(target_whole["directed_upper"])
    assert margin_at_target < 0
    print(dumps({
        "head":COMPARATOR, "caller_head":admission["caller"],
        "word_sha256":admission["inputs"]["WORD.json.gz"], "predecessor_head":PREDECESSOR,
        "input_sha256":PINS, "legacy_payload_sha256":SUPPORT_PAYLOAD,
        "old_crossing_upper":str(at), "price_probe":str(probe), "fixed_moonshot":str(target),
        "old_complete_margin":interval(cost(old,at)), "old_moonshot_margin":interval(cost(old,target)),
        "moonshot_complete_margin_upper":str(margin_at_target),
        "legacy_two_public_move_neighbors":len(paired), "allowed_helper_pairs":eligible,
        "positive_legacy_before_protection":positive_legacy, "protected_roles":sorted(protected),
        "first_case_cap":20, "first_runner_seconds":20, "build_cap":1, "price_unresolved":unresolved,
        "whole_compatible_at_incumbent":current_whole, "whole_compatible_at_moonshot":target_whole,
        "alternatives":out, "scope":"Exact inherited #7277 one-ADD/four-MOVE signatures, restricted to unprotected productive helpers. No current word or span decoded."
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
