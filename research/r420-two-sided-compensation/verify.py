"""Exact finite checker; prepared with substantial OpenAI Codex assistance.
Apache-2.0. Does not certify a changed recursive invoice or a new kappa.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
from construct import SOURCE, build, search


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def execute(gates, n=660):
    values = [1 << i for i in range(n)]
    for frame, destination, sources in gates:
        need(frame == 0, "D gate outside frame zero")
        need(120 <= destination < n and sources and len(set(sources)) == len(sources), "invalid D destination/sources")
        need(all(120 <= s < n and s != destination for s in sources), "invalid D operand")
        for source in sources:
            values[destination] ^= values[source]
    return values


def semantic_d(baseline, candidate):
    need(set(baseline) == set(candidate), "word keys changed")
    need(all(candidate[k] == baseline[k] for k in baseline if k != "D"), "field outside D changed")
    need(execute(candidate["D"]) == execute(baseline["D"]), "D endpoint differs on arbitrary inputs")


def count(word):
    return sum(len(g[2]) for sec in ("D", "A", "B", "C") for g in word[sec]) + sum(map(len, word["scatter"]))


def reject(action, name):
    try:
        action()
    except ValueError:
        return name
    raise ValueError("negative control was accepted: " + name)


def evaluate(outdir):
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for path, expected in pins["files_sha256"].items():
        need(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, "source pin: " + path)
    baseline = json.load(gzip.open(SOURCE, "rt"))
    need(digest(baseline) == pins["word_canonical_sha256"], "source word semantic pin")
    recipe = json.loads((HERE / "recipe.json").read_text())
    need(recipe == search(baseline), "frozen seed-3 nomination differs")
    candidate = build(baseline, recipe)
    semantic_d(baseline, candidate)
    spec = importlib.util.spec_from_file_location("predecessor_xcheck", ROOT / "research/e8-bit-r420/code/xcheck.py")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    W, labels, full, H, C, info = checker.check(baseline)
    need(all(H.values()) and all(C.values()), "baseline interface rejected")
    # Frames/labels are identical, so the exact geometry computed above is reusable.
    W.w = candidate
    candidate_full = W.full()
    candidate_H, candidate_C, _ = W.interface()
    need(not candidate_H["H2_D_frame0_targets_from_helpers"], "expected original H2 syntax rejection missing")
    need(not candidate_C["K_equals_D"], "expected original literal K extractor rejection missing")
    need(all(v for k,v in candidate_H.items() if k != "H2_D_frame0_targets_from_helpers"), "other interface condition changed")
    need(all(v for k,v in candidate_C.items() if k != "K_equals_D"), "other interface conclusion changed")
    controls = []
    hp, tp = len(recipe["helper_pairs"]), len(recipe["target_pairs"])
    for name, index in (("missing_helper_restoration", len(candidate["D"])-1),
                        ("missing_target_preparation", hp),
                        ("missing_target_restoration", len(candidate["D"])-hp-1)):
        bad = copy.deepcopy(candidate)
        del bad["D"][index]
        controls.append(reject(lambda: semantic_d(baseline, bad), name))
    bad = copy.deepcopy(candidate)
    bad["D"][hp+tp][2].pop()
    controls.append(reject(lambda: semantic_d(baseline, bad), "missing_feed_term"))
    bad = copy.deepcopy(candidate)
    bad["D"][0][0] = 1
    controls.append(reject(lambda: semantic_d(baseline, bad), "unpaid_nonzero_frame"))
    bad = copy.deepcopy(candidate)
    bad["ret"][0] = bad["ret"][1]
    controls.append(reject(lambda: semantic_d(baseline, bad), "changed_retained_total"))
    bad_recipe = copy.deepcopy(recipe)
    bad_recipe["transformed_rows"][0].pop()
    controls.append(reject(lambda: semantic_d(baseline, build(baseline, bad_recipe)), "corrupt_transformed_matrix"))
    # An F2-neutral gate pair is legal, but must pay two additional additions.
    neutral = copy.deepcopy(candidate)
    neutral["D"] = [[0,240,[241]], [0,240,[241]]] + neutral["D"]
    semantic_d(baseline, neutral)
    need(count(neutral) == count(candidate)+2, "neutral pair not charged")
    controls.append(reject(lambda: need(count(neutral) == count(candidate), "underpriced neutral pair"), "underpriced_neutral_pair"))
    outdir.mkdir(parents=True, exist_ok=True)
    candidate_file = outdir / "candidate.json"
    candidate_file.write_text(json.dumps(candidate, separators=(",", ":")) + "\n")
    report = dict(status="PASS_FINITE_TWO_SIDED_D", columns=660, labels=labels,
                  baseline_word_sha256=digest(baseline), candidate_word_sha256=digest(candidate),
                  recipe_sha256=digest(recipe),
                  helper_pairs=hp, target_pairs=tp,
                  baseline_D_adds=sum(len(g[2]) for g in baseline["D"]),
                  helper_only_D_adds=recipe["helper_only_adds"],
                  candidate_D_adds=sum(len(g[2]) for g in candidate["D"]),
                  baseline_native_adds=count(baseline), candidate_native_adds=count(candidate),
                  saved_adds=count(baseline)-count(candidate), negative_controls=controls,
                  unchanged_interface=[k for k,v in candidate_H.items() if v],
                  original_syntax_rejections=["H2_D_frame0_targets_from_helpers", "K_equals_D"],
                  scope="Finite native circuit and semantic frame-zero D extension; no new kappa or hosted invoice")
    return report, candidate_file


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--write-certificate", action="store_true", help="explicitly regenerate this package's certificate")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="r420-two-sided-") as tmp:
        out = args.output or Path(tmp)
        report, candidate = evaluate(out)
        independent = subprocess.run([sys.executable, "-B", str(HERE / "audit_independent.py"),
                        "--baseline", str(SOURCE), "--recipe", str(HERE / "recipe.json"),
                        "--candidate", str(candidate), "--output", str(out / "independent.json")],
                        capture_output=True, text=True)
        need(independent.returncode == 0, "independent audit failed: " + independent.stdout + independent.stderr)
        native = subprocess.run([sys.executable, "-B", str(HERE / "native.py"), str(candidate),
                                 "--out", str(out / "native")], capture_output=True, text=True)
        need(native.returncode == 0, "native audit failed: " + native.stdout + native.stderr)
        native_report = json.loads((out / "native/RESULT.json").read_text())
        # Portable proof-relevant fields only; compiler paths and gzip bytes are execution metadata.
        report["native"] = {name: {k:v for k,v in native_report[name].items() if k != "input_sha256"}
                            for name in ("baseline", "candidate")}
        report["native"]["comparison"] = native_report["comparison"]
        report["native"]["missing_D_negative_control"] = native_report["native_missing_D_negative_control"]
        certificate = HERE / "CERTIFICATE.json"
        if args.write_certificate:
            certificate.write_text(json.dumps(report, indent=2) + "\n")
        else:
            need(report == json.loads(certificate.read_text()), "certificate does not match exact recomputation")
        print("Independent set audit: PASS; native Python audit: PASS; official C++: " + native_report["official_cpp"]["status"])
        print("PASS_R420_TWO_SIDED D={baseline_D_adds}->{candidate_D_adds} "
              "native_ADDs={baseline_native_adds}->{candidate_native_adds} "
              "saved={saved_adds} columns=660 no_new_kappa".format(**report))


if __name__ == "__main__":
    main()
