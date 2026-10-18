"""Mathematical rejection, isolated optimized replay and regeneration checks."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("weighted_checker", ROOT / "verify.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
data = json.loads((ROOT / "CERTIFICATE.json").read_text(encoding="utf-8"))


def reject(function, label):
    try:
        function()
    except (ValueError, KeyError, TypeError):
        return label
    raise ValueError(f"control accepted: {label}")


def main():
    controls = []
    original = data["witnesses"]["A1"]
    # Every query is individually necessary to this literal minimum word.
    for index in range(14):
        bad = copy.deepcopy(original)
        bad.pop(index)
        controls.append(reject(lambda: checker.need(checker.query_coefficients(bad)[0] == checker.M, "deleted query"), f"delete_query_{index}"))
    for index in range(14):
        bad = copy.deepcopy(original)
        bad[index][2] *= -1
        controls.append(reject(lambda: checker.need(checker.query_coefficients(bad)[0] == checker.M, "flipped query"), f"flip_query_{index}"))
    for label, mutate in (
        ("missing_witness", lambda d: d["witnesses"].pop("A2")),
        ("wrong_factor", lambda d: d["factors"]["B0"].reverse()),
        ("aliased_leaf", lambda d: d["leaves"]["A1"][0].__setitem__(2, d["leaves"]["A1"][0][1])),
        ("unpaid_restoration", lambda d: d["leaves"]["A1"].pop()),
        ("wrong_repeated_operator", lambda d: d["witnesses"].__setitem__("A1", d["witnesses"]["B0"])),
        ("false_census", lambda d: d["census"]["B0"].__setitem__("feasible", 545)),
        ("wrong_fixture", lambda d: d.__setitem__("chosen", "B0")),
    ):
        bad = copy.deepcopy(data)
        mutate(bad)
        controls.append(reject(lambda: checker.verify(bad, exhaustive=(label == "false_census")), label))
    for prices in ([0, 1, 1, 1, 1, 1], [-1, 1, 1, 1, 1, 1], [1, 2]):
        controls.append(reject(lambda: checker.select_word(data, prices), f"invalid_prices_{prices}"))
    # Positive control: B0-repeat is mathematically valid but not optimal here.
    prices = [16, 28, 40, 52, 4, 10]
    _, counts = checker.query_coefficients(data["witnesses"]["B0"])
    bill = sum(counts[name] * c for name, c in zip(checker.NAMES, prices))
    checker.need(bill == 332 and checker.select_word(data, prices)["minimum"] == "308", "valid nonoptimal comparator")
    # Nonlinear readout restores z yet depends on its incoming dirt.
    def nonlinear(z):
        y = 0
        z += 1
        y += z * z
        z -= 1
        y -= z * z
        return z, y
    checker.need(nonlinear(0) == (0, 1) and nonlinear(2) == (2, 5), "nonlinear boundary")
    controls += ["valid_nonoptimal_comparator", "nonlinear_readout_boundary"]
    literal = data["leaves"]["A1"]
    bad = copy.deepcopy(literal)
    bad[0][0], bad[1][0] = bad[1][0], bad[0][0]
    controls.append(reject(lambda: checker.need(checker.execute(bad) == checker.desired(checker.M, data["factors"]), "ordered factors changed"), "noncommuting_factor_order"))
    for label, indices in (("scratch_dirt_erased", (7, 8, 9)), ("initial_output_erased", (3, 4, 5))):
        initial = checker.identity(10)
        for r in indices:
            initial[r] = {}
        controls.append(reject(lambda: checker.need(checker.execute(literal, initial) == checker.desired(checker.M, data["factors"]), "initial dirt lost"), label))
    with tempfile.TemporaryDirectory(prefix="weighted-connector-") as directory:
        relocated = Path(directory) / "package"
        shutil.copytree(ROOT, relocated, ignore=shutil.ignore_patterns("__pycache__"))
        subprocess.run([sys.executable, "-I", "-O", "-B", str(relocated / "verify.py")], check=True, capture_output=True)
        initial = (relocated / "CERTIFICATE.json").read_bytes()
        subprocess.run([sys.executable, "-I", "-B", str(relocated / "generate.py")], check=True, capture_output=True)
        checker.need((relocated / "CERTIFICATE.json").read_bytes() == initial, "deterministic regeneration")
        # Whole-package corruption checks happen in a separate optimized process.
        for filename, change in (
            ("CERTIFICATE.json", lambda p: p.write_text('{"format":"corrupt"}', encoding="utf-8")),
            ("EXPECTED.json", lambda p: p.write_text('{}', encoding="utf-8")),
            ("sources/PR944-README.md", lambda p: p.write_bytes(p.read_bytes() + b"corruption\n")),
            ("SOURCES.json", lambda p: p.write_text(json.dumps({"base": data["base"], "retained": {}}), encoding="utf-8")),
        ):
            path = relocated / filename
            before = path.read_bytes()
            change(path)
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(relocated / "verify.py")], capture_output=True)
            checker.need(result.returncode != 0, f"optimized corruption accepted: {filename}")
            path.write_bytes(before)
            controls.append(f"optimized_corruption_{filename}")
    receipt = {"status": "PASS_WEIGHTED_SIGNED_PACKAGE", "controls": controls,
               "count": len(controls), "optimized_relocation": "PASS", "deterministic_regeneration": "PASS"}
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
