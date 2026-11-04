"""Regenerate the complete literal GL histograms and their determinant slices."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from dependency import joint
from finite import Field
from headers import census, check_expected
from laws import pattern


def independent(k):
    return [(1, *(int(j == i) for j in range(1, k))) for i in range(k)]


def pencil_forms(q):
    return [(1, a) for a in range(q)]


def experiments(large=False):
    if large:
        return [(4, 3, pencil_forms(4), "pencil")]
    return ([(q, 2, pencil_forms(q), "pencil") for q in (2, 3, 4, 5, 7, 8, 9)] +
            [(2, 3, independent(3), "independent"), (3, 3, pencil_forms(3), "pencil"),
             (3, 3, independent(3), "independent"), (2, 4, independent(4), "independent"),
             (3, 3, [(1, 0, 0), (1, 1, 0), (1, 2, 0), (1, 0, 1), (1, 1, 1)], "mixed")])


def collect(large=False):
    records = []
    for q, m, forms, name in experiments(large):
        field = Field(q)
        row = census(q, m, forms)
        row["family"] = name
        check_expected(row, lambda mask: joint(field, [f for i, f in enumerate(forms)
                                                        if mask & (1 << i)], m))
        if name == "pencil":
            for mask in range(1 << len(forms)):
                actual = row["masks"].get(str(mask), 0)
                if row["headers"]*pattern(q, len(forms), mask.bit_count(), m) != actual:
                    raise ValueError("literal pencil mask vs inclusion-exclusion")
        records.append(row)
    return records


def main():
    large = sys.argv[1:] == ["--extended"]
    if sys.argv[1:] not in ([], ["--extended"]):
        raise ValueError("unknown check selection")
    result = collect(large)
    name = "GL4-ORDER3.json" if large else "LITERAL-GL.json"
    if json.loads(json.dumps(result)) != json.loads((HERE/name).read_text(encoding="utf8")):
        raise ValueError("frozen literal histogram or enumeration trace")
    print(json.dumps(dict(status="PASS_LITERAL_GUARD_HEADERS",fixture=name,
                          experiments=len(result), headers=sum(v["headers"] for v in result),
                          named_masks=sum(1 << len(v["forms"]) for v in result))))


if __name__ == "__main__":
    main()
