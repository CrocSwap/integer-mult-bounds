# Mode-fiber rounding radius: R ≤ 3/2

This continues the merged #6320 (`research/mode-fiber-radius-bounds`), which
answered part of Nick Petalas's #6312 question. For the PR4933 mode matrix M
(112×8), R is the least ℓ∞ radius such that every x with a nonempty integer
fiber {z : Mᵀz = Mᵀx} has a point of that fiber within R. #6312 proves
R ≥ 1 and #6320 proves R ≤ 2. This package proves:

- **Theorem D. R ≤ 3/2**, so **1 ≤ R ≤ 3/2**. The bound holds for every x, with
  no genericity assumption.
- **The idea.** Centre x at its nearest integer vector. Then move to a vertex of
  the fiber polytope inside the box [−½,½]^112. All but at most 8 rows land
  exactly at ±½, where both neighbouring integers are equally close. Snapping
  the last ≤ 8 leaves an 8-coordinate demand u ∈ L with ‖u‖∞ ≤ 4, which must be
  met by a sum of signed rows.
- **The balancing lemma.** Every block of 8 rows is "one pinned coordinate, three
  free", so it splits into four sign-free pairs worth ±2e_j each. With one pair
  per coordinate in every block ("rainbow"), each coordinate gets 7 pairs.
  Switching one or two blocks to four pairs in one direction fixes the parity
  class of u. That leaves 6 to 10 pairs per coordinate against a demand of at
  most 4.

[PROOF.md](PROOF.md) has the argument and exact scope, and [rounder.py](rounder.py) runs it
exactly. The pins are in [SOURCES.json](SOURCES.json). Complete κ and the selected
frontier are unchanged. This is a property of the exact-mode contract. It does
not claim that any caller needs the contract, and supplies no physical rounder or
error/tape bill. #6320's package is left unchanged; Theorem D supersedes its
Theorem C upper bound.

## Reproduce

From the repository root; the standard library suffices:

```sh
python3 -I -W error -B research/mode-fiber-radius-three-halves/verify.py
python3 -I -O -W error -B research/mode-fiber-radius-three-halves/verify.py
python3.12 -B scripts/research_package.py --package research/mode-fiber-radius-three-halves
```

Each prints `PASS_MODE_FIBER_RADIUS_THREE_HALVES` in about five seconds. Checked exactly:

- the 14 pinned blocks and MᵀM = 56·I;
- that the supports with 0 and 1⁸ form H8, and complements of supports are supports;
- that the column sums are divisible by 8;
- for every block, a rainbow matching and the four straight matchings, with every pair identity;
- the balancing table for all 16 parity classes (minimum 6 pairs on even coordinates, 7 on odd);
- 150 exact rounder runs, including the #6312 witness and all three parity cases (worst error 503/336).

Seven rejection controls fail closed: a flipped matrix entry, a mislabelled pair
direction, a skipped parity toggle, a skipped vertex step, a mode vector outside
L, a claimed radius of 7/5 and a tampered source.

A separate exact stress run of 12,000 random and sparse inputs (seeds 2–5)
found no failure. Its worst error was 1259/840 ≈ 1.4988, so this construction
cannot do better than 3/2.

## Open next questions

**Is R = 1?** By #6320's Theorem A this means asking whether every lattice point
of L in the open zonotope is a 0/1 subset sum of rows. The #6320 sample supports
yes.

- **Why the bound stops at 3/2.** Theorem D loses ½ only on rows whose vertex
  value lies on the far side of 0 from v_i.
- **First step.** Add the sign constraints sgn v′_i = sgn v_i for |v_i| > ¼ to
  the vertex polytope. Use the slack of the balancing lemma (n_j ≥ 6 against
  |u_j| ≤ 4) to repair the rows that those constraints leave at 0.
- **Blocker.** Rows at 0 snap into u with error ½, and nothing yet bounds how
  many there are.

## Credit

Dillon Amburgey (PR4933) supplies M. Nick Petalas (#6312) supplies the contract,
the radius-one witness and the question. Its predecessor credits (JoyboyBrian,
Dugongue, Ali Romman) carry over. #6320 (apoursh) supplies the reduction and the
earlier bound. The Hamming code and vertex arguments are classical. Prepared by
apoursh with substantial Anthropic Claude (Claude Code) assistance. New work is
Apache-2.0.
