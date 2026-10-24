#!/usr/bin/env python3
"""Bounded exact replay of the coded native interface. Apache-2.0."""
from pathlib import Path
from hashlib import sha256
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    for row in json.loads((HERE / "ORIGINS.json").read_text()):
        need(sha256((HERE / row["path"]).read_bytes()).hexdigest() == row["sha256"],
             "Changed frozen source: " + row["path"])
    results = {}
    for name, receipt in (("normalizers", "NORMALIZERS.json"),
                          ("gauge", "GAUGE.json"),
                          ("terminal", "TERMINAL.json"),
                          ("independent", "INDEPENDENT.json")):
        spec = importlib.util.spec_from_file_location("coded_caller_" + name, HERE / (name + ".py"))
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        result = module.run(HERE / "CONTROLLER.json") if name == "gauge" else module.run()
        result = json.loads(json.dumps(result))
        need(result == json.loads((HERE / receipt).read_text()), "Changed mathematical receipt: " + receipt)
        results[name] = result.get("status", "PASS_" + name.upper() + "_RECEIPT")
    print(json.dumps({"status": "PASS_CODED_NATIVE_INTERFACE_AND_CALLER_GATES",
                      "checks": results, "complete_gaussian_supplier": False, "complete_typed_rational_caller": True, "new_kappa": None}, sort_keys=True))


if __name__ == "__main__":
    main()
