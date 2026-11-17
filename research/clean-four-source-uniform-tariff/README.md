# Exact four-source uniform clean-row tariff

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration. In the generic
four-source paid-clean connector contract of Ali Romman's #5372, all positive
uniform complete source/readout prices b,a have exact optimum

```
min(8b + 23a, 16b + 15a).
```

The complete frontier of total source/readout counts is (8,23), (10,21),
(12,19), (14,17), (16,15). An explicit eight-call source walk reads seven outputs
once and eight twice. The [proof](PROOF.md) bounds every finite legal word and
executes all fifteen target updates for arbitrary compatible F2-linear maps,
including singular and rectangular maps. For example, b=10,a=1 gives exact
map-call cost 103, versus the classical Gray schedule's 175. Common paid row
allocation, zeroing and release costs must still be added.

This settles the uniform-price specialization of Open next question 2 in the
older [#6254](https://github.com/CrocSwap/integer-mult-bounds/pull/6254). It does
not classify individual call counts or settle heterogeneous prices. The source
mask counting argument and general Gray construction are credited inputs; the
new result is their sharp four-source tariff and aggregate frontier. Research
stopped at this first result. There is no new kappa or selected-frontier change.

## Reproduction and evidence

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/clean-four-source-uniform-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/clean-four-source-uniform-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/clean-four-source-uniform-tariff --check-source-history
```

Use another CPython 3.12 path elsewhere. The registered runner separately runs
normal and optimized warning-strict commands, each limited to 120 seconds.
The verifier writes no files and prints a generated, SHA256-bound JSON receipt
with marker `PASS_CLEAN_FOUR_SOURCE_UNIFORM_TARIFF`.

Finite coverage is 190231 source-walk states, 20769 closed visited sets, 20440
spanning closed sets, two independent XOR-distance algorithms for every closed
set, five attaining profiles, 147 exact price comparisons, 4880 rectangular-map
executions and 174 rejecting controls. These counts describe enumerated states
and executions. The written proof supplies the universal price, map and word
quantifiers. The finite reduction covers every potentially optimal uniform-price
word; it is not merely a length-sixteen search without a dominance argument.
No predecessor scientific verifier was replayed as this deliverable.

## Scope and sources

Canonical base e54523517d0f03e58352e647c403a5af3e525a57, priority revision 8,
selected #7000 with conditional kappa 0.00363005817. The priority prose still
names an older selection. The selected source-binding orientation and card's
945-pairing positive control passed; neither is evidence of the new theorem.
[TASK.json](TASK.json) records the changed card scope and advance claim.
[SOURCES.json](SOURCES.json) pins the two live contract/question inputs and
historical catalogue/selected-record provenance. Source hashes authenticate
those bytes; they do not certify predecessor mathematics.

The model has one paid clean row, immutable sources, unread dirty outputs and
one final restoration. Fixed per-call prices and the generic all-map requirement
are essential. Physical map/native lowering, row provisioning, descriptors,
routing, precision/tape, ownership admission, recursive hosting and the full
signed supplier invoice remain open. The five selected assumptions are unchanged.
No selected cold replay, full native/caller replay, Lean, Docker, independent
human review, formal proof-kernel acceptance or complete multiplication theorem
is claimed. CI finite replay and independent scientific review are distinct.
The [proof](PROOF.md) also records the bounded managed-allocation and static
analysis limitations of the verifier.

## Open next questions

1. Determine the four-source heterogeneous frontier. First use weighted source
   edges and target-specific readout costs in the finite visited-state reduction.
   The sixteen-call dominance cutoff here depends on uniform prices and does
   not settle the individual-count frontier. No such extension is reserved.
2. Identify an actual recursive caller whose complete prices favor the eight-call
   branch. First price its clean-row lifetime, full maps, routing, descriptors,
   restoration and precision. No physical caller or full positive invoice is
   supplied here.

## Credit

Credit Ali Romman #5372 for the paid-clean contract analysis, source-mask lower
bound and general-n Gray optimum in the a>=b region; Nick Petalas #6254 for the
three-source tariff and explicit four-source question; Cinna Davis #1954 for the
paid-row extension and #2271 for related borrowed-source Gray tours; Ross
Richardson #943 for the connector lineage. Cube walks, Gray cycles, shortest
paths and subset-XOR dynamic programming are classical. This contribution claims
the four-source tariff theorem, aggregate frontier and its rerunnable checker.
All predecessor files and credit lines remain unchanged.
