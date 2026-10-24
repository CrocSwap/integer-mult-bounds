# A sharp quadratic rounding guard for closed words

This contribution was produced by Nick Petalas. Claim type: scoped mathematical
proof with exact finite corroboration. No new kappa is claimed.

The generic simultaneous-rounding prescription in
[ywz65's PR2701](https://github.com/CrocSwap/integer-mult-bounds/pull/2701)
uses `p+ceil(log2(8 K B^3))` fractional bits, where `B` bounds every exact
prefix and its inverse. Retaining a separate endpoint norm `C>=1` gives

```
P = p + ceil(log2(8 K C B^2)).
```

For an exact closed word, `C=1` and the sufficient power falls from `B^3`
to `B^2`. For dyadic `B=2^q`, this saves exactly `q` fractional bits in
the displayed guard. The required endpoint and prefix certificates remain
hypotheses. This is an improvement to the final-output bound, not a smaller
uniform bound for every intermediate state.

The [proof](PROOF.md) gives the full trajectory estimate

```
||y_K-F_K y_0|| <= C (rho M+B sum_j ||u_j||)/(1-rho),
rho=sum_j ||F_j^-1 Delta_j F_(j-1)|| < 1.
```

It also gives matching all-size elementary words. With `b=2^q`, `L`
opposite shear pairs, and common prefix/inverse maximum `B_*=3b/2`, their
exact errors are `2L b^2 eta` at a closed endpoint and `2L b^3 eta` at an
endpoint of norm `b`. Every exact gate and inverse has norm at most two;
every exact and perturbed gate has determinant one. Taking `L=q` proves
that the respective quadratic and cubic powers cannot be lowered, including
the gate-count factor, in the stated bounded coefficient-error model.
Optimal numerical constants are not claimed.

## Evidence and reproduction

From the repository root, use CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/closed-word-rounding-guard/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/closed-word-rounding-guard
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/closed-word-rounding-guard --check-source-history
```

The interpreter path is the local reproduction environment. On another machine,
substitute a CPython 3.12 interpreter. `VERIFY.json` registers warning-strict
normal and optimized runs. Every mathematical check uses explicit branches and
remains active under `-O`. The verifier writes no files. `--emit` prints a
computed receipt bound to the package file hashes; redirect it outside the
checkout if desired.

Exact rational checks multiply the two independent input columns directly and
also use a separate interaction recurrence. They check the sharp identities,
literal prefix/inverse envelopes, bounded gates and determinant preservation.
The simultaneous guard checks add a noncommuting detour and perturb every
gate while injecting arithmetic errors. Controls reject a smaller power,
an endpoint-only premise, singular matrices, malformed/capped requests and
an exhausted small-error premise. The printed counts are finite corroboration;
the written proof supplies all-size coverage.

The checker caps a trajectory at 256 two-by-two gates, an excursion at
`q<=16,L<=32`, and the guard search at 128 candidates. Its fixed finite
calibrations use smaller limits. Functions fit within 60 physical lines.
Rational arithmetic uses managed allocation rather than preallocated storage;
the fixed matrices and bounded loops constrain the live data. Five fixed
rejection callbacks are a test-only indirect-call exception. Warning-strict
normal and optimized execution supply the available interpreter diagnostics.

## Scope and limitations

The lower examples describe admissible bounded coefficient perturbations,
including errors in nonzero dyadic shear coefficients. They do not assert that
nearest rounding on those coefficients generates those errors. A specified
rounding rule could impose additional restrictions.

This package does not bind a production emitted caller, implement reversible
rounded arithmetic, certify integer bits or overflow, price physical movement,
admit a supplier, or prove the complete multiplication theorem. No selected
cold replay, native replay, Lean or Docker build is required or claimed.
Independent human and formal proof-kernel review are unclaimed.

The card `formal-interface-lemma` is changed to this original written
precision-interface result. The selected source-binding positive control was
run before the algebraic work; its metadata check is not an operator replay.
The first proved improvement ends this investigation.

## Sources and overlap

Credit ywz65's PR2701 for the simultaneous interaction-coordinate theorem and
the original `8 K B^3` guard, and Vlado Vojdanovski's PR1673 for its capped
Toeplitz precision interface and retained predecessor lineage. Standard
product perturbation mathematics is not claimed as new. The contribution is
the endpoint-conditioned guard and the matching bounded elementary-word
obstruction. No predecessor executable is imported or rerun as the result.
The source README is pinned by Git blob and SHA256 in `SOURCES.json`.

The base is `a5df48c55ea806d7952b65acc9c76d878ff09b13`, priority revision 7.
Before the claim, the overlap helper covered 306 open PRs and 4,307 Discussion
records with complete remote pagination. The local sparse note scan covered
154 of 6,918 HEAD note paths; all-main distinctive-term searches supplemented
it. Live recent account work, handoffs, active Discussions and merged PRs were
also checked. These checks do not cover unpublished work or arbitrary diffs.

## Open next questions

1. Which production caller has a certified endpoint norm `C` much smaller
   than its prefix bound `B`? Pin one emitted word and prove its endpoint
   norm before applying the guard. A caller binding and arithmetic kernel
   remain missing.
2. Can a specified deterministic rounding rule improve the guard further?
   Start by identifying which correlated shear errors that rule can realize.
   The present arbitrary bounded-error model does not answer that question.

Structured versions, including relevance and blockers, are in `TASK.json`.
Apache-2.0.
