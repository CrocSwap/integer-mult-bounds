# Legal GL(2) bases do not lower the G20 boundary below 38 ADDs

**Scoped negative result; no new kappa.** On the pinned PR5840 controller, a
basis change preserves the labeled target diagonal if and only if it is an
independent `GL(2, F2)` action on each of the 16 equal-monomial coordinate
pairs. Every such action still needs at least **38 unit binary ADDs on each
32-wire side**. The published words meet 38, so the scratch-free invoice is
**76 ADDs per port** and this commutant does not improve it.

This answers the open question in
`research/g20-full-boundary-floor` and the GL(2) question in
`research/g20-target-pair-boundaries`. It is not a new multiplication
exponent, a helper-split, or an admission of the ordinary BIT supplier.

## Legal bases

The controller diagonal has 32 monomial identifiers. They agree on each pair
`(2k, 2k+1)` and the 16 pair values are distinct. On a pair with equal
monomial `t`, the diagonal acts as `t I`. Every invertible `F2` block on that
pair therefore satisfies `S^{-1} D S = D`. A column that mixes two different
monomials is not a scalar multiple of one new basis vector, and a
transposition of two unequal wires exchanges their labels. Thus the matrices
that preserve this diagonal are exactly the block-diagonal elements of
`GL(2, F2)^16` on those pairs.

The same identity is the target-pair conjugation: if `L P R = D` and `S`
commutes with `D`, then `(S^{-1} L) P (R S) = D`. The new boundaries are
`S^{-1} L` and `R S`. Both are charged. No physical permutation is free.

## Why the two blocks stay separate

Chain wires are `{0..15, 30, 31}` and exchange wires are `{16..29}`. Every
coordinate pair lies entirely in one side, and both source matrices have no
edge across the cut. Right multiplication mixes only the two columns of a
pair, and left multiplication mixes only its two rows. The cut therefore
survives every commutant element. For a disjoint union,
`n - v + z` is the sum of the two blocks, so a 32-wire bound is the sum of
the 18-wire chain bound and the 14-wire exchange bound.

## The 38-ADD floor

Use the counting bound of Alan Bu, Evan Fan and Robert Joo, *Minimum
Synthesis Cost of CNOT Circuits*, arXiv:2408.07898, Lemma 3.6 and Theorem
5.2, in the form already used for the fixed endpoint. A join of two
interaction components cannot change a diagonal entry. Every other gate
changes at most one diagonal entry. If the endpoint has `z` zero diagonal
entries and its undirected support graph has `v` components, then any
scratch-free unit-ADD word has length at least `n - v + z`. Intermediate
cross-component gates are allowed by this count. It does not allow scratch
or a gate outside the wires being bounded.

Pair contributions commute: each GL(2) block rewrites only its own two rows
or columns. The verifier therefore runs a partition dynamic program. The
state is the reachable undirected support partition together with the fewest
zero diagonal entries that produce it. Branching on all six group elements
at each pair gives the exact minimum of `n - v + z`.

| Block | Wires | Pairs | States reached | Floor on each side |
|---|---:|---:|---:|---:|
| Chain | 18 | 9 | 3 (peak 6) | 20 |
| Exchange | 14 | 7 | 54 | 18 |
| Full side | 32 | 16 | sum of the blocks | **38** |

Both the left action `S^{-1} L` and the right action `R S` meet these floors.
Forty-eight deterministic samples recompute the bound directly and agree with
the split. The exchange half was also checked, outside this replay, by
enumerating all `6^7 = 279,936` matrices on each side; the minimum was 18.
The chain minimum agrees with a separate exhaustive run of all `6^9`
configurations performed while testing the program. The replay itself uses
the dynamic program, not those enumerations.

## Sharpness

Each published side expands to 14 ADDs and eight SWAPs. With the usual
three-ADD SWAP, the word has length 38. Replaying it reproduces the stored
matrix, the two sides are inverses, and the counting bound of each matrix is
38. The identity element of the commutant is therefore optimal, and no other
element is better. This does not list every element that also attains 38.
The earlier 65,536-orientation census already found 16 attaining swap
patterns; any further attaining GL(2) elements still cost 38.

## Limits

Not covered: scratch, a gate that touches a wire outside this 32-wire
boundary, a nonlinear gate, a non-unit or non-binary tariff, a basis that
changes the labeled diagonal, a changed controller, and every native,
owned-erasure, compiler, precision, stock, and analytic obligation. The
recursive paid profile is unchanged. Selected conditional kappa and its five
framework assumptions are unchanged. No predecessor circuit search or
selected-frontier replay was run.

## Reproduce

Python 3.12 and the standard library are enough. From the repository root:

```sh
python3 -I -W error -B research/g20-gl2-commutant-floor/verify.py
python3 -B scripts/research_package.py --package research/g20-gl2-commutant-floor
```

Expected token:

```text
PASS_G20_GL2_COMMUTANT_FLOOR legal=GL2^16 chain=20 exchange=18 side=38 witness=38 states=3+54/3+54 peak=(6, 54)/(6, 54) samples=48 no_new_kappa
```

The only live input is
`research/g20-isolated-exchange-floor/inputs/CONTROLLER.json`, pinned in
[SOURCES.json](SOURCES.json). Catalogue and selected-record pins are
provenance for this base commit.

## Open next questions

Can one priced scratch wire, or one gate that leaves these 32 wires, lower
either legal commutant side below 38 unit ADDs? That matters because every
gate in this proof stays inside the 32 wires. The first step is to fix the
scratch tariff and test the four-wire endpoint corner before a larger
search. An unpriced scratch wire is not a saving, and no such tariff is
chosen here.

## Credit

Ali Romman supplied PR5840, the equal-target conjugation, and the controller
retained by Charan .'s PR5851. JoyboyBrian's fixed-endpoint 38-ADD theorem
posed the legal-GL(2) question answered here. Nick Petalas proved the
18-wire chain component, and the twelve-wire exchange floor is the adjacent
block. Alan Bu, Evan Fan and Robert Joo own the general counting bound; this
package applies it to the commutant and does not claim a new CNOT theorem.
The target-pair lineage retains PR5834, PR5807/5828, PR5708/5671,
ai-nanachi PR5512, Dugongue and ToikY.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human or proof-assistant acceptance is claimed.
