# Independent recount of #4598's five-request threshold headers

**Task:** independent-moment (independent recount). **Base:** canonical main `f626db5c`. **No κ is claimed.**

petalas's #4598 (head `c80f445e`) claims a count for k = 5 pairwise orthogonal rank-one requests on F₂⁶. Of all complete headers G ∈ GL₆(F₂), exactly **2,880** pass every guard; a guard asks that the leading principal minors of orders 1–5 of G P_t G⁻¹ be nonzero. The density is 1/6,999,552. This refutes the 2·k! = 240 pattern suggested at k = 3 and 4.

This package recounts the headers **without #4598's method**. It uses no J − I decomposition, no rank or idempotence argument and no rectangle-subset search. It also imports nothing from #4598.

## Method

1. **Guard condition.** G P_t G⁻¹ = I − g_t h_tᵀ, where g_t is column t of G and h_t is row t of G⁻¹. So the order-j minor is 1 − Σ_{i≤j} h_t[i] g_t[i].
2. **Headers as pairs.** Let X be the first k columns of G and Y the first k rows of G⁻¹. Headers correspond one-to-one with pairs (X, Y) satisfying YX = Σᵢ yᵢxᵢᵀ = I_k, because the last column of G is the unique nonzero vector of ker Y.
3. **Ordered convolution.** The count is therefore an ordered convolution of m = k+1 increments yᵢxᵢᵀ:
   - the first k increments must have a zero diagonal;
   - the total must be I_k;
   - each increment is weighted by how many pairs (y, x) produce it, so the zero matrix has weight 2·2^k − 1.

   Zero and repeated increments are therefore counted, not excluded by argument. The convolution is evaluated exactly by meet-in-the-middle with Python integers.
4. **Failure control.** Drop the order-3 guard at k = 3 (m = 4). The convolution and the brute force over GL₄ then agree on a different count, 252. Both routes respond to the guard semantics in the same way.
5. **Cross-check.** Steps 1–3 are checked against the leading-minor definition by brute force over all of GL₃(F₂) (k = 2) and GL₄(F₂) (k = 3). The GL₄ check uses both the coordinate requests and a non-coordinate orthogonal family.

## Result

| k | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| passing headers (convolution) | 2 | 12 | 48 | **2,880** |
| brute force from the definition | 2 | 12 (both families) | — | — |

- **Agreement.** Every value agrees with #4598, and with its k = 3, 4 controls (#4275, #4345).
- **Density.** |GL₆(F₂)| = 20,158,709,760 and 2,880 divides it, so the density is 1/6,999,552.
- **The 2·k! pattern fails at k = 5:** 2,880 ≠ 240.
- **Zero increments.** Setting the zero increment's weight to 0 leaves every count unchanged for k = 2 through 5. So no passing sequence contains a zero increment, which independently confirms the corresponding step of #4598's argument.
- **Independence.** The k = 5 total therefore follows from the minor condition through a different route. It does not depend on #4598's bijection or on its claim that every decomposition uses five distinct nonzero rectangles. Its zero-increment step is confirmed separately, as noted above.

## Verify

```text
python3 -B research/pr4598-header-recount/verify.py
```

The script takes about 9 s and uses the standard library only.

## Limitations

- **Scope.** Only #4598's stated header problem is checked: k ≤ 5, m = k+1, F₂, orthogonal kernels and complete equally weighted headers.
- **Not re-checked.** #4598's listing of the 24 subsets and its hand counterexample.
- **Brute force.** Coverage stops at GL₄. For k = 4 and 5 the result rests on the exact convolution together with the bijection derived above.

## Open next questions

- The same convolution gives the k = 6 (m = 7) count. Its meet-in-the-middle tables grow to roughly 3⁹ × 2^36 sums, so it needs a Walsh–Hadamard version with modular arithmetic. First step: port the convolution to a mod-p fast Walsh–Hadamard transform over 2^36 cells, or exploit the symmetric group action on coordinates to shrink the space.

Credit: petalas (Nick Petalas) for #4598 and the #4275 threshold framing; Cinna Davis for the BIT request context. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
