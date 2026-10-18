# Research record

The assigned route was to integrate the paid P111 shared-carrier decoder from
PR1060, or to prove an exact obstruction to a substantial integration class.
The source head was `d27499553138bde007f5b1163e65e71da1b18899`. The cost-63
algebra was already known. It was not a new result of this work.

## Three candidates

1. Put the complete paid decoder into the existing nine-call owner geometry.
2. Restore centres and use helpers earlier, so that their endpoints need less
   owner space.
3. Reuse the existing U8 gather rows for the changed query, while retaining
   the old side-correction word and its helper contracts.

The first candidate has an immediate narrow problem. PR1060 has 449 active
helpers, each ending at dimension nine in its literal word. Nine calls need
4041 width-9 helpers per replica. The P111 owner bins can hold at most
`444*(floor(16/9)+floor(32/9)+floor(48/9)) = 3996` such helpers. The three
inactive helpers were already omitted in this comparison.

This count is not a general obstruction. A centre can be restored at its
query frame before its source helpers leave. Thus the centre can end at
dimension eight. Source-use cleanup can also become earlier when the source
visits a suitable query frame. These endpoint changes defeat a simple
argument based only on the literal width-9 helper count. No complete hosted
word was obtained from that candidate.

The third candidate had a stronger exact test. The old U8 word has a paid
side-correction path. Reusing its clean rows could avoid a second independent
helper module. We tested every root puncture at the end of A. The unique
expressions and fixed future frames then gave the antichain obstruction in
`PROOF.md`. The full favorable invoice still fails after using each actual
removed data path. This is the completed contribution.

## Source reconstruction

Some committed `evidence/local` files in the U8 ancestry contain older R492
words. Those files are not the U8 word identified by the current source recipe.
The investigation did not use them as current receipts.

The checker reads only `native/jx/FULL-WORD.json.gz` from the pinned PR799
archive. It applies `RECIPE-U8.json` with the pinned `build_tri.py`. Both raw
content hashes must match their source pins. It then derives all rows and
frames from this fresh output. The raw and canonical label charts must not
be mixed. Every root-to-label pairing and every clean row's frame support is
checked in the raw chart.

## Completed domain and stopping rule

There is no random seed. The domain is all 112 possible extra punctures of
the fixed U8 root set. For each puncture, the check includes every nonzero
eligible row, rational independence, the unique query expression, every
required future-frame intersection, every pair of required frames, and the
complete relaxed moment. Coverage is 112 of 112.

The investigation stopped this branch when the exact lower bound exceeded
one in every case, after free preparation and pooled rank-48 owner space.
More packing search cannot improve that lower bound. A construction must
change a stated restriction. This is not a failed search presented as a proof
that every P111 route is impossible.

## Concurrent work

The open PR list was refreshed before handoff on 2026-10-13. PR1060 still had
head `d27499553138bde007f5b1163e65e71da1b18899`.

- PR1097, head `ad0cc538d7f827461da6364c3c0e09176b10bcae`, checks archived
  P111 fitting-matrix claims. It does not price this added U8 query.
- PR1115, head `c9d2523a3d30b8f6b16cf038bf723a191342ff20`, rewrites four
  U8 B fragments. A changed B word is outside the present source pin.
- PR1119, head `bc0140e016bd865fffc7fdf64e12158183d52339`, changes the
  full-frame U8 cleanup. Its description names the same raw U8 content hash.
  This provides a separate source identification, not proof of this result.
- PR1077 extends the complex eight-term copy-cost result to arbitrary complex
  coefficients. It does not supply the new query transport or owner cost.

No other result in that review supplied the exact row, future-frame, and
whole-owner inequality proved here. No new sprint issue was created. The
local `CLAIM.md` records the scope because the coordinator found no pinned
coordination issue.
