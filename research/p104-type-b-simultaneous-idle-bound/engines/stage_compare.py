"""Reconcile every R124 stage/cardinality and every missing-stage certificate."""
from argparse import ArgumentParser
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

PINS = {
    "lead/RESULT.json": "01f4a0ff68b3a9428a82920a55751ccec7f5cf628cd2d9bd02bebbcaa6bbbde3",
    "independent/RESULT.json": "5bf41ba41b70ee549526289d5e38a3987515dd387ef142a77d80a557a269e2a7",
}


def read(root, rel):
    raw = (root / rel).read_bytes()
    if sha256(raw).hexdigest() != PINS[rel]:
        raise ValueError(f"changed dependency {rel}")
    return loads(raw)


def main():
    parser = ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    lead, independent = (read(args.root, rel) for rel in PINS)
    for key in ("head", "caller", "q", "body", "literal_events", "comparisons", "exact_match_count",
                "eliminations", "remaining_even_sites", "unvisited_stages", "timeout"):
        assert lead[key] == independent[key], key
    assert lead["comparisons"] == 18443 and independent["compatible_comparisons"] == 4527
    assert lead["exact_match_count"] == 0 and lead["timeout"] is None
    assert lead["unvisited_stages"] == lead["remaining_even_sites"] == []
    assert len(lead["eliminations"]) == 1 and len(lead["eliminations"][0]) == 60
    for left, right in zip(lead["stages"], independent["stages"], strict=True):
        assert left["stage"] == right["stage"] and left["matches"] == right["matches"] == []
        for a, b in zip(left["cardinalities"], right["cardinalities"], strict=True):
            for key in ("k", "odd_subsets", "even_subsets", "comparisons", "exact_sums"):
                assert a[key] == b[key], (left["stage"], key)
            assert a["modular_collisions"] == b["rational_scalar_equal"] == 0
    result = dict(pins=PINS, stages=len(lead["stages"]), stage_cardinality_rows=68,
                  comparisons=18443, fully_mask_compatible=4527, exact_matches=0,
                  missing_stage_certificates=60, unvisited_stages=[])
    print(dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
