# The sharp all-precision quadratic Neumann truncation is 226 p²

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped proof with exact finite corroboration. No new κ.**

For every integer `p >= 1`, set `g = 1/(16p)` and `J = 226p²`. Then

```text
2(1-g)^J/g = 32p (1-1/(16p))^(226p²) < 2^(-16p).
```

Moreover, **226 is the smallest nonnegative integer coefficient** that works
in `J = c p²` simultaneously for every positive integer precision. The
coefficient 225 fails at `p = 1`.

Jose Manuel's [PR #3851](https://github.com/CrocSwap/integer-mult-bounds/pull/3851)
uses `J = 512p²` in the normalized Gaussian core. Its proof bounds the
difference between the global inverse and a principal-window inverse by
the scalar tail above and imposes margins larger than `Jw`.
James Reed's [PR #3864](https://github.com/CrocSwap/integer-mult-bounds/pull/3864)
checks the 512 coefficient for precisions 101 through 200 and at precision 1.
Those source results are cited, not replayed as this contribution. The new
step is the smaller truncation prescription, its all-precision proof and its
exact optimality within this integer quadratic family.

## Proof

At `p = 1`, the two exact integer comparisons are

```text
2^21 * 15^226 < 16^226,
2^21 * 15^225 > 16^225.
```

Thus 226 succeeds and 225 fails. The tail decreases strictly with the
coefficient, so every nonnegative integer coefficient below 226 also fails
at precision 1. This proves the required lower bound without a search over
coefficients.

For the uniform upper bound at `p >= 2`, put `n = 16p`. The first four
terms in the binomial expansion give

```text
(1 - 1/n)^(-n) = (1 + 1/(n-1))^n
  >= 1 + n/(n-1) + n/(2(n-1)) + n(n-2)/(6(n-1)^2)
   = 8/3 + (9n-10)/(6(n-1)^2)
   > 8/3.
```

This uses only the integer binomial theorem and positivity, since `n >= 32`.
Consequently `(1-1/(16p))^(16p) < 3/8`. As `226p² >= 224p²`,

```text
32p (1-1/(16p))^(226p²) * 2^(16p)
  < 32p [(3/8)^14 * 2^16]^p
   = 32p (3^14/2^26)^p
   < 32p / 8^p
  <= 1.
```

The second strict inequality is the integer comparison `3^14 < 2^23`.
The final inequality follows by induction. At `p = 2`, `32p = 8^p = 64`.
For each `p >= 2`, the ratio of consecutive values of `32p/8^p` is
`(p+1)/(8p) <= 3/16 < 1`. Together with the precision-1 comparison, this
proves the upper bound for every positive integer precision.

The uniform quantifier comes from this argument. The sixteen direct
comparisons in the verifier are finite corroboration, not its proof.

## Consequence and limits

Whenever the inherited caller supplies the same contraction `g = 1/(16p)`
and the same prefactor `2/g`, 226p² terms suffice for its stated tail budget.
In the locality argument, a bandwidth-w path of length below J stays inside
the retained window under a margin larger than Jw. This scalar result permits
that argument to use `226p²w` in place of `512p²w`, subject to all its other
hypotheses. No caller code or production-domain predicate is changed here.

The result does not establish the contraction, the inverse-norm hypotheses,
rounded arithmetic error, physical evaluation cost, complete outer tensor or
integer recovery. The production core starts at `p >= 101`, so the global
optimality witness at `p = 1` does not establish optimality restricted to its
production domain. A nonquadratic prescription may be smaller. No independent
human or formal proof-kernel review, complete multiplication theorem or
selected-frontier change is claimed.

## Reproduce

From the repository root, using Python 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/optimal-neumann-quadratic-tail/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/optimal-neumann-quadratic-tail/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/optimal-neumann-quadratic-tail
```

Expected output includes
`PASS_OPTIMAL_NEUMANN_QUADRATIC_TAIL coefficient=226 excluded=225 direct_precisions=16 domain_controls=4 no_new_kappa`.
The verifier checks both precision-1 integers, the polynomial identity in
the binomial proof, the induction constants, and the full tail at each
precision 1 through 16 by both integer and rational arithmetic. It rejects
four out-of-domain calibration calls and confirms that coefficient 225 fails.
Checks use explicit exceptions and remain enabled under optimized Python.

Normal replay writes nothing. `verify.py --receipt /absolute/new/path.json`
creates a receipt with the result, interpreter version and SHA256 hashes of
all five package files. It refuses an occupied output. Receipts and logs
belong outside the checkout. No hand-written receipt is supplied.

All [source pins](SOURCES.json) are historical provenance. The new proof and
verifier import no predecessor executable and have no external live inputs.
The [task record](TASK.json) records the scope change from proof audit to an
original truncation improvement, overlap coverage and local validation.

## Open next questions

1. What is the least quadratic integer coefficient when only `p >= 101`
   is required? The precision-1 obstruction disappears. First prove a
   monotonicity bound for the normalized logarithmic tail on that domain,
   then check its actual integer boundary. This is separate from the
   all-positive-precision optimum proved here.
2. Can the production caller use the smaller window margins while preserving
   every setup, rounding, routing and ownership obligation? First trace each
   occurrence of J in the exact PR3851 caller and retain its full error sum.
   The present scalar theorem does not supply that integration.

## Predecessor credit and coordination

Jose Manuel, `jmbarrancoml`, supplies the physical Gaussian core, the global
and principal inverse comparison, the `1/(16p)` contraction and the original
512p² prescription. His retained Chafik Boukhalfa, RaD project, Mason Hale,
Dugongue and upstream FFT/Gaussian lineage keeps its credit in the unchanged
source. James Reed, `jwr404`, supplies the finite-range tail package.
Classical binomial and geometric-series inequalities are used here; no claim
of priority for those general methods is made.

The canonical [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144249)
states the same scalar question. Base main is
`a5df48c55ea806d7952b65acc9c76d878ff09b13`, priority revision 7.
Live PR and Discussion searches, merged-PR searches and tracked README
searches found no same-question result at the claim checkpoint. Sparse
working-note cache coverage is incomplete; the direct Git search covers
tracked README files. Unpublished work and arbitrary code diffs are outside
these overlap checks.
