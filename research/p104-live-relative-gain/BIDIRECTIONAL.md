# Rational circuits with 5,680 and 5,676 paid transfers

The 5,676-transfer circuit raises the rational crossing from [0.00388013644474, 0.00388013644475] in PR 7830 to [0.00389586937146, 0.00389586937147], a gain of 0.40547%. It uses the same 1,289 input and output charts as the 5,700-transfer circuit. Both exact passes check the map on every independent field. [Four-term quotient and replay](#the-four-term-quotient) · [PR 7830](https://github.com/CrocSwap/integer-mult-bounds/pull/7830)

## The 5,680-transfer circuit

The circuit has the same 1,289 independent inputs, output charts and scalar map as the 5,700-transfer circuit in this package. It changes the signals shared by 21 ordered chart pairs. Across the 48 calls, the number of paid occurrences falls from 282,816 to 281,856. All 52,512 productive occurrences keep their grades. The new rational crossing is between 0.00389323292306 and 0.00389323292307. Its lower endpoint is 0.2552% above the previous rational crossing and 0.3375% above the rational crossing in PR 7830. [Counts, chart pairs and crossing](BIDIRECTIONAL-RECEIPT.json) · [PR 7830](https://github.com/CrocSwap/integer-mult-bounds/pull/7830)

## How two signals can share a transfer

Let M be the required rational map. Let X contain the coordinates of inputs that start outside chart 3. For each scalar in the old circuit, compute two row vectors. The first, u, gives its coefficients on X. To obtain the second, z, apply the X rows of the inverse of M to the outputs. Propagate those linear forms backward through the circuit. The entries of z give the effect of a change in the scalar on the recovered X coordinates.

At a chart, let U and Z have one row for each incoming or outgoing scalar. A new local coefficient matrix K must satisfy both equations

```text
K U_in = U_out,       Kᵀ Z_out = Z_in.
```

These equations imply that the sum of the outer products uᵀz is the same on both sides. For example, two transfers with vector pairs (u,0) and (0,z) have zero total outer product. One transfer with pair (u,z) carries both directions. This replacement adds uᵀz to the sum on that link. The other links or boundary transfers at its two charts must account for the difference. At each changed chart, factor the remaining difference into outer products and solve the two equations for the local coefficients. The 21 changed pairs involve 28 interior charts. The word retires 31 old transfers and adds 11. [Exact chart list and transfer witness](BIDIRECTIONAL.json.gz) · [Chart pair inventory](BIDIRECTIONAL-RECEIPT.json)

At chart 127, choose the terminal rows to recover the protected coordinates. If the resulting trial map is F, check that M⁻¹F is the identity on X and has an invertible block on the inputs at chart 3, with zero blocks between these groups. Precompose the chart 3 encoder with the inverse of its block. The resulting circuit now has the required map on every independent input. These chart equations give a construction method. The replay checks the final circuit directly over the rationals in dependency order.

## Reproduce the result

```sh
python3.12 -I -B research/p104-live-relative-gain/verify_bidirectional.py
```

The witness stores differences from the supplied parent word. An `add` record gives the difference vector for its row. A `combine` record gives a linear combination of earlier literal difference vectors. Apply each difference to the corresponding parent row. Fresh transfers start with an empty row. After expansion, 1,445 rows have 199,225 changed coefficients. The checker reconstructs the dependency order and verifies the canonical SHA-256 digest.

The forward pass checks all 1,289 terminal rows with 24,268,860 rational scalar products. The smallest integer grid that contains each such product on integer basis inputs is 154113755636630124932500335624192000. The largest literal numerator or denominator uses 57 bits. The adjoint pass independently checks the 1,289 input columns with 86,265,205 terms. It also checks that each donor is at the correct chart and that each paid and productive move joins strictly nested charts. Outward bounds from integer square roots verify the two signs at the reported crossing and the strict decrease of the signed margin on [0, 0.004]. [Replay](verify_bidirectional.py) · [Receipt](BIDIRECTIONAL-RECEIPT.json)

## The four-term quotient

A second choice of 25 chart pairs at 34 interior charts gives an intermediate word with 5,678 paid transfers and 1,290 independent fields. In the transpose of this word, write each source at chart 127 as a variable x indexed by its original owner. Impose the relation

```text
x[1017] = -x[371] + x[946]/2 + x[970].
```

On this subspace, transfer 104455 equals the difference of transfers 98030 and 104472, and transfer 106 is zero. Substitute the difference at its readers and omit the zero term. This retires one grade-three and one grade-six transfer and surrenders the original grade-nine helper 1017. The additional independent field from chart 3 to chart 127 takes its public role number. The exported word realizes the original ordered map, including every independent terminal in that public layout.

The supplied delta goes directly from 5,680 to 5,676. It retires eight transfer records and installs four. Transfer label 105 is reused with new endpoints and an empty initial coefficient row. The exact replay expands 126,844 coefficient changes in 771 rows. It checks 25,106,153 forward products and 89,136,223 adjoint terms. The largest literal still uses 57 bits and the least common product grid equals that of the 5,680-transfer word. The complete 48-call tally is 281,664 paid occurrences and 52,512 productive occurrences. [Delta](BIDIRECTIONAL-QUOTIENT.json.gz) · [Receipt](BIDIRECTIONAL-QUOTIENT-RECEIPT.json)

```sh
python3.12 -I -B research/p104-live-relative-gain/verify_bidirectional.py --quotient
```

## Two independent helper splits

With the same 5,676 paid transfers, split helper 233 at chart 750 and helper 205 at chart 34. The first grade-nine job becomes grade-three and grade-six jobs. The second becomes grade-one and grade-eight jobs. Each new input is independent. At each cut, a local expression reads a linear combination of source fields. The injection replaces that combination with the new input in the remaining program. A basis change within the original source and return banks keeps the other fields independent. The journal gives the two covectors, their nonzero pairings with the source directions, the literal readers and the injection coefficients. [Journal](HELPER-SPLITS.json) · [Reconstruction](verify_split_helpers.py)

The word now delivers 1,291 independent fields. The forward check covers 25,038,131 products. The adjoint check covers 88,780,337 terms. The 48-call rational crossing is between 0.00389749436514 and 0.00389749436515. The full replay also checks the short scalar programs for the new 57-bit literals. [Split receipt](HELPER-SPLITS-RECEIPT.json) · [Complete application](APPLICATION.md)

## Open next questions

At κ = 0.00391884648 the rational margin is between −21.649081521691 and −21.649081521690. Another circuit needs more than 0.45102 per rational call. A further split must identify where the independent return can be read and where the second input can enter in time for its readers. [Binary and rational budgets](README.md#open-next-questions)

Ali Romman prepared the construction and replay with substantial OpenAI Codex assistance. The 48-call profile and parent come from Clear1nsight's PR 7830 and the preceding P104 constructions. [Pinned sources and attribution](README.md#reproduce)
