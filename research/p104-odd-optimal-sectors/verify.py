"""Check the odd-width integer relaxation, without running predecessor code."""

import hashlib
import json
from pathlib import Path


MAX_Q = 15
PACKAGE_FILES = (
    "PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(q: int, inventory: tuple[int, ...]) -> None:
    require(type(q) is int and 1 <= q <= MAX_Q and q % 2 == 1,
            "fixture width must be odd and in [1, 15]")
    require(type(inventory) is tuple and len(inventory) == 6,
            "inventory must have six coordinates")
    require(all(type(v) is int and v >= 0 for v in inventory),
            "inventory coordinates must be nonnegative integers")


def relaxation(q: int, inventory: tuple[int, ...]) -> bool:
    validate(q, inventory)
    x, y, z, h, j, w = inventory
    common = x + z - (2 * q - y)
    return (
        x + y + z + h + j + w == 4 * q
        and 2 * (x + y + z) + 3 * (h + j) + 4 * w == (21 * q + 1) // 2
        and w >= q
        and x + z <= 2 * q
        and x >= 2 * common
        and z >= 2 * common
        and x + h + w >= 2 * q
        and z + j + w >= 2 * q
    )


def enumerate_relaxation(q: int) -> tuple[set[tuple[int, ...]], int]:
    """Enumerate all x,y,z; the two equalities determine w and h+j."""
    validate(q, (0,) * 6)
    found = set()
    candidates = 0
    target = (21 * q + 1) // 2
    for x in range(4 * q + 1):
        for y in range(4 * q + 1):
            for z in range(4 * q + 1):
                candidates += 1
                total_pairs = x + y + z
                w = target - 12 * q + total_pairs
                triples = 4 * q - total_pairs - w
                if w < q or triples < 0:
                    continue
                for h in range(triples + 1):
                    inventory = (x, y, z, h, triples - h, w)
                    if relaxation(q, inventory):
                        found.add(inventory)
    return found, candidates


def six_forms(q: int) -> set[tuple[int, ...]]:
    validate(q, (0,) * 6)
    k = (q - 1) // 2
    found = set()
    for a in range(3):
        for b in range(3 - a):
            lower_h = max(0, 1 - a)
            upper_h = k + 1 - max(0, 1 - b)
            for h in range(lower_h, upper_h + 1):
                found.add((2 * k + a, k + 2 - a - b, 2 * k + b,
                           h, k + 1 - h, q))
    return found


def check_consequences(q: int, inventory: tuple[int, ...]) -> None:
    x, y, z, h, j, w = inventory
    ranks = (x + h + w, 4 * q - z, 4 * q - x, z + j + w)
    require(w == q, "common endpoint sector exceeds q")
    require(h + j == (q + 1) // 2, "wrong triple-sector mass")
    require(x + y + z == (5 * q - 1) // 2, "wrong pair-sector mass")
    require(all(3 * q - 1 <= r <= 3 * q + 1 for r in ranks[1:3]),
            "odd-stage rank escaped its three values")
    require(abs(ranks[1] - ranks[2]) <= 2, "odd-stage rank imbalance exceeds two")
    require(sum(ranks) == (21 * q + 1) // 2, "wrong total stage rank")
    require(ranks[0] >= 2 * q and ranks[3] >= 2 * q, "endpoint support lost")


def check_controls() -> dict[str, int]:
    positive = (3, 1, 3, 1, 1, 3)
    require(relaxation(3, positive), "positive width-three fixture rejected")
    invalid = ((0, positive), (2, positive), (True, positive), (17, positive),
               (3, (1, 2)), (3, (-1, 1, 3, 1, 1, 3)),
               (3, (True, 1, 3, 1, 1, 3)))
    rejected = 0
    for q, inventory in invalid:
        try:
            validate(q, inventory)
        except ValueError:
            rejected += 1
    require(rejected == len(invalid), "invalid input accepted")
    mutants = ((3, 1, 3, 1, 1, 4), (2, 1, 3, 1, 1, 3),
               (3, 2, 3, 1, 1, 3), (3, 1, 3, 0, 1, 3))
    for inventory in mutants:
        require(not relaxation(3, inventory), "changed inventory accepted")
    inequality_controls = (
        (2, 2, 2, 2, 2, 2),  # w>=q
        (3, 0, 4, 2, 0, 3),  # x+z<=2q
        (1, 3, 3, 2, 0, 3),  # individual x image bound
        (3, 3, 1, 0, 2, 3),  # individual z image bound
    )
    for inventory in inequality_controls:
        require(not relaxation(3, inventory), "rank-inequality control accepted")
    # This tuple satisfies every displayed inequality except endpoint A support.
    support_counterexample = (0, 1, 1, 0, 1, 1)
    require(not relaxation(1, support_counterexample), "missing endpoint support")
    require(support_counterexample not in six_forms(1), "endpoint filter absent")
    return {"invalid_inputs": rejected, "changed_inventories": len(mutants),
            "rank_inequality_controls": len(inequality_controls),
            "endpoint_support_control": 1}


def source_hashes() -> dict[str, str]:
    root = Path(__file__).resolve().parent
    hashes = {}
    for name in PACKAGE_FILES:
        with (root / name).open("rb") as source:
            data = source.read(1024 * 1024 + 1)
        require(len(data) <= 1024 * 1024, "package file exceeds one MiB")
        hashes[name] = hashlib.sha256(data).hexdigest()
    return hashes


def main() -> None:
    records = []
    for q in range(1, MAX_Q + 1, 2):
        actual, candidates = enumerate_relaxation(q)
        expected = six_forms(q)
        require(actual == expected, f"six-form enumeration mismatch at q={q}")
        require(len(actual) == 3 * (q + 1), f"inventory count mismatch at q={q}")
        for inventory in sorted(actual):
            check_consequences(q, inventory)
        records.append({"q": q, "candidate_triples": candidates,
                        "relaxation_inventories": len(actual)})
    controls = check_controls()
    print("PASS_ODD_OPTIMAL_SECTOR_REDUCTION")
    print(json.dumps({"scope": "finite integer relaxation, not word attainability",
                      "records": records, "controls": controls,
                      "package_sha256": source_hashes()}, sort_keys=True))


if __name__ == "__main__":
    main()
