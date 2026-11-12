#!/usr/bin/env python3
"""Complete #7363's residual using at most four new exact support evaluations.

The transfer argument reuses ToikY's reversible bank method in #7367.
The two pinned trace and pairing implementations come from #7363.
"""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from time import monotonic

ROOT = Path(__file__).resolve().parent
SOURCE = "a0502b0b30a4a4a0e9a37c08e83febbd515c5955"
BASE = "e54523517d0f03e58352e647c403a5af3e525a57"
WORD_HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER_HEAD = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PACKAGE = "research/p104-rank-eight-fixed-paid-bank-bound"
MANIFEST_SHA = "99aab01167c7306be2fa62281c225f3bf74fcfdadf107516d3253edd5e46d15a"
SEEDS = ((40243, 242), (41740, 242), (45266, 242))
NEW = ((45270, 242), (45277, 242), (45435, 242), (45676, 1091))
ANCHORS = SEEDS + NEW


def need(value, reason):
    if not value:
        raise ValueError(reason)


def digest(data):
    return sha256(data).hexdigest()


def unique(pairs):
    out = dict(pairs)
    need(len(out) == len(pairs), "duplicate JSON key")
    return out


def decode(data):
    return json.loads(data, object_pairs_hook=unique)


def checked(path, expected):
    data = path.read_bytes()
    need(digest(data) == expected, f"source digest changed: {path.name}")
    return data


def add(a, b, factor):
    for k, v in b.items():
        z = a.get(k, 0) + factor * v
        if z:
            a[k] = z
        else:
            a.pop(k, None)


def as_text(v):
    return {str(i): str(q) for i, q in sorted(v.items())}


def coord(v):
    return {int(i): Q(x) for i, x in v.items()}


def dot(a, b):
    return sum((q * b.get(i, 0) for i, q in a.items()), Q(0))


def span(basis):
    s = {0}
    for x in basis:
        need(x not in s, "independent chart basis")
        s |= {x ^ y for y in s}
    return s


def barrier(event, live, f, n):
    """An event outside the bank is neutral; only internal public shears/scales may touch it."""
    op, r, *a = event
    here = r < n and live[r] == f
    if op == "MOVE":
        return r < n and (here or a[1] == f)
    if op in ("ADD", "COPY"):
        src = a[0]
        peer = src < n and live[src] == f
        return (here or peer) if op == "COPY" else here != peer
    if op == "SCALE":
        return here and not Q(a[0])
    need(op in ("INIT", "CLEAR") and r >= n, "owned lifecycle")
    return False


def layout(word, keys, cohort):
    """Track actual coframes; collect public banks and start-of-epoch cuts."""
    n = word["public"]
    live = word["initial"] + [None] * word["owned_fields"]
    fs = {f for _, f in keys}
    target = span(word["frames"][245])
    need(all(len(word["frames"][f]) == 4 and span(word["frames"][3]) <
             span(word["frames"][f]) < target for f in fs), "rank-four geometry")
    request = defaultdict(list)
    for t, f in sorted(keys):
        request[t].append(f)
    epochs = dict.fromkeys(fs, 0)
    facts, history = {}, {}
    start, end = min(request), max(request)
    for t, e in enumerate(word["program"]):
        for f in request.get(t, ()):
            here = [i for i, chart in enumerate(live) if chart == f]
            facts[t, f] = {"key": [t, f], "public": [i for i in here if i < n],
                           "owned": [i for i in here if i >= n],
                           "pivots": sorted(cohort.intersection(here)),
                           "epoch": epochs[f]}
            need(facts[t, f]["pivots"], "productive bank pivot")
        op, r, *a = e
        if start <= t < end:
            history[t] = (live[r], live[a[0]] if op in ("ADD", "COPY") else None)
        for f in fs:
            if barrier(e, live, f, n):
                epochs[f] = t + 1
        if op == "MOVE":
            need(live[r] == a[0] and a[2] == (r >= n), "literal MOVE binding")
            live[r] = a[1]
        elif op == "INIT":
            need(live[r] is None and r >= n, "literal INIT binding")
            live[r] = a[0]
        elif op == "CLEAR":
            need(live[r] == a[0] and r >= n, "literal CLEAR binding")
            live[r] = None
        else:
            need(live[r] == a[-1], "literal scalar binding")
            if op in ("ADD", "COPY"):
                need(live[a[0]] == live[r] and a[0] != r, "literal pair binding")
    need(set(facts) == set(keys), "missing cut")
    need(live == word["final"] + [None] * word["owned_fields"], "literal final chart vector")
    return facts, history


def transfer(tape, history, old, new):
    """Check the interval directly and construct both the basis change and its inverse."""
    start, f = old["key"]
    end, other = new["key"]
    bank = set(old["public"])
    need(f == other and old["public"] == new["public"] and start < end, "same-bank interval")
    mat = {r: {r: Q(1)} for r in bank}
    ops = []
    for t in range(start, end):
        op, r, *a = tape[t]
        dest_chart, src_chart = history[t]
        if op == "MOVE":
            need(r not in bank and not (not a[2] and f in a[:2]), "public MOVE across bank boundary")
        elif op in ("ADD", "COPY"):
            src = a[0]
            if r in bank or src in bank:
                need(op == "ADD" and r in bank and src in bank and
                     r != src and dest_chart == src_chart == f, "mixed or noninvertible bank contact")
                q = Q(a[1])
                add(mat[r], mat[src], q)
                ops.append((t, op, r, src, q))
        elif op == "SCALE" and r in bank:
            q = Q(a[0])
            need(dest_chart == f and q != 0, "invertible bank scale")
            mat[r] = {i: q * v for i, v in mat[r].items()}
            ops.append((t, op, r, None, q))
        elif op in ("INIT", "CLEAR"):
            need(r not in bank, "public lifecycle inside interval")
    inv = {r: {r: Q(1)} for r in bank}
    for _, op, r, src, q in reversed(ops):
        if op == "ADD":
            add(inv[r], inv[src], -q)
        else:
            inv[r] = {i: v / q for i, v in inv[r].items()}
    for a, b in ((mat, inv), (inv, mat)):
        for r, v in a.items():
            z = {}
            for k, q in v.items():
                add(z, b[k], q)
            need(z == {r: Q(1)}, "interval inverse")
    return dict(chart=f, start=start, stop=end,
                elementary_events=[list(tape[t]) + [t] for t, *_ in ops],
                matrix={str(r): as_text(row) for r, row in sorted(mat.items())},
                inverse={str(r): as_text(row) for r, row in sorted(inv.items())})


def paired_space(basis):
    """Canonical row space of the cut coefficients stacked with productive image."""
    pivots = {}
    for bank, image in basis:
        row = {(0, i): q for i, q in bank.items()} | {(1, i): q for i, q in image.items()}
        for p in sorted(pivots):
            if row.get(p, 0):
                add(row, pivots[p], -row[p])
        need(bool(row), "independent exact kernel basis")
        p = min(row)
        a = row[p]
        row = {i: v / a for i, v in row.items()}
        for old in pivots.values():
            if old.get(p, 0):
                add(old, row, -old[p])
        pivots[p] = row
    return sorted((i, sorted(v.items())) for i, v in pivots.items())


def primary(word, banks, cohort, files, deadline):
    rank = run_path(str(files / "inputs/paired_rank.py"))
    paired = run_path(str(files / "inputs/paired_support.py"))
    controls = paired["controls"]()
    by_time = {k[0]: row["public"] for k, row in banks.items()}
    f = rank["side"](word, by_time, cohort, deadline, False)
    r = rank["side"](word, by_time, cohort, deadline, True)
    need(set(f) == set(r) == set(by_time), "primary trace timed out or missed a cut")
    answer = {}
    for (t, chart) in banks:
        a, b = f[t], r[t]
        hit = paired["paired"](a, b, deadline) if any(c for _, c in a) and any(d for _, d in b) else None
        answer[t, chart] = (a, b, hit)
    return answer, controls


def checks():
    # Same-bank invertible shear and scale; a transfer into an outside role must fail.
    a = {"key": [0, 0], "public": [0, 1]}
    b = {"key": [2, 0], "public": [0, 1]}
    program = [["ADD", 0, 1, "-2", 0], ["SCALE", 1, "3/2", 0]]
    info = {0: (0, 0), 1: (0, None)}
    good = transfer(program, info, a, b)
    need(good["matrix"] == {"0": {"0": "1", "1": "-2"}, "1": {"1": "3/2"}}, "transfer control")
    for replacement, msg in [(["ADD", 2, 1, "-2", 0], "mixed or noninvertible"),
                             (["COPY", 0, 1, "-2", 0], "mixed or noninvertible"),
                             (["SCALE", 0, "0", 0], "invertible bank scale")]:
        try:
            transfer([replacement, program[1]], info, a, b)
        except ValueError as err:
            need(msg in str(err), "wrong control rejection")
        else:
            raise ValueError("unsafe transfer accepted")
    return ["shear_and_scale_inverse", "mixed_bank_contact", "copy_inside_bank", "zero_scale"]


def run(files, receipts):
    need(__debug__, "run with assertions enabled")
    pins = decode(checked(files / "LOCAL-PINS.json", MANIFEST_SHA))
    for rel, pin in pins.items():
        checked(files / rel, pin)
    fixed = decode((files / "receipts/SHA256.json").read_bytes())
    price = decode(checked(receipts / "input/price/PRICE.json", fixed["input/price/PRICE.json"]))
    remaining = [tuple(x) for x in decode((files / "receipts/UNRESOLVED.json").read_bytes())]
    need(len(remaining) == len(set(remaining)) == 29 and set(NEW) <= set(remaining) and
         not set(SEEDS) & set(remaining), "frozen residual denominator")
    need((price["head"], price["caller"]) == (WORD_HEAD, CALLER_HEAD) and
         price["productive_delta"] == {"4": 34, "8": -17} and price["paid_delta"] == {} and
         0 < Q(price["at_incumbent"]["gross_one"][1]) < 1, "inherited one-split economics")
    cohort = set(price["cohort"])
    word = decode(decompress((files / "inputs/7334-WORD.json.gz").read_bytes()))
    need(len(cohort) == 15 and len(word["program"]) == 76466 and
         all((word["initial"][i], word["final"][i]) == (3, 245) for i in cohort), "frozen cohort")
    geometry = decode(checked(receipts / "input/lead/GEOMETRY.json", fixed["input/lead/GEOMETRY.json"]))
    need(geometry["eligible_bank_count"] == 326 and
         set(remaining) <= {tuple(k) for k in geometry["all_representative_keys"]}, "frozen geometry denominator")
    past = {}
    for rel in ("independent/RESULT.json", "independent/FOLLOWUP.json"):
        inherited = decode(checked(receipts / rel, fixed[rel]))
        need(not inherited["timeout"] and not inherited["selected_unvisited"], "inherited exact receipt")
        for row in inherited["results"]:
            k = tuple(row["key"])
            if k in SEEDS:
                need(row["status"] == "no_exact_unit_pair" and
                     row["cut_pairing_matrix"] == row["endpoint_pairing_matrix"] == [["0"]],
                     "inherited zero pair")
                past[k] = row
    need(set(past) == set(SEEDS), "exact predecessor controls")
    stock = decode(checked(receipts / "lead/CONTINUATION.json", fixed["lead/CONTINUATION.json"]))
    modular = {tuple(x["key"]): x for x in stock["rows"]}
    facts, history = layout(word, set(remaining) | set(SEEDS), cohort)
    groups = defaultdict(list)
    for key, row in facts.items():
        groups[key[1], row["epoch"]].append(key)
    anchors = {}
    for group, keys in groups.items():
        seeds = sorted(set(keys) & set(SEEDS))
        keep = seeds[0] if seeds else min(keys)
        need(keep in ANCHORS and keep == min(keys), "frozen representative selection")
        anchors[keep] = sorted(k for k in keys if k in remaining)
    need(set(anchors) == set(ANCHORS), "four new independent classes and three inherited classes")
    controls = checks()
    certificate = {}
    for key, keys in anchors.items():
        a = facts[key]
        certificate[key] = {
            "anchor": list(key), "source": "inherited" if key in SEEDS else "new", "residual_keys": [list(k) for k in keys],
            "bank": a, "transfers": [transfer(word["program"], history, a, facts[k]) for k in keys if k != key],
        }
        if key in past:
            need(all(a[k] == past[key][k] for k in ("key", "public", "owned", "pivots")), "inherited live bank")

    # The positive 35-second allowance is per engine as in #7363.
    banks = {k: facts[k] for k in NEW}
    first, primary_controls = primary(word, banks, cohort, files, monotonic() + 34)
    exact = run_path(str(files / "engines/rational/exact_six.py"))
    rational = run_path(str(files / "engines/rational/r97_independent.py"))
    independent_controls = exact["checks"]()
    deadline = monotonic() + 34
    independent = exact["trace"](word, [banks[k] for k in NEW], deadline)
    evidence = []
    dispositions = dict.fromkeys(SEEDS, "no_exact_unit_pair")
    for k, (p, s) in zip(NEW, independent, strict=True):
        data = banks[k]
        m = modular[k]
        need(m["status"] == "dual_drop", "upstream modular residual")
        need(all(m[side][fld] == data[fld] for side in ("prefix", "suffix")
                 for fld in ("public", "owned", "pivots")), "independently rebound bank")
        row = rational["evaluate"](exact, data, p, s, cohort, deadline)
        fa, fb, candidate = first[k]
        aa = [(coord(x["a"]), coord(x["c"])) for x in row["prefix_pure_basis"]]
        bb = [(coord(x["b"]), coord(x["d"])) for x in row["suffix_pure_basis"]]
        need(paired_space(aa) == paired_space(fa) and paired_space(bb) == paired_space(fb),
             "independent exact stacked kernel spaces disagree")
        need(bool(candidate) == (row["status"] == "exact_unit_pair"), "independent pairing decision")
        need(row["cut_pairing_matrix"] == [[str(dot(a, b)) for b, _ in bb] for a, _ in aa] and
             row["endpoint_pairing_matrix"] == [[str(dot(c, d)) for _, d in bb] for _, c in aa],
             "separately recomputed pairing forms")
        evidence.append(row)
        dispositions[k] = row["status"]

    coverage = {k: dispositions[a] for a, cases in anchors.items() for k in cases}
    need(set(coverage) == set(remaining) and sum(map(len, anchors.values())) == 29,
         "complete residual coverage with no duplicate")
    for k, v in certificate.items():
        v["disposition"] = dispositions[k]
    positives = [list(k) for k in NEW if dispositions[k] == "exact_unit_pair"]
    return {
        "source_head": SOURCE, "canonical_main": BASE, "word_head": WORD_HEAD, "caller_head": CALLER_HEAD,
        "new_case_cap": 4, "new_case_count": len(evidence), "dispositions_by_new_case": Counter(dispositions[k] for k in NEW),
        "residual_in": 29, "residual_covered_by_inherited": sum(len(anchors[k]) for k in SEEDS),
        "residual_covered_by_new_exact_checks": sum(len(anchors[k]) for k in NEW),
        "transfers": sum(len(row["transfers"]) for row in certificate.values()),
        "frozen_representative_count": 326, "excluded_total": 297 + sum(v != "exact_unit_pair" for v in coverage.values()),
        "positive_representatives": positives,
        "physical_materialization_or_kappa_gain_claimed": False,
        "controls": controls, "primary_pairing_controls": primary_controls,
        "independent_pairing_controls": independent_controls,
        "classes": [certificate[k] for k in sorted(certificate)], "new_exact": evidence,
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "exact7363" / PACKAGE)
    parser.add_argument("--receipts", type=Path, default=ROOT / "evidence/predecessor")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = run(args.source, args.receipts)
    with args.out.open("x") as out:
        json.dump(report, out, indent=2, sort_keys=True)
        out.write("\n")
    print("PASS_P104_RANK_EIGHT_RESIDUAL", json.dumps({
        k: report[k] for k in ("new_case_count", "dispositions_by_new_case", "residual_in",
                               "transfers", "excluded_total", "positive_representatives")
    }, sort_keys=True))


if __name__ == "__main__":
    main()
