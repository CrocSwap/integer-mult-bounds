# Multiplicative shell counts have the sharp valuation-rank exponent

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

Claim type: scoped written mathematical proof with exact finite corroboration.
For every fixed finite integer alphabet containing the height base M>=2,
let r be its rational prime-valuation rank. Its multiplicative monoid has

    J_l = Theta((l+1)^(r-1))

elements in the half-open shell [M^l,M^(l+1)). The new step is an effective
matching lower bound for JoyboyBrian's
[PR6086](https://github.com/CrocSwap/integer-mult-bounds/pull/6086).
The predecessor upper theorem is cited, not reverified.

Choose generators g_1,...,g_d whose valuation vectors extend v(M) to a
basis, with d=r-1, and put H=max_i ceil(log_M g_i), or H=1 if d=0.
The lower bound is

    J_l >= binom(floor(l/H)+d,d),   for every integer l>=0.

Each bounded exponent tuple supplies one distinct shell element after
multiplication by the least suitable power of M. The [proof](PROOF.md)
also gives the exact shell-count formula for independent generators.
Dependent alphabets and rank one are included in the lower theorem.

Using PR6086's reported p16 rank eleven as a premise gives a matching
shell degree ten for that historical alphabet. The full-monoid exponent
cannot decrease. A better actual width bound must use further information,
such as reachable plateau restrictions or LCM cancellation. This is not a
lower bound on compiler widths, physical costs or multiplication complexity.
No new kappa, supplier, selected-frontier update or framework-assumption
discharge is claimed.

## Scope and evidence

The base is `e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8.
The source-binding orientation check reports selected #7000 at conditional
kappa 0.00363005817; the older strategic text predates that selection.
[TASK.json](TASK.json) records the change from the caller-bound
`uniform-transfer-audit` card to this adaptive-compiler counting side result.
[SOURCES.json](SOURCES.json) pins the catalogue, selected record and cited
predecessor documents as provenance. The checker has no external live inputs.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19538428)
reserves the lower-bound question. Live overlap checks covered open PR
metadata, recent handoffs and active Discussions, this account's previous
PRs, merged searches and all-main README searches for shell lower bounds,
valuation rank and semigroups. These searches do not cover unpublished work
or every historical source file. PR6086 proves the upper theorem. PR5962
and PR6612 give different width upper bounds and cancellation results.

The exact finite checker constructs 360 alphabet/base fixtures and checks
1,800 shells, including 4,016 lower-witness occurrences. Multiplicative
closure agrees with an independent integer-divisibility membership oracle
in every fixture. Seven independent-generator models give 49 exact shell
identities with 297 point occurrences. Nine controls cover invalid domains,
dependent generators, the excluded upper endpoint, capacity exhaustion,
the missing-base hypothesis and rank one. These counts describe the declared
finite domains; the universal conclusion rests on the written proof.

## Reproduce

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/multiplicative-shell-sharpness/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/multiplicative-shell-sharpness/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/multiplicative-shell-sharpness
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/multiplicative-shell-sharpness --check-source-history
```

Substitute any CPython 3.12 path on another machine. Run the last command
after committing. Each direct run prints `PASS_MULTIPLICATIVE_SHELL_SHARPNESS`
inside a generated JSON receipt with counts and SHA256 of all six package
files. It writes no files. The registered runner executes both modes and
checks metadata and Git pins. No receipt is handwritten.

No predecessor scientific replay, actual p16 compiler, selected cold replay,
Lean, Docker, physical caller or complete multiplier is run or certified.
The constants are fixed-alphabet constants. Varying alphabets/bases,
restricted reachable subsets and monoids without M are outside the theorem.

## Open next questions

1. Can one nonhomogeneous compiler use a smaller actual reachable set?
   Derive its exact plateau language, retaining every chronological cut.
   A proved reachability invariant and full LCM bound are missing.
2. Can source-count prime valuations improve the level-LCM bound despite
   the sharp shell exponent? Start with an all-prime cancellation bound
   along actual decreasing child chains in one nonhomogeneous profile.
   Counting shell elements alone does not control those valuations.

## Credit

JoyboyBrian supplies PR6086's upper shell theorem, adaptive application and
open finite-bound question. Retain codyw912's PR4638 level-LCM recurrence,
Nick Petalas's PR5962 refinement, Mihir Srivastava, zxv, Jacob Alan Sussman,
Ryanson Jonathan, Cinna Davis and the predecessor compiler/native lineage.
PR6612 is cited only to distinguish cancellation from counting. Unique
factorization, valuation independence and stars and bars are classical;
general literature priority is unclaimed. No predecessor files are changed.

## Implementation constraints

The checker has no recursion, subprocesses, network, dynamic evaluation or
package writes. Every enumeration is finite. Its main fixture list has
360 entries and five levels each; the exact free-model list has seven
entries and seven levels each. Matrix work is bounded by eight rows and
six columns. Constructor domains have at most three independent directions
and levels at most sixteen. Closure has a one-million-integer ceiling;
the separate literal oracle has an 8,000-integer ceiling. Runtime contracts
raise explicit exceptions and remain active with Python optimization.
All functions fit within 60 physical lines.

Power of Ten rule 3 deviation, `verify.py`: Python sets, Fraction and integer
operations allocate during verification. Fixed allocation conflicts with this
standard-library reference's managed runtime. The finite capacities above
bound live data; only one alphabet is processed at a time. Boundary rejection
controls and both interpreter modes check those limits. Runtime-internal
allocation was not instrumented. A fixed-allocation implementation is needed
before making any native fixed-memory claim.

Rule 9 deviation, `check_controls`: a fixed seven-case table dispatches to
four named checker functions, with no user-selected target or lifecycle.
All seven rejecting calls are executed. Replace this test-only dispatch if
the checker is ported to a platform forbidding indirect calls. Rule 10 uses
warning-strict normal/optimized execution and AST inspection. No separate
project-wide type checker or linter is claimed.
