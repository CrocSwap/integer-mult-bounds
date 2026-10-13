#!/usr/bin/env python3
"""Reproduce PR626 native gzip false rejection and verify the opt-in fix.

Standard library only. Finite source-bound tooling checks, not a new theorem.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
import zlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PKG = ROOT / "research/complex-k492-owner-repair"
FIXTURE = ROOT / "research/community-k492-audit/pr622/replay"
ORIGINAL = PKG / "extras/check_owner_map.py"
ADAPTED = HERE / "check_owner_map.py"
NAMES = ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz")


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load_adapter():
    spec = importlib.util.spec_from_file_location("payload_adapter", ADAPTED)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(script, work, out, providers=()):
    out.unlink(missing_ok=True)
    command = [sys.executable, "-I", "-O", "-B", str(script),
               "--work", str(work), "--out", str(out)]
    for pid, directory in providers:
        command.extend(("--provider", pid + "=" + str(directory)))
    start = time.perf_counter()
    result = subprocess.run(command, cwd=work, capture_output=True,
                            text=True, timeout=30)
    seconds = time.perf_counter() - start
    return {
        "returncode": result.returncode, "stdout": result.stdout,
        "stderr": result.stderr,
        "output": out.read_bytes() if out.exists() else None,
        "seconds": seconds,
    }


def accepted(result, expected):
    require(result["returncode"] == 0, result["stderr"])
    require(result["output"] == expected, "Complete owner receipt changed")
    require(result["stdout"] == "PASS independent map and exact moments\n",
            "Successful diagnostic changed")


def rejected(result, diagnostic=None):
    require(result["returncode"] != 0, "Invalid input accepted")
    require(result["output"] is None, "Failure emitted a success receipt")
    if diagnostic:
        require(diagnostic in result["stderr"], "Wrong rejection: " + result["stderr"])


def changed_scalar(payload, filename):
    obj = json.loads(payload)
    changed = copy.deepcopy(obj)
    if filename == NAMES[0]:
        additions = [gate for gate in changed["A"] if gate[0] == "add"]
        additions[88 % len(additions)][3] += 1
        require(changed["start"] == obj["start"] and
                changed["final"] == obj["final"] and
                changed["local_profile"] == obj["local_profile"],
                "Scalar mutation changed counted widths/profile")
    else:
        scalars = [event for event in changed["forward"] if event[0] == "scalar"]
        event = scalars[88 % len(scalars)]
        event[1][-2] += 1
        for direction in ("forward", "backward"):
            require(Counter(e[-1] for e in obj[direction]
                            if e[0] in ("climb", "center")) ==
                    Counter(e[-1] for e in changed[direction]
                            if e[0] in ("climb", "center")),
                    "Scalar mutation changed child counts")
    require(obj != changed, "Scalar negative control is a no-op")
    return json.dumps(changed, separators=(",", ":")).encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=5,
                        help="same-input timing pairs (1..31), no speed threshold")
    parser.add_argument("--out", type=Path, help="optional evidence receipt")
    args = parser.parse_args()
    require(1 <= args.pairs <= 31, "Use 1..31 timing pairs")
    adapter = load_adapter()
    sources = json.loads((HERE / "SOURCES.json").read_text())
    require(sources["base_commit"] ==
            "66849e1475c930fd7732b1a0067ffee7e1e95f60", "Wrong upstream base")
    for item in sources["files"]:
        raw = (ROOT / item["path"]).read_bytes()
        require(digest(raw) == item["sha256"], "Fixture source drift: " + item["path"])
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == item["git_blob"], "Fixture Git blob changed")
        if "payload_sha256" in item:
            require(digest(gzip.decompress(raw)) == item["payload_sha256"],
                    "Fixture payload pin changed")
    historical = json.loads((PKG / "comparison/PR622-NATIVE-HASHES.json").read_text())
    originals = {}
    for pid in ("ck", "jp8"):
        for filename in NAMES:
            key = pid + "/" + filename
            raw = (FIXTURE / (pid + "-local") / filename).read_bytes()
            require(digest(raw) == historical[key], "Historical native container changed")
            require(digest(gzip.decompress(raw)) == adapter.PAYLOAD_HASHES[key],
                    "Adapter payload pin not derived from historical container")
            originals[key] = raw
    expected = (HERE / "EXPECTED-OWNER-CHECK.json").read_bytes()
    expected_obj = json.loads(expected)
    require(expected_obj["calls"] == 72 and expected_obj["roles"] == 35424,
            "Unexpected reference scope")
    require(sum(int(r) * n for r, n in expected_obj["profile"].items()) == 520704,
            "Unexpected rank mass")

    controls = []
    timings = {"original": [], "adapted": [], "order": []}
    with tempfile.TemporaryDirectory(prefix="pr626-native-payload-") as temporary:
        temp = Path(temporary)
        work = temp / "native"
        work.mkdir()
        for key, raw in originals.items():
            pid, filename = key.split("/")
            p = work / (pid + "-local") / filename
            p.parent.mkdir(exist_ok=True)
            p.write_bytes(raw)
        output = temp / "receipt.json"
        # Counterbalanced deterministic order; OS seed 88 selects original first.
        for pair in range(args.pairs):
            order = ("original", "adapted") if (88 + pair) % 2 == 0 else ("adapted", "original")
            timings["order"].append(list(order))
            for name in order:
                result = run(ORIGINAL if name == "original" else ADAPTED, work, output)
                accepted(result, expected)
                timings[name].append(result["seconds"])

        for key, raw in originals.items():
            pid, filename = key.split("/")
            path = work / (pid + "-local") / filename
            payload = gzip.decompress(raw)
            header = bytearray(raw)
            header[4:8] = (88).to_bytes(4, "little")
            middle = len(payload) // 2
            representations = {
                "mtime-only": bytes(header),
                "level-1": gzip.compress(payload, compresslevel=1, mtime=88),
                "level-9": gzip.compress(payload, compresslevel=9, mtime=88),
                "two-members": (gzip.compress(payload[:middle], mtime=88) +
                                gzip.compress(payload[middle:], mtime=88)),
            }
            for kind, variant in representations.items():
                require(variant != raw and gzip.decompress(variant) == payload,
                        "Representation control is not equivalent")
                path.write_bytes(variant)
                old = run(ORIGINAL, work, output)
                rejected(old, "unchanged PR622 native word and program")
                new = run(ADAPTED, work, output)
                accepted(new, expected)
                controls.append({"input": key, "control": kind,
                                 "original": "rejected", "adapted": "identical receipt"})

            bad_crc = bytearray(raw)
            bad_crc[-8] ^= 1
            mutations = {
                "scalar-coefficient": gzip.compress(changed_scalar(payload, filename), mtime=88),
                # Same JSON object is intentionally rejected: only gzip representation
                # is normalized, not formatting or any uncompressed byte.
                "payload-whitespace": gzip.compress(payload + b" ", mtime=88),
                "crc-corruption": bytes(bad_crc),
                "truncated": raw[:-4],
            }
            for kind, variant in mutations.items():
                path.write_bytes(variant)
                for script in (ORIGINAL, ADAPTED):
                    result = run(script, work, output)
                    rejected(result, "unchanged PR622 native word and program"
                             if kind in ("scalar-coefficient", "payload-whitespace") else None)
                controls.append({"input": key, "control": kind,
                                 "original": "rejected", "adapted": "rejected"})
            path.write_bytes(raw)

        # Explicit provider paths must receive the same payload checks.
        overrides = temp / "overrides"
        shutil.copytree(work, overrides)
        for key, raw in originals.items():
            pid, filename = key.split("/")
            p = overrides / (pid + "-local") / filename
            p.write_bytes(gzip.compress(gzip.decompress(raw), compresslevel=1, mtime=88))
        providers = tuple((pid, overrides / (pid + "-local")) for pid in ("ck", "jp8"))
        accepted(run(ADAPTED, work, output, providers), expected)
        controls.append({"control": "explicit-provider-overrides", "adapted": "identical receipt"})
        rejected(run(ADAPTED, work, output, (("unknown", overrides),)),
                 "known provider overrides")
        controls.append({"control": "unknown-provider", "adapted": "rejected"})

        # Isolate source-drift controls in a minimal relocated copy. No repository
        # file is modified, and the original mathematical scripts stay pinned.
        shadow = temp / "shadow"
        for item in sources["files"]:
            src, dst = ROOT / item["path"], shadow / item["path"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
        relocated = shadow / ADAPTED.relative_to(ROOT)
        relocated.parent.mkdir(parents=True)
        shutil.copyfile(ADAPTED, relocated)
        accepted(run(relocated, work, output), expected)
        controls.append({"control": "relocated-adapter", "adapted": "identical receipt"})
        for relative in adapter.SOURCE_HASHES:
            path = shadow / "research/complex-k492-owner-repair" / relative
            raw = path.read_bytes()
            path.write_bytes(raw + b"\n")
            rejected(run(relocated, work, output), "Source pin mismatch: " + relative)
            controls.append({"control": "source-drift:" + relative, "adapted": "rejected"})
            path.write_bytes(raw)

    stable = {
        "status": "PASS_PR626_NATIVE_PAYLOAD_BINDING",
        "base_commit": sources["base_commit"], "assignment_seed": 88,
        "native_inputs": len(originals), "representation_controls": 16,
        "payload_and_container_negative_controls": 16,
        "additional_controls": 6,
        "owner_receipt_sha256": digest(expected),
        "calls": 72, "roles": 35424, "rank_mass": 520704,
        "controls": controls,
        "scope": "Exact decompressed-byte binding plus unchanged finite owner/profile/moment checks; no supplier rebuild, new kappa or all-size theorem.",
    }
    require(len(controls) == 38, "Control inventory changed")
    timing_receipt = {
        **timings,
        "median_seconds": {name: statistics.median(timings[name])
                           for name in ("original", "adapted")},
        "scope": "Complete fresh subprocesses, same original containers, alternating order; OS caches not flushed; reproducibility fix, no speedup claim.",
    }
    receipt = {
        "result": stable,
        "timing": timing_receipt,
        "environment": {"python": sys.version, "platform": platform.platform(),
                        "zlib_runtime": zlib.ZLIB_RUNTIME_VERSION,
                        "zlib_compile": zlib.ZLIB_VERSION,
                        "optimized_children": True},
    }
    if args.out:
        args.out.write_text(json.dumps(receipt, indent=2) + "\n")
    print(stable["status"] + " inputs=4 representations=16 rejected_mutants=16 additional=6")
    print("Identical full receipts: 72 calls, 35424 roles, rank mass 520704, both exact moments.")
    print("Median same-input seconds: original={:.6f}, adapted={:.6f}".format(
        timing_receipt["median_seconds"]["original"],
        timing_receipt["median_seconds"]["adapted"]))


if __name__ == "__main__":
    main()
