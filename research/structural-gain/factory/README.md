# The packet factory bottleneck and an output-borrowing attempt

The current 16-helper factory per Hamming block cannot be reduced while retaining
its twelve face packets and monotone scalar frames. A cross-block output-borrowing
screen identifies 28 actual helpers that could potentially be replaced by output
registers, but the first exact partial-restoration attempt fails. This package
does not claim a new scalar word, helper reduction, paid profile, or exponent.

Prepared by Dominik Scholz with substantial OpenAI Codex (GPT-6 Astra) assistance.
The inspected packet modules and same-partition construction are from icekylinx's
PR531 `direct-delivery504-global` package, retaining its PR514/507/425 ancestry and
the original contributors' assistance disclosures. These are new experiments on
that construction, not a review of PR569.

Run the exact checks, including the literal partial inverse, with:

```sh
python3 research/structural-gain/factory/packet_plane_bound.py \
  --source /path/to/pr564/research/direct-delivery504-global/inputs/hamming \
  --out /tmp/packet-plane-bound.json
```

The script records both input SHA256 values. It uses explicit checks that remain
active under `python3 -O`. The retained receipt is `PACKET-PLANE-BOUND.json`.

## Why removing two factory helpers per block needs an architectural change

Every one of the twelve normalized packets has four nonzero source coefficients.
Their binary labels span its exact rank-three packet plane. The twelve planes are
distinct; every proper subspace of a plane contains at most two source labels.
The script checks these properties for all fourteen blocks. The resulting 168
planes are also distinct across blocks.

To create the first scalar row whose source support spans one of those planes, a
two-register addition must take place at that plane. A unary scale cannot create
the support. Both participating registers visit the plane. Since equal-rank
distinct planes are incomparable, a register with a nested sequence of frames
cannot visit two of them. Hence at least 24 registers are needed per block: eight
source registers plus sixteen helpers. The existing factory attains this count.

Producing two retained copies of every packet raises this bound to 36 registers,
or 28 helpers per block. With only two registers ever visiting a given plane, the
two incoming clean rows must be independent: each comes from a proper subspace
with at most two source labels, while their union must cover four labels. Invertible
two-register scalar operations cannot turn these two independent rows into two
copies of one packet. If the first packet leaves the plane, the remaining proper
row cannot create a second copy without another register entering. Thus a third
register must visit each plane. Globally, the factory and required second copies
already attain the resulting 392-helper lower bound.

This argument fixes the face-packet decomposition, its exact output planes and
the nested-frame scalar model. It permits different intermediate arithmetic. It
does not cover a different packet decomposition, nonmonotone frame transitions,
free use of output registers, or a scalar construction that avoids the two-copy
interface.

## What foreign output registers make possible geometrically

None of a block's own eight output hyperplanes contains any of its twelve packet
planes. Foreign outputs are different. A selected output coordinate must fit both
final hyperplanes of its two-output basis and every center frame that scatters
into it. Testing that stronger cap gives:

| Compatible foreign coordinates per packet plane | Packet planes |
| --- | ---: |
| 0 | 96 |
| 2 | 32 |
| 4 | 40 |

Each block has four late-retired factory carriers. Two are borrowed sources and
two are actual helpers. All 28 actual helpers admit an injective matching into
foreign output coordinates; the receipt includes the literal matching. Counting
all 56 carriers as removable helpers would be incorrect.

This is only a necessary geometric assignment. It does not account for the
center-cut ordering, the changed response to arbitrary output values, cleanup
of helper and source registers, or the output's later frame path. The current
selected scatter and target basis are held fixed in this test.

## A literal attempted partial cleanup

Take block `(0,1,2,3)`, module helper 17, and foreign output coordinate 28. After
the first forty module operations, aliasing that helper with the output gives:

```text
borrowed output = y28 + x68 + x71
register 23     = (x71 - x68 - y28)/2
```

The proposed partial inverse is legal at their common rank-two frame:

```text
register 23 += borrowed output / 2       # becomes x71
borrowed output -= register 23           # becomes y28 + x68
```

The exact execution retains the arbitrary initial `y28` column. It restores the
butterfly partner, but leaves `x68` in the borrowed output. The existing other
`x68` branches have already reached the rank-two frames `(448,24)` and `(454,30)`.
Neither frame can join the borrowed output while staying inside its permitted
cap. Reading a fresh copy of the original `x68` line would cancel the residual,
but introduces a replacement helper and cancels this raw one-helper saving.

This is an optimistic cut before any center mutations. In the actual schedule,
the late assembly and the output's earlier center scatter add constraints.

The broader exact screen asks whether *any* linear combination of the other
current register rows can clear the candidate's clean source contribution while
all donors fit the output cap. It checks each admissible helper/output pair at
the first-forty frontier and after the twelve face assemblies: all 160 checks
fail. Existing second face copies duplicate packet rows, so they cannot enlarge
the tested clean row span. The receipt includes exact elimination remainders.
This rejects restoration by additions from the retained rows with those donors
unchanged, not every circuit that changes donor rows or recomputes signals.

## The remaining concrete bypass

The 28-helper matching is still useful for a different scalar architecture:
retain part of the factory computation in foreign output registers as part of
their final desired values, instead of requiring those outputs to return to
their original values before their current loads. Doing that requires jointly
changing the output basis, the center injection and the subsequent delivery
word. The arbitrary initial output columns must be propagated explicitly and
the changed center injection conjugated by that output transformation. Its
actual frame increments and replacement work must then be charged.

A second possibility changes the face-packet decomposition itself, bypassing
the 392-helper bound. Simply rescheduling the existing 12-packet factory or
adding an uncharged reverse frame traversal does not supply either construction.
