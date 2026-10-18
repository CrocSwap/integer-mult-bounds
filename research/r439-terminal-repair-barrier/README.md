# No terminal XOR compensation under the R439 final-frame contract

**Scoped obstruction; no new supplier or kappa.** After the fixed C section of
PR967 and both PR1062 helper-star words, no appended elementary XOR program can
repair **any nonempty subset** of omitted final D restorations while preserving
the existing monotone common-frame rule and prescribed final target frames.
The suffix may have arbitrary length, arbitrary intermediate subspaces, and any
finite number of additional independent dirty wires. This is a written proof
with exact finite premises, not an enumeration of suffix programs or a Lean proof.

[PR1580](https://github.com/CrocSwap/integer-mult-bounds/pull/1580), Arham Tahir,
head `2490dac98eacc294bac29f136f0715343611d55e`, already excludes moving the
*unchanged* restoration gates to the terminal cut. It establishes the defect
`K(S-I)h` and asks for a conjugated restoration and target repair with legal
frames. This successor allows **arbitrary compensation** and closes that terminal
route under the retained frame contract. The defect itself is predecessor work.
PR1194/1311's restored semantic-D substitution is a separate, unaffected result.

## Contract and proof

A frame is the rational span of its listed eight-dimensional E8 label vectors.
At every XOR `d ^= s`, both operands must be in the same gate frame; each
register's frame can only increase by inclusion. Its final frame is prescribed.
These are the actual Part F rules of the pinned `xcheck_p.py`, not additional
interface restrictions. The permitted suffix has only elementary XORs; no new
COPY/ERASE, frame contraction, free relabeling or correlated/clean allocation.
Additional wires have independent arbitrary initial values and must be restored.
Their initial frames and intermediate subspaces may otherwise be arbitrary.

The monotone-frame dependency argument is an application of the boundary
reasoning used by Ali Romman's [PR1128](https://github.com/CrocSwap/integer-mult-bounds/pull/1128)
and Cinna Davis' [PR1393](https://github.com/CrocSwap/integer-mult-bounds/pull/1393);
the new result is its exact terminal-target application to these changed D
words, together with the relaxed sharp repair invoices. We include the short
argument so this application is reviewable without importing either proof.
Hanson Sun's [PR1517](https://github.com/CrocSwap/integer-mult-bounds/pull/1517)
is a related high-information confinement result on different complex interfaces.

**Frame-cone lemma.** If a final output has nonzero coefficient on a wire's value
at the cut, the latter wire's cut frame is contained in the output's final frame.
Initially the coefficient has a length-zero path. Each XOR propagates it along
an operand-to-destination path through a common frame, and every subsequent
frame contains the earlier one. Induction proves the assertion. Cancellation
can remove a coefficient, but cannot create a path violating containment. The
same proof includes any finite number of added dirty wires.

For all three pinned words the checker independently reconstructs the actual
post-C frames, before relying on final-frame declarations:

* All 111 sources and 439 helpers already have the full rank-eight frame.
* Each of the 111 targets already has its rank-seven prescribed hyperplane.
  These 111 hyperplanes are distinct. Exact rational elimination checks, for
  every target t and all 661 original cut wires, that its admissible original
  contributor set is exactly `{t}`.

Thus a legal suffix cannot deliver any original helper cut value to a target.
This includes relays through extra wires: a relay receiving a full-frame value
must itself climb to a frame containing that full space and cannot subsequently
feed a rank-seven target. Extra independent initial dirt cannot replace the
missing helper coordinate.

Let a selected restoration be `h_c ^= h_l`. Its leaf is not a center, no leaf is
repeated, and all star restorations commute. If those in a nonempty set E are
omitted, the full fixed continuation leaves

```
h_c(cut) = h_c + sum_{(c,l) in E} h_l
y_t(cut) = y_t + x_t + sum_{(c,l) in E} K[t,c] h_l
h_l(cut) = h_l.
```

Omitting these frame-zero gates changes no frame itinerary: their operands
already have frame zero, and the earlier preparation and later continuation
are retained. The post-C cones above therefore apply to every subset.
The omitted word is invertible on the 661 original coordinates, so its cut values
are independent arbitrary coordinates. Correcting target t therefore requires
adding the displayed parity of **full-frame leaf cut coordinates**. Every actual
center has a nonzero K column. Distinct leaf columns mean any nonempty E gives
a nonzero parity in at least one target; different centers cannot cancel an
independent leaf. The frame-cone lemma excludes that correction. This covers
all `2^221-1` subsets in each 221-edge word and `2^236-1` in the candidate.
It is not limited to compensation that first restores the helpers.

## Sharp scalar bill when frames are discarded

For one whole star, let w be the number of targets observing its center. The
required terminal map adds the parity of its l selected leaves to its center
and those w targets, fixing every other wire. Write t=w+1. Here l is one or two,
and w is at least eight.

* For l=1, the minimum is t elementary XORs: each changed destination needs a
  write, and direct fanout attains the bound.
* For l=2 and t>=2, the minimum is t+2, even with arbitrary restored dirty extra
  wires. Compute the parity in one leaf, fan it out to the t destinations, and
  undo the leaf update. This uses no clean temporary.

For the second lower bound, each of the t changed outputs needs a write. Any
other wire that is written must be written at least twice: if written just
once, its nonzero donor row changes its independent initial value permanently.
So any program writing a non-output has at least t+2 gates. If no non-output is
written, the target-to-target block stays invertible at every step. A target
written just once either reads one immutable independent coordinate (insufficient
for the required two-source parity), or reads a target with nonzero target-block
row (so it cannot retain its original target row). Every target then needs at
least two writes: 2t>=t+2. The t=1 exception costs two, as explicitly tested.

Consequently, relative to keeping the original restorations in D, a terminal
repair costs **w extra XORs for one leaf**, or **w+1 extra XORs for two leaves**.
These are exact minima only for one star's entire terminal correction in the
frame-free scalar alphabet. They are not minima for multiple stars jointly.
The witnesses are deliberately rejected by the real frame contract: their
helper-to-target gates require rank eight at rank-seven final outputs. There
is no legal repaired paid profile or precision claim. The original local
profile is independently recounted at rank mass 5,129; moving helper gates
alone cannot establish a complete supplier improvement.

## Evidence and reproduction

The package independently consumes only the five main-branch inputs pinned in
[SOURCES.json](SOURCES.json), at base
`1f327c6f3e3a35271c5c141d381b540bab8ad005`. No predecessor implementation is
imported or vendored. Pending PR heads are attribution/context pins in
[TASK.json](TASK.json), not executable dependencies.

```
python3.12 -I -B scripts/research_package.py --package research/r439-terminal-repair-barrier
```

The read-only replay checks rational frame cones for all 333 target occurrences,
all 880 within-star nonempty subsets, sharp relaxed repair invoices, all 661
dirty columns forward and reverse,
and a separate direct Boolean dirty witness for each repair. It recounts the
original ordered paths and paid profile. A small breadth-first search excludes
repairs shorter than four gates for the two-source/two-output case with an
additional arbitrary dirty wire. This fixture supports, but does not replace,
the general written lower bound. Controls address a missing parity undo, missing
target repair, one-output exception, reversed containment and target-only false
acceptance. Packaging tests use actual input/receipt corruptions and an optimized,
read-only minimal relocation. [CERTIFICATE.json](CERTIFICATE.json) records the
full deterministic receipt; [VERIFY.json](VERIFY.json) declares the bounded hook.

This is an F2 scalar/common-frame obstruction, not an unconditional impossibility
for alternative physical representations or interfaces. Native multistage replay,
whole-hosted emission/invoice, changed precision/tape, all-size realization,
analytic transfer and Lean formalization are not run or established. The selected
record and frozen evidence are unchanged. Local CPython 3.12.14 registered replay
and all five package tests pass, including optimized minimal export. The 20
repository research-workflow tests pass with one skip. A separate Python 3.14.7
optimized replay and the selected binding/arithmetic baseline also pass.
Hosted CI and maintainer review are separate from local validation.

## Open next questions

Move the cut **before** an affected target has reached its final hyperplane and
allow the continuation to change. Choose one candidate star and the first target
read observing its center; derive the exact cut conjugation and count every
carrier climb before searching a word. This could escape the terminal cone, but
needs a legal common-frame dirty identity and a strict complete paid improvement.
Neither is supplied here. Arbitrarily extending a terminal suffix cannot answer
that different question. Structured question and blockers are in TASK.json.

## Credit and coordination

PR1580 owns the fixed-continuation defect/subset argument and the explicit repair
handoff; woklerx's PR1017 owns the D-omission atlas. mightyOil/Philipp's PR1203
and Sagar Thakrar's PR1199 give the reader/stabilizer context. The finite words
are Sricharan Vagvala's PR967 helper stars, Sagar Thakrar's PR1062 composition,
Gareth Davidson's PR915/926 lineage, Aaron Wang's PR1015 B programs and Ross
Richardson's PR923 frame-520 program. DreamingOfClouds' PR589 on eumemic's
PR555/543 provides the retained supplier, frame semantics and owning checker,
with the PR425 scalar-interface lineage retained. This work does not claim
these constructions, their existing savings or the general reader principle.

One OS draw selected bit-helper-contract (nonce and priority revision in TASK).
The required first working example passed. The scope explicitly changes to the
terminal-compensation handoff because PR1194/1311 already cover the original
restored semantic-D question. Entry overlap covered 725 open PRs and 229
Discussion records with complete pagination; body/README/ledger search limits
remain explicit. A final refresh at 03:36 UTC covered 727 open PRs and 233
Discussion records without pagination warnings; PR1580/1194/1311 heads were
unchanged. PR1128/1393/1517 were directly read and credited as related boundary
work, on different questions and words. The [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1565#discussioncomment-18914119)
joins the predecessor's scoped thread. No novelty certificate is implied.

Prepared by Arham Tahir with substantial OpenAI Codex assistance in the proof,
code, verification and writing. One agent, no subagents or independent human
review. New work Apache-2.0; no predecessor source is copied into this package.
