# Exact mixed-root UT4 middle-factor relaxation

A scoped all-size proof determines the exact necessary coefficient-relaxation
minimum for every diagonal mixture of UT4 u/v/z targets:

    n_min = 2d+k+[d=k=1],

where d counts active coordinates and k counts pure-central coordinates.
The new step pairs a lone pure-central coordinate with any noncentral partner
in five columns. Together with credited predecessor blocks, this attains the
mixed lower bound uniformly. The full statement and six explicit blocks are
in [PROOF.md](PROOF.md).

This is a sharp limit of the declared four-matrix relaxation, not a paid
chronological word. Stronger word bounds need further coefficient or chronology
information. No physical supplier, new kappa or selected-frontier change is claimed.

## Credit and relation to earlier work

This contribution is produced by Nick Petalas. ToikY's
[PR1662](https://github.com/CrocSwap/integer-mult-bounds/pull/1662) already solves
the pure-central relaxation. Gareth Davidson's
[PR2027](https://github.com/CrocSwap/integer-mult-bounds/pull/2027) supplies the
mixed-root span unions and asks about mixed pure-central targets. Nick Petalas's
[PR2175](https://github.com/CrocSwap/integer-mult-bounds/pull/2175) supplies the
mixed 2d+k lower bound and one z/uz fixture. Those results are credited premises,
not replay or audit deliverables. The new result uniformly attains the mixed
relaxation, including every one-pure-central partner type.

The pinned proofs retain the complete register-model lineage. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/ut4-mixed-relaxation-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/ut4-mixed-relaxation-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/ut4-mixed-relaxation-optimum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/ut4-mixed-relaxation-optimum --check-source-history
```

Any CPython 3.12 path may replace the local interpreter path. Normal execution
is read-only and prints `PASS_UT4_MIXED_RELAXATION_OPTIMUM`. The registered hook
runs both normal and optimized checks. RESULT.json is generated from scientific
outputs and SHA256 hashes of package files and pinned live proofs. Explicit
`--emit NEW_PATH` writes an external receipt and refuses an occupied path.

Local exact checks cover 5,602 exhaustive mixed/padded fixtures through four
active roles, 1,098 larger fixtures through 64 roles, all seven scalar minima,
15 independently multiplied block templates with 176 entries, and eight
rejection controls. The universal statement rests on the written proof.

The generic card's historical first command, `scripts/research_baseline.py`,
fails at `KeyError: 'bit_lower'` on the selected record. This unrelated source
orientation failure was recorded; no shared code or selected record was changed.
The selected review and source manifest were read directly.

## Limitations

The proof is quantified over every finite diagonal family and dirty identity
extension. The executable constructor supports at most 64 active roles and two
dirty coordinates. All four equations and active-span restrictions are necessary
conditions, so an attaining fixture is not a formal operator construction.
Physical address realization, native/compiler, hosting, precision/tape, actual
paid paths and outer transfer remain unrun obligations. No selected cold replay,
Lean build, independent human acceptance or formal verification is claimed.

## Open next questions

1. Which additional chronological equation gives a stronger mixed-family bound?
   Start with one pure-central and one u target, impose actual prefix/suffix
   paths on the five-column table, and charge all outer calls. The present
   relaxation deliberately omits these paths.
2. Can the larger mixed families' complete paid tariffs be characterized?
   Start with a named target outside the existing z/uz weighted region, retaining
   all formal coefficients and arbitrary dirty restoration. Relaxation attainment
   alone does not establish an upper word or its tariff.

Structured questions and exact source pins are in TASK.json and SOURCES.json.
