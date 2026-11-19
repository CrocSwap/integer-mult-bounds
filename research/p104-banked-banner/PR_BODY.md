Title: P104 banked-class banner in Lean: κ < .009526828 for banked natives on #7761's invoice; #7761 supplies every premise except Valid (no κ claim)

Lean-only package. No κ claim.

**Banner.** For every banked native in the class C below, priced by #7761's invoice (2048-call caller block + 2048 × the native graph), κ < 2381707/250000000 = .009526828 (certificate root .0095268277). Kernel-checked, Lean 4.33.0-rc1 with pinned Mathlib; every listed theorem's axioms are within [propext, Classical.choice, Quot.sound]; no `sorry`, `native_decide`, `axiom` or `extern`; finite facts by `decide +kernel`. Every unproved premise is a named hypothesis in the signature.

**#7761 is in C, up to Valid.** `Bridge7761.kappa7761_lt_banner_head` applies the headline to #7761's final graph: every premise except `Valid` is a kernel term built from packed data for that graph (5746 banks, 1262 fields, 1099 charts). Its only hypotheses are 0 < κ < 1 and `Valid` (κ is a crossing of #7761's SPEC invoice, i.e. the definition of κ). Valid is satisfiable, so the instance is not vacuous: our exact Python model of #7761's invoice has F(1 − κ) > 0 at κ = 1e-6 and its root at .0038206983, #7761's published κ (Python only).

Headline theorems:
- `BankBannerHead.bank_kappa_lt_banner_head`: the banner for class C (composition of `BankMed.bank_kappa_lt_banner_tiedS_loc` with `BankPrem.bankPrice_le_specInvoice` and `BankPrem.hcaller_of_valid`).
- `Bridge7761.kappa7761_lt_banner_head`: the #7761 instance (alternatives `kappa7761_lt_banner_hO`, `kappa7761_lt_banner`).
- Supporting: `ChainRow.chain_mass_ge_56` (≤ 8 pure relay chains give descent mass D ≥ 56), `BankMed.last_descent_split` (mediation derived), `BankBanner.excess_ge_112` (X = 2D + W ≥ 112), `BankPrem.bankPrice_le_specInvoice` (P-1S').

| Premise of the headline | In the kernel for #7761 | Outside Lean |
|---|---|---|
| Banked graph (P-LOC, P-ACYC, P-LIN), nonzero principal minors, flag contract, P-NEST, P-POS, 400 mains climbing 8 | yes (`Net7761`, `minors7761`, `Con7761`, `nest7761`, …) | |
| Height-stop contract `HSContract` | yes (`HS7761`) | |
| ≤ 8 pure relay chains `ChainTie`, ports `hin`/`hout`, coverage `hcov`, `ComputesS` | yes (`τ7761`, `hin7761`, `hout7761`, `hcov7761G`, `computes7761`) | |
| Height balance Flow, W ≥ 0 | yes (`gflow7761`, `gW7761`, W = 0) | |
| Mediation, D ≥ 56, X ≥ 112, P-1S', exact certificate | proved for the whole class | |
| P-CALLER' | reduced to `Valid` | **Valid** = the SPEC crossing (definition of κ); satisfiable in Python |
| Caller block T/P (`hT`, `hP`) | lists decide-checked (`consts7761`) | T/P = #7761's SPEC caller block: Python |
| Packed data | Lean numerals | data = the posted #7761 graph: generators (shipped) |
| P-NOCHAN (word realisable as a banked graph) | | named; not checkable from data |

**Lower proved rungs** (same invoice, kernel): κ < .01994 / .019933 for banked graphs with the flag rows only (`BankFit.bank_kappa_lt_flag`, `_flag_tight`, `BankPrem.bank_kappa_lt_flag_spec`); κ < .019187 with the height-stop contract (`BankFitHS.bank_kappa_lt_hs`). Structures are non-vacuous on toy graphs over ℚ (`BankFitB.nonvacuous`, `BankFitD.nonvacuous_hs`). Theorem W gives D ≥ 56 for zigzag, branch, merge and β = 0-split descent shapes (`zig_mass_ge_56`, `branch_mass_ge_56`, `merge_mass_ge_56`, `zlayout_mass_ge_56`, with `_rank8` variants).

**Not covered.**
- The banner needs ≤ 8 pure relay chains; other descent shapes have only the D ≥ 56 lemmas, not a banner theorem; zigzag + split combinations in one chain and fresh-content trunks in mixed DAGs have neither.
- Valid stays a hypothesis; T/P = the SPEC caller block and packed data = the posted graph are not in Lean.
- ≥ 9 chains with stacked rank ≥ 9 (the decoder core); no decoder wall is assumed.
- Other callers (the certificate is #7761's 2048-call caller block).
- W < 0.
- Words not realisable as banked graphs (P-NOCHAN).

**How to check.**
```
cd research/p104-banked-banner/lean
lake exe cache get    # pinned Mathlib 55b7917b, toolchain v4.33.0-rc1
./check.sh            # sequential guarded build of build-order.txt, then #print axioms on Check.lean (122 names)
python3 -I -B ../verify.py   # static checks only: pins, token bans, module order, declared names, headline signatures
```
`CHECK-axioms.txt` is the `#print axioms` output for these sources. #7761's graph is not redistributed: it is identified by graph sha256 `c6387f5a887f3ef2e79782cf2d7d167aeae5e6cd1e92d577e4c6e610ed360f84` and rebuilt from #7761's posted files by `lean/tools/bridgegen/apply.py`; the generators then regenerate the packed Lean data (README).

The construction under study is Clear1nsight's #7761 and the PRs it builds on. DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
