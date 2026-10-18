# One raised join beats the least legal frame profile

The least forced frame assignment need not minimize a concave paid-call
bill. On PR1868's legal single-writer fixture, raising only A[591] to its
original rank-four frame and propagating forced joins replaces six paid
climbs with three. The complete histogram changes by

    -4 C1 - C2 + 2 C3.

For every cost C_r=r^p with 0<p<1, the exact saving is
4+2^p-2*3^p>0. All 661 arbitrary dirty inputs, the original scalar word,
all final frames and all nine rank-seven COPY frames are preserved.

This answers open question 2 in Aaron Wang's
[PR2428](https://github.com/CrocSwap/integer-mult-bounds/pull/2428), which
explicitly suggests testing coalescing joins on Sagar Thakrar's PR1868
fixture. The predecessor already identifies the possibility; the explicit
A[591] witness and its complete checked cost difference are this result.
Its 312 geometric exclusions remain untouched. This raised profile still
costs more than the fixture's original frame profile. It is not a new best
word, an optimum, a native supplier admission or a new kappa.

## Construction and complete boundary

Start with the pinned PR1062 candidate. Make only the known PR1868 scalar
edit: remove the **terminal** D restoration `506 ^= 374` and replace the
donor `[374]` of A[288] by `[69]`. This is the predecessor's 11,499-ADD
fixture; the source candidate costs 11,500. The earlier identical D gate
is retained. Source files and contextual PR2428 head are pinned in
[SOURCES.json](SOURCES.json) and [PREDECESSOR.json](PREDECESSOR.json).

For the least assignment, each gate uses the rational span of its operands'
current frames, with fixed starts and finals. For the new assignment, use
the same rule except at the zero-based gate **A[591]**, stored as
`[266,243,[244]]`. There take the join with the source's frame 266. This
raises the gate from span{line9,line10,line13}, rank three, to the original
rank-four frame with labels `{1,2,4,7,8,9,10,11,12,13}`. Propagate subsequent
forced joins in the usual way. No scalar gate, donor or order changes.

The only changed paid climbs are:

| Register | Least assignment | Raised assignment |
|---|---|---|
| 243 | 1->3 at A[591], 3->4 at A[592] | 1->4 at A[591] |
| 244 | 2->3 at A[591], 3->4 at A[599] | 2->4 at A[591] |
| 247 | 1->3 at A[595], 3->4 at A[596] | 1->4 at A[595] |

Every other paid climb is identical. The verifier checks this from the
complete word, rather than assuming a local edit has only local effects.
It checks rational containment at every climb and final boundary. It also
compares each of the nine COPY spans with the original pinned word's
scatter-time span, in both containment directions, all with rank seven.
The inherited clean COPY temporary is created and erased exactly. The
661 persistent registers remain arbitrary dirty inputs throughout the
scalar endpoint proof, including forward and reversed literal execution.

| Rank | Least forced profile | One raised join |
|---|---:|---:|
| 1 | 1494 | 1490 |
| 2 | 1305 | 1304 |
| 3 | 47 | 49 |
| 4 | 44 | 44 |
| 5 | 103 | 103 |
| 6 | 10 | 10 |
| 7 | 19 | 19 |

Both rank masses are 5,129; the child count falls from 3,022 to 3,019.
The removed increments are `(2,1),(1,1),(2,1)` and the replacement
increments are `3,2,3`. For 0<p<1, strict subadditivity
`(a+b)^p < a^p+b^p` for positive a,b proves the saving for each of the
three merges, hence the stated inequality. This is a universal symbolic
cost comparison, not a floating-point sample. The direct source profile
`{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}` is only a positive control;
the construction does not improve that profile.

## Evidence and reproduction

```sh
python3.12 -I -O -B research/r439-coalesced-legal-join/verify.py
python3.12 -B scripts/research_package.py --package research/r439-coalesced-legal-join
```

No predecessor executable is imported. Exact rational elimination is
cross-checked by modular elimination at prime 1,000,003 for every encountered
span. [RESULT.json](RESULT.json) retains the exact changed climbs, gate
labels, histograms and boundary evidence. Normal verification compares the
receipt without changing it. Four controls reject missing scalar correction,
a full-frame target leak, a missing raised join and a changed COPY frame.
CPython3.12.14 registered optimized replay, Git-free relocation and three
actual receipt/source/join corruptions pass locally. A separate AI reviewer
read the full proof with no actionable finding. The PR1062 baseline passes
661 columns and eight controls. This is orientation evidence only; no selected cold
replay or hosted CI success is claimed.

The unchanged scalar word makes the all-input operator equality independent
of the frame repricing, but physical validity of the new climbs still needs
native recipes, host placement, precision/tape bounds and recursive admission.
The same exclusions apply to the predecessor's word-level free-frame model.

## Open next questions and credit

What is the cheapest legal reframing of this scalar fixture? A bounded next
step is to optimize compatible raised joins while retaining each pinned COPY
and final frame. This witness disproves least-profile optimality but supplies
no global lower bound or optimizer. A physical implementation must be priced
separately before any supplier or exponent claim.

Credit Sagar Thakrar/PR1868 for the scalar absorption and PR1062 word;
Aaron Wang/PR2428 for the forced-carry closure and exact optimization handoff;
Adam Gall/PR1913 and Aaron Wang/PR1937 for the absorption domains; Sricharan
Vagvala/PR967 and the retained R439/eumemic lineage for the word and frame law.
New witness and checker prepared for ywz65 with substantial OpenAI Codex
assistance. No human review, proof-assistant verification or literature
priority is claimed. Apache-2.0; predecessor notices are retained.
