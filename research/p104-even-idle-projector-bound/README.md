# Type B even-idle projector bound on the signed P104 caller

**NO VERIFIED GAIN. Exact conditional κ change 0%.** On the exact
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
17-stage caller reused by [#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277),
no two Type B even IDLE_ONE jobs with disjoint masks can be replaced
by one grouped one-role idle with their union. The exclusion covers
insertion at any clock and role. Every other caller event and the
native word stay fixed.

The singleton gate checks all 544 distinct-stage pairs among
34 singleton-mask jobs. The complete gate checks all 1,348
disjoint-mask pairs among 60 even IDLE_ONE jobs, including the
same 544 singleton pairs. The independent exact rational replay
finds different prefix-conjugated projectors at both signed
unit-body probes for every pair. Zero cases survive or remain
unresolved.

## Exact price and support

The primary replay reconstructs the complete signed #7277 invoice
with 17 native copies, 110,536 paid positions and 22,461 productive
fields. It saves every directed price before testing support. The
retained grouped idle interface charges rank 8 times the mask
size. At equal field volume, a pair of old ranks r and s has
optimistic signed credit `8(Hᵣ + Hₛ − Hᵣ₊ₛ)` across the eight
Type B ports. Hᵣ is the retained tariff at the exact old crossing
upper. The price-only credit for a singleton pair is about
0.3206061111022773 raw units. There are at most 17 disjoint
singleton replacements, giving a whole-stock upper of about
5.450303888738714.

For all masks, the replay prices 35 rank signatures. Each event
is assigned its largest incident upper credit. Half the sum of
these event weights bounds any disjoint selection, because each
selected pair uses two distinct events. The complete optimistic
upper is about 35.71990804514672 raw units. These upper bounds
grant original field volume and free additional work. The exact
rational prices and paid histograms are in the emitted receipts.
Both bounds fall to zero after support.

At body one, the removed and inserted even idles are identity.
The [derivative proof](PROOF.md) compares the two normalized
derivatives for one variable from each disjoint mask. A one-role
replacement has the same projector for both derivatives, which
forces equality of the two original projectors at either q sign.
The primary replay certifies off-axis nonzero components modulo
65521. The independent replay recomputes full rational prefixes,
their inverses and the original endpoint at q = ±1. It confirms
every primary exclusion at the indicated sign. Controls cover
a role-changing coordinate swap, a separating shear, overlapping
masks and the event-weight upper bound.

The scope covers one replacement, with no simultaneous change
to the retained J blocks, QUERYs, odd idles or other scalar events.
Repeated stages, a changed carrier volume, a multi-role replacement
and changes to the surrounding caller require separate evidence.
The complete comparable witness remains κ = 0.003645669928698.

## Replay

From a clean checkout with CPython 3.12 and assertions enabled:

~~~sh
python3.12 -B scripts/research_package.py --package research/p104-even-idle-projector-bound
python3.12 -B scripts/check_research_commit.py --package research/p104-even-idle-projector-bound --check-modes --check-source-history
~~~

From a Git-free export, this also emits all six complete receipts
into a fresh directory:

~~~sh
python3.12 -I -B research/p104-even-idle-projector-bound/replay.py --out fresh-receipts
~~~

[PROVENANCE.json](PROVENANCE.json) pins seven public inputs by
commit, path, Git blob and SHA-256. [LOCAL-PINS.json](LOCAL-PINS.json)
pins the bundled replay closure by package-relative path. The
replay verifies all six deterministic plaintext receipts against
[SHA256.json](receipts/SHA256.json). [SUMMARY.json](receipts/SUMMARY.json)
contains the exact pre-support uppers and closed counts.
Only the standard library is required.

## Credit and relation to earlier screens

[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at
`07a76c5e2738882c0cb322278e56f6cae3c9885d` supplies the signed caller
and grouped-idle physical interface. [#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277)
at `ed090b57ed88f8859e5ff4643645099e6ba856ea` supplies the native
word and complete comparable invoice. [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)
supplies the retained directed tariff and known-good invoice control.

[Discussion #7111](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111)
reports an earlier fixed-caller conjugacy screen of 1,984 pairs and
the common-cut projector criterion. Its local proof pins the older
signed caller with SHA-256
`9557f713ab4ffb91ede05e8a6d5668c694b9940fc16f2f2d657e2f2b2cac2d3f`.
The matching [#7108 caller retained by #7113](https://github.com/CrocSwap/integer-mult-bounds/blob/07a76c5e2738882c0cb322278e56f6cae3c9885d/research/signed-caller-8x9/replay/supplier7108/CALLER.json)
has 256 Type A disjoint pairs, 1,536 Type B even-even pairs and
192 Type B odd-even pairs when its four odd-odd pairs are excluded.
This count and digest identify the earlier 18-stage stock.
Earlier local analysis of [#7003](https://github.com/CrocSwap/integer-mult-bounds/pull/7003)
and [#7002](https://github.com/CrocSwap/integer-mult-bounds/pull/7002)
used unit-body derivative projectors for other fixed-HOST bounds.
The present certificate replays the exact 17-stage Type B stock
with complete signed pricing and independent rational checks.

[#7144](https://github.com/CrocSwap/integer-mult-bounds/pull/7144)
supplies the related diagonal-gauge rigidity result,
[#7295](https://github.com/CrocSwap/integer-mult-bounds/pull/7295)
the fixed-contact idle-capacity bound,
[#7296](https://github.com/CrocSwap/integer-mult-bounds/pull/7296)
the one-child displaced-volume bound for an odd/even pair, and
[#7305](https://github.com/CrocSwap/integer-mult-bounds/pull/7305)
the BIT arbitrary-slot analogue. OpenAI Codex and subagents
materially assisted.

## Open next questions

Can a multi-role grouped operator preserve both distinct normalized
projectors at a favorable complete price? Pin one changed child
action and its field-volume tariff. Bound compatible savings across
the full signed invoice before attempting a literal construction.
A surviving proposal still needs exact signed arbitrary-input
action, ownership, restoration, precision and tape checks.
