# Faster exact replay of the corrected seven-source word census

This package accelerates Nicholas Stone's corrected PR2973 census by replacing
loops over prefix states with two 64-bit permutations. It preserves the ordered
traversal, both Hamming-weight collision budgets, exact leaf coverage, counters,
witness files and cap/failure behavior. This is a **tooling improvement** with a
written representation-equivalence proof, not a new kappa or a new exclusion.

The original complete domain is six cases: L20 splits (10,10), (10,9), (10,8),
(9,9), (10,7), and L18 split (9,9). Together they visit **917,753,852 nodes**.
The retained finite conclusion is `22 <= f(7) <= 24` in Ross Richardson's PR943
singleton prefix-walk model. The length22 question remains open here.

## Mechanism and evidence

On the final registered replay, the complete six-case census takes
**226.66 s -> 100.52 s (2.25x)** on this Linux/GCC host.
Every non-timing field and ordered witness file agrees. The earlier full
same-input experiment measured 2.26x; both runs are local measurements.

Deleting coordinate bit0 is a bijection on each *fixed weight-parity coset*.
The two classes remain separate. Keeping their compressed masks relative to
the current prefix q turns a one-coordinate walk step into one block swap.
The resulting masks directly give the new point's pair differences. This
removes the per-extension scans without adding a pruning rule or a cache.
[PROOF.md](PROOF.md) states the invariants, rollback and leaf-coverage argument.
The source-bound adapter leaves the original package untouched.

Same-input measurements are recorded in [RESULT.json](RESULT.json), with
compiler, flags, source hashes and separate search/wall times. The comparison
alternates baseline/replacement order and freshly executes every case from the
empty prefix, without a cap. Timing is machine-dependent and is not an
asymptotic integer-multiplication improvement. Compilation and the additional
verification controls are outside the reported census wall times.

| Case | Nodes | Original wall s | Accelerated wall s |
| --- | ---: | ---: | ---: |
| n7_l20_10_8 | 14,450,133 | 3.812 | 1.789 |
| n7_l18_9_9 | 951,416 | 0.258 | 0.120 |
| n7_l20_10_7 | 35,241 | 0.009 | 0.007 |
| n7_l20_9_9 | 67,643,567 | 17.661 | 8.324 |
| n7_l20_10_9 | 244,301,902 | 61.783 | 27.844 |
| n7_l20_10_10 | 590,371,593 | 143.133 | 62.432 |

Checks include the predecessor's 164 raw-product comparisons and 36 capped
seven-source Python comparisons; a new independent scalar reconstruction of
every internal set/collision counter in those runs; all 448 permutation
basis/label cases; sanitizer-trap checks in dimensions 1 through 7; positive
universal words; exact ordered witness comparisons; partial/multiple-shard
controls; four rejecting implementation mutants and two source/adapter
invalidation controls. The known wrong-budget counterexample `01021323` is
required to occur in the actual emitted witnesses.

The complete large replay compares every JSON field except validated finite,
nonnegative `seconds` fields, and compares the witness bytes. It shares the
predecessor's DFS and pruning logic, so it is **not a second independent
full-domain implementation proof**. The independent state oracle runs on the
stated bounded domains, including the complete L20 (10,7) case. The unchanged
full mathematical justification is pinned in the predecessor `MATH.md`.

## Reproduce

Python 3.12+ and a C11-capable `cc` with unsigned 128-bit integers and the declared
sanitizer-trap flags are required. No third-party Python dependencies, network
or solver is needed. Both engines execute every benchmark case afresh; the
stored predecessor counts are a comparison.

```sh
python3 -I -B research/f7-parity-mask-replay/verify.py --work /tmp/f7-mask-replay
```

Use a **new** work directory. Expected markers are
`PASS_F7_PARITY_MASK_CONTROLS` and `PASS_F7_PARITY_MASK_COMPLETE`, followed by
the fresh receipt path. `--controls-only` and `--benchmark-only` split these
obligations and label their output accordingly. The registered package hook
runs both, with separate bounded timeouts. Full replay takes several minutes
on the recorded Linux host. The generated `accelerated.c` in the work directory
retains the original command-line interface and compile-time N/L limits.

Direct replay requires the six source paths declared in `VERIFY.json`; hashes
are checked before compilation/import. Its `.py` inputs execute from source
with a private bytecode-cache location. No source restoration, repinning or
production adoption is performed automatically. The generator's Git provenance
checks additionally require the recorded base history.

## Scope, provenance and credit

Registered Python 3.12 replay passes. A read-only Git-free export under
optimized Python 3.14 reproduces every control result. These are local checks;
hosted CI and independent review are separate.

Scientific base: `472f4e78b338215f0b2c3f590b0bc7d2f03c02eb`.
Submission synchronized to `b3f3ee0392b71b118fd086a6eaf6b4cab54ef455`; relevant
guidance, selected record, replay runner and predecessor inputs are unchanged.
PR2973 head: `d48f3945dbb1ef5d06835744c4082b3bd04181c0`.
Corrected C source SHA256:
`265ead915d1b490c1923bce9b894ecac60f6195fc3d2ceadd6b25077238f415a`.
All input pins are in [SOURCES.json](SOURCES.json). Seed 88 selected verification
engineering and the L20 (10,8) pilot. [TASK.json](TASK.json) records the three
candidates, overlap/freshness, stopping rule and
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18977093).

Credit Nicholas Stone for the corrected engine, mathematical correction and
independent Python/brute oracles; Ross Richardson for the PR943 model;
Aaron Wang/opencode for the preceding census and set-cover research; and
Douglas Colkitt for the retained construction/record lineage. This work adds
the moving-origin parity representation, equivalence argument, state oracle,
mutant controls and same-domain benchmark. Frozen sources and `upstream/`
remain unchanged. Tekalign (@tekuuu), with substantial OpenAI Codex assistance
in research, code, checks and writing. Apache-2.0. No independent human or
formal-kernel review, new supplier or full multiplication theorem is claimed.

## Open next questions

Measure the same domain on another compiler/architecture before generalizing
the speedup. For length22, coordinate with the active set-cover work and first
derive a sound search specification; this adapter retains the L<=20 guard.
The structured questions, first steps and blockers are in `TASK.json`.
