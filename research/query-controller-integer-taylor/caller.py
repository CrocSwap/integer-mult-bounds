"""Invoke the entire retained caller with one exact exponential substitution."""

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/query-thinned-controllers"
ENGINE = ROOT / "research/kappa-rebuild/architecture/mixed_target_probe.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError("source module loader")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def hash_endpoints(digest, x, result):
    """Length-prefix binary integers without changing Python's decimal limits."""
    for value in (x, *result):
        for integer in (value.numerator, value.denominator):
            raw = abs(integer).to_bytes(max(1, (abs(integer).bit_length() + 7) // 8), "big")
            digest.update(bytes([integer < 0]))
            digest.update(len(raw).to_bytes(4, "big"))
            digest.update(raw)


def run(mode, capture=False):
    if mode not in ("baseline", "candidate"):
        raise ValueError("unsupported arithmetic mode")
    controller = load(SOURCE / "controller.py", "controller")
    verifier = load(SOURCE / "verify.py", "retained_query_verifier")
    replacement = load(HERE / "integer_exp.py", "query_integer_exp").exp_interval
    original_load = controller.load
    records = []
    digest = sha256()
    work = {"exponential_calls": 0, "taylor_steps": 0}

    def instrumented(path, name):
        module = original_load(path, name)
        if path == ENGINE:
            operation = replacement if mode == "candidate" else module.exp_interval

            def exponential(x):
                work["exponential_calls"] += 1
                work["taylor_steps"] += 48
                if work["exponential_calls"] > 128:
                    raise ValueError("exponential call capacity")
                result = operation(x)
                hash_endpoints(digest, x, result)
                if capture:
                    records.append((x, result))
                return result

            module.exp_interval = exponential
        return module

    controller.load = instrumented
    result = verifier.run()
    controller.need(result == json.loads((SOURCE / "RESULT.json").read_text()), "Complete scientific receipt")
    payload = {"result": result, "work": work, "mode": mode, "trace_sha256": digest.hexdigest()}
    return (payload, records) if capture else payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("baseline", "candidate"))
    args = parser.parse_args()
    print(json.dumps(run(args.mode), sort_keys=True, separators=(",", ":")))
