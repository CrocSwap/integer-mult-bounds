#!/usr/bin/env python3
"""One complete frozen complex-network CLI with retained exact observations.

Parent-owned serial wall/RSS/aggregate guard is mandatory. Profile mode is one
literal baseline diagnostic/anchor, not a performance sample. Both benchmark
modes require its immutable anchor. No search, retry, orchestration or network.
"""
from __future__ import annotations

import time
START_WALL = time.perf_counter()
import argparse
from contextlib import redirect_stdout
from fractions import Fraction
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import resource
import runpy
import shutil
import stat
import sys

sys.dont_write_bytecode = True
import adapters
ROUND = Path(__file__).resolve().parent.parent
HERE = ROUND / "baseline"
REFERENCE_DRIVER_SHA = "0d976d2eb6b845f20d4a3396591a806f966688b88693cd6a5f8a0c9e48925e36"
BASE = "19fdb086ea96af9a9f87936a2b888e10af4ed810"
UPSTREAM = "adc7f1241b42e322a6451854ab7e4b4c146bf78a"
PIN_SHA = "88bba3caf5975f30fa7abceaea9454110cf3b069233e8241a2ca13d1dff171a7"
REFERENCE_SHA = "1f763d95c7ff163aa71d13cd82784f16665be8afb21f75e76941e2119562098f"
ENGINE_PINS = {
    "native_gf2.c": "e9c3c9194a08718bd1575c1cf08c6c6772d3b644c2e274c25a84a1f9249d06cc",
    "native_backend.py": "e473c38245c3668715b5a78dfe980b2fe3ed0d0c9b8c97c666fbae6ecf1fffd5",
    "finite_controls.py": "df989a831aac43cc1af95169dad8c64a7548760e6e1f96976da996703f2c8f7a",
    "compare_side_verifier.py": "6e507bb0c7e00d090a60289fddb6c55e90c946d0850c42c3c5e3e15c27604a68",
    "profile_side_verifier.py": "9c994378171c20a91539418d93cb8387e1daa93465d6862beefea90e12999c2a",
    "source/complex_circuit.py": "d623617f7c5cb3189580883a8ab30c0bd3832688ae3f1f0c1f881bbbbff8e0c1",
    "source/complex_network.py": "0da395e67ac04fa213494e71012c1b19b544596d34cdce5a3b172b1fb6af5f1b",
}
COMPLEMENT_EXPECTED = {
    "calls": 238685,
    "canonical_stream_bytes": 55839507,
    "sha256": "7dec2bf33303c37e1c699609e83768d61df7e19104d34a26a148f66d5ccc4838",
    "schema": "v2-jsonl:call,us,vs,result(type=list+values or type=None); ordered exact integer vectors",
}
EXPECTED_STDOUT = (
    "PASS conditional 59/100000000000 > 2^-31; minimum margin 14779261/25000000000000000\n"
    "Side roles per invocation 108195 vs original 3693800\n"
)


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def cpu():
    own = resource.getrusage(resource.RUSAGE_SELF)
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + own.ru_stime + children.ru_utime + children.ru_stime


def inventory(root, pins, *, exact=True):
    need(root.is_dir() and not root.is_symlink(), "Missing or symlinked input root")
    files = {}
    for path in sorted(root.rglob("*")):
        need(not path.is_symlink(), "Symlink in frozen inputs: " + str(path))
        if path.is_file():
            relative = str(path.relative_to(root))
            if relative not in pins:
                need(not exact, "Undeclared frozen input: " + relative)
                continue
            raw = path.read_bytes()
            expected = pins[relative][0] if type(pins[relative]) is list else pins[relative]
            need(sha(raw) == expected, "Frozen input digest changed: " + relative)
            files[relative] = {"sha256": sha(raw), "mode": stat.S_IMODE(path.stat().st_mode), "bytes": len(raw)}
    need(set(files) == set(pins), "Frozen input inventory incomplete")
    return files


def typed(value):
    """Lossless full return representation, including order and exact types."""
    kind = type(value)
    if kind is Fraction:
        return ["Fraction", value.numerator, value.denominator]
    if value is None:
        return ["None"]
    if kind is bool:
        return ["bool", value]
    if kind is int:
        return ["int", str(value)]
    if kind is float:
        return ["float", value.hex()]
    if kind is str:
        return ["str", value]
    if kind is list or kind is tuple:
        return [kind.__name__, [typed(item) for item in value]]
    if kind is dict:
        return ["dict", [[typed(key), typed(item)] for key, item in value.items()]]
    raise TypeError("Unsupported exact full-certificate return type: " + kind.__name__)


class Phases:
    """Observational wrappers delegate each call and preserve its return."""
    def __init__(self):
        self.rows = {}

    def call(self, name, function, *args, **kwargs):
        wall, used = time.perf_counter(), cpu()
        try:
            return function(*args, **kwargs)
        finally:
            row = self.rows.setdefault(name, {"calls": 0, "wall_seconds": 0.0, "cpu_seconds_with_children": 0.0})
            row["calls"] += 1
            row["wall_seconds"] += time.perf_counter() - wall
            row["cpu_seconds_with_children"] += cpu() - used

    def wrap(self, owner, attribute, name):
        original = getattr(owner, attribute)
        def observed(*args, **kwargs):
            return self.call(name, original, *args, **kwargs)
        setattr(owner, attribute, observed)
        return original, observed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frozen-root", type=Path, default=HERE / "frozen")
    parser.add_argument("--reference", type=Path, default=HERE / "reference/certificates/complex-network.json")
    parser.add_argument("--lanes", choices=("none", "sets", "guards", "trace", "all"), required=True)
    parser.add_argument("--finite-only", action="store_true")
    parser.add_argument("--output", type=Path, required=True, help="New external directory; every write stays below it")
    parser.add_argument("--anchor", type=Path, default=HERE / "anchor.json")
    args = parser.parse_args()
    args.mode = "candidate"  # Every new arm starts from the original native C configuration.
    need(args.finite_only or sys.flags.optimize == 0, "Every full-caller mode requires original assertions")
    need(sys.implementation.name == "cpython" and sys.version_info[:2] == (3, 12), "Frozen CPython 3.12 required")
    need((args.mode == "profile") == (args.anchor is None), "Profile creates the anchor; both benchmark arms require --anchor")
    frozen, reference = args.frozen_root.resolve(), args.reference.resolve()
    output = args.output.resolve()
    need(not output.exists(), "Refusing to overwrite run evidence")
    need(not output.is_relative_to(HERE) and not output.is_relative_to(frozen), "Output must be outside immutable sources")
    need(reference.is_file() and not reference.is_symlink(), "Reference certificate missing or symlinked")
    source_pin_bytes = (HERE / "SOURCE-PINS.json").read_bytes()
    need(sha(source_pin_bytes) == PIN_SHA, "Source inventory pin changed")
    pins = json.loads(source_pin_bytes)
    need(len(pins) == 32, "Frozen closure must contain twelve scripts, manifest and nineteen payloads")
    reference_bytes = reference.read_bytes()
    need(sha(reference_bytes) == REFERENCE_SHA, "Original full certificate reference changed")
    driver_before = Path(__file__).read_bytes()
    new_custody_before = adapters.custody(ROUND, args.lanes)
    reference_driver_before = (HERE / "full_driver.py").read_bytes()
    need(sha(reference_driver_before) == REFERENCE_DRIVER_SHA, "Reference driver pin changed")
    anchor_bytes = None if args.anchor is None else args.anchor.read_bytes()
    expected_anchor = None if anchor_bytes is None else json.loads(anchor_bytes)
    if expected_anchor is not None:
        need(expected_anchor.get("schema") == "gf2-full-network-anchor-v1" and
             expected_anchor.get("base_commit") == BASE and expected_anchor.get("source_pin_sha256") == PIN_SHA and
             expected_anchor.get("driver_sha256") == REFERENCE_DRIVER_SHA and
             expected_anchor.get("engine_pins") == ENGINE_PINS,
             "Anchor source/driver/engine identity differs; no benchmark permitted")
    output.mkdir(parents=True)
    compiler_tmp = output / "compiler-tmp"
    compiler_tmp.mkdir()
    os.environ["TMPDIR"] = str(compiler_tmp)
    phases = Phases()
    frozen_before = phases.call("input_custody", inventory, frozen, pins)
    engine_before = phases.call("engine_custody", inventory, HERE / "engine", ENGINE_PINS)
    manifest = json.loads((frozen / "upstream/manifest.json").read_bytes())
    need(manifest["commit"] == UPSTREAM and len(manifest["files"]) == 19, "Wrong pinned upstream manifest")
    need({"upstream/" + name for name in manifest["files"]} ==
         {name for name in pins if name.startswith("upstream/") and name != "upstream/manifest.json"},
         "Source verifier payload closure changed")
    for name, info in manifest["files"].items():
        need(info["sha256"] == pins["upstream/" + name][0], "Manifest payload hash differs from independent frozen pin")

    runtime, engine = output / "runtime-root", output / "engine"
    phases.call("fresh_root_copy", shutil.copytree, frozen, runtime)
    phases.call("fresh_engine_copy", shutil.copytree, HERE / "engine", engine)
    # copytree retains readonly source directory permissions. Only this new
    # private root is made writable for the original CLI certificate output.
    runtime.chmod(0o755)
    (runtime / "certificates").mkdir()
    runtime_before = inventory(runtime, pins)
    copied_engine_before = inventory(engine, ENGINE_PINS)
    need(runtime_before == frozen_before and copied_engine_before == engine_before, "Copy changed input bytes or modes")
    for name in ("complex_network.py", "complex_circuit.py"):
        need((engine / "source" / name).read_bytes() == (runtime / "scripts" / name).read_bytes(),
             "PR5929 engine/source differs from the full caller closure")
    script_names = {Path(name).stem for name in pins if name.startswith("scripts/")}
    engine_names = {"native_backend", "finite_controls", "compare_side_verifier", "profile_side_verifier"}
    need(not (script_names | engine_names) & set(sys.modules), "Scientific module already loaded; fresh process required")
    sys.path[:0] = [str(engine), str(runtime / "scripts")]
    backend = phases.call("cold_engine_import", importlib.import_module, "native_backend")
    comparison = importlib.import_module("compare_side_verifier")
    native = None
    finite = None
    build = None
    if args.mode == "candidate":
        native, build = phases.call("cold_compile_link_load", backend.build_native, output / "cold-build")
        extensions = phases.call("new_adapter_preparation", adapters.prepare, ROUND, backend, native, output, args.lanes, phases)
        finite = phases.call("all_native_finite_independent_controls", importlib.import_module("finite_controls").run_controls, native)
        phases.call("all_new_controls", adapters.run_controls, extensions, backend, native, phases)
        (output / "finite-controls.json").write_bytes(canonical(finite) + b"\n")

    if args.finite_only:
        need(inventory(frozen, pins) == frozen_before and inventory(HERE / "engine", ENGINE_PINS) == engine_before, "Finite immutable source custody changed")
        need(inventory(runtime, pins) == runtime_before and inventory(engine, ENGINE_PINS) == copied_engine_before, "Finite copied source custody changed")
        need(adapters.custody(ROUND, args.lanes) == new_custody_before, "Finite new source custody changed")
        result = {"status": "H25_BOOKKEEPING_FINITE_PASS", "lanes": args.lanes,
                  "optimized": sys.flags.optimize, "original_controls": finite,
                  "new_controls": extensions["controls"], "new_source_custody": new_custody_before,
                  "driver_sha256": sha(driver_before),
                  "reference_driver_sha256": REFERENCE_DRIVER_SHA, "phases": phases.rows}
        (output / "receipt.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps(result, sort_keys=True))
        return

    circuit_module = phases.call("cold_complex_module_load", backend.load_source, "complex_circuit")
    sys.modules["complex_circuit"] = circuit_module
    rank_calls = []
    complement = extensions["trace_type"](circuit_module.Label)
    phases.call("private_set_adapter_installation", adapters.install_set, extensions, circuit_module)
    binding = None
    if args.mode == "candidate":
        binding = backend.bind(circuit_module, native, rank_calls, complement)
    else:
        backend.guard_module(circuit_module)
        backend.attach_trace(circuit_module, rank_calls, complement)
    captures = {}
    phases.wrap(circuit_module.ComplexSideCircuit, "__init__", "side_construction")
    phases.wrap(circuit_module.Checks, "__init__", "checks_initialization")
    phases.wrap(circuit_module, "compile_roles", "compile_roles")
    phases.wrap(circuit_module.Checks, "verify_map", "verify_map")
    phases.wrap(circuit_module.Checks, "verify_labels", "verify_labels")
    original_roles = circuit_module.verify_role_frames
    def observe_roles(c, checks, code=None):
        need("side" not in captures and code is not None, "Unexpected role-frame invocation")
        result = phases.call("verify_role_frames", original_roles, c, checks, code)
        captures["side"] = (c, checks, code, result)
        return result
    circuit_module.verify_role_frames = observe_roles

    certify = phases.call("cold_certify_import", importlib.import_module, "certify")
    phases.wrap(certify, "verify_sources", "original_upstream_verify_sources")
    prepare = phases.call("cold_prepare_import", importlib.import_module, "prepare_layers")
    search = importlib.import_module("search_network")
    phases.wrap(search, "log_integer_bounds", "full_log_integer_bounds")
    original_serializable = prepare.serializable
    depth = 0
    def observe_serializable(value):
        nonlocal depth
        outer = depth == 0
        if outer:
            need("full_return" not in captures and type(value) is dict, "Unexpected outer serialization")
            captures["full_return"] = value
        depth += 1
        try:
            # Recursion still delegates the original serializable exactly once
            # per value; only the outer call is captured/timed.
            if outer:
                return phases.call("original_serializable", original_serializable, value)
            return original_serializable(value)
        finally:
            depth -= 1
    prepare.serializable = observe_serializable

    phases.call("private_set_lease_sealing", adapters.seal, extensions)
    caller = runtime / "scripts/complex_network.py"
    old_argv = sys.argv
    stdout = io.StringIO()
    try:
        adapters.arm(extensions)
        sys.argv = [str(caller)]
        with redirect_stdout(stdout):
            namespace = phases.call("complete_original_cli", runpy.run_path, str(caller), run_name="__main__")
    finally:
        sys.argv = old_argv
        adapters.disarm(extensions)
    cli_stdout = stdout.getvalue()
    need(cli_stdout == EXPECTED_STDOUT, "Original CLI stdout changed")
    certificate_bytes = (runtime / "certificates/complex-network.json").read_bytes()
    need(certificate_bytes == reference_bytes, "Original CLI certificate bytes differ from the pinned reference")
    need(sys.modules["complex_circuit"] is circuit_module and
         namespace["ComplexSideCircuit"] is circuit_module.ComplexSideCircuit and
         namespace["Checks"] is circuit_module.Checks and namespace["compile_roles"] is circuit_module.compile_roles and
         namespace["verify_role_frames"] is observe_roles and namespace["serializable"] is observe_serializable,
         "Caller used a different scientific module or observation binding")
    need(captures.keys() == {"side", "full_return"}, "Missing exact caller observations")
    c, checks, code, role_result = captures["side"]
    full_return = captures["full_return"]
    need(full_return["role_frames"] is role_result and full_return["upstream_commit"] == UPSTREAM,
         "Role return or actual source verification boundary changed")
    for name in ("side_construction", "checks_initialization", "compile_roles", "verify_map", "verify_labels",
                 "verify_role_frames", "original_upstream_verify_sources", "full_log_integer_bounds",
                 "original_serializable", "complete_original_cli"):
        need(phases.rows.get(name, {}).get("calls") == 1, "Original phase was omitted or repeated: " + name)
    imports = {}
    for name in script_names - {"complex_network"}:
        module = sys.modules.get(name)
        expected_path = engine / "source/complex_circuit.py" if name == "complex_circuit" else runtime / "scripts" / (name + ".py")
        need(module is not None and Path(module.__file__).resolve() == expected_path.resolve(), "Unpinned scientific import: " + name)
        imports[name] = str(module.__file__)
    if binding is not None:
        binding["runtime_guard"].check()
        need(binding["counters"] == {"complement_native": 238685, "complement_fallback": 0,
                                      "gram_native": 59959, "gram_fallback": 0}, "Native full-call coverage changed")

    side_result = {key: full_return[key] for key in ("circuit", "side_map", "labels", "role_frames")}
    witness = {
        "support": c.support, "args": c.args, "kind": c.kind, "active": sorted(c.active),
        "pieces": [(target, node, (coefficient.numerator, coefficient.denominator)) for target, node, coefficient in c.pieces],
        "labels": [(key, list(label.basis.items()), label.dim, label.key) for key, label in checks.cache.items()],
        "code": {"roles": code["roles"], "gates": code["gates"], "sources": list(code["sources"].items()),
                 "outputs": list(code["outputs"].items())},
    }
    side_output = output / "side-observations"
    side_output.mkdir()
    side_receipt = phases.call("identical_lossless_side_serialization", comparison.write_scientific,
                               side_output, side_result, witness, rank_calls)
    complement_receipt = complement.receipt()
    need(complement_receipt == COMPLEMENT_EXPECTED, "Every ordered complement observation must match PR5929")
    full_typed_bytes = canonical(typed(full_return))
    (output / "full-return.lossless.json").write_bytes(full_typed_bytes)
    (output / "original-stdout.txt").write_text(cli_stdout, encoding="utf-8")
    (output / "complement-transcript.json").write_bytes(canonical(complement_receipt) + b"\n")
    science = {
        "full_cli_certificate_sha256": sha(certificate_bytes), "full_cli_stdout_sha256": sha(cli_stdout.encode("utf-8")),
        "full_return_lossless_sha256": sha(full_typed_bytes), "side": side_receipt,
        "ordered_complements": complement_receipt, "upstream_commit": UPSTREAM,
    }
    anchor = {"schema": "gf2-full-network-anchor-v1", "base_commit": BASE, "source_pin_sha256": PIN_SHA,
              "driver_sha256": REFERENCE_DRIVER_SHA, "engine_pins": ENGINE_PINS, "science": science}
    if expected_anchor is not None:
        need(anchor == expected_anchor, "Complete certificate/types/ordered observations differ from frozen anchor")
    else:
        (output / "anchor.json").write_bytes(canonical(anchor) + b"\n")
    need(inventory(frozen, pins) == frozen_before and inventory(HERE / "engine", ENGINE_PINS) == engine_before,
         "Immutable source bytes/modes changed")
    need(inventory(runtime, pins, exact=False) == runtime_before and inventory(engine, ENGINE_PINS) == copied_engine_before,
         "Runtime scientific source bytes/modes changed")
    runtime_files = {str(path.relative_to(runtime)) for path in runtime.rglob("*") if path.is_file()}
    need(runtime_files == set(pins) | {"certificates/complex-network.json"}, "Unexpected full-caller file side effect")
    need(Path(__file__).read_bytes() == driver_before and reference.read_bytes() == reference_bytes and
         (anchor_bytes is None or args.anchor.read_bytes() == anchor_bytes), "Driver/reference/anchor changed during run")
    need(adapters.custody(ROUND, args.lanes) == new_custody_before, "New source custody changed")
    receipt = {
        "new_source_custody": new_custody_before,
        "status": "FULL_NETWORK_PROFILE_ANCHOR_PASS" if args.mode == "profile" else "FULL_NETWORK_COMPLETE_PASS",
        "mode": args.mode, "lanes": args.lanes, "bookkeeping": adapters.receipt(extensions),
        "reference_driver_sha256": REFERENCE_DRIVER_SHA,
        "science": science, "base_commit": BASE, "native_predecessor_pr": 5995,
        "driver_sha256": sha(driver_before), "source_pin_sha256": PIN_SHA,
        "frozen_custody": frozen_before, "engine_custody": engine_before, "scientific_imports": imports,
        "build": build, "finite_controls": finite,
        "private_root_permission": "runtime-root is0755; copied input file modes are retained and checked; immutable stages are never chmodded",
        "compiler_tmpdir": str(compiler_tmp),
        "native_calls": None if binding is None else dict(binding["counters"]),
        "phases": phases.rows, "process_wall_seconds_before_receipt": time.perf_counter() - START_WALL,
        "process_and_compiler_cpu_seconds_before_receipt": cpu(),
        "environment": {"python": sys.version, "executable": sys.executable, "platform": sys.platform},
        "measurement": "Parent outer guard is authoritative. Phases are nested observations, not additive costs. Profile is excluded from performance selection. Every timed arm includes copies, source checks, original CLI and retained full witnesses/transcripts; candidate additionally pays cold build/load/all finite controls.",
        "scope": "Complete frozen historical complex-network CLI with retained observations; conditional certificate only. No bare-CLI factor, selected-frontier, new kappa or PR5864 speed claim.",
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    sys.stdout.write(cli_stdout)
    print(json.dumps({"status": receipt["status"], "mode": args.mode, "science": science,
                      "wall_seconds": receipt["process_wall_seconds_before_receipt"],
                      "cpu_seconds_with_compiler": receipt["process_and_compiler_cpu_seconds_before_receipt"],
                      "phases": phases.rows}, sort_keys=True))


if __name__ == "__main__":
    main()
