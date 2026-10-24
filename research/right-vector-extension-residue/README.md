# Exact rank-one lift counts over a residue-field extension

This package was produced by Nick Petalas. It answers Open next question 1
of [#4770](https://github.com/CrocSwap/integer-mult-bounds/pull/4770) with a
**scoped counting proof and exact finite corroboration**. No new kappa is claimed.

Let K=F_q be a subfield of L=F_Q. Let R be a finite-dimensional central local
L-algebra with canonical residue R/J=L, and put z=|J|. Paid factors are
I+u v^T with u in R^2 and v in K^2; arbitrary GL_2(K) maps are free anywhere.
Fix a rank-one residue A in M_2(L). Among the q+1 lines in K^2, let t(A)
count those whose nonzero vectors A sends into K^2 minus {0}. Then

```text
t(A) belongs to {0,1,q}.

For the z^4 lifts of A:
    cost 1 = 0                         if t(A)=0;
             1+t(A)*(z^2-1)             otherwise.
    cost 2 = z^4-cost_1.
```

The numbers of rank-one residues in these three classes are exactly

```text
N_q = (q+1)*(q^2-1)
N_1 = (q+1)*(q^2-1)*(Q-q)
N_0 = (Q+1)*(Q^2-1)-N_q-N_1
```

Thus the total number of one-factor lifts is
`(q+1)*(q^2-1)*(Q*z^2-q+1)`. The remaining rank-one-residue lifts cost two.
Neither radical multiplication nor its nilpotency index enters this formula.
The [proof](PROOF.md) classifies the eligible lines, counts their kernel
fibers, and double-counts eligible residue/line pairs. The one-factor criterion
and unit-pivot two-factor bound are credited inputs from #4276, specialized
in #4770; this package does not audit or rerun their verifiers.

The first example is R=F4[e]/e^2 over K=F2. Its 75 rank-one residues split
into 9,18,48 residues with t=2,1,0 respectively. Their 19,200 lifts have
exact costs one and two in counts **567** and **18,633**. Allowing F4-valued
right vectors and free maps instead gives 4,575 one-factor lifts by #4770's
formula. The field allowed in the alphabet changes a concrete cost count.

## Finite evidence

The standard-library verifier constructs the literal one-factor image
`{(I+u v^T)G}` from every left vector, projective base-field right vector and
free endpoint G. It does not use the eligible-line criterion to construct
this image. It then enumerates every rank-one residue and every lift, comparing
literal membership counts separately at each residue with the new formulas.
The resulting cost-two counts use the cited unit-pivot theorem.

The eight fixed fixtures use R=L[e]/e^k, including k=1, when J=0. Their
exact cost-one/cost-two counts are:

- F4 over F2, k=1: 27 / 48.
- F4 over F2, k=2: 567 / 18,633.
- F4 over F2, k=3: 9,207 / 4,905,993.
- F8 over F2, k=1: 63 / 504.
- F8 over F2, k=2: 4,599 / 2,317,833.
- F9 over F3, k=1: 224 / 576.
- F9 over F3, k=2: 23,264 / 5,225,536.
- F16 over F4, k=1: 975 / 3,360.

All **12,511,409** lifts are enumerated across these fixtures. The residue
classification is also checked separately for every residue. Fields are
polynomial quotients, and F4 inside F16 is identified by a^4=a. Nine controls
cover the three line classes, the empty-union exception, a scalar kernel with
zero image, a missing radical-kernel condition, the first example, changing
the base field, and changing the extension degree.

Every run emits a generated SHA256 receipt for all six package files. It
writes only to stdout and does not rely on Git, network access, external
packages, cached data or predecessor executable code. All checks use explicit
exceptions and remain enabled with optimized Python.

## Reproduction

Run from the repository root with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/right-vector-extension-residue/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/right-vector-extension-residue/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/right-vector-extension-residue
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/right-vector-extension-residue --check-source-history
```

Any CPython 3.12 interpreter may replace the local absolute path. Both verifier
commands are registered with a 120-second timeout. The expected final marker
is `PASS_RIGHT_VECTOR_EXTENSION_RESIDUE`. SOURCES.json pins the mathematical
predecessors as historical provenance at canonical main
`624de9dc66858af0945e5f8a0942488d62280d43`. There are no live external inputs.

The current source-binding orientation control passed
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. This is orientation only, not a selected
operator replay.
The formal-interface-lemma card is explicitly changed to this algebraic side
question rather than a proof-assistant or selected-caller obligation. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19131534)
identifies the exact question and credited sources.

## Limits and implementation decisions

The written proof quantifies over every finite-field extension and every
finite-dimensional central local L-algebra with canonical residue L. The
software checks only the fixed commutative fixtures. Nonsplit residue maps,
noncentral coefficient fields, other residue ranks and more than two roles
are outside the result. Native coefficient preparation, free-map realization,
routing, restoration, precision, stock and a complete supplier bill are unknown.
No supplier admission, complete multiplication theorem or selected-frontier
change is supplied. Independent human and formal proof-kernel review are
unclaimed. No Lean, Docker or selected-construction replay was run.

The verifier has no recursion, subprocess, solver or variable-size command-line
input. Field size is at most 16, ring size at most 81, nilpotency length at
most three, and base-field size at most four. Arithmetic tables have at most
81^2 entries. A literal image loop has at most
`180*5*81^2` iterations, conservatively combining the separate enforced bounds.
A residue loop has at most 16^4 candidates and a noise loop at most 16^4
candidates per residue. Only one case and one current target are live at a time.
Each function has fewer than 60 physical lines. Warning-strict ordinary and
optimized runs provide the diagnostics available without additional packages.

Power of Ten rule 3 has a managed-runtime deviation. Python allocates tuples,
integers, dictionaries and set entries during the finite computation. Live
literal targets are bounded by the paid-image loop above, plus the fixed
arithmetic tables and at most 4,335 residue keys. Each receipt input is capped
at 1 MiB. No persistent resource or steady service is present. A future larger
census needs explicit new memory/runtime bounds; no domain expansion is claimed.

## Open next questions

1. What is the one-factor lift distribution above rank-one residues on more
   than two roles? A one-factor word fixes a base-field hyperplane, so begin
   with three roles and the intersections of eligible hyperplane kernels.
   Pairwise intersections need not be just zero; the present line argument
   does not classify them. This would test whether a comparable residue-only
   count survives at larger role count.
2. Can a native producer and consumer realize this restricted alphabet with
   a favorable complete cost? Specify one source and destination contract,
   including coefficient preparation, free-map costs and dirty restoration.
   These unknown physical costs prevent turning the count into a supplier.

Structured questions, first steps and blockers are in TASK.json.

## Credit

Produced by Nick Petalas. Nick Petalas's #4770 supplies the explicit extension
question and scalar-residue count; #4276 supplies the one-factor and local
unit-pivot criteria; #4243 supplies the free-map normal form. ToikY's #4334
and Nick Petalas's #4601/#4749 develop related shared-chart local/semilocal
interfaces. Wentao Li's #4099 supplies the paid alphabet and column bound,
following #2513. The finite-field and projective-line tools are classical.
The new claim is their extension-residue counting application. Apache-2.0.
