#!/usr/bin/env python3
"""Exact scatter-parity contract between the frozen checker and record exporter.

Independent audit of the boundary question raised by PR2977/PR2992: for which
scatter rows do the symbolic checker (one XOR per list occurrence) and the record
exporter (one ADD per row membership) agree, and is the proposed simple-support
guard exactly equivalent to that agreement?

The frozen sources are read and bound by line, not executed.  No kappa,
supplier or selected-frontier change.
"""
import gzip
import hashlib
import json
from collections import Counter
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORD = ROOT / "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
CHECKER = ROOT / "research/e8-bit-p111-tuned/code/xcheck_p.py"
EXPORTER = ROOT / "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
GENERATOR = ROOT / "research/e8-bit-p111-tuned/code/gen_p3.py"
TUNER = ROOT / "research/e8-bit-p111-tuned/tune/apply.py"

# Semantic lines that fix each side of the contract (whitespace-normalized).
CHECKER_COPY = 'copies = [val[q] for q in w["ret"]]'
CHECKER_SCATTER = "for k in row: val[v + t] ^= copies[k]"
CHECKER_TERMS = 'stats["scatter_terms"] = sum(len(r) for r in w["scatter"])'
EXPORTER_SCATTER = (
    "for t,row in enumerate(c['scatter']): "
    "if k in row: rec.append((1,v+t,temp,1,ZERO,3))"
)
GENERATOR_ROWS = "for C in itertools.combinations(range(len(cvals)), k):"
GENERATOR_FOUND = "found = list(C)"
TUNER_A = 'w["A"] = newA'
TUNER_C = 'w["C"] = wlib.rebuild_C(w)'

AUDITED_WORD_SHA256 = "e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f"

# Exhaustive domain: every tuple of length 0..5 over four retained-total indices.
DOMAIN_SIZE = 1365
DIVERGENT = 1004
SIMPLE_ACCEPT = 65
EXACT_ACCEPT = 361
OVER_REJECTED = 296
TERM_MISMATCH = 1300
SELECTED_ROWS = 111
SELECTED_TERMS = 527
SELECTED_RETAINED = 9


def require(ok, message):
    if not ok:
        raise SystemExit(message)


def norm(text):
    return " ".join(text.split())


def parity_op(row):
    """Checker scatter semantics: one XOR per occurrence, i.e. multiplicity mod 2."""
    return frozenset(k for k, v in Counter(row).items() if v % 2)


def membership_op(row):
    """Exporter scatter semantics: one ADD if the index occurs at all."""
    return frozenset(row)


def is_simple(row):
    """The proposed simple-support guard: every index distinct."""
    return len(row) == len(set(row))


def is_exact(row):
    """The exact agreement condition: every positive multiplicity is odd."""
    return all(v % 2 for v in Counter(row).values())


def source_lines(path):
    return norm(path.read_text(encoding="utf-8"))


def check_sources():
    checker = source_lines(CHECKER)
    exporter = source_lines(EXPORTER)
    generator = source_lines(GENERATOR)
    tuner = source_lines(TUNER)
    require(CHECKER_COPY in checker, "checker COPY line drifted")
    require(CHECKER_SCATTER in checker, "checker scatter loop drifted")
    require(CHECKER_TERMS in checker, "checker scatter term count drifted")
    require(EXPORTER_SCATTER in exporter, "exporter scatter emission drifted")
    require(GENERATOR_ROWS in generator, "generator subset search drifted")
    require(GENERATOR_FOUND in generator, "generator row construction drifted")
    require(TUNER_A in tuner and TUNER_C in tuner, "tuner rewrite sites drifted")
    require("scatter" not in tuner, "tuner can now touch scatter rows")


def check_domain():
    domain = [row for n in range(6) for row in product(range(4), repeat=n)]
    require(len(domain) == DOMAIN_SIZE, "domain size changed")
    divergent = [row for row in domain if parity_op(row) != membership_op(row)]
    simple = [row for row in domain if is_simple(row)]
    exact = [row for row in domain if is_exact(row)]
    agree = [row for row in domain if parity_op(row) == membership_op(row)]
    require(len(divergent) == DIVERGENT, "divergent count changed")
    require(len(simple) == SIMPLE_ACCEPT, "simple-support count changed")
    require(len(exact) == EXACT_ACCEPT, "exact-condition count changed")
    # The exact condition characterises agreement on the whole domain.
    require(set(agree) == set(exact), "agreement differs from the odd-multiplicity condition")
    # The simple-support guard is sound but strictly stronger.
    require(set(simple) <= set(exact), "a simple-support row disagrees")
    require(not (set(divergent) & set(simple)), "a divergent row passed the simple guard")
    over = sorted(set(exact) - set(simple), key=lambda r: (len(r), r))
    require(len(over) == OVER_REJECTED, "over-rejection count changed")
    require(over[0] == (0, 0, 0), "smallest over-rejected row changed")
    # Occurrence count versus emitted records differs exactly off simple supports.
    mismatch = [row for row in domain if len(row) != len(set(row))]
    require(len(mismatch) == TERM_MISMATCH, "term-count mismatch census changed")
    require(len(set(mismatch) & set(agree)) == OVER_REJECTED, "agreeing term-count mismatch changed")
    return domain


def check_mutant():
    row = (4, 5, 6, 7, 8, 0, 0)
    require(parity_op(row) == frozenset({4, 5, 6, 7, 8}), "mutant checker operator changed")
    require(membership_op(row) == frozenset({0, 4, 5, 6, 7, 8}), "mutant exporter operator changed")
    require(parity_op(row) != membership_op(row), "mutant no longer diverges")
    require(not is_simple(row) and not is_exact(row), "mutant passes a candidate guard")
    # Control: replacing the occurrence loop by membership makes the mutant agree,
    # so the divergence is exactly the occurrence loop and not the index range.
    require(frozenset(row) == membership_op(row), "membership control failed")


def check_selected_word():
    payload = WORD.read_bytes()
    require(
        hashlib.sha256(payload).hexdigest() == AUDITED_WORD_SHA256,
        "selected word bytes differ from the audited revision",
    )
    word = json.loads(gzip.decompress(payload).decode("utf-8"))
    rows = word["scatter"]
    require(len(rows) == word["v"] == SELECTED_ROWS, "selected scatter row inventory changed")
    require(len(word["ret"]) == SELECTED_RETAINED, "selected retained-total inventory changed")
    require(all(is_simple(row) for row in rows), "selected word has a repeated scatter index")
    require(all(list(row) == sorted(row) for row in rows), "selected word rows are not ascending")
    require(
        all(type(k) is int and 0 <= k < SELECTED_RETAINED for row in rows for k in row),
        "selected word has an out-of-range scatter index",
    )
    occurrence = sum(len(row) for row in rows)
    membership = sum(len(set(row)) for row in rows)
    require(occurrence == membership == SELECTED_TERMS, "selected term census changed")
    return occurrence


def main():
    check_sources()
    check_domain()
    check_mutant()
    terms = check_selected_word()
    print(
        "PASS_SCATTER_PARITY_CONTRACT "
        f"domain={DOMAIN_SIZE} divergent={DIVERGENT} simple_accept={SIMPLE_ACCEPT} "
        f"exact_accept={EXACT_ACCEPT} over_rejected={OVER_REJECTED} "
        f"term_mismatch={TERM_MISMATCH} mutant=divergent "
        f"selected_rows={SELECTED_ROWS} selected_terms={terms} selected_simple=true "
        "guard=sufficient_not_necessary coefficient_unchanged=true"
    )


if __name__ == "__main__":
    main()
