# Cross-review: source-bound MOVE home adapter

**Verdict: pass for the stated formatted-packet, one-event ABI. No borrowed premise silently fails within that boundary. The raw-zero initializer and larger-compiler obligations remain explicitly open.**

Reviewed pins:

- Parent proof pins the native core at `3a27ab1d302d13b1ce52411f8a174e7a32baab77` and B1 dispatcher at `b4fcc9d64971fdabd0b1d82cfb749d8aac920437`, under canonical main `e54523517d0f03e58352e647c403a5af3e525a57`.
- `worker-b/research/source-bound-move-home-primitive/PROOF.md`: SHA-256 `4beaa35f0d6637daa2bafac3fa0a1b7a66a18745dc936e94e3fcb3236f8798c2`.
- `worker-b/research/source-bound-move-home-primitive/adapter.py`: SHA-256 `04462e141548c6a86c500d40b4aee8c446c539bd9269098d7516fa13400ef099`.
- Frozen native `inputs/native/PROOF.md`: SHA-256 `aa7897029c9761fdf96c3336ab37c2827f08b0df29c868e3b2257ecc661ac7b6`; `inputs/native/move.py`: `42e4293ab59ffa1c99e0dbbd5fded0833a5d726e1e794f0f263ae9a4686587a5`.
- Frozen dispatcher `inputs/dispatch/PROOF.md`: SHA-256 `63f29469fd49751f267db6e26e3494e2bea567fa909d5ebfa2ec9a5924674a4e`; `inputs/dispatch/tape_graph.py`: `7d3cee3e79ba5fe410e1a6b5f4cf6a2fbe5e274f838b798cd8860344ff258b54`.
- Native local ABI constants and tape model are from frozen `inputs/native/reference/linear/inputs/controller_reference.py`, SHA-256 `e664a748e6b6797d4b60f60a7a7dd68b59a5608acf56b9c5d8b466f363755f73`.

## Header/data seam and complete tensor ABI

The split is exact for each positive canonical Gamma code. With `z` prefix zeros, the adapter copies those `z` zeros while appending `z` unary guide marks, copies the leading one, then consumes exactly `z` suffix bits while erasing one guide mark per bit. It therefore copies `2z+1` header bits and leaves the working head at the next code. Six fixed-control repetitions copy exactly E bits, including cutoff, without expanding any value. The remainder through the outside `|` is copied as DATA and the delimiter is excluded, yielding exactly V bits followed by blank on the native DATA port. Repacking concatenates the unchanged E-bit header and complete V-bit output before the same outside delimiter, preserving F=E+V.

The copied DATA extent is the entire `[P] x [2^f]^9 x [S]` field with all r coefficients, all nine native blocks, and every spectator address. Neither parser nor repacker reorders or projects coordinates. `primitive` accepts only the named unary MOVE service and B1 gathers/returns the same selected owner; the other equal-length HOME remains a spectator. The unchanged native core receives its six codes and DATA on distinct ports, so its all-f/cutoff and numerical promise is preserved exactly.

## Origin and marker compatibility

The B1 tape alphabet includes `^` as the permanent nonnegative-origin marker and `|` as field delimiter. The frozen native controller uses `MARK='|'` at each native private origin−1 guard and permits signed tape coordinates. Port injection `t -> t+3` maps native HEADER/DATA to graph tapes 3/4, native private tapes to 5..33, and the separate guide to 34. The adapter moves all 31 core ports two cells right before parsing. Thus B `^` stays at cell 0, the native private guard lands at blank cell 1, and native origin is cell 2. The source program can reach its guard but cannot cross it; successful core cleanup erases that guard before the 29 private heads move back two cells. The public HEADER/DATA ports are rewound to B `^` then shifted back to native origin for core entry. Their B cell 1 is blank. No tape aliases another owner.

This is the required paid ABI adapter between the two marker conventions. The invalid +1 shift would collide the core's private guard with B `^`; the proof correctly treats that as a mutation monitor, not as runtime protection. `adapter.py` authenticates the native inputs and pins the dispatcher graph hash. `embed` preserves source reads/writes/moves/gotos and replaces halt by one transition. Within the stated local Graph model, the nonnegative-head restriction is respected.

One composition detail is checked: B1's graph reserves extra homes using its tape 3 as guide. Here `compile_home` passes `productive_count=2` for exactly two owners, so `reserve(extra_homes=0)` returns without touching tape 3, which is reused as native HEADER. Changed reservation setups were not reviewed here. A further composition must check guide retirement before native entry; sequential reuse may be possible, so relocation is not proved necessary. (Lead clarification.)

## Time and retained history

For one Gamma code, the parser uses at most `3z+2` transitions; summing gives at most `2E+6`. DATA copy costs `V+1`. The adapter's stated post-parse movement, return and repacking allowance `5F+148` then gives

`T_adapter,local <= 7E + 6V + 155`.

Since `F=E+V` with positive extents, this is below `128(F+1)`. Directly counting the two-home B1 gather and scatter in `tape_graph.py` gives at most `5F+10` and `6F+10` respectively, including the home rewinds and working-body return/erasure. Adding those scans still leaves local adapter-plus-dispatch work below `128(F+1)`; the complete selected graph therefore satisfies the displayed `128(F+1)+2^24(fV+E+1)` bound. This absorption is specific to the fixed one-event/two-HOME graph. General B1 dispatcher work remains separately `O(RK(F+1))`.

For backing, the native core contributes `1024(V+E+1)=1024(F+1)`. The adapter's shifted origins, split/repack windows, guide and fixed alignment accesses are covered by its `64(F+1)` allowance. Their sum is exactly `1088(F+1)`. The bound is additive to complete `K_entry`; erasure does not release prior extents. B1 HOME/operand history is separately charged where the whole dispatcher is considered.

## Borrowed premises and limits

The native core theorem requires a correctly formatted six-Gamma packet, a complete DATA field on the common grid, 29 distinct blank private banks, and its all-f numerical/cutoff admission. The adapter supplies those banks and constructs HEADER/DATA from the packet before invoking the core. The B1 theorem only provides binary HOME fields; it does not produce this semantic packet. The adapter explicitly requires the formatted packet as input and says raw owned `0^F` is not a packet or initializer. Thus raw-zero typed initialization is not silently assumed, but a selected caller that must create this packet still needs a paid producer/layout bridge.

The review accepts the native all-f core and B1 home-dispatch lemmas at their frozen pins and does not repeat the full packet execution. It finds no mismatch in their stated interfaces for this fixed graph. It does not extend the adapter to multiple events, a reserved-home configuration using tape 3, malformed packet cleanup, raw-zero initialization, or a complete selected caller.
