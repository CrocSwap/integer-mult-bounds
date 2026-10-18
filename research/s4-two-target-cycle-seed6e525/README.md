# S4 two-target cycle mechanism — seed 6e525611

**Bounded bit-mechanism construction attempt; no new κ claimed.**

## Scope and cost screen

This is a changed `bit-new-register-model` assignment: the address group is
`S4`, the paid letters are the adjacent transpositions `s1=(12)`, `s2=(23)`
and `s3=(34)`, and each letter costs one call. There are three scalar roles
over `F2`; each call is `I + ([s]+[e])N` for one of the 28 rank-one
idempotents `N=uv^T`, `v^T u=1`. The target is
`diag([c],[c],[e])`, where `c=s1*s2*s3` is a 4-cycle. Every input role is
arbitrary and dirty, and all roles must be restored exactly.

Free scalar `GL3(F2)` changes between paid calls are included: move each
change through the adjacent paid factors by conjugating its rank-one
idempotent, which preserves the set of all 28 idempotents. Augmentation
`[g] -> 1` makes every paid factor the identity and forces any final free
scalar map to be the identity as well.

The direct word costs six calls, three for each copy of `c`. A useful local
construction must use at most five, saving at least one of the six paid
transpositions (16.7%). This bill counts every address letter, while granting
free `GL3(F2)` scalar mixing and the third role with no separate hosting or
allocation charge. Those are explicit optimistic assumptions. The endpoint
restores the dirty third role; no clean state, uncharged undo or extra address
letter is allowed. This screen is local only: it has not identified an
occurrence in the selected bit supplier, whose current selected baseline is
complex-primitive-bound. No recursive moment or selected κ change follows.

The selected accepted record is `κ=836330098538459/500000000000000000`
(`certificates/selected-result.json`, SHA256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`). Its
review is `docs/research/community-batch1099-review.md`, source manifest is
`research/community-frontier1094-audit/SELECTED-SOURCE.json`, certificate is
`research/community-frontier1094-audit/ASSEMBLY.json` (SHA256
`1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`), and
reproduction command is `make frontier1094-verify`. The selected-record
binding-only baseline was checked with the pinned `scripts/research_baseline.py`.

## Exact result

No word of at most five calls realizes this target. The direct six-call word
therefore has exact minimum six in the declared model. The search enumerates
the complete radius-two ball from the identity and radius-three ball from the
target using all 84 involutive factors. The shell counts are `[1,84,4697]` and
`[1,84,4697,232692]`, for 4,782 and 237,474 states; their intersection is
empty. Every coefficient is an exact 24-bit element of `F2[S4]`, not a test
under one representation of the address group.

Completeness follows by splitting any word of length at most five as `A B`
with `|A|≤2` and `|B|≤3`. Every factor squares to identity, so `A=T B^-1`
for target `T`; a shorter word would put the same state in both enumerated
balls. A separate literal group-algebra matrix multiplier checks every factor
is involutive, verifies the six-call direct construction, rejects all six
single-call omissions, and rejects a changed third-role target. The optimized
meet uses byte-packed coefficients and exact right-convolution tables.

The complete search took 2.29 seconds and peaked at 60,576 KiB RSS under
Python 3.12.3, well inside the 110-second/1-GiB implementation limits. No
partial search is used in the result. The full seed, base, catalogue and
selected-record pins are in [TASK.json](TASK.json) and [SOURCES.json](SOURCES.json).

## Reproduce

From the repository root:

```sh
python3.12 -I -B research/s4-two-target-cycle-seed6e525/verify.py
python3.12 scripts/research_package.py --package research/s4-two-target-cycle-seed6e525 --check-only
python3.12 scripts/research_package.py --package research/s4-two-target-cycle-seed6e525
```

To regenerate the deterministic receipt before replay, use
`python3.12 -I -B research/s4-two-target-cycle-seed6e525/verify.py --write`.
The direct word is the positive control; six omitted-call words and the
changed endpoint are semantic negative controls. The checker is an exact
bounded proof for this finite alphabet, not a proof assistant result.

## Live overlap and coordination

The final open-PR census covered 405 PR records via REST at 2026-10-14
07:40–07:43Z. The nearest scopes were PR #1478 (the UT3 two-central-commutator
endpoint at two or three roles), PR #1705 (four coordinate-SWAP targets in
`F2[GL2(F2)]` at four roles), and PR #1711 (two affine targets in
`F2[AGL2(F2)]` at two roles). Discussion #1317 contains current AGL2 claims;
the cached complete discussion scan (351 records, fetched 07:28Z), plus direct
current reads of #1167 (through 07:22Z) and #1317 (through 07:31Z), showed no
S4/adjacent-transposition claim.
The S4 group, 4-cycle target, three-role dirty endpoint and adjacent-
transposition alphabet are distinct from those scopes. A current fresh
Discussion fetch and new claim post are unavailable:
GitHub GraphQL reports the account rate limit exceeded, and the installed REST
API has no create/update endpoint for Discussion comments. This local claim
card and package are being used while that limitation holds. The result is
submitted in [PR #1720](https://github.com/CrocSwap/integer-mult-bounds/pull/1720).

## Open next questions

No immediate next question is justified: the complete six-call minimum closes
the proposed S4 endpoint and removes the candidate saving. Searching another
target tuple or alphabet requires a new mechanism, separate overlap check and
fresh cost screen.

## Credit

The formal rational three-register bound and UT3 central-commutator study are
the immediate predecessors. Their changed alphabets and endpoints are pinned
in [SOURCES.json](SOURCES.json); live nearby PR heads are recorded in
[TASK.json](TASK.json). Prepared by Cinna Davis with substantial OpenAI Codex
assistance in scoping, exact search, verification and exposition. New work is
Apache-2.0.
