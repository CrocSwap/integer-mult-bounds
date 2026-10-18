# Selected complex height ledger

**Result: a finite source certificate and a written conditional proof.** The
actual selected R480/T16 event stream fits PR #2287's common-grid height
allowance. This independently supplies the finite accounting premise requested
by PR #2327 in [discussion #2253](https://github.com/CrocSwap/integer-mult-bounds/discussions/2253#discussioncomment-18941636).
No discrepancy was found under the stated execution semantics. No new supplier,
production precision reduction or multiplication exponent is claimed.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

## Exact scope and result

The checker reads the pinned selected PR1094 archive directly. It does not
import PR2287's ledger, scalar-charge function or schedule checker. It accounts
for both 24,767-event local words, all 144 calls, the 482-event caller,
35,840 idle deadlines and 7,526 positive idle remainders. Per cover class:

- 3,566,448 local events and 32,256 external signed bridge ADDs;
- 510,662 recursive children, with unnormalized rank mass **1,041,408**;
- sufficient scalar-prefix charge **4,382,272**, below the predecessor's
  conservative **21,194,688**;
- 6,088 local monomial records with invertible binary address maps and unit
  quarter phases; maximum scalar shifts 16 forward and 7 backward.

The proof in [PROOF.md](PROOF.md) applies these actual counts to the unfinished
child recurrence. It explicitly includes completed-child height resets, the
initial remainder, scalar scratch, parked coefficients and shift extents. With
`s=1041408*Gamma`, `E=2^100000`, `B=s+E`, and `C0=2^210000`, it proves the
conditional bound `A(e)<=2Be` and the retained layer guard `<C0*d`.
This uses PR2327's credited primitive lemmas; it is not another proof of the
Horner technique or a new abstract recurrence formalization.

[RESULT.json](RESULT.json) records all counts, source member hashes, prefix-ledger
hashes, exact inequalities, finite controls and the coefficient witnesses.
The ledger represents the complete cover symbolically; it never enumerates
`O(73,2)` or executes the selected full payload.

## Reproduction

From the repository root, CPython 3.12, standard library only:

```sh
python3 -I -B scripts/research_package.py --package research/selected-complex-height-ledger
```

The registered replay runs normal and optimized verification plus the focused
integrity tests. Its main marker is:

```text
PASS_SELECTED_COMPLEX_HEIGHT_LEDGER local_events=3566448 children=510662 rank_mass=1041408 scalar_height=4382272 controls=10 conditional_no_new_kappa
```

Normal verification reads and compares the receipt without rewriting it.
Only `python3 -I -B research/selected-complex-height-ledger/verify.py --write`
regenerates `RESULT.json`. The verifier uses explicit checks even under `-O`.
The metadata/source-only check is:

```sh
python3 -I -B scripts/research_package.py --package research/selected-complex-height-ledger --check-only
```

Finite arithmetic controls apply all 332 distinct actual scalars to 2,324
signed dyadic SCALE cases and 6,972 ADD cases, inspecting every allocated
arithmetic temporary against exact rational bounds. Ten rejection controls
cover missing events/idle children, wrong native ranks, wrong dispatch,
unknown operations, unpaid padding, non-quarter phases, nondyadic coefficients
and improper live-family normalization. Eight focused tests also exercise
singular adapters, a changed bridge coefficient, missing idle dispatch,
source-byte corruption and typed receipt changes.
These finite tests support the source application, not an all-input or all-size
payload execution. The quantified argument is the written proof.

## Dependencies, independence and limits

Base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The selected scientific baseline remains PR1094 at
`0fc329d0bec93ca7cd288eaea1295172e8789810`.
Pending predecessors are pinned byte-for-byte:

- Jose Manuel's [PR2287](https://github.com/CrocSwap/integer-mult-bounds/pull/2287),
  `8c60765b5dea9d862b3b190d55da102a576031bf`: proposed interpreter and arithmetic.
- AAAmirinu's [PR2327](https://github.com/CrocSwap/integer-mult-bounds/pull/2327),
  `367a8539770166d3ccd555583b41e96097178a3e`: primitive prefix/shift lemmas and the handoff.

The advance claim is [discussion #2253, comment 18942782](https://github.com/CrocSwap/integer-mult-bounds/discussions/2253#discussioncomment-18942782).
The active [physical-monomial refinement](https://github.com/CrocSwap/integer-mult-bounds/discussions/2253#discussioncomment-18942629) concerns one actual PR2250 adapter; our local shape check does not duplicate that interpreter proof.

The source arithmetic is imported only as the subject of the finite coefficient
checks. The source-to-ledger reconstruction and rational oracle are separately
implemented. The exact source pins and Git blobs are in [SOURCES.json](SOURCES.json).
Native endpoint correctness, common-label realization, hosting, complete
physical dispatch, work/parking lifetime, row/tape/time admission and outer
transfer remain hypotheses or unchecked obligations. No Lean build, selected
cold replay, full selected payload or hosted CI is claimed. Author checking is
not independent human review.

PR2284's generic recurrence formalization and PR2341's generic tensor lift
address different implications. This account's earlier PR1421 reconstructs the
binary PR589 paid-rank invoice; this package studies the selected complex
arithmetic/recursive height boundary. It does not change any frozen predecessor,
selected record or existing replay.

## Open next questions

1. **Physical interpreter binding.** Does one actual selected native child,
   its monomial adapters, coefficient scratch and parking implementation meet
   the semantic hypotheses listed in PROOF section 1? This is the remaining
   bridge from the conditional height result to executed supplier precision.
   Coordinate with the active monomial refinement above; begin with one selected rank-one recipe and its complete return boundary;
   stop at a source-bound implementation or an exact discrepancy. The blocker
   is the missing complete physical interpreter, not a larger integer guard.
2. **Chronological height refinement.** Can a per-family ledger improve the
   global maximum bound while retaining all scalar scratch and child-return
   obligations? First replay one complete call with symbolic endpoint widths
   and compare it with the present coarse bound. This could clarify sufficient
   guard constants, but it cannot change the exponent on its own and should
   follow, not replace, physical admission work.

Structured versions and the full task scope are in [TASK.json](TASK.json).

## Credit

Jose Manuel (@jmbarrancoml) supplied PR2287's construction and arithmetic;
AAAmirinu supplied PR2327's primitive audit and requested the missing binding.
Gareth Davidson (@bitplane) supplied the earlier PR1282 prefix/Horner analysis.
The selected R480/T16 inputs retain the Rohan Arun, Jeremy Kothe, Hao Yan,
DreamingOfClouds/eumemic and broader supplier lineage recorded by the selected
review and the copied PR2287 NOTICE. No predecessor result is reattributed here.
The original notices and Apache-2.0 terms are retained. OpenAI Codex assisted
substantially with derivation, implementation, verification and writing;
no independent human review is claimed.
