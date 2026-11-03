# Exact nonnested capacity completion

The [all-size finite-field proof](PROOF.md) counts matrices of EVERY rank
that meet a prescribed map and an arbitrary finite list of source/target
capacity inclusions. Targets need not be nested. A positive count gives
an explicit witness. If no invertible completion exists, the method gives
the exact maximum feasible rank and an attaining matrix.

The method uses classical kernel-subspace inversion. Its new repository
application is the general shared late-capacity contract left open by
[PR6489](https://github.com/CrocSwap/integer-mult-bounds/pull/6489). The
reference is exponential. It does not replace the source's fast nested
criterion or claim a new general efficient matrix-space algorithm.

A fixed injection on u independent directions reduces the kernel lattice
from ambient dimension n to n-u. All coupling to the fixed image space
is kept. The uncompressed API supports n<=4. The compressed API supports
ambient n<=12 with n-u<=4. Both execute over F2, F3 and F5; the written
formula holds for every finite field and dimension.

The discriminating F5 example has four line contacts. Every triple has
four invertible completions, but all four together force the zero map.
All corresponding subset sum/intersection dimensions agree. This is a
classical projective obstruction bound to the exact joint contract.
It prevents using separate feasible contacts as a shared-map certificate.

## Replay and evidence

```sh
python3.12 -B scripts/research_package.py --package research/nonnested-capacity-rank-count
```

Standalone: `python3.12 -I -Werror -B verify.py` here, and again with
`-O`. The [receipt](RESULT.json) is recomputed. Only Python's standard
library and the committed package files are required; no Git or network.

The verifier checks every ordered binary two-dimensional pair of capacity
constraints with each one-vector partial injection, plus random larger
and odd-field contracts, arbitrary affine systems, every subset of the
four-line example, and the source's 4/12/0 nested compatibility example.
Literal matrix actions and vector-image sizes supply independent counts.
Every returned witness is checked against original vector constraints.
Independent diagonal, block and free-matrix formulas cover dimension four.
Larger compressed frames use distinct domain/range charts and preserve
coupling to the fixed image space. Exact counts are in RESULT.json.

The base is canonical main 7c49fe32c55de02c2c873655c804b16e4c3fef0a,
priority 8, selected 6030. The selected binding example passed. The
03:13Z cache covered 479 open PRs and 6,467 Discussion records. Live
handoffs, PRs and main searches were also checked. Nonnested G20 coframes
use a different contract; no overlapping joint GL count was found.
Sparse history, nested diffs and unpublished work remain coverage limits.

## Open next questions

Extract one actual emitted caller's prescribed map and all late capacities.
A small unfixed quotient could permit exact synthesis or rejection. Native
symplectic/signed constraints, absolute phase and every physical cost must
then be checked. A separate useful question is a faster criterion for a
restricted nonnested family; the four-line obstruction and nested source
are required controls for any such criterion.

No new native caller, paid physical invoice, kappa gain or selected-frontier
change is claimed. Precision, stock, ownership, tape, compiler, outer
admission and all five selected assumptions remain. Independent human
and proof-kernel acceptance are unclaimed. Lean, Docker and the selected
cold replay were not run.

## Credit

Ali Romman with substantial OpenAI Codex assistance; no subagents.
Credit Nick Petalas / PR6489 and PR4919; Brian / JoyboyBrian / PR5020;
Cao Yifan / intqwq / PR4610; codyw912 / PR4735; Cinna Davis, Dugongue,
zxv, Jacob Alan Sussman and the retained native/compiler lineage.
The source proof is byte-exact. Finite-field subspace inversion, Gaussian
coefficients, basis extension and cross-ratio geometry are classical;
Stanley's text is linked in the proof. No global literature-priority
claim is made. New work is Apache-2.0.
