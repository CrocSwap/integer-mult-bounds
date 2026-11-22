# Graded information cuts and a complete normalized relay repair

The pinned 111-port P104 graph saturates eight global dimension cuts. Its
2,776 upward scalar contacts pay exactly **4,750 total rank units**, the
minimum for the same public input and output chart bindings in the binary
constant-field model. An exact relaxation of the powered upward price still
has slack; it is not a construction. Each of the 27 native downward slots is
individually rigid under the fixed-suffix model. The fixed 326 → 531 → 1 relay loses one
binary degree of freedom, and its sharp multi-copy success rate is known.
An explicit changed normalized word restores all 630 public rows, but costs
one additional total paid rank unit and alters five dirty clear records. No
new κ bound or admitted physical supplier is claimed.

## Eight saturated cuts

For each `j = 1,...,8`, take the charts of dimension at least `j`. Fix the
inputs initially inside that region and let the other inputs vary. The
required inside targets have respective binary ranks

```
516, 627, 627, 627, 616, 616, 616, 505.
```

An incoming scalar message has at most two values, so a deterministic
fixed-schedule protocol needs at least that many contacts entering each
region. Outgoing messages and arbitrary inside computation do not increase the
number of incoming transcripts. Every upward rank-`r` contact crosses exactly
`r` thresholds. Summing the eight inequalities proves the **4,750** upward
rank minimum; the original word attains equality at each threshold. New charts,
recoded messages, unbounded local storage and retiming are allowed, provided
initial external information and schedule observations are not supplied free.
One net unit of lost upward grade is therefore impossible in this model. The
27 downward contacts contribute 63 further native grade units, for which this
upward argument gives no corresponding lower bound. Rank-preserving fusions
may change a concave powered tariff. [Proof and precise scope](DIMENSION-CUTS.md).

For every original dimension-seven chart, the union of it and chart 1 also
saturates its outside-input cut. For `{1,531}` there are 506 independent
required outputs and 506 inbound contacts. Replacing 326 → 1 by 531 → 1
makes the latter internal and leaves only **505** external contacts; arbitrary
recoding or retiming cannot repair this fixed incidence. Restoring one external
contact passes this necessary cut, without itself constructing a correct word.
The checker covers all 120 pairs, with separate lost, restored and extra-contact
controls.

## Exact powered interval relaxation

For `0 < t ≤ 1`, relax the actual endpoint and timing constraints and minimize
`Σ r^t` over multisets of consecutive dimension intervals covering the eight
cut demands. Its sharp optimum is

```
505·8^t + 11·7^t + 100·6^t + 11·3^t.
```

The superlevel intervals give a primal cover. Ordering levels by demand and
assigning successive differences `j^t − (j−1)^t` gives a feasible dual with
the same value. At `t = 1 − 0.00389046`, the native upward price is in
`[4737.618920783137811, 4737.618920783137812]` and the relaxed minimum is in
`[4712.558924499539618, 4712.558924499539619]`. The gap is approximately
**25.059996283598193 per native invocation**. These intervals are an abstract
lower bound and need not be realizable by causal messages at legal endpoints;
they exclude downward and caller costs. [Primal, dual and scope](GRADE-PRICE.md).

## Curvature and a conditional fusion budget

For a histogram of paid ranks \(r\le R\), write `G = Σ r n_r`,
`H_j = Σ n_r max(r−j,0)` and `w_j = 2j^t−(j−1)^t−(j+1)^t`.
A telescoping identity gives the exact powered bill
`G − Σ_{j=1}^{R−1} w_j H_j`; concavity makes every `w_j` nonnegative.
For the native upward histogram and the optimal interval relaxation, the
relaxed-minus-native `H_j` values at `j=1,…,7` are
`2149, 2967, 2539, 2067, 1554, 1020, 505`. The first two priced terms of the
25.059996283598193 relaxation gap are approximately **11.5746371588693** and
**6.00177780362279** per native invocation. They are relaxation headroom,
not realized savings.

Among hypothetical fusions of positive ranks with sum at most eight, the
largest saving is `2·4^t − 8^t`, approximately **0.02142834703346313** at
the trial rate. Reconstructing the complete 36-call binary raw invoice from
the pinned graph and caller shows that six such fusions cannot close its raw
deficit. Seven hypothetical balanced 4+4 fusions would pass that raw test if
all other terms were unchanged; no physical fusion or powered outer test is
established. In the original word exactly one ordered 4+4 pair has matching
intermediate chart and increasing clock, compared with 4,227 ordered 2+2
pairs. These are incidence counts only: payload availability, common owner,
legal shortcut and displaced readers have not been established. [Derivation,
source bindings and controls](CURVATURE.md).

## Individual downward feedback rigidity

At any one of the 27 native downward logical slots, keep all other interior
instructions and incidences fixed but allow the replacement bit to be an
arbitrary deterministic function of all binary inputs and every terminal
chart to decode its full history freely. The received bit must equal the
native bit or its globally known complement. Two distinct terminal charts,
each with three observations and jointly independent histories, witness each
claim. This single-slot theorem does not prohibit coordinated changes to
several slots or interior computations.

For each slot, a separate screen grants every strictly cheaper existing sender
and the destination their entire zeroed-receipt histories, even future arrivals.
None of the **4,643** candidate sender–slot pairs can determine the required
native bit. This overgrant includes geometrically incomparable sources. A
second implementation independently replays all 27 zeroed words, computes the
stock exclusions using low-pivot elimination and checks both 256-entry Boolean
truth tables for each witness pair. The result excludes a cheaper single
sender with the same destination in this fixed-suffix model; it does not prove
a global 63-unit downward lower bound. [Proof and exact scope](FEEDBACK-RIGIDITY.md).

## Sharp success probability on the relay schedule

The #8041 diagnostic changes the contact at clock 8075 from 326 → 1 to
531 → 1. By clock 10141 chart 531 has two incoming bits but sends three bits
to chart 1. Chart 1 has 502 other arrivals and 505 independent required final
bits. Even with arbitrary deterministic causal binary encoders and decoders,
the combined transcript has at most 504 bits, so the entire native map can be
correct on at most half of uniformly distributed constant binary inputs.
The literal relay attains that bound: its error is `s (r·x)` for nonzero `s`
and the specified 27-coordinate residual `r`, so correctness is exactly the
629-dimensional hyperplane `r·x = 0`.

For `k ≥ 1` jointly encoded copies and `m ≥ 0` extra input-dependent one-bit
messages on fixed, input-independent routes and times, the sharp success
fraction in the stated side-information model is `2^(-max(0,k-m))`. The
upper bound grants all side-message values to the decoder; the attaining
construction grants the missing residual bit as an **oracle** to chart 531
for each corrected copy. Physical delivery and price of that oracle remain
open. The theorem's binary scalar restriction and full proof are in
[INFORMATION-PROOF.md](INFORMATION-PROOF.md); it is not a claim against
address-dependent nonconstant field packing.

## An exact graph repair and its limits

The changed word keeps the shortened 8075 contact and recodes the later
10138 receipt, 3152 path and 3298 chain. The 124 source-clock edits in [EXACT-EDITS.json](EXACT-EDITS.json) and
[REPAIR-PROOF.md](REPAIR-PROOF.md) yield all **630 of 630** original normalized
forward rows and their exact replayed transposes. Rational projectors certify
the five changed nesting relationships. A corruption of the 3298 repair fails
row 117. All 3,433 private clear values remain nonzero; four clear values
change and a fifth owner's clear moves from chart 8 to chart 0.

The paid contact count stays 2,803. Its histogram trades one rank-five for one
rank-six contact; total rank rises **one**, rather than falling. The graph
identity alone does not prove physical erasure, live stock, general-field
adjoints, a compiler, the complete 36-call inventory, or either signed
supplier's outer application. It does not establish an improved κ.

## Relation to earlier work

- [#8036](https://github.com/CrocSwap/integer-mult-bounds/pull/8036) studies
  chart-510's two-export deletion and its residual recovery. Here the graded
  cuts cover all chart dimensions, and the constructive word uses the separate
  326/531 relay.
- [#8037](https://github.com/CrocSwap/integer-mult-bounds/pull/8037) prices
  single co-endpoint helper hyperplanes with surviving traffic fixed. Here the
  cut allows arbitrary retained-message recoding and the repair changes
  incidences and sender equations on the unrestricted binary domain.
- [#8038](https://github.com/CrocSwap/integer-mult-bounds/pull/8038) screens
  fixed-clock two-hop shortcuts. The new two-chart cut survives arbitrary
  retiming, while the repair changes multiple original operations.
- [#8041](https://github.com/CrocSwap/integer-mult-bounds/pull/8041) gives the
  fixed chart-1 cut and the relay with an unpriced residual oracle. This result
  supplies all dimension cuts, the sharp joint-copy information theorem and a
  fully explicit normalized repair with its actual extra rank and clear diffs.

The external #8027 source and #8041 lineage are pinned in [SOURCES.json](SOURCES.json).
The verifier authenticates the embedded bytes and Git blob, not the external
publication ancestry; the archive does not contain that source Git history.
The separately retained five-file prerequisite `0618e75a22cec54d1651394ef83d088551b7f026`
addresses repository CI guide and historical replay issues; it is not evidence
for these mathematical claims.

## Reproduce

Using Python 3.12 and only the standard library, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/p104-graded-cut-relay-repair
```

The registered command authenticates the one vendored graph and all checked
scripts, compares eight deterministic receipts, and exercises damaged-source,
damaged-receipt, witness, rank-preserving histogram and incidence controls,
plus wrong-oracle, missing-ADD and cut-restoration controls. The
checks include independent forward and transpose replays. They do not provide
an independent human review. For individual commands see the proof files.

## Open next questions

- Can this normalized repair satisfy the physical clear, stock, lifetime and
  general-field contracts? Implement the named changes in the real compiler,
  audit the five changed clears and both field orientations, then price the
  actual paired caller. These obligations are not supplied here.
- Can a different causal, endpoint-compatible roster realize a favorable part
  of the powered interval relaxation while respecting all other cuts and the
  full signed invoices? Begin with specific contacts and clocks; the relaxed
  optimum alone does not supply them.
- Can the relay residual be delivered without an extra net cost? Bind an
  actual source, route, clock and displaced reader. The oracle supplies no
  physical route.

## Attribution

Ali Romman supplied the graph and physical supplier. ToikY nominated the
chart-510 site, DreamingOfClouds supplied the #7852 toolkit, and Clear1nsight
prepared this follow-up with substantial OpenAI Codex assistance. The retained
predecessor credits are in [PARENT-NOTICE](PARENT-NOTICE); see
[NOTICE.md](NOTICE.md) and [LICENSE](LICENSE).
