# Exact chronological libraries with a separate ambient cap

**Result.** Extend the evaluated integer rank-library construction of
[#7345](https://github.com/CrocSwap/integer-mult-bounds/pull/7345) from
`A=m=max target` to every fixed integer `A>=m`, using the selected
source's actual ambient-cap flow. Prove explicit binary and fixed-tape
metadata bounds with A exposed, and a family where varying A forces
quadratic total bit output for evaluated all-rank widths. This is progress
on a numerical premise of the `compiler` assumption. **No new kappa**:
the selected `0.00363005817` remains conditional, with all five assumptions.

The theorem takes a finite evaluated target/paid histogram and a maximum N.
It produces replication a_n, width B_n, expanded leaf count P_n and
expanded mixed-unit count O_n for every n<=N. Individual chronological
exits retain their own child divisibility constraints. Product aggregation
counts identical-rank occurrences without pooling their actual cuts.

## Exact findings

For fixed A and fixed separated histograms, output integers still have
polylogarithmic bit lengths in N. With the explicit parameters K,Z,J in
[PROOF.md](PROOF.md), indexed metadata construction costs `O(K Z^3)`;
the sequential companion costs `O(K (N Z+(J Z)^2+Z^3))` and uses
`O((N+J) Z)` historical cells. Reading children, sorting, setup, copying,
restoring tape heads, writing base rows and all integer bit lengths are
charged. These become `N*polylog N` and `N^2*polylog N` for each fixed
rule. They are metadata costs, not native payload execution costs.

The ambient dependence is necessary in general. Fix targets
`((2,1),(3,1))`, one paid rank-1 site, and any A>=4. For A<=n<2A,

```
B_n = 2^(floor((n-A)/2)+1),
sum_(n=A)^(2A-1) bit_length(B_n) = floor((A-1)^2/4)+2A.
```

Thus the evaluated widths alone require Omega(N^2) output bits at
`N=2A-1` when A varies. This excludes a *uniform* near-linear explicit
output bound and uniform polylogarithmic row widths. It does not refute
the retained construction, which fixes its template before multiplication
input size varies, or exclude polynomial-in-N algorithms and succinct
symbolic representations.

For A=64 the cap-1 plateau has `S=2` and `B_127=2^32`. Reusing the
default plateau exponent `m=3` would give divisor 8 and is false.
The proved general-ambient exponent is
`tau=A*ceil(log2 k_min)`. The exact proof, including contraction,
plateau visits and all-prime divisibility, is in PROOF.md §§3--5.

A separate exit control uses A=4, two productive rank-3 roles and two
paid rank-2 sites. At rank 12 there are four distinct rank-4 cuts with
child width 2. Valid replication is 2; pooling their equal ranks would
incorrectly allow 1.

## Predecessors and exact scope

The ambient geometry already appears in the selected retained
[#6916 compiler proof §6](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/p104-shared-native-helper-splits/retained/compiler/PROOF.md).
[#4507](https://github.com/CrocSwap/integer-mult-bounds/pull/4507) and
[#5071](https://github.com/CrocSwap/integer-mult-bounds/pull/5071) supply
whole-cut gcd/LCM integrality. [#4638](https://github.com/CrocSwap/integer-mult-bounds/pull/4638)
supplies the default plateau-visit mechanism. #7345, exact head
`022461f115369efd988ef8c459907f5544bb8bb3`, supplies the default evaluator
and quantitative cost framework. This package proves their combined
quantitative extension at independent A, with an explicit obstruction to
silently dropping ambient dependence. The source census at a fixed cap
is inherited; recursive complements n-s do not follow by scaling a
default library.

The theorem supplies a valid numerical library for an abstract chronological
leaf locator at the same ambient and histograms. The separate
[leaf/owner locator](https://github.com/CubeJerry/integer-mult-bounds/tree/81f0b0b9a920bd1c9da583cbc3612efd5e75ea94/research/chronological-leaf-owner-index)
is contextual companion work, not a runtime dependency or an upstream PR.
Ordered native manifests, owner routes and physical execution remain separate.

The selected `A=153^1920` lies in the parameter domain. No selected
target/paid manifest or winning library was materialized. A huge-A test
evaluates only toy-rule bounds and bit-count descriptors using that same
ambient; it generates zero library rows. All native, owned-erasure,
complete instruction, tape/precision and analytic obligations remain.

## Verification

Run from the repository root with Python 3.12 and the standard library:

```sh
python -I -W error -B research/ambient-rank-library/verify.py
python -I -O -W error -B research/ambient-rank-library/verify.py
python -B scripts/research_package.py --package research/ambient-rank-library --check-only
```

Expected direct marker: `PASS_AMBIENT_RANK_LIBRARY`. Default replay writes
nothing and checks its complete computed [VALIDATION.json](VALIDATION.json).
An optional `--receipt /absolute/new/external.json` refuses existing files
and paths inside the package. [VERIFY.json](VERIFY.json) declares both runs.

The independent oracle [literal_oracle.py](literal_oracle.py) imports no
production evaluator. It materializes productive-role words, paid-site
paths and target slots, matches actual parent demands, and retains distinct
exiting cuts. Widths use prime valuations; costs use exact rational per-array
recurrences. The author evaluator instead aggregates products and uses
gcd/LCM with integer child-copy totals. All rows and census fields agree
on 12 fixtures: **1,267 ranks, 21,442 units, 31,124 cuts and 35,141
chronological constraints**. Exact all-prime plateau divisibility holds
at every tested rank. Finite chain and plateau-visit dynamic programs
also check the envelopes.

The lower-bound family is checked at all 4,000 plateau rows for A=4,...,80
and A=127,128,255,256, including both parities. Fifteen controls reject
invalid domains/capacities and mutations of height, fit, base range,
individual exit divisibility, repeated cut costs, complement gcd savings
and the default-width constant. A fit mutation needed a heterogeneous
3/5-target fixture: the homogeneous initial fixture has no disputed fit
threshold. That diagnostic adjustment is disclosed; no scientific result
was silently overwritten. The 146 default-A rows agreeing with the frozen
#7345 evaluator are regression evidence, separate from the independent
oracle. Six frozen local sources are authenticated by SHA256 and Git blob
hashes before loading code.

Universal statements rely on the written proof. A separate agent accepted
the proof and independently reconstructed positive source censuses and least
replications by bounded integer trial: 269 complete rows, 57,744 candidate
replications, 260 additional plateau widths and three mutation controls.
Normal and optimized receipts agree. The review and portable reproduction
command are retained in [independent/REVIEW.md](independent/REVIEW.md).
The root separately authenticated all nine exact commit/path source bindings.
No human or proof-kernel acceptance is claimed. No selected cold replay, Lean or Docker was run.

## Sources and recovery

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
[SOURCES.json](SOURCES.json) pins nine files, including the selected
record/review, task catalogue, ambient proof, width proof and #7345 head.
Frozen predecessors remain unchanged. Only this package is added.
[TASK.json](TASK.json) records the assignment and [OVERLAP.json](OVERLAP.json)
the bounded overlap check. The lead agent manages claims, independent
review, commits and fork publication; no upstream PR is opened by this run.

Direct verification needs only this package. Registration/provenance checks
additionally use canonical scripts and pinned Git objects. Scientific
files, source copies, receipt and [PR.md](PR.md) preserve the restart trail;
the publisher records the final branch and commit. Unpublished local files
are temporary, not a remotely durable checkpoint.

## Open next questions

1. **Bind an evaluated selected manifest.** Derive exact chronological
   product, completion and split histograms and owner metadata from the
   selected recipe. This supplies the actual finite input; a symbolic
   product power is not a materialized table.
2. **Improve source-specific ambient constants.** Preserve gcd cancellation
   in selected-profile widths. A uniform improvement needs hypotheses
   excluding the two-target family or a changed output representation.
3. **Emit and execute the whole native instruction stream.** Supply unit
   scalar/phase/adapter/lifecycle events, preserve owner identity, and price
   each physical access and inverse return. Counts supply no missing native
   endpoint or erasure contract.

Prepared for **@CubeJerry**, with substantial OpenAI assistance.
[NOTICE.md](NOTICE.md) credits source authors and originating PRs. New
material is Apache-2.0; predecessor files retain their notices.
