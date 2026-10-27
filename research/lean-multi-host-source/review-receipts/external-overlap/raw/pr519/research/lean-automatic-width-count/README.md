# Automatic-width binary counting in Lean

These three modules extend the exact binary dispatcher interface from PR511. A ten-state, two-tape, three-symbol machine allocates a zero counter from actual input symbols and then counts the word. The transition table receives neither the word length nor a supplied counter width. The final stored natural value is the input length n.

## Exact checked contract

For every finite Boolean word, the input initially has `left = word.reverse.map bitSymbol`, a blank head and an empty right list. This is the represented blank immediately to the right of the whole word. The second tape is pristine `Tape.blank`.

The final control state is 9. The input has `left = word.reverse.map bitSymbol ++ [blank]`, a blank head and an empty right list. The counter is at its home blank, with an n-bit little-endian result followed by its represented terminal blank. The result has width n and natural value n. Both tapes' complete finite-list footprints are specified; visited blank cells are not silently erased or identified.

`count_run` gives a run index at most `(CarryTape.pass n (List.replicate n false)).2.reads + 4*n + 4` reaching this configuration. `final_halted` proves the endpoint is halted. This is an upper bound, not a first-completion claim or a linear amortized bound. The empty word is included: no size or capacity premise is supplied, and the zero-width result has value zero.

The components are:

- `BinaryCountDispatcherMarkedInput`: a same-machine representation simulation for the exact home/terminal-blank input footprint, reusing the accepted dispatcher count theorem.
- `BinaryCounterZeroAllocation`: a four-state allocation scan reaching the marked input and n zero counter cells at run index `2*n+3`, including three steps for empty input.
- `BinaryAutomaticWidthCount`: successful-prefix lifts of allocation and counting. Allocator state 3 is identified with the renamed dispatcher initial state, so there is no extra bridge transition. Existing zero-multiplication and core modular arithmetic prove the stored value n without a capacity assumption or a new arithmetic induction.

## Dependencies and reuse

The four dispatcher/carry sources are exact external dependencies from PR511 at commit `79f7c03c7f820ab89955b75ef239cbaccc627e6e`. The two foundational sources are exact external dependencies from PR488 at commit `edd3102b415df5b9d6f633ac0a4dedcf69c58525`. Neither PR is assumed merged. The new package includes only the three additions and retains the original module names.

PR64 already provides richer generic ripple-counter, first-completion and amortized arithmetic results. Binary counting and increment are not claimed as new algorithms here. The additional checked result is this explicit finite-control allocation/count composition, its full tape endpoint and exact value, in the retained `FixedTapeMachine` model. The direct PR64-to-current pass-receipt amortization bridge remains open.

An input4 work copy in slot 2 or 3 has the required right-blank form with `word = (pad n x).reverse` or the corresponding y word. Its slot 0/1 original-input footprints are different. Actual four-tape control composition and the supply of a pristine counter tape still require their own proof. Compact counter normalization, the source's one-string prelude, radix grouping and Plan/Budget realization are also outside this package.

## Validation

All nine modules in the exact dependency closure have current Lean4.21.0 checks. The three new roots print 13 standard-axiom probes; the complete closure prints 49. The automatic-width run proof uses `Classical.choice` together with `propext` and `Quot.sound`. No admitted proof or extra axiom is accepted. The isolated nine-source package replay passed in 11.7677 compiler seconds and 0.00378 queue seconds, with peak virtual memory 3,074,072,576 bytes. All nine object hashes match the accepted checks; all 49 complete theorem/axiom outputs match after whitespace normalization. See `REPLAY_SUMMARY.json`.

## Author-checked conditional project context

At source base `12a4934d15006e8c10f9b2264f13f8f341be802b`, the selected conditional project value is κ=`90446448750933/125000000000000000`=`0.000723571590007464`. The captured selected-result file and its linked certificate agree. This context retains the all-size compiler, weighted/common-ancestor chart, restored-row, selector/routing, prime-supply, precision/recovery, complex-symbolic and analytic-transfer obligations. These generic machine modules do not discharge those obligations or prove a multiplication or κ theorem.

## Reproduce the isolated package

Use Linux, Python 3 and the official Lean 4.21.0 distribution. Obtain separate source worktrees at the two exact dependency commits. For example:

```sh
git clone https://github.com/jamesyc/integer-mult-bounds.git dependencies
git -C dependencies worktree add --detach ../input-foundation edd3102b415df5b9d6f633ac0a4dedcf69c58525
git -C dependencies worktree add --detach ../dispatcher-foundation 79f7c03c7f820ab89955b75ef239cbaccc627e6e
python3 check.py --lean /path/to/lean-4.21.0-linux/bin/lean \
  --input-foundation-root /path/to/input-foundation/research/lean-binary-input-preparation \
  --dispatcher-foundation-root /path/to/dispatcher-foundation/research/lean-binary-count-dispatcher \
  --build-dir /tmp/automatic-width-count-check
```

The output directory must not already exist. The checker itself is offline: it validates all three included and six external source hashes and import order, then compiles exactly nine modules with only the fresh output directory and the installed Lean core on its search path. No Mathlib or Python package installation is needed. The resource audit uses Linux `/proc`. Per-module hard limits are60seconds and4GiB address space; a successful check over40seconds or3.5GiB stops for review. No compiled objects are shipped.

`DEPENDENCIES.json` pins both unmerged dependency packages, `MANIFEST.json` fixes the exact compile order, and `ACCEPTED_CHECKS.json` records prior accepted objects and all49 whitespace-normalized complete axiom statements. The original attribution and Apache-2.0 license are retained. Prior work and dependencies are [PR64](https://github.com/CrocSwap/integer-mult-bounds/pull/64), [PR488](https://github.com/CrocSwap/integer-mult-bounds/pull/488) and [PR511](https://github.com/CrocSwap/integer-mult-bounds/pull/511).
