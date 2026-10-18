# Exact optimal directions for QQ16 scalar sweeps

For the **fixed dirty-bridge word and bank-major access protocol of
[PR #2722](https://github.com/CrocSwap/integer-mult-bounds/pull/2722)**, choosing
one increasing or decreasing complete site sweep per scalar instruction gives
this exact minimum closed two-tape word-address travel, for every integer `N >= 1`:

| Window | PR2722: every pass increasing | Optimal pass directions |
|---|---:|---:|
| L2 | `3564N - 896` | `3518N - 850` |
| F0 inverse | `8302N - 1944` | `8222N - 1864` |
| Total | `11866N - 2840` | **`11740N - 2714`** |

The saving is exactly **`126(N-1)` address steps**. At `N=2`, the total falls
from 20,892 to 20,766. At `N=1` the protocols coincide. The provided schedule
uses 23 reverse L2 passes and 40 reverse F0-inverse passes.

This is a source-bound **local access lemma**, with an optimality proof for
this stated protocol. It does not give a minimum over instruction reorderings,
scalar resynthesis, layouts, caching or general tape programs. It does not
complete a QQ16 caller or improve kappa. PR2722's increasing-pass tariffs remain
correct for its specified protocol.

## Exact boundary and unchanged charges

There are two independently movable word-address tapes. Z and W each contain
112 banks, with `address(bank, site) = bank*N + site`. An ADD reads its source
and updates its destination at the **same site**, using one scalar source
register; a CLEAR updates its target. Every instruction visits all sites
contiguously, either `0..N-1` or `N-1..0`, and finishes before the next
instruction. Both tapes start and return to address zero separately for each
window. Idle heads remain where they were; motion is charged by the sum of
absolute head displacements. The unchanged physical layout needs no conversion.

The source is ywz65's PR2709 word at
`d7749c49e967b214537c0bd832e435e177e21d4f`, with the L2 markers at zero-based
indices 633 and 1066, and F0-inverse markers at 1172 and 2125. Interior events
are scalar ADDs/CLEARs only. The verifier checks the source bytes, markers,
coefficient alphabet and owned bank bounds before using them.

As in Nick Petalas's PR2722, the eight `W[k] -= W[k+8]` instructions use the
existing dirty Z0 bank via four cross-tape ADDs:

```text
Z0 += W[k+8]; W[k] -= Z0; Z0 -= W[k+8]; W[k] += Z0
```

For arbitrary `(Z0,W[k],W[k+8])=(z,f,g)`, these return `(z,f-g,g)`.
This bridge is inherited, not a new construction. The resulting windows have
432 and 976 instructions; every ADD touches distinct tapes. The sole change
here is the direction in which each complete instruction sweeps its sites.
[SCHEDULE.json](SCHEDULE.json) records one direction per instruction in the
reconstructed bridge word: `0` increases, `1` decreases. Ties are resolved
lexicographically at `N=2`; all paths tie at `N=1`.

The complete added local invoice remains **864 unit ADDs, 832 quarter ADDs and
288 CLEARs: 17,472 real scalar primitives** at the inherited prices 8, 12 and 2.
This includes PR2722's 24 extra unit ADDs relative to PR2709. Native events
are unchanged: the inherited invoice has 224 rank-one and 16 rank-eight
children (mass 352), 480 wrappers and 208 full-cover maps. Original F0/B1 work
is additional. The new checker independently counts the source scalar word;
it does not replay those native kernels or admit their prices.

The **whole-window ownership premise is retained**: W0 for L2, W0..W15 for
F0 inverse, and the temporary dirty-Z0 bridge access. Scratch at many sites
coexists between passes. There is no additional payload bank, and this is not
a return to PR2709's one-owner-at-a-time release contract. The precision-sized
source register, instruction control, in-word arithmetic and surrounding native
movement still require physical implementation and pricing.

## Proof of semantics and optimality for all N

**Semantics.** Each site executes precisely the same ordered scalar instruction
sequence as PR2722. Changing an instruction's site direction only reorders
operations on disjoint cells. Thus the transformation preserves every cell for
arbitrary initial inputs and disposable output dirt, and retains the bridge's
exact restoration of dirty Z0. No original clear, frame change or native event
moves across a window boundary. This argument is dimension-independent;
small rational fixtures below are controls, not its universal justification.

**Endpoint state.** Before an instruction, each head is at
`b_t*N + e_t*(N-1)`, where `b_t` is the last bank touched on tape `t` and
`e_t` is 0 or 1. Initially both pairs are `(0,0)`. The last bank depends only
on the fixed instruction prefix. The two endpoint bits therefore give at most
four states. For instruction direction `d` (0 increasing, 1 decreasing), a
touched tape enters bank `b` at offset `d*(N-1)`, travels `N-1` within that
bank, and finishes with endpoint bit `1-d`. An untouched head keeps its bit.
The exact entry distance is

```text
abs((b - b_t)*N + (d - e_t)*(N-1)).
```

The final return charge is `sum_t (b_t*N + e_t*(N-1))`. Direct walks attain
these distances; triangle inequality precludes a cheaper walk with those same
visits. Reading then writing distinct tapes does not change the sum of their
individual head distances.

**Affine law.** Write `delta=b-b_t` and `v=d-e_t`, so `v` is -1, 0 or 1.
For every positive integer N, the entry distance equals:

```text
 delta*N + v*(N-1),   delta > 0
-delta*N - v*(N-1),   delta < 0
 abs(v)*(N-1),        delta = 0.
```

The signs hold even at `N=1`: a nonzero integer bank difference dominates an
offset of magnitude at most `N-1`. Within-bank travel and final returns are
also affine in N. Consequently every complete direction word has travel
`T_path(N) = T_one + (N-1)*A_path`. Here `T_one` is the **same for every
path**, because at `N=1` every pass is a single bank address, independent of
direction. Minimizing at `N=2` therefore minimizes `A_path` and is optimal for
all `N>1`; it also attains the common value at `N=1`. This is not a polynomial
fit or a conclusion extrapolated from finitely sampled N.

**Bellman lower bound and witness.** For each instruction, `optimize` enumerates
both directions from every reachable endpoint state and retains the least
cost for each successor state at `N=2`. Induction on the prefix proves that
these are exactly the minimum prefix costs. Including the final returns and
minimizing over terminal states gives the complete minimum; the retained path
attains it. This covers all `2^432` and `2^976` direction choices without an
exponential enumeration. The two separately closed windows optimize independently,
so their minima add. [RESULT.json](RESULT.json) records all reported constants.

## Reproduce and evidence

Standard-library Python 3.12, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/qq16-bidirectional-sweeps
```

Expected primary output, normally and with optimization:

```text
PASS_QQ16_BIDIRECTIONAL_SWEEPS minimum=11740*N-2714 scalar=17472 no_new_kappa
```

The registered command also runs five CLI integrity groups. Direct replay needs
only the package files, works from another directory without Git, and writes
nothing. The generic runner uses Git only to authenticate historical task/base
provenance. There are no imported predecessor executables or Python packages.

Checks include:

- Independent literal address enumeration at `N=1..32,64`, including recovery
  of both original PR2722 tariffs and both optimized tariffs.
- Exhaustive direction enumeration for all 120 words of lengths 1..4 over a
  three-instruction toy alphabet, at `N=1,2,3,5` (6,216 path cases), compared
  with the endpoint DP. This covers single-tape clears and idle-head state.
- The affine edge identity for all 223 possible bank differences, both previous
  endpoints, both directions and `N=1,2,3,64` (3,568 cases).
- Exact rational full-cell comparisons against the unbridged original windows
  at `N=2,3,5`, including nonzero dirty Z0. A wrong source-site alignment at one
  final Z write disagrees. Omitting head returns also disagrees.
- Rejection of native events inside a scalar window, borrowed X access,
  inactive W16 scratch and aliased ADD fields.
- Git-free read-only replay, source-byte corruption, typed result corruption,
  direction-receipt corruption and equivalent gzip recompression.

Local registered replay passes on CPython 3.12.14 / macOS arm64; direct CPython
3.14.7 replay also passes. Frozen input pins use SHA256 of the decompressed word
and its original Git blob. Gzip container headers do not define mathematical
equality. The verifier is bounded to 256,000 source bytes, 2,415 source events,
1,408 rewritten instructions per window, 64 literal sites and five fixture sites.
Python's managed allocations remain; this is an offline verifier, not a
finite-control tape implementation or a formal-kernel proof.

## Scope, overlap and family decision

Selected-source bindings passed; the selected record is unchanged. Base main is
`b017900dbb94d81afec343924c1a7fa6d540a7db`, priority revision 5. The task picker
selected recursive interfaces with nonce `2b009b56cc2256f685cd5a8d0b321095`.
[TASK.json](TASK.json) refines `joint-query-controller` to this exact access
obligation and records live-overlap freshness and source heads.

PR2722 explicitly leaves other sweep schedules outside its tariff; this provides
one exact protocol optimum, not a correction to that predecessor. PR2540,
PR2651 and PR2709 supply the decoder, bank coalescing and scratch ownership
premises. Later zero-retention QQ16 words have different instructions and are
outside this theorem. The existing investigation is
[Discussion #2617](https://github.com/CrocSwap/integer-mult-bounds/discussions/2617).
No advance public reservation was made; work is reported as a finding.

The family decision is **narrow and stop at this local lemma**. Unknown caller,
retention, precision, instruction-control and output-consumer costs are not zero.
No complete favorable supplier moment, selected cold replay, full native-kernel
replay, independent human review or new kappa is claimed. A smaller local address
bill alone does not justify another dependent construction campaign.

## Open next questions

Can an actual QQ16 caller afford the **whole** physical bill under these
whole-window ownership conditions? Pin its producer/native/consumer schedule,
check W and Z0 availability throughout each window, and combine native
movement, instruction control, precision-dependent source-register work and
retention in one budget. The absent complete caller and physical ledger are the
blockers. Stop if that complete bill is unfavorable. Optimizing more local
schedules before this budget exists is not the recommended next task.

## Credit

Arham Tahir, with substantial OpenAI Codex assistance in derivation,
implementation, verification and writing. New work is Apache-2.0.

Credit **Nick Petalas / PR2722** for the access model, increasing-pass tariffs,
dirty-bridge word and physical-cost handoff; **ywz65 / PR2709 and PR2540** for
scratch-slice reuse and the complete local decoder; **commdata2338 / PR2651**
for output-bank coalescing; and the retained QQ16/native lineage of Ali Romman,
starship-s, Sagar Thakrar, Ross Richardson and the geometry/supplier contributors.
The exact predecessor word is retained byte-for-byte in the compressed input.
Bellman optimization and sweep reversal are standard; this contribution is the
source-bound optimum and all-N proof for the stated physical access protocol.
