# SPDX-License-Identifier: GPL-3.0-or-later
"""Passive exact GCC patch projection and narrow function comparison only."""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
F = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def lf_lines(raw):
    parts = raw.split(b"\n")
    return [line + b"\n" for line in parts[:-1]] + ([parts[-1]] if parts[-1] else [])


def target(raw):
    name = raw.split(b"\t", 1)[0].split(b" ", 1)[0]
    if name.startswith((b"a/", b"b/")):
        name = name[2:]
    if name.startswith(b"src/"):
        name = name[4:]
    return name


def project(raw, patch):
    # Independent exact-context application; no patch program, fuzz, or imports.
    lines, patch_lines = lf_lines(raw), lf_lines(patch)
    selected, pos, receipts = False, 0, []
    while pos < len(patch_lines):
        row = patch_lines[pos]
        if row.startswith(b"+++ "):
            selected = target(row[4:].rstrip(b"\n")) == b"gcc/gcc.cc"
        match = re.match(rb"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", row)
        if not selected or match is None:
            pos += 1
            continue
        old_count, new_count = int(match[2] or b"1"), int(match[4] or b"1")
        old, new = [], []
        pos += 1
        while len(old) < old_count or len(new) < new_count:
            require(pos < len(patch_lines), "truncated hunk")
            row = patch_lines[pos]
            require(row[:1] in (b" ", b"+", b"-"), "unsupported hunk body")
            if row[:1] in (b" ", b"-"):
                old.append(row[1:])
            if row[:1] in (b" ", b"+"):
                new.append(row[1:])
            pos += 1
        require(len(old) == old_count and len(new) == new_count and old,
                "hunk counts/insertion-only frontier")
        matches = [i for i in range(len(lines) - len(old) + 1)
                   if lines[i:i + len(old)] == old]
        require(len(matches) == 1, "nonunique or absent exact hunk context")
        index = matches[0]
        lines[index:index + len(old)] = new
        receipts.append(dict(actual_LF_line=index + 1, old_count=old_count, new_count=new_count))
    return b"".join(lines), receipts


def function(raw):
    start = raw.index(b"static void *\nfor_each_path (")
    end = raw.index(b"\n/* Callback for build_search_list.", start)
    return raw[start:end], raw[:start].count(b"\n") + 1


def main():
    pin_path = F / "implementation/c05_gcc_rules_sourcepins_v1.json"
    model_path = F / "implementation/c05_gcc_rules_derivation_v1.json"
    pins_raw, model_raw = pin_path.read_bytes(), model_path.read_bytes()
    require(sha(pins_raw) == "5564d0d2b47a5803c96b3767d838676e8f2427089e3b02cda1b1e62430a3c24d",
            "frozen source pins changed")
    require(sha(model_raw) == "efd4f9ec5742dfb60ce05cf9ff1fcb8d05820e3f1068e57303993ff1f6916e9d",
            "frozen source derivation changed")
    pins = {row["path"]: row for row in json.loads(pins_raw)["files"]}
    projection = next(row for row in json.loads(model_raw)["model"]["definite_patch_projection"]
                      if row["target"] == "gcc/gcc.cc")
    inputs = []

    def read(name):
        pin = pins[name]
        raw = (F / "source-artifacts" / name).read_bytes()
        require(len(raw) == pin["bytes"] and sha(raw) == pin["sha256"], "source bytes changed")
        inputs.append(dict(pin))
        return raw

    base = read("gcc-base-selected/gcc/gcc.cc")
    applied, receipts = base, []
    for patch in projection["patches"]:
        path = "gcc-debian-patch-inputs/debian/patches/" + patch["patch"]
        applied, hunks = project(applied, read(path))
        receipts.append(dict(path=path, hunks=hunks))
    require(sha(applied) == projection["definite_patch_projection_sha256"],
            "independent projection differs from frozen projection")
    original_function, original_line = function(base)
    applied_function, applied_line = function(applied)
    addition = (b"\t  len += MAX (strlen(DEFAULT_REAL_TARGET_MACHINE), multiarch_len) + 2; "
                b"/* triplet prefix for as, ld.  */\n")
    require(applied_function.count(addition) == 1 and
            applied_function.replace(addition, b"", 1) == original_function,
            "for_each_path has additional changes beyond allocation margin")
    (HERE / "for_each_path.base.cc.txt").write_bytes(original_function)
    (HERE / "for_each_path.definite-applied.cc.txt").write_bytes(applied_function)
    report = dict(schema="gcc13-prefix-source-comparison-v1", inputs=inputs,
                  frozen_sourcepins_sha256=sha(pins_raw), frozen_derivation_sha256=sha(model_raw),
                  base_sha256=sha(base), definite_applied_sha256=sha(applied), patches=receipts,
                  base_function_LF_line=original_line, applied_function_LF_line=applied_line,
                  base_function_sha256=sha(original_function), applied_function_sha256=sha(applied_function),
                  difference="one added allocation-margin line; callback visit ordering unchanged",
                  installed_applied_equivalence_proven=False, full_C05=False,
                  license="GPL-3.0-or-later", original_execution=False)
    encoded = (json.dumps(report, sort_keys=True, indent=2) + "\n").encode("ascii")
    (HERE / "SOURCE-COMPARISON-v1.json").write_bytes(encoded)
    print(json.dumps({"comparison_sha256": sha(encoded), "base_function_sha256": sha(original_function),
                      "applied_function_sha256": sha(applied_function),
                      "difference": report["difference"]}, sort_keys=True))


if __name__ == "__main__":
    main()
