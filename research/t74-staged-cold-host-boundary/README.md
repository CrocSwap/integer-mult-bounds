# The boundary of staged cold-host recovery

**Scoped obstruction and handoff; no improved κ.** On both PR2823 words for
`473 → 277`, arbitrary host-only staged recovery after the final inherited host
read cannot restore the required reference at end rank at most eight. This
closes a specific part of PR2823's open staged-recovery question; it does not
exclude precomputation that changes other registers or the consumer contract.

## Result and reason

At the cut before B1202, the required reference is
`z = x277 - x100 - x226 + x54`. The host's necessary rank-seven frame contains
vector 33. Reading 100 before B1429 carries that vector into target 112, whose
fixed output frame excludes it; reading 100 later forces host rank nine.
Source 67 has the same obstruction at B1430/target 169. Those two sources and
two targets are the only registers that ever carry an independent variation of
cut coordinate `x100`. Consequently any valid host-only additions or scalings
remain insensitive to a coordinate whose required coefficient is −1.

A second necessary-coordinate screen checks all 22 naturally retired cold
FULL-ended helpers compatible with the host's rank-eight cap. None carries
original input 100, so no rational combination of their unchanged rows, even
with initial cold-helper preloads, supplies the missing recovery increment.
This is a restricted precomputation screen, not a census of changed circuits.

[PROOF.md](PROOF.md) states the exact grammar, invertibility premises, witnesses
and induction. [TASK.json](TASK.json) records the cost ledger and stopping rule.
The frozen inputs and frame engine come from
[PR2823](https://github.com/CrocSwap/integer-mult-bounds/pull/2823) at
`ca5eead6afd871614ceb635679edbcc3d04b9d8c`; hashes and Git blobs are in
[SOURCE-PINS.json](SOURCE-PINS.json). The original task/base provenance is in
[SOURCES.json](SOURCES.json).

## Reproduce

From the repository root, using standard-library Python:

```sh
python3.12 -B scripts/research_package.py --package research/t74-staged-cold-host-boundary
```

A Git-free package export can run its checks directly:

```sh
python3 -I -B verify.py
python3 -I -B exploration/natural_bank_coordinate.py
```

The staged receipt checks both providers, every 756 remaining scalar events per
provider, prefix invertibility, two legal rank-eight single-read controls and
six rejected semantic mutants. Local replays use Python 3.14.5 and 3.13; Python 3.12 is the registered CI target and was not available locally. Stored receipts are evidence for comparison;
the checkers recompute their findings. A separate AI review uses explicit sets
of GF(2)^9 vectors and a register-version inclusion graph to check the frame
facts without the inherited engine, plus a separate sparse coordinate replay.
This separate implementation covers the staged theorem; it does not audit the natural-bank screen. A Git-free read-only export passed all three entrypoints with unchanged files; both engine-consuming entrypoints rejected corrupted source before execution. Package metadata/source pins passed the latest repository runner. The full registered runner requires Python 3.12 and was not run locally. No independent human review or formal proof-assistant result is claimed.

## Cost and limits

PR2823's authenticated exact-pricing replay was also rerun as an inherited
control. Its ideal width-eight ledger leaves less than 0.005786 H1-equivalent
extra **net** moment per call relative to pinned PR2802. That is an optimistic
pattern-budget constraint, not a realizable owner allocation. Splitting an
already paid recursive rank must be charged by the net profile change; counting
only newly introduced children would be misleading.

This package supplies no profitable changed word, full operator cancellation
for a new circuit, native/physical stock or precision admission, chronological
owner fill, outer transfer, new κ, or full selected cold replay. The selected
record is unchanged. A different precomputation or target contract can escape
these obstructions.

## Open next questions

Can a changed precomputation put the missing input 100 component into an already
paid compatible bank before the target barrier? First emit one literal circuit
with arbitrary dirty inputs, all initial compensation, restoration and cleanup,
then check its complete rank-neutral local profile and inventory against the
small inherited budget. Only a candidate passing that gate justifies native,
owner and outer integration. No such completed circuit is currently supplied.
Structured questions and blockers are in [TASK.json](TASK.json).

## Coordination and credit

Canonical claim/finding:
[Discussion2612](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-18962107).
Scientific main baseline was `6e40ee619ab5ec7240c3e5299035e7e4d4800583`;
publication branch was refreshed to `8dc7cef9d60b4eb974f61362b277cbc85121fdda`.
Priority revision 5, selected record and relevant guidance were unchanged.
Freshness and coverage limits are recorded in TASK.json; absence of a metadata
match does not establish novelty.

New analysis prepared for Yiyang (@Lyy-iiis) with substantial OpenAI Codex
assistance, including parallel mathematical and adversarial review agents.
Credit Marius-Paul Dumitrean for the J lead, PR2802 and PR2823; Tekalign,
DavidAriasC, Mason Hale, Cinna Davis, Philippe Van Velzen, Jeremy Kothe and the
retained borrowing/native/owner lineage. Exact inherited notices are retained
under vendor. New work is Apache-2.0.
