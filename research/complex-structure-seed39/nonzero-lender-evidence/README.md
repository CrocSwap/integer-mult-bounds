# Four low aliases through lifted-target compensation

The subsequent [composition with PR2435's entrance frames](composition2435/README.md)
verifies the conditional value
**κ = 0.0016991608921398251600279999999999999999999998999999999999999999999999**.
It combines the four aliases below with Jeremy Kothe's 24 entrance raises
and an explicit six-slot owner replacement per call. This is approximately
**0.03824% above PR2435**; the gain is modest. Both changed native words,
the complete owner geometry, global program, physical invoice and modern
outer transfer pass. See that package for its exact source pins, controls,
reproduction command and inherited assumptions.

The original four-alias snapshot establishes the conditional value
**κ = 0.0016972105695892372197269999999999999999999998999999999999999999999999**.
Both native words, the complete literal global program, physical invoice and
current outer transfer have passed. This improves the pinned PR2374 value by
approximately **1.5618687466793e-8 (0.0009203%)**. It is a small numerical gain.
Concurrent [PR2435](https://github.com/CrocSwap/integer-mult-bounds/pull/2435)
at `324d7d3590dc21003940a44cb0cbdc32b3620f25` reports the larger constructed
value `0.0016985113436976293290517338141877446308…`. The standalone snapshot
below is below that value. It remains independently reviewable; its original
certificate does not include the later composition linked above.
The selected frontier remains unchanged; this is a contribution for review,
not a maintainer-selected result or an unconditional multiplication theorem.

Base: `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`.
Assignment: OS seed39, complex supplier. The starting sources are PR2339
`bf1742aee4d855efb8bbd44a8419eddb33a679e5` and PR2269
`b479fc5567bc09ab9185bffe89b62594f36d74e5`. The comparison is the constructed
PR2374 claim at `5449da65da12bdfd94675dccc38731eaa91e93b6`; it is not described
here as maintainer-selected. Exact comparison pins are in
`COMPARISON-TRANSFER-CHECK.json`.

## Constructed change

Starting from the 48-high-alias words, helpers640,641,642,644 borrow from
sources33,55,74,85. Four same-frame scalar additions restore the lenders
before handoff. Four targets move their existing first rank-one climb to
after the entry adapters, before A. Flag-preserving monomials permit exact
compensation there, and four shared center COPY calls split rank8 into7+1.
Every compensation operation, source restoration and inverse cleanup is
explicit in `words/FOUR-base.json.gz` and `words/FOUR-extra.json.gz`.

The complete local change is
`+4 H1 -4 H3 -4 H5 +4 H7 -4 H8`, with four fewer width-eight helpers.
Both words have428 helpers,652 arbitrary input columns, rank mass5328,
helper-width sum3472 and76 private FULL cleanup buffers. The original
400-helper word is not the baseline for this construction.

## Verified evidence

- `FOUR-CANDIDATE.json`: exact formal endpoint, source restoration and profile.
- `NATIVE-RESULT.json`: both complete native chains, including exact phases,
  explicit forward/dual recipes, wrappers and Lemma G. All15 distinct stages
  passed. The original fixed-inventory orientation check failed, then the
  candidate-specific binding passed; the original failed log was overwritten
  by resume. This history is retained in the receipt and compiler review.
- `FOUR-OPERATORS-INDEPENDENT.json` and `FOUR-CHRONOLOGY-CHECK.json`:
  independent exact Gaussian-column, coefficient-transport and chronology
  implementations.
- `TRANSPORT-CONTROLS.json` and `TRANSPORT-FLAG-CONTROL.json`:12 word
  mutations plus a mutation preserving handoff but breaking the entrance
  flag are rejected by the applicable native transport.
- `budget/RESTRICTED-VERIFICATION.json`:285048 literal retained roles,
  bridge-aware windows, axes, charts and complete recursive profile checked.
  At primitive rate0.0016971949509017704265940818773, excess minus deficit
  is less than−0.21859429593742802. This earlier recursive-cost screen alone was not a κ certificate. The
  subsequent complete invoice is covered by the global admission below.

A cold native replay (NumPy required) is:

```sh
python3 -B research/complex-structure-seed39/nonzero-lender-evidence/replay_native.py --out /fresh/absolute/output
```

Expected final line:
`PASS_FOUR_LIFTED_NATIVE_BOTH_WORDS_NO_GLOBAL_ADMISSION`.
The actual verified output directory is
`/home/zoe/MP/maths/mult/seed39-four-native-cold-20261015T0734Z`.
The default reproduction is fresh; `--resume` checks input payload equality,
preserves future attempt logs and reuses successful stages.

## Complete global admission and reproduction

The global program binds all 666 calls to their literal owner maps and lowers
all local operands to physical families. It separately reserves all 76 zero
buffers, adds an explicit CLEAR at allocation and release, and charges all
warp adapters and binding work. The total physical stock is 66,818. The prefix
is 1,442 < 2,048 bits and the physical row coefficient is 19,545 < 20,161.

The fresh strict replay passed 21 controller, six buffer, 114 assembly, 12 bit,
eight independent owner, five new interface and six geometry controls.
The current pinned outer transfer passes 63 strict inequalities, 17 rejecting
controls, independent balance arithmetic and 19 retained evidence replays.
Two independent rational engines bracket the native supplier endpoint in
[0.001697210569589237219727, 0.001697210569589237219728].

Reproduce the complete global and outer admission (Python with NumPy and
SymPy 1.14 available; approximately a few minutes):

```sh
python3 -B research/complex-structure-seed39/nonzero-lender-evidence/verify_global.py --out /fresh/absolute/output
```

Expected final status: `PASS_FOUR428_CONDITIONAL_BOUND`. This command reuses
explicitly hash-bound complete native evidence and freshly emits and checks
the global construction and outer ledger. Use `replay_native.py` above to
regenerate native evidence independently. Receipt reuse is not described as
fresh native compilation.

The previous PR2269 aggregate replay failed on serialization-dependent hashes.
Its failure remains recorded; it is not converted into a successful receipt.
The new construction uses exact pinned source geometry, the actual successful
PR1297 admission, and its own fresh global admission. Source archives retain
exact byte pins; regenerated gzip mathematical equality uses complete payloads.
The inherited unused SPEC metadata field `expected.mutations_rejected=15`
comes from the parent freezer; the actual 21 named controller controls are
independently required by the final evidence checker.

The construction remains conditional on all-size compiler and mutable-source/
common-label realization, whole-call hosting, precision and tape bounds,
exact recovery, the PR559 native correction, PR589 bit H1–H5, the retained
prime theorem and written gauge-free/locality/outer-transfer arguments.
Finite certificates do not formally prove the full multiplication theorem.
No selected certificate or `upstream/` source is changed.

The required `make verify` was run once in an isolated export. It stopped in
the historical `frontier741-verify` / `bit589` stage at a bytewise gzip
comparison; the generated and pinned files have identical decompressed bytes
and parsed JSON. This broad suite is **failed**, not passed. The focused
construction checks above passed separately. The retained diagnosis and log
are `global-admission/MAKE-VERIFY-RESULT.json` and `make-verify-bit589.log`.

## Attribution

Tekalign (@tekuuu), with substantial OpenAI Codex assistance; Apache-2.0.
Credit Cinna Davis (@1337isnot1337), PR2226, for anticipatory dirty borrowing;
Sagar Thakrar, PR2339, for its low-alias construction; Jeremy Kothe, PR2269,
for the T74 words, native machinery and owner framework. Retained source
notices preserve their predecessors. PR2374 (jeremykothe2, with the PR2349/PR2363 owner lineage) supplies
comparison and exact outer-transfer sources; its optimized owner map is not used.
Concurrent PR2402 (Sagar Thakrar) prices fixed-word moves, and PR2406
(Jeremy Diviney) caps fixed scalar/handoff frame refits. Our new target COPY
stages and handoff operations change their stated hypotheses. The exact-cost engines and capacity predecessors retain
credit in `budget/README.md`.
