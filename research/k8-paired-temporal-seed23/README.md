# A shared ADD defeats independent temporal gauge optimization

On the frozen seven-slot k8 complex word, jointly scheduling L225 and L350
saves **474 scalar primitives per complex invocation in each orientation**.
The joint optimum is **six primitives cheaper than every composition of
individually optimal schedules** in the declared domain, including all ties.
One shared ADD explains the entire difference.

This is a finite scalar construction and a bounded optimization result. It
does not change the selected supplier, paid recursive profile, or kappa. The
larger constant-gauge construction in PR1263 and its successors already have
lower total scalar bills. This package establishes a coupling effect that
cannot be obtained by adding independently optimized temporal savings.

| Complete local scalar word | Original | Joint L225/L350 | Saving |
|---|---:|---:|---:|
| Forward | 149,002 | 148,528 | 474 |
| Backward | 149,018 | 148,544 | 474 |

The forward schedule inserts 55 SCALE macros costing 62 real-component
primitives and saves 299 in ADD lowering. The backward schedule inserts 59
SCALE macros costing 66 and saves 303 in ADD lowering. Both net savings are
237 per real component. Real coefficients make the complex invoice twice that.

## Reproduce

With Python 3.10+ and the standard library, from the repository root:

```sh
python3 -I -O -B research/k8-paired-temporal-seed23/verify.py
```

Expected output:

```text
PASS_K8_PAIRED_TEMPORAL_NO_NEW_KAPPA pair=225,350 saved=474/474 strict_coupling_gain=6/6 pairs=16 orientations=2 columns=712
```

The verifier writes no files, requires no network or Git history, and also
works when called by absolute path from another directory. `--emit` prints
the recomputed certificate instead of comparing it with [CERTIFICATE.json](CERTIFICATE.json).
Default verification always compares every deterministic certificate field.
Schedules contain the original zero-based event index and both exponents.
They determine the complete emitted word; its canonical JSON SHA256 is in the
certificate. [SOURCES.json](SOURCES.json) pins the immutable input archives,
receipt linkage, three consumed archive members and the literal lowerer.
Historical review/assembly hashes are provenance, not live replay dependencies.

## Domain and completed coverage

The investigation base is `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
The OS assignment seed was 23, complex supplier. The [claim](CLAIM.md) records
three candidate tasks, overlap checks, the complete selected pair list and the
stopping rule. The source provider has 237 cold/FULL, unwrapped, non-center
helpers without COPY/CLEAR, and 2,414 unordered ADD-interacting pairs.
Seed23 selects sorted pairs [23:39]. All 16 pairs and both orientations are
complete; no pair or exponent-box expansion was performed.

For each selected pair, both gauge exponents lie in the integers [-4,4]. They
may change before each ADD incident to either helper, and must equal zero
before **every nonscalar event**, including events on unrelated helpers.
Entry and exit exponents are zero. All other helpers have zero gauge. Every
original SCALE remains present and separately priced. No original operation,
operand, frame, source access, wrapper or recursive child is removed or
reordered. No new helper, COPY or CLEAR is introduced. Extra scales use the
helper's current frame, including scales that restore zero before a boundary.

This domain covers arbitrary timing within each scalar block: between two
incident ADDs, original diagonal SCALEs commute with the gauge, other
operations do not use the selected helper, and the triangle inequality lets
multiple changes collapse into one at the next incident ADD without increasing
cost. There is no all-integer exponent claim and no global circuit optimum.

Five pairs have a strict gap against **all** tied independent optima in both
orientations: L225 paired with L350, L356, L384, L388 and L401. Their real gaps
are 3, 2, 2, 2 and 2. L225/L350 is selected for the largest strict coupling gap,
with lexicographic pair order breaking ties. L225/L401 has the lowest complete
bill among these 16 pairs; no priority or best-known-circuit claim is made for
the chosen witness. The other eleven pairs show no strict advantage over the
best tied independent composition in this bounded domain.

## Complete cost and exact recurrence

Write a nonzero dyadic coefficient as `q = sign(q) p 2^e` with positive odd p.
The retained PR696 ADD lowerer has real-component price

`C(q) = 1 + bit_length(p) + popcount(p) + |e| - [p=1 and e=0]`.

This includes coefficient-work initialization and clearing. A SCALE by `2^d`
costs `|d|`. For a state `s=(a,b)`, an incident ADD's coefficient becomes
`q 2^(sigma_a a + sigma_b b)`, where each sigma is +1 for the destination,
-1 for the source and zero otherwise. A shared ADD uses their difference and
is charged once.

Inside a scalar block, set `D_0(0,0)=0` and all other initial costs to infinity.
For each incident ADD i, the exact recurrence is

`D_i(s) = C(q_i 2^(sigma_i dot s)) - C(q_i) + min_t(D_(i-1)(t) + ||s-t||_1)`.

The block price is `min_s(D_last(s)+||s||_1)`, charging restoration. Sum block
prices and add the complete original word's invoice. All recursive work is
retained, so there is no discount to hide outside this scalar delta.

[search.py](search.py) evaluates the transition minimum by two coordinate
distance transforms. [verify.py](verify.py) separately enumerates all 81 by 81
state transitions with literal PR696 lowering lengths. It checks 49,693,014
transition candidates across all 32 cases. These implementations share the
source-derived incident list and finite domain; they are independent transition
and price calculations, not independent extraction of the whole supplier.

To handle ties correctly, the main checker finds each single-coordinate
shortest-path DAG using forward/backward costs, then minimizes joint cost over
the product of those DAGs. The dense oracle instead minimizes a lexicographic
pair: first the sum of the two independently charged path costs, then the
actual joint cost. The first objective attains the sum of the separate minima
because paths can be chosen independently; equality forces both paths to be
individually optimal. The second objective therefore checks every tied
composition without relying on the DAG implementation. Both methods agree.

## The small coupling witness

Only one block contributes the strict gap for L225/L350. Its incident events
run from 18,338 through 24,523, with 104 incident ADDs and just one shared ADD
at event 22,786. Forward, that shared ADD has coefficient 2 and exponent `a-b`.

Let A(a) and B(b) be the independently optimized real-component block deltas,
conditioned on each helper's exponent at that shared ADD. Both include all
entry/transition/exit scales. The verifier reconstructs these profiles using
separate one-dimensional prefix and suffix minima and literal lowering:

| Exponent | -4 | -3 | -2 | -1 | 0 | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A, L225 | -35 | -38 | -41 | -43 | -42 | -39 | -36 | -33 | -30 |
| B, L350 | 0 | -3 | -6 | -9 | -12 | -14 | -12 | -9 | -6 |

Since there is exactly one shared ADD, the complete joint block delta is

`A(a)+B(b)+C(2*2^(a-b))-C(2*2^a)-C(2*2^(-b))+C(2)`.

The independent minimizers force `(a,b)=(-1,1)`. Their nominal sum is -57,
but the shared-operation correction is +4, giving -53. The unique best joint
state is `(0,1)`: A pays one more primitive while avoiding all four of that
correction, giving **-56**. All 81 state pairs are checked. Thus arbitrary
tie-breaking elsewhere cannot remove the three-primitive gap. The backward
profiles reverse the exponent order; its unique joint state is `(0,-1)` and
its separate minima force `(1,-1)`, with the same costs.

Other blocks contribute the same -181 optimum with or without this coupling.
The full joint delta is -237, versus -234 for the best tied independent
composition. Twice their difference gives the six-primitive complex gain.

## Identity, accounting and checks

The actual candidate stream is parsed independently of its schedule. The
checker tracks the relative diagonal scale, verifies every conjugated ADD,
retains each original event, checks all inserted scale frames, and requires
both gauges to be zero at every nonscalar event. Thus the original nonscalar
interfaces receive exactly the same registers. This supplies an event-by-event
invariant, not an assumption that nonzero gauges commute through children.

Both original and candidate scalar words replay on all 712 formal columns in
both directions, including arbitrary helper dirt and all private centers.
All 327 distinct ADD coefficients and 23 SCALE coefficients pass separate
literal primitive-map checks, including arbitrary coefficient-work input.
Complete literal invoices match the recurrence and the inherited paid profiles.
The local positive-prefix ceilings remain 52 bits forward and 68 backward;
the denominator-depth bounds remain 22 and 26. Their signed fixed-point
payload fits the retained 192-bit local allowance.

The verifier includes 729 exhaustive tiny paths, two zero-schedule controls,
and twelve rejection checks for missing transition work, changed endpoints,
wrong frames, out-of-domain exponents, incomplete schedules, source corruption
and source-inventory omission. [VALIDATION.json](VALIDATION.json) records the
tested runtimes, source Git-blob checks, outside-checkout execution and repository
checks.

The full selected cold replay and native/hosted admission were not run. The
added macro events can change adapter accounting in a future physical
composition. Local scalar savings alone do not establish a cheaper supplier
invoice or multiplication runtime. Inherited compiler, realization,
common-label/mutable-source, whole-call hosting, global precision/tape,
analytic-transfer and bit H1-H5 obligations remain. No finite replay here is
a formal proof of the full theorem. Selected kappa at the base remains
`836330098538459/500000000000000000`.

## Predecessors and concurrent work

- @woklerx PR1161 introduced the single-helper constant gauge. Hanson Sun /
  @bbMisk PR1214 established the at-most-two constant-gauge optimum and priced
  shared ADDs. Those constant families differ from this temporal family.
- Sagar Thakrar's PR1259 supplies the temporal recurrence, source loading,
  sparse scalar replay and primitive invoice code adapted here. Philipp /
  @mightyOil PR1270 supplies the zero-at-every-nonscalar-boundary contract and
  single-helper census. These mechanisms are credited, not rediscovered claims.
- Philipp's PR1263/1310/1322 treat simultaneous constant gauges, pair moves and
  coherent triples. Cinna Davis / @1337isnot1337 PR1350/1353 add L253/L248
  temporal gauges over a fixed many-helper background. Concurrent PR1369 now
  covers the zero-static single helpers, and PR1376 proves that the disjoint
  L248/L253 temporal objectives separate. This package starts at the original
  zero-gauge word and proves a strict interaction gap for a different pair.
  It does not claim superiority to their invoices. All these source heads are
  recorded in SOURCES.json; PR1369/1376 are context, not runtime dependencies.
- The unchanged k8 provider follows Jeremy Kothe's construction/schedules,
  Rohan Arun's selected PR1094 composition, the icekylinx scalar/frame lineage,
  and the predecessors in the retained maintainer review. The literal PR696
  lowerer is Sagar Thakrar's contribution, building on that lineage.

Contribution by Sagar Thakrar / `thakrarsagar`, with substantial OpenAI Codex
assistance in research, implementation, proof writing and review. New files
are under the repository's Apache-2.0 license. No independent human review is
claimed. Frozen packages, selected records and `upstream/` are unchanged.

## Open next questions

1. Can this pair's strict coupling advantage survive a fixed many-helper
   background? First rederive the two conditional profiles on a pinned
   PR1263/1310/1322 word. Their altered coefficients prevent adding these
   savings numerically. Check active temporal claims before starting.
2. What physical invoice results after admitting the added SCALE events?
   Begin with the unchanged native frame checker and count every added adapter.
   Macro-event overhead may outweigh the local scalar saving; no favorable
   supplier conclusion is assumed here.
3. Does an exact clipping argument close the unbounded two-coordinate domain?
   Start from the single-shared-ADD conditional profiles. Independent clipping
   need not preserve their difference, so the single-helper proof alone is
   insufficient. The present [-4,4] census leaves that question open.
