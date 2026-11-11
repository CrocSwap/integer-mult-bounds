# A 14,886-byte paired residue sampler bank

All 144 nonzero ordered residue pairs `(a,b)` can share **21 canonical tables**
from zxv's [#6072](https://github.com/CrocSwap/integer-mult-bounds/pull/6072).
The new bank uses **14,886 payload bytes**, including all 144 selectors. It
preserves the independent Bernoulli laws, the cited optimal expected draws and
each coin tape's original stopping time. Output labels on an individual tape
may change.

The construction and package were produced by Nick Petalas. Claim types are a
scoped written proof and an exact finite certificate. This is a forward logical
storage improvement, with no new kappa or physical service claimed.

## The changed interface

Reduce each parameter to `min(a,13-a)` and sort the pair. The resulting
representatives are `1 <= u <= v <= 6`. After sampling, exchange and complement
the output bits as required. [PROOF.md](PROOF.md) gives the full law, prefix-count
and pointwise stopping-time arguments.

The source's per-configuration 702-byte table is unchanged. A fully resident
144-table bank has 101,088 transition bytes. This construction stores
`21*702=14,742` transition bytes and a 144-byte selector. The selector contains
the table index and all three output flags; no entry-pointer array is needed.
Runtime logical control needs at most 17 bits, including the retained selector.

Nick Petalas's older
[#6124](https://github.com/CrocSwap/integer-mult-bounds/pull/6124) reports an
84,578-byte shared bank that preserves every ordered coin-to-label function.
This bank saves a further 69,692 payload bytes by changing that contract. It
does not contradict #6124's fixed-function state minimum. Those predecessor
counts are cited, not replayed. A single on-demand source table still needs only
702 bytes, so a resident bank is not always the best physical choice.

## Evidence

[bank.py](bank.py) constructs the packed bytes and interprets supplied finite
coin prefixes. [verify.py](verify.py) checks all 144 selector product laws,
all eight output permutations and all **89,856** selector/state/coin transitions.
It checks 576 terminating paths, their 576 unfinished prefixes, 144 two-period
continuations and 15 exact-reason rejection controls. Six orbits have size four;
fifteen have size eight. No sampling estimate or floating-point acceptance is
used. The source sampler's law and expected-bit optimum remain cited premises.

The generated bank SHA256 is
`1604e7b1fc7492e034a9160d8001ba58235aa81273848982154e7d16a14ffd2c`.
The verifier can emit both the bank and a receipt binding every package file
and the declared source manifest. It writes no file by default.

## Reproduce

From the worktree root, using CPython 3.12.15 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/signed-swap-residue-bank
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/signed-swap-residue-bank --check-source-history --check-modes
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/signed-swap-residue-bank/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/signed-swap-residue-bank/verify.py
```

Expected markers are `PASS_REGISTERED_RESEARCH_PACKAGE`,
`PASS_RESEARCH_COMMIT_BYTES` and `PASS_SIGNED_SWAP_RESIDUE_BANK`. Elsewhere,
substitute a local CPython 3.12 executable. For optional artifacts, append
`--emit-bank /absolute/external/path/bank.bin --receipt /absolute/external/path/receipt.json`
to the direct verifier. The parent directory must exist outside the checkout.

## Limitations

The original 144-table coin-to-label functions are not preserved. This is not
a minimum-state or minimum-byte result over all samplers. Code, headers,
physical table access, selector preparation, tape movement, stopping records,
output storage and reversible cleanup are outside the payload count. The
finite-prefix interpreter has a 4096-coin fixture limit; the written proof
handles arbitrary paths. Mathematical stopping time remains unbounded.

No source-bound inverse caller, conditionally fresh reused tape, physical
speedup, supplier admission, selected-frontier change, independent human review
or formal proof-kernel acceptance is claimed. The five selected framework
assumptions remain. No predecessor probability/mean suite, selected/native
cold replay, Lean or Docker was run.

## Open next questions

Price one actual nonadaptive caller's selector, packed lookup, output and tape
movement against on-demand generation. Begin with the reached residue pair
and its ownership layout. The missing physical caller contract blocks a runtime
comparison.

Derive a reversible lifecycle retaining the selector through terminal
relabelling, then price its stopping record and returned tape. Forward law
preservation alone cannot transfer the tariffs of #6102 or #6127. The structured
questions and blockers are in [TASK.json](TASK.json).

## Credit

zxv supplies #6072's exact graph, probability law, expected-bit optimum and
table-sharing question. Classical DDG methods and output symmetries are not
claimed as new. The new contribution is their explicit signed-exchange bank,
packed representation, changed contract and checked inventory.

JoyboyBrian's #5037/#5069 inverse lineage and #6096/#6102 residue and reversal
interfaces retain their credit. Nick Petalas's #6026 stochastic-prefix context,
#6124 fixed-function shared bank and #6127 counterless reversal are distinct
predecessors. ToikY's #6747/#6749 are written reviews of the original sampler
and fixed-function quotient. Their original notices and bytes are unchanged.
New work is Apache-2.0. Exact source blobs and SHA256 pins are in
[SOURCES.json](SOURCES.json).
