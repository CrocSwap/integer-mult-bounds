"""Cold entry point for the physical Gaussian compression checks."""
import argparse
import importlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gaussian_sources import opened, require


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", required=True)
    args = parser.parse_args()
    groups = {"bounds": ("budget", "production"), "arithmetic": ("setup", "convolution"),
              "numerical": ("exponentials", "interior", "axis")}
    require(args.suite in (*groups, "setup", "convolution", "exponentials", "interior", "axis",
                          "boundary", "window", "consumer", "production", "ownership", "sources", "budget"),
            "registered Gaussian suite")
    with opened():
        for suite in groups.get(args.suite, (args.suite,)):
            name = "gaussian_check_" + suite
            module = importlib.import_module(name)
            require(Path(module.__file__).resolve() == Path(__file__).resolve().parent / (name + ".py"),
                    "package-local Gaussian checker")
            result = module.run()
            print(json.dumps({"status": "PASS_PHYSICAL_GAUSSIAN_CORE", "suite": suite,
                              "evidence": result}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
