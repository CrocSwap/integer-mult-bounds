# Direct return for the marked Counter

One initial-ONE branch removes actual tape reads, writes and unit moves from
Nick Petalas's PR6495 cached decrement, preserving the complete private tape,
backing length, head, finished flag and cleanup. The even borrow path remains
literal. This answers6495's known-position return question; its earlier N-read
cached-terminator saving is credited prior work.

For a complete countdown from N>0, put c=ceil(N/2). The additional saving is

    reads=2c+1, writes=3, moves=2c+4; total=4c+8.

N=0 is unchanged. The branch uses fixed symbols and one existing boolean,
without decoding a cardinality or head position into host control. At oddx>1
it returns one step left instead of rewinding. At x1 it also avoids deleting
and rebuilding the already-correct ZERO/RIGHT representation. PROOF.md proves
whole-array state equivalence and exact all-parameter traffic differences.

The same replacement is executed in the complete retained linear-sign caller.
For M>=2,B>=1,S>=1, define

    K=B(4(M-2)+M*1_{S>1}),
    P=1+B+2B*1_{M>2}+K,
    C=ceil(B/2)+2Bceil((M-2)/2)+Bceil((M-1)/2)+Kceil(S/2).

Its additional complete-call saving is (reads,writes,moves)=(2C+P,3P,2C+4P).
Zero counters at M2 remain charged; the S1 literal copy shortcut is respected.
Constructors, finally cleanup, public-word arithmetic, payload traffic and
source-head returns are included in the primary full-source measured interval.
This is exact traffic in the pinned logical-tape ABI, not wall-clock speedup,
an optimal transducer or a physical machine/compiler/supplier admission.

## Evidence and reproduction

CPython3.12, standard library only:

```sh
python3.12 -I -W error -B research/marked-countdown-direct-return/verify.py
python3.12 -I -W error -B research/marked-countdown-direct-return/oracle.py
```

Repeat with -O. Strict defaults require the retained receipts; --emit prints a
candidate without overwriting files. Eleven exact source objects authenticate
before use. The primary compiles the seven declared runtime modules from those
same bytes in private import tables and changes only Counter.decrement. No
author scientific verifier is imported or replayed. All frozen originals remain.

All810 complete countdowns pass, including every intermediate private state,
padding, shrink-to-one, complete backing arrays, protected input and disposal.
N covers0..255 plus2^k-1,2^k,2^k+1 for k8..12; high-zero padding is0,1,4.
All252 actual complete source-caller runs pass for M2/3/4/5/8/9,B1/2/3,
S1/2/3/4/7/8/9 and two opaque payload patterns. Output bits and source-coordinate
observations, source/extents, ownership and closed Counter tapes are checked.

An independently written literal transition oracle imports no author or primary
program. It checks810 countdowns and252 direct caller-control simulations.
Root joins all810 old/new RWM totals and normalized final/closed states, and
all252 changed caller deltas, allocation/positive/odd counts and payload hashes.
Intermediate state hashes use different encodings and are not compared. The
oracle does not emit the primary source-coordinate trace hash. It does not
independently implement unchanged positive_extent/one_bit_suffix recognition,
Count setup or Arena/Unsigned absolute billing. Complete absolute caller totals
are primary source replay evidence; independent claims cover the stated shared
state/delta/payload projection. VALIDATION.md records exact receipts and history.

## Source, scope and credit

Base7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority8, selected6030 unchanged.
6495head9ba6f43b4d1da64e250f948a8e684011ef9fb0c6; seven runtime objects come
from canonical main. SOURCE-PINS.json retains all bytes/Git blobs/SHAs.
[Finding/handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19367016).
The local claim preceded experiments. A stale browser binding delayed the
public post; it was published as an in-progress finding after reconnection,
not represented as a prior public reservation.496openPR bodies and a fresh
latest100/source6495head/feedback plus currentHub were checked. Arbitrary diffs,
hidden/unpublished work and sparse history remain unknown. Related3611 uses
a different left-origin/top-digit ABI and is not this direct-return change.

Credit Nick Petalas6495 cached terminator/conformance; Arham Tahir2877 earlier
complete traffic invoices; David Arias2753 linear-sign algorithm; Jose Manuel
2697 Counter/tape library and all retained notices. ToikY with substantial
OpenAI Codex assistance and separate AI implementation/static review, Apache-2.0.
Separate AI review is not independent human or proof-kernel acceptance.

The exact model counts reads, writes and unit moves; it does not separately
price every Python or finite-control branch. The existing managed allocation,
exceptions and source loader model remain explicit. No native call, arbitrary
dirty-state restoration outside this contract, current supplier adoption,
precision/stock/compiler/outer admission or new kappa follows. All five selected
framework assumptions remain. Selected cold replay, Lean and Docker are unrun;
the selected frontier is unchanged.

## Open next questions

- Adopt the branch in one current complete ordinary caller with its physical
  control compiler. Freeze its exact ABI/aliases, then charge control, access,
  allocation and cleanup; historical conformance is not current admission.
- Examine one even borrow/top-marker return with a complete state/invoice
  comparison. Those paths are still literal and paid; no further saving or
  optimality is claimed here.
