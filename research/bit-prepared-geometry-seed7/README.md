# Prepared geometry for complete exact bit-word checks

**Verification tooling; no new construction or kappa.** An opt-in wrapper for
PR589's frozen `xcheck_p.py` validates E8 labels, lattice and frame geometry
once, then replays each candidate word completely. Changed non-gate fields use
the original full checker. Frozen source code and the selected frontier are
unchanged.

## Result and measurement

The differential replay covers 16 specified fixtures on all 661 symbolic input
columns: 111 sources, 111 dirty targets and 439 dirty helpers. It compares every
mathematical receipt and each rejection type/message with a fresh full checker.
Four additional controls test template mutation, returned-state mutation,
changed checker bytes and the initial checker pin. Committed exact receipts and
measurements are in [EVIDENCE.json](EVIDENCE.json).

The three timing inputs are the selected word, two canceling D gates, and two
canceling C gates. The last preserves the full scalar identity but makes the H4
literal-reversal flag false: a successful scalar replay is not interface
admission. Both paths receive identical inputs, with alternating execution order
and three repeats per word. Preparation is priced separately and included in
batch speedup. Timings depend on machine/workload and never decide acceptance.

On Linux x86_64 / CPython 3.12.3, the nine paired checks measured a median
**1.44045 s full versus 0.12134 s prepared (11.87x)**. Preparation cost
**1.38884 s**; the complete nine-word batch including setup was **5.12x faster**.
These are fixed-input measurements, not a claim about all searches.

## Why reusing geometry preserves this check

This argument is specific to the pinned checker SHA256 in [SOURCES.json](SOURCES.json),
not a generic guarantee for later checker versions.

1. `Word.__init__` (source lines 144–167) reads the header, labels and frames. It
   constructs dimensions, perpendicular bases, FULL/ZERO identifiers and an
   empty nesting memo. It does not read D/A/B/C.
2. `Word.labels` (171–216) depends on those same fields: exact lattice/root
   validation and closure of every frame. The prepared key serializes **every**
   JSON field except D/A/B/C, including annotations, starts/finals, retained
   helpers and scatter. Thus an identical key preserves all initialization and
   label dependencies. JSON list order and scalar types are preserved.
3. Each check deep-copies the prepared geometry and the candidate word. It runs
   the original `full`, `totals`, and `interface` calls in the same order as
   `check` (397–405). Gates, chronological frame legality, all dirty-input
   endpoints, retained COPY ranks, and every H1–H5/U/J/K/restoration flag are
   checked afresh. The geometry's nesting memo begins empty for every candidate.
4. Any non-gate change falls back to the original `check`, including invalid
   geometry and legitimate annotations. Checker bytes are SHA256-checked on
   preparation and each call. The module executes those hashed bytes directly,
   bypassing bytecode caches. No candidate result is cached, and returned state
   cannot mutate the internal template.

The code contract is JSON trees, serial use, and this exact checker. The cache
holds one template. It does not accelerate geometry changes or validate a new
checker version. The differential fixtures support this code argument; they are
not a formal verification of the full multiplication theorem.

## Use and reproduce

From repository root (Python 3.12, standard library only):

```sh
python3.12 -B scripts/research_package.py --package research/bit-prepared-geometry-seed7
```

Expected: `PASS_BIT_PREPARED_GEOMETRY: 16 exact oracle cases, 4 isolation controls,
661 symbolic columns`, followed by registered-package success. It also compares
the deterministic receipt with the committed evidence. To reproduce the timing:

```sh
python3.12 -I -O -B research/bit-prepared-geometry-seed7/verify.py --benchmark
```

For a serial candidate stream, import `PreparedBitChecker` from
`scripts/prepared_bit_checker.py`, prepare with the checker path and template
word, then call `.check(candidate)` instead of the frozen module's `.check`.
It returns the same `(Word, labels, full, H, C, info)` shape and original `Reject`
exceptions; catch them with `except prepared.reject_type` because the wrapper
loads its own pinned module. Inspect all H/C flags for interface admission. `geometry_hits` and
`full_fallbacks` count attempted calls, including rejected candidates.

## Scope, pins and stopping rule

Base: `81e81af67714bdc8d1693b0bf5c29468b92f62ff`; OS assignment seed **7**, bit
supplier track. Exact file blobs and SHA256 pins are in SOURCES.json. The selected
certificate at that base is #1094, kappa
`836330098538459/500000000000000000`; its bit input is PR589 on PR555. Its
inherited all-size/compiler, common-label/mutable-source, whole-call hosting,
precision/tape, analytic and H1–H5 assumptions remain unresolved by this tool.
The complex supplier remains binding in the selected certificate.

Three initial narrow candidates and their overlap are recorded in TASK.json.
The bounded cold-A screen examined all 439 helpers of the selected word and
found none with exactly one A write and no A donor use. This closes only that
eligibility screen, not a carried-basis mechanism or resynthesis. One pivot
produced this tooling side result; the bit-helper-contract construction
acceptance gate is not met. The experiment stops after the 16 fixed fixtures,
four isolation controls and nine timed checks per path. Seed7 fixes the first
alternating path order. No larger search or bound improvement is claimed.
Claim: [Discussion1653](https://github.com/CrocSwap/integer-mult-bounds/discussions/1653).

## Open next questions

Does preparation help a real native bit-search stream containing many rejected
words? That affects practical utility because early failures and fallback rates
vary. Start with one pinned reproducible candidate stream, compare full receipts,
and report complete batch timing including setup. The blocker is a concrete
search workload. TASK.json records this question and its first step.

## Credit

The checker is eumemic's PR555 punctured-word adaptation with substantial
Anthropic Claude assistance. The selected tuned word is DreamingOfClouds' PR589
(head `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`) on eumemic's PR555 (head
`65a6bc19f820c8b1873f65a517bcf70cd6887223`). Their frozen files retain their
Apache-2.0 notices. This wrapper changes neither algorithm nor mathematical
coverage of those source calls.

Concurrent thakrarsagar PR1584, head
`dddaa467d2bbbcf45bcc6b2cf92a78e8d1c4ccad`, speeds finite-bit block-core transition
checks. It is a distinct workload, not a dependency or an imported implementation;
this contribution reuses complete E8 geometry across candidate words.
New work: Cinna Davis (1337isnot1337), with substantial OpenAI Codex assistance
in implementation, experiments and documentation. Apache-2.0.
