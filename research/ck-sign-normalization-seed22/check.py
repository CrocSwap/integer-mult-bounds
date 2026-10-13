"""One-command exact primary and independently implemented CK verification.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location("ck_package_" + name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    primary = load("verify")
    independent = load("check_independent")
    actual = primary.verify()
    primary.require(primary.canonical(actual) == primary.canonical(primary.read(HERE / "EXPECTED.json")),
                    "primary receipt differs")
    second = independent.verify()
    primary.require(primary.canonical(second) == primary.canonical(primary.read(HERE / "INDEPENDENT.json")),
                    "independent receipt differs")
    for direction, row in actual["programs"].items():
        other = second["programs"][direction]
        for key in ("baseline_real_primitives", "candidate_real_primitives", "scalar_macros"):
            primary.require(row[key] == other[key], "independent count differs: " + key)
        primary.require(row["runs"] == other["scalar_runs"], "run coverage differs")
        primary.require(row["candidate_primitive_sha256"] == other["primitive_word_sha256"],
                        "independent primitive stream differs")
    print("PASS_CK_SIGN_PACKAGE runs=2219+2219 columns=725 saved=224/224 kappa=unchanged")


if __name__ == "__main__":
    main()
