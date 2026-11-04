"""Replay the proof's finite certificates using only package files and stdlib."""
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from checks import controls, scientific_result, sign_rows
from flat_check import flat_examples
from headers import census
from laws import full_flat, universal_positive_size
from scaling import brackets
from triples import box_triple, certificates
from ternary import four_rows


def sources():
    meta = json.loads((HERE/"SOURCES.json").read_text(encoding="utf8"))
    count = 0
    for row in meta["files"]:
        if "vendored_as" not in row:
            continue
        data = (HERE/row["vendored_as"]).read_bytes()
        oid = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if oid != row["git_blob"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise ValueError("source bytes or Git blob")
        if "upstream_origin" in row:
            origin = row["upstream_origin"]
            if origin["git_blob"] != oid or not row["pin"].endswith(":" + row["path"]):
                raise ValueError("pending source binding")
        count += 1
    if count != 7:
        raise ValueError("source inventory")
    return count


def frozen(name, value):
    if json.loads(json.dumps(value)) != json.loads((HERE/name).read_text(encoding="utf8")):
        raise ValueError("frozen result: " + name)


def smoke():
    controls()
    row = census(5, 2, [(1, i) for i in range(5)])
    if row["masks"] != {"0": 80, "15": 64, "23": 64, "27": 64, "29": 64, "30": 64, "31": 80}:
        raise ValueError("literal five-direction matrix guard")
    if box_triple(3, 3) != Fraction(20, 117):
        raise ValueError("affine box triple anchor")
    if full_flat(3, 3, 4) != Fraction(17, 520):
        raise ValueError("full affine flat anchor")
    if universal_positive_size(3) != 5:
        raise ValueError("ternary dense-size anchor")
    four_rows()


def main():
    n = sources()
    if sys.argv[1:] == ["--controls"]:
        smoke()
        print(json.dumps(dict(status="PASS_PENCIL_SEMANTIC_CONTROLS",sources=n)))
        return
    if sys.argv[1:]:
        raise ValueError("unknown mode")
    result = scientific_result()
    signs = sign_rows()
    frozen("RESULT.json", result)
    frozen("SIGN-WINDOWS.json", signs)
    frozen("ASYMPTOTICS.json", brackets())
    frozen("FULL-FLATS.json", flat_examples())
    triples = certificates()
    quartets = four_rows()
    frozen("TRIPLE-CERTIFICATES.json", triples)
    frozen("TERNARY-FOUR.json", quartets)
    print(json.dumps(dict(status="PASS_COMMON_IMAGE_GUARD_LAW",sources=n,
                          prefix_cases=len(result["raw_prefix_cases"]),
                          triple_exceptions=sum(len(x["exceptions"]) for x in triples),
                          ternary_quartets=len(quartets["exceptions"]),
                          formula_checks=result["finite_formula_checks"],
                          sign_windows=len(signs["windows"]),sign_cases=signs["finite_comparisons"])))


if __name__ == "__main__":
    main()
