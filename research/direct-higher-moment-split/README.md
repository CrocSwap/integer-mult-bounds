# Sharp direct higher-moment split charge

For every real `0<t<1` and `sigma>1`, the least coefficient in

```
split_t(R,J) <= K(t,sigma) R^sigma J^(t-sigma),
R=qJ+r>J,  0<=r<J,
split_t(R,J)=q J^t+r^t,
```

is

```
K(t,sigma) = (1+s^t)/(1+s)^sigma,
t s^(t-1)+(t-sigma)s^t-sigma=0,  0<s<1.
```

The defining equation has one solution, and the coefficient is sharp over
integer jobs. This answers Open next question 2 of
[PR4832](https://github.com/CrocSwap/integer-mult-bounds/pull/4832).
The claim type is a scoped written proof with exact finite corroboration.

The coefficient is strictly smaller than the linear-rank coefficient
`K(t,1)` transferred to the higher moment. At `t=1/2, sigma=17/10`,

```
K = (5/4)(16/17)^(17/10),
9/8 < K < 8/7 < 6/5 < K(1/2,1).
```

Every `J=16n, R=17n`, with positive integer n, attains this new coefficient.
[PROOF.md](PROOF.md) proves the universal optimization, integer sharpness and
its exact strictification consequence. No new kappa or selected-frontier change
is claimed.

## What changes in the retained compiler estimate

Retain all hypotheses of zxv's
[PR4433 higher-moment construction](https://github.com/CrocSwap/integer-mult-bounds/pull/4433).
With `C=1-t` and `u>C`, its complete sufficient charge improves as follows.

```diff
-alpha^v + K(t,1)   gamma_u^v + 2 delta^v
+alpha^v + K(t,t+u) gamma_u^v + 2 delta^v
```

The full completion charge and unsplit overcount remain. The proof derives
this consequence from the credited moment-product premise, without replaying
predecessor programs or numbers. This is a sharp coefficient for the full
split charge, not a net-tax optimum, a smaller demonstrated tensor power or
a newly admitted supplier. PR4483's different direct compiler can avoid
strictification under its own gates.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/direct-higher-moment-split/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/direct-higher-moment-split/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/direct-higher-moment-split
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/direct-higher-moment-split --check-source-history
```

Other hosts may substitute their CPython 3.12 path. The last check requires
committed publication bytes. The scientific command prints a JSON receipt with
`PASS_DIRECT_HIGHER_MOMENT_SPLIT`; the runner prints
`PASS_REGISTERED_RESEARCH_PACKAGE`. To save a generated receipt, append
`--receipt /absolute/path/outside/the/checkout.json` to a direct command.
Normal replay writes no files. Receipts bind all six package files and both
source documents by SHA256; no receipt is hand-written or treated as an oracle.

The finite verifier checks 30 rational parameter pairs, 7,650 exact integer
splits, 6,720 strict quotient comparisons and 30 near-maximizing integer
witnesses. It also checks the exactly attaining family representative and
13 rejecting controls. Rational polynomial bisection encloses each maximizing
remainder; comparisons use powers of positive rational numbers. No floating
point or predecessor executable is used. The written proof covers arbitrary
real parameters; finite examples do not supply that universal quantification.
Checks remain enabled under Python optimization.

## Scope and overlap

The `uniform-transfer-audit` card is changed from assumption audit to a new
compiler coefficient theorem. This side result tightens one sufficient
accounting bound; it does not discharge any of the five framework assumptions.
The documented first source-binding control passes against selected PR6030.
Source provenance is canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.

[The advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19358948)
records the exact question. Entry checks inspected live open PRs, recent handoff
claims, merged titles/bodies and distinctive formulas in all tracked main
package READMEs. The question source predates the recent contribution series.
Search coverage does not certify novelty; sparse notes, arbitrary historical
diffs and unpublished work remain limits.

Native semantics, dirty restoration, paid placement, chronological compiler
closure, precision, stock, tape access and exact recovery remain inherited
obligations. No physical caller, selected cold replay, native suite, Lean or
Docker run is supplied. No independent human or proof-kernel acceptance is
claimed.

## Verification design

The verifier has no recursion, subprocesses, callbacks or imported predecessor
code. All scientific loops have explicit finite bounds. Its census uses six
exponents, five higher moments, 32 remainder parameters and eight quotients;
root isolation takes 72 steps. Rational parameters have denominators at most
16, `0<t<1` and `1<sigma<=4`. Functions stay below 60 physical lines. Input
source documents must match the declared hashes.

Power of Ten deviation, rule 3: Python's integers, fractions and JSON serializer
allocate dynamically. The fixed census, root precision, parameter limits and
2 MB per-file check bound this verifier's mathematical workload. The reviewed
local metadata files and synchronous standard-library reads are trusted inputs;
this is not an allocation-free or hostile-filesystem parser. A fixed-memory
port would be needed if that execution contract becomes a requirement.

## Open next questions

- Apply the coefficient to one fully charged supplier that still uses
  strictification. First reuse its exact moment enclosures and replace only
  this coefficient. A smaller sufficient tensor power must retain all native,
  completion, compiler and outer premises.
- Determine the least direct coefficient for the net splitting tax. Start with
  `(q+s^t-(q+s)^t)/(q+s)^sigma`, and inspect PR4480's net-tax bounds. The quotient
  monotonicity here concerns a different objective and cannot be transferred.

## Credit

This contribution was produced by Nick Petalas. Independent human and formal
proof-kernel review are unclaimed. Apache-2.0.

PR4832 supplies the question and linear-rank predecessor. zxv's PR4433 supplies
the higher-moment splitting/completion framework; PR4480 and PR4483 retain their
net-tax and direct-compiler results. Cinna Davis's PR4412/4414/4416 supplies the
chronological tensor product and padding construction. Jacob Alan Sussman
supplies the integer compiler. Their native, helper, controller and outer
predecessors retain their existing credit. Elementary one-variable calculus
is classical; no literature-priority claim is made.
