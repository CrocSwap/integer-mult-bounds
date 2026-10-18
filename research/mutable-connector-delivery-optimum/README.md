# Exact mutable-connector cost under sequential delivery cuts

A dirty connector can stay open between output requests while its source
changes. The optimal schedule must balance the source calls saved against
**paid source-update corrections**. This package proves the exact generic
query optimum for that combined interface, including arbitrary call
multiplicities, and supplies an attaining two-state schedule.

This closes a specific gap between woklerx's [PR1439 mutable-source
construction](../mutable-source-persistent-connector/README.md) and
[PR1442 delivery-cut optimum](../connector-delivery-cut-optimum/README.md).
Neither predecessor's unrestricted batch bill can simply be reused under
both requirements. The result is an abstract interface optimum and a literal
finite circuit. **No selected supplier, recursive profile or new kappa is
claimed.** The selected #1094 record remains unchanged.

The three-output pilot costs **52 scalar XORs instead of 64**, with all source
updates and connector corrections included. This extends the predecessor's
43-to-31 two-output pilot; no priority is claimed for that pair or for the
correction identity `D=BC`. The new content is the exact chain price, its
lower bound for all legal words, the matching corollary, and separate checks.

## Contract and exact optimum

Work over F2. All rows are distinct and arbitrarily dirty. There is one source
`x`, one connector `z`, read-only update rows `u_1,...,u_(k-1)`, and distinct
output rows `y_1,...,y_k`. Fixed maps `B,A_i,C_j` are linear and dimensionally
compatible; they need not commute, be invertible or have full rank.

During request epoch i the source is `x_i`. The required output is
`y_i += A_i B x_i`. No output may be written before its request or after its
delivery; requests are disjoint and sequential. After delivery i, the imposed
source update is `x_(i+1)=x_i+C_i u_i`. This is an intended data change, not
unpaid scratch. The final source has all updates, every `u_i` is unchanged,
and `z` must return to its arbitrary initial value `z0`.

Allowed operations are complete additive calls:

- `B_i: z += B x_i` in source epoch i, price `b_i > 0`.
- `A_i: y_i += A_i z` inside request i, price `a_i > 0`.
- At cut i, the imposed source update costs `m_i`, and any number of
  `D_i: z += B C_i u_i` corrections may be called at price `d_i > 0` each.

Each epoch is its output request interval; a cut contains the one mandatory
mutation followed by D_i calls. A terminal close can occur after the final
readout and before its delivery. The word is straight-line and must work for
arbitrary maps and inputs under this contract. Specialized zero maps or dependent update inputs may be
cheaper. No other data operation, extra connector, free copy, source mutation,
combined query or change of role/frame is allowed. Complete call prices include
their private scratch, source access, restoration, routing/frames, head returns
and dispatch. The tariff is fixed for each named call: there is no unpriced
reuse between its invocations. Positive rational prices are used by the checker;
the proof applies to positive real prices as well.

Let `p_0=p_k=0` and `p_i in {0,1}` for interior cuts. Then the exact query bill is

```
Q = 2 sum_i a_i
    + min_p { sum_(i=1..k) b_i [2 - (p_(i-1) XOR p_i)]
              + sum_(i=1..k-1) d_i p_i }.
```

Add the mandatory `sum m_i` and actual caller admission, coefficient preparation,
connector reservation, program storage and other charges not already in the
complete tariffs. If that additional overhead depends on the chosen path, it
must be priced for that path; `Q` alone is not a physical supplier invoice.
`TASK.json` records the precise scope and the source-bound first-step baseline.

## Lower bound for every legal query word

Specialize to scalar identity maps, with independent `x_1,u_j,z0,y_i0` bits.
Every valid generic word must work on this specialization. Let `n_i` count
B calls in epoch i, and `t_j` count D calls at cut j.

1. Each output needs an even positive number of A_i calls to cancel the
   arbitrary `z0` coefficient, hence at least two.
2. If no B occurs inside request i, the coefficient of `x_1` in z is constant
   throughout that interval. Any even number of A_i calls then cancels it,
   contradicting the required coefficient one in the delivered output.
   Thus `n_i >= 1`, even if there are extra readouts or early preparations.
3. Final z restoration forces `sum_i n_i = 0 mod 2`. Define
   `p_j = sum_(i<=j) n_i mod 2`. The coefficient of the independent update
   `u_j` in the final connector is `t_j + sum_(i>j) n_i`; it vanishes iff
   `t_j = p_j mod 2`. This uses the final parity just established.
4. Accordingly, `n_i` is at least one if successive p states differ and at
   least two otherwise; `t_j >= p_j`. Multiplying by positive complete
   prices gives exactly the displayed lower bound.

No assumption of a coherent intermediate connector or paired readouts was
used in this bound. In fact it still holds if every past D_j remains available
inside later requests at the same price: D_j has no `x_1` coefficient, and
its final coefficient is still governed by step 3. The independent checker
also explores that relaxed alphabet. This is not a claim about combined
correction queries, aliases, cross-output operations or free source mixing.

## Attainment and recurrence

The construction maintains `z=z0+p B x_i` at each request entrance.
Given incoming p and desired outgoing q, execute

```
A_i; B_i; A_i; [B_i if p=q]; deliver i.
```

The two A_i calls differ by precisely `A_i B x_i`, so arbitrary dirt cancels
without commuting any maps. One B toggles the connector type; a second B
retains it. At the next source update, call D_i exactly when q=1. Then

```
z0 + q B x_i + q B C_i u_i = z0 + q B x_(i+1).
```

This proves every delivery and the final endpoint for arbitrary compatible
linear maps. It attains every term in the lower bound. The recurrence starts
at state 0, charges `b_i[2-(p XOR q)]` on a transition, then `q*d_i` at an
interior cut, and ends at state 0. The numeric minimum requires O(k) arithmetic
operations and two running costs; reconstructing the path uses O(k) storage.
The reference implementation retains path tuples for deterministic tie-breaking
and does not claim linear implementation time for those tuple copies.

For **uniform** source price b, the optimum is a maximum-weight matching on
the path of requests. Pairing adjacent i,i+1 saves `2b-d_i`. To see why adjacent
pairs suffice, each run of open cuts from l through r-1 saves 2b in B calls
and pays `sum_(j=l..r-1) d_j`. Replacing that run by any single edge inside
it preserves the source saving and cannot increase the positive correction
bill. Distinct runs give disjoint pairs. Conversely every matching is attained.
For constant correction price d the exact saving over closed calls is

```
floor(k/2) * max(0, 2b-d).
```

Uniformity is necessary for that simplification. With `b=(10,1,10)`,
`d=(2,2)`, `a=(1,1,1)`, keeping the connector open across both cuts costs
32 versus 48 closed. Any one adjacent pair costs at least 39. The two-state
recurrence handles this nonadjacent optimum exactly.

## Literal pilot and complete local bill

Use PR1439's three-bit `B=(3,6,7)` row masks, updates `C_i=(1,0,0)` from
independent one-bit `u_i`, and readers alternating `(2,4,1)` and `(3,2,4)`.
Every matrix entry one is one literal source-to-target XOR. Hence `b=7`,
`d=2`, `m=1`, and the three readout prices are `(3,4,3)`.

| Charged work, k=3 | Closed after every output | Optimal persistent pair |
|---|---:|---:|
| B calls / scalar XORs | 6 / 42 | 4 / 28 |
| A calls / scalar XORs | 6 / 20 | 6 / 20 |
| Mandatory source updates | 2 | 2 |
| D corrections / scalar XORs | 0 / 0 | 1 / 2 |
| Total XORs / writes | 64 | 52 |
| Data reads (two per XOR) | 128 | 104 |
| Head steps in the explicit return-to-origin tariff | 1,006 | 858 |

Both programs use the same 17 data bits, including three dirty connector bits,
and no clean ancilla. The head tariff visits source then target and returns to
bit zero, so a gate at positions s,t costs `2 max(s,t)` head steps. A common
one-bit read buffer, if used, has the same admission/restoration in both words.
Program storage/dispatch uses 64 versus 52 equal-width XOR records, plus the
same source/request metadata. These are exact local counts, not a native
runtime or the repository's recursive tape admission.

The fixed pilot's macro lower bound is also sharp: `B e0=(1,0,1)` is nonzero,
each `A_i B e0` is nonzero, and each independent update contributes that same
nonzero vector times its own u_i. The four parity steps therefore apply to
this particular map as well. **52 is optimal in the declared indivisible
macro tariff, not among unrestricted scalar XOR circuits.** Pilots for
k=1..8 are checked; k=2 reproduces and credits PR1439's 43-to-31 comparison.

## Reproduce and checked scope

Python 3.12, standard library only, from repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/mutable-connector-delivery-optimum
```

The primary checker reconstructs `RESULT.json` read-only, with explicit checks
active under `-O`. Receipt regeneration is separate and requires
`verify.py --write-receipt`. The registered commands run:

- Exact two-state pricing and attaining words for all 518 tariff vectors with
  k=1..4, `b_i in {1,3}`, `d_i in {1,2,5}`, alternating A prices 1,2;
  3,280 uniform-source matching comparisons for k=1..8, b=3 and
  `d_i in {1,6,9}`; an exact rational-price fixture; all dirty basis columns
  of both literal pilots for k=1..8.
- A separate Dijkstra checker over the entire finite scalar-identity state
  quotient, allowing arbitrary readout/query multiplicities. It independently
  agrees on every tariff: 67,023 settled states for cut-local corrections and
  184,183 for the delayed-correction relaxation. No depth/state cap is used.
- All 4,096 triples of 2x2 B,C1,C2 maps on all four boundary paths, with fixed
  distinct readers including singular and noncommuting cases: 16,384 exact
  full-column map checks. Both three-output scalar words are additionally
  replayed on all 131,072 assignments of their 17 dirty bits, at every delivery.
- Six semantic controls and six test groups, including endpoint-neutral writes
  outside delivery intervals, an output-correct but unrestored connector,
  omitted mutations/adapters, price aliases, wrong gates, corrupted receipts,
  missing/drifting sources, and optimized read-only relocated replay.

`SOURCES.json` binds the retained predecessor text by exact Git blob and SHA256;
the generic runner additionally verifies historical catalogue/selected-record
provenance. The independent checker imports no primary or predecessor code.
Both implementations are by the same assisted author; this is not independent
human or proof-assistant verification. Finite checks support the written
universal proof, rather than replace it. Selected cold replay, native/compiler,
hosted owner realization, precision/tape and outer analytic transfer were not
performed or inferred. `VALIDATION.md` records the actual local commands.

## Open next questions

Find a concrete recursive caller with these sequential output cuts, a mutable
source, complete B/BC tariffs, and a reserved connector. That would determine
whether this exact price changes a paid recursive profile. First extract one
call pair's actual maps, source-update cuts and routing/precision requirements;
then price the attaining word including extra lifetime costs. The blocker is
the absence of such a source-pinned physical caller, not the local parity
identity. Stop adoption if the correction and extra lifetime bill exhaust the
saved complete source calls. Structured details are in `TASK.json`.

## Sources, overlap and credit

Base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. The single catalogue draw was
`d75d8f45c97a449ba6ec24ee203b7c12`, revision 3, recursive-interfaces /
`persistent-boundary`, refined to this exact contract. [Discussion1776](https://github.com/CrocSwap/integer-mult-bounds/discussions/1776)
records the claim and disposition. Entry overlap covered 442 open PRs and
408 Discussion records. The final 09:45-09:47 UTC snapshot covered 446 open
PRs and 418 Discussion records with complete pagination and no warnings;
all 31 returned matches were inspected, plus a synonym search of cached
bodies. Local package metadata and the ledger were included. That coverage
is not proof of novelty.

Credit **woklerx**: PR1439 head `3852c2d03044895cebdc9b31b0c7131a617774d2`
for the mutable-source correction, the two-call construction and pilot;
PR1442 head `7c573bc769798ce4e336fd5be630060bd9d69a71` for delivery cuts,
its static-source lower bound and finite-query verification method. Their
retained main-branch README bytes are the live pins used here. Credit
**Ross Richardson** PR934/943 for the universal dirty connector model and
its retained dirty-commutator lineage. **Cinna Davis** PR1739 head
`e33645b34521460bce61f9fb913f98f506d34d4d` changes B across a two-call boundary;
this work fixes B and proves the chronological chain optimum. The active
selected helper-476 residual-boundary claim and Z4 echo compositions concern
different maps. The synonym search also found tennisbowling PR1524 head
`5c1f39788a0fc669b7e37e27785c63e85788c350`: its arbitrary-count uniform
tariff concerns five freely mixed, ultimately restored sources and offline
all-mask outputs. Those source-shear/query choices and observation permissions
differ from this imposed-update, sequential-delivery chain. All selected
construction and inherited community credit stays with its sources.

Prepared by Ross Richardson with substantial OpenAI Codex assistance in
algebra, implementation, checking and writing. No subagents were used.
New material is Apache-2.0 under the repository LICENSE. No frozen predecessor,
upstream input or selected certificate is modified.
