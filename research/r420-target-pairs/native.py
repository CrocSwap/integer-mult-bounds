"""Unmodified PR493 cohort checkers for the target-pair experiment.

Prepared by Sagar Thakrar with substantial OpenAI Codex assistance; Apache-2.0.
The checkers and exporter are credited to their authors in the pinned sources.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import shlex
import struct
import subprocess
import sys
import tempfile


SOURCE_HASHES = {
    "code/bit/export_records.py": "8a5999601f917dbb492bb9ae9a344611f18cc7cedc53dc3c76496a369e530eb3",
    "code/bit/regression/stage_cohort.py": "6c288f6f234b528c1a7c0a4adfb724e91e0fe6b18c8dffad96af3f973de1829a",
    "code/bit/checkers/legality_h.cpp": "6c1ef2b24e57781d6951c172a1024fc4300e6fd392c9d6672079a7806ab663b3",
    "code/bit/checkers/columns_k.cpp": "1c344d18fcd494eeca93e259f10cafae7705780e6592f6dcb35b34752dab9bc2",
    "code/bit/checkers/json.hpp": "aaf127c04cb31c406e5b04a63f1ae89369fccde6d8fa7cdda1ed4f32dfc5de63",
    "portable-include/bits/stdc++.h": "420094be2af295eed03a983dd66debbbe9cfb78d8252859f4498a615a0074b99",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def positive_prefix(records, n):
    """Exact integer replay of the cancellation-free local row bounds."""
    events = list(struct.iter_unpack("<6i", records.read_bytes()))
    maxima = []
    for reverse in (False, True):
        norms = [1] * (n + 1)
        maximum = 1
        opened = False
        for op, dst, src, coefficient, frame, rank in (reversed(events) if reverse else events):
            if op == 0:
                continue
            if reverse and op in (2, 3):
                op = 5 - op
            if op == 1:
                norms[dst] += abs(coefficient) * norms[src]
                maximum = max(maximum, norms[dst])
            elif op == 2:
                require(not opened, "nested prefix copy")
                norms[n] = norms[dst]
                opened = True
            else:
                require(op == 3 and opened, "invalid prefix erase")
                norms[n] = 0
                opened = False
        require(not opened, "unclosed prefix copy")
        maxima.append(maximum)
    forward, backward = maxima
    payload = 64 * forward**3 * backward**2
    return {
        "forward": str(forward), "reverse": str(backward),
        "native_payload_upper": str(payload), "native_payload_bits": payload.bit_length(),
    }


def verify_native(original_word, changed_word):
    """Return fresh official 5/9/11-stage receipts and corruption controls."""
    package = Path(__file__).resolve().parents[1] / "e8-bit-carrier-skeleton"
    for relative, expected in SOURCE_HASHES.items():
        require(hashlib.sha256((package / relative).read_bytes()).hexdigest() == expected,
                "source hash mismatch: " + relative)
    for word in (original_word, changed_word):
        require((word["h"], word["v"], word["R"]) == (8, 120, 420), "wrong R420 dimensions")
    bit = package / "code/bit"
    checkers = bit / "checkers"

    def run(args, rejected=False):
        result = subprocess.run(list(map(str, args)), text=True, capture_output=True)
        if rejected:
            require(result.returncode != 0, "native corruption control was accepted")
            require("local defining-decoder full formal column" in result.stderr,
                    "unexpected native rejection: " + result.stderr)
        elif result.returncode:
            raise RuntimeError(f"command failed: {shlex.join(map(str, args))}\n{result.stderr}")
        return result

    with tempfile.TemporaryDirectory(prefix="r420-target-pairs-") as temporary:
        work = Path(temporary)
        compiler = shlex.split(os.environ.get("CXX", "c++"))
        flags = ["-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9", "-DVPORTS=120", "-DRHELP=420",
                 "-I" + str(package / "portable-include"), "-I" + str(checkers),
                 "-I" + os.environ.get("BOOST_INCLUDE", "/usr/include")]
        run([*compiler, *flags, checkers / "legality_h.cpp", "-o", work / "legality"])
        for pairs in (2, 4, 5):
            run([*compiler, *flags, f"-DKPAIRS={pairs}", checkers / "columns_k.cpp",
                 "-o", work / f"columns-{pairs}"])

        def export(word, name):
            directory = work / name
            directory.mkdir()
            path = directory / "word.json"
            path.write_text(json.dumps(word, separators=(",", ":")))
            run([sys.executable, "-I", "-B", bit / "export_records.py", path, directory / "records"])
            run([sys.executable, "-I", "-B", bit / "regression/stage_cohort.py",
                 directory / "records", directory / "records", directory / "cin", directory / "cout"])
            run([work / "legality", directory / "cin", directory / "cout", directory / "legality.json"])
            return directory

        def columns(directory, pairs):
            output = directory / f"columns-{pairs}.json"
            run([work / f"columns-{pairs}", directory / "cout/COHORT249-RECORDS.bin", output])
            receipt = json.loads(output.read_text())
            receipt.pop("seconds")
            receipt.pop("local_scalar_stream")
            require(receipt["formal_columns_checked"] == 2 * pairs * 120 + 420, "formal column count")
            require(len(receipt["stages"]) == 2 * pairs + 1, "native stage count")
            require(len(receipt["negative_controls"]) == 6 * (pairs - 1), "omitted bridge control count")
            require(all(item["rejected"] for item in receipt["negative_controls"]), "bridge control accepted")
            return receipt

        receipts = {}
        for name, word in (("baseline", original_word), ("target_pairs", changed_word)):
            directory = export(word, name)
            prefix = positive_prefix(directory / "cout/COHORT249-RECORDS.bin", 660)
            cohorts = {str(2 * pairs + 1): columns(directory, pairs) for pairs in (2, 4, 5)}
            for receipt in cohorts.values():
                require([row["cancellation_free_signed_row_l1_upper"]
                         for row in receipt["signed_lift_prefix"]] == [prefix["forward"], prefix["reverse"]],
                        "independent positive prefix disagrees")
                require(receipt["payload_prefix_upper"] == prefix["native_payload_upper"], "native payload differs")
                require(receipt["payload_prefix_bits"] == prefix["native_payload_bits"], "native payload bits differ")
            legality = json.loads((directory / "legality.json").read_text())
            receipts[name] = {
                "legality": {key: legality[key] for key in (
                    "status", "records", "common_frame_ADDs", "nested_MOVEs", "copies", "erasures",
                    "rank_mass", "paid_histogram", "all_final_frames_pass")},
                "prefix": prefix,
                "cohorts": {stage: {
                    **{key: receipt[key] for key in (
                        "status", "formal_columns_checked", "local_scalar_additions", "bridge_additions",
                        "fresh_center_copies", "reverse_fresh_center_copies", "local_raw_H")},
                    "stage_count": len(receipt["stages"]),
                    "omitted_bridge_controls_rejected": len(receipt["negative_controls"]),
                } for stage, receipt in cohorts.items()},
            }

        require(receipts["baseline"]["legality"]["paid_histogram"] == receipts["target_pairs"]["legality"]["paid_histogram"],
                "paid histogram changed")
        require(receipts["baseline"]["cohorts"]["5"]["local_raw_H"] == receipts["target_pairs"]["cohorts"]["5"]["local_raw_H"],
                "local raw histogram changed")
        controls = {}
        dropped = copy.deepcopy(changed_word)
        target_gates = [i for i, (_, dst, sources) in enumerate(dropped["D"])
                        if 120 <= dst < 240 and any(120 <= source < 240 for source in sources)]
        require(target_gates, "no target-pair gate to mutate")
        del dropped["D"][target_gates[-1]]
        wrong_helper = copy.deepcopy(changed_word)
        for _, _, sources in wrong_helper["D"]:
            if any(source >= 240 for source in sources):
                index = next(i for i, source in enumerate(sources) if source >= 240)
                sources[index] = next(source for source in range(240, 660) if source not in sources)
                break
        else:
            raise AssertionError("no helper read to mutate")
        for name, mutant in (("dropped_target_unmix", dropped), ("wrong_helper_read", wrong_helper)):
            directory = export(mutant, name)
            for pairs in (2, 4, 5):
                run([work / f"columns-{pairs}", directory / "cout/COHORT249-RECORDS.bin",
                     directory / f"columns-{pairs}.json"], rejected=True)
            controls[name] = {"legality_passed": True, "formal_columns_rejected_stages": [5, 9, 11]}
        return {"source_sha256": SOURCE_HASHES, "receipts": receipts, "negative_controls": controls}
