# F₄ census of two thin maps on the three-leaf paired star

Base commit `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The selected frontier is unchanged: κ = 781451/250000000.

## Contract

Block size d=2 and g=3 leaves, so the matrix size is N=8. A full call is one of the twelve F₂ orthogonal resolutions of a leaf, used as the two halves (I + xⱼ P)(I + e R) in the polynomial ring F₂[e, D₀, D₁, D₂]/(e²). Each stage uses exactly those two halves. A word is an ordered product of the six calls. There are 12³ × 720 = 1,244,160 words. The list order is the left-to-right product, so the first listed call is the leftmost factor.

The target is the left-to-right product of the three stage factors (I + xⱼ Eⱼ). A pure hit is a word whose degree-zero part equals that target. There are seven gaps in the product of six calls. A two-map word puts a constant factor I + eZ into two distinct gaps. The resulting equations on the two unknown matrices are F₂-linear. `search.c` builds them from the monomials of degree at most 2 in each Dᵢ (27 monomials). The replay records overflow 0, so these products never produced a Dᵢ³ term.

## The field

The admissible field asked for by the entries-outside-F₂ question has to be named. This census uses

F₄ = F₂[a]/(a² + a + 1).

Elements are 0, 1, 2, 3, with a = 2 and a² = a + 1. Multiplication is

```
0 0 0 0
0 1 2 3
0 2 3 1
0 3 1 2
```

and the nonzero inverses are 1, 3, 2. Field addition is XOR of these labels. `verify.py` checks the products and the inverses.

Because the endpoint equations have coefficients in F₂, the solution set over F₄ is the scalar extension of the F₂-affine solution set. A particular solution and the kernel generators are F₂ matrices. An F₄ point assigns one coefficient in F₄ to each generator and adds that coefficient, by the XOR rule above, to every entry that carries the generator. The same generator bits appear on both matrices.

Rank is Gaussian elimination in this field. A matrix defined over F₂ keeps its F₂ rank over F₄. Extra F₄ points of an affine space can have smaller rank than every F₂ point, which is why the extension is a real question. Points with coordinates outside F₄ are not in this search.

## Exhaustive structural facts

The census solves every gap pair on every pure hit.

| count | value |
| --- | ---: |
| words screened | 1,244,160 |
| pure hits | 159,984 |
| consistent gap-pair systems | 566,352 |
| inconsistent gap-pair systems | 2,793,312 |
| affine classes | 1,746 |
| nullity | 7 through 32 |

The pure-hit count matches the GF(256) evaluation of the same polynomial, and that evaluation matches an independent scalar gate product at (2, 3, 5). `affine_samples_ok` substitutes the particular solution and each kernel vector into the monomial system.

On all 566,352 consistent systems, `dep[e] = dep[64+e]` and

Zh = Zg + D

for the single matrix whose rows are `54 a8 01 02 01 02 01 02` in little-endian bits. Its F₂ rank is 4. In 2×2 blocks ordered as core, leaf 1, leaf 2, leaf 3,

```
D = [ 0 I I I ]
    [ I 0 0 0 ]
    [ I 0 0 0 ]
    [ I 0 0 0 ]
```

with I the 2×2 identity. The ones are the pairs (0,2), (0,4), (0,6), (1,3), (1,5), (1,7) and the opposite pairs. `verify.py` checks D³ = D, D² ≠ D, and D² ≠ 0.

The commuting control uses the diagonal resolution. Its two thin maps are the core–leaf identities for leaves 1 and 2, and for leaf 3. Each has rank 4, their XOR is D, and the eight-factor polynomial product equals the target in both the degree-zero part and the coefficient of e. The affine space at those two gaps has nullity 16. The F₄ search on that space returns minimum rank sum 8 after 454,928 nodes, and the control point itself has rank sum 8, so 8 is achieved and is the minimum on that space.

## Rank search, and where it stops

For each new affine class the free variables are grouped by union-find: two generators meet when some row of Zg or Zh depends on both. A component of eight or more variables, a sixteenth component, or a row that meets two components returns −1. The census has `class_bad = 0`, so every class fit the enumerator. Each component has at most seven F₄ variables.

Rows with no free variable are inserted first. If their rank sum is already at least 8, the class is finished. Otherwise components are assigned from the largest. The frontier stores partial row spaces whose rank sum is still below 8, packed in reduced row echelon form. Identical spaces are merged. A branch is dropped when the rows assigned so far already have rank sum at least 8. Later rows cannot lower rank, so a dropped branch cannot contain a point of rank sum 6 or 7.

A finished search returns 8 when every branch was dropped, or the smaller completed rank sum when a full assignment survives. No class returned a completed sum below 8 (`class_low = 0`). 1,562 classes returned 8. That is an exhaustive F₄ proof for those classes.

The frontier holds 2²⁰ partial spaces. On 184 classes it filled while every stored space still had rank sum below 8. The search returns −3 and does not report a minimum. Those 184 classes are an incomplete search. A point of rank sum 6 or 7 can still sit in a branch the frontier did not reach. Raising the node counter does not close them: the stop is the stored frontier.

## What this does not decide

The 184 capped classes remain open over F₄. A completed F₄ census would still leave F₈, F₁₆, and the algebraic closure open, because a larger extension has points that are not F₄-points of the same affine space. A restricted field search can show that some named field has a low-rank word. It cannot prove that no characteristic-2 field has one.

Three or more thin maps, and a stage with three or more full calls, are different words. This census does not speak for them.

## Open next questions

See `README.md`. The first unfinished object is the set of 184 capped classes. The second is any extension strictly larger than F₄.
