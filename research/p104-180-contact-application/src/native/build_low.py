#!/usr/bin/env python3
"""Build the matched #7636 source and contact-379 combination with one ADD split."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path


HEAD = "7e68d8dd62d9a38c0f3c942262a7a85ca7125b75"
SOURCE_RAW = "98b8c12ece2f323a6ff5cac8c7ed2f78ba3835438ea56b16bd7d4698ec5ad5b2"
SOURCE_GZIP = "1b4e33c3e3b69d1f1b42d019a2e372ac612fa28494bd8da18a734618f9bda659"
C_RAW = "375f924e1588893680d39a194d29e5400bec4ab7e0b5db24b05f4cfe6fd05e15"
C_GZIP = "3fb11603e14fc9d67aff97e1b0e737f98c1395180ff71119fa64b4d8acaa8626"
LOWERED_SOURCE = "9ea1dab98cbd532af75ab780f284c513534d5df13fa366c3241a08a36c3610f8"
B_RAW = "9b5b66e93f91c9538525d8d7b1278e0f203058d5cd4e1351fa06f8315fdaa555"
SOURCE_CLEAR = "94809b766d041f6bb400df151de5702c5e8ec0a8a47c80ddfe5b2b3a5e0f09d2"
C_CLEAR = "11caf0ddb32cbd94c4d5842a3324e6236b551090080dea5598c71f9dee72c7ff"
PUBLIC = 1501
CLEARS = 180
SOURCE_EVENTS = 202668
SOURCE_SPLIT = 150836
COMBINED_SPLIT = 150834
ORIGINAL = ["ADD", 841, 284, "23184221/921600", 127]
SPLIT = [["ADD", 841, 284, "25", 127], ["ADD", 841, 284, "144221/921600", 127]]
OLD = {
    127153: ["MOVE", 902, 3, 618, False],
    127445: ["MOVE", 1091, 373, 618, False],
    127446: ["ADD", 1091, 902, "1/2", 618],
    127469: ["MOVE", 1091, 618, 733, False],
    130068: ["MOVE", 902, 618, 913, False],
    131142: ["MOVE", 379, 748, 1065, False],
    131294: ["MOVE", 379, 1065, 1072, False],
}
REPLACEMENT = {
    127153: ["MOVE", 902, 3, 373, False],
    127445: None,
    127446: ["ADD", 1091, 902, "1/2", 373],
    127469: ["MOVE", 1091, 373, 733, False],
    130068: ["MOVE", 902, 373, 913, False],
    131142: None,
    131294: ["MOVE", 379, 748, 1072, False],
}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def pinned(path, expected):
    require(path.is_file() and not path.is_symlink(), f"missing or symlink input {path}")
    data = path.read_bytes()
    require(sha(data) == expected, f"SHA-256 changed for {path}")
    return data


def load_word(path, gzip_sha, raw_sha):
    raw = gzip.decompress(pinned(path, gzip_sha))
    require(sha(raw) == raw_sha, f"decoded SHA-256 changed for {path}")
    return json.loads(raw)


def write_bytes(path, contents):
    with path.open("xb") as stream:
        stream.write(contents)


def write_json(path, value):
    write_bytes(path, (json.dumps(value, sort_keys=True, indent=2) + "\n").encode())


def read_certificates(path, digest, word):
    cert = json.loads(pinned(path, digest))
    require(cert.keys() == {"clear_event_index"}, "source CLEAR schema")
    rows = cert["clear_event_index"]
    clocks = {str(i) for i, e in enumerate(word["program"]) if e[0] == "CLEAR"}
    require(len(clocks) == len(rows) == CLEARS and rows.keys() == clocks, "all 180 exact CLEAR clocks")
    return rows


def apply_splice(source, replacements):
    new, clock_map = [], {}
    for clock, event in enumerate(source["program"]):
        if clock in replacements:
            require(event == OLD[clock], f"source anchor {clock}")
            event = replacements[clock]
        if event is not None:
            clock_map[clock] = len(new)
            new.append(event)
    return {**source, "program": new}, clock_map


def lower(word, clock):
    program = word["program"]
    require(program[clock] == ORIGINAL and program.count(ORIGINAL) == 1, f"unique scalar split at {clock}")
    require(all(op[0] != "CLEAR" for op in program[clock:]), "a CLEAR unexpectedly follows the split")
    return {**word, "program": program[:clock] + SPLIT + program[clock + 1:]}


def matched(input_root):
    src = load_word(input_root / "source-word.json.gz", SOURCE_GZIP, SOURCE_RAW)
    raw_c = load_word(input_root / "raw-combined.json.gz", C_GZIP, C_RAW)
    require(len(src["program"]) == SOURCE_EVENTS, "source length")
    built_c, clock_map = apply_splice(src, REPLACEMENT)
    require(built_c == raw_c and len(raw_c["program"]) == SOURCE_EVENTS - 2,
            "frozen combined word differs from the seven source-clock anchors")
    cert_s = read_certificates(input_root / "source-clear.json", SOURCE_CLEAR, src)
    cert_c = read_certificates(input_root / "combined-clear.json", C_CLEAR, raw_c)
    require({str(clock_map[int(clock)]): terms for clock, terms in cert_s.items()} == cert_c,
            "combined certificate transport")
    repaired_source, repaired_c = lower(src, SOURCE_SPLIT), lower(raw_c, COMBINED_SPLIT)
    require(sha(canonical(repaired_source)) == LOWERED_SOURCE, "match the earlier repaired source exactly")
    require(clock_map[SOURCE_SPLIT] == COMBINED_SPLIT, "combined prior clock of the lowered ADD")
    return src, repaired_source, repaired_c, clock_map, cert_s, cert_c


def bind_word(out, word, terms, clock):
    out.mkdir()
    raw = canonical(word)
    gzip_bytes = gzip.compress(raw, mtime=0)
    cert_bytes = (json.dumps({"clear_event_index": terms}, sort_keys=True, indent=2) + "\n").encode()
    write_bytes(out / "WORD.json.gz", gzip_bytes)
    write_bytes(out / "CLEAR-CERTIFICATES.json", cert_bytes)
    return {"raw_sha256": sha(raw), "canonical_sha256": sha(raw), "gzip_sha256": sha(gzip_bytes),
            "clear_sha256": sha(cert_bytes), "events": len(word["program"]), "parent_split_clock": clock}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    args = parser.parse_args()
    authorization = json.loads(args.authorization.read_bytes())
    require(authorization["public_claim"] and authorization["running_event"]
            and authorization["source_raw_sha256"] == SOURCE_RAW and authorization["raw_combined_sha256"] == C_RAW,
            "authorization does not name this supplemental source and candidate")
    _, source, candidate, clock_map, cert_s, cert_c = matched(args.inputs)
    args.out.mkdir(exist_ok=False)
    sr = bind_word(args.out / "source", source, cert_s, SOURCE_SPLIT)
    cr = bind_word(args.out / "candidate", candidate, cert_c, COMBINED_SPLIT)
    receipt = {"status": "PASS_7636_MATCHED_SCALAR_LOWERING_BUILD", "source_head": HEAD,
               "source_parent_raw_sha256": SOURCE_RAW, "candidate_parent_raw_sha256": C_RAW,
               "source": sr, "candidate": cr, "authorization": authorization,
               "role_379_phase_control_clock": clock_map[131294], "contact_control_clock": clock_map[127446],
               "source_cuts": [{"clock": j, "original": OLD[j], "candidate_clock": clock_map.get(j),
                                "replacement": REPLACEMENT[j]} for j in OLD],
               "lowering": {"old": ORIGINAL, "new": SPLIT}}
    write_json(args.out / "BINDING.json", receipt)
    print(f"{receipt['status']} source={sr['raw_sha256']} candidate={cr['raw_sha256']}", flush=True)


if __name__ == "__main__":
    main()
