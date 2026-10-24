# A smaller reusable residual bound for principal windows

One positive source barrier improves the retained #3851/#3872 setup fixture's
all-principal-window inverse-error constant from **4/11 to 83/234**. The exact
decrease is 23/2574. Its sufficient known-integer recovery threshold increases
from residual infinity norm `<11/8` to `<117/83`.

At residual `7/5`, the improved certificate gives error at most
`581/1170 < 1/2`, while the older row-gap certificate gives `28/55 > 1/2` and
does not decide recovery. Integral exact output is an explicit premise.

The claim type is a scoped proof with exact finite corroboration. This is a
new numerical certificate at Dugongue's fixed-source sliding-window boundary,
taking [#3872](https://github.com/CrocSwap/integer-mult-bounds/pull/3872) Open
next question 3. It does not re-audit its inverse cache or reproduce its slide
census. The matrix is an actual retained rational setup fixture, not a
production Gaussian window. No production guard or selected frontier changes.

## Result and optimality boundary

For a complex matrix H, let `M_ii=|H_ii|` and `M_ij=-|H_ij|` off the diagonal.
Assume a positive vector w satisfies `Mw>0`. For any nonnegative full-source
residual envelope r, set `h=M^-1 r`. Then every principal window J satisfies

```text
|H_J y-b| <= r_J    implies    |y-H_J^-1 b| <= h_J.
```

The same h covers every ordered slide sequence, regardless of length. It is
the componentwise least full-source supersolution `Md>=r`. For r=1 it also
attains the best scalar certificate `max(d)/min(Md)` over positive d with Md>0.
For the retained fixture,

```text
h = (49/156, 10/39, 83/234),        Mh = (1,1,1).
```

[PROOF.md](PROOF.md) gives the dimension-uniform maximum-principle argument,
principal-restriction implication, optimality and recovery corollary. The
comparison matrix itself attains the bound. This proves sharpness over the
same-magnitude comparison class, not the exact inverse norm of the signed
source H or the optimal cost of a physical decoder.

For rational M and r, including this fixture, preparing h costs one dense
rational solve, O(N^3) field operations, with O(N) stored barrier rationals in
addition to solve workspace and source access. The complex theorem does not
assert rational arithmetic for irrational magnitudes.
All residual formation, coefficient preparation, comparisons, scaling, page
emission and cleanup remain paid. A physical saving is not inferred from the
smaller sufficient error constant.

## Evidence and reproduction

CPython 3.12, standard library only, from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/window-comparison-barrier
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/window-comparison-barrier/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/window-comparison-barrier/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/window-comparison-barrier --check-source-history
```

The marker is `PASS_WINDOW_COMPARISON_BARRIER`. Every run constructs the new
barrier by rational elimination and checks it with a separate permutation-sum
determinant oracle. It enumerates all 15 ordered nonempty principal windows,
all 16 sign choices at the four nonzero off-diagonal positions and all residual
box vertices, giving 1,248 direct error comparisons. It also checks 78 literal
known-integer recoveries at residual 7/5, the sharp comparison-class half-unit
boundary and 12 rejected malformed or insufficient certificates. No predecessor
module is imported or executed.

Source hashes are checked before AST-only extraction of the retained fixture.
The [source manifest](SOURCES.json) binds the source README, proof and immutable
setup file to canonical main `81e9bd69e4a5b00ba9c713a1620e36d576d5522e`.
All three are declared replay inputs. Catalogue and selected-record pins are
provenance only. The [task record](TASK.json) states the changed card scope.

An optional `--receipt /absolute/new/path.json` writes a generated result and
package-file SHA256 manifest outside the checkout. Ordinary runs write nothing.
Receipts are not hand-written. Normal and optimized registered replays run the
same explicit checks; correctness does not depend on Python assertions.

The universal result rests on the written proof. Finite cases corroborate the
fixture and verifier. Independent human and formal proof-kernel review are
unclaimed. No full Gaussian page integration, native or fixed-tape execution,
selected cold replay, complete supplier admission or new kappa is claimed.

## Open next questions

- Bind the barrier to an actual rounded production factor page. First freeze
  its global H, format, incoming-grid bound and exact residual envelope, then
  compare complete old/new guards. The missing physical preparation, emission
  and cleanup bill blocks an operational saving claim.
- If the global source changes, can its least comparison barrier be updated
  without a new dense solve? First specify one exact source update and its
  comparison-matrix change. A preserved positive dominance witness is required;
  the present theorem assumes one fixed source.

## Credit

This result was produced by Nick Petalas. David Ganz / Dugongue's #3872 supplies
the fixed-source sliding-window boundary, weighted recovery question and retained
fixture. Jose Manuel / jmbarrancoml's #3851 at
`7ab67b4a84d28cd562b9711aa315ca5b47822b37` supplies that exact setup fixture and
physical preparation context. Credit Chafik Boukhalfa's #489/#481/#486,
RaD / hipotures, Jose Manuel's #3787 and the retained Gaussian/FFT lineage for
the predecessor framework. Classical M-matrix and maximum-principle reasoning
retain their mathematical credit. The new step is this reusable least-barrier
contract and its exact fixture improvement, not invention of comparison theory.
No predecessor source or credit line is changed. New work is Apache-2.0.
