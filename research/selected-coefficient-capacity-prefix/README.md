# Coefficient capacity prefixes and an eleven-index extension

An independent source audit finds that PR2796's halved child-extension phase
needs **11 additional index Words**, rather than its stated 10. Six parent
indices and `f` remain live while division requests four more. Two separately
built literal witnesses distinguish the exact capacities: ten rejects and
eleven succeeds. The complete child bound remains **22**, so this correction
does not invalidate PR2796's main numerical allowance.

The audit also establishes the missing prefix implication in PR2831's handoff:
for unchanged PR2697 `numeric.selected_coefficient`, the credited adapter
allowance **37,672 residue / 22 index Words** and child allowance
**20,494 / 22** bound the *next requested allocation*, before successful return
is assumed. A first inventory failure is impossible when each capacity is at
least `max(K,L+B)`, with K already allocated slots, L **all** live entry residents,
and B the corresponding allowance. This includes canonical warm free-slot
histories. It does not assume a completed reference run with larger capacity.

[PROOF.md](PROOF.md) gives the written prefix induction and first-failure
contradiction; [INDEPENDENT.md](INDEPENDENT.md) supplies a separate AI source
audit. Canonical source/program/field/value, arithmetic-margin and arena
ownership hypotheses remain. Other semantic/host errors, actual selected
catalogue membership and the complete caller's success are not proved. The
full physical reserve, supplier, formal/human proof and new kappa remain outside
scope. The original constants and arithmetic constructions belong to their
credited predecessors.

## Exact sources and checks

[INPUTS.json](INPUTS.json) binds original paths, exact heads, Git blobs and SHA256.
Runtime sources are Jose Manuel/jmbarrancoml's
[PR2697](https://github.com/CrocSwap/integer-mult-bounds/pull/2697),
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`, unchanged. Nick Petalas's
[PR2759](https://github.com/CrocSwap/integer-mult-bounds/pull/2759),
[PR2770](https://github.com/CrocSwap/integer-mult-bounds/pull/2770),
[PR2778](https://github.com/CrocSwap/integer-mult-bounds/pull/2778), and
[PR2781](https://github.com/CrocSwap/integer-mult-bounds/pull/2781) supply primitive,
evaluator, constructor and adapter lifetimes; Arham Tahir's
[PR2796](https://github.com/CrocSwap/integer-mult-bounds/pull/2796) supplies the
closed child allowance. Their proof/scope texts are preserved unchanged in
`evidence/`; relative links within those snapshots resolve at their source PRs.
The runtime loader authenticates before compiling source bytes directly.

Python 3.12 or later, standard library only:

```sh
python3.12 -I -Werror -B scripts/research_package.py \
  --package research/selected-coefficient-capacity-prefix
python3.12 -I -O -Werror -B research/selected-coefficient-capacity-prefix/independent.py
```

The primary replay checks every pending `Arena.zero` request in nine successful
literal coefficient fixtures and three actual underbudget failures. The fixtures
cover good ranks1/42, fallback and halved-unit children, F3/Z9, depth0/2,
borrowed residents and retained warm backing. They recover the predecessors'
sharp residue witnesses and the child index22 witness, check exact outputs,
entry ownership/bytes/heads, erased free slots and source rollback on the three
quota failures. These finite cases are not an exhaustive catalogue or proof of
all-parameter success. The integer adapter oracle is an unchanged, credited
export from PR2781; the separate half witness does not import the primary
fixture, probe or oracle.

Eight controls reject the false ten-index phase bound, an understated prefix
budget, a retained-f source mutation, corrupted sources, missing source pins
and changed typed receipts; they also require observation of the actual rejected
index request. Normal replay is read-only and compares all [RESULT.json](RESULT.json)
fields. `--emit` prints a fresh receipt without replacing the committed one.
[VALIDATION.md](VALIDATION.md) records final commands and environment limits.

## Scope and credit

This takes [PR2831's released handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/2831),
narrowed to closed coefficients under the priority-5 stock card. The random
picker's recursive-interface suggestions and explicit scope override, live
metadata overlap and exact freshness are in [TASK.json](TASK.json). The
[canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18961966)
records the bounded investigation. No other construction is modified.

Credit Jose Manuel/jmbarrancoml for the source and retained lineage; Nick Petalas
and Arham Tahir for the audited bounds; Ross Richardson for PR2825/2831; David
Arias and ywz65 for the separate recursive/physical work. The source
[vendor/NOTICE.md](vendor/NOTICE.md) and Apache-2.0 license are retained. New
material by Ross Richardson with substantial OpenAI Codex assistance, including
a separately implemented math-storage-lifetimes AI audit. No independent human,
formal-kernel or hosted-CI verification is implied.

## Open next questions

1. Complete the non-coefficient `Consumer.apply` prefix proof before replacing
   its successful-call premise by actual numerical capacity admission. Start
   with initialization/validation and trace/Layout/stream allocation requests
   from PR2821/2825 at the same all-entry-resident baseline.
2. Bind the complete chronological inventory to physical banks, including
   payload/count/key/program/continuation/bookkeeping and movement. This
   numerical component cannot supply the missing representation/outer grants.

The corresponding first steps and blockers are structured in TASK.json. This
session stops at the coefficient implication and corrected extension phase.
