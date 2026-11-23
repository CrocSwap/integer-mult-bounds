#!/usr/bin/env python3
"""Emit and receive the #8088 target fixed directory in separate processes.

Usage: python3.12 -I -B receiver_check.py run CANDIDATE_ROOT
Individual modes: emit CANDIDATE_ROOT OUTPUT_DAG; receive CANDIDATE_ROOT DAG
EXPECTED_SHA256; controls CANDIDATE_ROOT DAG EXPECTED_SHA256.

The candidate root contains runtime/ and research/frequency-weighted-native-
multiplier/. The paired run authenticates the receiver against the digest of
the directory emitted in its own first child. No WASI fuel or universal setup
time bound follows from these finite checks.
"""

from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
from tempfile import TemporaryDirectory


RUNTIME_PINS = {
    "installations.py": "5df81fddba26013b142195f5c3119491fa2f07b1e72c3616ae76e7d7ffbb0fd1",
    "raw_binary_stage.py": "e24bd735598d278dbd46cada584a63da01796d77ad557a45b80a4dfc7bbbd0b0",
    "strong_binary.py": "64673cce85c94f90c498ca01bfda138bb98e08b56ad3777c6565be86bde09020",
    "strong_complex.py": "8f3fb92523df006e2e94505127088aaf2e64fadd20b3cab2344f62d7690e875d",
    "grades.py": "6124744b40f806c80b6f10010a72e755bc11d64a8cc9a04f5e8316799eb6f05d",
    "transport.py": "9eb8f0d77a4c53fc4fddffdfe198cab930b6d1f49e2b6d43c970397051bb7818",
    "retimed_supplier.py": "2a87c2781ca93fa854aee098dcb7c50a65f2a46267ba926e3997b442e5a25f2c",
    "binary_receiver.py": "a7cc759e9a88e60dbcd59ca314ae5b9d39a33b5c642b56e680bbab775b0f06c5",
    "band_product.py": "0a2a243378ced624fa94100d7743bab5209edacda1e3b5a5c2fda6fd0a66791b",
    "upstream.py": "d9b079965d8abc04be3eda662fc84ba9a08c4f03e8ccc7bd3e775876164e6c10",
    "strong-bit.json.gz": "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362",
    "w5669_shortcut5.json.gz": "6ef741c346ea075c4f2ed11f9d42d7076103e72d4a9e5059d495f1cb990fd149",
}
PORTABLE_PINS = {
    "consumer.py": "411cc1052a70f7084de81f6f1e54636737d5e5155d0756b8271d5d82c268d3b3",
    "compiler_state.py": "11f371903410a53aa138bb9b9c49e9441393a34092fff922716a78b5521e1870",
    "tape_directory.py": "70bf289334f724cabf1cfa9e074199e6be93ef0aeba8193f279e5ef1336de97b",
    "fixed_directory.py": "c99e9945295b954b453f4995474db4ec8da9e7d8d6ba1a564456213d066e5904",
    "record_census.py": "8132c345cfcc5e7d89494fa437685673273f878f2dc40e0187bf2b84eee17e08",
}
EXPECTED_HEIGHTS = ((3000, 3080, 1024), (8192, 106000, 1681001, 85406))


def digest(path):
    h = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def verify_pins(root, pins):
    for name, expected in pins.items():
        if digest(root / name) != expected:
            raise ValueError(f"Source differs at {name}")


def paths(root):
    runtime = root / "runtime"
    portable = root / "research/frequency-weighted-native-multiplier/portable"
    verify_pins(runtime, RUNTIME_PINS)
    verify_pins(portable, PORTABLE_PINS)
    return runtime, portable


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def emit(root, output):
    runtime, portable = paths(root)
    sys.path[:0] = [str(runtime), str(portable)]
    from upstream import install
    install()
    from compiler_state import construct
    from installations import ENTRY, TERMINAL, PROFILES
    from tape_directory import dump
    from grades import WeightedRecipe
    from transport import Recipe
    assert tuple(PROFILES.values()) == (ENTRY, TERMINAL)
    assert TERMINAL.kappa == Q(39, 10000) and TERMINAL.eta == Q(1, 256)

    def forbidden(*args, **kwargs):
        raise AssertionError("Fixed directory construction opened a native calendar or width")

    saved = Recipe.open, Recipe.width, WeightedRecipe.open, WeightedRecipe.width
    Recipe.open, Recipe.width = forbidden, property(forbidden)
    WeightedRecipe.open, WeightedRecipe.width = forbidden, property(forbidden)
    try:
        state = construct()
        heights = tuple(tuple(recipe.rank_log for recipe in layer) for layer in state[0])
        assert heights == EXPECTED_HEIGHTS
        assert all(r.level_floor == 18960 for layer in state[0] for r in layer[:-1])
        with output.open("xb") as target:
            count = dump(target, state)
    finally:
        Recipe.open, Recipe.width, WeightedRecipe.open, WeightedRecipe.width = saved
    assert count < 2**32 and output.stat().st_size < 2**38
    verify_pins(runtime, RUNTIME_PINS)
    verify_pins(portable, PORTABLE_PINS)
    return {"status": "PASS_TARGET_DIRECTORY_EMITTED", "directory_sha256": digest(output),
            "directory_bytes": output.stat().st_size, "directory_records": count,
            "profile_heights": heights, "lazy_native_open_and_width_forbidden": True}


def check_digest(path, expected):
    if len(expected) != 64 or any(ch not in "0123456789abcdef" for ch in expected):
        raise ValueError("Expected digest must be a lowercase SHA-256")
    actual = digest(path)
    if actual != expected:
        raise ValueError("Fixed-directory digest mismatch")
    return actual


def receive(root, directory, expected):
    runtime, portable = paths(root)
    check_digest(directory, expected)
    with TemporaryDirectory(prefix="fixed-receiver-") as tmp:
        machine = Path(tmp) / "machine"
        shutil.copytree(runtime, machine, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        consumer = load_module("pinned_consumer", portable / "consumer.py")
        # Reuse the exact seven-getter AST adapter; verify its source above.
        assert sum(len(v) for v in consumer.BINDINGS.values()) == 7
        consumer.install_bindings(machine)
        target = machine / "installed-native.dag"
        shutil.copyfile(directory, target)
        check_digest(target, expected)
        # Authenticate the same open file before and after parsing, then bind
        # the stock consumer's compiler_state/tape_directory functions.
        (machine / "fixed_directory.py").write_text(
            "from functools import cache\nfrom hashlib import sha256\nfrom pathlib import Path\n"
            "from compiler_state import bind\nfrom tape_directory import load\n"
            f"EXPECTED = {expected!r}\n"
            "@cache\ndef data():\n"
            "    with Path(__file__).with_name('installed-native.dag').open('rb') as f:\n"
            "        h = sha256()\n"
            "        for b in iter(lambda: f.read(1048576), b''): h.update(b)\n"
            "        if h.hexdigest() != EXPECTED: raise ValueError('fixed-directory digest mismatch')\n"
            "        f.seek(0)\n        state = bind(load(f))\n"
            "        f.seek(0)\n        h = sha256()\n"
            "        for b in iter(lambda: f.read(1048576), b''): h.update(b)\n"
            "        if h.hexdigest() != EXPECTED: raise ValueError('fixed-directory changed during load')\n"
            "        return state\n"
        )
        linked_sha = {name: digest(machine / name) for name in
                      ("strong_binary.py", "grades.py", "raw_binary_stage.py", "fixed_directory.py")}
        sys.path.insert(0, str(machine))
        from upstream import install
        install()
        from binary_receiver import Receiver
        from band_product import prepare_native, production_supplier
        from fixed_directory import data
        from grades import numerical_recipe, numerical_source
        from installations import ENTRY, TERMINAL, PROFILES
        from raw_binary_stage import binary_recipe, binary_word
        from retimed_supplier import Positive
        from strong_binary import caller, fixed_binary_charts, graph

        compiled = data()
        assert tuple(PROFILES.values()) == (ENTRY, TERMINAL)
        assert (graph() is compiled[2] and caller() is compiled[3]
                and fixed_binary_charts() is compiled[4])
        assert binary_word() is compiled[1] and numerical_source() is compiled[5]
        assert Receiver.__init__.__globals__["binary_recipe"] is binary_recipe
        assert Positive.__init__.__globals__["numerical_source"] is numerical_source
        assert Positive.__init__.__globals__["numerical_recipe"] is numerical_recipe
        assert tuple(tuple(r.rank_log for r in layer) for layer in compiled[0]) == EXPECTED_HEIGHTS
        owner_rows, positive_rows = [], []
        for profile, layer in zip(PROFILES.values(), compiled[0], strict=True):
            assert tuple(prepare_native(profile)) == layer
            for height, recipe in zip(profile.rank_logs, layer[:-1], strict=True):
                assert binary_recipe(height) is recipe and recipe.level_floor == 18960
                # Direct mode avoids expanding an astronomical quotient table;
                # the actual Receiver constructor still materializes its owner.
                receiver = Receiver(1 << height, (0, 2, 1, 1), direct=True, profile=profile)
                assert receiver.recipe is recipe and receiver.owners.bit_count() == 1
                assert receiver.owners.bit_length() == 92 * height + 1
                assert receiver.stock == receiver.owners and receiver.low == receiver.high == 1
                owner_rows.append({"height": height, "owner_bits": receiver.owners.bit_length(),
                                   "direct_receiver": True})
                del receiver
            positive = production_supplier(profile.complex_log, profile.positive_stop_denominator)
            assert isinstance(positive, Positive) and positive.physical is compiled[5][0]
            assert positive.recipe is layer[-1] and numerical_recipe(profile.complex_log) is layer[-1]
            assert positive.carrier.bit_length() == profile.complex_log + 1
            assert positive.carrier.bit_count() == 1
            assert [v.multiplicity for v in positive.recipe.types()] == [5, 451]
            cells = positive.recipe.typed_cells()
            assert len(cells) == 88
            owners = positive.owners
            assert owners.bit_count() == 1 and owners.bit_length() == 92 * profile.complex_log + 1
            positive_rows.append({"height": profile.complex_log, "carrier_bits": positive.carrier.bit_length(),
                                  "owner_bits": owners.bit_length(), "multiplicities": [5, 451],
                                  "typed_cells": len(cells)})
            del positive, owners
        assert check_digest(target, expected) == expected
        return {"status": "PASS_FIXED_DIRECTORY_RECEIVED", "directory_sha256": expected,
                "directory_bytes": target.stat().st_size, "getter_count": 7,
                "ordinary_receivers": owner_rows, "positive_suppliers": positive_rows,
                "linked_source_sha256": linked_sha,
                "scope": "Fresh process; seven getters bound and actual direct owners instantiated. No astronomical compiled execution, WASI trace or universal setup bound."}


def controls(root, directory, expected):
    runtime, portable = paths(root)
    check_digest(directory, expected)
    rejected = []
    with TemporaryDirectory(prefix="fixed-receiver-corrupt-") as tmp:
        temp = Path(tmp)
        variants = {}
        bad = temp / "corrupt.dag"
        shutil.copyfile(directory, bad)
        with bad.open("r+b") as f:
            f.seek(16); old = f.read(1); f.seek(16); f.write(bytes([old[0] ^ 1]))
        variants["corrupt_byte"] = (bad, expected)
        truncated = temp / "truncated.dag"
        shutil.copyfile(directory, truncated)
        with truncated.open("r+b") as f:
            f.truncate(truncated.stat().st_size - 1)
        variants["truncated_directory"] = (truncated, expected)
        variants["wrong_digest"] = (directory, "0" * 64)
        for name, (path, pin) in variants.items():
            try:
                check_digest(path, pin)
            except ValueError:
                rejected.append(name)
            else:
                raise AssertionError(f"Control accepted: {name}")
        # Repinning a malformed input does not make the binary parser accept it.
        sys.path[:0] = [str(runtime), str(portable)]
        from upstream import install
        install()
        from tape_directory import load
        malformed = {"repinned_bad_magic": b"BAD-DAG!",
                     "repinned_truncated_record": b"IMBDAG1\x00" + struct.pack("<BI", 2, 4) + b"\x01"}
        for name, raw in malformed.items():
            path = temp / name
            path.write_bytes(raw)
            check_digest(path, sha256(raw).hexdigest())
            try:
                with path.open("rb") as f:
                    load(f)
            except (ValueError, IndexError, struct.error):
                rejected.append(name)
            else:
                raise AssertionError(f"Malformed directory accepted: {name}")
    return {"status": "PASS_DIRECTORY_CORRUPTION_CONTROLS", "rejected": sorted(rejected)}


def run(root):
    script = Path(__file__).resolve()
    with TemporaryDirectory(prefix="independent-fixed-install-") as tmp:
        target = Path(tmp) / "target.dag"
        def child(*args):
            proc = subprocess.run([sys.executable, "-I", "-B", str(script), *map(str, args)],
                                  check=True, capture_output=True, text=True)
            return json.loads(proc.stdout)
        emitted = child("emit", root, target)
        received = child("receive", root, target, emitted["directory_sha256"])
        failures = child("controls", root, target, emitted["directory_sha256"])
        assert emitted["directory_sha256"] == received["directory_sha256"]
        return {"status": "PASS_SEPARATE_PROCESS_FIXED_INSTALLATION",
                "emitter": emitted, "receiver": received, "controls": failures}


if __name__ == "__main__":
    if not __debug__:
        raise ValueError("Run with assertions enabled")
    args = sys.argv[1:]
    with TemporaryDirectory(prefix="receiver-import-cache-") as cache:
        sys.pycache_prefix = cache
        sys.dont_write_bytecode = True
        if len(args) == 2 and args[0] == "run":
            result = run(Path(args[1]).resolve())
        elif len(args) == 3 and args[0] == "emit":
            result = emit(Path(args[1]).resolve(), Path(args[2]).resolve())
        elif len(args) == 4 and args[0] == "receive":
            result = receive(Path(args[1]).resolve(), Path(args[2]).resolve(), args[3])
        elif len(args) == 4 and args[0] == "controls":
            result = controls(Path(args[1]).resolve(), Path(args[2]).resolve(), args[3])
        else:
            raise SystemExit(__doc__)
        print(json.dumps(result, indent=2, sort_keys=True))
