# Exact conditional compensation invoices

The complete one-helper-per-edge fallback is legal at the contract's scalar/frame
level but fails the nominal cost screen by a large margin. With the conservative
fullwidth K profile, its best tested L3/L5/L7 nominal κ is below 6.0·10^-7,
compared with the selected conditional κ=0.001672660197076918. This audit makes
**no new κ, full compiler admission, or precision/theorem claim**.
The complete address-bucket variant halves the helper count to 227,312,640
and has a best tested root below 1.266·10^-6; it also fails both targets.

## Replay and scope

```sh
python3 -B research/h6-compensation-network/pricing/verify.py
```

Python >=3.11 and the standard library suffice. The verifier writes
`pricing/RESULT.json`, binds source files and the prior exhaustive pairing
census, constructs the mass/rank invoice independently, and uses the exact
rational logarithm/exponential oracle from `h6-independent-audit/invoice`.
The predecessor calculator nominates nominal-root brackets; the independent
oracle certifies both endpoint signs afresh. Target-pressure decisions and
helper allowances use exact rational enclosures without floating decisions.

## Complete fallback profile

The invoice assumes a K-word satisfying the contract's arbitrary-source,
arbitrary-target and arbitrary-helper-dirt interface. The extension preserves
its actual data paths. For the explicit conservative profile priced here,
sources and targets each follow [16], all 816 ordinary K-center helpers follow
[17], and K's private center-copy bill is 816·17=13,872. The full compensation
adds R=480,337,920 ordinary helpers, each [1,15,1]. The K-center helpers and
edge helpers are separately paid; the private-copy bill is additional work.
`k_encoder/RESULT.json` now supplies the explicit full-center scalar/frame/copy
word and exact factor identity, removing the abstract K-macro gap for this
profile. The universal physical family now supplies endpoint/adapter recipes and
a finite movement price; all-size precision admission remains separate. Its coefficient histograms are independently recounted here.

For m=16L+1, q=floor(m/17), p=m-17q:

```
W = (L-1)*30960 + L*(R+816)/q
D = (L-1)*30960 - L*13872
edge_helper_pressure = L*[2*((m/1)^alpha-1)
                          +15*((m/15)^alpha-1)
                          +(p/q)*((m/p)^alpha-1)]
K_helper_pressure = L*[17*((m/17)^alpha-1)
                       +(p/q)*((m/p)^alpha-1)]
alpha = kappa/(1-kappa)
```

Each helper group adds rank mass Lm·count/q and stock L·count/q, leaving D
unchanged. All retained idle ranks and pads are included. The private descents
are charged at rank17. Replication T=q makes each group's helper-bank count
integral, even when separate groups have incompatible divisibility. The
receipt checks complete stock/mass identities and strict m²>2r² child caps.

| L | q | pad | stock per template | nominal κ interval |
|---|---:|---:|---:|---|
| 3 | 2 | 15 | 720,570,024 | [0.000000409346908435, 0.000000409346913436] |
| 5 | 4 | 13 | 600,547,260 | [0.000000566584420981, 0.000000566584425982] |
| 7 | 6 | 11 | 560,580,952 | [0.000000598929959282, 0.000000598929964283] |

For the full address-bucket variant, one helper serves every target port having
the same binary cap for a fixed source. Weighted precompensation and scatter
still cover all R edges; gather and cleanup occur once per lane. Each lane has
the same [1,15,1] path and the K composition preserves source[16]/target[16].
The full-mask census binds its **227,312,640** lanes.

| L | bucketed stock per template | bucketed nominal κ interval |
|---|---:|---|
| 3 | 341,032,104 | [0.000000864929953895, 0.000000864929958896] |
| 5 | 284,265,660 | [0.000001197068906024, 0.000001197068911025] |
| 7 | 265,384,792 | [0.000001265346351896, 0.000001265346356897] |

The same exact target allowances below apply to either fullwidth inventory,
since they vary the number of identical paid [1,15,1] lanes. Coalescing slots
changes their count, without changing a lane's pressure or giving free stock.

The actual [1,15,1] edge allowance, after paying the 816 K helpers, is:

| target | L3 | L5 | L7 |
|---|---:|---:|---:|
| selected κ | 83,925 | 94,434 | 82,742 |
| pending PR1424 title κ | 83,631 | 94,027 | 82,312 |

Both adjacent signs are certified. These allowances use the present profile;
they are not copied from H6's different [1,7,8,1] helper budget. Positive
per-helper pressure proves the global integer boundary for each fixed L.

The receipt also prices a conditional alternative retaining private-copy widths
{17:256,15:560}, bill12,752, while still paying all 816 ordinary K helpers.
Its L3/L5/L7 roots are respectively about 4.7708748·10^-7,
6.2482359·10^-7 and 6.5189431·10^-7. This arithmetic alternative does not
establish that a K-word realizes the heterogeneous profile at this boundary.
Neither profile includes speculative stage sharing or idle hosting credit.

## Scalar primitive count

The contract has **4R=1,921,351,680 scalar additions**: two weighted
precompensation/scatter operations and two unit gather/cleanup operations per
edge. With 3,363,840 exceptional |t|=3 edges, the inherited weighted-operation
bound gives:

```
cost(±1/16)=8, cost(±5/16)=11, cost(±1)=4
total <= 24*R + 6*R3 = 11,548,293,120 scalar primitives per invocation
```

These are scalar operations, not extra Fourier children. They exclude K,
representative adapters, controller routing, tape and precision. The actual
compiler must include them and reconstruct its bounds; endpoint dirt
cancellation does not cancel intermediate precision cost.

The bucketed variant has 2R+2Rlane=1,415,301,120 scalar additions and
primitive bound
16R+8Rlane+6R3=9,524,090,880. The K coefficient histograms contain 6,440,208
nonzeros on each side. Their independently recounted bounds are
247,217,040 forward and 247,219,488 dual, including clear/copy/erase charges.
Using the larger orientation, the complete local scalar primitive bounds are
**11,795,512,608** for the edge fallback and **9,771,310,368** for the bucketed
variant. These include K scalar work; physical adapter movements are separately bounded in the universal family and
bank ledger. Integrated routing, tape and approximate-child precision remain open.

## Actual partial-route charges

The three independently replayed standalone routes are priced using their
emitted profiles. No source subset is substituted for N=30,960 in a complete
controller recurrence, and no partial block receives a nominal κ.

| route | sources | target paths | helper paths | local transition rank |
|---|---|---|---|---:|
| eight-column fiber | 8×[16] | 15,872×[1,15] | 8×[1,16] | 254,216 |
| k2 masks | 16×[16] | 15,872×[1,15], 7,936×[2,14] | 16×[1,1,15] | 381,456 |
| k4 masks | 32×[16] | 5,152×[1,15], 11,904×[2,14], 8,864×[3,13], 1,984×[4,12] | 32×[1,1,1,1,13], 64×[1,1,1,14] | 448,608 |

The receipt reports each route's per-L actual transition work, ordinary-helper
stock, pad work, integral replicated bank count and exact target-pressure
contribution for m=49/81/113. A complete all-port data/controller stock and
deficit are absent. These charges quantify local routes; they cannot by
themselves establish a complete supplier saving.

The cheap mask routes leave targets at different nonzero mask frames during
their scatter. The original K macro requires targets at zero. Appending that
macro for free is invalid: K must be fused through separately priced private
center-copy chains or supplied by a different admitted schedule.

## Fixed two-full-center-chain screen

A model duplicating each of the 816 fullwidth private descents across two
chains has C=2·816·17=27,744. This **fixed model** fails both selected and
pending targets for every odd L>=3, even before charging its helpers.

L3 and L5 have negative deficits. For every L>=7, m/16>L and the active data
work alone gives

```
pressure/(N*L) > 32*alpha*log(L)
               >= 32*alpha*log(7)
               > 1-C/N > D/(N*L).
```

The last strict inequality is certified by the rational log enclosure. Its
gap at the selected target exceeds 0.0004536254770085672. This rejects the
specified doubled-copy inventory, including all later stages. It does not
exclude altered center factorizations, different paths, shared arithmetic,
coordinate mixing or a cheaper fused K implementation.

## Open next questions

- Integrate the emitted exact K word, universal frame family and cleared
  coefficient streams into the literal bank/controller/tape compiler. The
  nominal invoice here already uses its measured fullwidth data/helper/copy profile.
- Compress compensation while preserving all independent dirt columns and
  low-frame incidence. The partial routes demonstrate local compression but
  their target chronology must be integrated with K and a complete controller.
- Recount primitive, adapter, precision and tape costs for the whole word,
  followed by bit and outer transfer. The nominal failure above needs none of
  those missing positive costs to reject this fallback.

Geometry/accounting and the banked interface are credited to Dominik Scholz
PR606; the H6 escape-map package to DreamingOfClouds. Contract, routes and this
pricing were prepared with substantial OpenAI Codex assistance. Apache-2.0.
