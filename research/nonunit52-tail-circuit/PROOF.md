# One reversible draw for the nonunit denominator-52 tails

## Result and contract

This package supplies a different tail controller for the 288 mixed and
96 endpoint source pairs excluded from the exact nonzero-pair core
interface in PR7757. One fixed circuit uses 1,277 gates and 382 clean
work bits per draw. It preserves the original ordered coin-to-label
function, continuing-node index and stopping depth after entry.

The circuit accepts two read-only parameters `1 <= u,v <= 12`, one
orientation bit and one mode bit. These are fixed before the first tail
coin. Its live packet contains a four-bit unit phase modulo thirteen,
a two-bit node/label field and a stopping flag. The resident coin is
preserved. The input stopping flag and high node bit are zero. Endpoint
mode permits only node zero; mixed mode permits nodes zero and one.
Only the stated pending packets are the semantic input domain.

No physical tape tariff, prefix implementation, first-entry return or new
kappa is supplied. The source first-entry boundary from PR7757 remains
unpaid. A full sampler must retain enough control to distinguish that
boundary from a later cyclic tail return.

## Exact source reduction

The original joint weights, in label order `00,01,10,11`, are

```text
w = ((52-a)(52-b), (52-a)b, a(52-b), ab),  0 <= a,b < 52.
```

At depth four, the unfinished digit streams have residues `w mod169`.
For the 384 pairs considered here, all nonzero residues are multiples
of thirteen. Divide each residue by thirteen. Their later binary digits
are exactly those of the resulting four numbers over denominator
thirteen. The old integer parts cancel in every digit difference.

If `a=13t`, where `t` is 1, 2 or 3, and thirteen does not divide `b`, put

```text
u = (4-t)b mod13,    v = tb mod13.
```

Both parameters are nonzero. The reduced row-pair weights are
`(13-u,u,13-v,v)`. If instead `b=13t`, use `a` in the formula and transpose
the two off-diagonal entries. These are the column-pair weights
`(13-u,13-v,u,v)`. Each vector sums to twenty-six, so it represents a
complete pool with two live nodes. It is not a fresh one-root probability
distribution.

If `a=0` and thirteen does not divide `b`, set `u=4b mod13`; the reduced
weights are `(13-u,u,0,0)`. If `b=0`, use `u=4a mod13` and weights
`(13-u,0,u,0)`. These endpoint pools have one live node. The source recipe
sets the unused parameter `v=u`. The circuit also permits every other
nonzero `v` in endpoint mode and charges its arithmetic.

The counts are `2*3*48=288` mixed pairs and `2*48=96` endpoint pairs.
The checker validates every one against the pinned actual inverse mode
columns, with a public owner witness in `{-1,0,1}^112`. It compares all
16,128 source-tail transitions over a complete period with a direct
integer-floor calculation using denominator 2,704. The sixteen dyadic
pairs have no tail, and the other 2,304 pairs use the different core
interface; neither class is accepted by this source recipe.

## A constant live-pool controller

The twelve powers of two modulo thirteen are distinct and return to one.
At phase `theta`, define

```text
du = 1 if (u*theta mod13) >= 7, otherwise 0,
dv = 1 if (v*theta mod13) >= 7, otherwise 0.
```

For a complementary pair `(13-u,u)`, the two probability digits are
`(1-du,du)`. Neither residue is zero. Thus each complementary pair gives
exactly one leaf at every step.

In mixed mode there are two leaves and two continuing children per step.
Node zero always stops: its coin selects the first or second ordered
leaf. Node one always continues: its new node is the coin. Row-pair
leaves have high bit equal to the coin and low bit selected from `du,dv`.

For column pairs, the two candidate labels are `2*du` and `2*dv+1`.
They are reversed in sorted order exactly when `du=1` and `dv=0`.
Put `swap=du*(1-dv)`, and select the column with `coin XOR swap`.
The output low bit is that column, and its high bit is the corresponding
digit. A plain transpose of the row output would not preserve ordered
coin labels in that case. The circuit includes the sorting condition.

In endpoint mode, coin zero stops at the unique leaf. Coin one continues
at node zero. Its leaf is `(du,0)` in low/high-bit order for row orientation
and `(0,du)` for column orientation. Both modes then double the phase
modulo thirteen.

## Inverse and complete reversible circuit

Write `theta'` for the new phase. The previous phase is

```text
theta = (theta' + 13*(theta' mod2))/2.
```

In mixed mode the old node is one minus the new stopping flag. In endpoint
mode it is zero. The previous high node bit and stopping flag are zero.
The coin and all four read-only parameters remain available. These formulas
recover the old valid packet even when the new packet is a terminal label.
They apply inside the tail; they do not invert the prefix-to-tail entry.

Nick Petalas's unchanged Boolean primitives implement the arithmetic.
The modular adder first forms the five-bit sum `s` in `[0,24]`. It also
forms `s+19 mod32`. The top bit of that second word distinguishes `s<13`
from `s>=13`, so selection gives `s mod13`. Repeated doubling and four
controlled terms form each parameter product. Adding nine to a residue
makes bit four equal to its threshold digit.

The forward oracle computes the new packet into seven clean backing bits
and reverses all temporary arithmetic. Seven bit swaps exchange the
packets. The inverse oracle computes the old packet into the backing bits,
which clears them, then reverses its temporary arithmetic. Every gate in
this sequence is counted. The generated gate list is a permutation on
all its wires; the claimed packet function is restricted to the valid
semantic domain above.

| Resource per tail draw | Count |
| --- | ---: |
| X / CNOT / Toffoli | 70 / 895 / 312 |
| Total gates | 1,277 |
| Temporary work + clean packet backing | 375 + 7 = 382 bits |
| Live packet / read-only parameters / resident coin | 7 / 10 / 1 bits |
| Total wires | 400 |

The ten parameter bits are the two four-bit residues, orientation and
mode. The same circuit handles 576 runtime parameter settings. The full
20,736-edge semantic domain is checked in both directions, including
every work bit, every parameter and the coin. A separate scalar gate
interpreter checks 1,152 boundary cases both ways. All 169 modular-addition
inputs and their uncomputation pass. Five gate controls alter the stopping
flag, residue parameter, mode, work state or output order and fail.

## Stopping and evidence limits

Under fresh independent fair coins, an endpoint entry needs two tail
coins in expectation. A mixed entry at node zero needs exactly one;
at node one it needs three in expectation. Indeed node one continues
for one step and then selects node zero or one with equal probability.
The unique finite solution is `E1=1+(1+E1)/2=3`. The two mixed entry
prefixes are equiprobable conditional on reaching the unfinished pool,
so their average is two. Worst-case stopping time remains unbounded.
These expected coin counts are not physical tape or complete caller costs.
Conditional freshness is an inherited obligation, not proved here.

All 19 retained source files are authenticated by Git blob and SHA-256.
The full fixed-pair arithmetic verifier runs unchanged as a primitive
source cross-check. The source-domain kernel fixtures, complete PR7757
verifier, full PR7755 runtime verifier, historical probability/mean
catalogue, selected cold replay, Lean and Docker were not run. The runtime
verifier file is retained for its interpreter attribution, not executed.

Parameter preparation, the first four coins, their entry/return protocol,
physical wire and tape access, output retention, stopping storage,
conditional freshness and the complete native invoice remain open.
The generic core's larger gate count concerns a different semantic domain;
no matched physical speedup or global gate optimum is claimed. All five
assumptions and the selected frontier remain unchanged. Separate numerical
and gate paths do not imply independent human or formal-kernel acceptance.
