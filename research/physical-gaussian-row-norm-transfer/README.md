# Physical Gaussian row-norm transfer

**Status: independently proved the all-center local contraction and its
unit-ball consequence; no tensor theorem claimed.**

## Question and result

At the exact normalized Gaussian interface used by PR #3878, does the row-sum
bound hold uniformly over every center and periodic source labeling, and does
the local tile error then keep its output inside the next tile's unit-ball
domain? Yes. For every real center `c` and `alpha >= 2`,

```text
sum_j exp(-pi (j-c)^2/alpha^2) <= 1 + alpha,
||S/2||_(infinity -> infinity) <= 1/2 + 1/(2 alpha) <= 3/4.
```

With PR #3878's per-output error `C 2^-p`, `C=sqrt(2)+2^-11`, this alone
implies `||tile(x)||_infinity < 1` for every unit-ball input whenever `p>=3`.
The cited PR uses `p>100`, so its local precision is sufficient. The
all-center proof and exact guards are in [PROOF.md](PROOF.md).

The result is a local independent check of a premise in PR #3878. It does not
replay the tile implementation or establish that a full caller applies the
tile to every source interval. The live handoff at #1166 comment `19010279`
claims the larger tensor join; this pass deliberately stops at the local
row-norm/domain implication and does not prove its error recurrence.

## Reproduce

From the repository root:

```sh
python3 -B research/physical-gaussian-row-norm-transfer/verify.py
```

The verifier checks exact rational endpoint constants and the retained PR
proof snapshot hash. The all-center result follows from the layer-cake proof
in `PROOF.md`, not a finite Gaussian sum search. See
[SOURCES.md](SOURCES.md) for source heads and digests.

## Open next questions

The active full tensor-join handoff at discussion #1166 comment `19010279`
owns the next larger question. No distinct local follow-up is justified until
that caller is published; its per-axis source and grid contracts can then be
checked against this lemma.

Credit: Jose Manuel (`jmbarrancoml`), PR #3878, for the physical tile and local
error theorem. The row-sum proof and exact precision implication here are
separate work by OpenAI Codex (`macbook-11`). No independent human or formal
kernel review is claimed.
