# Linear signed residues with two fewer numerator traversals

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped constructive proof with exact finite corroboration.
The compact rounded ADD of CubeJerry's [PR6990](https://github.com/CrocSwap/integer-mult-bounds/pull/6990)
can compute its signed odd residue during the existing numerator rewind.
The new phase has exactly `8o+2` graph labels and `14o+4` literal rows,
counting both component parities. It stores no power of two. The complete
graph bound becomes `O(LK+Ko+o)` in place of `O(LK+o²+Ko)`.

For an M-bit numerator, the change saves exactly `2M+2` virtual reads,
`2M+2` virtual moves and `4M+6` executed rows per component. Under the
retained coded-port executor, this is `28(M+1)` physical tape actions.
Both private banks, the complete rounded map, staging, cancellation,
source preservation and successful cleanup contracts are retained.
[PROOF.md](PROOF.md) states the boundaries and all-width proof.

The three source-compatible coefficient fixtures give these generated
fixed-table row counts. The old compiler is a resource comparator for
the new step; its scientific result is not audited here.

| Coefficient | Original rows | New rows | Rows removed |
|---|---:|---:|---:|
| -14729531/163840 | 100,033 | 99,807 | 226 |
| -1379/250 | 187,806 | 38,300 | 149,506 |
| 1085645/393216 | 76,560 | 76,494 | 66 |

These are enumerated instruction counts, not timing measurements. No
new kappa, selected-frontier change or complete multiplication theorem
is claimed. This is an opt-in compiler adapter; no production file changes.

## Reproduction and evidence

From the repository root, use CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -X dev -B research/reverse-horner-residue/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -X dev -B research/reverse-horner-residue/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/reverse-horner-residue
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/reverse-horner-residue --check-source-history
```

Substitute another CPython 3.12 path on another machine. The direct marker
is `PASS_REVERSE_HORNER_RESIDUE` in a generated JSON stdout receipt bound
to all package-file hashes. Nothing is written by replay. The last command
requires committed package bytes and full Git history.

The verifier separately interprets 63,240 signed phase executions, covering
every bit string of widths one through eight, both parities and every odd
divisor from 3 through 125. It enumerates 31,868 phase labels and 55,800
phase rows across those 62 graphs and checks the exact operation counts.
Complete changed tables execute through the retained Controller primitive,
coded ports and lifecycle on 2,720 exhaustive ADD calls, with 2,298 successes
and 422 correct range rejections. Three additional cancellation fixtures
produce `(-80,0)`, `(-4,0)` and `(1,0)`. Their physical-action and executed-row
savings agree with the proved formulas.

Two deliberately damaged signed-Horner constructions each fail on four of
eight enumerated three-bit words. Long-to-short dirty-bank reuse, a late
whole-field overflow, reuse after that rejection, and invalid coefficient
guards are checked. Dyadic and integral tables equal the original tables
exactly. All checks remain active under optimized Python. The written proof
supplies the universal statement; these finite domains do not replace it.

## Scope, source binding and limits

The question refines the economical fixed-graph opening in CubeJerry's
[PR6988](https://github.com/CrocSwap/integer-mult-bounds/pull/6988), Open next
question 1. PR6990 already supplies the compact numerator construction;
this package contributes the smaller, shorter signed-residue phase.
Horner evaluation, two's-complement arithmetic and graph substitution are
classical. No global literature-priority claim is made.

The executable accepts exact rational coefficients with `L<=24`, odd part
`o<=125`, and a finite construction cap of 500,000 labels and 2,000,000 rows.
Exceeding a cap rejects explicitly. The mathematical local phase works for
all positive bit widths and finite odd divisors. The inherited numerator,
quotient, external-format and lifecycle premises remain required.

The adapter reads four exact live sources declared in [SOURCES.json](SOURCES.json)
and [VERIFY.json](VERIFY.json). It injects a private Builder into the exact
named source compiler definition, replaces two known construction edges
and emits ordinary immutable six-opcode tables. Runtime payload execution
contains no adapter callbacks. Source hashes are checked before parsing or
execution, and Python bytecode caches are bypassed by compiling those bytes.
No predecessor file or attribution line is changed or copied.

Base is canonical main `e54523517d0f03e58352e647c403a5af3e525a57`, priority
revision 8, selected #7000. The selected metadata baseline passed; it is not
a scientific replay. The `uniform-transfer-audit` card explicitly changes
scope to a local implementation improvement. Its five-assumption goal is
not claimed. [The advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19542452)
records this boundary. Main README searches, merged/open PR searches,
recent account work, live handoffs and local reservations were checked.
The overlap helper covers all 558 cached open PRs and 7,226 Discussion
records, but only 222 of 10,178 local notes. Unpublished work, omitted notes
and arbitrary historical diffs remain coverage limits.

Full catalogue/recursive source binding, complete physical supplier tariffs,
native operators, production coefficient installation, outer recovery and
the selected cold replay remain unrun. No independent human or formal
proof-kernel review is claimed. The selected five framework assumptions
retain their status.

## Implementation bounds

New functions are shorter than 60 lines. There is no recursion, network,
child process, shared-file mutation or persistent payload cache. Coefficient
and graph caps bound the inherited construction queue; the new-phase loop
has at most `8o+2` iterations. Test domains and literal phase step budgets
are explicit. Inherited runtime loops are justified by their cited finite
word and lifecycle contracts and by the local decreasing-width proof.
Warning-strict normal and optimized development-mode execution provide
local Python diagnostics. Ruff, Mypy and Pyright are unavailable on PATH.

Power-of-ten rule 3 has a managed-Python allocation deviation. Graph
construction and exact verification allocate bounded Python collections
and integers. No fixed-allocation runtime claim is made for the verifier;
the generated table carries the target's finite control. A larger-domain
backend would need a separate capacity contract. Rules 8 and 9 have a
construction-only source-loading and dependency-injection deviation.
Only four hash-authenticated source files, fixed named definitions and two
Builder classes are admitted. The new local interpreter, complete coded
execution, identical dyadic controls and negative constructions check this
seam. A future production integration can expose a direct Builder parameter
instead; modifying frozen predecessors is outside this package.

## Open next questions

1. Install this phase through an explicit public Builder parameter in a
   versioned production compiler. Begin with the two redirected edges and
   preserve source pins, primitive lifecycle and finite-control charges.
   Shared-code adoption and its downstream consumers remain separate.
2. Share the power-free residue graph among the full current coefficient
   catalogue while retaining exact source tokens. First group coefficients
   by odd divisor and bind each quotient continuation. Full catalogue and
   recursive field delivery are not supplied here.

## Related open work

No open PR targeting this signed-residue prepass or compact rounded-ADD
table-size quantity was found in the live targeted search. The open rounded
MOVE, inverse-code recovery and tensor-extraction packages have different
operators and contracts. No numerical agreement or disagreement is inferred.

## Credit

CubeJerry / Jerry Chen supplied PR6988's rounded scalar boundary, PR6990's
compact ADD compiler, exact Builder, coded-port lifecycle and physical
fixtures. DreamingOfClouds supplied the #6936 word and #6937 rounded-division
proposal. The original packages retain their full contributor lineage,
including Nick Petalas's older one-carry work. The new signed-residue
construction, source adapter, scoped proof and verifier were produced by
Nick Petalas.
