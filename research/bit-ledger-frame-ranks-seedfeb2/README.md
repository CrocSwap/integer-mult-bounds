# bit-ledger-frame-ranks-seedfeb2

**Scoped partial audit of the selected bit supplier's paid-rank accounting. No new
kappa; the selected record, the certificate and the suppliers are unchanged.**

Contributor: Aaron Wang (with help from opencode). Apache-2.0.
Task card: [TASK-CARD.md](TASK-CARD.md); structured metadata: [TASK.json](TASK.json);
machine-readable result: [RESULT.json](RESULT.json).

## Question

[research/selected-suppliers-de-diagnostic](../selected-suppliers-de-diagnostic/README.md)
prices both selected ledgers but takes the paid profiles from the published
aggregates, and names as open question 2: can `nine.profile` be rebuilt from the
original gate operations of the pinned
`research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz` word rather than
taken from `EXPECTED.json`? Its stated first step is: compute the per-frame
transition ranks of the word file and compare against `word.local_histogram` and
`nine.profile`. This package closes that first step up to the emitter boundary
(below): the paid-rank **mass** aggregate is re-derived from the word geometry;
the paid-record **histogram** is not.

This matters for the bit-side coverage identity `D = T(2Kv - L*cst) = W - 63N =
10272`, which the discussion-1587 coverage finding states with the hosted bit
template step marked inferred.

## What is established

All numbers below are recomputed by
[verify.py](verify.py) from the pinned word file and `tune/EXPECTED.json`, with
frame dimensions computed here by exact rational rank (no import of the
supplier's checker chain).

1. **Frame dimensions from operations.** The 636 label frames (live line sets:
   closures of the 120 labelled E8 lines, punctured to 111, per `pwordl.py`) have
   exact rank spectrum `dim 0:1, 1:111, 2:153, 4:70, 6:180, 7:120, 8:1`.
2. **Per-register net frame climbs.** With each register's recorded start and
   final frame ids: every X slot climbs 7 (111 registers), every Y slot climbs 7
   (111 registers), every helper climbs 8 (439 registers). Total net climb is
   **5066 = 8R + 14v** for `R = 439`, `v = 111`.
3. **Copy block.** The nine retained totals (`word.ret`, nine distinct helper
   registers) carry the recorded copy ranks 7 each: 63 = 9 x 7, equal to the
   recorded decoder constant 63.
4. **Paid-rank mass from operations.** 5066 + 63 = **5129 = 8R + 63 + 14v**,
   matching `word.legality.rank_mass` and the identity asserted by the supplier's
   `verify.sh`. The decomposition (which register class contributes what) is
   word-geometric and did not exist outside the checker before this package.
5. **Aggregate cross-consistency.** `word.local_histogram` has weighted sum
   `sum(r n_r) = 5129` equal to the re-derived mass; `nine.profile` has weighted
   sum 1,808,352 = 64W - (W - 63N) with `W = 32*8*111 = 28416` and
   `N = 32*9 = 288`, i.e. the recorded deficit `W - 63N = 10272`.

Five semantic mutation controls must each be rejected: collapsing the full frame
to one label; setting one register's start frame to its final frame; mutating one
copy rank to 6; a one-count mutation of `local_histogram`; a one-count mutation
of `nine.profile`.

## Method and independence

Standard-library Python only, exact `fractions.Fraction` arithmetic. The
verifier reads the pinned gzip word and `tune/EXPECTED.json` directly and checks
their recorded `file_sha256`/`content_sha256` first. It imports nothing from the
supplier's pipeline (`code/gen_p3.py`, `code/xcheck_p.py`,
`e8-bit-carrier-skeleton` checkers, `stage_cohort.py`, `legality_h.cpp`,
`global_k.py`), and it does not run that pipeline. The frame-dimension
convention is derived from `code/pwordl.py`'s word format documentation (frames
are live line sets, closures of the labelled E8 lines) and is validated by the
independent identity 5066 = 8R + 14v across 661 registers.

## Limits (what is NOT established)

- The 2920-record `word.local_histogram` is **not** decomposed into per-record
  MOVE prices. That decomposition lives in the emitter's register-level event
  stream (`COHORT249-RECORDS.bin` via `stage_cohort.py`, priced by
  `legality_h.cpp`, needing a C++17 compiler and Boost), which is out of this
  session's budget. The histogram is only cross-checked at aggregate level.
- The nine copy ranks (7 each) are the recorded block from `word.copy_ranks`;
  they are not re-derived from the word file's gate stream here.
- `nine.profile` is checked at aggregate level only, not rebuilt from the
  32-replica template expansion.
- Nothing here re-checks the moment acceptance, the H1-H5 interface obligations,
  hosting/precision admission, or the complex ledger. This is not a
  multiplication theorem.

## Reproduce

From the repository root (Python 3.10+, standard library only, seconds):

```sh
python3 -B research/bit-ledger-frame-ranks-seedfeb2/verify.py
python3 scripts/research_package.py --package research/bit-ledger-frame-ranks-seedfeb2 --check-only
```

Observed: `PASS_BIT_LEDGER_FRAME_RANKS`, 13 checks plus 5 rejected controls.

## Open next questions

- **Record-level histogram from gate operations.** Question: can the 2920-record
  `word.local_histogram` be decomposed into per-record MOVE prices and the nine
  COPY ranks directly from the A/B/C/D gate streams and the frame menu? Why it
  matters: it completes the from-operations rebuild of `nine.profile`'s inputs.
  First step: reconstruct each register's frame trajectory from the serialized
  gate lists using `pwordl.py`'s `gate`/`climb` convention and compare the
  induced MOVE-price histogram with `word.local_histogram`. Blocker: the paid
  charging convention is defined by the emitter's event stream
  (`stage_cohort.py` + `legality_h.cpp`); free ADDs carry no frames in the word
  file. See [TASK.json](TASK.json) for both recorded next questions.
- **Copy ranks from punctured-hyperplane geometry.** Question: is the nine-element
  copy-rank block derivable as exact frame dimensions of the nine punctured
  hyperplanes? Why it matters: it would make the 63 term of
  `rank_mass = 8R + 63 + 14v` fully from-operations. First step: compute the
  exact rank of each punctured-hyperplane closure and compare with the recorded
  copy rank 7. Blocker: the label-to-copy-frame mapping is defined in the
  supplier's emitter/xcheck.

## Credit

Prepared by Aaron Wang, with help from opencode (substantial AI assistance; no
independent human review claimed). Predecessor credit: the open question and the
pricing model are from Navinor's
`research/selected-suppliers-de-diagnostic` (itself building on Douglas
Colkitt's pricing model in `autoresearch.md` and
`research/pending-claims-independent-pricing`); the pinned bit word, its format
and its checker chain are the PR589/PR555 lineage (eumemic and predecessors,
retained unchanged by the selected record); the bit-side coverage identity
`mass = 63W + 63N` and the port-direction analysis are ctoth's discussion-1587
finding with the disclosed reviewing models. An independently corroborated or
superseded contribution still deserves credit; this package adds the
word-geometric decomposition of the mass aggregate that none of those record.
