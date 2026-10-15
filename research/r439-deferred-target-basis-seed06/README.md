# Deferred target basis: `V R = I` replaces H5 together with the H2 target clause

**Replacement-interface result with finite R439 instances. No new κ, and the bit side does not
bind.** The selected result, the selected bit supplier (PR589) and `upstream/` are unchanged.

## The interface result

Three statements of the interface keep two clauses fixed: the inherited interleaved lemma (eumemic's
PR543, `research/e8-bit-r420/README.md`) and the two later R439 replacements of H2/K. The clauses are:

- the target clause of H2: D adds to the targets without changing their basis, `R = I`;
- H5: the raw word `W0' = (A, scatter, B)` has target-to-target block `V = I`.

The two replacements are woklerx's PR1194 semantic D (H2-sem) and PR1868's twisted helper contract.
PR1194 states the first clause as "complete restoration of every helper and target basis at D's
boundary".

This package replaces that pair by their product. D may leave the targets in any basis R, provided
`W0'` applies `R^-1` before the targets climb:

| | inherited / PR1194 / PR1868 | H5-tw (this package) |
|---|---|---|
| D operator | `(x, y + N h, T h)` (`T = I` except PR1868) | `(x, R y + N h, T h)` |
| D shape | zero frame, source-free, no COPY/ERASE/climb | same |
| target basis | `R = I` and `V = I` | **`V R = I`** |
| source response | `J = I` | `J = I` |
| helper response | `N = K` (PR1194), `N = K'T` (PR1868) | **`V N = K'T`** |
| cleanup | z-only at the full frame; literal H4 (`T = I`) or PR1868's H4-tw | z-only at the full frame; `C U'(I ⊕ T) = I` |
| H1, H3 | kept | kept |

**Lemma (H5-tw, with its converse).** Assume:

- H1, H3 and the D shape;
- C is z-only at the full frame;
- D acts as `(x, y, h) -> (x, R y + N h, T h)`, and `W0'` has block form
  `z' = U'z`, `y' = V y + J x + K' h`.

Then the complete word acts as `(z, y) -> (C U'(I ⊕ T) z, V R y + J x + (V N + K'T) h)`. So it maps
`(x, y, h) -> (x, y + x, h)` on every F2-module **if and only if** all four of these hold:

    V R = I,    J = I,    V N = K'T,    C U'(I ⊕ T) = I.

Each equation is read off the unit columns, so all four are necessary. The inherited contract is the
case `R = V = I`. Under the literal H4, the last equation holds exactly when `T = I`; PR1868's H4-tw
is that equation itself. [PROOF.md](PROOF.md) section 1 gives the proof.

**The bridge, cut by cut.** A deferred word W' differs from its base word W only on the targets,
and only by the target basis. From W's undo to W''s deferred undo, every target of W':

- sits at the zero frame;
- is read by no z gate (H1): the only gates touching it are scatter ADDs into it and the undo gates;
- holds `M` times W's target values, where `M = E` during A and the scatter.

The undo runs at the zero frame, after which the complete states (values and frames) are equal and
the remaining instructions are identical. `verify.py` replays the deferred word's own D, A and B
prefix against W in lockstep. It checks this invariant at every cut on every word, for example
3,585 cuts on PR1062 and 3,136 on PR1188.

W itself is anchored as before. For the 17 words with `T = I`, its D has PR589's D operator, and the
PR1194-style splice passes every inherited owner flag. PR1868's two words use its own bridge.

**We argue that no new physical premise is needed** (PROOF.md section 3). The deferred undo consists
of zero-frame B target writes from target sources, which the inherited H3 admits. W's own scatter
ADDs are already zero-frame target writes made after A's climbs.

This differs from PR1194's substitution, which was restricted to frame-zero D prefixes. Here the
twisted window extends through A and the scatter, with the targets held at frame zero and unread.

It also differs from PR1868. There, three helpers climbed out of the zero frame holding a twisted
value, which needed the helper common-frame / climb-additivity premise. Here no twisted register
ever climbs.

**Maximality (fixed ordered frame paths).** Here B means W's B, which is W''s B after the deferred
undo. On every word:

- the nonzero frame sets of the 111 targets are pairwise disjoint (0 of 6,105 pairs share one);
- every target's first B touch climbs out of the zero frame, the first at B[0];
- no B target write reads a target, and B's own target block is I.

Hence every target-from-target gate must run at the zero frame before its operands' first climbs.
The deferred undo is one such placement.

- **Timing.** The undo cannot follow B[0], whose target is an undo operand.
- **Absorption.** No undo gate can be absorbed into a B target write. Of the 585 (undo gate, B write)
  pairs per word (587 on PR1040, 586 on PR1449), none is frame-legal.
- **Prefix splits.** Among prefix splits of the literal undo order only, full deferral is a best
  split: keeping a prefix of the undo in D never makes the scatter cheaper.

**Full deferral is not optimal once commuting reorders are allowed.** The pre-PR proof review found
a better split, which the same lemma covers. Keep an order ideal (a commutation-closed down-set) of
the undo's dependency poset at the end of D, list the scatter in the resulting basis, and run the rest
of the undo first in B. See "Order-ideal refinement" below and [PROOF.md](PROOF.md) sections 4–5,
which also give the scope limit when paths may change.

## The construction

Every committed PR915-lineage R439 word has a D section of this shape:

    helper-star preparations, P_E (306 gates), helper reads (111), U_E = P_E reversed, helper restorations

All of it runs at the zero frame. `P_E` has 307 gates on PR1040 and PR1449, and PR915's word has no
helper stars. The deferred word makes three changes:

1. it deletes `U_E` from D;
2. it runs the same gates, at the zero frame, as the first gates of B;
3. it replaces the scatter listing S (111 rows over the nine retained totals) by the rows of `E S`.

`E S` is the unique listing for this placement (PROOF.md section 1). Its consequences:

- **Twisted window.** During A and the scatter the targets hold E times their original values.
- **Contract.** `R = E` and `V = E^-1`.
- **Unchanged.** T, J, K', U' and C are all unchanged.
- **Scatter.** `E S` has 55 nonzero rows and 97 ones, against 527 ones in S.
- **Count.** The complete local ADD count falls by 430 (432 on PR1040; see below). The undo's ADDs
  move from D to B; none is deleted.
- **Frames and bounds.** Frame paths, COPY ranks, MOVE records and the paid profile are unchanged.
  F is unchanged, and B falls.

## Census of every committed lineage word (as of base c6765481)

All 19 distinct committed lineage words were found by scanning `research/` for R439 word files and
deduplicating vendor copies by canonical hash. To repeat the scan (it needs git), run:

```sh
python3 research/r439-deferred-target-basis-seed06/verify.py --census-scan
```

It lists every committed R439 word and reports any word missing from the verifier's lists. At c6765481
it reports 27 distinct words (19 lineage and 8 outside), all listed.

Every number below is recomputed live by `verify.py` and pinned in [EXPECTED.json](EXPECTED.json).

| word (PR, author) | ADDs base → deferred | saving | F | B base → deferred | local/nine-stage bits |
|---|---:|---:|---:|---:|---|
| PR915 (Gareth Davidson), `r439-target-compensation` | 13,208 → **12,778** | 430 | 49,347 | 9,534,616 → 8,742,940 | 100/189 → 99/189 |
| PR926 (Gareth Davidson) | 11,980 → 11,550 | 430 | 71,907 | 10,562,318 → 9,770,642 | 102/192 → 101/192 |
| PR941 (Gareth Davidson) | 11,949 → 11,519 | 430 | 70,083 | 10,548,832 → 9,757,156 | 101/192 → 101/192 |
| PR941 floor-calibration word | 11,948 → 11,518 | 430 | 73,603 | 10,518,760 → 9,727,084 | 102/**193** → 101/192 |
| PR965 (Ross Richardson) | 11,840 → 11,410 | 430 | 72,399 | 10,464,656 → 9,672,980 | 102/192 → 101/192 |
| PR967 (Sricharan Vagvala) | 11,783 → **11,353** | 430 | 72,847 | 10,394,084 → 9,602,408 | 102/192 → 101/192 |
| PR1040 (woklerx) | 11,780 → 11,348 | **432** | 72,847 | 10,394,084 → 9,602,408 | 102/192 → 101/192 |
| PR1047 (woklerx) | 11,769 → 11,339 | 430 | 72,847 | 10,394,084 → 9,602,408 | 102/192 → 101/192 |
| PR1449 (Hanson Sun, @bbMisk) | 11,781 → 11,351 | 430 | 72,847 | 10,394,084 → 9,602,408 | 102/192 → 101/192 |
| PR1062 (Sagar Thakrar) | 11,500 → **11,070** | 430 | 25,717 | 5,911,840 → 5,024,524 | 95/182 → 95/181 |
| PR1062 composition word | 11,515 → 11,085 | 430 | 24,625 | 5,846,566 → 4,971,904 | 95/181 → 95/180 |
| PR1062 pair-control word | 11,715 → 11,285 | 430 | 24,563 | 5,892,602 → 5,005,286 | 95/181 → 95/180 |
| PR1543 (ToikY) | 11,489 → **11,059** | 430 | 25,885 | 5,977,064 → 5,089,748 | 96/182 → 95/181 |
| PR1709 (Cinna Davis) | 11,488 → 11,058 | 430 | 27,061 | 5,921,344 → 5,034,028 | 96/182 → 95/181 |
| PR1868 absorbed PR1062 (Sagar Thakrar), `T ≠ I` | 11,497 → 11,067 | 430 | 25,717 | 5,858,638 → 4,976,508 | 95/182 → 95/181 |
| PR1122 (Gareth Davidson) | 10,652 → **10,222** | 430 | 15,223 | 3,910,388 → 2,996,128 | 92/176 → 91/174 |
| PR1208 (ToikY), `r439-abc-zrewrite-seed16` | 10,542 → **10,112** | 430 | 13,721 | 3,663,878 → 2,774,762 | 91/174 → 91/173 |
| PR1188 (Gareth Davidson) | 10,492 → **10,062** | 430 | 13,667 | 3,758,418 → 2,825,146 | 91/175 → 91/173 |
| PR1868 absorbed PR1188 (Sagar Thakrar), `T ≠ I` | 10,489 → **10,059** | 430 | 13,667 | 3,748,680 → 2,816,834 | 91/175 → 91/173 |

Bold ADD counts are the eight pinned in `verify.py`'s probe table (from the unpublished exploratory
probe); all eight reproduce exactly. On every word `verify.py` checks all of the following:

- **Boundary.** `(x, y, h) -> (x, y + x, h)` on all 661 dirty columns, forward and reverse, through
  the literal COPY/ERASE stream, for both the base and the deferred word.
- **Frames.** The ordered per-register frame paths and the exporter's 2,911 MOVE records are
  identical.
- **Paid profile.** Every lineage word has the PR589 profile `{1:1323, 2:1342, 3:79, 4:44, 5:102,
  6:11, 7:19}`, rank mass 5,129. It is computed from the frame paths and, separately, by the pinned
  exporter (`research/e8-bit-carrier-skeleton/code/bit/export_records.py`), which runs with exit code 0.
- **Guards.** The exporter's ADD count and F/B match the literal replay. Both strict guards
  (`64 F^3 B^2 < 2^104`, `2^18 F^5 B^4 < 2^192`) hold on every deferred word, and the guard bits
  never rise.
- **Owner checker.** The unchanged `research/e8-bit-p111-tuned/code/xcheck_p.py` accepts geometry
  and endpoint. Exactly one flag becomes newly false, `H5_V_identity`, beside the inherited
  `H2_D_frame0_targets_from_helpers` and `K_equals_D`. PR1868's words also keep their inherited
  `H4_C_literal_reverse_at_full` and `C_is_U_inverse`.
- **Identities.** `V R = I`, `V N = K'T`, `J = I` and `C U'(I ⊕ T) = I` hold, with `R = E` and `V`
  equal to the matrix of the literal undo gates. The base word is the `R = V = I` case.

**Not reproduced as stated.** An exploratory estimate of 430 on every word does not hold for
PR1040: its E differs (PR1040's extra target step), its `E S` listing has 95 ones, and the saving is
432. PR1449 also has 307 preparation gates, split by a helper gate, but its listing has 97 ones and it
saves 430. Every other probe number reproduces.

**Composition with PR1868.** PR1868's absorbed PR1188 word is merged. Deferral on it gives
**10,489 → 10,059**, the lowest full-deferral count in this census.

**Words outside the lineage.** Eight committed R439 words have no target-basis block: PR555, PR589,
PR904, PR936, PR952, PR980, PR1127 and PR1221. Their D is the 111 helper reads, so `R = I` and the
deferral is vacuous; `verify.py` checks the shape.

Some packages carry moves or certificates rather than a committed word. They are not censused here:

- PR1045 and PR1400 (helper fusion and descent moves);
- PR1704 (two-copy scatter).

## Order-ideal refinement (found by search, not optimal)

Call a set I of undo gates an **order ideal** when it contains, with each gate, every earlier undo gate
that the gate does not commute with. Keeping such an I in D is then commutation-equivalent to splitting
the undo there. The ideal-split word keeps I at the end of D (at the zero frame), lists the scatter as
`G_I E S`, where `G_I` is the product of the gates in I, and runs the rest of the undo first in B. It
meets the same lemma, with `R = G_I E` and `V = E^-1 G_I^-1`.

`verify.py` runs two searches on every lineage word:

- an exhaustive search over all ideals of size at most 4 (566,500 of size 4 on the 306-gate words);
- a greedy strict descent.

Both find the size-3 ideal {31, 51, 52} with scatter nnz 94 against 97 ({32, 52, 53} on PR1040 and
PR1449, with 92 and 94). No size-4 ideal does better.

On four words it builds the split and applies every check of the deferred word: boundary both ways,
paths and MOVE records, exporter profile, guards, owner checker (exactly `H5_V_identity` newly false),
H5-tw identities and the per-cut bridge.

| word | base | full deferral | ideal split |
|---|---:|---:|---:|
| PR1062 | 11,500 | 11,070 | **11,067** |
| PR1188 | 10,492 | 10,062 | **10,059** |
| PR1040 | 11,780 | 11,348 | **11,345** |
| PR1868 absorbed PR1188 | 10,489 | 10,059 | **10,056** |

F, B and the guard bits equal the full-deferral values. They match the counts an independent pre-PR reviewer found.

Full deferral remains the headline construction, because its contract is the cleanest (`R = E`,
`V = E^-1`). The ideal split is a refinement under the same lemma. It was found by search, and no
optimality is claimed.

## Committed instances

[candidate-1062.json.gz](candidate-1062.json.gz) and [candidate-1188.json.gz](candidate-1188.json.gz)
are the fully deferred PR1062 and PR1188 words. They are canonical JSON, gzip mtime 0, rebuilt
deterministically by `verify.py --write`. The verifier requires the decompressed payload to equal
the rebuilt word byte for byte. The gzip containers are also byte-identical under CPython 3.12.15.
They differ under 3.14.8, as CONTRIBUTING.md anticipates, while the payloads still match. The
ideal-split words are rebuilt in memory and pinned by SHA-256 in EXPECTED.json.

## Selected-word heuristic (PR589)

PR589 has no target basis, but a scatter basis G fits the same contract, with `R = G` and
`V = G^-1`. G comes from a minimum spanning tree over the scatter rows plus a zero root, with edge
cost `2 + Hamming distance`. It has 79 transvections, placed after the D reads at the zero frame, and
`G^-1` runs first in B.

The scatter-related cost falls from 527 to 412 (158 basis gates plus 254 listing ones), and the word
from 24,305 to 24,190 ADDs. The same checks pass:

- boundary, frames and exporter profile;
- guards: 93/177 bits, unchanged, while the reverse bound B rises from 1,113,070 to 1,117,988;
- H5-tw identities and the bridge to PR589.

PR589 itself passes every owner flag, so here three flags become newly false:

- `H2_D_frame0_targets_from_helpers` and `K_equals_D`: the lineage's syntactic departure, caused by
  target gates in D;
- `H5_V_identity`.

**This is a heuristic, not an optimum, and no supplier change is proposed.**

## Controls

The PR1062 and PR1188 instances carry these controls. All must fail or be rejected.

1. **Deferral with the old listing S.** The dirty endpoint is wrong on all 111 targets, and
   `J = I` and `V N = K'T` fail.
2. **Undo moved after B[0]**, the first B climb of an undo operand. The frame replay rejects it:
   register 111 would descend from frame 127 to 0. With frames ignored, the endpoint is wrong on 28
   targets.
3. **First undo gate dropped.** The endpoint is wrong on 6 targets; `V R = I` and `V N = K'T` fail.
4. **Reordered undo.**
   - *Preparation order instead of its reverse:* the endpoint is wrong on all 111 targets, and all
     three target equations fail.
   - *Adjacent swaps (honest census):* 305 per instance. 270 swap commuting gates and keep the
     operator; a checked one keeps the boundary exact. The other 35 change the operator; the first
     (gates 7 and 8) breaks the endpoint on 24 targets. So the order matters only through the product
     `E^-1`.
5. **One wrong `E S` row** (row 1, bit 0 flipped). The endpoint is wrong on 6 targets.
6. **Corrupted source pin.** The SHA-256 check rejects it.

**Check-level controls.** Each must be rejected by the intended check, which is matched by its error
message.

| check | control (per instance unless noted) |
|---|---|
| bridge structure | the deferred word with its last D gate dropped |
| bridge invariant | the old-S word |
| bridge, undo complete | the swapped-undo word |
| owner delta | `(base, base)`, which has no newly false flag |
| frame paths | a legal frame raise of B[500], frame 508 → 422 |
| paid profile | the same raise, which also changes the profile |
| exporter profile | the base word's exporter profile against the raised profile |
| maximality | the census run with the deferred word as its own base |
| precision guard (once) | the PR941 floor-calibration base word, 193 nine-stage bits |

**Mutation run.** We ran 26 mutants of copies of the verifier (not shipped). Disabling the body of
any check (guards, paths, profile, exporter profile, owner delta, bridge invariant, bridge structure,
undo completion or maximality) now makes the verifier fail.

Six mutants still pass:

- **Call-site removals (2).** One drops the base-word guard call; the other forces the owner delta.
  Their outputs stay pinned in EXPECTED.json.
- **Equivalent mutant (1).** Changing `<` to `<=` at the guard caps makes no difference, because no
  word sits exactly at a cap.
- **Redundant pins (2).** Removing the review-number pin, or the F/B-equality check, for the ideal
  splits is covered: those values are also pinned in EXPECTED.json.
- **gzip mtime (1).** A changed gzip mtime passes, as CONTRIBUTING.md requires.

## Reproduce

From the repository root (standard library only; about 40–95 s per run on an Apple-silicon Mac,
depending on the interpreter):

```sh
python3 -I -B research/r439-deferred-target-basis-seed06/verify.py
python3 -I -O -B research/r439-deferred-target-basis-seed06/verify.py
python3 scripts/research_package.py --package research/r439-deferred-target-basis-seed06 --check-only
python3.12 scripts/research_package.py --package research/r439-deferred-target-basis-seed06
```

The expected final line is:

```text
PASS_R439_DEFERRED_TARGET_BASIS words=19 outside=8 instances=2 ideal_splits=4 columns=661 controls=33 no_new_kappa (… s)
```

All 29 inputs are pinned by SHA-256 and git blob in [SOURCES.json](SOURCES.json): 27 words, the owner
checker and the exporter. The verifier refuses drifted bytes.

- **Owner checker.** It runs from its verified bytes in-process. It raises its own `Reject`, not
  `assert`.
- **Exporter.** It runs from its verified bytes in a child interpreter without `-O`.
- **Checks.** They raise `ValueError`, so `-O` cannot weaken them. The report must equal
  EXPECTED.json exactly.
- **Portability.** The report is identical under CPython 3.12.15 and 3.14.8.

`--write` regenerates EXPECTED.json and the two payloads. `--census-scan` repeats the word census.

## Task and scope

The card is `bit-helper-contract` (scope key 3475f46c8358c6a9211b), and the scope status is
**changed**. The card asks for an H2/K replacement for a helper operation. This package also relaxes
H5 (`V = I`), which the card keeps, and its object is the target-basis block, not a helper operation.
It also broadens to every committed lineage word, instead of narrowing to one helper-star instance as
the card's allowed variation suggests. TASK.json records the full reason.

## Scope and limits

- **The new result.** It is the interface lemma H5-tw with its converse, the argued cut-by-cut
  bridge, the maximality census among prefix splits, the order-ideal refinement and the finite
  instances. The ADD savings are finite consequences. They do not change the paid profile, the
  selected moment or κ.
- **Scope of maximality.** It is proved for fixed ordered frame paths and prefix splits of the literal
  undo order. If paths may change, `verify.py` counts the other targets that could be co-located at a
  B target write's frame, under three criteria:
  - *loose upper bound* (the target's final frame contains the write frame): 102 of 213 writes, up to
    58 targets;
  - *with the target's current frame inside the write frame:* 102 writes, up to 55;
  - *monotone through the target's own fixed touches:* 94 writes, up to 7.

  Any such move changes that target's path and the paid profile, so it is not covered.
- **Not run.**
  - Native 5/9/11-stage C++ replay and hosted emission/invoice were not run on the deferred words.
    For the deferred PR1122 word, PR1806's PR1122 nine-stage hosted-invoice replay is the obvious
    route.
  - The undo now sits in B's exporter phase rather than D's, and any phase-specific expectation of
    those tools is unchecked.
  - The all-size compiler, common-label/mutable-source realization, rounding/tape and analytic
    obligations remain inherited.
- **Adoption.** Whether H5-tw becomes the interface is a maintainer decision. The owner checker's H5
  is literal, and it flags every deferred word.

## Related and concurrent work

- **PR1704** (Ross Richardson, merged, `research/bit-two-copy-scatter`) is the nearest construction.
  It rewrites the same 527-ADD scatter of PR1062's word, using two simultaneously live COPY
  temporaries under a replacement copied-workspace contract, and reaches 527 → 407.
  - It is a different mechanism, under a different interface: this package keeps one temporary and
    the inherited COPY/ERASE contract. PR1704's README explicitly excludes target-basis changes.
  - **The two savings are not additive.** Both rewrite the same block. After deferral the scatter has
    97 ADDs, and PR1704's −120 was computed on S, not on `E S`.
- **PR1194** (woklerx) and **PR1868** keep `R = V = I`. This package keeps their D-shape and cleanup
  clauses, replaces the target-basis pair by `V R = I` and generalizes K to `V N = K'T`.
- **PR794** (commdata2338, open) is R420 target-basis compensation. Its preparation, reads and undo
  all stay inside D, as in PR915, and it does not defer the undo.
- **PR2037** (commdata2338, open) routes R439 H2/K work through the retained semantic-D evidence.
- **PR1806** (mtpsl, merged) is the complete PR1122 nine-stage hosted invoice. It is the hosted route
  for the deferred PR1122 word.
- **PR1580 and PR1592** (Arham Tahir, merged) exclude terminal helper-star restoration and arbitrary
  terminal star compensation under fixed frames. They are the contrasting deferral results: those
  move helper restorations to the end, while this package moves a target-basis undo past A and the
  scatter.
- **Same-card and nearby work.**
  - Discussion #1166, cycle 18 (Cinna Davis, @1337isnot1337): a post-read one-gate star compensation
    run on PR1062's word, which was not pushed.
  - PR2033 (ToikY, open): a helper-sharing pair on PR1062's star word.
  - PR1913 (Adam Gall, merged) and PR1937 (Aaron Wang, open): helper-star absorption corrections.

  All of these are helper side.
- **PR1435** (woklerx) bounds late mixing of the retained totals before the COPY by its paid COPY
  frames. That is helper side, not target basis.
- **Overlap search.** `gh pr list --state all --search` was run for: scatter, "target basis", H5,
  V_identity, "deferred undo", 10,062, 11,070 and "twisted target". It found no PR that defers the
  undo or lists the scatter in the target basis. The last five terms returned nothing relevant.
  `scripts/find_overlap.py` with "deferred undo", "H5_V_identity", "twisted target" and "deferred
  target" returned no matches. This is not a novelty certificate.

## Open next questions

The structured versions are in [TASK.json](TASK.json).

1. **A joint basis for the reads and the scatter.**
   - *Why it matters:* E was chosen by PR915's application of PR794's greedy search, for the D reads
     alone. Once the undo is deferred, the same basis also prices the scatter (`nnz(E S)`).
   - *First step:* add `nnz(E S)` to that search's objective, under the same prefix guards.
2. **A shorter circuit for `E^-1`, and better order-ideal splits.**
   - *Why it matters:* maximality fixes where target-from-target gates may run, not the circuit for
     `E^-1` or the best split. The ideal search is exhaustive only up to size 4.
   - *First step:* resynthesize `E^-1` at the zero frame with a bounded linear-circuit search, and
     extend the ideal search (larger sizes, or a joint split and resynthesis).
3. **Composition with other rewrites.**
   - An exploratory probe suggests the deferral also composes with a shear-descent D rewrite, but no
     number is claimed until it is verified.
   - Whether a two-copy pairing in the style of PR1704 still pays on the 97-ADD `E S` listing is
     open.
4. **Native and hosted replay.**
   - *First step:* run PR1188's native checkers (or PR1902's audit harness) on
     `candidate-1188.json.gz`, or PR1806's hosted-invoice replay on the deferred PR1122 word.
   - *Blocker:* a host with Boost or PR1509's checked stand-in.
5. **An optimal scatter basis on PR589.** The MST basis is a heuristic, and an exact or better bound
   for this cost model is open.

## Credit

- **Target-basis lineage.**
  - Gareth Davidson (@bitplane): PR915 guarded target-basis compensation on R439, the E block this
    package defers; also PR926, PR941, PR1122 and PR1188, and the outside words PR904, PR952 and
    PR980.
  - commdata2338: PR794 (open), the guarded target-basis method and the greedy prefix-guarded search
    that PR915 transfers to R439.
  - Scott Woolsey Biggart (@swbiggart): PR713, the first restored target basis, on R420.
  - Sagar Thakrar: PR716, optimal disjoint R420 target pairs.
  - Dugongue: #476 and #478, the reversible donor-receiver target identity. The deferral stretches
    that identity across the scatter.
- **Lineage words.**
  - Sricharan Vagvala (@theon199): PR967 helper stars.
  - Ross Richardson: the PR923 frame-520 circuit inside the words; PR965 helper triples; PR936.
  - Aaron Wang (@navinor): the PR1015 B circuits inside the words; PR1127.
  - Sagar Thakrar: PR1062 and PR1868.
  - woklerx: PR1040 and PR1047.
  - Hanson Sun (@bbMisk): PR1449 and PR1221.
  - ToikY: PR1543 and PR1208.
  - Cinna Davis (@1337isnot1337): PR1709.
  - DreamingOfClouds: PR589 tuning, on eumemic's PR555 word, built on DreamingOfClouds' PR545
    punctured unit.
- **Interface and checkers.**
  - eumemic: PR543, the R420 word and the H1–H5 interleaved lemma in `research/e8-bit-r420`; PR555
    and its checker adaptation `xcheck_p.py`.
  - Zhihao Chen: PR425 (open), the scalar-interface lemma.
  - Mikhail R. Gadelha: PR686 (open), the first semantic D-boundary substitution.
  - woklerx: PR1194 semantic D.
  - Arham Tahir (@Arham-Tahir64): PR1311 bridge.
  - Dylan Crow: the exporter `export_records.py` (per its header, carried in eumemic's PR493
    package).
  - Hanson Sun (@bbMisk): PR1902 native audit of PR1868's words.
- **Nearest construction.** Ross Richardson's PR1704 two-copy scatter: a different mechanism, not
  additive with this one.
- **Review.** The pre-PR review found the order-ideal refinement, the bridge's reliance on the base
  word, and the missing check-level controls, all fixed here.

Prepared by Sagar Thakrar with substantial Anthropic Claude assistance (Claude Code, including
subagents for the exploratory probe, its independent checks, the pre-PR review and package assembly).
No independent human review. New work is Apache-2.0.
