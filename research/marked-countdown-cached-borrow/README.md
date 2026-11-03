# Save one tape read per marked-counter decrement

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

Caching the terminating ONE in the retained marked binary countdown saves
exactly N reads in a complete countdown from N. Every intermediate counter
value, delimiter, head, write, move and blank return is preserved. No new tape
or numerical host-control state is introduced. The constructor and disposal
remain charged. This is a scoped implementation-equivalence and cost proof,
with exact finite evidence. No new kappa is claimed.

Using Arham Tahir / PR2877's complete invoice, the new positive-N bill is
`14N + 14d - 5 popcount(N) + 36`, improving its `15N` leading term to `14N`.
The zero case is unchanged. [PROOF.md](PROOF.md) proves the exact one-read
trace deletion and derives the complete-caller saving.

The unchanged linear-sign caller saves exactly
`B [3M-4 + 4(M-2)S + M S 1_{S>1}]` reads. At M=65, B=S=1, complete logical
traffic falls from 24,454 to 24,011 operations. At (M,B,S)=(65,3,7), it saves
7,230 reads. Writes, movement and the actual source-coordinate permutation
are identical. These are executed logical operation counts, not timings.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/marked-countdown-cached-borrow
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/marked-countdown-cached-borrow/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/marked-countdown-cached-borrow/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/marked-countdown-cached-borrow --check-source-history
```

A clean CPython 3.12 can replace that interpreter path. Direct verification
prints `PASS_MARKED_COUNTDOWN_CACHED_BORROW` in a generated JSON receipt;
the registered launcher prints `PASS_REGISTERED_RESEARCH_PACKAGE`.
Normal replay writes nothing. To regenerate a receipt outside the checkout,
add `--emit-result` and redirect stdout. RESULT.json is generated and binds
every other package file by SHA256.

The checker compares all 24,768 intermediate decrement states in 387 fixtures,
including zero, powers of two, odd counters and padded input widths. Thirty
complete sign-call pairs check every output source coordinate and all actual
read/write/move deltas, plus zero-restored counters and numerical temporaries.
The complete fixture coverage and source-coordinate digests are generated in
RESULT.json. Finished-counter and invalid-terminator controls reject.

## Scope, credit and overlap

Base main is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected PR6030. The selected binding orientation passed. The
`uniform-transfer-audit` card changes to a new local tape implementation and
cost proof. This is a conditioning-independent control-cost side result. It
reduces one actual retained caller's ordinary work, with no recursive histogram
or exponent change. No broader caller-construction round is proposed.

Arham Tahir / [PR2877](https://github.com/CrocSwap/integer-mult-bounds/pull/2877)
retains the exact countdown and full-sign invoices. David Arias /
[PR2753](https://github.com/CrocSwap/integer-mult-bounds/pull/2753) retains the
linear-sign algorithm. Jose Manuel / PR2697 retains the marked Counter and
binary tape library. Their original notices and algorithms are unchanged.
Only the new decrement is added here. Its runtime closure is seven declared,
authenticated predecessor modules, read directly from their retained paths;
no predecessor scientific checker is imported or replayed.

Live claims, local reservations, recent-account work, cached card overlap,
open PR bodies, main object/formula searches and merged-PR searches were
checked. The cache reported complete remote pagination and incomplete sparse
local notes. Arbitrary diffs and unpublished work remain outside coverage.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19363491)
predicted both cached reads and fewer rewind operations. Delivery stops at
the first verified improvement, caching the borrow terminator; rewinds are
retained literally.

The new routine is supplied as an isolated replacement, exercised in the
retained caller. Frozen production files are unchanged. Native operations,
physical compiler/tape realization, uniform caller integration, selected cold
replay, supplier admission and the five framework assumptions remain outside
scope. No Lean, Docker or complete multiplication-theorem replay was run.

## Engineering bounds

The new decrement has one borrow loop bounded by the current encoded digit
width, no recursion, and fixed-symbol local state. Every function is below
sixty lines. The retained tape implementation remains the execution model;
its existing allocation and exceptions are inherited rather than replaced.
The verifier uses fixed fixture sets, counts at most 128 and sign volume at
most 1,365. CPython collection allocation is a managed-runtime deviation from
static allocation. Its loader compiles exactly seven hash-authenticated source
modules, a bounded dynamic-code deviation needed to exclude stale bytecode.
Warning-strict normal and optimized replay are the recurring diagnostics.
No shared diagnostic configuration changes.

## Open next questions

- Can a smaller finite-control return path remove known-position rewind work
  while retaining the same private tape and every cleanup contract? Start
  from one literal decrement and meter each borrow-length case. The current
  proof pays all those rewinds; no additional saving or optimality is claimed.
- Can this replacement be adopted in a current complete ordinary caller?
  Pin its actual Counter ABI and all imported aliases, then compare its full
  instruction trace and physical control bill. Historical-call compatibility
  does not by itself establish current supplier admission.
