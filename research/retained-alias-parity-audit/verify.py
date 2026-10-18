#!/usr/bin/env python3
"""Retained-helper alias audit. theon199, with OpenAI Codex; Apache-2.0."""

import argparse
import copy
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import types
from collections import Counter

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
CHECKER = "research/e8-bit-p111-tuned/code/xcheck_p.py"
EXPORTER = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
SELECTED = "research/community-frontier1094-audit/SELECTED-SOURCE.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticated(root):
    sources = json.loads((PACKAGE / "SOURCES.json").read_bytes())
    data = {}
    for row in sources["files"]:
        if row["usage"] == "input":
            body = (root / row["path"]).read_bytes()
            require(hashlib.sha256(body).hexdigest() == row["sha256"],
                    "source mismatch: " + row["path"])
            data[row["path"]] = body
    selected = json.loads(data[SELECTED])["files"]
    for path in (WORD, CHECKER, EXPORTER):
        require(hashlib.sha256(data[path]).hexdigest() == selected[path],
                "selected-source binding: " + path)
    return data


def discrepancy(retained, row):
    """Exact criterion: XOR even-positive slot multiplicities by helper."""
    grouped = set()
    for k, count in Counter(row).items():
        if count % 2 == 0:
            grouped.symmetric_difference_update([retained[k]])
    return sorted(grouped)


def direct_scatter(retained, row, values):
    """Evaluate occurrence and membership loops, without the criterion."""
    symbolic = 0
    for k in row:
        symbolic ^= values[retained[k]]
    exported = 0
    for k, q in enumerate(retained):
        if k in row:
            exported ^= values[q]
    return symbolic, exported


def partitions(size, prefix=()):
    """Restricted-growth strings: every alias pattern exactly once."""
    if len(prefix) == size:
        yield prefix
        return
    for value in range(max(prefix, default=-1) + 2):
        yield from partitions(size, prefix + (value,))


def exhaustive():
    cases = agreement = extra = patterns = 0
    smallest = None
    for size in range(1, 5):
        for retained in partitions(size):
            patterns += 1
            values = [1 << q for q in range(max(retained) + 1)]
            for length in range(7):
                for row in itertools.product(range(size), repeat=length):
                    left, right = direct_scatter(retained, row, values)
                    criterion = not discrepancy(retained, row)
                    require((left == right) == criterion, "grouped criterion")
                    odd = all(count % 2 for count in Counter(row).values())
                    require(not odd or criterion, "odd condition remains sufficient")
                    cases += 1
                    agreement += criterion
                    if criterion and not odd:
                        extra += 1
                        candidate = (len(row), size, retained, row)
                        if smallest is None or candidate < smallest:
                            smallest = candidate
    require(smallest == (4, 2, (0, 0), (0, 0, 1, 1)),
            "minimal alias cancellation changed")
    return dict(patterns=patterns, cases=cases, agreement=agreement,
                agreement_with_even_multiplicity=extra,
                smallest=dict(retained=list(smallest[2]), row=list(smallest[3])))


def word_replay(word):
    """Independent simultaneous-column F2 interpreter of the JSON word."""
    n, v = 2 * word["v"] + word["R"], word["v"]
    values = [1 << r for r in range(n)]
    for section in ("D", "A", "scatter", "B", "C"):
        if section == "scatter":
            copied = tuple(values[q] for q in word["ret"])
            for t, row in enumerate(word["scatter"]):
                for k in row:
                    values[v + t] ^= copied[k]
        else:
            for _frame, dest, sources in word[section]:
                require(dest not in sources and len(set(sources)) == len(sources),
                        "invertible prefix/suffix gate premise")
                increment = 0
                for source in sources:
                    increment ^= values[source]
                values[dest] ^= increment
    return values


def expected_values(word):
    n, v = 2 * word["v"] + word["R"], word["v"]
    values = [1 << r for r in range(n)]
    for t in range(v):
        values[v + t] ^= 1 << t
    return values


def record_replay(records, n):
    """Independent packed-record interpreter; MOVE has no scalar action."""
    require(len(records) % 24 == 0, "record alignment")
    values = [1 << r for r in range(n)] + [0]
    opened = None
    copy_ranks = []
    for op, first, second, coefficient, frame, phase in struct.iter_unpack("<6i", records):
        if op == 0:
            require(0 <= first < n, "MOVE role")
        elif op == 1:
            require(0 <= first < n and 0 <= second <= n and coefficient == 1, "ADD shape")
            require(second < n or opened is not None, "live copied input")
            values[first] ^= values[second]
        elif op == 2:
            require(opened is None and 0 <= first < n and second == n, "COPY shape")
            values[n], opened = values[first], first
            copy_ranks.append(phase)
        elif op == 3:
            require(opened == first and second == n, "ERASE binding")
            require(values[n] == values[first], "ERASE value changed")
            values[n], opened = 0, None
        else:
            raise ValueError("record opcode")
    require(opened is None and values[n] == 0, "closed copy lifetime")
    return values[:-1], copy_ranks


def exported(body, word, directory):
    directory.mkdir()
    script, source, output = directory / "export.py", directory / "word.json", directory / "out"
    script.write_bytes(body)
    source.write_text(json.dumps(word), encoding="utf-8")
    run = subprocess.run([sys.executable, "-I", "-B", str(script), str(source), str(output)],
                         capture_output=True, text=True, timeout=30, check=False)
    require(run.returncode == 0, "export failed: " + run.stderr)
    records = (output / "249-records.bin").read_bytes()
    require(len(records) <= 30000 * 24, "bounded records")
    return records


def symbolic(module, word):
    _, labels, full, hypotheses, conclusions, _ = module.check(word)
    require(labels["labels"] == 111 and full["columns"] == 661, "symbolic dimensions")
    require(len(hypotheses) == 5 and all(x is True for x in hypotheses.values()), "H1-H5")
    require(len(conclusions) == 4 and all(x is True for x in conclusions.values()), "conclusions")
    return dict(columns=full["columns"], scatter_terms=full["scatter_terms"],
                copy_ranks=[x["rank"] for x in full["totals"]],
                hypotheses=hypotheses, conclusions=conclusions)


def fixtures(word):
    require(len(word["ret"]) == 9 and len(set(word["ret"])) == 9, "selected injectivity")
    k = 62 % len(word["ret"])
    t = next((62 + i) % word["v"] for i in range(word["v"])
             if k not in word["scatter"][(62 + i) % word["v"]])
    require((k, t) == (8, 64), "deterministic seed selection")
    require(word["ret"][k] == 480 and k not in word["scatter"][t], "seed site")
    balanced = copy.deepcopy(word)
    balanced["ret"].append(word["ret"][k])
    balanced["scatter"][t].extend([k, k, 9, 9])
    unpaired = copy.deepcopy(balanced)
    unpaired["scatter"][t] = unpaired["scatter"][t][:-2]
    distinct = copy.deepcopy(balanced)
    distinct["ret"][9] = word["ret"][7]
    return dict(baseline=word, balanced_alias=balanced,
                unpaired_even=unpaired, distinct_helpers=distinct)


def audit(root):
    data = authenticated(root)
    module = types.ModuleType("authenticated_checker")
    # Compile authenticated bytes directly: no mutable import or bytecode cache.
    exec(compile(data[CHECKER], CHECKER, "exec", optimize=0), module.__dict__)
    word = json.loads(gzip.decompress(data[WORD]))
    results = {}
    with tempfile.TemporaryDirectory(prefix="retained-alias-audit-") as temporary:
        for name, fixture in fixtures(word).items():
            checked = symbolic(module, fixture)
            literal = word_replay(fixture)
            require(literal == expected_values(fixture), "symbolic positive fixture")
            records = exported(data[EXPORTER], fixture, Path(temporary) / name)
            lowered, ranks = record_replay(records, len(literal))
            differences = [(i, a ^ b) for i, (a, b) in enumerate(zip(literal, lowered)) if a != b]
            require((not differences) == (name in ("baseline", "balanced_alias")), "alias control")
            criterion = all(not discrepancy(fixture["ret"], row) for row in fixture["scatter"])
            require(criterion == (not differences), "full-size criterion")
            if differences:
                require(len(differences) == 1 and differences[0][0] == 175
                        and differences[0][1] >> 480 & 1, "dirty input 480 witness")
            require(ranks == checked["copy_ranks"], "COPY charge agrees with checker")
            results[name] = dict(symbolic=checked, records=len(records) // 24,
                records_sha256=hashlib.sha256(records).hexdigest(),
                scatter_adds=sum(e[0] == 1 and e[-1] == 3 for e in struct.iter_unpack("<6i", records)),
                copy_rank_sum=sum(ranks), grouped_criterion=criterion,
                exported_equals_symbolic=not differences,
                differences=[dict(output=i, input_columns=[j for j in range(661) if delta >> j & 1])
                             for i, delta in differences])
            if name == "balanced_alias":
                broken = remove_partner(records, len(literal))
                require(record_replay(broken, len(literal))[0] != literal, "omitted ADD detected")
    single = copy.deepcopy(word)
    single["scatter"][64].append(8)
    try:
        module.check(single)
    except module.Reject as error:
        require("targets not y + x" in str(error), "single occurrence rejection reason")
    else:
        raise ValueError("single occurrence accepted")
    return dict(status="PASS_RETAINED_ALIAS_PARITY_AUDIT", seed=62, target_row=64,
                retained_index=8, retained_helper=480, exhaustive=exhaustive(), fixtures=results,
                controls=["unpaired_even", "distinct_helpers", "omitted_export_ADD", "single_occurrence"])


def remove_partner(records, n):
    events = list(struct.iter_unpack("<6i", records))
    opened = None
    for index, event in enumerate(events):
        if event[0] == 2:
            opened = event[1]
        elif event[0] == 3:
            opened = None
        elif event == (1, 111 + 64, n, 1, 0, 3) and opened == 480:
            return b"".join(struct.pack("<6i", *e) for e in events[:index] + events[index + 1:])
    raise ValueError("missing cancellation partner")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    result = audit(ROOT)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write_receipt:
        args.write_receipt.write_text(payload, encoding="utf-8")
    else:
        require(payload == (PACKAGE / "EXPECTED.json").read_text(encoding="utf-8"), "exact receipt")
    print(result["status"], "columns=661 cases=" + str(result["exhaustive"]["cases"]),
          "balanced_alias=agrees controls=4 no_new_kappa")


if __name__ == "__main__":
    main()
