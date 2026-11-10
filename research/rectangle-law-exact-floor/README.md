# The exact floor of an odd rectangle of residual ranks, for any stage size and hub count

**Scoped proof over every field of characteristic not 2, with exact finite corroboration.
No new κ, no word, no price, no supplier admission, no frontier change.**

This answers open question 2 of DreamingOfClouds's [PR #6935](https://github.com/CrocSwap/integer-mult-bounds/pull/6935)
(`research/p104-root-cut-laws`): does Theorem S, the residual-rank floor 144 for 18 two-unit
stages, extend to stages of more than two units and to rho > 2 with a floor proportional to rho?
Its Lemma 1 (the rectangle law) gives only min(rho, 2) when rho > 2.

## Result

Take signs s_dc, s_df, s_ec, s_ef = ±1 with product -1, matrices A_d, A_e of size u by h and B_c, B_f of
size h by u over a field of characteristic not 2, and the four cells C_xy = s_xy I_u − A_x B_y.

**Theorem 1.** The least possible value of rank C_dc + rank C_df + rank C_ec + rank C_ef is

    f(u, h) = max(0, 2u − h, 3u − 2h, 4u − 4h).

| u \ h | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| 2 | 4 | 2 | 1 | 0 | 0 | 0 |
| 3 | 8 | 5 | 3 | 2 | 1 | 0 |
| 4 | 12 | 8 | 6 | 4 | 3 | 2 |
| 5 | 16 | 12 | 9 | 7 | 5 | 4 |
| 6 | 20 | 16 | 12 | 10 | 8 | 6 |

At u = h = rho the floor is rho, not min(rho, 2). The proof is two block-rank inequalities
(2u = rank of an invertible sign matrix tensored with I_u, bounded by h plus the residual
ranks, and the same for the h by h products B_y A_x) joined by the identity
rank(s I − AB) = u − h + rank(s I − BA). Attainment is one perturbed block and a rank
factorisation. See [PROOF.md](PROOF.md).

**Corollary 2 (Theorem S for any stage size and hub count).** Under hypothesis (S) of the source
with u-unit stages (invertible u by u factors Xi_d, H_c) and any h hub coordinates, the hub-removed
residual ranks R_dc of the 18-stage grid satisfy

    sum over d ≠ c of R_dc ≥ 72 f(u, h).

At u = h = rho this is 72 rho (144 at rho = 2, the source's Theorem S).

**Proposition 3.** At u = h = rho the total 72 rho is attained, so it is the exact minimum of the
abstract matrix problem. The scalar case rests on a finite search: over x, y in {±1}^18 the least
number of off-diagonal cells with x_d y_c ≠ sgn(d − c) is 72. The same search gives ⌊(L−1)²/4⌋ for
every L from 2 to 18 (computed, no general-L proof). Hence 72 is also the largest number of
cell-disjoint odd rectangles in the L = 18 grid.

## Evidence

`verify.py` (standard library; about 20 s; normal and optimized modes):

* the lower bound is a written proof, not a search; the verifier checks the identity
  rank(s I − AB) = u − h + rank(s I − BA) on 300 random instances over F_3, F_5, F_7, F_11;
* 512 explicit configurations (every 1 ≤ u, h ≤ 8, all eight odd sign patterns) built by the
  proof's construction over Q, each with total rank exactly f(u, h);
* exhaustive minimum over all (A_d, A_e, B_c, B_f), canonical signs, equal to f(u, h) for
  (u, h) in F_3: (1,1), (1,2), (2,1), (1,3), (3,1), (2,2), and with A_d reduced to its normal form
  (1,4), (4,1), (2,3), (3,2); in F_5 and F_7: (1,1), (1,2), (2,1). The eight odd sign patterns agree
  at (1,1), (2,1), (1,2) over F_3. At (3,2) the minimum is 5, above the 4 that either of
  2u − h and 4(u − h) alone would allow;
* controls: over F_2 the floor is 0 at (1,1) and (2,2), and with an even sign product it is 0
  over F_3 at (1,1) and (2,2);
* the 72 rectangles of Lemma 2 of the source (disjoint, off-diagonal, odd product, 288 cells),
  and the scalar grid minima for L = 2 to 18;
* the block-diagonal configuration attains 72 rho exactly for rho = 1 to 4;
* the five quoted source statements occur verbatim in the pinned `THEOREM.md` (SHA256-bound).

The recomputed values are compared with [RESULT.json](RESULT.json).

## Reproduce

From the repository root:

```sh
python3.12 -I -B -W error research/rectangle-law-exact-floor/verify.py
python3.12 -I -O -B -W error research/rectangle-law-exact-floor/verify.py
python3.12 -B scripts/research_package.py --package research/rectangle-law-exact-floor
```

Each verifier run ends with `PASS_RECTANGLE_LAW_EXACT_FLOOR`. `--write` regenerates RESULT.json.

## What changed in the task

The card asks about joint helper bases and a legal causal split. This package is a side result:
a rank inequality for the odd-rectangle step of a hub-removed cut bound. It builds no split and
changes no paid profile.

## Limitations

* Hypothesis (S) with u-unit stages is a matrix hypothesis. Whether any actual root with rho > 2
  satisfies it, and how many hub coordinates such a root has, is not shown. The hub rank law and
  Theorem H of the source are not used or re-derived.
* For u ≠ h the grid floor 72 f(u, h) is a lower bound only. It is vacuous where f = 0, and no
  matching total is claimed away from u = h.
* The scalar minimum ⌊(L−1)²/4⌋ is a finite computation for L ≤ 18, not a theorem for all L.
* The source's Lemma 2 packing and Theorem S are cited, not replayed beyond the finite recount in
  `verify.py`. No independent human or proof-kernel review is claimed.

## Open next questions

The structured form is in [TASK.json](TASK.json).

1. **Exact grid total for u ≠ h.** The packing bound need not be tight when u ≠ h. First step: the
   exact least total on small L by the same separation trick, for example L = 4 to 6 over F_3 at
   (u, h) = (1, 2) and (2, 1). Blocker: the search space grows as p^(2L·u·h).
2. **A closed form for every L.** Prove ⌊(L−1)²/4⌋ for the scalar grid and exhibit that many
   cell-disjoint odd rectangles. First step: read the optimal sign vectors for L = 10 to 18.
   Blocker: no general packing is exhibited.
3. **Roots with rho > 2.** Does any connected root satisfy (S) with u > 2, and with how many hubs?
   First step: the hub rank law of #6881 on a root with N − n = 3. Blocker: no such root is in the
   repository.

## Credit

This package was produced by Nick Petalas. DreamingOfClouds's PR #6935 supplies the setting, Lemma 1,
Lemma 2 and Theorem S, and the question; the hub rank law is from the same author's #6881. The
Schur-complement and block-rank facts are classical. New work is Apache-2.0.
