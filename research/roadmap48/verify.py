"""One-command local correctness, direct pricing and regression tests."""
import argparse
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import subprocess
import sys

import experiment as E
import cost_model as MODEL
import optimizations as OPT


def content_hash(path):
    raw = path.read_bytes()
    return E.digest(gzip.decompress(raw) if path.suffix == ".gz" else raw.replace(b"\r\n", b"\n"))


def dependency_bindings():
    text = [
        "research/gauge44-frames-x/independent/audit_local.py",
        "research/gauge44-frames-x/independent/price_profile.py",
        "research/gauge44-frames-x/construction/promo/build_promotion.py",
        "research/gauge44-frames-x/data/UPSTREAM-PINS.json",
        "research/gauge44-frames-x/inputs/PR589-EXPECTED.json",
        *["research/complex-k492-owner-repair/vendor/multicold/engines/"+name+".py"
          for name in ("moment", "base_two_moment", "outer")],
    ]
    immutable = [E.ARCHIVE.relative_to(E.ROOT).as_posix(),
        "research/gauge44-frames-x/data/OWNERS.json.gz",
        "research/community-k492-audit/pr622/replay/baseline558/complex-global/base/split-centres/CANONICAL-WORD.json.gz"]
    return ({name: content_hash(E.ROOT / name) for name in text},
            {name: E.digest((E.ROOT / name).read_bytes()) for name in immutable})


def check_committed(receipt, committed):
    """Bind every regenerated payload and source; timestamps are diagnostic."""
    expected = json.loads((committed / "VERIFICATION.json").read_bytes())
    E.require(receipt["sources"] == expected["sources"], "committed source bindings differ")
    E.require(receipt["immutable_inputs"] == expected["immutable_inputs"], "committed immutable input bindings differ")
    E.require(receipt["artifacts"] == expected["artifacts"], "regenerated artifact bindings differ")
    names = {p.name for p in committed.iterdir() if p.name.endswith((".json", ".json.gz"))
             and p.name != "VERIFICATION.json"}
    E.require(names == set(expected["artifacts"]), "committed artifact inventory differs")
    for name, digest in expected["artifacts"].items():
        E.require(content_hash(committed / name) == digest, "committed payload changed: "+name)
    for key in ("status", "local_audit", "tests", "actual_kappa", "combined_kappa",
                "hypothetical_kappa", "output_content_sha256", "artifact_hash_policy", "source_hash_policy"):
        E.require(receipt[key] == expected[key], "verification field changed: "+key)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=E.ROOT / "build/roadmap48")
    parser.add_argument("--check-committed", action="store_true", help="Compare with every retained public payload and source binding")
    args = parser.parse_args()
    E.require(__debug__, "Use normal Python, not -O")
    out = args.out.resolve()
    committed = E.HERE / "artifacts"
    E.require(not args.check_committed or out != committed.resolve(), "replay output must differ from retained artifacts")
    E.run(out)
    result = json.loads((out / "RESULT.json").read_bytes())
    direct = MODEL.evaluate(result["retained_owner_price"]["profile"])
    E.require(direct["outer"]["kappa"] == result["retained_owner_price"]["outer"]["kappa"], "two direct cost drivers disagree")
    E.dump(out / "DIRECT-COST.json", direct)
    # These are explicitly changed-parameter models, not generated templates.
    E.dump(out / "PARAMETER-SCENARIOS.json", dict(
        status="DECLARED_PARAMETER_MODELS_ONLY",
        m74_fixed_profile=MODEL.evaluate(direct["profile"], m=74),
        capacity_one_unit_larger=MODEL.evaluate(direct["profile"], live=E.Q(7168)+E.Q(1,73)),
        roadmap_large_volume_nominal=MODEL.evaluate(E.ROADMAP_PROFILE, live=E.Q(8192)),
        scope="Changed geometry is a model hypothesis; no owner/phase/template realization of these alternatives is claimed."))
    optimized = OPT.run(out)
    test = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests",
                           "-p", "test_roadmap48.py", "-v"], cwd=E.ROOT, capture_output=True,
                          text=True, encoding="utf-8")
    (out / "TESTS.log").write_text(test.stdout+test.stderr, encoding="utf-8")
    E.require(test.returncode == 0, "Regression tests failed:\n"+test.stdout+test.stderr)
    print(test.stderr.strip(), flush=True)
    receipt = dict(status="PASS_DIRECT_CONSTRUCTION_VERIFICATION", generated_utc=datetime.now(timezone.utc).isoformat(),
        local_audit="PASS", tests="PASS",
        actual_kappa=direct["outer"]["kappa_decimal"],
        combined_kappa=optimized["combined_price"]["outer"]["kappa_decimal"],
        hypothetical_kappa=result["roadmap_hypothetical_price"]["outer"]["kappa_decimal"],
        output_content_sha256=result["output_word_content_sha256"],
        artifacts={p.name: content_hash(p)
                   for p in sorted(out.iterdir()) if p.is_file() and p.name != "VERIFICATION.json"
                   and (p.name.endswith(".json") or p.name.endswith(".json.gz"))},
        artifact_hash_policy="Compressed JSON hashes cover decompressed bytes; text hashes cover LF-normalized bytes.",
        sources={p.relative_to(E.ROOT).as_posix(): content_hash(p)
                 for p in sorted(E.HERE.rglob("*")) if p.is_file() and "__pycache__" not in p.parts
                 and "artifacts" not in p.relative_to(E.HERE).parts})
    receipt["sources"]["tests/test_roadmap48.py"] = content_hash(E.ROOT / "tests/test_roadmap48.py")
    dependencies, immutable = dependency_bindings()
    receipt["sources"].update(dependencies)
    receipt["immutable_inputs"] = immutable
    receipt["source_hash_policy"] = "Source text hashes cover LF-normalized bytes; immutable input archives use exact file bytes."
    if args.check_committed:
        check_committed(receipt, committed)
        print("PASS every retained payload and source binding", flush=True)
    E.dump(out / "VERIFICATION.json", receipt)
    print(receipt["status"], "actual kappa", receipt["actual_kappa"], flush=True)


if __name__ == "__main__":
    main()
