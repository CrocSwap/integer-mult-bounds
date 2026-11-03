"""Exact conformance of the packed PR1443 transition. Apache-2.0."""
import hashlib
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load_adapter():
    spec = importlib.util.spec_from_file_location("dihedral_adapter", HERE / "run.py")
    require(spec is not None and spec.loader is not None, "adapter loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def columns(original, fast):
    count = 0
    for generator in original["GEN"]:
        for pair in range(1 << 16):
            first = (pair & 255) | ((pair >> 8) << 16)
            for state in (first, first << 8):
                require(fast(state, generator) == original["step"](state, generator),
                        "single-column transition")
                count += 1
    return count


def balls(original, fast):
    reference = original["step"]
    states = set()
    for start in (original["IDENTITY"], original["TARGET"]):
        expected, layers = original["ball"](start, 4)
        original["step"] = fast
        actual, actual_layers = original["ball"](start, 4)
        original["step"] = reference
        require(actual == expected and actual_layers == layers,
                "every ball state and its first witness")
        states.update(expected)
    count = 0
    for state in sorted(states):
        for generator in original["GEN"]:
            require(fast(state, generator) == reference(state, generator),
                    "all reached-state transitions")
            count += 1
    return len(states), count


def expect_failure(call, label):
    try:
        call()
    except ValueError:
        return
    raise ValueError("control accepted: " + label)


def controls(adapter, original, fast):
    permutations = original["PERM"]
    expect_failure(lambda: adapter.packed_step({1: permutations[1]}), "missing label")
    expect_failure(lambda: adapter.packed_step({1: [], 2: permutations[2]}), "short table")
    invalid = {key: list(value) for key, value in permutations.items()}
    invalid[1][0] = 256
    expect_failure(lambda: adapter.packed_step(invalid), "non-byte value")
    changed = {key: list(value) for key, value in permutations.items()}
    changed[1][1], changed[1][2] = changed[1][2], changed[1][1]
    mutant = adapter.packed_step(changed)
    probes = [(state, generator) for state in (1, 2, 256, 65536, 0x12345678)
              for generator in original["GEN"]]
    require(any(mutant(s, g) != fast(s, g) for s, g in probes), "wrong permutation rejected")
    require(any(fast(s, (g, 3 if x == 1 else 1, y)) != fast(s, (g, x, y))
                for s, (g, x, y) in probes), "wrong scatter rejected")
    require(any(fast(s, (3 - g, x, y)) != fast(s, (g, x, y))
                for s, (g, x, y) in probes), "wrong label rejected")
    require(any((fast(s, g) & 0xFFFF) != fast(s, g) for s, g in probes),
            "discarded second row rejected")
    return 7


def source_controls(adapter):
    read = Path.read_bytes
    for name, _ in adapter.PINS:
        target = adapter.ROOT / name

        def changed(path):
            raw = read(path)
            return raw + b"corrupt" if path == target else raw

        with patch.object(Path, "read_bytes", changed):
            expect_failure(adapter.source_bytes, "changed source: " + name)
    return len(adapter.PINS)


def main():
    adapter = load_adapter()
    original = adapter.load_original()
    fast = adapter.packed_step(original["PERM"])
    column_checks = columns(original, fast)
    states, reached_checks = balls(original, fast)
    rejected = controls(adapter, original, fast) + source_controls(adapter)
    expected = json.loads(json.dumps(original["run"]()))
    actual = adapter.replay()
    require(actual == expected, "complete original scientific result")
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sorted(HERE.iterdir()) if path.is_file()}
    print(json.dumps({"status": "PASS_DIHEDRAL_PACKED_REPLAY", "column_checks": column_checks,
                      "reached_states": states, "reached_transition_checks": reached_checks,
                      "controls": rejected, "minimum": actual["minimum"],
                      "complete_certificate_equal": True, "package_sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
