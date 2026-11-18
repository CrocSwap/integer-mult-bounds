# The 226/990 courier on the original 74 erasures

## Word and protected interface

All clocks below are zero-based positions in the 76,673-event source from [#7645](https://github.com/CrocSwap/integer-mult-bounds/pull/7645), head `8ee7e6869b57ce445dbebd1d720366eab1f8ca40`. Its decoded SHA-256 is `6c52b2fba7c20343a50cb92ed4b997aa9921c78f212ac6428d13fff2bcd014cf`. The candidate has the same length and decodes to `450c7e544efb5258c4b8b4858b49cbd7482d14f206cdda1a71833fc73343ac66`. The expected bytes are checked after reconstruction from pinned source. Unchanged headers bind the 1,501 public registers, 68 owned register labels, start and end charts, and fixed target/caller interface.

[#7617](https://github.com/CrocSwap/integer-mult-bounds/pull/7617), by DreamingOfClouds, proposed two couriers on SYLforge’s 113-lifetime #7616 word. This package transfers the 226/990 courier to the original 74-erasure word. The earlier #7645 joint main-46 and 82/185 corrections remain part of the source. The distinct 134/329 experiment announced by #7647 remains under its own coordination.

## Literal edits

| Source location | Candidate operation |
|---|---|
| After 41465, before 990 leaves 719 at 41466 | Keep the subtraction of the old 473 from 990 first. Advance the original 41470 MOVE of 226 from 260 to 719 and its 41471 addition to 473. Then subtract 226 from 990. |
| 41467 | Retain the addition of half of 931 into 990 at 907. |
| 43515–43517 | Retain the addition of half of 990 into 166. Delete the 719→907 MOVE of 226 and the subtraction of half of 226 from 166. |
| 45736–45740 | Preserve the unrelated MOVE of 1477. Before 1477 reads 226, move 990 from 907 to 127, move 226 directly from 719 to 127, and add 226 back into 990. Keep both original reads at 127 in order. |

The script checks each replaced event, including its chart, sign and operands. The combined edit map reconstructs the same candidate separately in the #7605 coordinates used by the native application. It preserves the charged source paths and their attributions.

## Arbitrary-input identity

Let $X$ be the value in 226. Let $Y$ and $Z$ be the initial values in 990 and 473 at the contact at 719. Write $Q=Y-Z+R$, where $R$ is the later contribution of half of 931. The initial subtraction uses the old $Z$ in both words. Upon completion of the advanced corrections, 473 has the same value $Z+X$ and 990 carries $Q-X$ at the consumer in the successor. The source carries $Q$ there. If 166 initially contains $W$, its source adds $Q/2$ and then subtracts $X/2$. Its candidate adds $(Q-X)/2$ once. The source’s intervening MOVE has no scalar read of 166. At 127 the candidate restores 990 to $Q$ before its next sensitive read. Register 226 carries its original $X$ throughout.

The early write to 473, encoded interval in 990, and interval between the source’s two writes to 166 each require their own observation check. Literal co-location, all 630 ordered private or COPY observations, all 74 ordered erased values and every final public input coefficient are checked against the pinned word. The separate rational interpreter reconstructs register trajectories and labels from the two words without consuming the constructor’s alignment map.

A price-preserving control reverses the order of the read of old 473 and its update by 226, with both operands cocharted. It leaves the full invoice, all 74 erasures and all 630 protected observations equal. It changes 65 public rows. On unit input 2, the coefficient of output 17 changes from 0 to 4. The separate wrong-sign control changes that coefficient from 0 to −8. Decoding before the courier arrives fails chart legality. [Ordering control receipt](independent/ordering-control.json)

## Complete moment and ceiling

The old 719→907→127 route has dimension increments 1 and 2. The direct 719→127 transition has increment 3. The signed 17-call paid histogram therefore changes by $-17$ at rank 1, $-17$ at rank 2 and $+17$ at rank 3. The full application derives the histogram from the actual word and caller. Paid positions fall from 110,298 to 110,281, with 22,461 productive positions and the other invoice terms fixed. Strict subadditivity gives $3^t<1+2^t$ for every $0<t<1$. Directed decimal and dyadic interval calculations also put the source and candidate on opposite sides of the proposed public gate.

The old crossing is about 0.003652118209307584843. The new crossing is about 0.003652423811866664780 and bounds this fixed invoice from above. The conservative public gate 0.0036524238117 leaves approximately $1.66665\times10^{-13}$ of headroom. Its improvement over #7645’s public gate is exactly 0.0000003056025. Increasing this invoice’s crossing requires a different paid or productive profile or a newly justified change of contract.

## Physical and universal scope

The native application replays 2,959 chart pairs on the modular physical word. Its separate affected-pair checks examine all 512 forward and 512 adjoint columns, their absolute Gaussian phases, and all five route compositions, including 719→907→127. The extra phase check distinguishes a globally rotated operator even when its action on signed Pauli coordinates agrees. The signed application checked 3,044 catalogue maps, 104 main boundary pairs, the ordinary and precision/tape bills, and the 54 strict and four functional outer predicates on the candidate word. The five inherited premises cover all-column operators and spectators, ownership and erasure, the uniform compiler, uniform precision and fixed tape, and analytic recovery. The receipts give finite evidence under these premises. Independent maintainer review remains the admission decision.
