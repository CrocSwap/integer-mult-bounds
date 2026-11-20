"""Bind the native proofs and the changed mixed prices to immutable Git objects."""

import gzip
import hashlib
import json
import subprocess
from fractions import Fraction


MIXED = "87fbf4f7b35b0f18ab12b5767775a9a424cf0b15"
NATIVE = "a7f99a5f5f919dd3ffb2987f90c1e7d6527feb1e"
MP = "research/p104-mixed-rank-supplier"
NP = "research/grade14-native-realization"


def blob(head, path):
    return subprocess.check_output(["git", "show", f"{head}:{path}"])


def document(head, path):
    return json.loads(blob(head, path))


def require(ok, claim):
    if not ok:
        raise ValueError(claim)


def hash_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def run():
    mixed = document(MIXED, f"{MP}/RESULT.json")
    audit = document(MIXED, f"{MP}/AUDIT.json")
    binary = document(MIXED, f"{MP}/BIT.json")
    origins = document(NATIVE, f"{NP}/ORIGINS.json")
    pins = document(MIXED, f"{MP}/SOURCES.json")
    old_audit = document(NATIVE, f"{NP}/retained/grade14-audit.json")
    old_binary = document(NATIVE, f"{NP}/retained/grade14-bit.json")
    require(binary["native"] == old_binary["native"], "complete binary native record")
    changes = sorted(k for k in audit | old_audit if audit.get(k) != old_audit.get(k))
    require(changes == ["compiler_report_sha256", "outer"], "complete complex physical record")
    for local, field in (("binary", "binary_word"), ("complex", "rational_word"), ("layout", "layout")):
        name = f"retained/data/{local}.json.gz"
        old = next(row for row in origins if row["local"] == name)
        new = next(row for row in pins if row["path"] == old["source"])
        raw = blob(NATIVE, f"{NP}/{name}")
        require(raw == blob(new["head"], new["path"]) and hash_bytes(raw) == new["sha256"] == old["sha256"],
                f"same compressed source for {local}")
        canonical = json.dumps(json.loads(gzip.decompress(raw)), sort_keys=True, separators=(",", ":")).encode()
        require(hash_bytes(canonical) == (mixed.get(field) or audit[field]), f"canonical {local}")
    actual = [
        [sum(binary["native"][k].values()) for k in ("targets", "paid")],
        [sum(audit["signed"][k].values()) for k in ("productive", "paid")],
    ]
    require(actual == [[20706, 107460], [52512, 283152]], "complete word populations")
    stock = binary["delayed_cover_and_stock"]
    rate = Fraction(stock["covered"])
    previous = Fraction(0)
    for step in [dict(claim=stock["seed"])] + stock["stages"]:
        claim = Fraction(step["claim"])
        envelope = (249*rate + previous)/250
        require(previous < claim < envelope < Fraction(1, 250), "strict stage and stock room")
        if "previous" in step:
            require(Fraction(step["previous"]) == previous and all(Fraction(e) == envelope for e in step["envelope"]),
                    "source stage binding")
        previous = claim
    gate = audit["outer"]["finite_compiler"]
    require(previous == Fraction(mixed["binary_ordinary"]) and previous - Fraction(gate["tested"]) == Fraction(1, 62500000000000),
            "separate supplier budgets")
    h = int(gate["H"])
    c = audit["common_root"]["common_context_c"]
    bits = (c*1920*153**1920*(h+1)**2).bit_length()
    require((h, c, bits) == (15171300000000000000, 856, 14083) and bits < h, "same full root guard")
    print(f"mixed {MIXED} native {NATIVE}")
    print(f"native words and route layout match; binary and complex target/paid counts {actual}")
    print(f"six stages from zero; complex trial {gate['tested']}; ordinary {previous}; depth guard {bits} < {h}")


if __name__ == "__main__":
    run()
