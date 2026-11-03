# Exact collision-free projection density on composite axes

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written algebraic proof with exact finite corroboration.
For every modulus m>=2 and nonempty finite primitive demand list D in
(Z/mZ)^2, the exact number of coefficient pairs v for which d.v is nonzero
for every d in D is

```text
A_m(D) = m^2 - 1 - sum_{q|m, q>1} phi(q) d_q.
```

Here d_q counts the distinct demand classes modulo q under multiplication
by units, and phi is Euler's totient. There are exactly
`J_2(m)-phi(m)d_m` primitive safe pairs. A safe pair exists exactly when
`d_m < psi(m) = m product_{p|m}(1+1/p)`, and a primitive safe pair can always
be constructed. The sharp blocking threshold is therefore psi(m) demand
classes. The empty list is handled separately. [PROOF.md](PROOF.md) gives
all quantifiers, the divisor decomposition and the witness construction.

For example, modulo 9 the demands `(1,0),(1,3)` have d_3=1 and d_9=2,
giving exactly 66 safe pairs. Omitting the proper divisor gives 68;
using a field-style distinct-line count gives 64. The three points
`(0,0),(1,0),(2,3)` have primitive pairwise differences and exactly 60
injective scalar projections among all 81 coefficient pairs.

## Connection and limits

David Ganz / Dugongue's [PR5564](https://github.com/CrocSwap/integer-mult-bounds/pull/5564)
constructs prime-free coprime grids and leaves their complete numerical
caller open. This takes one arithmetic step in its Open next question 1:
collision avoidance for two-coordinate modular projections. The result
identifies the divisor-level data required by a composite axis. It builds
on that question without auditing or replaying the predecessor's construction.
The card's admission-audit scope is explicitly changed in TASK.json.

For a point set with every pairwise difference primitive modulo m, apply
the formula to one signed copy of each difference. It then counts the
injective projections exactly. It does not cover arbitrary nonprimitive
differences, more than two coordinates or a numerical aliasing bound.
The blocking threshold concerns arbitrary primitive demand lists; not every
list is asserted to arise as all differences of a prescribed point set.

No actual selected caller, numerical resampling, integer recovery, native
implementation, physical movement, precision/storage, compiler closure or
complete paid budget is established. No new kappa, selected-frontier change,
complete multiplication theorem, independent human acceptance or formal
proof-kernel review is claimed. The selected binding-only positive control
passed; the selected scientific cold replay, Lean and Docker were not run.

## Reproduce

From the repository root, CPython 3.12 and the standard library suffice:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/composite-projection-density/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/composite-projection-density/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/composite-projection-density
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/composite-projection-density --check-source-history
```

Substitute another CPython 3.12 path on another machine. The direct marker
is `PASS_COMPOSITE_PROJECTION_DENSITY`; the registered marker is
`PASS_REGISTERED_RESEARCH_PACKAGE`. Stdout is a generated JSON receipt
bound to all seven package files and the exact predecessor context bytes.
No receipt is handwritten or committed. Direct checks write no files.

[density.py](density.py) supplies `projection_count(m, demands)` and
`projection_witness(m, demands)`. The executable accepts m from 2 through
64, at most 256 demands and integer coefficients of magnitude at most 2^31.
The mathematical theorem has no such finite size caps. A primitive demand
means `gcd(a,b,m)=1`; either coordinate individually may be a nonunit.

The checker derives its oracle from complete literal dot-product kernel
bitmasks, independently of the class formula. It checks every subset of
all kernel representatives for moduli 2 through 9. For the sixteen named
larger moduli through 64, it checks empty/full lists, every singleton,
every full-list single deletion and every pair among the first twelve
representatives. The generated receipt enumerates all shapes and counts.
The exhaustive part has 12,696 subset comparisons; larger shapes add
2,680 comparisons. All agree, including the primitive counts and witness
existence. Additional checks cover duplicate and signed demands, the literal
three-point injectivity example, twenty rejecting invalid calls and three
false-formula controls.
No predecessor executable is imported or replayed.

## Open next questions

1. Extend the count to nonprimitive demands. Start with mixed contents
   modulo 9 and compute the union of congruence conditions at different
   depths. The present primitive-kernel disjointness no longer applies.
2. Bind a literal resampling/recovery caller to the primitive-difference
   contract, then price coefficient selection and movement. A proof of
   the required gcd conditions and the complete numerical error contract
   is still missing.

Structured relevance, first steps and blockers are in [TASK.json](TASK.json).
Research stops at the first exact count and witness criterion.

## Sources and overlap

Base canonical main is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8, selected PR6030. [The advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19375509)
precedes substantial implementation. Live handoffs, active Discussions,
open/account PRs, local reservations, main README formulas and several
merged/general-form searches were checked. The refreshed broad cache covered 575 open PR records and 6,651
Discussion records with complete reported pagination. Sparse local notes,
arbitrary diffs, unpublished work and general literature novelty remain
outside that coverage. No exact matching result was identified in those searches.

Credit David Ganz / Dugongue's composite-axis question, ToikY's guard-safe
bands, Jose Manuel's tensor caller, Tekalign's CRT streams and the retained
native/CRT lineage. PR5564's exact README is authenticated context in
SOURCES.json. Nick Petalas's PR6273 classifies common Fourier permutations;
it is a separate address contract and is not the source of this question.

Bezout, CRT, projective ring lines and Euler/Jordan totients are classical.
Havlicek and Saniga's [modular projective-line work](https://www.geometrie.tuwien.ac.at/havlicek/pub/generalqudit.pdf)
already describes the underlying primitive points and vector layers.
The contribution here is the explicit collision formula and constructor
for this recovery interface. No broad literature-priority claim is made.
Predecessor files and credit lines are unchanged.

## Verifier constraints

Power-of-ten inspection covers the two new Python files. No recursion,
subprocess, network operation or verifier file write is used. Functions
remain below 60 physical lines. Public counter/witness inputs enforce the
bounds above. Every exhaustive subset domain has at most twelve classes.
Larger domains have at most 144 classes, at most 356 declared subsets per
modulus and at most 4,096 coefficient pairs per kernel. Inputs and package
files are capped at one MiB; source metadata is validated separately by
the registered runner. Explicit exceptions remain active under optimization.

Rule 3 has a managed-runtime deviation in both Python files. CPython
allocates integers and containers during execution; the enforced finite
bounds constrain live data and loop work. Each kernel mask has at most
4,096 bits and at most 144 masks are retained for one modulus. No fixed
allocation or native runtime claim is made. A native implementation would
need preallocated arrays before such a claim. Warning-strict normal and
optimized executions are the available diagnostics; no shared build
configuration is changed. The single local import uses the explicit package
path so isolated execution finds the counter without ambient PYTHONPATH.
