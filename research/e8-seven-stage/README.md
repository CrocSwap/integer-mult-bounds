b = 9.32783231884153e-4 (complex supplier; no new κ)

# E8 in a seven-stage bridged word

This package places Jacob Sussman's E8 helper circuit, unchanged, in a **seven-stage bridged word** B₃. Sussman's
layout B₂ has five stages; B₃ generalises it to seven. In B₃ the circuit's certified complex coarse saving is

**b = 932783231884153/10¹⁸ ≈ 9.32783·10⁻⁴**, which is +6.45 % over the five-stage 8.76248·10⁻⁴ of PR #352.

**This is not a new κ.** The bit side binds, at about 8.05·10⁻⁴ in #361/#362. What changes is the complex cap: a bit-side
improvement now counts toward κ until about 9.33·10⁻⁴, not 8.76·10⁻⁴.

## The layout

In Sussman's B₂ (`Work/Bridge/Net.lean`, `Work/BridgeGeom/Net.lean` at `9c94857`), every class has two bank pairs:
- Pair 1 runs forward, backward, forward.
- Pair 2 runs only backward, forward. It borrows its first forward invocation from pair 1 through three layers of
  free ±1 additions between "twin" roles that stand at equal frames.

So two pairs are exchanged with five invocations instead of six, on the label space H ⊕ 4·H (m = 5h).

B_K repeats the borrowing along a chain: pair p borrows from pair p − 1 in the same way. With K pairs this takes
2K + 1 invocations on H ⊕ 2K·H (m = (2K+1)h) and 6(K − 1) twin gates per class (`code/complex/code/bridged.py`):

    stage 0, 1, 2      pair 1: forward, backward, forward          windows block 0, F0, F1
    stage 2p-1, 2p     pair p: backward, forward  (p = 2..K)       windows F(2p-2), F(2p-1)
    after stage 2p-3   X(p-1) += X(p),  Y(p) -= Y(p-1)
    after stage 2p-2   Y(p) += Y(p-1),  X(p-1) -= X(p)
    at the end         Y(p-1) -= Y(p),  X(p) += X(p-1)       for p = K .. 2

Each data role still makes m − 1 moves and each helper m. For a unit with v pairs and cst copy moves, the moves
saved per block are therefore D = 2K·v − (2K+1)·cst. For E8 (v = 120, cst = 72) that is D = 120 at K = 2 and
D = 216 at K = 3. The cost side gains the two extra invocations and the idle climbs of the extra pair.

| | K | stages | m | W = 2Kv + R | D | b (E8) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B₂ (Sussman, #352) | 2 | 5 | 45 | 1,263 | 120 | 876248285600677/10¹⁸ |
| **B₃ (this package)** | 3 | 7 | 63 | 1,503 | 216 | **932783231884153/10¹⁸** |
| B₄ | 4 | 9 | 81 | 1,743 | 312 | 9.19445·10⁻⁴ (lower) |

Seven stages is the best of these for E8.

## What is checked (`bash research/e8-seven-stage/verify.sh <fresh dir>`, ~10 s)

1. **Layout** (`bridged.py`). Every frame is a coordinate set in the one orthonormal basis of a class, as in
   Sussman's general stage geometry (`Work/BridgeGeom/Stage.lean`, proved for any number of blocks). For K = 2
   and K = 3 the check verifies:
   - every climb is nested;
   - every twin gate joins two roles at equal frames;
   - every invocation is entered at its stage's bank frame;
   - the final frames are right (X at every coordinate, Y at all but (block 0, l));
   - every data role makes exactly m − 1 moves;
   - the exchange identity X_i = −y_i, Y_i = x_i holds (sympy), at the level of abstraction of the header of
     `Work/Bridge/Net.lean`.

   For K = 2 it reproduces Sussman's B₂ idle climbs exactly (2h+2 | 2h−2, h−1, 4). For K = 3 the idle climbs are
   4h+2 | 2h−2, h−1, 2h+4 | 4h−4, h−1, 6. The two largest are split at an intermediate coordinate frame
   (38 → 31 + 7, 32 → 31 + 1), so that every child stays below m/2. This is the finite guard's half-shrink
   condition, which holds here as 2 · 31 = 62 < 63.
2. **Complex checks.** PR #352's portable checks take the layout as one parameter K (`pins-e8.json` K = 2,
   `pins-e8-b3.json` K = 3). The K = 2 run is a regression: every #352 pin holds, and its full receipt equals
   #352's except for the wall-clock seconds. The K = 3 run covers:
   - gx.check1 with the exact scalar identity, and gxcore;
   - every label and paid child;
   - both scalar words and lifetimes;
   - the splice, with seven windows and the 7-stage recipe;
   - the finite precision guard at m = 63, W = 1,503: rows 12,064 < 20,161, induction gap 63·B, local bill
     2⁴² < 2⁴⁸, global groups 2¹⁹³⁶ < 2⁶⁰⁵⁰, router 2⁵⁷⁶⁵ < 2³⁰⁰⁰⁰, m ≤ 72.
3. **The circuit is Sussman's.** His vendored generators regenerate, byte for byte, the 24 Lean modules and the
   comparator configuration of his kernel-checked `wht_main_block_B2Ge8x` from the vendored certificate. His
   stand-alone replay accepts it at 8762479.
4. **Exact b.** For B₂ and for B₃, b comes from the guard's own seven-stage histogram (7·H + 2v·idle blocks), with
   PR #315's two rational moment engines and the 10⁻¹⁶ fallback, and the next 10⁻¹⁸ grid point must fail. B₂ gives
   #352's b exactly; B₃ gives 932783231884153/10¹⁸.

`SOURCE-pr352.json` records the git blob ids of the 93 files taken unchanged from PR #352 (`04b4c3c`). The edited
code files are `portable_complex.py`, `complex_splice.py` and `complex_scalars.py` (the layout parameter) and
`code/provenance.py` (now checking against #352).

## Open obligations

- **No Lean proof of B₃.** Sussman's `bridge2_certificate` is for B₂. A `Bridge3` structure would need the same
  algebra (verified here symbolically) and the same group-theoretic wiring (r_l, s_l on Orth(H ⊕ 6·H)) proved in
  Lean, on top of his general geometry. The layout is checked here by the finite coordinate-frame bookkeeping and
  the exchange identity, not by a kernel proof.
- **The exchange identity is checked at the abstraction of `Work/Bridge/Net.lean`'s header**: forward Y += X,
  backward X −= Y, twin gates ±1. The frame maps of the individual invocations are those of B₂ extended to more
  blocks; they are not re-derived here.
- **Inherited from #352/#346/#315:** the complex symbolic correctness, the precision/recovery and row interfaces,
  the additive row constants 9909 + 252, and the analytic transfer.
- **No new κ** is claimed. This is a conditional finite construction, not a formal verification of the
  multiplication theorem.

## Credits

- Jacob Sussman: the bridged five-stage word B₂ and its Lean geometry, which B₃ generalises; the E8 unit; gx,
  gxcore, the generators and the replay (wht-power-saving-lean, Apache-2.0).
- The complex checks: PR #352 on PR #346's port of PR #315's portable checks (#256/#233/#202/#200/#194/#184
  lineage).
- E8's devices from this repository: jamesyc #124 and eumemic #143; Chafik Boukhalfa #200/#233; icekylinx #184,
  carried in ikeboy's #191/#193.

See `NOTICE.md`.
