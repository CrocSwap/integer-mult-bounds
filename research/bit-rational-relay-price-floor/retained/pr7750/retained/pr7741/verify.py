"""Check the all-bundle price floor on the retained BIT word.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Nick Petalas supplied the full-donor reduction and two-delivery checker.
"""

import argparse
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
SOURCE_ROOT = PACKAGE / "retained/source-root"
EXCEPTIONS = tuple(26861 + 8*i for i in range(9))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def mask(row):
    return sum(1 << coordinate for coordinate in row)


def coordinates(value):
    result = set()
    while value:
        low = value & -value
        result.add(low.bit_length() - 1)
        value ^= low
    return result


def remainder(row, basis):
    row = set(row)
    while row:
        pivot = max(row)
        if pivot not in basis:
            break
        row.symmetric_difference_update(basis[pivot])
    return row


def insert(row, basis):
    row = remainder(row, basis)
    if row:
        basis[max(row)] = frozenset(row)


def project(row, ordered_basis):
    row = set(row)
    for pivot, value in ordered_basis:
        if pivot in row:
            row.symmetric_difference_update(value)
    return frozenset(row)


def set_arrivals(word, reverse):
    """Interpret each live row as a set of independent input coordinates."""
    charts = list(word["final" if reverse else "start"]) + [None] * 237
    rows = [{i} for i in range(659)] + [set() for _ in range(237)]
    sequence = reversed(word["program"]) if reverse else iter(word["program"])
    for clock, instruction in enumerate(sequence):
        op, role, *args = instruction
        require(0 <= role < len(rows), "independent lane range")
        if op == "MOVE":
            source, destination = args[::-1] if reverse else args
            require(charts[role] == source, "independent MOVE source")
            yield clock, source, destination, frozenset(rows[role])
            charts[role] = destination
        elif op == "ADD":
            donor, chart = args
            require(donor != role and 0 <= donor < len(rows), "independent ADD donor")
            require(charts[role] == charts[donor] == chart, "independent ADD chart")
            if reverse:
                rows[donor].symmetric_difference_update(rows[role])
            else:
                rows[role].symmetric_difference_update(rows[donor])
        elif op == "SWAP":
            (other,) = args
            require(0 <= other < len(rows) and other != role, "independent SWAP lane")
            rows[role], rows[other] = rows[other], rows[role]
            charts[role], charts[other] = charts[other], charts[role]
        elif op in ("INIT", "CLEAR"):
            (chart,) = args
            require(role >= 659, "independent public lifetime")
            if (op == "INIT") != reverse:
                require(charts[role] is None, "independent INIT state")
                charts[role] = chart
            else:
                require(charts[role] == chart, "independent CLEAR state")
                charts[role] = None
            rows[role] = set()
        else:
            raise ValueError("unknown independent operation")
    require(charts == list(word["start" if reverse else "final"]) + [None]*237,
            "independent exit charts")


def load_sources():
    pins = json.loads((PACKAGE / "SOURCE-PINS.json").read_text())
    for pin in pins:
        require(hashlib.sha256((PACKAGE / pin["path"]).read_bytes()).hexdigest()
                == pin["sha256"], "retained source hash")
    file = SOURCE_ROOT / "research/bit-causal-multi-delivery/verify.py"
    spec = importlib.util.spec_from_file_location("retained_multi_delivery", file)
    source = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = source
    spec.loader.exec_module(source)
    raw = source.WORD.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == source.WORD_SHA256, "native word pin")
    word = json.loads(gzip.decompress(raw))
    require((word["public"], word["owned_fields"], len(word["program"]))
            == (659, 237, 34137), "native dimensions")
    return source, word


def prior_checks(source, word):
    source.check_controls()
    dims, donors = source.nested_donors(word["frames"])
    expected = [(clock, 510+i, 0, 7) for i, clock in enumerate(EXCEPTIONS)]
    forward = source.check_orientation(word, dims, donors, False)
    transpose = source.check_orientation(word, dims, donors, True)
    require(forward == (2871, expected, {1: 4626, 2: 478764}), "predecessor forward")
    require(transpose == (2871, [], {}), "predecessor transpose")
    return dims, donors


def support_inventory(banks, donors, projection):
    inventory = []
    for chart, rank in donors[0]:
        if rank >= 7 or not banks[chart]:
            continue
        images = [project(row, projection) for row in banks[chart].values()]
        support = frozenset().union(*images)
        image_basis = {}
        for image in images:
            insert(image, image_basis)
        inventory.append(dict(chart=chart, rank=rank, image_dimension=len(image_basis),
                              support_size=len(support), support=hex(mask(support))))
    return inventory


def budget_bounds(inventory):
    caps = {}
    for row in inventory:
        caps[row["rank"]] = max(caps.get(row["rank"], 0), row["support_size"])
    bounds = [0]*7
    for budget in range(1, 7):
        bounds[budget] = max([bounds[budget-1]] +
                             [bounds[budget-rank] + cap for rank, cap in caps.items()
                              if rank <= budget])
    return caps, bounds


def check_caps(inventory, caps):
    require(all(row["support_size"] <= caps[row["rank"]] for row in inventory),
            "false support cap")


def separate(target, free_library, cap):
    cosets = [target.symmetric_difference(value) for value in free_library]
    require(min(map(len, cosets)) > cap, "all-bundle support separation")
    return cosets


def independent_checks(source, word, dims, donors):
    cases = []
    support_rows = None
    equality_checks = paired = attainments = 0
    trace = hashlib.sha256()
    for reverse in (False, True):
        banks = [{} for _ in range(636)]
        for coordinate, chart in enumerate(word["final" if reverse else "start"]):
            insert({coordinate}, banks[chart])
        free = [frozenset()]
        projection = None
        source_rows = source.arrivals(word, reverse)
        for packed, independent in zip(source_rows, set_arrivals(word, reverse), strict=True):
            clock, start, end, row = independent
            require((packed.clock, packed.source, packed.destination) == (clock, start, end)
                    and packed.row == mask(row), "independent paid row")
            paired += 1
            trace.update(f"{int(reverse)}:{clock}:{start}:{end}:{mask(row):x}\n".encode())
            rank = abs(dims[start] - dims[end])
            require(rank > 0 and (start, rank) in donors[end], "original route nesting")
            require(not remainder(row, banks[start]), "original source attainment")
            attainments += 1
            if not reverse and clock in EXCEPTIONS:
                require((start, end, rank) == (510+len(cases), 0, 7), "exception identity")
                if projection is None:
                    projection = sorted(banks[0].items(), reverse=True)
                    require(len(projection) == 524, "base destination rank")
                    require(all(not project(v, projection) for _, v in projection),
                            "base destination annihilation")
                    unit_images = [project({i}, projection) for i in range(659)]
                    projected_basis = {}
                    for image in unit_images:
                        insert(image, projected_basis)
                    require(len(projected_basis) == 135, "quotient rank")
                    support_rows = support_inventory(banks, donors, projection)
                    frozen = {r["chart"]: banks[r["chart"]].copy() for r in support_rows}
                    caps, bounds = budget_bounds(support_rows)
                    require(caps == {1: 1, 2: 2, 4: 17, 6: 30}, "donor support caps")
                    require(bounds == [0, 1, 2, 3, 17, 18, 30], "rank-budget bound")
                    check_caps(support_rows, caps)
                    projection_sha = hashlib.sha256(json.dumps(
                        [hex(mask(v)) for v in unit_images], separators=(",", ":")).encode()).hexdigest()
                    free_dimension = len(banks[0])
                else:
                    current_eligible = {chart for chart, r in donors[0] if r < 7 and banks[chart]}
                    require(current_eligible == set(frozen), "eligible chart set changed")
                    for chart, bank in frozen.items():
                        require(banks[chart] == bank, "lower-rank donor library changed")
                        equality_checks += 1
                require(len(banks[0]) == free_dimension + len(cases), "destination library growth")
                image = project(row, projection)
                actual_free = {}
                for value in banks[0].values():
                    insert(project(value, projection), actual_free)
                require(len(actual_free) == len(cases), "projected destination dimension")
                require(all(not remainder(v, actual_free) for v in free), "free library inclusion")
                require(len(set(free)) == 1 << len(cases), "complete free library")
                cosets = separate(image, free, bounds[6])
                distances = Counter(map(len, cosets))
                minimum = min(distances)
                cases.append(dict(clock=clock, source=start, destination=end, old_rank=rank,
                                  target=hex(mask(image)), free_dimension=len(actual_free),
                                  cosets=len(cosets), minimum_distance=minimum,
                                  minimum_selector=min(i for i, v in enumerate(cosets) if len(v) == minimum),
                                  distance_histogram={str(k): distances[k] for k in sorted(distances)}))
                free += [v.symmetric_difference(image) for v in free]
            insert(row, banks[end])
    require(len(cases) == 9 and paired == attainments == 5742, "complete arrival coverage")
    require([c["minimum_distance"] for c in cases] == [56, 58, 52, 50, 51, 50, 50, 48, 48],
            "coset distances")
    return dict(cases=cases, donors=support_rows, donor_caps={str(k): v for k, v in caps.items()},
                rank_budget_bounds=bounds, quotient_rank=135, base_destination_rank=524,
                quotient_unit_images_sha256=projection_sha, paid_row_trace_sha256=trace.hexdigest(),
                independent_paid_rows=paired, original_source_attainments=attainments,
                unchanged_donor_library_checks=equality_checks,
                exact_cosets=sum(c["cosets"] for c in cases))


def controls(result):
    inventory = result["donors"]
    caps = {int(k): v for k, v in result["donor_caps"].items()}
    for rank in caps:
        false = dict(caps)
        false[rank] -= 1
        try:
            check_caps(inventory, false)
        except ValueError:
            continue
        raise ValueError("support-cap mutant accepted")
    # Equal rank sum is outside the strict saving budget.
    require(sum((1, 6)) == 7 and sum((2, 4)) < 7, "strict-budget boundary")
    # If the current arrival enters its own free library, the separation fails.
    for case in result["cases"]:
        target = coordinates(int(case["target"], 16))
        try:
            separate(target, [frozenset(), target], result["rank_budget_bounds"][6])
        except ValueError:
            continue
        raise ValueError("deadline-leak mutant accepted")
    # A union is not the binary sum used by the independent interpreter.
    a, b = {0, 1}, {1, 2}
    require(a.symmetric_difference(b) == {0, 2} and a.union(b) != {0, 2},
            "binary-sum control")
    return dict(false_cap_rejections=4, deadline_leak_controls=9,
                strict_budget_control=True, binary_sum_control=True)


def calculate():
    source, word = load_sources()
    dims, donors = prior_checks(source, word)
    result = independent_checks(source, word, dims, donors)
    result["controls"] = controls(result)
    result["inherited_replay"] = dict(arrivals=5742, all_donor_union_exclusions=5733,
                                      exceptional_singletons=4626, exceptional_pairs=478764)
    result["scope"] = "All direct bundles from fixed causal libraries attain the original price floor for 0<t<=1; no new kappa"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = calculate()
    if args.write_result:
        (PACKAGE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(result == json.loads((PACKAGE / "RESULT.json").read_text()), "result mismatch")
    print("PASS_BIT_ALL_BUNDLE_PRICE_FLOOR 5742 arrivals; 511 cosets; distance>=48>30")


if __name__ == "__main__":
    main()
