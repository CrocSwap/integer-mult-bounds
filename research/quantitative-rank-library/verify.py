"""Bounded independent literal-word oracle and negative controls; stdlib only."""
from collections import Counter
from dataclasses import asdict
from fractions import Fraction
from hashlib import sha1, sha256
from itertools import product
import json
from math import gcd, prod
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import library as subject


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate_sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for entry in manifest["sources"]:
        data = (HERE / entry["local"]).read_bytes()
        require(len(data) == entry["bytes"], "source length: " + entry["local"])
        require(sha256(data).hexdigest() == entry["sha256"],
                "source SHA256: " + entry["local"])
        blob = sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == entry["git_blob"], "source Git blob: " + entry["local"])
    return len(manifest["sources"])


def rejects(label, operation):
    try:
        operation()
    except (ValueError, IndexError):
        return label
    raise ValueError("control failed to reject: " + label)


def literal_flow(rule, n):
    """Explicit paths/role words and literal incoming slot edges; no DP."""
    roles = tuple(k for k, count in rule.targets for _ in range(count))
    sites = tuple(r for r, count in rule.paid for _ in range(count))
    g = 0
    while rule.m * rule.kmin ** (g + 1) <= n:
        g += 1
    require(g <= 5 and len(roles) <= 8 and len(sites) <= 8,
            "literal oracle domain")
    units = []
    targets = {}
    incoming = set()
    exits = []
    for h in range(g + 1):
        for path in product(range(len(sites)), repeat=h):
            rho = prod(sites[j] for j in path)
            for word in product(range(len(roles)), repeat=g - h):
                column = prod(roles[i] for i in word)
                if rule.m * rho * column > n:
                    continue
                units.append((path, word))
                for role, rank in enumerate(roles):
                    key = (path, word, role)
                    require(key not in targets, "duplicate target identity")
                    targets[key] = rho * column * rank
                for site, rank in enumerate(sites):
                    if word:
                        destination = (path + (site,), word[1:], word[0])
                        require(destination not in incoming, "duplicate incoming edge")
                        incoming.add(destination)
                    else:
                        exits.append((path, site, rho * rank))
    require(incoming <= targets.keys(), "incoming target missing")
    sources = Counter(rank for key, rank in targets.items() if key not in incoming)
    return g, len(units), sources, exits


def factor_small(value):
    """Independent trial-division valuation oracle, bounded to tiny fixtures."""
    require(0 < value and value.bit_length() <= 4096, "factor oracle domain")
    result = {}
    trial = 2
    while trial * trial <= value:
        require(trial <= 2000000, "factor oracle work cap")
        exponent = 0
        while value % trial == 0:
            value //= trial
            exponent += 1
        if exponent:
            result[trial] = exponent
        trial += 1
    if value > 1:
        result[value] = 1
    return result


def literal_library(rule, maximum):
    """Prime deficits plus normalized Fractions, not author batch copies."""
    widths = [None]
    leaves = [None]
    units = [None]
    result = [None]
    literal_units = literal_cuts = sources_seen = 0
    for n in range(1, maximum + 1):
        if n < rule.m:
            width, scale, leaf_ratio, unit_ratio = 1, 1, Fraction(n), Fraction(0)
        else:
            _, local, sources, exits = literal_flow(rule, n)
            literal_units += local
            literal_cuts += len(exits)
            sources_seen += sum(sources.values())
            constraints = [(n - s, count) for s, count in sources.items() if s < n]
            constraints += [(e, 1) for _, _, e in exits]
            needs = {}
            for child, count in constraints:
                require(1 <= child < n, "literal child descent")
                for prime, exponent in factor_small(widths[child]).items():
                    available = 0
                    divided = count
                    while divided % prime == 0:
                        divided //= prime
                        available += 1
                    needs[prime] = max(needs.get(prime, 0), exponent - available, 0)
            scale = prod(prime ** exponent for prime, exponent in needs.items())
            total = sum(sources.values())
            width = scale * total
            leaf_ratio = sum((Fraction(count, total) * leaves[n - s]
                              for s, count in sources.items() if s < n), Fraction(0))
            leaf_ratio += sum((leaves[e] / total for _, _, e in exits), Fraction(0))
            unit_ratio = Fraction(local, total)
            unit_ratio += sum((Fraction(count, total) * units[n - s]
                               for s, count in sources.items() if s < n), Fraction(0))
            unit_ratio += sum((units[e] / total for _, _, e in exits), Fraction(0))
        require((width * leaf_ratio).denominator == 1, "literal paid integral")
        require((width * unit_ratio).denominator == 1, "literal units integral")
        widths.append(width)
        leaves.append(leaf_ratio)
        units.append(unit_ratio)
        result.append(subject.Row(scale, width, int(width * leaf_ratio), int(width * unit_ratio)))
    return tuple(result), (literal_units, literal_cuts, sources_seen)


def mutant(old, new, name):
    source = (HERE / "library.py").read_text()
    require(source.count(old) == 1, "mutation anchor: " + name)
    module = types.ModuleType("mutant_" + name)
    sys.modules[module.__name__] = module
    exec(compile(source.replace(old, new), str(HERE / "library.py"), "exec"), module.__dict__)
    return module


def different_or_reject(module, rule, maximum, expected):
    try:
        rows = module.compile_library(rule, maximum).rows
    except (ValueError, IndexError):
        return
    actual = [None if x is None else asdict(x) for x in rows]
    require(actual != [None if x is None else asdict(x) for x in expected],
            "semantic mutant escaped")


def check_case(rule, maximum):
    actual = subject.compile_library(rule, maximum)
    expected, counts = literal_library(rule, maximum)
    require(actual.rows == expected, "literal complete library mismatch")
    work = subject.Work()
    degree = subject.height(rule, maximum)
    targets = subject.product_tables(rule.targets, degree, subject.Limits(), work)
    paid = subject.product_tables(rule.paid, degree + 1, subject.Limits(), work)
    for n in range(rule.m, maximum + 1):
        g, units, sources, exits = literal_flow(rule, n)
        flow = subject.census(rule, n, targets, paid, subject.Limits(), work)
        require((flow.height, flow.units, flow.sources, flow.exits) ==
                (g, units, tuple(sorted(sources.items())),
                 tuple(sorted(Counter(e for _, _, e in exits).items()))),
                "literal source/exit census mismatch")
    bounds = subject.envelope(rule, maximum)
    for row in actual.rows[1:]:
        require(row.width.bit_length() <= bounds["width_log_bound"] + 1,
                "width envelope")
        require((row.width + row.leaves + row.units).bit_length() <=
                bounds["combined_output_bits"], "combined count envelope")
        require(max(x.bit_length() for x in asdict(row).values()) <= bounds["Z"],
                "common bit cap")
    return actual, counts


def main():
    source_count = authenticate_sources()
    fixtures = [
        (subject.Rule(((2, 1),), ((1, 1),)), 32),
        (subject.Rule(((2, 2),), ((1, 5),)), 40),
        (subject.Rule(((2, 1), (3, 1)), ((1, 2),)), 48),
        (subject.Rule(((3, 2), (5, 1)), ((2, 2),)), 135),
        (subject.Rule(((4, 1), (6, 1)), ((1, 2), (2, 1), (3, 1))), 48),
        (subject.Rule(((2, 1), (4, 1), (8, 1)), ((1, 3),)), 128),
        (subject.Rule(((3, 1), (9, 1)), ((1, 1), (2, 2))), 60),
        (subject.Rule(((5, 3),), ((1, 2), (2, 1), (4, 1))), 30),
    ]
    for m in (2, 3, 4):
        for w in (1, 2, 3):
            for p in (1, 2, 3):
                fixtures.append((subject.Rule(((m, w),), ((1, p),)), 20))
    totals = [0, 0, 0]
    completed = 0
    negative_surplus = 0
    for rule, maximum in fixtures:
        _, counts = check_case(rule, maximum)
        completed += maximum
        totals = [a + b for a, b in zip(totals, counts)]
        if sum(k * w for k, w in rule.targets) < sum(r * p for r, p in rule.paid):
            negative_surplus += 1

    # Complementary peer supplied this strict-separation cut-pooling witness.
    cut_rule = subject.Rule(((3, 2), (5, 1)), ((2, 2),))
    cut_library = subject.compile_library(cut_rule, 135)
    work = subject.Work()
    target = subject.product_tables(cut_rule.targets, 3, subject.Limits(), work)
    paid = subject.product_tables(cut_rule.paid, 4, subject.Limits(), work)
    cut_flow = subject.census(cut_rule, 135, target, paid, subject.Limits(), work)
    require(cut_flow.sources == ((60, 16), (81, 16), (90, 8), (100, 4), (135, 8)),
            "peer control sources")
    require(cut_flow.exits == ((16, 16),), "peer control separate exits")
    pooled = 1
    bad_batches = [(135 - s, count) for s, count in cut_flow.sources if s < 135]
    bad_batches += list(cut_flow.exits)
    for rank, count in bad_batches:
        width = cut_library.rows[rank].width
        factor = width // gcd(width, count)
        pooled = pooled // gcd(pooled, factor) * factor
    require((cut_library.rows[16].width, cut_library.rows[135].replication,
             pooled, pooled % cut_library.rows[16].width) ==
            (24, 12509640, 1563705, 9), "peer cut-pooling values")
    controls = [rejects("pooled-exit-divisor", lambda: subject.finish_row(
        cut_flow, cut_library.rows[:135], pooled, subject.Limits()))]

    tiny = subject.Rule(((2, 1), (3, 1)), ((1, 2),))
    for label, operation in [
        ("rank-zero-child", lambda: subject.child(cut_library.rows, 135, 0)),
        ("not-smaller-child", lambda: subject.child(cut_library.rows, 135, 135)),
        ("duplicate-rank", lambda: subject.Rule(((2, 1), (2, 2)), ((1, 1),))),
        ("zero-multiplicity", lambda: subject.Rule(((2, 0),), ((1, 1),))),
        ("unseparated", lambda: subject.Rule(((2, 1),), ((2, 1),))),
        ("nonpositive-maximum", lambda: subject.compile_library(tiny, 0)),
        ("rank-capacity", lambda: subject.compile_library(tiny, 50, subject.Limits(max_rank=49))),
        ("record-capacity", lambda: subject.compile_library(tiny, 50, subject.Limits(max_records=3))),
        ("bit-capacity", lambda: subject.compile_library(tiny, 50, subject.Limits(max_bits=3))),
    ]:
        controls.append(rejects(label, operation))

    expected = subject.compile_library(tiny, 24).rows
    changes = [
        ("value = limits.integer(value + next_value)",
         "value = limits.integer(next_value)", "product-overwrite"),
        ("if depth < gmax:", "if False:", "missing-incoming-subtraction"),
        ("if limits.integer(rule.m * size) > rank:",
         "if limits.integer(rule.m * size) >= rank:", "fit-equality"),
        ("units = limits.integer(scale * flow.units)",
         "units = 0", "missing-outer-units"),
        ("limits.integer(count * multiplicity)))",
         "limits.integer(count)))", "merged-native-occurrences"),
    ]
    for old, new, name in changes:
        different_or_reject(mutant(old, new, name), tiny, 24, expected)
        controls.append(name)

    # This profile has negative rank surplus and hundreds of millions of
    # paid-path labels, none of which the tested evaluator materializes.
    large_rule = subject.Rule(((2, 2), (3, 1)), ((1, 9),))
    large = subject.compile_library(large_rule, 2048)
    bounds = subject.envelope(large_rule, 2048)
    bound_ratio = large_rule.m * bounds["F"] ** bounds["D"]
    for row in large.rows[1:]:
        require(row.width + row.leaves + row.units <= row.width * bound_ratio,
                "large normalized count envelope")
        require(row.width.bit_length() <= bounds["width_log_bound"] + 1,
                "large width envelope")
    row_packet = "\n".join(",".join(format(x, "x") for x in asdict(row).values())
                           for row in large.rows[1:]).encode()
    homogeneous = subject.compile_library(subject.Rule(((2, 2),), ((1, 5),)), 1023)
    for n, row in enumerate(homogeneous.rows[1:], 1):
        require(row.width == 2 ** (n.bit_length() - 1), "credited homogeneous width")

    result = {
        "status": "PASS_QUANTITATIVE_RANK_LIBRARY",
        "scope": "exact formal metadata, no native word, no new kappa",
        "authenticated_inert_sources": source_count,
        "literal_fixtures": len(fixtures), "literal_library_rows": completed,
        "literal_units": totals[0], "literal_cuts": totals[1],
        "literal_sources": totals[2], "negative_surplus_fixtures": negative_surplus,
        "controls": controls,
        "exit_pooling_control": {"rank": 135, "child_width": 24, "cuts": 16,
                                  "correct_replication": 12509640,
                                  "pooled_replication": pooled, "residue": 9},
        "large": {"rows": 2048, "height": bounds["height"],
                  "unexpanded_paid_paths_at_max_height": 9 ** bounds["height"],
                  "table_sha256": sha256(row_packet).hexdigest(),
                  "max_output_bits": max(max(x.bit_length() for x in asdict(row).values())
                                         for row in large.rows[1:]),
                  "work": asdict(large.work), "envelope": bounds},
        "credited_homogeneous_rows": 1023,
        "core_sha256": {name: sha256((HERE / name).read_bytes()).hexdigest()
                        for name in ("library.py", "PROOF.md", "verify.py")},
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
