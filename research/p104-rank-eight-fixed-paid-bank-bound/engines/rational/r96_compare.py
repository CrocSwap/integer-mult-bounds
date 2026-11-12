"""Authenticate and compare the primary and independent R96 exact dispositions."""
from argparse import ArgumentParser
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

PINS = {
    "primary": "362a879401158678c8a30ea0dbd4f919a9a0e907db2d2247ce96ac8724f68b14",
    "independent": "69c694a17e562a6e6534406e252428ca081f8e2ac6673ec01cf21e77cb468b58",
}


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("Duplicate JSON key")
    return result


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    for name in PINS:
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    data = {}
    for name, expected in PINS.items():
        raw = getattr(args, name).read_bytes()
        if sha256(raw).hexdigest() != expected:
            raise ValueError(f"Changed receipt {name}")
        data[name] = loads(raw, object_pairs_hook=unique)
    primary, independent = data["primary"], data["independent"]
    assert primary["head"] == independent["head"]
    assert primary["selected_unresolved"] == independent["selected_unvisited"] == []
    assert len(primary["results"]) == len(independent["results"]) == 4
    rows = []
    for p, i in zip(primary["results"], independent["results"], strict=True):
        assert all(p[field] == i[field] for field in ("key", "owned", "public", "pivots"))
        assert p["status"] == "no unit pairing" and i["status"] == "no_exact_unit_pair"
        assert p["pure_prefix_dimension"] == i["prefix_nullity"] == 1
        assert p["pure_suffix_dimension"] == i["suffix_nullity"] == 1
        assert p["nonzero_prefix_images"] == i["nonzero_prefix_basis_images"] == 1
        assert p["nonzero_suffix_images"] == i["nonzero_suffix_basis_images"] == 1
        rows.append(dict(key=p["key"], prefix_rank=i["prefix_rank"], suffix_rank=i["suffix_rank"],
                         prefix_nonzero_dimension=1, suffix_nonzero_dimension=1,
                         exact_unit_pair=False))
    assert len(primary["unselected"]) == independent["modular_dual_drops_outside_exact_scope"] + (
        independent["unvisited_modular_representatives"]) == 312
    print(dumps(dict(head=primary["head"], receipt_sha256=PINS, agree=True,
                     results=rows, outside_exact_scope=primary["unselected"]),
                indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
