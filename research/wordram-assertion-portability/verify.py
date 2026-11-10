"""Run the complete adapted entry and controls; emit a generated stdout receipt."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adapter import (ERROR_NAME, HERE, MAX_BYTES, authenticate, bounded_tree,
                     lower, need, read_sources, reference, replay)


def rejected(function, arguments, exception, label):
    try:
        function(*arguments)
    except exception:
        return label
    raise ValueError("control accepted: " + label)


def outcome(code):
    environment = {ERROR_NAME: AssertionError}
    try:
        exec(code, environment)
        failure = None
    except AssertionError as error:
        failure = repr(error.args)
    return environment.get("events"), failure


def transformation_controls():
    samples = [
        "events=[]\nassert events.append('test') is None, events.append('message')",
        "events=[]\nassert events.append('test'), events.append('message')",
        "events=[]\nassert False",
        "events=[]\nassert False, None",
        "events=[]\nassert False, ('message', 2)",
        "events=[]\nfor i in range(3):\n events.append(i)\n assert i < 2, i",
        "events=[]\ndef f():\n assert False, 'inside function'\nf()",
        "events=[]\ntry:\n assert False, 7\nexcept AssertionError as e:\n events.append(e.args)",
    ]
    compared = 0
    for sample in samples:
        expected = outcome(compile(sample, "control", "exec", optimize=0))
        for level in range(3):
            code, checks = lower(sample.encode(), "control", optimize=level)
            need(len(checks) == 1 and outcome(code) == expected,
                 "assertion evaluation, message and exception preservation")
            compared += 1
    controls = [
        rejected(bounded_tree, (b" " * (MAX_BYTES + 1), "large"), ValueError, "large source"),
        rejected(bounded_tree, (ERROR_NAME.encode() + b"=1", "alias"), ValueError, "reserved alias"),
        rejected(lower, (b"if not __debug__: pass", "guard"), ValueError, "foreign guard"),
        rejected(lower, (b"x=1", "entry", True), ValueError, "missing entry guard"),
        rejected(authenticate, (b"changed", "0" * 64, "mutant"), ValueError, "changed source bytes"),
    ]
    return compared, controls


def with_fault(module, name, replacement, call, label):
    original = getattr(module, name)
    setattr(module, name, replacement)
    try:
        return rejected(call, (), AssertionError, label)
    finally:
        setattr(module, name, original)


def semantic_controls(finder):
    modules = finder.loaded
    ram = modules["ram/verify_wordram.py"]
    circuit = modules["ram/circuit_sharing.py"]
    integration = modules["verify_integration.py"]
    recovery = modules["recovery/fixedpoint_fft.py"]
    original_run = ram.run

    def bad_ram(*args, **kwargs):
        result = original_run(*args, **kwargs)
        result.memory[3] ^= 1
        return result

    def bad_circuit(*args, **kwargs):
        return (0,)

    original_execute = integration.execute

    def bad_execute(*args, **kwargs):
        result, digits = original_execute(*args, **kwargs)
        return result, [digits[0] ^ 1, *digits[1:]]

    controls = [with_fault(ram, "run", bad_ram, ram.run_checks, "wrong RAM residue"),
                with_fault(circuit, "evaluate", bad_circuit, circuit.check, "wrong circuit value")]
    calls = iter((True, False))

    def one_bad_execute(*args, **kwargs):
        if next(calls):
            return bad_execute(*args, **kwargs)
        return original_execute(*args, **kwargs)

    controls.append(with_fault(integration, "execute", one_bad_execute,
                               integration.verify, "wrong whole-program digits"))
    controls.append(with_fault(recovery, "nearest", lambda value: 0,
                               lambda: recovery.run(4, 40, 0), "wrong FFT rounding"))
    return controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scratch", type=Path, default=Path(tempfile.gettempdir()))
    args = parser.parse_args()
    need(args.scratch.is_dir(), "scratch directory exists")
    files = read_sources()
    compared, controls = transformation_controls()
    expected = reference(args.scratch)
    result, finder, children = replay(files, args.scratch)
    controls.extend(semantic_controls(finder))
    need(read_sources() == files, "source files remain unchanged")
    result.pop("seconds")  # This clock field is not scientific output.
    need(result == expected, "complete scientific output equals original normal entry")
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(HERE.iterdir()) if p.is_file()}
    receipt = {"status": "PASS_WORDRAM_ASSERTION_PORTABILITY", "python": sys.version,
               "optimization": sys.flags.optimize, "assertion_semantics_cases": compared,
               "rejection_controls": controls, "source_result": result,
               "adapted_assertions": finder.checks, "NTT_children": children,
               "package_sha256": hashes}
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
