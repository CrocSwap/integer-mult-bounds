#!/usr/bin/env python3
"""Record the local import boundary of the nine replay tasks."""

import argparse
import importlib.util
import json
from pathlib import Path
import runpy
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    package = args.package.resolve()
    runtime = Path(sys.base_prefix).resolve()
    spec = importlib.util.spec_from_file_location("review_runner", package/"replay.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    opened, forbidden = [], []

    def audit(event, values):
        if event == "open" and isinstance(values[0], str):
            opened.append(Path(values[0]).resolve())
        if event in ("subprocess.Popen", "socket.connect", "os.system"):
            forbidden.append(event)
            raise RuntimeError("Unexpected external action during import: " + event)

    sys.addaudithook(audit)
    checks = []
    for name, script, _, _ in runner.tasks():
        runpy.run_path(str(package/"frozen"/script), run_name="publication_import_review")
        checks.append(name)
    outside = [str(p) for p in set(opened) if not p.is_relative_to(package) and not p.is_relative_to(runtime)]
    if outside or forbidden:
        raise ValueError({"unexpected_paths": outside, "external_actions": forbidden})
    modules = sorted({str(Path(module.__file__).resolve()) for module in sys.modules.values()
                      if getattr(module, "__file__", None) and
                      Path(module.__file__).resolve().is_relative_to(package)})
    result = {
        "status": "PASS_IMPORT_BOUNDARY", "scripts": checks,
        "python_runtime": str(runtime), "package_modules": modules,
        "source_reads": sorted(str(p) for p in set(opened) if p.is_relative_to(package)),
        "external_process_or_network_events": forbidden,
        "reads_outside_package_and_python_runtime": outside,
        "scope": "Top-level import closure of all nine replay tasks. The separate fresh replay ran each main path in its copied frozen tree.",
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(result["status"])


if __name__ == "__main__":
    main()
