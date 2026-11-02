# Rank-sensitive mirror capacity admits a previously excluded profile

This contribution is produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

Claim type: scoped written mathematical proof with exact finite corroboration.
Keeping each inner source's paid rank, with a freely chosen ambient scale,
gives a strictly weaker sufficient
complement-capacity test for the conditional capped-flow compiler. The new
lemma includes leaf funding and a critical-root shifted-logarithmic corollary.
No native supplier or new kappa is claimed.

## Result

For target/paid ranks `k>r`, the exact source window has rank
`s=rkz>r floor(n/m)`. With `Lambda>m` and
`n<=Lambda floor(n/m)`, charge that source by

```text
eta_r(t) s^t,          eta_r(t)=t(r/Lambda)^(1-t).
```

The actual nonlinear complement capacity dominates this charge. Retain the
per-paid-rank mirror coefficients `S_(J,r)`, and replace the uniform mirror
comparison by

```text
E_J(t) <= b sum_r eta_r(t) S_(J,r)(t),     b<1.
```

If the occupation surplus and leaves also satisfy
`(1-b)eta_1 A_t >= (1-eta_1)F_t`, every exit is funded. A moment crossing,
an explicit positive tilted-mean gap, and this strict weighted mirror
condition imply the same conditional critical-exponent polylogarithmic
leaf bound as the predecessor. [PROOF.md](PROOF.md) gives the hypotheses
and argument, including integer floors and zero-leaf cases.

The abstract integer histograms

```text
targets: W_16=1, W_64=2
paid:    P_1=2, P_4=6, P_36=1
theta=1/2, Lambda=289/4
```

have equal moments of 20 and positive tilted-mean gap. The only exit cell
has coefficients `E=24`, `S_1=32`, `S_4=192`. The old uniform mirror
test fails because `3/28>1/16`. The new weighted ratio is `51/52<1`.
The floor guard holds for every `n>=512`. Exact tail factors `279/400`
and `18/25` give a separate positive control. This exhibits a strict
extension of a sufficient test, not a native saving of one half.

## Reproduce

From the repository root, using CPython 3.12 and only its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/rank-sensitive-mirror/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/rank-sensitive-mirror/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/rank-sensitive-mirror
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/rank-sensitive-mirror --check-source-history
```

Replace the interpreter path with another CPython 3.12 installation as needed.
The direct verifier is read-only and Git-free. Its generated stdout receipt
binds all six package files by SHA256. Expected scientific marker:
`PASS_RANK_SENSITIVE_MIRROR`.

The finite replay covers all mirror cells of this new toy, 49 capped-flow
fixtures at heights 1 through 7 and ranks `24^2,25^2,32^2,33^2,48^2,64^2,65^2`,
369 source-term checks across those fixtures, and 1,220 funding cases.
Two enumeration methods agree on the toy base measures. All nonlinear
square-root capacity comparisons are exact squared rational comparisons.
The nine semantic controls include a changed paid-rank distribution,
the strict-mirror equality boundary, the two sides of the cutoff guard,
four malformed profiles, and an uncovered source window. A separate
underfunding control retains the leaf charge. These finite checks corroborate
the written proof. They do not prove its universal conclusion by enumeration.

## Scope and credit

The question comes from Dillon Amburgey's
[PR4532](https://github.com/CrocSwap/integer-mult-bounds/pull/4532), Open next
question 1. The new step retains source rank inside complement capacity;
the full distribution-dependent measure question remains open. Cite zxv's
[PR4436](https://github.com/CrocSwap/integer-mult-bounds/pull/4436) and
[PR4483](https://github.com/CrocSwap/integer-mult-bounds/pull/4483) for the capped
flow and occupation estimates, Ryanson Jonathan's corrected
[PR4459](https://github.com/CrocSwap/integer-mult-bounds/pull/4459) for the mirror
identity, and Jacob Alan Sussman for the integer compiler. Dillon's
critical-root tail construction and shifted-logarithmic argument are cited
premises. Their retained native, geometry, helper, Cinna Davis and outer
contributors keep their credit. Concavity and weighted summation are classical.
No predecessor code, examples, counts or credit lines are modified or audited.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19358858)
specifies the scope. Canonical base is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
[TASK.json](TASK.json) declares the change from selected-assumption work to a
compiler side lemma; [SOURCES.json](SOURCES.json) pins historical provenance.
The verifier has no live predecessor input or executable dependency.

The histograms are abstract. No native realizing word, chronological batch
width, physical caller, restoration, precision/tape/stock budget, supplier
admission or analytic recovery is supplied. The five selected framework
assumptions remain. The selected cold replay, native suites, Lean and Docker
are unrun. The corollary is conditional on the cited compiler/recurrence
contracts. It supplies no explicit useful base cutoff or physical cost bound.

## Verifier bounds

The verifier has no recursion, subprocess, network, external input, or
mutable global state. Functions stay below 60 physical lines. Every scientific
check uses an explicit exception and remains enabled under optimization.
The fixed workload has seven heights, seven ranks and six source-pair types.
The literal base enumerator has at most
`sum_(d=0)^6 3^d 2^(6-d)=2059` words at the largest height.
The receipt reads six regular files capped at 256 KiB each.

Power-of-ten rule 3 has a managed-runtime deviation in `verify.py`: Python
allocates integers, fractions and collections during checking. The fixed
height/alphabet bounds limit live state; only one capped fixture is live at
a time. The largest product-law support has at most `3^7=2187` entries,
and the literal enumeration streams its words. Normal/optimized replay and
an AST/function-size inspection check this bounded design. Fixed storage
would require replacing Python's arithmetic/runtime, beyond this isolated
proof package. Reassess the bound before exposing configurable workloads.
Warning-strict execution is the available diagnostic; no separate Python
type checker or whole-repository static analysis is claimed.

## Open next questions

1. Can an actual native profile pass this test while failing the old one,
   with a complete paid/target and physical bill? Start with its exact
   per-paid-rank source cells and mean gap. A native realization and full
   implementation budget are missing here.
2. Can the actual capped base measure weaken the new pointwise test further?
   Start with a failing weighted cell and prove a uniform mass bound.
   Finite sampled caps are insufficient. This is the remaining part of
   PR4532's broader question. Structured questions are in TASK.json.
