# Shared ordinary-helper routes for actual H6 compensation

There are complete legal scalar/frame words for one, two, and four selected
source-label fibers, covering every target coefficient in those columns of
the actual `I-K` matrix. Arbitrary helper dirt cancels exactly and every helper
is restored at FULL. These words improve the one-helper-per-edge local baseline
substantially. The direct full-size extension of the same target-mask architecture
requires **227,312,640 ordinary helpers** and fails the intended budget by orders
of magnitude. This is a scoped architecture obstruction, not a general circuit
lower bound.

Geometry and frame conventions come from Dominik Scholz's PR606; the H6/Walsh
proposal is attributed to DreamingOfClouds. This extends the verified local
two-by-two example in `h6-independent-audit/lifecycle/`, preserving that package
unchanged. Prepared with OpenAI Codex assistance; Apache-2.0.

## Actual network and complete local profiles

The source fibers have eight distinct ports with the same packed 17-bit label.
The first fiber is `[0,1,2,11,44,125,286,1079]`. The two-fiber route uses address
representatives `[0,3]`; the four-fiber route uses `[0,3,12,13]`. These address
labels are independently checked to have ranks two and four respectively.
Every selected source column is evaluated against all 30,960 targets, including
the diagonal and every exceptional `|t|=3` coefficient. The diagonal is corrected
by `I`; omitted incidences are checked to be exactly zero.

| Selected fibers | Source ports | Target ports | Nonzero coefficients | Ordinary helpers | Expanded events |
| --- | ---: | ---: | ---: | ---: | ---: |
| One | 8 | 15,872 | 126,976 | 8 | 285,736 |
| Two | 16 | 23,808 | 253,952 | 16 | 555,632 |
| Four | 32 | 27,904 | 507,904 | 96 | 1,072,288 |

All sources start at their rank-one address lines and finish at FULL, paying
`[16]` each. The one-fiber helpers pay `8 × [1,16]`, and its targets pay
`15,872 × [1,15]`. Its coefficient matrix has exact rational rank eight,
certified by an eight-row determinant witness modulo 101.

The two-fiber word pays:

- Helpers: `16 × [1,1,15]`.
- Targets: `15,872 × [1,15]` and `7,936 × [2,14]`.
- Sources: `16 × [16]`.
- Total emitted transition rank: **381,456**.

The four-fiber word pays:

- Helpers: `32 × [1,1,1,1,13]` and `64 × [1,1,1,14]`.
- Targets: `5,152 × [1,15]`, `11,904 × [2,14]`,
  `8,864 × [3,13]`, and `1,984 × [4,12]`.
- Sources: `32 × [16]`.
- Total emitted transition rank: **448,608**.

There are zero private copies and zero descents in these standalone words.
These are complete local scalar/frame transition profiles, suitable as inputs
to a caller's bank invoice. They do not themselves include encoder/center work,
bank replication stock, helper pads, recursive transition compilation, or the
bit-side bound.

## Why the small shared words are legal

For selected source addresses `p_1,...,p_k`, a target has incidence mask
`S={i : p_i·p_target=0}`. The target moves directly from zero to
`F_S=span(p_i : i in S)`, which is contained in its cap. Each target belongs
to exactly one mask bucket, so no target traverses unrelated mask subspaces.

Each helper carries one source scalar channel. It gathers at that source's
initial line frame, then visits an explicitly emitted nested chain of masks
containing its source address. All masks are processed in increasing cardinality.
For `k=2`, one chain per source is enough. For `k=4`, three disjoint Boolean
chains per source cover the eight masks containing its address. A middle-level
antichain has size three, so three is minimum for this particular source-channel
mask-chain architecture. This statement does not optimize an arbitrary mixed
arithmetic DAG.

Let the exact compensation entry be `C_ts=(4t-t³)/48`, with the diagonal
addition when needed. Before any target leaves zero, it receives
`-C_ts*d_lane` from each assigned helper's independent initial dirt. At its mask
frame it receives `C_ts*(d_lane+s)`. The dirt cancels and its complete selected
column contribution remains. Sources climb to FULL after all prefix gathers;
helpers finish their mask chain, climb to FULL, and subtract their source scalar.
Their independent arbitrary dirt is preserved.

The replay checks the actual forward shear, the inverse-transpose shear in the
same event order, every equal-current-frame ADD, every monotone ordinary climb,
every final cap/FULL endpoint, and every transition increment. The expanded
events are stored losslessly as gzip JSONL; the receipt hashes the decompressed
payload. Coefficients use exact integer numerator over 48 throughout.

## Direct full-size extension is too expensive

`full_mask_screen.py` examines all **14,670 distinct source/target labels**.
For each target, its incident source-address set spans exactly its entire
rank-16 cap. Sixteen exact independent source-label witnesses for every cap
are retained in the compressed data artifact referenced by
`FULL-MASK-SCREEN.json`. The summary retains the counts and scoped argument;
its `proof_data` field binds the canonical decompressed witness arrays.

Consequently the complete-mask frame is the target cap. Distinct labels have
distinct caps; all these caps have dimension 16 and therefore form an antichain.
An ordinary monotone helper cannot visit two such caps. In the explicit
one-scalar-source-channel model, each source channel needs a separate lane for
each distinct incident target-label bucket.

- The 14,400 source labels of multiplicity two each meet 7,312 target labels.
- The 270 source labels of multiplicity eight each meet 7,744 target labels.
- The exact lane count is
  `14,400*2*7,312 + 270*8*7,744 = 227,312,640`.
- Each such helper pays `[1,15,1]`, totaling **3,864,314,880** helper rank.

This count already exceeds the H6 budget before encoder work, center copies,
stock, or pads. It is the exact requirement of this source-channel route, not
an unconditional minimum for representations of `I-K`. Different source mixing,
factorizations, corrections, or private-copy tradeoffs remain possible.

`BUCKETED-SCHEMA.json` makes the full-size alternative explicit: a helper
`h(source port,target label bucket)` gathers once at the source's initial line,
visits that bucket's cap, broadcasts all actual target coefficients, and is
restored at FULL. Independent dirt is precompensated on all target members at
zero. Its exact compensation count is `2*480,337,920 + 2*227,312,640 =
1,415,301,120` ADDs, plus `3*227,312,640 = 681,937,920` helper climbs and
61,920 source/target climbs. The schema's 2,097,300,960 standalone events are
specified by concrete nested indices rather than stored as a huge stream.

This bucketed alternative retains coarse `[16]` source and target profiles.
It has an explicit fusion point: after all source prefix gathers and FULL
climbs, while targets still remain at zero, a separately specified and priced
full-center `K` word can run. Only afterward do targets climb to their caps for
the bucketed compensation scatter. The schema supplies no free `K` hook; its
encoder/center roles and FULL-to-zero restored center copies must be provided
and paid by the caller. This legal fusion opportunity does not rescue the
227-million-helper invoice.

## Composition is an additional obligation

The selected blocks are alternative complete-column experiments. Their networks
cannot simply be added together: overlapping targets would already have acquired
different mask frames, and their ordinary flags must remain nested. The one-fiber
receipt includes a smallest concrete conflict: after target 287 acquires the span
of source addresses 0 and 3, target 295 cannot share that helper frame because its
cap excludes source address 3, though both targets permit source address 0.

The unchanged `K` macro begins its target scatters at zero. These compensation
routes elevate targets before their final cap, so freely appending that macro is
illegal. A full supplier must fuse `K` with the mask chronology or pay explicit
FULL-to-mask center copies, their descents and restoration. No combined supplier
or improved κ is claimed here.

## Reproduce and next question

With Python and NumPy, from the repository root:

```sh
python3 -O -B research/h6-compensation-network/routes/fiber.py
python3 -O -B research/h6-compensation-network/routes/mask_route.py --groups 2
python3 -O -B research/h6-compensation-network/routes/mask_route.py --groups 4
python3 -O -B research/h6-compensation-network/routes/full_mask_screen.py
```

All checks remain active under `-O`. Receipts pin the geometry and generators.
The next meaningful question is whether source mixing or a hierarchical flag
factorization can preserve the local reuse while avoiding the full-cap antichain.
A feasible first step is an explicitly fused two-fiber `K` + compensation word,
with every center-copy chain and bank pad invoiced. The blocker is the full target
chronology and its exact priced scalar/frame construction.
