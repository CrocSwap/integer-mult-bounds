"""Cold entry point for exact FFT-word checks."""
import argparse
import importlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fft_word_sources import opened, require


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", required=True)
    args = parser.parse_args()
    require(args.suite in ("fft", "base", "codec", "plan", "failures", "sources", "budget"),
            "registered FFT-word suite")
    with opened():
        name = "fft_word_check_" + args.suite
        module = importlib.import_module(name)
        require(Path(module.__file__).resolve() == Path(__file__).resolve().parent / (name + ".py"),
                "package-local FFT-word checker")
        result = module.run()
    print(json.dumps({"status": "PASS_PHYSICAL_FFT_WORD", "suite": args.suite,
                      "evidence": result}, sort_keys=True))


if __name__ == "__main__":
    main()
