# Conditional κ = 793392809291691/10¹⁸: PR #346's bit word with a per-point p = 10 complex supplier

**Claim (conditional, finite).** Assume the inherited interfaces of PR #315/#325/#346. Take PR #346's final w3
bit word (bit coarse saving c = 32069035133443/(4·10¹⁶)) together with the complex program
`certificates/gcert1-p10-b325-c2.json.gz` (complex coarse saving b = 794022782431403/10¹⁸). Then PR #315's outer
assembly admits κ = 793392809291691/10¹⁸ with the complex side binding, and rejects the next 10⁻¹⁸ point. The
same computation applied to PR #346's own b = 396604388013523/(5·10¹⁷) gives PR #346's κ =
396290046684973/(5·10¹⁷) exactly.

## 1. The complex program

The program is PR #327's recipe and chain, vendored at `40ed045`, applied to the modules of `spec/c2.json`. Each
invocation has its own module:

| invocations | module |
|---|---|
| triple module | PR #327's `tmod_t2_p10.json` |
| 90 all-but-one invocations | PR #325's `qmod_p10.json` |
| pair invocations (i, 0) and (i, 1) | `modules/pointwise/pmod_i{i}.json` |

The layer is `layers/c2/`: 6,779 carrier arcs, 10,036 moved frames, 1,680 maximum-weight pairs and no kernel pairs.

The graph is built by `spec_graph.finish_spec`, which is PR #327's `centre46.finish_centre46` with the module
looked up per invocation. Two anchors check it against PR #327's code on the one-module-per-kind spec
`spec/uniform.json`:

- **(e)** `finish_spec` and `finish_centre46` build the same graph, in every field;
- **(f)** `aligned_word_spec.py --spec` and PR #327's `aligned_word_p.py --centre46` write the same seven files.

`aligned_word_spec.py` differs from `aligned_word_p.py` only in its graph-building branch.

The full run then applies PR #327's chain to the per-point word, and every step must pass:

1. the module contracts (`load_pmod46` for every pointwise module);
2. `compile_closure` on the frozen arcs, and the forward closure returning every frozen frame;
3. `paircheck.py` with five mutation controls;
4. PR #200's complete complex checker;
5. PR #184's flow (new R 6,253) and the exact lift;
6. PR #194's contract (13 checks);
7. PR #256's emitter, then `gx.check1` (labels, blocks, N = R·h + 2v(h − 1) + cst = 161,900, exact scalar
   identity) and the `gxcore` mirror, both on the raw program and on its star form;
8. the E5 controls;
9. byte equality with the committed program (canonical sha256 `ff2d7307…5112`).

**Price.** The five-stage word at h = 20 has H₅ = 5·H_inv + 2v(e₃₈ + e₁₉ + e₄₂ + e₄), m = 100, W = 4v + R =
10,093, deficit 2,040. The exact bounds give:

- PR #225's upper bound: a = 7940/10⁷, with and without the 10⁻¹⁶ fallback;
- source527's lower bound: 7941/10⁷ is rejected;
- both rational engines: b = 794022782431403/10¹⁸ with the fallback (794022785498833/10¹⁸ without), with the next
  10⁻¹⁸ point excluded.

The program has not been built in Lean (§4).

## 2. The bit word

The bit word is PR #346's and is vendored unchanged. `verify.py` checks the following:

- **records.** The decompressed final records match PR #346's `RECORD-SHA256SUMS` (`TT/249-records.bin`). They
  are 405,188 six-tuples: 47,020 MOVE, 358,128 ADD, 20 COPY and 20 ERASE.
- **paid children.** An independent recount over the MOVE and COPY records gives H (45,884 children, rank mass
  169,560).
- **normalized histogram.** PR #346's histogram is 60·H + 12·2v·(e₃₈ + e₁₉ + e₄₂ + e₄) exactly.
- **stock.** W = 125,712 = 12·(4v + 132,720/20), taken from PR #346's receipt.
- **bit saving.** Both engines certify c = 32069035133443/(4·10¹⁶) with the 10⁻¹⁶ fallback and exclude the next
  point. This equals PR #346's c.

The bit word's own legality (Design T, PR #266's checkers, primes, banks) is PR #346's claim and is not re-run here.

## 3. κ

The steps are PR #315's `math_check` (as in PR #329) on the complex-bound path:

1. β = 10⁻⁹, η = 10⁻¹², and the cap is (1 − β)·b.
2. Take s = min(c, ⌊cap − 10⁻¹⁸⌋₁₀⁻¹⁸). Here s < c, so the complex side binds. s is re-certified by the moment.
3. Bootstrap three times from 384599/10¹⁰: a ← (1 − s)·s + s·a.
4. Set q = a(1 − 2η) and minimum = (1 − η)·q/(1 + q). κ is the last 10⁻¹⁸ grid point strictly below the minimum.
5. `outer.assembly(a, b, bridge, κ)` passes all 47 strict constraints and the 7 margins. At κ + 10⁻¹⁸ it fails. At
   the cap itself it fails `leaf_saving_above_bit`.

The results:

| complex b | κ |
|---|---|
| PR #346: 396604388013523/(5·10¹⁷) | 396290046684973/(5·10¹⁷) ≈ 7.92580093369946·10⁻⁴ (reproduced) |
| this package: 794022782431403/10¹⁸ | **793392809291691/10¹⁸ ≈ 7.93392809291691·10⁻⁴** |

The gain is +812715921745/10¹⁸ = +0.1025 %.

## 4. What is not claimed

- **No Lean build of the 7940/10⁷ program yet.** It passes `gx.check1`, `gxcore` and every Python check above. The
  companion 7932/10⁷ program (`spec/uniform.json`) was built in Lean with Sussman's unchanged generator
  (`wht_main_block_B2Gcu32x` at 1 − 7932084/10¹⁰, `Compare.lean` PASS; `lean/companion-7932-evidence.txt`).
- **PR #346's bit-side obligations** are inherited unchanged: the w3 downstream chain is not ported to p = 10, the
  bank feasibility only, and the scalar/prime/finite stages.
- PR #315's portable complex checks, ported to p = 10 by PR #346 (labels, scalar words, splice, precision guard),
  are not run on this program.
- The five-stage B₂ ledger at h = 20 and the 10⁻¹⁶ fallback envelope are inherited assumptions, as in PR
  #327/#346.
- This is a conditional finite construction under the retained public all-size hypotheses, not a theorem about κ.
