# Idle 48-pair repartitions on the #1094 frontier

This research candidate improves on the repository's current reviewed result,
#1094 (`κ = 0.001672660197076918`), by repartitioning 1,825 completely idle
rank-48 child pairs as `48 + 48 → 45 + 51`. It gives the exact native
candidate `κ = 0.001672846574134982`; the conservative price is
`0.001672846571282754`. The native gain is
`0.000000186377058064`, or about `0.01114%` relative to #1094.

For each selected pair, three axes are moved from one rank-48 child to the
other. The pair keeps the same total axis set, so its exact Z4 phase polynomial
is unchanged. The moved axes commute with all stage X/Y translations and both
children's terminal translations. Each changed child remains an independent
orthogonal axis set, neither slot appears in the frozen owner map, and no
hosted chart or invocation changes. The resulting maximum child rank is 51;
the finite halving guard remains `73² = 5329 > 2·51² = 5202`.
An exhaustive matching over each replica/port group confirms that 1,825 is
the maximum number of disjoint pairs for this move and commuting condition.

## Reproduction and receipts

The retained selected replay and T16 source archive make the candidate
reproducible. First extract them, restore the exact frozen data inputs, emit
the baseline hosted template, and audit that emission:

```sh
mkdir -p /tmp/frontier1094 /tmp/rarepkg
mkdir -p /tmp/frontier1094/baseline-audit
tar -xzf research/community-frontier1094-audit/selected-replay.tar.gz \
  -C /tmp/frontier1094 candidate/strict/global
tar -xzf research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz \
  -C /tmp/rarepkg
cp research/complex-t16-rare-pattern-exchanges/data/{SPEC.json,PLAN.json,OWNERS.json.gz} \
  /tmp/rarepkg/data/
WITNESS_SPEC=/tmp/rarepkg/data/SPEC.json \
  python3 -B /tmp/rarepkg/code/emit_allcold.py \
  --base /tmp/frontier1094/candidate/strict/global/base \
  --owners /tmp/rarepkg/data/OWNERS.json.gz \
  --plan /tmp/frontier1094/candidate/strict/global/PLAN.json \
  --out /tmp/frontier1094/baseline-hosted
WITNESS_SPEC=/tmp/rarepkg/data/SPEC.json \
  python3 -B /tmp/rarepkg/code/audit_allcold.py \
  /tmp/frontier1094/candidate/strict/global/base \
  /tmp/frontier1094/baseline-hosted \
  /tmp/frontier1094/baseline-audit/ASYNC-AUDIT.json --mutation-controls
python3 -B research/frontier1094-idle-exchanges/build_candidate.py \
  --replay-root /tmp/frontier1094/candidate/strict/global \
  --baseline-hosted-root /tmp/frontier1094/baseline-hosted
cp research/frontier1094-idle-exchanges/replay/SPEC-candidate.json \
  /tmp/rarepkg/data/SPEC.json
T16_SOURCE_CODE=/tmp/rarepkg/code \
T16_BASE_HOSTED=/tmp/frontier1094/baseline-hosted \
WITNESS_SPEC=/tmp/rarepkg/data/SPEC.json \
  python3 -B research/frontier1094-idle-exchanges/audit_allcold_idle_overlay.py \
  /tmp/frontier1094/candidate/strict/global/base \
  research/frontier1094-idle-exchanges \
  /tmp/frontier1094/candidate-audit.json --mutation-controls
python3 -B research/frontier1094-idle-exchanges/verify_overlay.py \
  --replay-root /tmp/frontier1094/candidate/strict/global \
  --baseline-hosted-root /tmp/frontier1094/baseline-hosted
```

The fresh emission is compared byte-for-byte in
[`BASE-EMITTER-REPLAY.json`](BASE-EMITTER-REPLAY.json). The candidate controller
command, full invoice and strict assembly are recorded in
[`replay/INTEGRATION-METHOD.md`](replay/INTEGRATION-METHOD.md). The exact global
assembly passed in strict mode using
[`replay/SPEC-candidate.json`](replay/SPEC-candidate.json); its full output is
[`replay/ASSEMBLY.json`](replay/ASSEMBLY.json), and the invoice is in
[`replay/audit/PREFIX-AND-INVOICE.json`](replay/audit/PREFIX-AND-INVOICE.json).
The finite row coefficient remains 16469, and every strict invoice and outer
assembly check passes.

The baseline emitter was rerun and reproduced the archived #1094 template,
idle frames, sigma maps and hosted summary byte-for-byte. Then the independent
serialized controller/owner auditor was adapted to read the explicit axis
overlay and rerun against the candidate; all 15 controller mutation controls
were rejected. The official mixed-provider invoice, strict global assembly,
all 69 assembly controls, and all 12 bit-supplier controls passed.

This remains a finite conditional construction, not a complete Lean theorem.
The candidate is not yet the repository's reviewed selected result; it needs
independent research review. Existing all-size compiler, common-label and
mutable-source realization, precision/tape, recovery, and analytic-transfer
obligations remain conditional.

## Open next questions

- Can an independent reviewer reproduce the 1,825-pair maximum-matching bound
  from the frozen #1094 replay and verify the overlay without trusting the
  candidate builder? The first step is to replay the package instructions and
  inspect the pair-group matching certificate; the blocker is the size of the
  retained replay and its external pinned engine sources.
- Can another commuting repartition or a coordinated move across more than two
  idle children improve the exact invoice while retaining the frozen controller
  and phase constraints? Start by searching larger local exchange patterns;
  the main blocker is proving a global maximum over those broader move classes.
- Which conditional proof obligations prevent this finite κ gain from becoming
  an end-to-end multiplication theorem? Start from the selected-result record
  and its review; the blockers include the compiler, mutable-source, precision,
  recovery, and analytic-transfer arguments listed above.

## Predecessors and attribution

This package builds on the repository's reviewed #1094 selected replay and
retained T16 rare-pattern exchange source. The earlier #1042 idle-transvection
exploration supplied an initial search idea and pricing helper; this candidate
keeps its own pinned pricing support so it can be replayed without importing
that unreviewed package. The #1042 notes remain unchanged.

Prepared with OpenAI Codex assistance. The exact pricing support pins each
moment and outer engine by source-file SHA-256 before loading it.
