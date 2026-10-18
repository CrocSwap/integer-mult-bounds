# Common-flag data floor with clean and disposable workspace

The common-flag bill remains `s >= Wm` when W counts independent designated
data inputs and all other workspace may be clean, copied, changed in width
or discarded. Garbage need not be restored. This closes explicit interface
exclusions in Navinor's PR825 by applying Jose Manuel / @jmbarrancoml's PR1757
outgoing-transcript proof to designated demands alone. It is a short credited
corollary, not a new cut principle or a new nonlinear-gate obstruction.

[PROOF.md](PROOF.md) states the precise contract and argument. Every physical
wire is charged; every gate has one frame on all ports. All frames must
preserve a common complete flag, possibly over a characteristic-zero extension.
The circuit is fixed and deterministic, with independent designated inputs
recovered at distinct designated sinks. Local constant creation, copying,
erasure, nonlinear functions and unconstrained garbage are allowed.

The prospective escape this closes is **changing workspace lifecycle while
retaining common-flag geometry**: a proposed copied-stream construction cannot
obtain a positive data-normalized rank deficit merely because intermediate
registers are clean or disposable. For the declared wire tariff and useful
volume W, its moment is at least one. No supplied mechanism with different
frames or a different coverage law is ruled out. In particular, this does
not resolve PR2167's arbitrary clean-ancilla question in its rational
group-algebra model, which lacks the common-flag premise used here.

## Executed changed interface

The independent checker represents actual DAG wires by source, destination
and destination port. It evaluates every input assignment and reconstructs
outside vertices using only outgoing cut messages and fixed outside inputs.
It enumerates every binary vertex partition in these finite fixtures:

* Clean constant allocation, copy fan-out, unused/discarded scratch and a
  required surviving data sink, with bill 2 in address dimension 2.
* Nonlinear scratch creation and cancellation with two recovered data values
  and unconstrained garbage, bill 4. A fractional noncommuting triangular
  frame assignment has bill 13 and satisfies the same floor.
* An arbitrary dirty auxiliary source whose final value need not be restored.
* All 256 three-input Boolean truth tables as scratch functions in a full
  copy/cancel graph. Every table entry executes on the eight independent
  inputs; only two sources are designated data demands.
* One independent symbol transported once and copied to three outputs. Its
  bill is 2, disproving the incorrect normalization `W=3` which would demand 6.

These graphs have changing live width and outputs outside the old complete
all-role permutation contract. Copy fan-out is represented by separate
physical wires, not by an uncharged outside observation. Written proof covers
arbitrary gate arities and finite alphabets; executable evidence is Boolean
with one output per vertex, arbitrary fan-out, and up to three input ports.
It is not an exhaustive census of all circuits or a nonlinear supplier.

Eight executable rejection controls cover erased required information,
missing outgoing edges, duplicate demands counted as volume, missing terminal
frame shift, violation of the supplied triangular flag, a nonlinear endpoint
that passes zero/one-hot tests, and omission of one physical fan-out edge.
The last two prevent replacing full semantics with a linear-column or
deduplicated-wire test. The eighth control separates locally created copies
from a preloaded data-dependent copy outside the source frame: with two
correlated source values `(x,x)` the designated endpoint passes at rank bill
zero, but the full independent-input endpoint fails. Thus simply saying
"auxiliary inputs are fixed" is insufficient if they already depend on data.
The free different-frame gate countermodel is written
in the proof; it is not counted as an executed check.

## Reproduce

```sh
python3.12 -I -O -B research/common-flag-disposable-workspace/verify.py
python3.12 scripts/research_package.py --package research/common-flag-disposable-workspace
```

Both are read-only. Expected: `PASS_COMMON_FLAG_DISPOSABLE_WORKSPACE cases=262`.
The registered hook also runs real-file source/proof/receipt corruption controls
and a Git-free minimal-export replay. The JSON receipt contains every fixture's
wire count, input count, rank bill, partition count and reconstruction count.
Source bytes authenticate before the checker is imported. Full selected cold
replay, hosted CI, proof-kernel checking and independent human review are not
claimed. The universal implication rests on the written proof, not the census.

## Scope and credit

Main base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The selected record is unchanged. The selected research baseline passed its
binding-only check. [TASK.json](TASK.json) records the changed card scope;
[SOURCES.json](SOURCES.json) pins exact unchanged inputs; [OVERLAP.md](OVERLAP.md)
records current and retained coverage separately.

Credit Navinor / PR825 for the rational common-flag obstruction, Jose Manuel /
@jmbarrancoml / PR1757 for the outgoing-transcript proof and nonlinear extension,
and the retained OpenAI finite-shear contract. The all-role circuit tests in
`nonlinear-cut-exhaustive-audit` remain distinct; their enumeration is not
repeated here. No prior proof or executable is copied or changed. Prepared for
ywz65 with substantial OpenAI Codex assistance in proof, implementation,
validation and writing, including separate AI review. Apache-2.0.

## Open next questions

Can a concrete copied-stream candidate with non-common-flag frames satisfy
its complete data-only boundary below Wm? Start with one explicit finite DAG,
independent designated inputs, all physical wires and actual frame assignment;
verify its full endpoint before pricing it. A successful circuit and complete
physical conversion are missing. Neither this corollary nor a failed bounded
search excludes that changed geometry.
