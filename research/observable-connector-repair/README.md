# Repair the observable part of a persistent connector

**Scoped recursive-interface construction; no new kappa.** A connector need
not track every component of a changing source when the current reader sees
only a quotient. The fixed seed-50 example needs **four connector corrections
instead of fourteen full-coherence corrections**. Allowing a paid output
correction lowers the exact minimum to **three**: two connector XORs and one
output XOR. The complete program has **61 XORs instead of 72**, with the same
source mutations, readers, two B calls, and final restoration.

The contribution refines woklerx's [PR1439](https://github.com/CrocSwap/integer-mult-bounds/pull/1439):
its stronger intermediate contract still correctly requires the full BC
adapter. We weaken that contract at explicitly typed observation cuts and
optimize partial connector corrections together with paid output corrections.
Reader kernels, dirty cancellation, source repair and output-defect repair are
predecessor ideas, credited below. The new evidence is this correction-mask
recurrence, its exact finite optimum and the completely emitted comparison.

This is a fixed-query interface result. Opening the toy matrices and directly
forming each A_i B product costs **26 XORs**, including the same source updates
and observation cuts. That checked control rules out any claim that 61 is a
minimum over arbitrary circuits. No selected supplier requiring these fixed
queries is identified, and no improved multiplication exponent is claimed.

## Contract and identity

Work over F2 with L-bit blocks. The distinct rows are d source blocks x,
one independent source block u, d connector blocks z, m output blocks y_i,
and an untouched spectator. All have arbitrary initial values. Fixed binary
B is d by d; a_i is a binary reader row. Source updates x_j += u follow a
known word. Its cumulative mask is q_i at reader i, and q_m=0 at exit.
Thus x_i=x_0+q_i u. The requested output at cut i is

```
y_i = y_i_initial + a_i B (x_0 + q_i u).
```

Every completed output stays correct at subsequent cuts. Future output ports
are reserved and may be prewritten before their first observation. The open
connector is hidden and reserved. The source may be observed at each completed
stage, with its prescribed current value. At batch exit x, u, z and the
spectator must all be restored. No output aliases another row. Adaptive readers,
unannounced source changes, early observation of future outputs, or reuse of
an open connector are outside this contract.

Prewrite every output with `y_i += a_i z_initial`, then open the connector
with `z += B x_0`. Let its carried correction be k_i u, so at read i

```
z = z_initial + B x_0 + k_i u.
```

Apply the second `y_i += a_i z` and, in the enlarged alphabet, an optional
`y_i += p_i u`. The old connector dirt cancels. Correctness for all input
blocks is equivalent to

```
a_i k_i + p_i = delta_i,        delta_i = a_i B q_i.       (1)
```

Necessity follows by setting one bit of u to one; sufficiency follows by
substitution. All other dirty variables cancel independently. At exit return
k to zero and close `z += B x` after q has returned to zero. This restores the
entire connector, including the directions hidden from previous readers.
The literal reversed XOR word is the inverse, with every gate paid again.

Full coherence is the special choice k_i=Bq_i and p_i=0. Equation (1) permits
other representatives of the reader's affine coset. This does not refute the
necessity of BC under PR1439's stronger boundary. It changes the admitted
intermediate state while retaining the exact requested observables.

## Complete cost recurrence and its scope

The fixed-query alphabet requires the two B calls, the two reads for every
output, and the prescribed source updates. Only the corrections vary:
`z_j += u`, and optionally `y_i += u` before output i's observation.
No extra source queries, direct A_i B calls, register mixing, clean helper,
free frame change or skipped restoration is allowed. Each allowed complete
call restores private scratch and heads. All correction costs are positive.

Let w_j(L) price one complete connector correction, and v_i(L) one output
correction. Prices include source/coefficient access, arithmetic, scratch
restoration, routing, frames and dispatch for the chosen implementation.
For h,k in F2^d put

```
d_w(h,k) = sum_j w_j(L) [h_j != k_j].
F_0(0)=0; F_0(k != 0)=infinity.
F_i(k) = min_h (F_(i-1)(h) + d_w(h,k) + v_i(L)*(delta_i + a_i k)).
R(L) = min_k (F_m(k) + d_w(k,0)).                         (2)
```

All sums inside the last bit expression are modulo two. In the connector-only
alphabet, retain only states with `a_i k=delta_i` and omit the v term.
The complete batch charge is

```
C(L) = P(L) + I(L) + c_B_open(L) + c_B_close(L)
       + sum_i (c_Ai_pre(L) + c_Ai_read(L) + c_source_i(L)) + R(L).  (3)
```

P pays program/coefficient/plan preparation; I pays layout, admission and
reservation. Every complete child call and both B directions appear. If used
as a forward/inverse echo, charge both words plus that parent's actual copies,
readouts and admission; they are not free or included implicitly in (3).
No separate COPY or helper is used by the emitted batch. Fixed port roles avoid
frame changes in this pilot; a physical supplier must add any required ones.

To prove optimality in this alphabet, commute corrections between consecutive
observations and cancel repeated toggles. Reaching k from h costs at least
one w_j for each differing bit; toggling those coordinates attains that price.
An output needs parity p_i from (1), so zero or one v_i is optimal. Any schedule
therefore yields a path counted by (2); every such path emits a legal schedule.
Induction on i proves the recurrence. This is a stage recurrence, **not a
contracting input-size supplier recurrence**.

The independent oracle instead uses a graph with vertices (stage,k), individual
paid coordinate-toggle edges and free/paid observation edges. Stored integer
potentials satisfy every edge inequality. Their value at the terminal zero
state is a lower bound, and the emitted path attains it. No floating-point
search decision or finite replay is used as a proof of the all-L identity.

## Exact fixed example

OS seed 50 selected recursive interfaces and the fixture in `model.selected`.
Three bounded matrix draws select the first invertible B; there is no
optimization search over fixtures. Masks use bit j for coordinate j.

```
B rows:       [8,13,6,2]
a_i:          [9,6,4,11,15,2,3,14]
source steps: [3,2,1,0,3,2,1,0]
q_i:          [8,12,14,15,7,3,1,0]
Bq_i:         [3,5,9,11,8,14,2,0]
delta_i:      [1,1,0,1,1,1,1,0]
```

Connector-only states at the eight reads are `[1,2,2,2,2,2,2,0]`.
The path starts and ends at zero and costs four XORs. A shorter restored path
would have zero or two toggles. Zero fails the first demand; two toggles could
only hold one coordinate through the first two nonzero demands. Those readers
have disjoint support (`9 & 6 = 0`), so two are impossible.

The mixed optimum uses `[0,2,2,2,2,2,2,0]`, with a direct correction to the first
output. Fewer than three gates would be at most two output repairs (six are
needed without connector help), or two connector toggles with no output repair
(already excluded). The three-gate witness attains the minimum. The graph
certificate additionally proves the weighted minima used below.

| Complete fixed fixture | Correction XORs | Total XORs | Data-head steps, L=1 |
|---|---:|---:|---:|
| Separately closed query pairs | 0 | 156 | 2732 |
| Carried full coherence, PR1439-style | 14 | 72 | 1484 |
| Output-only repair | 6 | 64 | 1434 |
| Observable connector repair | 4 | 62 | 1328 |
| Mixed observable/output repair | 3 | 61 | 1324 |
| Direct product fusion, outside the alphabet | 0 | 26 | 562 |

The new reduction is **72 to 61**, beyond the already credited shared-query
reduction. It saves eleven XORs and 160 data-head steps at L=1. No runtime
speedup follows from these abstract instruction counts.

## Tape, preparation and storage accounting

The literal interpreter stores row-major L-bit blocks in one-based tape cells:
x occupies rows 0..3, u row 4, z rows 5..8, outputs rows 9..16, spectator row 17.
For each bitwise XOR it visits source, target, then origin. It charges two
reads, one write, one XOR and one dispatch. The finite-control bit latch is set
when reading the source and reset in the target-write transition; it returns
to its entry state on every gate. No dirty data row is used as scratch. The
interpreter assumes instruction delivery at dispatch; a backend's address
decoding and instruction-tape movement must be included in its complete call
price. The five-unit tariff is not a claim that such delivery is free on a
Turing machine.

For a block XOR between rows s,t, the data-head travel is exactly
`(2 max(s,t)+1)L^2 + L`; the declared online tariff adds `5L`.
The mixed correction bill is `45L^2+18L`, against full coherence's
`194L^2+84L`. Thus complete online bills are

```
full coherence: 1412L^2 + 432L
mixed repair:   1263L^2 + 366L
saving:         149L^2 + 66L.
```

The same path minimizes both the quadratic coefficient (45) and gate count
(3), certified separately, hence minimizes this correction tariff for every
positive integer L. Data-head movement and instruction traffic are distinct:
instruction records number `72L` versus `61L`, and data storage is `18L` bits
in both. Records contain two addresses and an opcode, so their representation
uses O(log L) bits each. These are explicit counts for this interpreter, not
an all-size Turing-machine implementation or a free coefficient-access claim.

For dynamic instances, recurrence (2) examines m*4^d transitions after distance
precomputation. This small reference implementation additionally copies path
tuples for deterministic tie breaking and stores O(m*2^d) entries; discovering
a plan is not charged as zero online work. Fixed B/readers and the selected
plan can be compiled once, with program construction and coefficient storage
charged in P and per-call instruction delivery charged in the complete call prices. The complete advantage survives only if the candidate's
extra P+I cost is less than the saved online bill. An actual recursive backend
must supply its complete costs, layout and precision admission. This package
does not establish that instance.

## Reproduce and verification boundary

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3.12 scripts/research_package.py --package research/observable-connector-repair
```

Expected: `PASS_OBSERVABLE_CONNECTOR strict=4 mixed=3 coherent=14
complete_xors=72_to_61 small_cases=6220 controls=14 no_new_kappa`, five passing
package tests, then `PASS_REGISTERED_RESEARCH_PACKAGE`.
A standalone replay is `python3 -I -O -B research/observable-connector-repair/verify.py`.
`--write NEW_PATH` only exports an authoring candidate; ordinary replay compares
every recomputed field against [CERTIFICATE.json](CERTIFICATE.json).

Coverage: all 1,555 width-two demand sequences of length zero through four,
each in two tariffs and two alphabets (6,220 cases), compared with a separately
implemented shortest-path oracle. Lengths through three also enumerate every
mask path. Six complete pilot programs pass 648 independent array basis-column
checks across L=1,2,3, with literal inverses; a smaller batch checks all 256
dirty inputs. There are 5,696 observation checks and fourteen semantic/domain
controls. The package tests reject altered minima, missing certificates,
modified predecessor notes and changed live source, and check read-only
relocation plus byte-identical certificate export. Separate implementations
were authored in the same AI-assisted session; this is not independent human
review or proof-assistant formalization.

Research base: `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`.
The selected certificate still names conditional kappa `0.001672660197076918`;
its source-binding baseline was checked, not its complete cold replay.
[CLAIM.txt](CLAIM.txt), [TASK.json](TASK.json), [SOURCES.json](SOURCES.json),
[PREDECESSORS.json](PREDECESSORS.json) and [OVERLAP.json](OVERLAP.json) record scope,
exact pins and bounded overlap coverage. No selected record, upstream source,
frozen package or review disposition is changed.

## Open next questions

Does a real supplier expose a common-B boundary with source mutations and
reserved future outputs matching this contract? It matters because it decides
whether the eleven saved corrections can survive admission and routing costs.
A first step is to extract one actual pair/batch of entry and exit contracts
and compare (3) with its complete existing bill. The blocker is a hosted
supplier instance, not the finite mask optimizer. This question and the
constraint on early output writes are also recorded in TASK.json.

## Credit

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex assistance**
in derivation, both implementations, verification and prose. New work is
Apache-2.0. Prose was checked against the source notes and computed evidence.

Credit woklerx's PR1439 strong coherent source-mutation interface; mightyOil's
PR1203 distinct-reader kernel criterion and dirty wrapper; Hanson's PR1246
paid output-defect construction; Sagar Thakrar's PR1199/1227 cut and sign-frame
work; Ross Richardson's retained universal-connector/PR934 lineage and the
preceding dirty-echo work. The three most direct pending notes are retained
unchanged with exact heads and hashes. No priority is claimed for cancellation,
reader kernels, BC repair, paid output correction or dynamic programming.
Concurrent PR1506 (Discussion1489) changes both B and source over characteristic
zero while retaining strong connector coherence. Discussion1493 shares dyadic
source-query tours. Neither is incorporated as an assumed result.
