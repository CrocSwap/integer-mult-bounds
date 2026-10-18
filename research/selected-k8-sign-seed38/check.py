"""One offline command: two full exact engines and actual-word controls.

Scratch-net with substantial OpenAI Codex assistance. Apache-2.0.
"""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location("selected_k8_" + name, HERE / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


if __name__ == "__main__":
    primary, independent, controls = load("verify"), load("independent"), load("controls")
    result = primary.verify()
    primary.require(primary.canonical(result) == primary.canonical(primary.read(HERE / "EXPECTED.json")),
                    "primary receipt differs")
    second = independent.verify()
    primary.require(primary.canonical(result) == primary.canonical(second), "engines disagree")
    adverse = controls.run(primary, independent)
    primary.require(adverse["actual_run_mutants_rejected"] == 116 and adverse["toy_mutants_rejected"] == 4,
                    "control coverage differs")
    print("PASS_SELECTED_K8_SIGN_PACKAGE runs=2166+2166 columns=713 saved=408/408 controls=120 no_new_kappa")
