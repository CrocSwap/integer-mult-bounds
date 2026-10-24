"""Check the clean words and bound their conditional native budgets."""

import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parents[2]
REPO = CAMPAIGN.parents[1]
PRODUCER = CAMPAIGN / "lanes/budget-geometry-20261017/clean-exchange-budget-20261020"
ENGINE = HERE.parent / "low-displacement-budget-review-20261020"
ENGINE_PIN = "953690464698b38801b4f2ddf0f56035203a9337214595a557c7d3950e2e6f87"
FREEZE_PIN = "c2ee7b116d5b177c06b94fffb167354c3e6b49d759f2df16a4599eefded121d5"
RECEIPT_PIN = "30a59c5cda0ff3c6f9e6ad7f9f38ec98fbfe71d34c58ddf768964cda304ba30d"
COMMIT = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
LOCAL = "lanes/new-core-transfer-20261017/low-displacement-20261020/clean-late-exchange-20261020/"
B = Q(67018507072324140917, 40000000000000000000000)


def need(test, reason):
    if not test:
        raise ValueError(reason)


def digest(raw):
    return sha256(raw).hexdigest()


def read(path, pin, compressed=False):
    raw = path.read_bytes()
    if compressed:
        raw = gzip.decompress(raw)
    need(digest(raw) == pin, "Source pin: " + str(path))
    return json.loads(raw)


def freeze(path, pin):
    result = read(path, pin)
    for name, expected in result["files"].items():
        need(digest((path.parent / name).read_bytes()) == expected, "Frozen file: " + name)
    return result


freeze(ENGINE / "FREEZE.json", ENGINE_PIN)
spec = importlib.util.spec_from_file_location("third_exact_budget_engine", ENGINE / "check_review.py")
math = importlib.util.module_from_spec(spec)
spec.loader.exec_module(math)


def encode(interval):
    return [str(value) for value in interval]


def enclosure(interval, outer, label):
    a, b = map(Q, outer)
    need(a <= interval[0] <= interval[1] <= b, "Independent interval: " + label)


def census(word, initial):
    profile = Counter()
    field_ranks = Counter()
    tariffs = Counter()
    recipe_identity = {
        "matrix_rows": [1 << i for i in range(9)],
        "linear_Z4": [0] * 9,
        "quadratic_rows": [0] * 9,
        "offset": 0,
        "phase": 0,
    }
    direct = 0
    for event in word["events"]:
        if event[0] == "native":
            _, field, _, _, rank, key = event
            need(0 <= field < 224 and 0 < rank <= 17 and 2 * rank * rank < 25 * 25,
                 "Native data role and size")
            recipe = word["native_recipes"][key]
            need(recipe["rank"] == rank and recipe["left"] is not None
                 and recipe["right"] is not None, "Complete native recipe")
            profile[rank] += 1
            field_ranks[field] += rank
            if initial and rank == 9:
                need(recipe["left"] == recipe_identity == recipe["right"], "Direct H9 has identity sides")
                direct += 1
        else:
            need(event[0] == "scalar" and len(event[1]) == 4, "Every event is counted")
            op, target, source, value = event[1]
            value = Q(value)
            need(0 <= target < 224 and op in ("add", "scale"), "Scalar data role")
            if op == "add":
                need(0 <= source < 224 and abs(value) == 1, "Unit complex data ADD")
                price = 8
            else:
                need(source is None and value in (-1, 2, Q(1, 2), -2, Q(-1, 2)),
                     "Power-of-two SCALE")
                price = 2 * ((abs(value) != 1) + (value < 0))
            tariffs[price] += 1
    expected = Counter({1: 1392, 2: 64, 3: 48, 9 if initial else 8: 16})
    need(profile == expected, "Native histogram")
    need(set(field_ranks) == set(range(224)), "Every productive field is counted")
    need(Counter(field_ranks.values()) == (Counter({8: 208, 9: 16}) if initial else Counter({8: 224})),
         "Per-field rank sum")
    need(tariffs == Counter({8: 1032, 2: 96, 4: 38}), "Complete scalar tariff census")
    need(len(word["input_views"]) == (112 if initial else 128)
         and len(word["output_views"]) == 96 and direct == (16 if initial else 0),
         "All external and direct views are counted")
    side_maps = 2 * sum(profile.values()) - 2 * direct
    return {
        "profile": dict(sorted(profile.items())),
        "children": sum(profile.values()),
        "native_mass": sum(rank * n for rank, n in profile.items()),
        "scalar_primitives": sum(price * n for price, n in tariffs.items()),
        "scalar_tariff_census": dict(sorted(tariffs.items())),
        "input_maps": len(word["input_views"]),
        "output_maps": len(word["output_views"]),
        "native_side_map_bound": side_maps,
        "total_map_bound": len(word["input_views"]) + len(word["output_views"]) + side_maps,
        "field_rank_census": dict(sorted(Counter(field_ranks.values()).items())),
    }


def check_threshold(profile, row):
    expected = Counter({int(r): n for r, n in row["profile"].items()})
    need(profile == expected, "Complete histogram binding")
    need(sum(r * n for r, n in profile.items()) == row["mass"], "Complete native mass")
    value = math.moment(profile)
    enclosure(value, row["moment"], "base")
    need(value[1] < 1, "Positive conditional allowance")
    result = {"profile": dict(sorted(profile.items())), "moment": encode(value), "limits": {}}
    for rank in (1, 2):
        old = row["limits"][str(rank)]
        n = old["children"]
        yes = math.moment(profile + Counter({rank: n}))
        no = math.moment(profile + Counter({rank: n + 1}))
        enclosure(yes, old["accepted"], "accepted H" + str(rank))
        enclosure(no, old["next"], "next H" + str(rank))
        need(yes[1] < 1 < no[0] and old["rank_mass"] == rank * n, "Strict threshold")
        result["limits"][str(rank)] = {"children": n, "accepted": encode(yes), "next": encode(no)}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "normal")
    args = parser.parse_args()
    freeze(PRODUCER / "FREEZE.json", FREEZE_PIN)
    receipt = read(PRODUCER / "BUDGET.json", RECEIPT_PIN)
    need(receipt["dimension"] == 25 and receipt["productive_width"] == 224
         and receipt["calls"] == 3 and receipt["idle_profile"] == {}, "Exact conditional model")
    need(Q(receipt["historical_selected_b"]) == B == math.B and 0 < B < 1,
         "Exact positive historical exponent")
    need(receipt["engine_commit"] == COMMIT, "Historical certificate commit")
    selected_raw = (CAMPAIGN.parent / "historical" / COMMIT / "certificates/selected-result.json").read_bytes()
    need(digest(selected_raw) == receipt["selected_result_sha256"] == math.PINS["selected"],
         "Selected certificate source")
    selected = json.loads(selected_raw)
    assembly_raw = (CAMPAIGN.parent / "historical" / COMMIT / selected["certificate"]).read_bytes()
    need(digest(assembly_raw) == selected["certificate_sha256"]
         == receipt["assembly_sha256"] == math.PINS["assembly"], "Selected assembly source")
    need(Q(json.loads(assembly_raw)["complex_lower"]) == B, "Selected exponent from assembly")
    source = {}
    for path, pin in receipt["source_pins"].items():
        source[path] = read(CAMPAIGN / path, pin, path.endswith(".gz"))
        if path.endswith("FREEZE.json"):
            freeze(CAMPAIGN / path, pin)
    invoices = {}
    for name, suffix in (("clean", "run-normal/CLEAN-LATE-EXCHANGE.json.gz"),
                         ("dual", "dual-normal/CLEAN-DUAL.json.gz")):
        payload = source[LOCAL + suffix]
        need(set(payload["providers"]) == {"base", "extra"}, "Both native providers")
        for provider, variants in payload["providers"].items():
            need(set(variants) == ({"I", "Q"} if name == "clean"
                                   else {"inverse_adjoint", "selected_swap_conjugate"}),
                 "All clean and dual variants")
            for variant, word in variants.items():
                key = name + "/" + provider + "/" + variant
                bill = census(word, name == "clean" and variant == "I")
                old = receipt["literal"][name][provider + "/" + variant]
                need(bill["profile"] == {int(k): n for k, n in old["profile"].items()}
                     and bill["children"] == old["children"]
                     and bill["native_mass"] == old["mass"]
                     and bill["scalar_primitives"] == old["scalar"]
                     and bill["native_side_map_bound"] == old["native_side_map_bound"]
                     and bill["total_map_bound"] == old["total_map_bound"], "Independent literal invoice")
                invoices[key] = bill
    need(len(invoices) == 8, "All eight literal words")
    results = {}
    for name, initial in (("three_Q", 0), ("one_I_two_Q", 1)):
        local_q = Counter(invoices["clean/base/Q"]["profile"])
        local_i = Counter(invoices["clean/base/I"]["profile"])
        profile = Counter({r: (3 - initial) * n for r, n in local_q.items()})
        profile.update({r: initial * n for r, n in local_i.items()})
        profile = +profile
        old = receipt["results"][name]
        result = check_threshold(profile, old)
        result["cleanup"] = {}
        for size in (112, 128, 144):
            result["cleanup"][str(size)] = check_threshold(
                profile + Counter({1: size}), old["hypothetical_H1_cleanup"][str(size)])
        need(old["three_call_scalar_subtotal"] == 3 * 8600 == 25800, "Three scalar calls")
        maps = (3 - initial) * invoices["clean/base/Q"]["total_map_bound"]
        maps += initial * invoices["clean/base/I"]["total_map_bound"]
        need(maps == old["three_call_map_bound"] == 9792 - 48 * initial, "Three map counts")
        narrow = 196 - 16 * initial
        yes = math.moment(profile + Counter({1: narrow}))
        next_two = Counter({2: (narrow + 1) // 2, 1: (narrow + 1) % 2})
        no = math.moment(profile + next_two)
        need(yes[1] < 1 < no[0], "All mixtures of H1 and H2 have the stated sharp rank budget")
        result["all_H1_H2_mixtures"] = {
            "total_rank_limit": narrow, "all_H1_at_limit": encode(yes),
            "cheapest_next_profile": dict(sorted(next_two.items())),
            "cheapest_next_moment": encode(no),
        }
        broad = narrow + 1
        need(2 * 17**2 < 25**2 < 2 * 18**2, "Largest legal child rank")
        yes = math.moment(profile + math.packed(broad))
        no = math.moment(profile + math.packed(broad + 1))
        need(yes[1] < 1 < no[0], "Sharp total-rank budget over all legal child ranks")
        result["all_legal_ranks"] = {
            "largest_child_rank": 17, "total_rank_limit": broad,
            "best_profile": dict(sorted(math.packed(broad).items())),
            "accepted": encode(yes),
            "next_best_profile": dict(sorted(math.packed(broad + 1).items())),
            "next": encode(no),
        }
        terminal = math.moment(profile + Counter({1: 224}))
        need(terminal[0] > 1, "The complete 224-H1 terminal fails")
        result["full_terminal"] = {"moment": encode(terminal), "minimum_H1_removal": 224 - narrow}
        results[name] = result
    result = {
        "status": "PASS_INDEPENDENT_CLEAN_EXCHANGE_BUDGET",
        "checker_sha256": digest(Path(__file__).read_bytes()),
        "producer_freeze_sha256": FREEZE_PIN,
        "third_engine_review_sha256": ENGINE_PIN,
        "third_engine_imported_from_producer": False,
        "historical_certificate_commit": COMMIT,
        "historical_b": str(B),
        "invoices": invoices,
        "results": results,
        "scope": "Literal invoice and strict conditional native arithmetic only. No new phase review or routed caller.",
    }
    args.output.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode()
    (args.output / "REVIEW-CHECKS.json").write_bytes(raw)
    print(result["status"])
    print(digest(raw))


if __name__ == "__main__":
    main()
