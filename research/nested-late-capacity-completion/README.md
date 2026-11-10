# Exact shared maps for nested late capacities

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration. This
settles the nested-target case of Brian / JoyboyBrian's
[PR5020](https://github.com/CrocSwap/integer-mult-bounds/pull/5020),
Open next question 2. It gives an exact feasibility criterion, construction
and finite-field count for one prescribed injective map extended to an
isomorphism meeting any finite list of nested late capacities. Sources
may overlap arbitrarily and need not be nested. No new kappa is claimed.

## Result and first discriminating example

For h:U -> W injective, dim V=dim W=n, arbitrary sources A_i and nested
capacities C_1 <= ... <= C_k, put

```
S_i = sum_(j<=i) A_j,    U' = h(U),    u = dim U,
e_i = dim(U+S_i)-u,      c_i = dim C_i, b_i = dim(C_i intersect U').

An invertible g extending h with g(A_i)<=C_i exists exactly when
h(U intersect S_i)<=C_i and e_i<=c_i-b_i for every i.
```

[PROOF.md](PROOF.md) proves this over every field and counts every
completion over F_q. Its exact count is

```
product_i q^(b_i*(e_i-e_(i-1)))
          product_(e_(i-1)<=j<e_i) (q^(c_i-b_i)-q^j)
  * product_(u+e_k<=j<n) (q^n-q^j),   e_0=0.
```

The count is zero when a condition fails. Empty products equal one.
With no late constraints take e_k=0.

Separate one-capacity tests miss relations between sources. In F_2^3,
fix h(x+y)=z, request x -> <x> and y -> <x,y>. Each request alone
admits a completion, with counts 4 and 12. Their shared contract admits
zero because h(U intersect (A_1+A_2)) lies outside the final capacity.
A second fixture has U=0 and two independent source lines directed into
one common target line; it fails the cumulative quotient condition.

The new step is the simultaneous cumulative-source theorem and its count.
PR5020's one-capacity result, source-specific adapter and numbers are cited
context and are not replayed. The investigation stops at this scoped result.

## Exact evidence

The independent census constructs subspaces as literal finite vector sets,
enumerates invertible matrices by their complete vector permutations, and
groups every possible prescribed partial injection by its literal action.
For every source pair and nested target pair it compares the formula with
the exact number of satisfying GL matrices. It uses no reference row reducer.

| Field and dimension | Partial injections | Source/target/map cases |
| --- | ---: | ---: |
| F_2^0 | 1 | 1 |
| F_2^1 | 2 | 24 |
| F_2^2 | 16 | 4,800 |
| F_3^2 | 81 | 43,740 |
| F_5^2 | 625 | 840,000 |
| F_2^3 | 512 | 8,650,752 |

All 9,539,317 cases agree. Separately, 14,141 calls compare the bounded
row-reduction reference count with literal census values; 3,119 constructor
calls check existence, and every returned matrix is checked on complete
vector permutations and literal source/target membership. The constructor
also handles 112 attaining fixtures through dimension six, including empty,
repeated and eight-stage target flags. Fourteen malformed boundary cases
reject in both entry points. Checks use explicit exceptions under normal
and optimized Python.

Every run generates a JSON receipt with all six domain digests, counts,
controls and SHA256 hashes of all seven package files. The verifier writes
nothing; redirect stdout outside the checkout to retain the receipt.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/nested-late-capacity-completion/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/nested-late-capacity-completion/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/nested-late-capacity-completion
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/nested-late-capacity-completion --check-source-history
```

Any CPython 3.12 executable may replace the absolute path. Expected direct
marker: `PASS_NESTED_LATE_CAPACITY_COMPLETION`. Both registered commands
have 120-second limits. The direct verifier is self-contained in a Git-free
copy of these seven files. The source README, selected record and task card
are pinned historical provenance, not executable dependencies.

## Scope, costs and credit

The all-field conclusion rests on the written proof. The exhaustive
execution covers only the six stated prime-field domains. The reference
API accepts q in {2,3,5,7}, 0<=n<=6 and at most eight contacts; these are
software limits, not theorem hypotheses. It requires basis tuples and
rejects a noninjective prescribed map or nonnested targets.

This is unrestricted linear-algebra completion. No actual selected-word
contact is changed. Symplectic/native realization, absolute phases, source
access, causal scheduling, arbitrary dirty restoration, basis preparation,
delivery, productive target debits and the complete paid invoice remain
open. Precision, stock, tape, compiler, outer admission and all five
selected assumptions remain. No native build, selected scientific replay,
Lean or Docker run was needed or performed. Independent human and formal
proof-kernel review are unclaimed. The selected frontier is unchanged.

Credit Brian / JoyboyBrian for PR5020 and the explicit second-capacity
question; Cao Yifan / intqwq for PR4610's native-map caller; Nick Petalas
for PR4919's different three-subspace correspondence theorem; codyw912
for PR4735; and Cinna Davis, Dugongue, zxv, Jacob Alan Sussman and the
retained native/compiler lineage. Basis extension and finite-field
independent-vector counts are classical. No general literature-priority
claim is made. Predecessor text and code are not copied or modified.

The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19363406)
records the scope. Canonical base is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8, selected
PR6030. [TASK.json](TASK.json) records the explicit change from the
coverage-law card to this shared-map feasibility side result. The selected
orientation passed its metadata-only positive control. Live open/account
PRs, recent claims, main README and merged/general-form searches were
checked. Sparse historical notes, arbitrary diffs and unpublished work
remain overlap-coverage limits.

## Open next questions

1. Extend the prescribed-map theorem to two nonnested target capacities.
   Start with two intersecting binary planes and an oblique prescribed
   subspace. Their coupled image choices are not decided by this flag proof.
2. Bind a nested-capacity instance to an actual shared native operator.
   Export every same-operator source/image condition and determine whether
   its capacities form a flag. Phase/native realization and a complete
   signed invoice block any claimed helper or kappa gain.

The structured questions in [TASK.json](TASK.json) give first steps and
blockers. No continuation or physical construction is reserved here.

## Verifier bounds

No function exceeds 60 physical lines and no call path recurses. The literal
census has at most 25 vectors, 16 subspaces, 480 GL matrices and 66 target
flags in a domain; it enumerates at most 625 candidate matrices. It retains
counts as a digest rather than storing the millions of case records. The
reference has at most six coordinates, twelve-column elimination matrices
and eight contacts. Each package file is limited to 128 KiB when hashed.
Warning-strict normal/optimized execution and in-memory syntax compilation
supply diagnostics. Input failures propagate as explicit errors.

Python exact integers, dataclasses, iterators and bounded collections allocate
during execution. These are documented managed-runtime deviations from
Power of Ten static allocation and indirect-call restrictions, not a
constant-space physical implementation. There are no network, subprocess,
write or persistent shared-state paths in the scientific verifier.
