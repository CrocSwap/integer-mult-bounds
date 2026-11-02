# A fixed stock for changing selected-bit counts

This is a scoped tape-model construction with exact finite evidence. It extends
Open next question 1 of unpaidmoon's [PR6342](https://github.com/CrocSwap/integer-mult-bounds/pull/6342).
The one-round program and arithmetic return in unpaidmoon's PR4127 are premises.
Neither predecessor's scientific suite is replayed or audited here.

## Contract

Fix a matched layout, precision `p`, record count `M`, and coefficient count `r`.
Each invocation uses the cited program's physical source order and a permitted
height. Its selected-bit count `g` may change between invocations. Set

```text
w = p + 2
g_max = maximum selected-bit count over the layout's permitted heights
W_max = p + g_max + 2
C = 2 M r w
S = 2 M r W_max
```

The source packet is a new external presentation at each invocation, just as in
the one-round API. It is borrowed unchanged during that invocation. The previous
root and consumer packets may be discarded before the next presentation.
No diagonal or output-to-input transition is supplied. Retained host snapshots
in the verifier are observations, not additional tapes used by the construction.

The construction allocates seven physical bit arrays once:

| Tape | Capacity |
|---|---:|
| source | C |
| scratch | S |
| root | C |
| consumer | C |
| low | S/2 |
| high | S/2 |
| paired | S |

Thus its simultaneous allocated tape stock is exactly

`3C + 3S = 6 M r (w + W_max)`.

This is an upper bound achieved by this allocation, not a minimum over different
tape programs. Python objects, receipts, diagnostic scans and scalar control
storage are outside this bit-tape model. A complete machine lowering would have
to price its own control representation.

## Prefix simulation

In a round with count `g`, use `W_g = p + g + 2`. The source, root and consumer
retain length `C`. The other four arrays expose only the same prefixes requested
by the one-round program: `2Mr W_g` for scratch/paired and `Mr W_g` for low/high.
Prefix indexing rejects positions beyond that logical length. No cell is moved
when the logical length changes.

Maintain these invariants at a round boundary:

1. All seven physical heads are zero.
2. Scratch, low, high and paired are blank across their entire physical capacity.
3. Root and consumer contain only the most recent output, and source contains
   the current or previous borrowed presentation.

They hold initially. Before a later round, blank the two output tapes. Present
the new borrowed source in its unchanged packet width. All active prefixes then
have the same starting bits and heads as the one-round program. Every tape read,
write and seek has the same address, value and charged distance. No instruction
uses an inactive cell. The existing one-round return therefore yields the same
output packets and charged operation ledger.

The one-round program creates low, high and paired inside each selected-bit
iteration, and blanks and homes all three before returning from that iteration.
Consequently the same physical arrays can serve its next selected bit. Their
diagnostic counters restart at each allocation request, as fresh objects' counters
would, before the original program folds their charges into scratch. Restarting
these counters changes no physical bit and removes no operation from the ledger.

Each returned work prefix is blank, and its inactive suffix was blank and was
never accessed. Thus the entire physical work array is blank. Heads return to
zero, proving all boundary invariants and completing induction over any finite
schedule in the stated contract. This simulation is the proof; the finite
comparisons corroborate it rather than prove it for every layout.

## Reset charge and first witness

Blanking one length-`C` output at head zero writes `C` bits, reads none, and
travels `2(C-1)` cells. Resetting root and consumer therefore adds exactly
`2C` writes and `4(C-1)` moves between rounds. These charges are separate from
each unchanged one-round ledger. Presentation and source preservation use the
same convention as the cited one-round API.

For `ell=3`, flags `(True, False)`, `k=1`, `p=4`, there are `M=32` records,
`r=8` coefficients and selected counts one and two. Hence `w=6`, `W_max=8`,
`C=3072`, `S=4096`, and the stock is **21,504 cells**. The exact first witness is:

| Round | g | Reads | Writes | Moves | Gates |
|---|---:|---:|---:|---:|---:|
| h=2 | 1 | 24576 | 38400 | 125876 | 19776 |
| h=1 | 2 | 48128 | 71680 | 239476 | 28288 |

The intervening reset adds 6,144 writes and 12,284 moves. Both round outputs,
their actual root/consumer bit packets, borrowed source and complete one-round
ledgers match fresh calls. No κ or selected-frontier change follows.

## Executable bounds and remaining obligations

The executable accepts at most sixteen rounds, `2 <= ell <= 4`, one to three
Boolean axis flags, `1 <= p <= 16`, valid `k < ell`, at most nine address bits,
and at most `2^20` total tape cells. Its geometric count gives at most three
selected bits. These bounds constrain all new schedule and prefix loops.

Finite verification uses five schedules comprising fourteen rounds, including
both directions of the width change, repeated width changes, two chunk widths,
precision one and a one-to-three selected-bit change. Eleven rejection controls
cover prefix bounds, inactive dirt, invalid allocation state, invalid schedule
and layout, input bounds and restoration of the module binding after failure.

The adapter temporarily replaces `Tape` only in its privately loaded engine
module. Execution must be serial, and a `finally` block restores that binding.
No global import or shared repository module is patched. Python still allocates
control objects and verifier snapshots dynamically; only the seven bit arrays
are fixed. Explicit source-byte compilation is limited to the two named modules,
with the external engine checked against its SHA256 before execution. These are
the scoped managed-runtime and dynamic-loading deviations from Power of Ten.
All new functions are under sixty lines; invariants use checks that survive `-O`.

General physical lowering, retained-output storage, the framed diagonal,
production-size execution, the five selected framework assumptions and a
complete multiplication theorem remain unresolved. No Lean or Docker replay
or selected cold replay is included.

This construction, proof and verifier were produced by Nick Petalas. Credit
unpaidmoon for PR6342's stock question and scheduler and PR4127's one-round tape
program; Chris R / Clear1nsight for PR3623's matched layout and tensor; Sagar
Thakrar for PR3617's diagonal contract; and the PR3493, PR3593, PR3599 and PR3611
lineage retained in the one-round source. Apache-2.0.
