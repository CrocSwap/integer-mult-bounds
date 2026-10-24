# Beyond columnwise controls: finite certificates and routing bounds

Columnwise tensor tests leave genuine cross-column programs outside their hypotheses. A **fixed finite transfer table** supplies another usable contract: complete endpoint equality at every positive width has a finite exact certificate, or a literal discrepancy at a width bounded by the transfer dimension. This includes dense/non-Clifford local operators, finite-memory column mixing and explicitly represented recurrent width coefficients.

The same representation gives exact and robust obstructions. Swapping two k-column halves requires transfer dimension at least d^(2k); pairing their binary quadratic phases requires at least 2^k. At operator error ε<1 these become `(1−ε²)d^(2k)` and `(1−ε²)2^k`. These are bounds on representation at a specified column cut, not paid-query or tape-time bounds.

The [complete proof](PROOF.md) credits classical weighted automata and matrix-product methods. The new repository contribution is the concrete physical-column contract, complete-return/source adapter and the explicit enabling/exclusion boundaries. This is local written mathematics and author-checked code, awaiting independent review. No global literature priority, new κ or admitted supplier is claimed.

## The usable theorem

Let F,B be fixed role boundaries and T_(y,x) fixed D-by-D transitions for each physical output/input column pair. The width-f endpoint entry is

`[F T_(y1,x1) … T_(yf,xf) B]_(output_role,input_role)`.

**Every positive width agrees with the reference iff the residual vanishes at all widths 1,…,D.** This means every physical entry and every original/returned role at those widths. A few sampled columns are insufficient. The implementation avoids constructing those large matrices: it builds a reachable-row certificate R satisfying

`F T_s = E_s R`, `R T_s = C_s R`, `R B = 0` for every local symbol s.

These equations suffice for an independently checkable all-width conclusion. On failure the producer returns one physical input column, output column, input/output role pair and exact nonzero discrepancy. Its width is at most D. If the positive seed span has rank r1>0, the proof improves this to D−r1+1. A D-cycle has its first positive discrepancy exactly at width D, so the general D bound is sharp.

All coefficients are interpreted as concrete physical entries. Local inverse/phase relations are therefore already present. The statement does not require independent formal native letters, monomiality, a finite Clifford group, bounded expanded term support or column permutation symmetry.

## Contract and composition

| Feature | Construction and cost in transfer dimension |
|---|---|
| Sum or reference subtraction | Direct sum; dimensions add. Exterior scalars multiply one boundary. |
| Physical composition | Contract the intermediate column index and tensor virtual spaces; dimensions multiply. Global owner sums are performed separately. |
| Supplied inverse | Check both complete compositions. An arbitrary MPO inverse is not assumed to have finite transfer dimension. |
| Recurrent coefficient `a G^f b` | Tensor the k-state coefficient recurrence into the transitions; dimension multiplies by k. Polynomial, exponential and periodic coefficients fit. |
| Regular restrictions | Include the finite recognizer in the state bound. A restricted width subsequence is not all positive widths. |
| Dirty or rectangular role endpoints | Keep every required independent input/output role in F,B and the reference. Returning zero does not restore arbitrary dirt. |

Tables must remain fixed across widths, including any schedule/controller state. Bounded bond dimension separately at each width does not suffice. Explicit tables can grow exponentially during extraction from a succinct circuit. The classical polynomial equivalence algorithm is polynomial in the **extracted table**, not necessarily in the original program. The checker currently implements exact Q(i), shared arithmetic/parsing and separately transcribed closure checks; it imports no producer or elimination code. Its default state budget is 256; exceeding it is no decision.

## Examples that enable or stop research

**Genuine column mixing.** Prefix XOR maps `y_j=x_1 xor … xor x_j` using two transfer states and has an exactly certified inverse. It does not commute with swapping columns and therefore cannot be represented as a scalar sum of identical one-column tensor powers. A two-by-two cut minor proves that two states are necessary. This goes beyond the interface in [#5436](https://github.com/CrocSwap/integer-mult-bounds/pull/5436), while giving no free physical realization.

**Pinned native source.** The byte-exact [nine-axis, two-role source word](SOURCE-FIXTURE.json) comes from [#5369](https://github.com/CrocSwap/integer-mult-bounds/pull/5369)'s [source-conjugation example](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/native-tensor-cutoff/examples/source-conjugation.json). Its eight instructions implement and cancel the actual `G Z G^-1=R` query, with both dirty roles restored. The new frontend checks all four owner/input blocks, independently checks all 512 local addresses, and certifies the prefix-encoded source shear with eight virtual states and a two-row invariant. Removing R's absolute phase fails at width one. This is a concrete algebraic adapter, not a replay of the selected provider or caller.

**Routing that cannot stay bounded.** At the middle cut, a half-swap unfolds to a full permutation matrix; a phase `(-1)^(a dot b)` unfolds to a Walsh matrix. Exact rank and discarded Frobenius energy give the bounds above, including operator-norm approximation. Fixed transfer dimension fails for both families as width grows, in this column order. Changing column order, growing state or a different representation may evade them.

The signed phase and norm statements use complex coefficients. They are not F2/BIT bounds: in characteristic two those signs coincide. The prototype checker implements Q(i).

**Two misleading probes.** A three-state example vanishes on every constant repeated column yet fails on a mixed word of length two. A fixed unitary `α_N=(N+i)/(N-i)` has error at most 2M/N through width M, but some later width has error at least sqrt(2). Exact closure certificates work; short-width tolerance tests need a separate conditioning/contractivity theorem.

## Run and inspect

Python 3.10+ and its standard library are sufficient. From the repository root:

```sh
python3 -B research/finite-memory-lifting/certify.py \
  research/finite-memory-lifting/examples/prefix-inverse.json > /tmp/prefix-certificate.json
python3 -B research/finite-memory-lifting/check_certificate.py \
  research/finite-memory-lifting/examples/prefix-inverse.json /tmp/prefix-certificate.json
python3 -B research/finite-memory-lifting/verify.py
python3 -O -B research/finite-memory-lifting/verify.py
python3 -B research/finite-memory-lifting/audit_mutations.py
# Optional byte authentication against the pinned canonical checkout:
python3 -B research/finite-memory-lifting/verify.py --source-root .
```

The standalone checker can be distributed with `exact.py`, the problem and certificate; it does not need `certify.py`, `models.py`, Git or repository sources. Python isolated mode omits the script's sibling-module directory, so these commands use `-B`; the portable audit additionally supplies a fresh bytecode-cache prefix in a private directory. Arbitrary preexisting Python import environments are not authenticated by these direct commands.

The problem format declares `local_dimension`, `states`, `outputs`, `inputs`, `left`, `right` and a `transitions` object indexed by canonical `"output,input"` pairs. Every absent pair is the zero transition. Matrices use explicit integers/fraction strings or `[real,imaginary]` pairs. Floats, exponent notation, duplicate JSON keys and malformed dimensions reject. Supply the **residual** operator, including every required return. A counterexample names a physical entry; it is not a profitable program or a priced native witness.

## Evidence and attribution

[RESULT.json](RESULT.json) records exact finite calibration; [VALIDATION.json](VALIDATION.json) records the executed environment, output hash, portable and optimized checks; [MUTATIONS.json](MUTATIONS.json) records private semantic mutations. Tests cover literal path sums, sharp delayed counterexamples, full prefix matrices, exact source phases/returns, rank/Gram routing controls and forged-certificate rejection. Finite checks corroborate the written proof; they are not its universal justification.

Canonical base: [`32890bc5de034ab8fc93ac88ead7279a6a416d04`](https://github.com/CrocSwap/integer-mult-bounds/commit/32890bc5de034ab8fc93ac88ead7279a6a416d04), priority revision 7, selected conditional κ=.003027288235. [SOURCES.json](SOURCES.json) binds seven canonical provenance files and the classical literature. [OVERLAP.json](OVERLAP.json) records bounded coverage and the scope distinction. Closed historical bodies, arbitrary code diffs and unpublished work are not exhaustively searched.

The closest work is [#5235](https://github.com/CrocSwap/integer-mult-bounds/pull/5235)'s independent-operator register certificates by [zxv](https://github.com/zxv), [#5262](https://github.com/CrocSwap/integer-mult-bounds/pull/5262)'s true-inverse extension by [Krzysztof Wójt](https://github.com/krzysztofwojt), [#5352](https://github.com/CrocSwap/integer-mult-bounds/pull/5352)'s bit bounds by [Ali Romman](https://github.com/aliromman), and [#5369](https://github.com/CrocSwap/integer-mult-bounds/pull/5369)'s specialized physical native criterion. The new physical-pair alphabet resolves operator relations directly and permits finite-memory column coupling. It does not replace the predecessor frontends or their substantially more compact certificates in their own domains.

Retain [the recipe/source attribution](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/native-tensor-cutoff/README.md#sources-and-credit), including [Jose Manuel](https://github.com/jmbarrancoml)'s [#2250](https://github.com/CrocSwap/integer-mult-bounds/pull/2250) implementation and its native, phase, compiler and verification lineage. The [weighted-automata theorem](https://people.mpi-sws.org/~joel/publications/Q_weighted_automata13.pdf) and [matrix-product correspondence](https://arxiv.org/abs/0708.1221) are classical, as are cut-rank and projection-error arguments. New prose/code are Apache-2.0 with substantial OpenAI Codex assistance. No independent human or formal-kernel acceptance is claimed.

No full 112-owner/17-axis provider, selected cold replay, physical cross-column implementation, paid/tape/precision bill, generic replay registration, Lean or Docker run is included.

## Significance for researchers

The result makes a named class of cross-column proposals testable without forcing it into a columnwise or free-word model. A successful table yields complete all-width semantics with inspectable certificates; a failed table yields a concrete input/output discrepancy. Cut-rank certificates can reject bounded-state routing proposals before expensive synthesis, including some approximate proposals. The first work for an active caller is now explicit: extract its true physical transfer tables, retain source versions and returns, and measure dimension/column order before pricing a construction.

## Open next questions

| Direction | Useful first result | Risk or blocker |
|---|---|---|
| **One actual provider/consumer** | Extract a complete endpoint from [#5419](https://github.com/CrocSwap/integer-mult-bounds/pull/5419)'s changed-interface program or another source-bound caller. | State/table expansion may make the representation unusable; missing observations remain missing. |
| **Physical observation audit** | Bind one candidate relation from [#5427](https://github.com/CrocSwap/integer-mult-bounds/pull/5427) to actual local entries and phases. | Its formal-word nonmembership is not automatically physical nonmembership; this package has not decided that source question. |
| **A legal cross-column adapter** | Implement prefix encoding and return in a permitted native/tape contract. | Virtual dimension two does not price memory, access, copying or inversion. |
| **Source-specific cut certificates** | Exhibit one exact coefficient minor for an actual routing or observation demand. | Legal column reorderings and preexisting side information can change the cut. |
| **Compact table extraction** | Reuse [#5235](https://github.com/CrocSwap/integer-mult-bounds/pull/5235), [#5262](https://github.com/CrocSwap/integer-mult-bounds/pull/5262) and [#5352](https://github.com/CrocSwap/integer-mult-bounds/pull/5352) to avoid explicit word expansion in one physical frontend. | Concrete relations and succinct extraction can be harder than equivalence of the final table. |
| **Uniform approximate certification** | Add a proved contraction/conditioning hypothesis and an actual recovery error budget. | Finite-width tolerance tests fail even for fixed unitary families. |
| **Complete cost transfer** | Turn a semantically accepted table into a priced supplier or a justified scoped rejection. | The representation theorem alone settles none of the selected compiler, tape, storage, precision or analytic assumptions. |
