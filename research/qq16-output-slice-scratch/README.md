# Reuse unproduced QQ16 output slices as owner-local scratch

PR2651 explicitly asks whether its sixteen owner-local scratch arrays can use
not-yet-produced Y output slices. This package supplies a **conditional allocation
refinement**: use W0 for the earlier C lifetime, then W0..W15 for F0..F7/G0..G7,
one owner at a time. Both scalar bodies finish before any W output is produced.
The maximum additionally allocated local payload arrays becomes **16 → 0**,
provided the caller supplies the exact writable-slice access contract below.

The result retains **224 owned full-cover output banks, sixteen early retained
values, 17,280 scalar primitives and all 448 native events**. No arithmetic,
native operation, required retained value or global bill is removed. This is
neither a memory minimum nor a favorable physical/supplier budget.

## The changed boundary

The caller supplies exclusive access to W0..W15 at the current owner, with the
same payload extent and component order as the original local scratch. Owner
slices are disjoint, ordinary scalar operations address that owner's slices,
and these outputs are unobserved until their normal construction. If providing
this view requires seeking, staging or extra buffers, those costs remain charged
and those buffers are outside the zero-additional-scratch conclusion.

Owned W contents may be **arbitrarily dirty and disposable**. There is no
zero-initialization assumption: the original first scratch CLEARs and every
later output CLEAR remain. The caller must not promise preservation of W entry
contents. All 224 borrowed X/Y current inputs preserve their arbitrary contents
and physical frames exactly. Borrowing an input field instead of an output is
illegal. No frame conversion is assumed free for nonzero data.

[PROOF.md](PROOF.md) proves the owner-local simulation and then its whole-cover
consequence by disjoint-owner commutation. In the pinned source word, intervals
633..1066 and 1172..2125 contain only scalar instructions; the first W output
access occurs at 2127. Exact field aliasing, first/last charged CLEARs and future
discarding writes are checked. A full-cover bank is never identified with a
local array without this explicit slice-view premise.

Conditional on PR2651/PR2540's retained decoder/native contracts, the new word
returns the same 224 original logical arrays in **F_U1**, preserves both output
checkpoints and restores every current borrowed field. It does not restore the
original pre-F0 physical output frames. The 224 rank-one and sixteen rank-eight
children, mass352, 480 wrappers and 208 cover maps are unchanged. The inherited
F0/B1 history calls retain their own costs.

## Evidence and reproduction

The primary verifier authenticates source bytes before importing PR2651's
credited exact polynomial algebra and baseline interpreter. Its adapted replay
tracks actual W identities and forbids hidden private rows. It compares all
224 output operators over 240 temporal input symbols, borrowed restoration,
checkpoints, native events and the complete scalar invoice. Eight controls
cover alias collision, borrowed-input substitution, premature output use,
frame mismatch, missing clears, a native event inside a local body and a wrong
scratch source.

A separate JSON-only physical-bank checker imports neither implementation.
It executes scalar bodies owner by owner over 2,3,5 owners, comparing all 4,480
two-component output cells after 78,400 component updates. Native symbols use
explicit invertible noncommuting toy actions. A wrong-owner read fails. These
are allocation-equivalence checks, not an independent native-kernel proof.

```sh
python3.12 scripts/research_package.py --package research/qq16-output-slice-scratch
python3.12 -I -O -B research/qq16-output-slice-scratch/verify.py
python3.12 -I -O -B research/qq16-output-slice-scratch/check_owners.py
```

The registered integrity suite checks a Git-free export, source/candidate and
typed receipt corruption, and overwrite refusal. Windows sandbox users may
need writable TEMP/TMP. Default verification is read-only; `--write` creates
absent WORD/RESULT files only. Exact source provenance is in
[VENDOR.json](VENDOR.json) and [SOURCES.json](SOURCES.json).

## Open next questions

The revision-5 decision is **narrow and stop at this lifetime/access proof**.
An actual caller must implement the owner-slice view and compare complete
movement, retention, hosting, precision and output-consumer costs against the
original scratch allocation. Start with the two exact intervals and a concrete
bank/owner layout, recording every seek or staging allocation. That physical
access tariff is the blocker; unknown costs are not zero. No broader optimization
campaign, selected-frontier update or new kappa is claimed.

## Credit

Prepared by ywz65 with substantial OpenAI Codex assistance for proof, code,
testing, writing and separate AI review. PR2651 by commdata2338 supplies the
early-output-bank word and this explicit open question; PR2540/2511/2512 by
ywz65 supply the inherited complete decoder and native/logic work. Their
attribution to Ali Romman, starship-s, Sagar Thakrar, Ross Richardson and the
retained QQ16/supplier lineage is preserved in the unchanged source documents.
Storage reuse is standard; this source-bound access/lifetime refinement is the
new contribution. New material is Apache-2.0. No human or formal-kernel review
or selected cold replay is claimed.
