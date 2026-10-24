# Local radicals preserve the three-factor right-vector obstruction

**Scoped proof with exhaustive finite controls. No new kappa.** This takes
Open next question 1 of ToikY's [#4334](https://github.com/CrocSwap/integer-mult-bounds/pull/4334),
which proves the field-product case and leaves local products open.

Let `R=R_1 x ... x R_k` be a finite product of associative local
`K`-algebras. In each component the non-units must form a proper two-sided
ideal `J_i`. Set `J=product J_i`. Use two roles, paid factors
`I+u y^T` with `u in R^2`, `y in K^2`, and common free `GL_2(K)` maps.
For every invertible target `M`, [PROOF.md](PROOF.md) proves

```text
cost_R(M) <= 2  iff  cost_(R/J)(Mbar) <= 2,
cost_R(M) = max(delta_R(M), cost_(R/J)(Mbar)) <= 3,
delta_R(M) = min_{T in GL_2(K)} dim_K ((MT-I)K^2).
```

Local radicals therefore preserve exactly which invertible targets need
three factors. They can increase smaller residue costs. Over `F2[e]/e^2`,
`diag(1+e,1)` and `diag(1+e,1+e)` both reduce to the free identity but
cost one and two respectively.

The proof reduces the predecessor right-ideal criterion to a common unit
pivot, then reduces that pivot modulo each component ideal. It extends
#4334's three-factor word with the ring multiplications in their stated
order. It applies to noncommutative local algebras as well. In particular,
for finite `K=F_q`, the sharp component threshold remains `k=q+1`:
all invertible targets cost at most two for `k<=q`, and every such product
with `k>=q+1` has a cost-three target. For infinite `K`, all invertible
targets in a finite product cost at most two.

## Finite evidence

`verify.py` imports no predecessor code. It enumerates literal words of
cost zero, one and two over `A^k`, where `A=F2[e]/e^2`, for `k=1,2,3`.
All common right-vector pairs and all six common free endpoints are
included. Each local factor coefficient is independent across components.
For an invertible endpoint, filtering to invertible paid factors is sound
because determinants multiply in these commutative finite rings.

For each common pair and endpoint, it computes the local reachable set
and its complete `k`-fold Cartesian power. Their union is the exact
two-factor set, without using the pivot criterion. Separately, it computes
all six literal binary column ranks for delta. The explicit three-factor
formula is checked on all 96 local invertible matrices; its common
right-vector sequence makes the construction valid on every product tuple.

| Components | Invertible targets | Cost 0 | Cost 1 | Cost 2 | Cost 3 |
|---:|---:|---:|---:|---:|---:|
| 1 | 96 | 6 | 54 | 36 | 0 |
| 2 | 9,216 | 6 | 558 | 8,652 | 0 |
| 3 | 884,736 | 6 | 4,590 | 830,988 | 49,152 |

The maximum formula and radical invariance hold on all **894,048** targets.
The three-component residue cost-three count is 12, agreeing with #4334;
each residue target has `16^3=4096` lifts, all of cost three. The printed
receipt also records every residue-cost/lift-cost count and hashes every
complete cost table. It binds the results to the package's file hashes.
There is no handwritten receipt.

Controls detect changing an attaining factor, reversing a product,
allowing separate free charts, dropping an obstruction component, and
equating cost with residue cost while ignoring nilpotent contributions.
Checks remain active under Python optimization.

## Reproduce

From the repository root, with CPython 3.12 and NumPy 2.5.4:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/right-vector-local-products/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/right-vector-local-products/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/right-vector-local-products
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/right-vector-local-products --check-source-history
```

The verifier writes nothing and ends with
`PASS_RIGHT_VECTOR_LOCAL_PRODUCTS targets=894048 cost3=49152 formula=exact`,
followed by its generated digest and `no_new_kappa`. Each registered check
has a 120-second limit. Source commits, blobs and SHA256 pins are in
[SOURCES.json](SOURCES.json). Its catalogue and selected record are historical
provenance. The two predecessor proof files are live pinned inputs.

## Limits and engineering notes

The proof concerns invertible two-role targets in the formal alphabet.
Finite evidence covers the binary dual-number products only; it does not
enumerate noncommutative local algebras. Native preparation, conversion,
routing, precision, restoration and stock costs remain unknown. No supplier
is admitted and no multiplication theorem or frontier changes. Independent
human and formal proof-kernel review are unclaimed. No Lean, Docker or
selected construction replay is needed for this isolated result or claimed.

The verifier uses bounded ranges, no recursion, local immutable matrix
tuples, explicit checks and functions below 60 lines. Python and NumPy
allocate dynamically; live memory is bounded by arrays over at most
`96^3` targets and a fixed number of temporaries. This is the managed-runtime
deviation from static allocation. No shared code changes are included.

The orientation command `scripts/research_baseline.py` fails at this base
with `KeyError: 'bit_lower'` because it expects the earlier certificate
schema. The selected record's source-binding check succeeds after sparse
inputs are materialized. This package does not depend on the baseline helper.

## Open next questions

1. Does the two-factor radical reduction extend to all semilocal algebras?
   Start with a quotient having one `M_2(K)` block. This would separate
   radical lifting from noncommutative matrix-block effects, but the
   present non-unit-ideal argument does not apply to matrix algebras.
2. Which singular targets over local products are reachable, and do the
   reachable ones always cost at most three? Begin with the three-factor
   image over `F2[x,y]/(x,y)^2`. The current unit-pivot and upper-word
   arguments both use invertibility.

## Credit

This contribution was produced by Nick Petalas. ToikY's #4334 supplies the
field-product theorem, the three-factor formula extended here, and the
sharp scalar examples. Nick Petalas's #4276 supplies the one- and
two-factor criteria, following #4265 and #4243. Wentao Li's #4099 supplies
the alphabet and column bound, building on #2513. The new claims are the
local-product radical reduction, exact lift formula and their stated
consequences. Apache-2.0.
