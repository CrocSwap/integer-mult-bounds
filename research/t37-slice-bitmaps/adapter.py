#!/usr/bin/env python3
"""Run the unchanged T37 wrapper with an optional exact occupancy kernel."""
import argparse
from contextlib import contextmanager, redirect_stdout
import importlib.util
import json
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WRAPPER = "research/complex-t37-owners/independent/check_t37.py"
C = runpy.run_path(str(HERE / "common.py"))


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


@contextmanager
def core_hook(engine, capture):
    original = importlib.util.spec_from_file_location
    seen = []

    def spec_hook(name, *args, **kwargs):
        spec = original(name, *args, **kwargs)
        if name == "independent_t37":
            execute = spec.loader.exec_module

            def run_core(core):
                execute(core)
                seen.append(core)
                if engine == "bitmap":
                    capture["implementation"] = module(HERE / "kernel.py", "t37_bitmap_kernel").install(core)
                if capture.get("retain_context"):
                    check = core.check_roles

                    def retained(context, roles):
                        if "context" not in capture:
                            capture.update(context=context, roles=roles, core=core, reference_check=check)
                        return check(context, roles)
                    core.check_roles = retained
            spec.loader.exec_module = run_core
        return spec
    importlib.util.spec_from_file_location = spec_hook
    try:
        yield
        if len(seen) != 1:
            raise ValueError("exactly one pinned independent checker load required")
    finally:
        importlib.util.spec_from_file_location = original


def run(inputs, output, engine="bitmap", root=ROOT, retain_context=False):
    if engine not in ("reference", "bitmap"):
        raise ValueError("unknown engine")
    output, root = Path(output).resolve(), Path(root).resolve()
    manifest = C["pins"](root)
    if output.exists():
        raise ValueError("new output path required")
    output.mkdir(parents=True)
    inputs = Path(inputs).resolve() if inputs is not None else C["materialize"](root, output / "inputs", manifest)
    C["input_pins"](inputs, manifest)
    wrapper = module(root / WRAPPER, "pinned_t37_wrapper")
    arguments = [str(root / WRAPPER), "--word", str(inputs / "word.json.gz"),
                 "--local-replay", str(inputs / "local-replay.json"),
                 "--baseline-base", str(inputs / "baseline"), "--out", str(output / "receipt.json")]
    capture = {"retain_context": retain_context}
    saved = sys.argv
    try:
        sys.argv = arguments
        with (output / "audit.log").open("x") as log, redirect_stdout(log), core_hook(engine, capture):
            wrapper.main()
    finally:
        sys.argv = saved
    result = C["load"](output / "receipt.json")
    normalized = C["normalize"](result, manifest)
    expected = C["normalize"](C["load"](root / manifest["frozen_receipt"]), manifest)
    C["same"](normalized, expected, "complete receipt differs from maintainer replay")
    C["write"](output / "normalized-receipt.json", normalized)
    C["write"](output / "adapter.json", {"engine": engine, "implementation": manifest["implementation"],
                                        "patch": capture.get("implementation"), "complete_receipt_match": True})
    return normalized, capture


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--engine", choices=("reference", "bitmap"), default="bitmap")
    args = parser.parse_args()
    result, capture = run(args.inputs, args.output, args.engine)
    try:
        import resource
        usage = resource.getrusage(resource.RUSAGE_SELF)
        C["write"](args.output / "usage.json", {"peak_rss_native_units": usage.ru_maxrss,
                                               "platform": sys.platform,
                                               "cpu_seconds": usage.ru_utime + usage.ru_stime})
    except ImportError:
        pass
    print(result["status"], result["roles"], len(result["controls_rejected"]), len(result["omitted_edits_rejected"]))


if __name__ == "__main__":
    main()
