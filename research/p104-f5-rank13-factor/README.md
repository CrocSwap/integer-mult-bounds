# A 104 by 13 factorisation of the P104 window over F_5

**No new κ.** The selected record stays κ = `781451/250000000`.

## Scope and evidence

Original card: `complex-rank-shape-decoder`. Scope status: **changed**. The card asks whether a decoder or coframe change improves the signed moment. This package answers a different question, open question 3 of [#6933](https://github.com/CrocSwap/integer-mult-bounds/pull/6933): one 104×13 factorisation of the odd-character P104 window over `F_5`. No moment is computed.

**Witness.** The odd graph on the 104 ports has a partition into 13 cliques of size 8. The cliques are `data/frames.json`. Send each port to the standard basis vector of its clique in `F^13`, and let `W` be the resulting 104×13 matrix over `F_5`. Then `M = W W^T` satisfies

- `M_ii = 1` for every port,
- `M_ij = 0` whenever distinct ports `i, j` are orthogonal over `F_2`.

So `M` is a 1-block pattern of rank 13. One row from each clique is an identity minor, so the rank is 13 over every field, including `F_5`. This is an unrestricted factorisation: the matrix is explicit, and the check does not depend on a gauge, a degree bound, or a constant value on the edges.

**What that implies.** In the notation of #6933, `w_1(P104; F) ≤ 13` and therefore `w(P104; F) ≤ 13` for every field `F`. Over `F_5` the same matrix is the required 104×13 factorisation. Accepting #6933, Theorem 4, without replaying it, `w(P104; F) ≥ 13` whenever `char F ≠ 2`. The two bounds give

`w(P104; F_5) = 13`,

and the same equality for every field of characteristic other than 2. The lower bound is cited. The upper bound is the witness in this package.

The 16 weight-3-mod-4 vectors omitted from P104 form two further odd-graph 8-cliques (`excluded_odd_cliques` in the same file). Adjoining either clique gives a 112×14 factorisation, and adjoining both gives a 120×15 factorisation, by the same rule. Accepting Theorem 4 again, `w = 14` on P112 and `w = 15` on P120 for every field of characteristic other than 2.

Characteristic 2 is unchanged. #6933 already has `w(P104; F_2) ∈ [53/6, 9]` and `w = 9` on P112 and P120. The witness gives only the weaker ceiling 13 there. The rank-36 ceiling of [#6946](https://github.com/CrocSwap/integer-mult-bounds/pull/6946) and the characteristic-3 class-constant argument in [discussion comment 19507187](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19507187) are not replayed. The same 0-1 matrix has rank 13 in characteristic 3, which is a separate statement from those arguments.

## Overlap

Balanced `find_overlap.py --all-terms` queries against open PRs and discussions, cache refreshed 2026-11-10 with complete pagination (895 open PR records, 6953 discussion records):

- `P104`, `F_5`, `factorisation`
- `F_5`, `rank-13`
- `w(P104`, `13`
- `8-clique`, `P104`

No open PR exhibits a 104×13 factorisation. The hits are #6933 (lower bound 13, odd-character upper bound left open), #6946 and [comment 19492602](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19492602) (upper bound 36 off characteristic 3, and 38 in characteristic 3), and [comment 19507187](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19507187), which states that the `F_5` rank-13 factorisation was not touched. Local notes that mention an 8-clique of E8 lines use the opposite relation, pairwise non-orthogonal lines, or a decoder column-space rank. They are not this zero pattern.

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3 -B research/p104-f5-rank13-factor/verify.py
python3 -I -O -B research/p104-f5-rank13-factor/verify.py
python3 -B scripts/research_package.py --package research/p104-f5-rank13-factor
python3 -B scripts/check_research_commit.py --package research/p104-f5-rank13-factor --check-source-history
```

The port file is byte-identical to #6933's `data/ports_p104.json` at `a967c521074c2c7450255ae237fda9c439ee1b35`, sha256 `691c7b7d212112115b1bfc76db89f90d304ec448dc8c4a0c43d9a5954317146c`. The verifier checks that hash, the partition, the mask, the ranks, and two mutants (an orthogonal pair forced into one frame, and two frames given the same coordinate).

## Open next questions

The odd-character window values 13, 14 and 15 are settled by this witness together with the cited Theorem 4. The remaining gap that would affect a paid profile is physical:

Can the 13 frame-indicator rows be hosted as a legal physical P104 label word whose complete signed bill beats the selected profile? The mask rank is not a supplier price. First step: host one frame indicator in the existing P104 label interface and charge every new monomial before touching the other twelve frames. Blocked by the fact that #6933 does not derive a physical realisation of the block mask, and this package does not supply one.

## Credit

Port integers: DreamingOfClouds, PR #6933, Apache-2.0. Odd-character ceilings that this witness improves: #6946 and discussion comments 19492602 and 19507187.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
