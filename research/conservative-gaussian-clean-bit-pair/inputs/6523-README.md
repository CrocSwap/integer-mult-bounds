# A width-one rounded return for actual selected MOVE9896

This component implements the numerical native-return contract for zero-based
MOVE9896 of the selected PR6030 word: public field 236 moves from frame 3=[] to
frame 7=[21]. It updates that destination bank in place. This is one child at
tensor width one, not a complete caller or all-width supplier.

The literal entrance matters. Before 9896 the opcodes are ADD, INIT and SCALE.
Field 236 has exactly one earlier write, event 8203: initial236−2 initial720;
field 720 has no earlier write. Both are independent public coarse-grid inputs
in frame 3. Thus the actual entrance is on coarse grid h, even though the
caller stores fine h/32 records. No extra quantization is needed.

The frozen frame compiler gives Γ_[21]=K C K† on 512 complex coordinates.
The implementation reuses Ali Romman's PR6509 conservative Gaussian pair
kernel for its 256 disjoint pairs. Exact Gaussian monomials K† and K preserve
the grid and norm. Each pair has total squared error at most h², so completed
field error is at most 16h. At n=9, PR6499 uses p=t+14 and h=B2^-p, giving
16h=B2^-(t+10), exactly its completed-native allowance. A valid initial input
attains all 256 pair errors simultaneously, so this one-child envelope is sharp.
The pair theorem and kernel are predecessor work, not claimed as new.

## What is new

The actual selected entrance, frame order, absolute phases, integer record
conversion and completed return are bound together. An independent direct
XOR-mask/phase oracle checks the rounded result, not only ideal basis columns.
The implementation includes fixed-cycle in-place frame permutations and their
explicit zero-return swap temporary. The invoice includes every conversion,
permutation, native pair, route/control operation and workspace obligation.

The literal state map is nonlinear. Ideal basis columns verify the ideal frame
operator; they do not prove equality of rounded maps on arbitrary inputs.
The all-input error argument uses the predecessor pair theorem and a direct
sum of squared pair errors. The separate oracle evaluates actual rounded data.

## Reproduction

Use CPython 3.12 and its standard library:

```sh
python3.12 -I -W error -B research/p104-event9896-rounded-child/verify.py
python3.12 -I -W error -B research/p104-event9896-rounded-child/oracle.py
```

Repeat with `-O`. Strict defaults require retained receipts. `--emit` prints a
candidate without overwriting files. Six exact source objects are authenticated
before decompression or predecessor execution. The primary executes the frozen
pair kernel and compiles the fixed frame in a normal isolated Python child so
its retained assertions remain enabled even when the parent uses `-O`.
The separate oracle imports neither predecessor programs nor the new primary.

## Work, stock and scope

The destination field uses the caller's p+16 signed component records. The
existing p+21 temporary width safely covers every pair numerator. The full
invoice gives direct indexed bounded-word and O(512*(p+21)^2) guarded bit-work bounds,
including fixed route preparation, reads/writes, conversions and cleanup.
The norm-admission guard squares every real component; its wide products and
accumulator are charged explicitly. The core native data path is linear in
component width; the complete guarded reference has the stated quadratic bill.
This is a direct reference implementation, with no accelerated recursive tariff
or measured runtime-saving claim.

The cycle temporary returns exactly zero. This does **not** establish clean
reversible implementation of the reused pair kernel's internal temporaries.
Their initialization/clear work and control storage remain explicit charged
requests under the predecessor's indexed arithmetic model. Physical bit-circuit
cleanup, fixed tapes, routing and the complete supplier's stock/paid allowance
remain open. Python object collection is not erasure evidence.

No higher tensor width, other MOVE, complete caller, native supplier/compiler
or outer admission is supplied. At higher widths, simply reusing coarse h in
multiple rounded layers does not prove the same completed allowance. All five
framework assumptions, selected frontier and kappa remain unchanged.

## Direct logical invoice

Per forward call, the two frame maps use32 fixed points and 32 length 15 cycles:
1024 Gaussian swaps,1024 phase visits and512 selected component negations.
The native layer uses256 pairs,2560 data additions,512 exact half shifts and
4096 kernel range checks. Conversion reads/writes2048 real components each;
swap traffic adds4096 reads and4096 writes; phase traffic adds2048 each.

These are logical dataflow counts. The full retained invoice also charges
1024 component range/alignment checks,1024 component squares, one cap square,
1024 norm sums, wider guard storage, phase/index decoding and fixed-program
construction/storage. Read-only descriptor storage is bounded by21504 bits
plus243 bits of G/Q/phase parameters; pair scratch uses eight p+21-bit words and
the returned-zero Gaussian swap uses2(p+21) bits. Pair initialization/clear
requests are bounded by4096(p+21) bit writes. No extra whole field bank is
needed by the native data path. Source-compiler512-column checking is verification
work; it is not silently included in or excluded from a measured runtime claim.

## Source, coordination and credit

Canonical main 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority 8, selected PR6030.
PR6499 exact-scalar-records head d8f450f1583c4f150b0ed2a8db177453d49c841d;
PR6509 conservative-rounding head a4173e810c4d34a1d13b9745af123ad0ec6cfed5.
The caller MOVE convention is canonical provenance from
`research/p104-unread-path-resynthesis/local.py::native`; it is not executed.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19364477).
The 473-open-PR cache, bounded all-state searches, current1166claims and6509's
released5475handoff were checked. Exact9896searches found no matching result;
hidden/unpublished work, arbitrary diffs and sparse history remain unknown.

ToikY with substantial OpenAI Codex assistance, Apache-2.0. Credit Ali Romman
for6509's kernel/theorem and6499's record contract; JoyboyBrian/5485 and the
4743 port/error lineage; DreamingOfClouds/6030; Cinna Davis, David Arias,
Gareth Davidson and the retained native/compiler contributors; Tekalign's
reversible lifting, Arham Tahir, Nick Petalas, Adam Gall and all source notices.
Exact copied headers remain intact. Cycle permutations, bounded integer
arithmetic and Euclidean error sums are established methods. Separate AI
implementation/review is not independent human or formal-kernel acceptance.

## Open next questions

- Implement and price the pair kernel's internal clean bit workspace under one
  actual tape/circuit model, including addresses and controls. A state-map
  inverse alone does not discharge that implementation obligation.
- Prove a completed-return contract at a larger tensor width without adding an
  unpaid final downcast. Freeze the exact native layer order and all rounding
  errors before attempting precision or stock pricing.
- Bind more actual native sites and the full caller, then test the complete
  supplier/compiler/outer invoice. This one width-one child does not admit it.
