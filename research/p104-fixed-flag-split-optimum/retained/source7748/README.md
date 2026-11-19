# A signed split gather reduces P104 flag junk

**Finite certificate.** On source column 4 of one fixed eight-flag `C=56`
configuration, the exact single-gather minimum is **45 even off-diagonal
nonzeros**. A signed split gather at levels 0 and 4 leaves **44**. The split
preserves the nonzero diagonal and every required odd off-diagonal zero.

## Model and witness

As in PR #7689, chain `k` has virtual endpoints `z_k, z'_k` and a complete
binary flag from the line spanned by `z'_k` to the perpendicular space of
`z_k`. Write `tau_k(t)` for the first flag level containing port `t` and
`sigma_k(s)` for the last level perpendicular to port `s`. A gather at
level `g` is legal if `0 <= g <= sigma_k(s)`. With one read, the coefficient
on row `t` and source `s` is

```text
           G[t,z_k] G[s,z'_k]
sum over k ----------------- sum of gather pieces at levels g < tau_k(t).
                 G[z_k,z'_k]
```

For an active chain, the pieces sum to one. A single gather puts coefficient
one at one legal level. The signed extension allows rational pieces with the
same total. If the binary port labels have dot product one, then `t` cannot
enter the flag while `s` is still perpendicular to it. All legal pieces
contribute to that entry. The odd off-diagonal entries and the diagonal
therefore depend only on the terminal coefficient one.

The five active chains in column 4 are `0, 2, 3, 5, 6` in zero-based indices.
Their maximum gather levels are `0, 0, 4, 0, 1`. Exactly two of the ten
single-gather schedules leave 45 junk entries, two leave 47 and six leave 48.
One attaining schedule gathers at `(0,0,4,0,0)`. It suffices to change chain
3, whose virtual labels are 448 and 52. Gather `+2` at level 0 and `-1` at
level 4. Rows 0, 1, 50 and 56 become zero and rows 35, 86 and 90 become
nonzero. All other entries in the column stay fixed.

The checker embeds the split in a complete schedule and checks 104 diagonal
entries equal to 2 and all 5,720 required odd off-diagonal zeros. Since the
formal gather choices are independent by column, this split can also replace
column 4 of a full single-gather optimum for these same flags. The comparison
is with those fixed flags. The best split value, the optimum over all flag
choices, and the physical cost of the extra gather remain open. No selected
multiplication bound follows.

## Reproduce

From the repository root, using CPython 3.12.15 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p104-c56-split-gather-witness
python3.12 -B scripts/check_research_commit.py --package research/p104-c56-split-gather-witness --check-source-history
python3.12 -I -W error -B research/p104-c56-split-gather-witness/verify.py
python3.12 -I -O -W error -B research/p104-c56-split-gather-witness/verify.py
```

The verifier prints `PASS_P104_C56_SPLIT_GATHER_WITNESS`, the exact histogram
of the ten unsplit schedules and the split count. It rejects a misplaced
piece and a wrong total coefficient.

[WITNESS.json](WITNESS.json) holds the ordered labels, one eight-entry Gram profile
per line, chain pairs, flag bases and signed gather. The Gram profiles are the
inner products against the eight listed basis ports. If `H` is the Gram
matrix of the basis and `p_a` is a column of eight products for line `a`,
then `p_a^T H^-1 p_b` gives the full Gram entry. The verifier uses exact
rationals and matches the reconstructed 104-port Gram and labels to the
SHA-256 hashes of the source files. It checks the virtual-line entries against
the binary labels and reconstructs each flag. Replay has no network or
third-party dependency.

## Open next questions

- Can signed gathers decrease the best junk count over the admissible flags?
  Start by fixing flags from a low-junk single-gather witness and solving the
  per-column zero equations for signed prefix coefficients. A gain on the
  flags here gives no bound for the best flags in either model.
- Can a paid native gather implement the extra signed piece and its
  restoration at a cost below the removed junk? The fixed-flag calculation
  leaves the actual transport, storage and recursive prices open.

## Credit

This result was produced by Nick Petalas. Credit DreamingOfClouds for the
`C=56` model, the first eligible chain configuration and its geometry, and
for identifying split gathers as outside the prior bound.
[PR #7689](https://github.com/CrocSwap/integer-mult-bounds/pull/7689)

Source head `511e7d0852acdca291b50c538b978fb063ae7bac`, directory
`research/p104-c56-class-ceiling/certificate/`. The basis profiles use the
source `geo.py` ordering and its files `data/G104.npy`, `data/lines104.json`
and `data/f1cfgs.pkl`. The geometry program `geo.py` and configuration list
`data/f1cfgs.pkl` have SHA-256 values
`d907a68eaa8362d77ad7a0600ce8c6c0592397f8817ffa82de3675658f65632e`
and `3a65c5101058c283b72407ad4bbe116e2154cc760c63b524026f3f84012888f4`.
[Source tree](https://github.com/DreamingOfClouds/integer-mult-bounds/tree/511e7d0852acdca291b50c538b978fb063ae7bac/research/p104-c56-class-ceiling/certificate)

Apache-2.0.
