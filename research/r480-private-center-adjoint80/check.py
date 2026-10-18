"""One command for the two independently implemented complete matrix checks."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location("r480_center_" + name, HERE / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


if __name__ == "__main__":
    primary, forward = load("verify"), load("forward_check")
    result = primary.verify()
    primary.require(primary.canonical(result) == primary.canonical(primary.read(HERE / "CERTIFICATE.json")),
                    "certificate differs")
    primary.require(forward.verify() == 40, "forward omission coverage differs")
    private_faults = sum(p["classification"].get("private_input_only", 0) for p in result["programs"].values())
    primary.require(private_faults == 8, "private-only fault census differs")
    print("PASS_R480_PRIVATE_CENTER_PACKAGE coordinates=712 matrices=42 omissions=40 private_only=8 no_new_kappa")
