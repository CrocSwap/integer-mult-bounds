"""Reevaluate primary full-axis minors using the sealed independent projections."""
from argparse import ArgumentParser
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
ENGINE = "21dbd96192e1f60c00ceddba01a7e8d0ddd7d6ad7da4ad3ed22ef2e47cc589c4"
SELECTION = "910c8881f31721793cb8e8cbf3b3b3789a9986415e0d48dd9c97d146d5b37bcc"


def checked(path, expected):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != expected:
        raise ValueError("changed input " + path.name)
    return raw


def main():
    parser = ArgumentParser()
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--primary-sha256", required=True)
    parser.add_argument("--independent", type=Path, default=ROOT / "RESULT.json")
    parser.add_argument("--independent-sha256", required=True)
    args = parser.parse_args()
    assert __debug__
    primary = loads(checked(args.primary, args.primary_sha256))
    independent = loads(checked(args.independent, args.independent_sha256))
    path = ROOT / "inputs/second_prime.py"
    checked(path, ENGINE)
    engine = run_path(str(path))
    assert independent["prime"] == engine["PRIME"] == 65537
    assert primary["head"] == independent["head"]
    assert primary["pins"]["SELECTION.json"] == independent["pins"]["inputs/SELECTION.json"] == SELECTION
    by_key = {tuple(row["key"][:2]): row for row in primary["results"]}
    assert len(by_key) == len(primary["results"]) == 17
    assert len({tuple(row["key"]) for row in independent["rows"]}) == len(independent["rows"]) <= 17
    results = []
    for row in independent["rows"]:
        item = by_key[tuple(row["key"])]
        receipt = item["prefix"]
        for field in ("public", "owned", "pivots"):
            assert row[field] == item[field]
            if receipt is not None:
                assert row[field] == receipt[field]
        n = len(row["public"])
        if receipt is not None:
            assert receipt["exterior_rank"] <= n
        primary_full = None if receipt is None else receipt["exterior_rank"] == n
        second_full = row["disposition"] == "prefix exclusion"
        columns = None if receipt is None else receipt["columns"]
        determinant = None
        if primary_full:
            assert receipt["determinant"] and len(set(columns)) == len(columns) == n
            assert set(columns).isdisjoint(independent["cohort"])
            projected = [{int(col): val for col, val in vector.items()} for vector in row["exterior_rows"]]
            determinant = engine["verify_minor"](projected, columns)
        results.append(dict(key=row["key"], primary_full=primary_full, independent_full=second_full,
            axes=columns, primary_det=None if receipt is None else receipt["determinant"],
            primary_det_mod_65537=determinant))
    print(dumps(dict(prime=65537, primary_sha256=args.primary_sha256, independent_sha256=args.independent_sha256,
        banks=len(results), same_full_rank_disposition=sum(r["primary_full"] == r["independent_full"] for r in results),
        primary_nonzero_axes_at_second_prime=sum(bool(r["primary_det_mod_65537"]) for r in results),
        unresolved_at_second_prime=independent["unresolved"],
        primary_unvisited=[row["key"] for row in primary["results"] if row["prefix"] is None],
        results=results),
        indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
