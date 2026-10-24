# Literal binary execution at the CRT key port

This package compiles and **executes** the complete finite-control key service
of [PR #4795](https://github.com/CrocSwap/integer-mult-bounds/pull/4795) using
one-bit tape access, unit bit-head moves and one-bit Boolean/control operations.
It closes that package's explicit binary-encoding gap for its retained
u2,t2,y8 geometry and the original repair counter/bad-stream port.

The [scoped proof](PROOF.md) gives

`binary actions per key <= 43*3,287,110 + 984 = 141,346,714`.

The factor 43 is proved per source instruction. The additional 984 actions
actually initialize and erase all 492 control bits. This is a fixed-geometry
program theorem, not a uniform CRT compiler, complete outer repair tariff or
new multiplication result. The selected κ is unchanged.

## Executed representation

[binary.py](binary.py) produces three fixed bit programs, for source targets
0, 1 and 2, with 106,583 / 106,713 / 106,843 instructions. Every source cell
uses thirteen physical bits: all 4,096 opaque 12-bit payload labels and eight
source symbols have distinct codes. A separate register tag distinguishes
Boolean true/false from symbols. All runtime reads, writes, gates and branches
operate on individual bits; no host-decoded address/key enters the executor.

The same fifteen tape roles are retained. Source-cell head j is physical head
13j. Appending twelve source bit symbols advances the stream by **156 physical
bits**. Private tape bits and heads, borrowed heads and all control bits are
returned as stated in the proof; borrowed counter/ROM and prior payloads are
preserved. Serialization of input packets and source ROM creation are explicit
external prerequisites.

## Evidence at the actual caller

[verify.py](verify.py) independently represents symbol/Boolean values and
executes source instruction semantics. [RESULT.json](RESULT.json) records:

- All 4,104 codec values; 8,208 literal read and dirty-cell write cases, plus
  172 equality/Boolean/alias controls.
- Four complete binary key runs, including a transported parity-source key
  at address 892. Every one of its 44,340 source-instruction boundaries is
  checked against the independent observer: control target, physical head,
  written cell and defined register result.
- The original `bridge.split` with its actual middle-layer guard mask/raw
  source stream, calling the binary service on the **same physical tapes**
  at its first two holes. The source caller then continues to the third hole,
  at address two, demonstrating the returned head/record boundary.
- The unchanged original `one_pass` consumes a projection of those two completed
  pairs and preserves payload/key correspondence. Closing that captured prefix
  with END is explicit verifier setup; this is not a whole-layer replay.
- Five discriminating faults: short bit stride, dirty ROM head, omitted control
  erasure, missing Boolean tag and colliding marker code. Three framed malformed
  packets reject with borrowed data, blank scratch and cleared controls checked.

The six accepted full key invocations execute **5,348,850 binary actions**.
The actual two caller invocations take 859,622 and 859,888 actions; the other
four take 896,367–914,737. These observed counts do not establish the uniform
bound; the block simulation does. The entire bounded verifier takes about
three seconds locally, using one CPU and the standard library.

The source caller facade decodes symbols for the **unlowered outer controller**.
It never converts/copies an address or returned key at the service boundary:
the service directly sees the facade's underlying bit tapes. Its key execution
is wholly bit-level. Observer word decoding and oracle arithmetic are outside
the executor. This package does not price outer control, full sorting/reinsertion,
raw macro-S creation, ROM construction, variable-width parameters or E(p,ell).
No full 2,944-call binary layer or historical suite was run.

## Provenance and distinct scope

Exact predecessor #4795 is
`4e4cf7e47f3fc1c40e775d84fb2e7cd2603658cd`; it is retained unchanged on base
`b91956876e5b4122fd89179f1b57557ff8378f15`. Its source proof, #4752 ROM program
and original #4637 bridge/oracle, scanner increment, and original compact word
are pinned in [SOURCES.json](SOURCES.json). Retention is not scientific approval.

Current #4938 establishes evaluator/layout caps; #4942 and the reservoir-bill
package price ordinary-interchange wrapper calls; #4946 audits the word-census
prune; #4965 studies complex stopped recursion. Those do not supply this literal
binary key executor. [TASK.json](TASK.json) records the refined question and
bounded stop rule. Canonical coordination is
[Discussion #4709](https://github.com/CrocSwap/integer-mult-bounds/discussions/4709#discussioncomment-19138317).

## Reproduce

From the repository root, Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/crt-binary-key-port --check-only
python3.12 scripts/research_package.py --package research/crt-binary-key-port
python3.12 -O -B research/crt-binary-key-port/verify.py
```

The registered command has a 30-second cap and authenticates all declared live
inputs before executing. Direct replay compares the frozen result; only explicit
`--write-result` changes it. Source-history/committed-byte checks and the standard
exporter bind the published files. Direct verification works in a Git-free export;
the generic provenance-aware package runner itself requires Git history.

## Open next questions

1. Lower a bounded actual sparse-repair consumer (for example one radix pass)
   into literal bit control using the same 13-bit representation. The current
   facade still performs outer symbol decoding; a complete invoice must include
   its branching, routing and lifecycle rather than multiplying a cell count.
2. Supply physical ROM construction and variable-width parameter handling at
   the real CRT caller. The fixed-width program and its source theorem do not
   provide those prerequisites. First establish an encoded producer/consumer
   contract; a larger finite key census would not resolve it.

## Credit

Prepared by JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.
Retain #4795/#4752 authorship and the #4637 scanner/repair lineage: Cinna Davis,
ToikY, Hiroki KUMAZAKI, Ryanson Jonathan, unpaidmoon, Jose Manuel and the original
[source-specific notice](../unconditional-batched-crt/NOTICE.md). All predecessor
source files are reused unchanged. No independent human or proof-kernel review
is claimed.
