"""Check the literal invoices and the conditional native budgets."""

from collections import Counter
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys


HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parents[2]
REPO = CAMPAIGN.parents[1]
BUDGET = CAMPAIGN / "lanes/budget-geometry-20261017"
LOW = BUDGET / "low-displacement-budget-20261020"
MIXED = BUDGET / "mixed-exit-budget-20261020"
SOURCE = "lanes/new-core-transfer-20261017/low-displacement-20261020/"
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
PINS = {
    "low_freeze": "c730e61f7446b072c60411f9cb6af903e5b252b12ce9a4d9bce906990303fbef",
    "low_receipt": "12836f56beffb0c136b075b44ec25377bba88d122924c67bd0a159a5037b84d2",
    "mixed_freeze": "99f084410fcba6228d396d8c547dd4ed74835dc97de7fce004387b6de6ab92a5",
    "mixed_receipt": "7359fbab24858a21ea9879fff0b61883134ee3bb754916085689136f6d833224",
    "selected": "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
    "assembly": "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
    "rank9_review": "50f2e168cdbf08e2bdad445bf2aa28f96d699cbc669a39892927bf94593e3b51",
}
B = Q(67018507072324140917, 40000000000000000000000)
D, W = 25, 224
GRID = 10**60
LOG_TERMS = 64
EXP_DEGREE = 20


def need(value, reason):
    if not value:
        raise ValueError(reason)


def pinned(raw, digest, label):
    need(sha256(raw).hexdigest() == digest, "Source pin: " + label)
    return json.loads(raw)


def read(path, digest):
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    return pinned(raw, digest, str(path.relative_to(CAMPAIGN)))


def floor(value):
    return Q((value * GRID).__floor__(), GRID)


def ceil(value):
    return -floor(-value)


def log_series(z):
    need(0 <= z <= Q(1, 3), "Reduced logarithm argument")
    term, total = z, Q(0)
    for j in range(LOG_TERMS):
        total += 2 * term / (2 * j + 1)
        term *= z * z
    tail = 2 * term / ((2 * LOG_TERMS + 1) * (1 - z * z))
    return total, total + tail


@cache
def logarithm(value):
    need(value >= 1, "Positive logarithm")
    k = 0
    while value >= 2:
        value /= 2
        k += 1
    a, b = log_series((value - 1) / (value + 1))
    c, d = log_series(Q(1, 3))
    return floor(a + k * c), ceil(b + k * d)


def exponential(lo, hi):
    need(0 <= lo <= hi < Q(1, 100), "Small positive exponential")

    def partial(value):
        total = term = Q(1)
        for j in range(1, EXP_DEGREE + 1):
            term *= value / j
            total += term
        return total, term

    low, _ = partial(lo)
    high, last = partial(hi)
    tail = last * hi / (EXP_DEGREE + 1) / (1 - hi / (EXP_DEGREE + 2))
    return floor(low), ceil(high + tail)


@cache
def unit(rank):
    a, b = logarithm(Q(D, rank))
    c, d = exponential(B * a, B * b)
    return Q(rank, D * W) * c, Q(rank, D * W) * d


def counts(value):
    return Counter({int(r): n for r, n in value.items() if n})


def mass(value):
    return sum(r * n for r, n in value.items())


def moment(profile):
    answer = [Q(0), Q(0)]
    for r, n in profile.items():
        need(0 < r < D and n > 0, "Positive child multiplicity")
        low, high = unit(r)
        answer[0] += n * low
        answer[1] += n * high
    return tuple(answer)


def encode(value):
    return [str(x) for x in value]


def enclosure(inner, outer, label):
    a, b = map(Q, outer)
    need(a <= inner[0] <= inner[1] <= b, "Independent interval is enclosed: " + label)


def scalar_word(word):
    answer = []
    for event in word["events"]:
        if event[0] != "scalar":
            continue
        gate = event[1]
        if isinstance(gate[-1], str):
            op, target, source, coefficient = gate
            coefficient = Q(coefficient)
        else:
            op, target = gate[:2]
            source = gate[2] if op == "add" else None
            coefficient = Q(*gate[-2:])
        need(op in ("add", "scale") and 0 <= target < W, "Data scalar target")
        need(op != "add" or 0 <= source < W, "Data scalar source")
        answer.append((op, target, source if op == "add" else None, coefficient))
    return answer


def scalar_price(gate):
    op, _, _, coefficient = gate
    if op == "add":
        need(abs(coefficient) in (1, 2, 3), "Integer ADD tariff")
        return {1: 8, 2: 10, 3: 12}[abs(coefficient)]
    need(coefficient in (-1, 2, Q(1, 2), -2, Q(-1, 2)), "Dyadic scale tariff")
    return 2 * ((abs(coefficient) != 1) + (coefficient < 0))


def invoice(word):
    profile, field_mass = Counter(), Counter()
    inline = 0
    for event in word["events"]:
        kind = event[0]
        need(kind in ("scalar", "native", "monomial"), "Known local event")
        if kind == "scalar":
            continue
        need(0 <= event[1] < W, "Data native or map owner")
        recipe = word["native_recipes"][event[-1]]
        if kind == "native":
            rank = event[4]
            need(0 < rank <= 17 and recipe["rank"] == rank, "Native rank and recipe")
            need(recipe["left"] is not None and recipe["right"] is not None, "Two native side maps")
            profile[rank] += 1
            field_mass[event[1]] += rank
        else:
            need(recipe["rank"] == 0 and recipe["left"] is not None
                 and recipe["right"] is None, "One inline monomial map")
            inline += 1
    for endpoint in word["endpoint_adapters"]:
        need(endpoint["rank"] == 0 and endpoint["left"] is not None
             and endpoint["right"] is None, "One endpoint map")
    need(set(field_mass) == set(range(W)), "All data fields occur")
    scalars = scalar_word(word)
    census = Counter((op, coefficient) for op, _, _, coefficient in scalars)
    return {
        "profile": dict(sorted(profile.items())),
        "native_mass": mass(profile),
        "children": sum(profile.values()),
        "scalar_primitives": sum(map(scalar_price, scalars)),
        "endpoint_maps": len(word["endpoint_adapters"]),
        "inline_maps": inline,
        "map_bound": 2 * sum(profile.values()) + len(word["endpoint_adapters"]) + inline,
        "field_rank_census": dict(sorted(Counter(field_mass.values()).items())),
        "scalar_census": {op + ":" + str(c): n for (op, c), n in sorted(census.items())},
    }


def packed(total):
    q, r = divmod(total, 17)
    return Counter({17: q}) + (Counter({r: 1}) if r else Counter())


def main():
    for directory, key in ((LOW, "low"), (MIXED, "mixed")):
        freeze = read(directory / "FREEZE.json", PINS[key + "_freeze"])
        for name, pin in freeze["files"].items():
            need(sha256((directory / name).read_bytes()).hexdigest() == pin, "Frozen file: " + name)
    low = read(LOW / "BUDGET.json", PINS["low_receipt"])
    mixed = read(MIXED / "MIXED-BUDGET.json", PINS["mixed_receipt"])
    read(HERE.parent / "rank9-completion-review-20261020/FREEZE.json", PINS["rank9_review"])
    selected_path = "certificates/selected-result.json"
    selected = pinned((CAMPAIGN.parent / "historical" / BASE / selected_path).read_bytes(),
                      PINS["selected"], selected_path)
    assembly = pinned((CAMPAIGN.parent / "historical" / BASE / selected["certificate"]).read_bytes(),
                      PINS["assembly"], selected["certificate"])
    need(selected["certificate_sha256"] == PINS["assembly"], "Selected certificate binding")
    need(Q(assembly["complex_lower"]) == B == Q(low["selected_b_snapshot"])
         == Q(mixed["selected_b_snapshot"]), "Historical selected exponent")
    need(0 < B < 1 and (low["dimension"], low["productive_width"], low["calls"]) == (D, W, 3)
         and low["idle_profile"] == {}, "Conditional schedule")

    sources = {name: read(CAMPAIGN / name, digest) for name, digest in low["source_pins"].items()}
    raw = {
        "rank30": sources[SOURCE + "native-normal-v2/NATIVE-PROGRAM.json.gz"]["providers"],
        "odd_rank16": sources[SOURCE + "odd16-normal-v2/EXTENSION-PROGRAM.json.gz"]["providers"],
    }
    changed = sources[SOURCE + "coded-normal/CODED-EXITS-PROGRAM.json.gz"]["providers_by_response_and_code"]
    words = dict(raw)
    for family, local in (("rank30", "rank30"), ("odd_rank16", "rank16")):
        for code in ("W48_I64", "W112"):
            words[family + "_" + code] = changed[local][code]
    invoices = {}
    for name, providers in words.items():
        need(set(providers) == {"base", "extra"}, "Both providers")
        invoices[name] = {}
        for provider, directions in providers.items():
            need(set(directions) == {"forward", "backward"}, "Both orientations")
            for direction, word in directions.items():
                bill = invoice(word)
                retained = low["literal_native_invoices"][name][provider + "/" + direction]
                for key, value in bill.items():
                    expected = retained[key]
                    if key in ("profile", "field_rank_census"):
                        expected = {int(k): v for k, v in expected.items()}
                    need(value == expected, "Literal invoice: " + name + "/" + key)
                if "_W" in name:
                    family = name.split("_W")[0]
                    need(scalar_word(word) == scalar_word(raw[family][provider][direction]),
                         "The changed exit preserves the complete scalar sequence")
                invoices[name][provider + "/" + direction] = bill
    need(sum(len(x) for x in invoices.values()) == 24, "All raw and changed words")

    certificates = {}

    def check_profile(profile, retained, label):
        interval = moment(profile)
        enclosure(interval, retained, label)
        certificates[label] = {"profile": dict(sorted(profile.items())), "moment": encode(interval)}
        return interval

    def allowance(row, label):
        profile = counts(row["profile"])
        need(mass(profile) == row["native_mass"], "Native mass")
        need(check_profile(profile, row["moment"], label)[1] < 1, "Base passes")
        for rank, entry in row["limits"].items():
            rank, n = int(rank), entry["children"]
            yes = check_profile(profile + Counter({rank: n}), entry["accepted"], label + "/H" + str(rank))
            no = check_profile(profile + Counter({rank: n + 1}), entry["next"], label + "/H" + str(rank) + "+1")
            need(yes[1] < 1 < no[0], "Strict threshold")
            need(entry["rank_mass"] == rank * n, "Threshold rank mass")
        entry = row["all_legal_ranks"]
        n = entry["total_rank_limit"]
        need(entry["maximum_child_rank"] == 17 and 2 * 17**2 < D**2 < 2 * 18**2, "Strict size guard")
        need(counts(entry["best_profile"]) == packed(n)
             and counts(entry["next_best_profile"]) == packed(n + 1), "Packed rank optimum")
        yes = check_profile(profile + packed(n), entry["accepted"], label + "/packed")
        no = check_profile(profile + packed(n + 1), entry["next"], label + "/packed+1")
        need(yes[1] < 1 < no[0], "Strict total-rank threshold")

    for family in ("rank30", "odd_rank16"):
        row = low["results"][family]
        profile = counts(invoices[family]["base/forward"]["profile"])
        need(counts(row["profile"]) == Counter({r: 3 * n for r, n in profile.items()}), "Three raw calls")
        allowance(row, family)
        full = counts(row["profile"]) + Counter({1: 224})
        need(mass(full) == D * W and check_profile(full, row["unfused_terminal_moment"], family + "/full")[0] > 1,
             "Raw terminal comparator fails")
        need(row["H1_removal_from_unfused_terminal"] == 224 - row["limits"]["1"]["children"], "Raw terminal saving")
        for n, target in row["hypothetical_H1_terminal_targets"].items():
            check_profile(counts(row["profile"]) + Counter({1: int(n)}), target["moment"], family + "/target" + n)
            need(target["remaining_H1"] == row["limits"]["1"]["children"] - int(n), "Hypothetical remainder")
        for code in ("W48_I64", "W112"):
            name = family + "_" + code
            row = low["results"][name]
            local = counts(invoices[name]["base/forward"]["profile"])
            three = Counter({r: 3 * n for r, n in local.items()})
            need(counts(row["local_profile"]) == local
                 and counts(row["preterminal"]["profile"]) == three, "Three changed calls")
            allowance(row["preterminal"], name + "/preterminal")
            full = three + Counter({1: 224})
            check_profile(full, row["with_terminal_comparator_moment"], name + "/full")
            need(mass(full) == row["with_terminal_comparator_rank_mass"], "Changed complete mass")
            if code == "W48_I64":
                need(counts(row["all_other_debt_after_terminal"]["profile"]) == full, "Changed debt profile")
                allowance(row["all_other_debt_after_terminal"], name + "/debt")
                need(mass(full) + row["full_per_call_restoration_rank"] == D * W, "Full restoration mass")
            else:
                need(mass(full) == D * W + 96, "Uniform exit excess")

    fusion = low["results"]["matched_H7_H2_fusion"]
    allowance(fusion, "matched_H9")
    full = counts(fusion["profile"]) + Counter({1: 96})
    check_profile(full, fusion["complete_moment"], "matched_H9/full")
    need(full == Counter({1: 576, 2: 144, 5: 144, 7: 272, 8: 192, 9: 64})
         and mass(full) == 5600 and fusion["minimum_H1_saving"] == 15, "Reviewed H9 profile")

    mixed_limits = {}
    for family, rows in mixed["rows"].items():
        old = counts(invoices[family]["base/forward"]["profile"])
        new = counts(invoices[family + "_W48_I64"]["base/forward"]["profile"])
        difference = {r: new[r] - old[r] for r in old.keys() | new.keys() if new[r] != old[r]}
        need(difference == {1: -48, 2: 48, 3: -48}, "The common changed-exit histogram")
        mixed_limits[family] = {}
        for k, row in rows.items():
            k = int(k)
            profile = Counter({r: (3 - k) * n for r, n in old.items()})
            profile.update({r: k * n for r, n in new.items()})
            profile[1] += 224
            profile += Counter()
            need(profile == counts(row["profile"]) and mass(profile) == 5600 - 96 * k, "Mixed word histogram")
            label = family + "/mixed" + str(k)
            need(check_profile(profile, row["moment"], label)[1] < 1, "Mixed base passes")
            for rank, entry in row["limits"].items():
                rank, n = int(rank), entry["children"]
                yes = check_profile(profile + Counter({rank: n}), entry["accepted"], label + "/H" + str(rank))
                no = check_profile(profile + Counter({rank: n + 1}), entry["next"], label + "/H" + str(rank) + "+1")
                need(yes[1] < 1 < no[0], "Mixed strict threshold")
            saving = 96 * k - row["limits"]["1"]["children"]
            need(row["H1_saving_from_full_restoration"] == saving == (25 if family == "rank30" else 30),
                 "Full all-H1 restoration saving")
            mixed_limits[family][str(k)] = {rank: entry["children"] for rank, entry in row["limits"].items()}

    u1, u2, u3 = (unit(r) for r in (1, 2, 3))
    saving = (48 * (u1[0] + u3[0] - u2[1]) / u1[1],
              48 * (u1[1] + u3[1] - u2[0]) / u1[0])
    enclosure(saving, ["95.846609456084463", "95.846609456084464"], "Common H1-equivalent saving")
    need(Q("95.846609456084463") < saving[0] <= saving[1] < Q("95.846609456084464"),
         "Strict common saving enclosure")

    # These checks cover the discrete steps in the packing proof.
    for small in range(1, 17):
        for large in range(small, 17):
            before = moment(Counter([small, large]))
            after = moment(Counter([large + 1]) + (Counter([small - 1]) if small > 1 else Counter()))
            need(after[1] < before[0], "Moving rank to the larger child lowers the cost")

    out = {
        "status": "PASS_INDEPENDENT_LITERAL_AND_RATIONAL_BUDGET_REVIEW",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_pins": PINS,
        "upstream_source_pins": low["source_pins"],
        "selected_commit": BASE,
        "selected_certificate": selected_path,
        "selected_assembly": selected["certificate"],
        "selected_b_snapshot": str(B),
        "literal_words_checked": 24,
        "unchanged_changed_scalar_sequences": 16,
        "literal_invoices": invoices,
        "exact_method": {"log_series": "64 positive atanh terms after binary reduction",
                         "exp_degree": EXP_DEGREE, "outward_grid": str(GRID),
                         "producer_imports": 0, "retained_engine_imports": 0},
        "profile_intervals_checked": len(certificates),
        "certificates": certificates,
        "mixed_limits": mixed_limits,
        "common_changed_exit_H1_equivalent_saving": encode(saving),
        "discrete_packing_steps_checked": 136,
        "scope": "Literal event invoices and conditional D25 histograms. No native phase replay, routed caller, recursive admission, finite map cost, precision, or kappa claim.",
    }
    Path(sys.argv[1]).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print("PASS", len(certificates), "exact profile intervals; 24 literal words; 16 unchanged scalar sequences")


if __name__ == "__main__":
    main()
