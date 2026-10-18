#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared for Ali Romman with substantial OpenAI Codex assistance.
"""Check the exact bound for a fixed catalogue and a shared owner pool."""

import argparse
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import subprocess
import sys


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = "8bddbee377e2f3ce1f1247196c4b290d55767d20"
WIDTHS = (4, 5, 7, 8, 9)
PRICES = (-1, -20, -8, -2, 4)
BONUSES = {8: 2, 16: 4, 32: 8, 48: -13}
SOURCE_PATTERN = "*/data/SPEC*.json"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decimal(value):
    with localcontext() as context:
        context.prec = 40
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def histogram(value):
    need(isinstance(value, dict) and value, "empty histogram")
    need(all(str(int(r)) == r and int(r) > 0 and type(n) is int and n > 0
             for r, n in value.items()), "invalid histogram")
    return {int(r): n for r, n in value.items()}


def read_catalogue_sources(root, source_paths):
    """Read each registered source in the declared file scope."""
    sources, records, interfaces, index = {}, [], [], {}
    for relative in sorted(source_paths, key=Path):
        path = root / relative
        source = read(path)
        providers = source.get("providers", {})
        need(isinstance(providers, dict) and providers, "source has no providers: " + relative)
        sources[relative] = sha(path)
        for name, provider in sorted(providers.items()):
            inventory = histogram(provider["inventory"])
            profile = histogram(provider["expected_profile"])
            need(set(inventory) <= set(WIDTHS), "unpriced helper width: " + relative)
            need(max(profile) < 73, "improper local child: " + relative)
            need(sum(r * n for r, n in profile.items()) -
                 sum(w * n for w, n in inventory.items()) == 1856,
                 "changed per-call mass contract: " + relative)
            contract = provider.get("complete_contract")
            if contract:
                need((contract["v"], contract["h"]) == (112, 9), "changed local dimensions")
                need(Counter(contract["widths"]) == inventory, "contract width mismatch")
                need(histogram(contract["paid_profile"]) == profile, "contract profile mismatch")
            key = (tuple(sorted(inventory.items())), tuple(sorted(profile.items())))
            if key not in index:
                label = "P%02d" % (len(interfaces) + 1)
                index[key] = label
                interfaces.append(dict(id=label, inventory=inventory, profile=profile))
            records.append(dict(source=relative, provider=name, interface=index[key]))
    need(sources, "empty source scope")
    return dict(base=BASE, source_pattern="research/" + SOURCE_PATTERN,
                sources=sources, records=records, interfaces=interfaces)


def audit_current_tree(root, frozen):
    """Report source additions. Do not extend the proved catalogue."""
    paths = sorted((root / "research").glob(SOURCE_PATTERN))
    current_sources = {path.relative_to(root).as_posix(): sha(path) for path in paths}
    current_records = {(path.relative_to(root).as_posix(), name)
                       for path in paths for name in read(path).get("providers", {})}
    old_records = {(row["source"], row["provider"]) for row in frozen["records"]}
    added = sorted(current_records - old_records)
    return dict(status="ADDITIONAL_RECORDS_OUTSIDE_BOUND" if added else "NO_ADDITIONAL_RECORDS",
                additional_sources=sorted(set(current_sources) - set(frozen["sources"])),
                additional_records=[dict(source=p, provider=n) for p, n in added],
                missing_sources=sorted(set(frozen["sources"]) - set(current_sources)),
                changed_sources=sorted(p for p, digest in frozen["sources"].items()
                                       if p in current_sources and current_sources[p] != digest),
                scope="New records are not covered by the frozen base-catalogue theorem.")


def audit_base_tree(root, frozen):
    """Compare the frozen registry with the complete pinned Git tree."""
    def git(*args):
        return subprocess.run(["git", "-C", str(root), *args], check=True,
                              capture_output=True).stdout

    names = git("ls-tree", "-r", "--name-only", BASE, "research").decode("utf-8").splitlines()
    paths = []
    for name in names:
        parts = Path(name).parts
        if (len(parts) == 4 and parts[0] == "research" and parts[2] == "data"
                and parts[3].startswith("SPEC") and parts[3].endswith(".json")):
            paths.append(name)
    need(set(paths) == set(frozen["sources"]), "base tree source coverage mismatch")
    records = set()
    for path in paths:
        data = git("show", BASE + ":" + path)
        need(hashlib.sha256(data).hexdigest() == frozen["sources"][path],
             "base tree source hash mismatch: " + path)
        records.update((path, name) for name in json.loads(data)["providers"])
    need(records == {(row["source"], row["provider"]) for row in frozen["records"]},
         "base tree provider coverage mismatch")
    return dict(status="PASS_COMPLETE_BASE_TREE_COVERAGE", base=BASE,
                source_pattern=frozen["source_pattern"], sources=len(paths), records=len(records))


def validate_catalogue(frozen, actual):
    need(frozen["base"] == BASE and frozen["source_pattern"] == actual["source_pattern"],
         "catalogue scope mismatch")
    need(frozen["sources"] == actual["sources"], "catalogue source set or hash mismatch")
    need(frozen["records"] == actual["records"], "catalogue record coverage mismatch")
    # JSON uses strings for the integer keys in both inputs.
    normalized = json.loads(json.dumps(actual["interfaces"]))
    need(frozen["interfaces"] == normalized, "catalogue cost interface mismatch")


def add_form(form, other, factor=Q(1)):
    for rank, coefficient in other.items():
        form[rank] = form.get(rank, Q(0)) + factor * coefficient
        if not form[rank]:
            del form[rank]
    return form


def interval(form, values):
    lower = upper = Q(0)
    for rank, coefficient in form.items():
        lo, hi = values[rank]
        if coefficient < 0:
            lo, hi = hi, lo
        lower += coefficient * lo
        upper += coefficient * hi
    return lower, upper


def cost_forms():
    # Each form is a rational linear combination of phi(r).
    multiplier = {1: Q(48, 925), 48: Q(-1, 925)}
    slope = add_form({48: Q(1, 48)}, multiplier, Q(13, 48))
    return slope, multiplier


def reduced_form(provider, baseline):
    slope, multiplier = cost_forms()
    form = {int(r): Q(n) for r, n in provider["profile"].items()}
    add_form(form, {int(r): Q(n) for r, n in baseline["profile"].items()}, Q(-1))
    width_delta = sum(int(w) * n for w, n in provider["inventory"].items()) - \
        sum(int(w) * n for w, n in baseline["inventory"].items())
    price = dict(zip(WIDTHS, PRICES))
    credit_delta = sum(price[int(w)] * n for w, n in provider["inventory"].items()) - \
        sum(price[int(w)] * n for w, n in baseline["inventory"].items())
    add_form(form, slope, -width_delta)
    add_form(form, multiplier, credit_delta)
    return form


def bin_patterns():
    for capacity, bonus in BONUSES.items():
        for counts in itertools.product(*(range(capacity // w + 1) for w in WIDTHS)):
            used = sum(w * n for w, n in zip(WIDTHS, counts))
            if used <= capacity:
                yield capacity, capacity - used, bonus + sum(p * n for p, n in zip(PRICES, counts)), counts


def fill_recurrence():
    """Compute all maximum weights without the pattern enumeration."""
    best = {0: 0}
    for used in range(1, 49):
        choices = [best[used - w] + p for w, p in zip(WIDTHS, PRICES) if used - w in best]
        if choices:
            best[used] = max(choices)
    return {(capacity, capacity - used): bonus + score
            for capacity, bonus in BONUSES.items()
            for used, score in best.items() if used <= capacity}


def bin_form(rank, price):
    slope, multiplier = cost_forms()
    form = {rank: Q(1)} if rank else {}
    add_form(form, slope, -rank)
    add_form(form, multiplier, -price)
    return form


def certify_bins(values):
    maxima, count, strict, equalities = {}, 0, [], Counter()
    for capacity, rank, price, counts in bin_patterns():
        count += 1
        maxima[capacity, rank] = max(maxima.get((capacity, rank), price), price)
        form = bin_form(rank, price)
        need(sum(r * q for r, q in form.items()) == 0, "bin dual is not zero at b=0")
        if not form:
            equalities[rank] += 1
        else:
            bounds = interval(form, values)
            need(bounds[0] > 0, "bin support fails: " + str((capacity, counts)))
            strict.append(bounds[0])
    need(maxima == fill_recurrence(), "bin enumeration and fill recurrence disagree")
    need(count == 1163, "bin pattern coverage mismatch")
    need(set(equalities) == {0, 1, 48}, "unexpected support equality")
    rows = [dict(capacity=c, remainder=r, maximum_signed_price=p,
                 lower_margin=str(interval(bin_form(r, p), values)[0]))
            for (c, r), p in sorted(maxima.items())]
    return dict(patterns=count, maximum_cases=len(rows), equality_patterns=dict(equalities),
                minimum_strict_pattern_margin=str(min(strict)), cases=rows)


def certify_providers(interfaces, baseline, values):
    rows = []
    for provider in interfaces:
        form = reduced_form(provider, baseline)
        need(sum(r * q for r, q in form.items()) == 0, "provider penalty is not zero at b=0")
        lower, upper = interval(form, values)
        if provider["id"] == baseline["id"]:
            need(not form, "baseline reduced cost is not zero")
        else:
            need(lower > 0, "favorable or unresolved provider: " + provider["id"])
        rows.append(dict(id=provider["id"], lower=str(lower), upper=str(upper),
                         lower_decimal=decimal(lower),
                         form={r: str(q) for r, q in sorted(form.items())}))
    return rows


def load_engine(root, path, name):
    spec = importlib.util.spec_from_file_location(name, root / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def phi_values(engine, kind, lo, hi, ranks):
    values = {}
    for rank in sorted(ranks):
        if kind == "mercator":
            a, b = engine.logarithm(Q(73, rank))
            x, y = engine.exponential(lo * a, hi * b)
        else:
            a, b = engine.log_bounds(Q(73, rank))
            x, y = engine.exp_bounds(lo * a)[0], engine.exp_bounds(hi * b)[1]
        values[rank] = rank * x, rank * y
    return values


def derivative_values(engine, kind, right, ranks):
    values = {}
    for rank in sorted(ranks):
        if kind == "mercator":
            lo, hi = engine.logarithm(Q(73, rank))
            exp_upper = engine.exponential(Q(0), right * hi)[1]
        else:
            lo, hi = engine.log_bounds(Q(73, rank))
            exp_upper = engine.exp_bounds(right * hi)[1]
        values[rank] = rank * lo, rank * hi * exp_upper
    return values


def verify():
    need(not sys.flags.optimize, "retained outer arithmetic requires assertions")
    root = ROOT
    frozen = read(PACKAGE / "CATALOGUE.json")
    pins = read(PACKAGE / "DEPENDENCIES.json")
    need(sha(PACKAGE / "CATALOGUE.json") == pins["catalogue_sha256"], "frozen catalogue hash mismatch")
    validate_catalogue(frozen, read_catalogue_sources(root, frozen["sources"]))
    for path, digest in pins["sha256"].items():
        need(sha(root / path) == digest, "dependency source drift: " + path)
    paths = pins["roles"]
    need(set(paths.values()) <= set(pins["sha256"]), "unpinned arithmetic dependency")
    claim = read(root / paths["selected_claim"])
    plan = read(root / paths["capacity_plan"])
    bit = read(root / paths["bit_claim"])
    M = load_engine(root, paths["mercator"], "mixed_mercator")
    B = load_engine(root, paths["atanh"], "mixed_atanh")
    A = load_engine(root, paths["outer"], "mixed_outer")
    O = load_engine(root, paths["outer_driver"], "mixed_outer_driver")
    lower = Q(claim["complex_lower"])
    upper = lower + Q(1, 10**24)
    baseline_record = next(row for row in frozen["records"]
                           if row["source"] == "research/complex-t21-owners/data/SPEC.json"
                           and row["provider"] == "gauge44")
    baseline = next(row for row in frozen["interfaces"] if row["id"] == baseline_record["interface"])
    stock = plan["live"] // plan["T"]
    ports = len(next(iter(plan["provider_registry"].values()))["ports"])
    counts = Counter(cap for cap, _ in plan["windows"].values())
    capacities = {c: Q(n * ports, plan["T"]) for c, n in counts.items()}
    need((plan["M"], plan["L"], stock) == (73, 9, 896), "changed data geometry")
    need(capacities == {8: 672, 16: 448, 32: 448, 48: 448}, "changed idle capacity inventory")
    total_capacity = sum(c * n for c, n in capacities.items())
    total_bonus = sum(BONUSES[c] * n for c, n in capacities.items())
    profile = histogram(claim["profile"])
    idle = histogram(claim["idle"])
    local = histogram(baseline["profile"])
    expected = Counter({r: plan["L"] * claim["replicas"] * n for r, n in local.items()})
    expected.update(idle)
    need(expected == profile, "selected profile does not bind to U8 and idle children")
    need(claim["live"] == stock * claim["replicas"], "selected live stock mismatch")
    need(73 * stock - plan["L"] * 1856 - total_capacity == 320, "common mass deficit")
    price = dict(zip(WIDTHS, PRICES))
    width = sum(int(w) * n for w, n in baseline["inventory"].items())
    signed = sum(price[int(w)] * n for w, n in baseline["inventory"].items())
    slope, multiplier = cost_forms()
    reference = {r: Q(n, claim["replicas"]) for r, n in profile.items()}
    support = {r: Q(plan["L"] * n) for r, n in local.items()}
    add_form(support, slope, total_capacity - plan["L"] * width)
    add_form(support, multiplier, total_bonus + plan["L"] * signed)
    need(support == reference, "mixed support does not equal the selected reference profile")
    ranks = set(range(1, 49)) | {int(r) for p in frozen["interfaces"] for r in p["profile"]}
    engines = {}
    uniform_right = Q(1, 500)
    for name, engine in (("mercator", M), ("atanh", B)):
        values = phi_values(engine, name, lower, upper, ranks)
        need(interval(multiplier, values)[0] > 0, "nonpositive packing multiplier")
        rows = certify_providers(frozen["interfaces"], baseline, values)
        derivatives = derivative_values(engine, name, uniform_right, ranks)
        derivative_rows = certify_providers(frozen["interfaces"], baseline, derivatives)
        need(interval(multiplier, derivatives)[0] > 0, "packing multiplier derivative fails")
        changed_ids = {p["id"] for p in frozen["interfaces"] if p["inventory"] != baseline["inventory"]}
        for row, derivative in zip(rows, derivative_rows):
            if row["id"] != baseline["id"]:
                need(Q(row["lower"]) > Q(27, 4000), "selected-root provider penalty floor fails")
                need(Q(derivative["lower"]) > Q(19, 10), "uniform provider derivative floor fails")
            if row["id"] in changed_ids:
                need(Q(row["lower"]) > Q(113, 200), "selected-root width penalty floor fails")
                need(Q(derivative["lower"]) > 336, "uniform width derivative floor fails")
        engines[name] = dict(phi_interval={r: list(map(str, pair)) for r, pair in values.items()},
                             multiplier=list(map(str, interval(multiplier, values))),
                             bins=certify_bins(values), provider_penalties=rows,
                             uniform_derivative=dict(interval=["0", str(uniform_right)],
                                 phi_derivative_interval={r: list(map(str, pair)) for r, pair in derivatives.items()},
                                 bins=certify_bins(derivatives), provider_derivatives=derivative_rows))
    root_signs = {}
    for name, endpoint in (("lower", lower), ("upper", upper)):
        a = M.moment(profile, 73, claim["live"], endpoint)
        b = B.moment(73, claim["live"], list(profile.items()), endpoint)
        need(a[1] < 1 and b[1] < 1 if name == "lower" else a[0] > 1 and b[0] > 1,
             "selected root endpoint sign: " + name)
        root_signs[name] = dict(endpoint=str(endpoint), mercator=list(map(str, a)), atanh=list(map(str, b)))
    nine = bit["nine"]
    c = Q(nine["bit_lower"])
    bit_deficit = O.pr589_deficit(bit["word"], nine["bit"]["live"])
    bit_signs = O.moment_checks(M, B, histogram(nine["profile"]), 64, nine["bit"]["live"],
                               c, bit_deficit, True)
    need(c > upper, "bit supplier would bind first")
    outer_lower, outer_upper = O.outer47(c, lower, A), O.outer47(c, upper, A)
    need(outer_lower["kappa"] == outer_upper["kappa"] == claim["kappa"], "outer grid changed")
    return dict(status="PASS_HETEROGENEOUS_OWNER_CATALOGUE_BOUND", base=BASE,
                catalogue_sha256=sha(PACKAGE / "CATALOGUE.json"),
                sources=len(frozen["sources"]), records=len(frozen["records"]),
                interfaces=len(frozen["interfaces"]), baseline=baseline["id"],
                root_interval=[str(lower), str(upper)], root_signs=root_signs,
                capacity_per_replica={r: str(n) for r, n in capacities.items()},
                calls_per_replica=9, live_per_replica=stock, deficit_per_replica=320,
                exact_reference_profile={r: str(q) for r, q in sorted(reference.items())},
                engines=engines, bit_with_surcharge=bit_signs,
                alternative_call_penalty_floor="27/4000",
                changed_inventory_call_penalty_floor="113/200",
                uniform_interval=["0", str(uniform_right)],
                uniform_alternative_derivative_floor="19/10",
                uniform_changed_inventory_derivative_floor="336",
                bit_minus_complex_upper=str(c - upper),
                outer_lower=outer_lower, outer_upper=outer_upper,
                dependency_sha256=pins["sha256"],
                scope="All positive replica counts and all per-call mixtures of the pinned catalogue under the retained capacity inventory and whole-helper contract. Shared packing, real mixture counts, arbitrary times, and fragmented idle remainders are allowed as relaxations. No new supplier, owner witness, invoice, or physical admission is claimed.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--audit-current-tree", action="store_true",
                        help="Report later source records without extending the bound.")
    parser.add_argument("--audit-base-tree", action="store_true",
                        help="Check complete source coverage against the pinned Git tree.")
    args = parser.parse_args()
    need(not args.out.exists(), "output exists; choose a new file")
    result = verify()
    if args.audit_base_tree:
        result["base_tree_coverage"] = audit_base_tree(ROOT, read(PACKAGE / "CATALOGUE.json"))
    if args.audit_current_tree:
        result["current_tree_coverage"] = audit_current_tree(ROOT, read(PACKAGE / "CATALOGUE.json"))
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"], "records=" + str(result["records"]),
          "interfaces=" + str(result["interfaces"]),
          "kappa_grid_upper=" + result["outer_upper"]["kappa_decimal"])


if __name__ == "__main__":
    main()
