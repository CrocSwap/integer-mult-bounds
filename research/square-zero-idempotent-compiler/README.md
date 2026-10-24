# Exact square-zero coupling compilation

This contribution was produced by Nick Petalas.

A rank-q square-zero binary coupling can be implemented by exactly the
smallest even number of rank-one idempotent reflection calls greater than q.
The minimum is q+1 for odd q and q+2 for positive even q; the zero matrix
costs zero. This is a scoped algebraic proof with exact finite corroboration.

For rank three the new joint construction uses four calls, improving the six
calls of the factorwise compiler in ywz65's merged
[PR2716](https://github.com/CrocSwap/integer-mult-bounds/pull/2716).
The first improvement is shipped here without extending the operation alphabet.

The full endpoint is `I+(1+[g])N` over formal `F2[C2]`, with `N^2=0` and
one fixed nonidentity involution g. Each paid call has a binary rank-one
idempotent coupling. Free binary scalar mixing and any finite number of
restored arbitrary dirty roles are allowed. The matching lower bound applies
uniformly to all these dimensions. [PROOF.md](PROOF.md) gives the explicit
projectors, free-mixing normalization, parity obstruction and rank-saturation
obstruction. It proves the full formal identity, not only selected columns.

## Evidence and reproduction

From the repository root, use CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/square-zero-idempotent-compiler/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/square-zero-idempotent-compiler/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/square-zero-idempotent-compiler
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/square-zero-idempotent-compiler --check-source-history
```

Substitute another CPython 3.12 path outside this environment. Expected output
includes `PASS_SQUARE_ZERO_IDEMPOTENT_COMPILER rank3=4 previous=6 no_new_kappa`.
The verifier writes no files and emits a receipt bound to package and live
source hashes. No receipt is hand-written or inferred from a previous run.

The exact checks enumerate all 66,066 binary matrices through four roles.
An independent additive shortest-path search computes their minimum number
of rank-one idempotent summands, without using the proposed compiler. All
343 square-zero matrices match the formula, including all 210 rank-two
matrices, each requiring four summands. The compiler then checks every one
of those 343 complete formal endpoints and 2,678 faithful regular-action
basis columns. Eight further conjugated fixtures cover ranks one through
eight with two restored dirty spectators, 176 regular columns and 48
single-call omission controls. Four boundary controls reject non-square-zero
inputs, a noninvolutory-label substitution and dirty-input-only leakage.

These bounded checks corroborate the all-rank proof; they do not derive an
unbounded theorem from finite enumeration. CPython 3.12.15 is the recorded
local interpreter. No predecessor executable or census was replayed.

## Scope, overlap and limitations

This changes the `bit-new-register-model` card to a compiler side question.
It does not meet the card's native-supplier gate. The historical first command
`scripts/research_baseline.py` fails with `KeyError: 'bit_lower'` under the
selected schema; the current `scripts/research_selected_baseline.py` passes
its metadata orientation. Neither is a scientific premise of this proof.

Canonical base is `624de9dc66858af0945e5f8a0942488d62280d43`, priority
revision 7. [SOURCES.json](SOURCES.json) pins the inherited compiler README
and historical catalogue/selected context. [TASK.json](TASK.json) records the
changed scope and structured next question. The source README is cited and
authenticated, not offered as a verification deliverable.

Initial overlap-helper coverage was 428 open PRs at 23:37 UTC and 3,964
Discussion records at 23:38 UTC on October 22, 2026, with complete remote
pagination. Sparse local coverage was incomplete, so separate `git grep`
searches over main's full README tree and merged-PR searches covered
`square-zero`, `nilpotent`, `idempotent`, compilation and decomposition terms.
The finite-dihedral extension was discarded because David Arias's merged
PR2738 already covers arbitrary couplings. No-match searches do not establish
novelty, and unpublished work remains outside coverage.

Scalar basis conversion costs, native reflection implementation, recursive
child pricing, physical routing/hosting/precision/tape/stock and a complete
multiplication theorem remain unestablished. The four-call result alone does
not assert a better total physical bill or new kappa. The lower bound excludes
other address labels, clean/discarded workspace and nonconstant free maps.
Independent human and formal proof-kernel review are unclaimed. Lean, Docker
and the selected full cold replay were not run.

The verifier uses Python-managed allocations, a Power of Ten rule-3 deviation.
Its enforced maximum width is 20; the largest shortest-path state space is
65,536 binary matrices with 120 possible moves per state. Every loop has a
finite bound, functions are below 60 physical lines, and explicit exceptions
keep checks active under optimization. It uses no recursion, dynamic code,
external solver or subprocess. Both registered checks treat warnings as errors.

## Related open work

The title/body searches before publication found no open PR claiming this
square-zero-to-idempotent compilation minimum. Open PR4849 studies the
UT3(F4) central-target floor after admitting nilpotent calls. Its group,
endpoint and paid alphabet differ; it does not determine this fixed-involution
compiler cost. No numerical comparison or predecessor replay is asserted.

## Open next questions

Can this joint compiler improve a fully charged native boundary? Fix one
literal caller with a rank-three square-zero coupling and compare the four-call
construction with the six-call factorwise implementation, including every
scalar basis conversion, frame and movement cost. A native reflection contract
and complete physical invoice are the blockers. The structured question is in
[TASK.json](TASK.json).

## Credit

Credit ywz65/PR2716 for the arbitrary-coupling identity and factorwise dirty
compiler, and Adam Gall/PR1911 for the register context. The retained lineage
includes eumemic/PR288, Ali Romman/PR468, woklerx/PR1443, Gareth Davidson/PR1333,
Arham Tahir/PR1589 and Cinna Davis/PR2290. The new repository contribution is
the sharp joint compilation count and matching construction. No priority claim
is made for elementary idempotent-sum or square-zero matrix facts. New work is
Apache-2.0.
