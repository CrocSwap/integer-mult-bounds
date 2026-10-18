# A guarded bit caller for rank-seven dyadic ADDs

This package closes one part of [PR3078's guard-allocation handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/3078).
It implements `T += sign*S/2^k`, for `k = 1,2,3`, using literal reversible
CNOT and Toffoli gates. It restores the writable source and returns its carry
bit. Explicit bit connections avoid the rotations in a direct lowering of the
source walk. No complete supplier, runtime speedup or new κ is claimed.

## Result and cost

Let both encoded operands have signed two's-complement width `W`. The source
has `k` zero low bits, and the signed result must fit. Each operand may otherwise
be arbitrary, including a dirty target. All gates have explicitly numbered
physical bit operands. A CNOT or Toffoli between those operands costs one gate;
network routing and memory access are outside this direct-gate model.

| Circuit | CNOTs | Toffolis | Bits beyond the two W-bit operands |
|---|---:|---:|---:|
| Explicit reversible scratch baseline | `4W-2 + 2k(3W-2) + 2W` | `2W-2` | `W+1`, initially and finally zero |
| Rotated source walk | `4W-2 + 2k(3W-2)` | `2W-2` | one clean carry |
| Wired source circuit | `4W-2 + 2k` | `2W-2` | one clean carry |

The wired circuit saves exactly `6k(W-1)` CNOTs over the rotated source walk.
Against this scratch baseline it saves another `2W` CNOTs and a `W`-bit scratch
bank. Neither baseline is claimed optimal or claimed to be an existing upstream
bit implementation. Both are implemented and checked here.

For `W=64, k=3`, the wired circuit uses 260 CNOTs and 126 Toffolis, versus 1,394
and 126 for the rotated walk, or 1,522 and 126 for the scratch baseline. The
wired circuit and rotated walk each use 129 total bits. The baseline uses 193.
Negative coefficients use the inverse adder and have the same costs.

### Paying the guard allocation

`coarse_call` starts with two `P`-bit signed operands and sets `W=P+k`. It needs
`k` new zero source bits, `k` new zero target bits and one clean carry. Existing
data bits occupy positions `k..W-1` on each bus; the new bits occupy `0..k-1`.
This is a fixed input layout, not an uncharged runtime shift.

The source's `k` new bits and the carry return to zero. The target's new bits
are retained fractional output data. They cannot generally be erased or
truncated. Thus the wired caller allocates `2k+1` zero bits and returns `k+1`;
`k` become output storage. Its scratch baseline needs an additional `W` zero
bits and returns that whole extra bank. The complete storage is included in
`invoice`, rather than counting only the carry.

For example, with `P=5, k=3`, source `-5` and target `2`, the encoded source is
`-40`, the encoded target starts at `16` and ends at `11`. This is exactly
`2-5/8 = 11/8`. The source returns to `-40`; its three new low bits are zero.
The target's low bits are `011`, so returning all seven allocated bits to zero
would be false. No extra integer headroom is required beyond the declared
signed endpoint bound. There is no rounding operation.

The circuit temporarily writes source data as well as its guard bits. Its
caller must own exclusive mutable access during the call. It is not a
read-only-source replacement. The baseline leaves the original source
read-only. A clean carry and supplied zero guards are resource assumptions,
not free initialization theorems.

## Proof

Number bits from low to high. Write `S=2^k Q`. The signed representation of `Q`
consists of source bits `k..W-1`, followed by `k` copies of the source sign bit.
The source's low `k` bits start at zero. Copy the sign into them with exactly
`k` CNOTs. Use the source wire order

```text
[k, k+1, ..., W-1, 0, 1, ..., k-1]
```

as the adder's source. This is implemented by the literal gate operands,
not by a hidden permutation instruction. A modular adder updates the target
by `Q` and restores every source wire. Repeat the `k` sign CNOTs to return the
low source bits to zero. The original signed source is restored exactly.

The adder is a MAJ/UMA ripple circuit. On three bits, the forward gates
`c ^= a; b ^= a; a ^= b&c` replace `a` by the majority carry. The corresponding
return gates `a ^= b&c; c ^= a; b ^= c` restore `a,c` and put the sum bit in `b`.
Chaining these through the lower `W-1` positions and updating the top target
bit with two CNOTs proves addition modulo `2^W`, with the carry restored.
There are `2(W-1)` Toffolis and `4(W-1)+2` CNOTs. Reversing these gates gives
subtraction. The signed endpoint condition converts modular equality into
exact signed equality. This argument is uniform in `W`; the implementation
accepts `4 <= W <= 256` and `1 <= k <= 3`.

For the paid rotated comparison, an arithmetic half on a zero-low-bit input
uses `W-1` adjacent swaps, each expanded into three CNOTs, followed by a sign
CNOT. Its cost is `3W-2`. Apply `k` halves and their literal inverses. For the
scratch comparison, also XOR-copy the source into an owned zero bank and
XOR-clear that bank after undoing the halves. Both copies cost `W` CNOTs.
There is no destructive clear or omitted inverse shift.

The MAJ/UMA construction follows Steven A. Cuccaro, Thomas G. Draper,
Samuel A. Kutin and David Petrie Moulton,
[*A new quantum ripple-carry addition circuit*](https://arxiv.org/abs/quant-ph/0410184).
No novelty is claimed for ripple addition, signed bit slicing, sign extension
or the generic copy-elimination identity. The contribution is this guarded,
fully emitted caller and its source-bound rank-seven handoff.

## Evidence and reproduction

Both frozen PR3042 provider words are retained through PR3078 at exact head
`3da2ea9729f70b074713a5d0f69f0bdab32f2b47`. `VENDOR.json` binds their bytes,
original Git blobs and notices. The static inventory finds 2,544 candidate
unit-numerator dyadic ADDs per literal word, including inverse cleanup:
2,060 halves, 470 quarters and 14 eighths. For example, A gate 13 is
`X126 -= X83/2` at frame `[45]`. These are **candidate literal occurrences**,
not admitted native calls or proof that their producers supply guard zeros.

`verify.py` emits 180 circuits, writes and reads their gate bytes, and checks
107,526 signed input cases using both a packed-bit interpreter and a separately
written bit-array interpreter. All valid source/target pairs are exhausted at
widths 4 through 7, for all three policies, both signs and all three shifts.
Signed boundary fixtures extend through 256 bits. The independent interpreter
in `audit.py` does not import the producer. This is internal implementation
independence, not independent human or formal-kernel review.

Thirteen behavioral groups cover signed endpoints, coarse guard allocation,
retained target bits, source restoration, missing sign fill/cleanup, dirty
carry, odd unguarded sources, overflow, malformed gates, source corruption and
fresh-output protection. `evidence/RESULT.json` is deterministic.

With `RUN` an existing session-owned directory outside the checkout:

```sh
mkdir -p "$RUN/tmp"
TMPDIR="$RUN/tmp" python3.12 -W error -B \
  research/rank7-fixed-width-half-add/verify.py \
  --work "$RUN/circuits" > "$RUN/result.json"
cmp "$RUN/result.json" research/rank7-fixed-width-half-add/evidence/RESULT.json
TMPDIR="$RUN/tmp" python3.12 -W error -B \
  research/rank7-fixed-width-half-add/test_verify.py
TMPDIR="$RUN/tmp" python3.12 -B scripts/research_package.py \
  --package research/rank7-fixed-width-half-add
```

`--work` refuses an existing directory and preserves emitted diagnostics.
Without it, outputs are temporary under `TMPDIR`. Registered replay compares
the complete deterministic receipt and runs the behavioral controls. No
external numerical dependencies, native compiler, Lean or Docker is required.
See `evidence/CHECKS.json` for the checked environment and `ENGINEERING.md`
for implementation bounds.

## Scope

This is a completed local module, not supplier admission. The base is canonical
main `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6. The
`independent-moment` card's scope is changed to the specific physical-arithmetic
handoff, after checking its newer source and overlap. It does not repeat the
already-covered frame or moment audits.

The gate map, local guard/storage bill and clean return are proved here.
The actual native producer's magnitude/grid bound, exclusive source access,
routing/backing, output precision retention and subsequent cleanup are unknown.
Wrappers, warps, frames, recursive children, ownership, all-size/compiler and
the outer release are not replayed or assigned zero cost. The recursive paid
profile and selected frontier are unchanged. Do not multiply 2,544 by the
local saving and call it a complete supplier improvement.

## Open next questions

Can one actual producer of `X126 -= X83/2` provide this caller's exact guard,
range and ownership contract, while its consumer retains the fractional target
bit without repaying the saving? Start with that named occurrence and a full
producer/consumer storage and routing ledger. Stop if exclusive source access
or the lifetime of that output bit is unspecified. This is the next admission
question; another coefficient or frame census is not needed.

## Credit

Nick Petalas contributed this caller and its verification. PR3078 supplied the
arithmetic recipes and explicit guard handoff, following PR3060/3056.
Credit dcharb78 for PR3042, Jeremy Kothe for PR3015, Marius-Paul Dumitrean for
PR2979, Cinna Davis for PR2226, eumemic for PR411's earlier paid scalar recipes,
icekylinx and the retained native, geometry and owner lineage. Frozen
`vendor/CREDITS.md` and `vendor/NOTICE` preserve predecessor attribution.
Apache-2.0. Development used substantial automated assistance.
