# Root-defect bounds for minimal productive stages

**No new κ.** A normalized caller with `N` nonzero rank-one square-zero query
operators on `n` independent productive fields, and `F` full calls with fresh
coordinate rank-two stage masks in one common basis, must satisfy

\[
F\le2\delta(\delta+1),\qquad \delta=N-n,
\]

provided it has no idle stage operations. Thin queries may have arbitrary
supports and positions; repeated full supports are counted with multiplicity.
The proof covers every defect and does not assume a shortest root, a chain,
fixed scalar signs, or a finite query-count cutoff.

For the exact eighteen-call native profile from
CrocSwap/integer-mult-bounds#6833, this forces `δ≥3`. Complete target/paid
accounting gives the following rigorous raw upper ceilings:

| Defect | Complete-moment crossing bracket in κ |
|---|---|
| `δ=3` | `(0.0033288660495, 0.0033288660497)` |
| Every `δ≥4` | `(0.0029312090589, 0.0029312090593)` |

Both ceilings are below the pending **idle-bearing** benchmark `κ=0.00337180`
of CrocSwap/integer-mult-bounds#6833. At that headline, the respective upper
moments are enclosed by `(-7.08514120910689,-7.08514120910688)` and
`(-67.04640429875804,-67.04640429875803)`. A global monotonicity argument rules
out a later favorable interval. These are upper bounds on a restricted caller
family, not achievable κ values. The accepted selected frontier at the frozen
base remains `κ=0.003125804`; this package makes no selection change.

## A paired-query extension

A separate theorem tests a route around the scalar-query restriction: couple
pairs of native copies into square-zero rank-two query blocks and allow
commuting productive stages of rank four. At total rank defect two, **at most
five such full blocks can exist**, even with arbitrary intervening queries.
Thus nine paired full blocks cannot realize the proposed eighteen-native-copy
shortcut. The theorem does not require actual-prefix commutation, and five is
not claimed attainable.

The proof in [PAIRED-DEFECT-ADDENDUM.md](PAIRED-DEFECT-ADDENDUM.md) combines
the block defect identity with an ordered-sign constraint on intersections of
four-dimensional stage supports. Six full blocks require twelve dimensions,
whereas their stage supports can span at most ten. It permits arbitrary mixing
inside each stage and repeated supports. The separate reconstruction in
[SIX-FULL-REVIEW.md](SIX-FULL-REVIEW.md) checks both branches of that argument;
its verifier imports no author implementation. These finite controls corroborate
the proof and demonstrate why commutation and the field characteristic matter.

## Why this matters

Adding query factors can improve a root's geometric freedom, but each additional
factor also creates a paid request. The defect identity connects that query
budget to the full stage-support graph. A matching costs defect rank, a star of
`k` distinct neighbours costs at least `ceil(k/2)`, and repeated full occurrences
are separately constrained by active coordinates plus defect. These constraints
force the complete relaxed invoice to lose before the pending benchmark.

The result isolates a real interface limitation: a short algebraic root on a
quotient does not by itself produce eighteen compatible rank-two productive
stage masks. With `δ=1`, the theorem would permit at most four full occurrences
in the declared class. A quotient or moving-carrier mechanism can still be
valuable if it changes the target representation or another stated premise and
pays the resulting restoration and stage work.

The complete proof, including zero hub entries and ordinary-control normalization,
is in [PROOF.md](PROOF.md). Exact reproducibility evidence is in
[RESULT.json](RESULT.json). The finite graph/matrix checks corroborate boundary
cases; the universal theorem is established by the proof, not by enumeration.

[REVIEW.md](REVIEW.md) records a separate mathematical derivation and a second
rational arithmetic implementation, [audit_price.py](audit_price.py). Its
positive-exponential enclosure and direct derivative proof independently
corroborate the two losing envelopes. The registered replay runs both
implementations normally and with assertions disabled.

## Provenance and what is new

Base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The selected record and original
`joint-query-controller` task card are pinned as historical provenance in
[SOURCES.json](SOURCES.json); the card is retained verbatim in [TASK.json](TASK.json).

The native profile is parsed from an unchanged, retained source file from
CrocSwap/integer-mult-bounds#6833, head
`51f54e3c31f2f3a3e056a483b3ed66ae916ad06a`, Git blob
`7d9ff06de9dfbba31c06a141e6cacd9806852a41`. Its SHA256 and exact originating path
are in [retained/SOURCE-PINS.json](retained/SOURCE-PINS.json). Replay verifies both
hashes, uses `ast.literal_eval` on the two census dictionaries, and never imports
or executes the retained source. No remote file or uninstalled dependency is
needed for direct replay.

DreamingOfClouds's CrocSwap/integer-mult-bounds#6832
(`research/p104-query-block-bound`, head
`99a165a81be808f45c1b6f4b0a809145ac7923d1`) establishes the predecessor header
rank identity; Section 2 rederives it. CrocSwap/integer-mult-bounds#6842 classifies
the shortest-header case. CrocSwap/integer-mult-bounds#6840 supplies earlier
scoped star symmetrization, and CrocSwap/integer-mult-bounds#6839 supplies the
retained normalized native derivative estimate. The new result combines the
rank defect with maximum matching, arbitrary-coefficient star rank including
zeros, multiplicity accounting, and the complete no-idle invoice. It does not
repeat the earlier chain-family ceiling or make a novelty claim for the
inherited displacement identity.

## Reproduce

From the repository root, using Python 3.12 and only its standard library:

```sh
python3.12 -B research/noidle-root-defect/verify.py
```

Expected final output:

```text
PASS_NOIDLE_ROOT_DEFECT
No new kappa; F=18 requires defect>=3; both complete envelopes lose to 0.00337180.
Exact controls: 33867 graphs, 3905 star blocks, 10 roots, 9 rejection controls.
```

The registered package also runs the replay under `-O`, using explicit checks
that remain active when assertions are disabled:

```sh
python3.12 scripts/research_package.py --package research/noidle-root-defect --check-only
python3.12 scripts/research_package.py --package research/noidle-root-defect
```

`VERIFY.json` registers the scalar verifier, independent pricing audit, paired-query
controls and their independent boundary checker, each normally and under `-O`. The only optional
regeneration command is `python3.12 -B research/noidle-root-defect/verify.py --write`;
ordinary replay recomputes and requires exact equality with `RESULT.json`.

## Verification and negative controls

The completed deterministic finite domain is all 33,867 labelled simple graphs
on one through six vertices; all 3,905 ordered star blocks of sizes one through
five over the explicitly recorded five-pair coefficient alphabet, including
3,542 zero-product cases; and ten exact rational roots. Root fixtures include
parallel full supports and dense thin identity pairs. There is no random seed
and no early stopping: these finite domains are fully exhausted. Their purpose
is to check implementation and delicate boundary cases, not to infer the
universal theorem.

Exact rational logarithm and exponential enclosures certify both crossing
brackets, both negative benchmark tests, and the positive monotonicity lower
bound. The source profile is byte-authenticated. Nine rejection controls cover
source corruption, an invalid exponent, a changed root coefficient, zero and
one-coordinate queries, the false stronger star bound, replacing maximum
matching by maximal matching, omitting a thin-query charge, and collapsing
parallel occurrences. Omitting a single thin charge actually changes the
relaxed defect-three benchmark from negative to positive, so that control tests
a mathematically consequential accounting failure.

The lead reviewer separately reconstructed the graph/rank proof, including the
zero-product pivots, and independently implemented rational bounds with a
positive exponential series. That different arithmetic computation agrees with
the author's alternating exponential computation to all fourteen displayed
decimal places. The reviewer also obtained a separate no-re-entry proof from
separation of the negative coefficient ranks `2..6` and positive ranks `7,8,9,25`.
The author's self-contained replay remains the registered package verifier.

## Scope and unfinished obligations

The scalar theorem requires nonzero rank-one square-zero normalized queries,
characteristic different from two, arbitrary independent productive inputs,
fresh stages acting through rank-two coordinate projectors in one common basis,
and no idle stage operations. It does not cover higher-rank full stage masks,
stage-dependent controls, noncoordinate or noncommuting output representations,
zero-query native calls, nonproductive restored auxiliaries, or changed native
prices. It does not invalidate CrocSwap/integer-mult-bounds#6833, whose useful
caller pays for idle work, and it does not remove the selected theorem's five
inherited framework assumptions. No native/caller/compiler/outer admission
replay is claimed or needed to prove this scoped negative result.

## Open next questions

The paired theorem leaves higher rank defect, larger paid stages, noncommuting
outputs and non-square-zero shared-variable aggregates open. Can one of those
changes support a complete favorable native/target/paid invoice? First exhibit
its stage projectors and closure identity; an optimistic target census alone
does not settle productive compatibility.

A concrete algebraic quotient may have a short root yet lack compatible
productive projectors. Can it instead realize a restored output representation
outside the simultaneous coordinate rank-two contract, with a complete paid
invoice below the pending threshold? First derive its exact stage operators and
all restoration/output targets, then identify which premise above fails. The
missing legal productive interface and full accounting remain the blocker.

For idle-bearing callers, can a changed non-shortest root lower the combined
native, thin-query, idle and restoration bill? The present theorem deliberately
leaves that question open. A useful first experiment must derive an explicit
stage/idle decomposition and a favorable complete moment before any expensive
search; an algebraic root alone is insufficient.

## Credit

Prepared by Jerry Chen / **@CubeJerry**, with substantial **OpenAI GPT-6 Astra Pro**
assistance for mathematical exploration, proof development, implementation, and
review. The lead reviewer used a separate reasoning and arithmetic implementation.
Credit DreamingOfClouds for the query-block rank identity and the retained
chain-nested caller/native profile, the native source lineage of
CrocSwap/integer-mult-bounds#6824, and all predecessors named in
[NOTICE](NOTICE) and [retained/NOTICE-pr6833.txt](retained/NOTICE-pr6833.txt).
New work is Apache-2.0; retained source headers and notices are unchanged.
