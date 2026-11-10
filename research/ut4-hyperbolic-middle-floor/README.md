# Exact central UT4 tariffs for every restored dirty workspace

This contribution was produced by Nick Petalas. Apache-2.0.

Scoped proof: in ToikY's PR1662 formal F2[UT4(F2)] model, w central
targets require at least 4w paid b calls, for every finite number of
arbitrary restored dirty roles. The stronger bound is

    n_b >= 2w + rank(X_b) + rank(Y_b).

With the credited outer bounds and direct construction, the exact complete
tariff is 2w alpha+4w beta+2w gamma for all nonnegative uniform letter
prices. The unit minimum is 8w. In particular, neither remaining
seven-b rank pattern, (2,3) or (3,2), can realize two central targets.
This settles the mixed-rank question in Victor Li's
[PR3938](https://github.com/CrocSwap/integer-mult-bounds/pull/3938).

The new step stacks both a/c prefix maps and concatenates both suffix
maps. Their product is [[0,P],[P,0]], of rank 2w, and factors through
ker(X_b)/im(Y_b). [PROOF.md](PROOF.md) gives the full argument.
The lower bound already holds in the retained degree-three quotient;
no larger census or higher coefficient is needed. No new kappa or
selected-frontier change is claimed.

## Reproduce

From the worktree root with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/ut4-hyperbolic-middle-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/ut4-hyperbolic-middle-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/ut4-hyperbolic-middle-floor --check-source-history
```

Other machines may substitute their CPython 3.12 path. The standalone
verifier works in a Git-free six-file export and writes nothing. It emits
PASS_UT4_HYPERBOLIC_MIDDLE_FLOOR and a generated receipt containing all
six file hashes. Registered warning-strict normal and optimized checks
use explicit exceptions, so optimization cannot disable the checks.

Finite corroboration checks the new paired coefficient identities on
20,632 words, consisting of every two-role word through length three
and 192 deterministic eighteen-call three-role words. Polynomial
multiplication and prefix/suffix construction use different paths.
Forty-two attaining words through six roles have complete full-group
algebra endpoint checks, including common scalar conjugations and every
dirty output block. Eighty omitted-call controls and ten additional
contract, endpoint and hypothesis controls reject. The universal result
is the written rank argument, not extrapolation from these fixtures.

## Credit, overlap and scope

Credit ToikY / [PR1662](https://github.com/CrocSwap/integer-mult-bounds/pull/1662)
for the alphabet, fixed quotient homomorphism, outer and middle span
bounds, earlier rank-w middle quotient and direct (2,4,2) word. Credit
Victor Li / PR3938 and
[PR3887](https://github.com/CrocSwap/integer-mult-bounds/pull/3887) for
the mixed-rank question and earlier scoped exclusions. Credit Josie
Elliston / [PR1816](https://github.com/CrocSwap/integer-mult-bounds/pull/1816)
for two-target unit optimality and the weighted question. Retain Aaron
Wang / PR1690's profile lineage, ToikY / PR1680's workspace reduction,
and the steph4n-gh / PR1573, Arham Tahir / PR1589 and Hanson Sun / PR1607
register-model lineage credited by PR1662. The direct upper word and
outer floors are inherited. The paired middle quotient is the new result.

All source files in [SOURCES.json](SOURCES.json) are provenance only.
No predecessor program or census is imported, audited or replayed.
The scientific base is 7c49fe32c55de02c2c873655c804b16e4c3fef0a,
priority revision 8. The selected-binding baseline passed. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19360859)
asked about seven middle calls; the same new argument yields the uniform
tariff directly. Live PR bodies, recent account work, handoffs, batch
reservations, merged searches and distinctive main README searches were
checked. Sparse local coverage and unpublished work remain limitations.

The historical bit-new-register-model card is refined to this formal
tariff obstruction. It gives a stopping rule for this alphabet, rather
than a physical BIT improvement. Role-dependent prices, extra free
address maps, rational frames, clean allocation, native realization,
compiler/hosting, stock, precision, tape and analytic recovery are outside
the result. The five selected framework assumptions remain. No selected
supplier replay, Lean or Docker run was made. Independent human and
formal proof-kernel review are unclaimed.

## Open next questions

Can a changed operation alphabet, such as an additional paid address
letter, escape the 4w middle floor? Start by computing its image in Q
and deciding which equations in (1) of the proof cease to hold. A
candidate must pay for the added operation and retain arbitrary dirty
restoration before it can affect a supplier invoice. The present theorem
does not cover that changed alphabet. Structured details are in
[TASK.json](TASK.json).

## Verifier constraints

The six-file verifier has no recursion, subprocesses, network or output
files. Its fixed domains have at most six roles, 48 calls, 64 group
elements and 20,632 coefficient fixtures. Functions are below 60 lines;
matrix/rank dimensions and file reads have explicit limits. Failures
propagate as exceptions. The local AST/compile inspection and both
warning-strict modes are the available Python diagnostics.

Power-of-ten rule 3 deviation: CPython allocates managed integers and
containers during the finite command. Live state is bounded by the
fixed domains above, with at most 64 group matrices or 17 quotient
matrices per endpoint. Rule 9 deviation: rejection controls dispatch
only to quotient_rank, coupling, validate_word and central_check with
fixed local fixtures. No arbitrary callback or code loading is accepted.
An embedded fixed-allocation implementation would need a separate runtime.
