# A smaller shared bank for paired denominator-13 sampling

The 144 ordered-coin graphs of zxv's [PR #6072](https://github.com/CrocSwap/integer-mult-bounds/pull/6072)
have a shared forward dispatcher with **22,482 internal states**, down from
44,928 in their disjoint union. Its packed transition bank and 144 entry pointers
use **84,578 bytes**, down from 101,088 bytes for all separate resident tables.
This saves **16,510 bytes** while preserving every finite coin-tape output and
its first stopping depth. The state count is minimal for those fixed ordered-coin
functions when all residual information is in the counted controller state.

Claim type: **finite certificate with a scoped proof of minimality**.
This answers the logical state-sharing part of #6072's second Open next question.
The physical control-cost question remains open. This is a new shared
construction, not a re-check of its predecessor's sampling law or optimal means.
No supplier or new kappa is claimed.

## What is compared

The comparison is between a resident bank of all 144 configurations and one
shared resident bank. The predecessor can instead generate and store only one
702-byte configuration. The shared bank is not smaller than that single-table
working set, and no runtime speedup is measured.

The new encoding stores two 15-bit targets per internal state, plus 144 15-bit
entry codes. It needs 84,308 transition bytes and 270 entry bytes. The last
transition byte has four unused high bits. Interpreter code, layout headers,
table preparation, parameter selection, lookup, random-tape motion, outputs
and cleanup are outside these payload counts.

## Evidence and reproduction

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/shared-residue-dispatcher
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/shared-residue-dispatcher --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/shared-residue-dispatcher/verify.py
```

The first command runs both registered normal and optimized checks. The
publication check requires the package to have been committed. Elsewhere,
replace the absolute interpreter path with a local CPython 3.12 executable.

Expected status is `PASS_SHARED_RESIDUE_DISPATCHER`, with 144 configurations,
22,482 minimal internal states, 84,578 shared bytes, 36,864 literal tape controls
and five rejected certificate corruptions. Default replay writes no files.

To produce the actual packed bank and a generated hash-bound receipt, point
both output options at a scratch directory outside the checkout:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/shared-residue-dispatcher/verify.py --emit-dir "$HOME/.cache/imb-shared-bank" --receipt "$HOME/.cache/imb-shared-bank/receipt.json"
```

The exact packed payload hashes are:

```text
transitions.bin  a91f1d6fd9ba664e6e7de4ebda0121a5049ae129753669780f72651b0da0f8d1
entries.bin      08debab375f7fb0cdb7b07d43305239e36cf2edb8b3186ca052324a86e8b1d69
```

[PROOF.md](PROOF.md) defines the entire input graph and proves the refinement,
minimality and payload claims. `dispatcher.py` constructs the quotient;
`verify.py` checks the complete transition homomorphism, all refinement splits
using a separate sorting implementation, reachability, packing, finite tapes
and rejection controls. Distinguishing continuations of length at most nine
separate every inequivalent pair; a checked pair needs nine.

## Sources, scope and limitations

The exact predecessor is #6072 head
`9011bf83e85ecd0443c789cf03259442f750877d`, especially its
[`make` definition](https://github.com/CrocSwap/integer-mult-bounds/blob/9011bf83e85ecd0443c789cf03259442f750877d/research/paired-residue-sampler/verify.py)
and [written graph specification](https://github.com/CrocSwap/integer-mult-bounds/blob/9011bf83e85ecd0443c789cf03259442f750877d/research/paired-residue-sampler/README.md).
The graph is stated and constructed locally. Replay needs no network, pending
Git objects, predecessor imports or third-party packages. `SOURCES.json` pins
the historical task and selection as provenance, not scientific inputs.

The original `supplier-boundary-audit` card is changed to a constructive
sampler-table question rather than an audit or admission replay. This side
result reduces one logical inventory that a future stochastic inverse service
could use. It does not resolve that service's physical bill. The selected
record at base `721c03822c421b7f7fcbb2598993b947c4d88419` is PR6030,
conditional kappa 0.003125804, with all five assumptions retained.

Minimality requires unchanged output order and unchanged behavior on each
ordered coin tape. A different sampler with the same law, a parameter oracle,
output recoding, arithmetic control or compressed ROM can escape the statement.
The state minimum does not prove a byte minimum. Unbounded stopping remains.
Phase sharing can lose the inverse uniqueness needed by #6102; that reversal
is not transferred. No physical tape/native replay, selected scientific replay,
formal proof-kernel check or independent human review was run.

## Implementation bounds

The standard-library implementation uses dynamic allocation with explicit
finite limits, rather than fixed-memory real-time execution. There are at most
44,932 graph states, 144 roots, 16 refinement rounds and 16 bits per packed
code. Failure to stabilize within the cap raises an error; the declared graph
stabilizes at round ten. No recursion is used. The retained histories and sorted
signatures are bounded by these limits. Every function stays below 60 lines.
Warnings are errors in both registered modes. No repository-wide analyzer or
configuration changes are made for this isolated research package.

## Open next questions

- Can a physical finite-tape dispatcher exploit the shared bank after charging
  residue selection, packed lookup, output storage and coin movement? Start
  with one actual nonadaptive residue pair and compare against on-demand table
  generation. Neither side's physical bill is supplied here.
- What retained information would make a phase-merged dispatcher reversible?
  Start with #6102's predecessor-uniqueness condition and one merged pair.
  Forward equivalence alone does not permit transferring its cleanup protocol.

## Credit

This result was produced by Nick Petalas. Apache-2.0. zxv's #6072 supplies the
ordered-coin graphs, denominator-13 catalogue, sampling law, expected-bit
optimum and the sharing question. Moore refinement and residual-state
minimality are classical. The new contribution is this exact shared quotient,
its scoped state minimum, complete certificate and packed-bank construction.
JoyboyBrian's inverse and #6102 reversal, the classical DDG lineage, and the
retained arithmetic predecessors keep their attribution.
