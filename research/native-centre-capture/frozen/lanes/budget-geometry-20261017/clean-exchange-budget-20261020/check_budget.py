"""Count the frozen clean-exchange words and price their native profiles."""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parents[2]
REPO = CAMPAIGN.parents[1]
LOCAL = "lanes/new-core-transfer-20261017/low-displacement-20261020/clean-late-exchange-20261020/"
REVIEW = "lanes/new-native-recipes-20261017/clean-centre-exchange-review-20261020/"
PINS = {
    LOCAL + "FREEZE.json": "96048355033e5f5bdd26dadddb869708faae6f8b0d9a61a1ae696e5a5c20c0bc",
    LOCAL + "run-normal/CHECKS.json": "c47f36dbf492b445f84ce6aa97c632a0c5ddcc3eab5d9fa9b836f28133465d2b",
    LOCAL + "run-normal/CLEAN-LATE-EXCHANGE.json.gz": "b0432322c28ad3a03af8da550a0b7c7df048c7ff5a0664acc7f78efffcffd083",
    LOCAL + "DUAL-FREEZE.json": "fa8f910fe7f22a696f47513c95e814588723dc8abaaa68061fcba3676c308d43",
    LOCAL + "dual-normal/CHECKS.json": "ae71aade4909408b376ccf42c99fad56e51297f28c6f293b96639a4e880e163b",
    LOCAL + "dual-normal/CLEAN-DUAL.json.gz": "6c8869b1c1b45632635805e389899b83fa8348c9fe5b84e3c9c7821bcfd0568c",
    REVIEW + "FREEZE.json": "6cd34040ecd7d832f1bae3d44c5a7b97dcc11022d843e48007c5474cc4f3701d",
    REVIEW + "normal/REVIEW.json": "0108d659a4cb3b3e569df37de24dd53893db6e8b93d3945f2300c8eb5b2d2ed5",
}
COMMIT = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
SELECTED_PIN = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
ASSEMBLY_PIN = "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045"
ENGINE_ROOT = "research/complex-k492-owner-repair/vendor/multicold/engines/"
ENGINE_PINS = {
    "moment.py": "81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482",
    "base_two_moment.py": "aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098",
}
B = Q(67018507072324140917, 40000000000000000000000)
D, W = 25, 224
Q_PROFILE = Counter({1: 1392, 2: 64, 3: 48, 8: 16})
I_PROFILE = Counter({1: 1392, 2: 64, 3: 48, 9: 16})


def need(ok, text):
    if not ok:
        raise ValueError(text)


def mass(profile):
    return sum(r * n for r, n in profile.items())


def pinned(raw, pin, label):
    need(sha256(raw).hexdigest() == pin, "Source pin: " + label)
    return json.loads(raw)


def git_file(path):
    return subprocess.check_output(["git", "-C", str(REPO), "show", COMMIT + ":" + path])


def bounds(values):
    lo, hi = max(a for a, b in values), min(b for a, b in values)
    need(lo <= hi, "Exact engine intervals overlap")
    scale = 10**18
    return [str(Q((lo * scale).__floor__(), scale)), str(Q((hi * scale).__ceil__(), scale))]


def count_words(payload, receipt, dual=False):
    answer = {}
    identity = {
        "matrix_rows": [1 << i for i in range(9)], "linear_Z4": [0] * 9,
        "quadratic_rows": [0] * 9, "offset": 0, "phase": 0,
    }
    for provider, variants in payload["providers"].items():
        for variant, word in variants.items():
            is_I = not dual and variant == "I"
            expected = I_PROFILE if is_I else Q_PROFILE
            native = [e for e in word["events"] if e[0] == "native"]
            scalar = [e[1] for e in word["events"] if e[0] == "scalar"]
            need(len(native) + len(scalar) == len(word["events"]), "Every event is counted")
            profile = Counter(e[4] for e in native)
            need(profile == expected, "Literal native profile")
            fields = Counter()
            for event in native:
                need(0 <= event[1] < 224 and 2 * event[4]**2 < D**2, "Data role and child size")
                fields[event[1]] += event[4]
            need(len(fields) == 224 and Counter(fields.values()) ==
                 (Counter({8: 208, 9: 16}) if is_I else Counter({8: 224})), "Per-field rank count")
            census = Counter()
            cost = 0
            for gate in scalar:
                need(len(gate) == 4 and 0 <= gate[1] < 224, "Scalar target")
                coefficient = Q(gate[3])
                if gate[0] == "add":
                    need(0 <= gate[2] < 224 and abs(coefficient) == 1, "Unit data ADD")
                    cost += 8
                else:
                    need(gate[0] == "scale" and coefficient in (-1, 2, Q(1, 2), -2, Q(-1, 2)),
                         "Dyadic data SCALE")
                    cost += 4 if coefficient in (-2, Q(-1, 2)) else 2
                census[gate[0], str(coefficient)] += 1
            report = receipt["reports"][provider][variant]
            need(cost == report["real_scalar_primitives"] == 8600, "Scalar price")
            need(len(native) == report["native_children"] == 1520, "Native count")
            need(mass(profile) == report["native_mass"], "Native mass")
            need(len(word["input_views"]) == report["explicit_input_monomial_views"] == (112 if is_I else 128),
                 "Input view count")
            need(len(word["output_views"]) == report["explicit_output_monomial_views"] == 96, "Output view count")
            if is_I:
                direct = [e for e in native if e[4] == 9]
                need(len(direct) == 16, "Direct FULL count")
                need(all(word["native_recipes"][e[5]] == {"rank": 9, "left": identity, "right": identity}
                         for e in direct), "Direct FULL side maps are identity")
            side_maps = 2 * len(native) - (32 if is_I else 0)
            need(side_maps == report["native_side_map_upper_bound"], "Native side-map bound")
            answer[provider + "/" + variant] = {
                "profile": profile, "children": len(native), "mass": mass(profile),
                "scalar": cost, "input_views": len(word["input_views"]), "output_views": 96,
                "native_side_map_bound": side_maps,
                "total_map_bound": side_maps + len(word["input_views"]) + 96,
                "scalar_census": {op + ":" + coefficient: n for (op, coefficient), n in sorted(census.items())},
            }
    return answer


def main():
    source = {}
    for path, pin in PINS.items():
        raw = (CAMPAIGN / path).read_bytes()
        if path.endswith(".gz"):
            raw = gzip.decompress(raw)
        source[path] = pinned(raw, pin, path)
    selected = pinned(git_file("certificates/selected-result.json"), SELECTED_PIN, "selected result")
    assembly = pinned(git_file(selected["certificate"]), ASSEMBLY_PIN, selected["certificate"])
    need(selected["certificate_sha256"] == ASSEMBLY_PIN and Q(assembly["complex_lower"]) == B,
         "Historical selected exponent")
    literal = {
        "clean": count_words(source[LOCAL + "run-normal/CLEAN-LATE-EXCHANGE.json.gz"],
                             source[LOCAL + "run-normal/CHECKS.json"]),
        "dual": count_words(source[LOCAL + "dual-normal/CLEAN-DUAL.json.gz"],
                            source[LOCAL + "dual-normal/CHECKS.json"], True),
    }
    results = {}
    with tempfile.TemporaryDirectory(prefix="clean-exchange-moment-") as folder:
        engines = []
        for i, (name, pin) in enumerate(ENGINE_PINS.items()):
            raw = git_file(ENGINE_ROOT + name)
            need(sha256(raw).hexdigest() == pin, "Exact engine pin")
            path = Path(folder) / name
            path.write_bytes(raw)
            spec = importlib.util.spec_from_file_location("clean_exchange_engine_" + str(i), path)
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
            row = {"profile": profile, "mass": mass(profile), "moment": bounds(base), "limits": {}}
            for rank in (1, 2):
                unit = moments({rank: 1})
                n = [((1 - hi) / uhi).__floor__() for (lo, hi), (ulo, uhi) in zip(base, unit)]
                need(n[0] == n[1] and n[0] >= 0, "Both engines give the same allowance")
                yes = moments(profile + Counter({rank: n[0]}))
                no = moments(profile + Counter({rank: n[0] + 1}))
                need(all(hi < 1 for lo, hi in yes) and all(lo > 1 for lo, hi in no), "Strict pass and next failure")
                row["limits"][str(rank)] = {"children": n[0], "rank_mass": rank * n[0],
                                             "accepted": bounds(yes), "next": bounds(no)}
            return row

        for name, i_count in (("three_Q", 0), ("one_I_two_Q", 1)):
            profile = Counter({r: (3 - i_count) * n for r, n in Q_PROFILE.items()})
            profile.update({r: i_count * n for r, n in I_PROFILE.items()})
            profile = +profile
            need(mass(profile) == 5376 + 16 * i_count, "Complete three-call native mass")
            row = allowance(profile)
            row["hypothetical_H1_cleanup"] = {
                str(n): allowance(profile + Counter({1: n})) for n in (112, 128, 144)
            }
            row["three_call_scalar_subtotal"] = 25800
            row["three_call_map_bound"] = 9792 - 48 * i_count
            row["source_scope"] = "The local words are supplied. Their routed three-call composition and terminal are not admitted."
            results[name] = row

    receipt = {
        "status": "PASS_SOURCE_COUNTS_AND_EXACT_CONDITIONAL_BUDGET",
        "source_pins": PINS, "gzip_pin_convention": "SHA256 after decompression",
        "engine_commit": COMMIT, "engine_pins": ENGINE_PINS,
        "selected_certificate": selected["certificate"], "selected_result_sha256": SELECTED_PIN,
        "assembly_sha256": ASSEMBLY_PIN, "historical_selected_b": str(B),
        "dimension": D, "productive_width": W, "calls": 3, "idle_profile": {},
        "literal": literal, "results": results,
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "scope": "Native arithmetic only. The 112,128,144 H1 cleanup costs are hypotheses. No caller, terminal, host, precision, or current-frontier claim.",
    }
    (HERE / "BUDGET.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    for name, row in results.items():
        print(name, "base", {r: v["children"] for r, v in row["limits"].items()})
        print(name, "cleanup", {n: {r: v["children"] for r, v in c["limits"].items()}
                               for n, c in row["hypothetical_H1_cleanup"].items()})


if __name__ == "__main__":
    main()
