# Dirty-independent endpoint error for the PR628 rounded leaves

The actual PR628 classical fixed-grid prototype has a uniform endpoint error
bound independent of the initial borrowed arrays. This does **not** make the
implemented increment independent of dirt, or bound integer storage independently
of dirt. The essential distinction is to retain rounded coefficient powers in
each leaf's linear shadow. Replacing them with ideal powers breaks the uniform
additive-defect premise, as the large-input control demonstrates.

## Statement

Use the maximum complex Euclidean norm over array entries. There are `n >= 1`
ordered factors and arrays of any common positive length. At each leaf,
`0 < beta <= 1`, recurrence coefficients have norm at most `1-beta`, and
final multipliers have norm at most `R >= 1`. Let `u = 2^-p <= beta^2/2`.
All data arrays lie on the u-grid; all mutable arrays are distinct. Factor and
phase parameters are immutable, do not alias mutable data, and are reused
unchanged by inverse/repeated subwords. Arithmetic has unbounded exact integers.

For the balanced `dirty.compose` dispatcher, or any ordered full binary tree
using its four-subword commutator, let `G(x,t)` be the net target increment;
`t` lists arbitrary initial borrowed arrays. Linear leaf shadows `S_i` satisfy,
with `L = 4R/beta^2`,

```
||S_i|| <= L,
||G(x,t) - S_n ... S_1 x|| <= n L^(n-1) (8R u/beta^2).
```

For comparison with PR628's exact inverse oracle, also require `b != 0` for
each outside factor (the oracle forms `rho=1/b`). The frozen-shadow statement
alone allows zero. If `A_i` denotes the exact unrounded cyclic inverse leaf
and `||x|| <= B`, then

```
||G(x,t) - A_n ... A_1 x||
 <= n L^(n-1) [8R u/beta^2 + 4R B u/beta^4]
 <= 12R n L^(n-1) (B+1) u/beta^4.
```

Source and borrowed arrays are restored exactly. Initial target dirt also
drops out of the net increment. No commutativity is used. The theorem permits
different stable coefficients/multipliers per leaf. The source replay binds
PR628's inside/outside grammar with unit phases and `abs(scale) <= R`.

For endpoint accuracy `2^-q`, a sufficient integer data precision preserves
the incoming grid, satisfies closure, and obeys

```
p >= q + ceil(log2(12R n L^(n-1) (B+1)/beta^4)).
```

For fixed margin and multiplier bound this budget is linear in factor count.
Coefficient preparation error and its precision requirements remain separate.

## Proof

Index sites in traversal order. Exact open prefixes obey
`h_j=x_j+a_j h_(j-1)`, starting with the first input. Thus the prefix map
has norm at most `1/beta`. Componentwise half-up rounding has complex norm
error at most `u`. Implemented open prefixes differ by at most `u/beta`,
uniformly in input magnitude.

Let `p_j` be the implemented rounded coefficient powers, starting at one, and
`p_j^0` exact powers. Stability gives `|p_j-p_j^0| <= u/beta`, hence
`|p_j| <= 1+u/beta <= 3/2`. Write `d=1-p_last`, `d0=1-p_last^0`.
Since the cycle has positive length, `|d0| >= beta`, and
`|d| >= beta-u/beta >= beta/2`.

Define the linear shadow using exact data prefixes but **rounded powers**:

```
(S x)_destination(j) = multiplier_j * (h_j + p_j h_last/d).
```

The destination is the actual leaf permutation. Consequently
`||S|| <= R[1/beta+3/beta^2] <= 4R/beta^2`.
The implemented rounded seed differs from `h_last/d` by at most
`2u/beta^2+u`. The pre-multiplier output error is at most

```
u/beta + (3/2)(2u/beta^2+u) + u <= (13/2)u/beta^2.
```

After the last multiply/round it is at most
`(13/2)R u/beta^2+u <= 8R u/beta^2 = E0`.
This global additive bound holds for every grid source because every rounded
coefficient is frozen in S.

The exact leaf uses exact powers and denominator. Direct subtraction gives

```
|p_j/d-p_j^0/d0|
 <= |p_j-p_j^0|/|d| + |p_j^0||d-d0|/(|d||d0|)
 <= 2u/beta^2+2u/beta^3 <= 4u/beta^3.
```

Therefore `||S-A|| <= 4R u/beta^4 = Delta`.
The exact Neumann inverse bound is `||A|| <= R/beta <= L`.

The existing PR628/PR663 nonlinear commutator identity gives, for an earlier
block B and later block A and fixed deeper dirty rows t,

```
G_node(x,z,t) = G_A(z+G_B(x,t),t)-G_A(z,t).
```

Each subword restores its source and deeper borrowed rows and adds an increment
independent of its incoming target. This is true at leaves and inherited by
the four-subword composition; the negative call reverses the signed instruction
word exactly. Suppose subword shadows are S_A,S_B with uniform defects E_A,E_B.
Subtract S_A S_B x in the identity: the linear S_A z terms cancel, yielding

```
E_node <= ||S_A|| E_B + 2 E_A.
```

For a,b >= 1 leaves in the later and earlier blocks, induction yields

```
E_node <= L^a b L^(b-1) E0 + 2a L^(a-1) E0
        <= (a+b)L^(a+b-1)E0,
```

since L^b >= 2. This proves the bound for **every ordered binary tree**; it
does not mistake the repeatedly executed nonlinear leaves for independent
linear factors. Finally, telescoping the ordered shadow/ideal products gives
operator difference at most `n L^(n-1) Delta`, proving the endpoint claim.

## Reproduction

Run `python3.12 -I -O -B research/dirty-endpoint-defect/verify.py`, or
`python3.12 -B scripts/research_package.py --package research/dirty-endpoint-defect`.
The verifier authenticates source pins and loads fresh copies of the five
unchanged PR628 Python files. Its independent Fraction shadow is compared
with actual leaves and complete words, including both directions, non-dyadic
coefficients, rational unit phases and huge data. Complete words check source
and scratch restoration and exact negative-word cancellation.

`receipt.json` records finite evidence, not a universal theorem. The proof
above establishes the universal estimate. `--out PATH` exclusively creates
a regenerated receipt; default verification is read-only. Controls show that
the ideal map is not a uniform leaf shadow, the factor two is necessary,
unbounded nonlinear defect can amplify dirt, rounded increments can vary with
dirt, and a corrupted endpoint fails. The exact-oracle adapter rejects an
outside zero coefficient. Source and receipt mutations fail closed.

## Provenance, novelty and limits

Chafik Boukhalfa (`chafreaky`) supplied PR628, head
`0768f97d06c623b8211e651543c66135796b62bf`. Unchanged vendored sources and
prior notes are pinned by SHA-256 and Git blob in SOURCES.json. The nonlinear
identity/restoration is prior work, including 0xkilgore's PR663 and the
`lean-nonlinear-commutator` formalization. The `dirty-fanout-batch` note
already distinguishes restoration from dirt-independent output and gives a
generic error recurrence assuming uniform leaf errors. Here the new step
establishes that premise for actual PR628 leaves by retaining rounded powers,
then uses tree-level cancellation for this endpoint bound.
`dirty-cubic-precision` remains the broader preparation/word-size reference.

This is a classical rational-prototype result, not a bit-reversible compiler,
overflow guarantee, coefficient-preparation theorem, common-label Clifford
word, supplier, or selected-frontier change. Large dirt still requires large
integer storage and arithmetic time. Fixed parameters and phase nonaliasing
are hypotheses, including the known phase-alias gap in the entry guards.
Prepared by ywz65 with Codex assistance.

## Open next questions

* Can this bound be integrated with the retained coefficient-preparation
  contract without losing the data-rounding saving? First separate parameter
  error from frozen-power shadow error; preparation may still dominate.
* Can a finite-width compiler retain this uniform defect with an explicit
  overflow envelope? Start with one leaf and exact inverse updates. Arbitrary
  integer dirt requires a magnitude hypothesis for any fixed-width guarantee.
