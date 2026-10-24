"""Price the native words at the fixed selected-rate snapshot."""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import importlib.util
import json
from math import isqrt
from pathlib import Path
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parents[2]
REPO = CAMPAIGN.parents[1]
SOURCE = "lanes/new-core-transfer-20261017/low-displacement-20261020/"
MATCHED_BUDGET = "lanes/budget-geometry-20261017/matched-native-budget-20261018/MATCHED-NATIVE-BUDGET.json"
FUSION = "lanes/bridge-access-20261017/rank9-completion-20261020/"
PINS = {
    SOURCE + "NATIVE-FREEZE.json": "efdf8acc943934e83374f986a4a9a6f49ab7607a4f4e8d2973ec71cd5e1c5e24",
    SOURCE + "native-normal-v2/NATIVE-CHECKS.json": "8acc084b5cd1d9513fdd3373eede998bd08e7f3fe1624f9fd41f758d4de7cb82",
    SOURCE + "native-normal-v2/NATIVE-PROGRAM.json.gz": "e387b082422f085efc8122497cdda0b5211a86b0418af4b9fdbc1da15ac71558",
    SOURCE + "EXTENSIONS-FREEZE.json": "aec99dd0638e635619b14ffd056ab2581424d765d435462aed94b8c8f882a689",
    SOURCE + "odd16-normal-v2/EXTENSION-CHECKS.json": "a502af8c80df714e4d06012bedba0433f977a402c1093e210c0cb28cb4044197",
    SOURCE + "odd16-normal-v2/EXTENSION-PROGRAM.json.gz": "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4",
    SOURCE + "CODED-EXITS-FREEZE.json": "f466ce7bc9d6f5459462acd1799f269a6c2685aea124a3d18f579d542f269936",
    SOURCE + "coded-normal/CODED-EXITS-CHECKS.json": "b36bee542add54bac48e409c6a4a054b3bca5fba9c98d5513a90a6a92628d576",
    SOURCE + "coded-normal/CODED-EXITS-PROGRAM.json.gz": "7f7efbd4a080f641b7ffcb774c677c66344de60d57c6ecc67cdfc0e6f2f6f73d",
    MATCHED_BUDGET: "a1832aeb1d82498f423637ba8cab0ff11262383665ed440159759bc54fe5775e",
    FUSION + "FREEZE.json": "6177f89c88b503765a724e8c1baa934da582c490089dbe29e0f6ce2371f9904b",
    FUSION + "CHECKS.json": "c4b92b37441c095ff3c4d51ea920dd918edd54113764d76ce721a30ec435a2b0",
}
COMMIT = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
ENGINE_ROOT = "research/complex-k492-owner-repair/vendor/multicold/engines/"
ENGINE_PINS = {
    "moment.py": "81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482",
    "base_two_moment.py": "aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098",
}
B = Q(67018507072324140917, 40000000000000000000000)
D, W, CALLS = 25, 224, 3
RANK30 = Counter({1: 1036, 3: 48, 4: 55, 5: 55, 6: 9, 7: 9})
ODD16 = Counter({1: 1520, 2: 64, 3: 48})
CHANGED = {
    "rank30_W48_I64": Counter({1: 988, 2: 48, 4: 55, 5: 55, 6: 9, 7: 9}),
    "rank30_W112": Counter({1: 988, 2: 48, 5: 55, 6: 55, 7: 9, 8: 9}),
    "odd_rank16_W48_I64": Counter({1: 1472, 2: 112}),
    "odd_rank16_W112": Counter({1: 1408, 2: 112, 3: 64}),
}


def need(ok, text):
    if not ok:
        raise ValueError(text)


def mass(profile):
    return sum(r * n for r, n in profile.items())


def bounds(values):
    lo, hi = max(v[0] for v in values), min(v[1] for v in values)
    need(lo <= hi, "Both exact engines overlap")
    scale = 10**18
    return [str(Q((lo * scale).__floor__(), scale)), str(Q((hi * scale).__ceil__(), scale))]


def literal_invoice(receipt, payload, expected_profile, expected_scalar,
                    field_rank_census=None, endpoint_count=224, inline_maps=0, fraction_pairs=False):
    if field_rank_census is None:
        field_rank_census = Counter({8: 224})
    literal = {}
    for provider, directions in payload["providers"].items():
        for direction, word in directions.items():
            native = [e for e in word["events"] if e[0] == "native"]
            scalar = [e[1] for e in word["events"] if e[0] == "scalar"]
            monomial = [e for e in word["events"] if e[0] == "monomial"]
            need(len(native) + len(scalar) + len(monomial) == len(word["events"]), "Every local event is priced")
            need(len(monomial) == inline_maps and all(0 <= e[1] < 224 for e in monomial), "Inline monomial census")
            profile = Counter(e[4] for e in native)
            need(profile == expected_profile, "Literal native profile")
            fields = Counter()
            for event in native:
                need(0 <= event[1] < 224, "Native child uses data")
                fields[event[1]] += event[4]
            need(len(fields) == 224 and Counter(fields.values()) == field_rank_census, "Per-field rank census")
            need(all(g[0] in ("add", "scale") and 0 <= g[1] < 224
                     and (g[0] != "add" or 0 <= g[2] < 224) for g in scalar), "Scalar work uses data")
            if fraction_pairs:
                need(all(len(g) == (5 if g[0] == "add" else 4) for g in scalar), "Numerator-denominator gate schema")
                census = Counter((g[0], Q(*g[-2:])) for g in scalar)
            else:
                need(all(len(g) == 4 and isinstance(g[3], str) for g in scalar), "Fraction-string gate schema")
                census = Counter((g[0], Q(g[3])) for g in scalar)
            scalar_cost = 0
            for (op, coefficient), count in census.items():
                if op == "add":
                    need(abs(coefficient) in (1, 2, 3), "Admitted integer ADD coefficients")
                    cost = {1: 8, 2: 10, 3: 12}[abs(coefficient)]
                else:
                    need(coefficient in (-1, 2, Q(1, 2), -2, Q(-1, 2)), "Admitted dyadic scales")
                    cost = 4 if coefficient in (-2, Q(-1, 2)) else 2
                scalar_cost += count * cost
            bill = receipt["reports"][direction] if "reports" in receipt else receipt[provider][direction]
            need(scalar_cost == bill["real_scalar_primitives"] == expected_scalar, "Literal scalar invoice")
            need(bill["native_children"] == len(native) == sum(expected_profile.values()), "Literal native count")
            need(bill["native_mass"] == mass(profile), "Receipt native mass")
            need(len(word["endpoint_adapters"]) == bill.get("endpoint_maps", bill.get("external_endpoint_maps"))
                 == endpoint_count, "Endpoint count")
            literal[provider + "/" + direction] = {
                "profile": profile, "children": len(native), "native_mass": mass(profile),
                "scalar_primitives": scalar_cost, "map_bound": 2 * len(native) + endpoint_count + inline_maps,
                "field_rank_census": field_rank_census, "endpoint_maps": endpoint_count, "inline_maps": inline_maps,
                "scalar_census": {op + ":" + str(c): n for (op, c), n in sorted(census.items())},
            }
    return literal


def main():
    source = {}
    for path, pin in PINS.items():
        raw = (CAMPAIGN / path).read_bytes()
        if path.endswith(".gz"):
            raw = gzip.decompress(raw)
        need(sha256(raw).hexdigest() == pin, "Source pin: " + path)
        source[path] = json.loads(raw)
    literal = {
        "rank30": literal_invoice(source[SOURCE + "native-normal-v2/NATIVE-CHECKS.json"],
                                  source[SOURCE + "native-normal-v2/NATIVE-PROGRAM.json.gz"], RANK30, 5288),
        "odd_rank16": literal_invoice(source[SOURCE + "odd16-normal-v2/EXTENSION-CHECKS.json"],
                                      source[SOURCE + "odd16-normal-v2/EXTENSION-PROGRAM.json.gz"], ODD16, 7384),
    }
    changed_words = source[SOURCE + "coded-normal/CODED-EXITS-PROGRAM.json.gz"]["providers_by_response_and_code"]
    changed_receipts = source[SOURCE + "coded-normal/CODED-EXITS-CHECKS.json"]["receipts"]
    for family, prefix, scalar in (("rank30", "rank30", 5288), ("rank16", "odd_rank16", 7384)):
        for code in ("W48_I64", "W112"):
            name = prefix + "_" + code
            census = Counter({7: 96, 8 if code == "W48_I64" else 9: 128})
            literal[name] = literal_invoice(changed_receipts[family][code],
                                           {"providers": changed_words[family][code]}, CHANGED[name], scalar,
                                           census, 176 if code == "W48_I64" else 112, 48, fraction_pairs=True)

    results = {}
    with tempfile.TemporaryDirectory(prefix="low-displacement-moment-") as folder:
        engines = []
        for i, (name, pin) in enumerate(ENGINE_PINS.items()):
            raw = subprocess.check_output(["git", "-C", str(REPO), "show", COMMIT + ":" + ENGINE_ROOT + name])
            need(sha256(raw).hexdigest() == pin, "Exact engine pin")
            path = Path(folder) / name
            path.write_bytes(raw)
            spec = importlib.util.spec_from_file_location("low_displacement_engine_" + str(i), path)
            engine = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(engine)
            engines.append(engine)

        def moments(profile):
            values = [engines[0].moment(profile, D, W, B, False),
                      engines[1].moment(D, W, list(profile.items()), B)]
            bounds(values)
            return values

        def allowance(profile):
            base = moments(profile)
            need(all(hi < 1 for lo, hi in base), "Positive native headroom")
            answer = {"moment": bounds(base), "native_mass": mass(profile), "profile": profile, "limits": {}}
            for rank in (1, 2, 4, 8, 9, 17):
                unit = moments({rank: 1})
                counts = [((1 - hi) / unit_hi).__floor__() for (lo, hi), (unit_lo, unit_hi) in zip(base, unit)]
                need(counts[0] == counts[1], "Both engines give the same integer allowance")
                n = counts[0]
                yes, no = moments(profile + Counter({rank: n})), moments(profile + Counter({rank: n + 1}))
                need(all(hi < 1 for lo, hi in yes) and all(lo > 1 for lo, hi in no), "Strict allowance and next failure")
                answer["limits"][str(rank)] = {"children": n, "rank_mass": n * rank,
                                               "accepted": bounds(yes), "next": bounds(no)}
            rank_max = isqrt((D * D - 1) // 2)

            def packed(n):
                q, r = divmod(n, rank_max)
                return Counter({rank_max: q}) + (Counter({r: 1}) if r else Counter())

            lo, hi = 0, D * W - mass(profile)
            need(all(a > 1 for a, b in moments(profile + packed(hi))), "Full rank budget fails")
            while hi - lo > 1:
                mid = (hi + lo) // 2
                at = moments(profile + packed(mid))
                if all(b < 1 for a, b in at):
                    lo = mid
                else:
                    need(all(a > 1 for a, b in at), "Exact packed-rank sign")
                    hi = mid
            answer["all_legal_ranks"] = {
                "maximum_child_rank": rank_max, "total_rank_limit": lo, "best_profile": packed(lo),
                "accepted": bounds(moments(profile + packed(lo))),
                "next_best_profile": packed(hi), "next": bounds(moments(profile + packed(hi))),
                "scope": "Arithmetic optimum by concavity. No access or native construction is supplied.",
            }
            return answer

        for name, local, scalar, correction, status in (
            ("rank30", RANK30, 5288, 30, "Frozen literal native word"),
            ("odd_rank16", ODD16, 7384, 16, "Frozen literal native word; rational code and global admission remain separate"),
        ):
            need(mass(local) == 1792 and all(2 * r * r < D * D for r in local), "Local rank and size")
            whole = Counter({r: CALLS * n for r, n in local.items()})
            row = allowance(whole)
            row.update({"local_profile": local, "local_children": sum(local.values()),
                        "local_scalar_primitives": scalar, "three_call_scalar_subtotal": CALLS * scalar,
                        "source_status": status, "local_correction_rank": correction,
                        "unfused_terminal_H1": 224,
                        "H1_removal_from_unfused_terminal": 224 - row["limits"]["1"]["children"],
                        "unfused_terminal_moment": bounds(moments(whole + Counter({1: 224})))})
            need(mass(whole) == 5376 and mass(whole + Counter({1: 224})) == D * W, "Complete raw rank account")
            for count in (2 * correction, 6 * correction):
                row.setdefault("hypothetical_H1_terminal_targets", {})[str(count)] = {
                    "moment": bounds(moments(whole + Counter({1: count}))),
                    "remaining_H1": row["limits"]["1"]["children"] - count,
                    "scope": "An arithmetic target only. Local correction rank does not provide routed terminal access.",
                }
            results[name] = row
            print(name, "H1", row["limits"]["1"]["children"], "H2", row["limits"]["2"]["children"],
                  "any rank", row["all_legal_ranks"]["total_rank_limit"], flush=True)

        for name, local in CHANGED.items():
            need(all(2 * r * r < D * D for r in local), "Changed-output child size")
            whole = Counter({r: CALLS * n for r, n in local.items()})
            row = {"local_profile": local, "local_mass": mass(local), "preterminal": allowance(whole),
                   "source_status": "Frozen literal changed-output word; global transport and terminal remain separate",
                   "terminal_comparator": {"1": 224},
                   "terminal_scope": "A 224-H1 bill is a comparator only. The changed outputs need a new global terminal proof."}
            complete = whole + Counter({1: 224})
            row["with_terminal_comparator_moment"] = bounds(moments(complete))
            row["with_terminal_comparator_rank_mass"] = mass(complete)
            if name.endswith("W48_I64"):
                need(mass(local) == 1696 and mass(complete) + 288 == D * W, "Full per-call restoration loses")
                row["all_other_debt_after_terminal"] = allowance(complete)
                row["full_per_call_restoration_rank"] = 288
                row["restoration_scope"] = "If all 96 missing ranks are paid after every call, the full mass reaches DW and no positive b passes. This does not prove that the debt is necessary."
                print(name, "H1 debt", row["all_other_debt_after_terminal"]["limits"]["1"]["children"],
                      "any rank debt", row["all_other_debt_after_terminal"]["all_legal_ranks"]["total_rank_limit"], flush=True)
            else:
                need(mass(local) == 1824 and mass(complete) == D * W + 96, "Uniform output with full terminal exceeds rank budget")
                row["rank_excess_over_full_budget"] = 96
            results[name] = row

        matched = Counter({1: 160, 2: 48, 5: 48, 7: 112, 8: 64})
        need(source[MATCHED_BUDGET]["literal_local_invoice"]["base/forward"]["native_profile"]
             == {str(r): n for r, n in matched.items()}, "Pinned matched comparator")
        fusion_base = Counter({r: CALLS * n for r, n in matched.items()})
        fusion_base[7] -= 64
        fusion_base[9] += 64
        fusion = allowance(fusion_base)
        fusion["remaining_terminal_H1"] = 96
        fusion["minimum_H1_saving"] = 96 - fusion["limits"]["1"]["children"]
        fusion["complete_moment"] = bounds(moments(fusion_base + Counter({1: 96})))
        need({str(r): n for r, n in (fusion_base + Counter({1: 96})).items()}
             == source[FUSION + "CHECKS.json"]["complete_native_profile_after"], "Pinned rank-nine completion profile")
        need(source[FUSION + "CHECKS.json"]["complete_native_rank"] == 5600, "Rank-nine completion mass")
        fusion["scope"] = "The frozen bridge construction replaces the final 64 H7 and 64 terminal H2 by 64 H9. Its independent native review is pending. This checker binds its profile and prices it; it does not rerun the wrapper phase checks."
        results["matched_H7_H2_fusion"] = fusion

    out = {"status": "PASS_TWO_EXACT_ENGINES_WITH_EXPLICIT_SOURCE_SCOPE",
           "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
           "source_pins": PINS, "gzip_pin_convention": "Decompressed bytes",
           "engine_commit": COMMIT, "engine_pins": ENGINE_PINS,
           "dimension": D, "productive_width": W, "calls": CALLS, "idle_profile": {},
           "selected_b_snapshot": str(B), "literal_native_invoices": literal, "results": results,
           "W48_scope": "The frozen changed-exit histograms are counted literally. Global transport and terminal compatibility remain unproved. No mass-only pricing shortcut is used.",
           "global_scope": "A hypothetical three-call D25 placement is priced. Routed codes, terminal access, recursive host and complete finite costs remain separate."}
    (HERE / "BUDGET.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
