"""Derive an explicit engineering driver with a reversible, bounded edit list.

This script edits source text only. It never imports or executes scientific code.
The science anchor's driver digest names the immutable reference driver, while
each engineering receipt separately records the actual derived driver digest.
"""
from pathlib import Path
import ast
import hashlib
import json

ROOT = Path(__file__).resolve().parent.parent
REFERENCE_SHA = '0d976d2eb6b845f20d4a3396591a806f966688b88693cd6a5f8a0c9e48925e36'
PATCHES = [
    ('HERE = Path(__file__).resolve().parent',
     'import adapters\nROUND = Path(__file__).resolve().parent.parent\nHERE = ROUND / "baseline"\nREFERENCE_DRIVER_SHA = "' + REFERENCE_SHA + '"'),
    ('parser.add_argument("--frozen-root", type=Path, required=True)',
     'parser.add_argument("--frozen-root", type=Path, default=HERE / "frozen")'),
    ('parser.add_argument("--reference", type=Path, required=True, help="Pinned original complex-network.json file")',
     'parser.add_argument("--reference", type=Path, default=HERE / "reference/certificates/complex-network.json")'),
    ('parser.add_argument("--mode", choices=("profile", "baseline", "candidate"), required=True)',
     'parser.add_argument("--lanes", choices=("none", "sets", "guards", "trace", "all"), required=True)\n    parser.add_argument("--finite-only", action="store_true")'),
    ('parser.add_argument("--anchor", type=Path, help="Frozen anchor.json emitted by the one profile run")',
     'parser.add_argument("--anchor", type=Path, default=HERE / "anchor.json")'),
    ('args = parser.parse_args()\n    need(sys.flags.optimize == 0, "Every full-caller mode requires original assertions")',
     'args = parser.parse_args()\n    args.mode = "candidate"  # Every new arm starts from the original native C configuration.\n    need(args.finite_only or sys.flags.optimize == 0, "Every full-caller mode requires original assertions")'),
    ('driver_before = Path(__file__).read_bytes()',
     'driver_before = Path(__file__).read_bytes()\n    new_custody_before = adapters.custody(ROUND, args.lanes)\n    reference_driver_before = (HERE / "full_driver.py").read_bytes()\n    need(sha(reference_driver_before) == REFERENCE_DRIVER_SHA, "Reference driver pin changed")'),
    ('expected_anchor.get("driver_sha256") == sha(driver_before)',
     'expected_anchor.get("driver_sha256") == REFERENCE_DRIVER_SHA'),
    ('finite = phases.call("all_native_finite_independent_controls", importlib.import_module("finite_controls").run_controls, native)',
     'extensions = phases.call("new_adapter_preparation", adapters.prepare, ROUND, backend, native, output, args.lanes, phases)\n        finite = phases.call("all_native_finite_independent_controls", importlib.import_module("finite_controls").run_controls, native)\n        phases.call("all_new_controls", adapters.run_controls, extensions, backend, native, phases)'),
    ('    circuit_module = phases.call("cold_complex_module_load", backend.load_source, "complex_circuit")',
     '    if args.finite_only:\n        need(inventory(frozen, pins) == frozen_before and inventory(HERE / "engine", ENGINE_PINS) == engine_before, "Finite immutable source custody changed")\n        need(inventory(runtime, pins) == runtime_before and inventory(engine, ENGINE_PINS) == copied_engine_before, "Finite copied source custody changed")\n        need(adapters.custody(ROUND, args.lanes) == new_custody_before, "Finite new source custody changed")\n        result = {"status": "H25_BOOKKEEPING_FINITE_PASS", "lanes": args.lanes,\n                  "optimized": sys.flags.optimize, "original_controls": finite,\n                  "new_controls": extensions["controls"], "new_source_custody": new_custody_before,\n                  "driver_sha256": sha(driver_before),\n                  "reference_driver_sha256": REFERENCE_DRIVER_SHA, "phases": phases.rows}\n        (output / "receipt.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\\n")\n        print(json.dumps(result, sort_keys=True))\n        return\n\n    circuit_module = phases.call("cold_complex_module_load", backend.load_source, "complex_circuit")'),
    ('complement = backend.ComplementTrace(circuit_module.Label)',
     'complement = extensions["trace_type"](circuit_module.Label)\n    phases.call("private_set_adapter_installation", adapters.install_set, extensions, circuit_module)'),
    ('    caller = runtime / "scripts/complex_network.py"',
     '    phases.call("private_set_lease_sealing", adapters.seal, extensions)\n    caller = runtime / "scripts/complex_network.py"'),
    ('    try:\n        sys.argv = [str(caller)]',
     '    try:\n        adapters.arm(extensions)\n        sys.argv = [str(caller)]'),
    ('    finally:\n        sys.argv = old_argv',
     '    finally:\n        sys.argv = old_argv\n        adapters.disarm(extensions)'),
    ('"driver_sha256": sha(driver_before), "engine_pins": ENGINE_PINS, "science": science',
     '"driver_sha256": REFERENCE_DRIVER_SHA, "engine_pins": ENGINE_PINS, "science": science'),
    ('        "mode": args.mode, "science": science, "base_commit": BASE, "native_predecessor_pr": 5929,',
     '        "mode": args.mode, "lanes": args.lanes, "bookkeeping": adapters.receipt(extensions),\n        "reference_driver_sha256": REFERENCE_DRIVER_SHA,\n        "science": science, "base_commit": BASE, "native_predecessor_pr": 5995,'),
    ('    receipt = {\n        "status":',
     '    need(adapters.custody(ROUND, args.lanes) == new_custody_before, "New source custody changed")\n    receipt = {\n        "new_source_custody": new_custody_before,\n        "status":'),
]


def main():
    source = (ROOT / 'baseline/full_driver.py').read_bytes()
    if hashlib.sha256(source).hexdigest() != REFERENCE_SHA:
        raise ValueError('Pinned reference driver differs')
    original = source.decode()
    result = original
    for old, new in PATCHES:
        if result.count(old) != 1:
            raise ValueError('Driver edit does not have exactly one original match: ' + old[:100])
        result = result.replace(old, new, 1)
    ast.parse(result)
    reverse = result
    for old, new in PATCHES[::-1]:
        if reverse.count(new) != 1:
            raise ValueError('Driver inverse is ambiguous')
        reverse = reverse.replace(new, old, 1)
    if reverse != original:
        raise ValueError('Driver exact inverse failed')
    (ROOT / 'integration/full_driver.py').write_text(result)
    receipt = {'reference_driver_sha256': REFERENCE_SHA,
               'derived_driver_sha256': hashlib.sha256(result.encode()).hexdigest(),
               'patches': [{'old': old, 'new': new} for old, new in PATCHES],
               'exact_inverse_restores_original_bytes': True,
               'old_controls_and_observer_reference_unmodified': True,
               'both_new_arms_use_original_native_C_mode': True,
               'source_only_derivation_no_scientific_execution': True}
    (ROOT / 'integration/DERIVATION.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in receipt.items() if k != 'patches'}, sort_keys=True))


if __name__ == '__main__':
    main()
