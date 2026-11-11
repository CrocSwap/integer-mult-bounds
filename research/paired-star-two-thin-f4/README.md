# Two thin maps over F₄ on the three-leaf paired star

## Scope

Same full-call contract as PR #5747 at g=3, d=2: twelve F₂ orthogonal resolutions, six full calls, and 720 list orders. Exactly two thin maps, inserted in two of the seven gaps. Thin entries are taken in the concrete field

F₄ = F₂[a]/(a²+a+1),

with elements 0, 1, a=2, a+1=3 and the addition that matches XOR of those labels. The endpoint equations are F₂-linear, so each solution space over F₄ is the scalar extension of an F₂-affine space. The witness condition is the polynomial identity in F₂[e, D₀, D₁, D₂]/(e²), with each Dᵢ of degree at most 2.

This is a partial finite census. It is a scoped obstruction search on the two-map contract. The selected frontier stays κ = 781451/250000000.

## Result

Over this field and this contract:

- 1,244,160 words are screened. 159,984 have a pure product equal to the target. The polynomial product, its GF(256) evaluation, and an independent scalar product at (2, 3, 5) agree, with no degree overflow.
- The 21 gap pairs produce 566,352 consistent systems and 2,793,312 inconsistent systems. The consistent systems form 1,746 affine classes. Nullities run from 7 to 32.
- On every consistent system the two solution matrices differ by one fixed rank-4 matrix D, the paired star of identities between the core and the three leaves. Each free direction is added to both matrices. D is the XOR of the two commuting control maps, which have ranks 4 and 4, and D³ = D.
- The commuting control is an exact polynomial identity. Its F₄ rank-sum minimum is exactly 8.
- For 1,562 classes, exhaustive dynamic programming proves that every F₄ point has rank(Zg) + rank(Zh) at least 8.
- For 184 classes the search stores 2²⁰ partial row spaces while the rank sum is still below 8 and stops. Those classes are unresolved. No class returned a completed F₄ point of rank sum 6 or 7. An unfinished branch can still hide one.
- A search over F₄ leaves every larger characteristic-2 field open. Finishing these 1,746 classes would still leave F₈ and the algebraic closure undecided.

## Reproduction

From the repository root, with Python 3.12, gcc, and OpenMP:

```sh
python3 -B research/paired-star-two-thin-f4/verify.py
```

The command checks D and the control maps, compiles `search.c`, and replays `control`, `audit 11`, and `census 0 11`. The census takes about 90 seconds on four threads. It prints `proved_f4_classes=1562 unresolved_f4_classes=184` and `PASS_PAIRED_STAR_TWO_THIN_F4`.

## Open next questions

The structured questions are in `TASK.json`.

The useful next step on this same contract is to finish the 184 capped classes. The largest have nullity 32, and a frontier of 2²⁰ fills after two components of four F₄ variables. A Schur-complement argument for that block shape is the smallest algebraic step. It has to be checked against the classes whose free support is different before it can close the census.

The other step is one extension larger than F₄. Even a completed F₄ census would not decide F₈.

Three thin maps, and a stage that uses three or more full calls, are different contracts. They are already carried by fork draft #183 and by upstream PR #6956.

## Credit

The contract and the rank floor are PR #5747. The F₂ two-map census that left entries outside F₂ open is the package on `cursor/paired-star-two-thin-rank-b55f` (fork draft #157, upstream PR #6940).

Prepared by unpaidmoon with substantial Cursor Grok assistance. Independent human review and a proof-assistant proof are unclaimed.
