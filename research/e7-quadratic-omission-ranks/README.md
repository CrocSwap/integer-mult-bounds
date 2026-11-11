# The two E7 receipt forms have ranks 6 and 2, and every omission stays rank 11

**Proof, with an exhaustive check of the 135 frames and 24 omissions. No new κ.**
The selected conditional value stays `363005817/100000000000`.

## Result

Evaluate the pinned forms `Q_a` and `Q_b` on the 63 E7 roots. Their
polarizations on the pinned seven-vector slice are

```text
diag(1, 1, 1, -1, -1, -1, 0)
```

of rank 6, and the rank-2 matrix displayed in [PROOF.md](PROOF.md). Each form
is nonzero on 12 roots. The 135-by-12 frame-indicator matrix of either support
has rank 11. Its kernel is one-dimensional and has no zero coordinate, so
deleting any one column leaves rank 11. Direct elimination of all 24 deleted
matrices agrees. The supports, values and ranks are the receipt fields in
`research/e7-bitsliced-exhaustion/source/RESULT.json`.

The argument is [PROOF.md](PROOF.md). No word of the `2^27` kernel is scanned.

## Scope and evidence

Catalogue card `replay-runtime`, priority revision 8, base
`e54523517d0f03e58352e647c403a5af3e525a57`. Scope status: **refined**. The
card asks for a measured speedup that keeps coverage. PR #5729 published the
bit-lane speedup. `research/e7-bitslice-coverage-check` and
`research/e7-orbit-hash-partition` matched the weight-12 set to the receipt
orbits and left this rank half unreplayed. This package is that half. It does
not time the engine, rebuild orbits, or install the iterator in another
consumer.

`current-priorities.md` at this base still prints `0.00310045`. The live
selected record is `363005817/100000000000`. This package uses that record
and edits neither file.

Ordered eligible list for session r283, rebuilt on 2026-11-11 against
`e54523517d0f03e58352e647c403a5af3e525a57`. Dropped first: every unpaidmoon
pull request named in the session brief, from #4107 through #7288, and every
fork `cursor/*` branch named there. Structured handoffs whose later post
completes them, or whose canonical artifact is an open pull request, are
dropped. The three prose search failures still left open on 11 November
(signed frames at seven calls, the eight-source singleton, and the `c = 7`
depth-two block) are dropped because this account's open pull requests
already refine those questions. The revision-8 next-decision table comes
next. Catalogue cards that the table does not name follow, in catalogue order.

1. Complex helpers (`p104-side-correction`, `coverage-law-change`).
2. BIT helper contract (`bit-helper-contract`).
3. New decoders and interfaces.
4. Supplier audit (`supplier-boundary-audit`).
5. All-size audit (`uniform-transfer-audit`).
6. **This package.** Verification tooling (`replay-runtime`): the quadratic
   ranks and single-omission ranks left open by the E7 orbit-hash replay.
7. `bit-new-register-model`.
8. `r437-carrier-integration`.
9. `complex-rank-shape-decoder`.
10. `complex-new-helper-inventory`.

Rows 1 through 5 stay because the priority text still states those
decisions. Row 6 stays as well. The word-set half of that row is already
`research/e7-orbit-hash-partition` on main, and the E6, D6 and P112 iterator
matches are open pull requests of this account. The rank half of the same
receipt is the distinct remaining piece. Items 7 through 10 are the next
catalogue cards not named by the six rows.

Evidence classes:

1. **Proof.** The two polarizations and the omission lemma in [PROOF.md](PROOF.md).
2. **Exhaustive finite check.** All 135 frame sums, one exact rank of each
   135-by-12 indicator matrix, and all 24 single-column deletions. The domain
   is this pinned root list, not the `2^27` kernel.

A search that never runs is not a census of kernel words.

## Reproduce

Python 3.12 and the standard library, from the repository root:

```sh
python3 -B research/e7-quadratic-omission-ranks/verify.py
python3 -O -B research/e7-quadratic-omission-ranks/verify.py
python3 -I -B research/e7-quadratic-omission-ranks/verify.py
python3 -B scripts/research_package.py --package research/e7-quadratic-omission-ranks --check-only
python3 -B scripts/research_package.py --package research/e7-quadratic-omission-ranks
```

The direct verifier prints

```text
PASS_E7_QUADRATIC_OMISSION_RANKS
diagonal=6 product=2 frame_rank=11 omissions=24 frames=135 controls=4 kernel_words_scanned=0 no_new_kappa=true kappa=363005817/100000000000
```

Not run: the #5729 timing harness, the `2^27` codeword census, reflection
orbits, Lean, Docker, and `make frontier7000-verify`.
`scripts/research_selected_baseline.py` returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY` and is not a scientific replay.

## Open next questions

- Does every other word in the two receipt orbits have the same quadratic
  rank as its representative? The receipt assigns one rank to each orbit.
  This check sees only the two representative forms. The first step is one
  frozen reflection applied to each representative. This package does not
  call those permutations.
- Is there a fifth decoder code, other than this E7 kernel and the E6, D6
  and P112 sets already recorded by this account, for which the half-split
  matches `low_weight_words`? Name its generators, width and weight bound
  first. No fifth consumer is pinned here.

## Credit

The geometry and minimum-support statement are Nick Petalas's PR #5238,
retained in `research/e7-bitsliced-exhaustion/source/vendor/PR5238.py`. The
two forms, the receipt and the rank functions are Ali Romman's PR #5669,
frozen in `research/e7-bitsliced-exhaustion/source/verify.py` and
`source/RESULT.json`. The bit-lane engine is Ali Romman's PR #5729. The
orbit comparison that left this rank question open is
`research/e7-orbit-hash-partition`. This package does not modify those files.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
