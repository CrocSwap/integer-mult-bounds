# Eight-source singleton connectors need at least 28 source calls

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with finite exact corroboration. In the
restored binary singleton-connector model of Ross Richardson's
[#943](https://github.com/CrocSwap/integer-mult-bounds/pull/943),

```text
28 <= f(8) <= 32.
```

Every possible 28-call universal word has source multiplicities
`(4,4,4,4,4,4,2,2)`, up to relabelling. For the complete batch of 255 nonzero
binary rows, the total query count is at least **538**, even when outputs
may purchase more than two readouts. The inherited Gray-block construction
costs 542 queries. Neither lower bound is claimed attained.

The new step sums all eight coordinate-deletion constraints supplied by
conorholds's proved `f(7)=24` in
[#3058](https://github.com/CrocSwap/integer-mult-bounds/pull/3058).
Its deletion argument and seven-source theorem are cited premises. This
package does not replay or audit their proof, classification or censuses.
It answers the eight-source question in that package's Open next questions.

## Contract and proof of the source-call bound

The sources `x_0,...,x_7` are immutable. One connector `z` starts with arbitrary
dirty data and must return exactly. The only calls are complete source
injections `B_j: z += B_j x_j` and output readouts `A_i: y_i += A_i z`, over
characteristic two. Every source and output begins arbitrarily dirty. The
word must work uniformly for the admitted linear maps. Every call costs one;
no source mixing, source mutation, combined injection, clean state, extra
connector, frame operation or transfer is available.

Let `w` be the sequence of source labels, let `L` be its length, and let
`q_t` be its prefix parity vectors. Restoration gives `q_L=q_0=0` and an
even positive multiplicity `c_i` for every source. Write
`P={q_0,...,q_(L-1)}`. The inherited paired-readout criterion is

```text
w is universal exactly when D(w)=P+P=F2^8.
```

Deleting all occurrences of source `i` compresses the projected stationary
steps into a closed seven-source word of length `L-c_i`. Its prefix set is
exactly the coordinate projection of `P`; stationary steps add no new
vertices. Projection commutes with differences. A universal eight-source
word therefore projects to a universal seven-source word for every `i`.
By the credited seven-source theorem,

```text
L-c_i >= 24                 for each i=0,...,7.
sum_i(L-c_i) = 7L >= 192.
```

Thus `L>=ceil(192/7)=28`. At equality, every `c_i<=4`, while all `c_i` are
positive and even. Since their sum is 28, exactly six equal four and two
equal two. There are `choose(8,2)=28` labelled necessary count vectors.
These are necessary conditions, not 28 attaining words.

The same averaging identity for projections onto k of n coordinates is
`choose(n-1,k-1)L >= choose(n,k)f(k)`. This is simply double counting the
surviving occurrences. Only its `n=8,k=7` application is the result pursued
here; no larger-source optimization is included.

Douglas Colkitt's
[#1185](https://github.com/CrocSwap/integer-mult-bounds/pull/1185) already
provides the upper construction. Concatenate closed reflected Gray cycles
on disjoint blocks of four sources. Each block takes 16 steps and visits
its full coordinate subspace. Their prefix differences cover the sum of
those subspaces, hence all 256 masks. This gives `f(8)<=32`.

## Complete-batch bound with arbitrary readout counts

Consider one output for each nonzero mask, with the same generic, offline
interface. Every output needs an even positive number of readouts to cancel
the incoming connector dirt, so at least 510 readout calls are necessary.
If a mask is absent from `D(w)`, its output needs at least four rather than
two readouts. Let `U` be the number of these absent nonzero masks. Then

```text
total queries >= L + 510 + 2U.
```

All eight sources are needed, so `L>=16` is even. Separate cases give the
following bound without assuming a universal source word:

* If `16<=L<=22`, at most `choose(L,2)` nonzero differences occur. Thus
  `U>=255-choose(L,2)`. The four query floors, in increasing L, are
  796, 732, 660 and 580.
* If `L=24` or `26`, some source has `c_i>=4`. Deleting it leaves at most
  22 calls, so the seven-source word is not universal by `f(7)=24`.
  A missing projected mask has both of its eight-dimensional lifts absent
  from `D(w)`. It is nonzero because zero always occurs in a difference
  set. Consequently `U>=2`. The respective query floors are 538 and 540.
* If `L>=28`, the 510-readout bound gives at least 538 queries directly.

This proves the claimed 538-query floor even with arbitrarily many extra
readouts. The inherited 32-source-call word with exactly two readouts for
each of 255 outputs gives the upper bound `32+510=542`.

## Evidence and reproduction

The universal lower bounds rest on the written proof and the cited
seven-source theorem. The deterministic verifier imports no predecessor code.
It prints a generated receipt bound to all five package files and writes
nothing. Its finite checks cover:

* All 10,934 closed words of even length at most eight on one through four
  labelled sources, including unused coordinates. All 147,096 nonempty
  coordinate-subset projections have the stated prefix and difference images.
* All 12,870 positive even eight-source count vectors of total at most 32.
  The deletion constraints reject all 1,287 vectors shorter than 28. Exactly
  28 vectors at length 28 meet those necessary constraints.
* The explicit inherited 32-step Gray construction, all 255 paired readouts,
  all eight seven-source projections, and a literal complete 542-query
  two-bit linear-map execution on all 528 arbitrary dirty input basis columns.
* Invalid source words, a restored nonuniversal word, incorrect arithmetic,
  uncompressed deleted steps, and corrupted readout/chronology controls.

From the repository root, use CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/eight-source-singleton-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -O -B research/eight-source-singleton-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/eight-source-singleton-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/eight-source-singleton-floor --check-source-history
```

Another CPython 3.12 path may replace the local interpreter. Expected marker:
`PASS_EIGHT_SOURCE_SINGLETON_FLOOR 28<=f(8)<=32 queries>=538 upper=542`.
Normal and optimized registered commands keep every check enabled.

## Scope, provenance and implementation limits

The question is a source-count side result within the existing alphabet,
so [TASK.json](TASK.json) records a changed `connector-alphabet-change` scope.
The card's first working example passes its 945-pairing positive control;
the current selected-baseline command passes metadata orientation. Neither
is mathematical evidence for this contribution.

The public [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19146100)
proposed the weaker 26-call application of a published covering-code bound.
Summing the inherited deletion inequalities gives 28 immediately, so no new
coding-theory premise is needed. The delivered result is this summed bound
and its batch consequence. Research stopped at that step.

Canonical base is `ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c`, priority revision 7.
[SOURCES.json](SOURCES.json) pins the unchanged predecessor READMEs, selected
record and task catalogue as historical provenance. The direct verifier has
no external runtime inputs; historical source validation requires Git history.
The main/merged-PR searches and live PR/Discussion checks found no matching
eight-source floor. Sparse local metadata, arbitrary diffs and unpublished
work remain coverage limits, not evidence of novelty.

The new lower bound does not determine `f(8)`, construct a 28-call word,
prove a 538-query optimum, price a physical supplier, improve kappa, change
the selected frontier or establish a complete multiplication theorem.
The inherited seven-source theorem, including its published classification
premises, remains a mathematical dependency. Independent human and formal
proof-kernel review are unclaimed. Selected cold replay, Lean and Docker
were not run; no selected construction was changed.

The verifier has no recursion, subprocesses or generated code. Every loop
has a fixed finite domain; the largest raw word domain is `4^8=65536` and
there are at most 12,870 stored count records. Functions fit within 60 lines.
Explicit `require` checks survive optimization. Python's managed allocation
is a Power-of-Ten rule-3 deviation bounded by those domains and 528-bit
linear-state words. A fixed-storage implementation would be needed to remove
that runtime deviation. Warnings-as-errors and available static diagnostics
are the checks for this standalone interpreted command.

## Open next questions

1. Does a 28-step universal word with multiplicities `(4,4,4,4,4,4,2,2)`
   exist? This decides whether the new floor is sharp. Begin with an exact
   prefix-difference search restricted to those counts and explicit memory
   and time caps. No such search or candidate is supplied here.
2. Is the full batch minimum 538, 540 or 542 queries? First strengthen the
   missing-mask lower bounds at source lengths 24 and 26 by combining all
   failed coordinate projections, or seek a 28-call universal word. Counts
   alone do not supply attaining words or extra-readout schedules.
3. Can a named actual caller use this exact singleton interface at favourable
   complete prices? Pin its immutable ports and offline observations first.
   Setup, routing, stock, precision and the complete consumer bill are missing.

## Credit

conorholds's #3058 supplies `f(7)=24`, the coordinate-deletion argument,
the covering-code/classification lineage and the explicit eight-source
question. Ross Richardson #943 supplies the connector contract and
paired-prefix criterion. Douglas Colkitt #1185 supplies the Gray-block upper
construction and the six-source result. Those results are credited and used,
not rechecked as this deliverable. The new contribution is their summed
eight-projection consequence and the 538-query all-readout lower bound.
The earlier connector, source-call and dirty-state lineage retains its
attribution; no predecessor credit line or frozen evidence is changed.
