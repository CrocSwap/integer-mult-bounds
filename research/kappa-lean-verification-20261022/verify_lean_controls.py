"""Bounded rejection controls for verify_lean.py; does not compile Lean.

Apache-2.0. Substantial OpenAI Codex assistance; prepared for Cao Yifan.
Temporary mutations never overwrite the actual source, proof or receipt files.
"""
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    spec = importlib.util.spec_from_file_location("tested_lean_wrapper", HERE / "verify_lean.py")
    wrapper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wrapper)
    math_path = HERE / "MATH-LEAN-VERIFICATION.json"
    original = wrapper.read(math_path)
    runtime = {"lean_version": original["lean_version"]}
    valid, _ = wrapper.load_evidence([math_path.name], runtime)
    assert len(valid) == 4
    arithmetic_path = ROOT / "research/kappa-interface-round2-20261022/ARITHMETIC.json"
    native_path = ROOT / "research/warp-interface-20261022/NATIVE-VALIDATION.json"
    native = wrapper.read(native_path)
    actual_binding = wrapper.numerical_binding(wrapper.read(arithmetic_path), native)
    results = []

    def rejected(name, operation, expected_reason):
        try:
            operation()
        except ValueError as exc:
            reason = str(exc)
            assert expected_reason in reason, (name, reason)
            results.append({"name": name, "rejected": True, "reason": reason})
        else:
            raise AssertionError(name + " was accepted")

    base = HERE / ".lake"
    base.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="wrapper-controls-", dir=base) as directory:
        temp = Path(directory).resolve()
        assert temp.is_relative_to(base.resolve())
        for field in ("source_sha256", "olean_sha256", "log_sha256"):
            altered = wrapper.read(math_path)
            altered["modules"][0][field] = "0" * 64
            path = temp / (field + ".json")
            path.write_text(json.dumps(altered), encoding="utf-8")
            kind = field.removesuffix("_sha256")
            rejected("stale_" + kind + "_hash",
                lambda p=path: wrapper.load_evidence([str(p.relative_to(HERE))], runtime),
                "Reused " + kind + " hash differs")

        log = temp / "axioms.log"
        log.write_text("'X' depends on axioms: [propext, sorryAx]\n", encoding="utf-8")
        rejected("unexpected_axiom", lambda: wrapper.parse_axioms(log, ["X"]), "Sorry dependency")
        log.write_text("'X' depends on axioms: [propext]\n", encoding="utf-8")
        rejected("missing_axiom_report", lambda: wrapper.parse_axioms(log, ["X", "Y"]),
                 "Missing/extra axiom reports")

        source = temp / "forbidden.lean"
        source.write_text("axiom forged : False\n", encoding="utf-8")
        rejected("custom_axiom_source", lambda: wrapper.audit_source(source), "Forbidden proof shortcut")
        source.write_text("example : True := by native_decide\n", encoding="utf-8")
        rejected("native_decide_source", lambda: wrapper.audit_source(source), "Forbidden proof shortcut")

        altered = wrapper.read(math_path)
        altered["modules"][0]["argv"].insert(1, "-Ddebug.skipKernelTC=true")
        path = temp / "compiler-bypass.json"
        path.write_text(json.dumps(altered), encoding="utf-8")
        rejected("CLI_kernel_bypass",
            lambda: wrapper.load_evidence([str(path.relative_to(HERE))], runtime),
            "compiler/kernel trust bypass")

        arithmetic = wrapper.read(arithmetic_path)
        arithmetic["strictification"]["tested"] = "1/1000"
        rejected("tested_saving_drift", lambda: wrapper.numerical_binding(arithmetic, native),
                 "Exact tested saving drifted")
        arithmetic = wrapper.read(arithmetic_path)
        arithmetic["kappa"] = "1/1000"
        rejected("claimed_saving_drift", lambda: wrapper.numerical_binding(arithmetic, native),
                 "Exact claimed saving drifted")
        arithmetic = wrapper.read(arithmetic_path)
        arithmetic["paid"]["1"] += 1
        rejected("paid_JSON_profile_drift", lambda: wrapper.numerical_binding(arithmetic, native),
                 "Complete target/paid JSON differs")

        arithmetic = wrapper.read(arithmetic_path)
        original_strip = wrapper.strip_lean
        needle = "504 * (4 : ℝ)"
        assert needle in (HERE / "NumericalMoments.lean").read_text(encoding="utf-8")
        def changed_coefficient(text):
            return original_strip(text).replace(needle, "505 * (4 : ℝ)", 1)
        wrapper.strip_lean = changed_coefficient
        try:
            rejected("literal_Lean_coefficient_drift", lambda: wrapper.numerical_binding(arithmetic, native),
                     "Lean numerical coefficients differ")
        finally:
            wrapper.strip_lean = original_strip

    assert len(results) == 12
    bound = [Path(__file__), HERE / "verify_lean.py", math_path, arithmetic_path, native_path,
             HERE / "NumericalMoments.lean", HERE / "numerical_generate.py",
             ROOT / "research/kappa-interface-round2-20261022/price_profile.py"]
    receipt = {"schema_version": 1, "status": "PASS_12_LEAN_WRAPPER_REJECTION_CONTROLS",
        "controls": results, "valid_math_module_rows": len(valid),
        "valid_math_axiom_reports": sum(len(r["axioms"]) for r in valid.values()),
        "actual_numerical_binding": actual_binding,
        "source_sha256": {p.resolve().relative_to(ROOT).as_posix(): wrapper.digest(p) for p in bound},
        "scope": "Bounded Python verifier rejection controls with valid baseline checks. No Lean compilation, native semantic replay, or new theorem verification."}
    (HERE / "LEAN-WRAPPER-CONTROLS.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(receipt["status"], len(results), "controls", flush=True)


if __name__ == "__main__":
    main()
