# Thirteen row ADDs are globally necessary for the PR2271 boundary

This scoped mathematical proof was produced by Nick Petalas. Apache-2.0.

Cinna Davis's [PR2271](https://github.com/CrocSwap/integer-mult-bounds/pull/2271)
gives a thirteen-ADD circuit for three copies each of the source parities
A+B, A+B+C and A+C. It proves optimality within one-anchor tours. The new
lower bound permits arbitrary CNOT ordering, target feedback and any finite
number of additional restored dirty rows. **Thirteen is still the minimum.**

For arbitrary independent source and target rows over F2^L, L>=1, require

```text
A, B, C and every additional row return unchanged;
X_i += A+B;   Y_i += A+B+C;   Z_i += A+C,   i=1,2,3.
Every instruction is one paid r_d ^= r_s, d != s.
```

There are no free maps or clean initial rows. Every scalar row is an
independent arbitrary input. The new result is an unrestricted lower bound
inside this row-XOR alphabet. The upper construction is credited to PR2271
and is cited without replaying its verifier or finite certificate.

## Proof and evidence

[PROOF.md](PROOF.md) gives the complete written argument. Nine target writes
are mandatory. An unchanged row cannot be written exactly once. A putative
twelve-gate circuit therefore has only three surplus writes. If no source
changes, an invertible dirty-input block excludes every needed pure parity.
Otherwise only one source changes, either twice or three times. The
three-write case has too few intermediate values. In the two-write case,
at most one target can be written twice; if that target becomes pure, its
only possible pure value is the original single source coordinate. It
cannot supply a missing multi-source parity. This exhausts the budget.

The arbitrary-workspace conclusion is a written proof. The self-contained
verifier corroborates its lemmas on complete, explicitly finite domains:

- All 168 invertible binary three-row bases and all 1,008 single CNOT
  transitions change their destination row.
- All 55,987 words of length at most six on two fixed sources and two dirty
  rows preserve the invertible dirty block, across 380,713 prefix visits.
- All 12,288 four-write words with two writes into A and two into T, over
  eight frozen-row source offsets. Of these, 2,720 restore A. Their eight
  pure intermediate T values are all the original single A coordinate.
- All 680 surplus allocations across nine targets, three sources and two
  extra rows. The 275 allocations respecting the unchanged-row rule include
  33 with a changed source, all in the two cases used in the proof.
- All 219 closed pure-source itineraries with one through three writes,
  allowing even zero as an intermediate state. None visits all three masks.
  A four-write positive control does visit them.
- Interpreter-domain rejections and semantic controls distinguish missing
  source restoration, a changed source and a singular dirty block. Exact
  executed counts are emitted by the verifier.

These are new lemma checks, not a census of twelve-gate programs, a replay
of PR2271 or a proof-kernel certificate. The program writes no files and
prints a generated receipt binding all six package files by SHA256.

## Reproduce

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/global-thirteen-add-fanout/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/global-thirteen-add-fanout/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/global-thirteen-add-fanout
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/global-thirteen-add-fanout --check-source-history
```

Substitute another CPython 3.12 path on other machines. The direct marker is
`PASS_GLOBAL_THIRTEEN_ADD_LOWER_BOUND`; the registered and publication checks
report `PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
Run the last command after committing. Registered commands have independent
120-second timeouts. Direct replay also works without Git or repository
imports. Provenance documents are pinned historical inputs, not live
scientific dependencies.

## Scope, overlap and credit

Credit Cinna Davis / 1337isnot1337 for PR2271's exact boundary, borrowed-source
construction, complete restoration and earlier restricted optimality. Its
retained dirty-fanout and connector lineage remains credited in the unchanged
source. The new contribution is the incoming-write lower-bound argument,
its arbitrary-workspace application and the independent lemma corroboration.
Elementary binary linear algebra and CNOT circuits retain their classical
status; no global literature-priority claim is made.

Nick Petalas's older [PR4899](https://github.com/CrocSwap/integer-mult-bounds/pull/4899)
prices weighted pair-mask tours; recent
[PR6427](https://github.com/CrocSwap/integer-mult-bounds/pull/6427) prices
fixed-weight tours. Both restrict the program to an anchor-tour alphabet.
This result changes that hypothesis to arbitrary row CNOTs and proves a
lower bound on PR2271's original boundary. It does not take another mask
family in those restricted models.

The bit-helper-contract card is explicitly changed to this local algebraic
side result in [TASK.json](TASK.json). Canonical base is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
The selected-binding positive control passed for selected PR6030; it is
metadata orientation, not a selected scientific replay.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19371190).
Live PRs, recent account contributions, handoff claims, reservations,
all-main README and merged-PR searches were checked. Sparse notes,
unpublished work and arbitrary historical code diffs remain coverage limits.

This does not supply a physical caller, bit-coordinate mixing optimum,
native implementation, routing/tape bound, precision/stock ledger, recursive
invoice, supplier admission, new kappa or selected-frontier change. All five
framework assumptions remain. Clean inputs, free basis changes, nonlinear
instructions and input-dependent programs are outside the theorem. No
predecessor scientific suite, selected cold replay, Lean or Docker build
was run. Independent human and formal proof-kernel review are unclaimed.

## Open next questions

- Does the minimum survive one initially clean, zero-return row? Begin with
  this exact endpoint and charge initialization and restoration. The dirty
  invertibility argument does not cover the changed initial condition.
- Can an actual supplier use this boundary after complete physical costs?
  First identify a literal common-frame occurrence, then price its source
  references, movement, native work and restoration. No such occurrence or
  full recursive invoice is supplied here.

Structured first steps and blockers are in TASK.json. No broader search is
needed to obtain this first strengthening.

## Verifier bounds

The interpreter caps rows at eight and word length at twelve. Exhaustive
word loops have respectively at most 6^6 and 8*6*4^4 iterations. Prefix
storage has at most thirteen states of eight coefficients. Every function
is below sixty physical lines; there is no recursion, subprocess, network,
dynamic execution or predecessor import. Explicit guards remain enabled
under optimization. Source reads are capped at 256 KiB for each of six
files. The direct command has no output-file path or mutable external state.
Warning-strict normal/optimized execution and source compilation are the
available Python diagnostics.

Power of Ten rule 3 deviation: CPython and its standard library dynamically
allocate arithmetic values, tuples and iterator states. Scope is this
terminating, fixed-domain verifier. Fixed enumeration limits and one current
word bound live data; no allocator-internals or steady-service guarantee is
claimed. Both registered commands exercise the capacities and rejection
controls. A fixed-allocation runtime would be needed before reusing this
code under a no-allocation execution contract.
