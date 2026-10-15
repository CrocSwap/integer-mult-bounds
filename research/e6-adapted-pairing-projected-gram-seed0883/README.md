# E6 projected-Gram decoders with an adapted pairing

**Scoped exact obstruction; no new κ or supplier.** This package tests one explicit rank-four construction family for the open E6 low-T root-unit question. It does not rule out arbitrary rational E6 decoders or arbitrary admissible pairings.

## Model and target

The root-unit model from PR #1590 takes the 36 rational E6 root lines and an admissible binary pairing `B`. A four-total decoder is

`M = sum(j=0..3) p_j q_j^T`,

with every diagonal entry nonzero and `M[t,s]=0` whenever `B[t,s]=1` off the diagonal. If `R_j` and `A_j` are the supports of `p_j` and `q_j`, its local Theorem C charge is

`sum(j=0..3) max(5, rank_F2(B[R_j,A_j]))`.

Here the E6 per-total floor is `w=5`. Four totals have an ideal charge of 20. The E6 T=4 break-even thresholds are 23 at h=8, 22 at h=9, and 21 at h=10–11. This package uses 22 as its predeclared target. That charge is complete for the root-unit model; it does not include a physical mapping into the selected complex provider.

## Construction family and changed assumption

The exact E6 lines are generated in the E8 realization, scaled by two to integer coordinates. For ordered four-coordinate subsets `U,V` of the eight axes, let `P_U` and `P_V` be the 36-by-4 root-coordinate matrices and set

`M = P_U P_V^T`.

This is an exact four-term rational decoder when both factors have rank four and every diagonal entry is nonzero. For each such candidate, use the **maximal compatible symmetric pairing**: diagonal entries are one, and an off-diagonal pair receives ones in both directions exactly when the root lines are orthogonal and both decoder entries vanish. Every set pairing entry is therefore admissible and is a decoder zero.

This changes PR #2137's fixed full-orthogonality `B0` premise. The pairing is adapted to the projected decoder's zero pattern. The finite domains are all 70 principal projections `U=V`, followed, because none meets the target, by all 4,900 ordered pairs `(U,V)`.

## Exact result

`verify.py` exhausts both domains using integer root coordinates, exact rational rank checks, and F2 bit-matrix elimination:

- The 70 principal projections contain five full-rank, nonzero-diagonal candidates. Their minimum charge under the maximal compatible pairing is 84.
- Across all 4,900 ordered pairs, 13 candidates are full-rank with nonzero diagonal. Their minimum charge is 65, attained at `U=[3,4,5,6]`, `V=[3,4,5,7]`, with term block ranks `[17,17,17,14]`.
- No candidate in this projected-Gram/maximal-pairing family reaches the target 22.

The candidate counts, best witnesses, root hash, matrix and pairing hashes, and a six-clique certificate for each of the 13 valid candidates are recorded in `RESULT.json`.

### Rank-five Gram-pairing obstruction

For each of the 13 valid projected decoders, define the required-zero graph on E6 lines: an edge is present if the roots are nonorthogonal, or either directed entry `M[t,s]` or `M[s,t]` is nonzero. Every admissible pairing must be zero on each such edge.

Every one of these 13 graphs contains a certified six-clique. If a symmetric pairing had a Gram representation `B=A A^T` with five binary coordinates and unit diagonal, its six vectors on that clique would have self-dot-product one and pairwise dot-product zero. Their Gram matrix would be `I_6`, of rank six, which cannot factor through `F2^5`. Thus this decoder family has no rank-five Gram pairing.

This does **not** exclude rank-six pairings, non-Gram pairings, or subpairings whose four restricted support blocks each have low rank. The maximal-pairing cost 65 is not a lower bound for all sparser pairings.

## Verification

The verifier checks the 36-line E6 construction, exact norms and orthogonality, rational factor ranks and diagonal entries, pairing legality, the charged F2 block ranks, all 70/4,900 candidates, and all clique certificates. It also includes rank controls and negative controls for an illegal pairing edge and a zero decoder diagonal. The exact root-line set was compared against the pinned predecessor generator `ade.E6b()` during author verification; the replay itself uses the standard-library integer construction.

From the repository root:

```sh
python3 -I -O -B research/e6-adapted-pairing-projected-gram-seed0883/verify.py
python3 scripts/research_package.py --package research/e6-adapted-pairing-projected-gram-seed0883 --check-only
python3.12 scripts/research_package.py --package research/e6-adapted-pairing-projected-gram-seed0883
```

Expected verifier result begins `E6_PROJECTED_GRAM_SCREEN roots=36 principal=70 valid=5 best_cost=84 ordered=4900 valid=13 best_cost=65`, followed by `NO_COST_LE_22_IN_DECLARED_PROJECTED_GRAM_FAMILY`, `NO_RANK5_GRAM_PAIRING_FOR_DECLARED_PROJECTED_DECODERS`, and `PASS_E6_ADAPTED_PAIRING_CONTROLS_AND_RESULT`. The direct verifier was replayed locally with Python 3.14.7. The registered package wrapper requires Python 3.12, which is not installed in this environment; `--check-only` and the repository selected-record gate pass, while the generic Python 3.12 replay remains for CI.

## Open next questions

- Can the best projected decoder use a rank-six or higher non-Gram pairing whose four restricted blocks have total charge at most 22? The first step is a shared-pairing exact rank search for that single witness; this package does not enumerate sparse subpairings.
- Can a structured rank-four E6 decoder outside the coordinate-projection family reach cost 22? The next step is to choose a new factor family and screen its favorable full local budget before synthesis.
- What source, frame, copy, precision, restoration, hosting, and interface costs would be needed to place a root-unit decoder inside the selected provider? No provider occurrence is established here.

## Pins and credit

The assignment seed is `0883a0f84126624d58444b85d7c6b119`, track `complex-mechanisms`, chosen task `complex-rank-shape-decoder`, priority revision 4, and exact base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. The selected-record SHA-256 is `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`. Full source blob and SHA-256 pins are in [SOURCES.json](SOURCES.json); the public claim and its scope update are in [Discussion #1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18937268).

Predecessors: DreamingOfClouds' merged [PR #1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590) defines the root-unit decoder model and charge; open [PR #2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) records the T=3 decoder questions; open [PR #2125](https://github.com/CrocSwap/integer-mult-bounds/pull/2125) records the E6 thresholds; and open [PR #2137](https://github.com/CrocSwap/integer-mult-bounds/pull/2137) excludes only its fixed-B0 coordinate-bilinear family. This package credits that work and changes the pairing premise.

Prepared by Cinna Davis with substantial OpenAI Codex assistance. No independent human review is claimed. No κ or selected-frontier change is claimed.
