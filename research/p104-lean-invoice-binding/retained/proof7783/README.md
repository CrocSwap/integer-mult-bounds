# p104-banked-banner: a kernel-checked κ banner for the banked class containing #7761

**Banner.** κ ≤ .00952683 (Lean: `κ < 2381707/250000000` = .009526828) for every banked native in class **C**
below, priced by #7761's invoice (2048-call caller block + 2048 × the native graph). For the current frontier #7761
(κ .0038207), **every premise except Valid is a kernel term**: `Bridge7761.kappa7761_lt_banner_head` instantiates the
headline on #7761's final graph, and its only hypothesis besides 0 < κ < 1 is `Valid`, i.e. κ is a crossing of #7761's
SPEC invoice, which is the definition of κ. Valid is satisfiable, so the witness is not vacuous: the invoice
F(1 − κ) is > 0 at κ = 1e-6 and = 0 at the published .0038206983 (Python only, see below).
**Outside Lean:** Valid; that the caller block T/P is the SPEC caller block of #7761 (Python); that the packed data is
the posted #7761 graph (generator only, `lean/tools/bridgegen/`); and P-NOCHAN.
Headline: `BankBannerHead.bank_kappa_lt_banner_head` (`lean/Nov15/BankBannerHead.lean`, a composition of
`BankMed.bank_kappa_lt_banner_tiedS_loc` with `BankPrem`'s invoice lemmas). Every listed theorem's axioms are within
`[propext, Classical.choice, Quot.sound]` (107 of the 122 print all three, 15 print a subset or none). There is no
`sorry`, `native_decide`, `axiom` or `extern`. Finite facts use `decide +kernel`. Every unproved premise is a **named
hypothesis in the signature**.

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

## Build and check
```
cd research/p104-banked-banner/lean
lake exe cache get   # Mathlib oleans (rev pinned in lakefile.toml / lake-manifest.json); toolchain v4.33.0-rc1
./check.sh           # builds build-order.txt (one lean at a time, RSS guard), then #print axioms on all of Check.lean
```
`check.sh` fails on a build error, `sorryAx`, `Lean.ofReduceBool`, any axiom outside the Mathlib three, a source-level
`axiom`/`extern`, an excluded module in `Nov15/`, or a headline that does not print. `CHECK-axioms.txt` is the
`#print axioms` output of `Check.lean` for these sources (122 names). `verify.py` (standard library, no Lean) checks
the file pins, the source-level token bans outside comments, the module set and import order, that every
`Check.lean` name is declared, the two headline signatures, the toolchain/Mathlib pins and `CHECK-axioms.txt`.
`BankBannerHead` is the packager's own composition file (20 lines, no new mathematics). Source comments carry
working labels (module provenance) and are not part of any statement.

## The class C (premises of the headline, per call i < 2048)
| Premise | Lean form | Status |
|---|---|---|
| Banked scalar graph over ℚ: P-LOC, P-ACYC, P-LIN (bank forms read their source chart; outputs read their chart) | `BankedGraph.N : Net` (`read`, `out`) | named; #7761: kernel (`Net7761 hO7761`) |
| All principal minors of O are nonzero | `BankedGraph.minors` | named; #7761: kernel |
| Main contract + chart model of the 14 + 14 flag rows | `BankedGraph.con : Contract` | named; #7761: kernel |
| P-NEST (every bank nested), P-POS (fields climb), 400 mains climbing 8 | `nest`, `climb`, `Mn`/`main8`/`card` | named; #7761: kernel |
| Height-stop contract: π injective, support {f, πf}, 104 + 104 partner rows | `HSContract` | named; #7761: kernel |
| Descents form ≤ 8 pure relay chains (charts b_k = a_{k+1}, β ≠ 0), injectively on banks | `ChainTie`, `card T ≤ 8` | named; #7761: kernel |
| G's outputs realise the live P104 pattern, up to nonzero scalars c | `ComputesS` | named; #7761: kernel |
| P-LOC at the ports: lq p ∈ A(xin p); B(yout s) ⊥ lq s | `hin`, `hout` | named; #7761: kernel |
| Every descent is a chain step | `hcov` | named; #7761: kernel |
| Mediation (odd pairs = Σ chain descents × gathers) | derived by `last_descent_split` | **proved** |
| Descent mass D ≥ 56 | `tie_desc_ge_56S` ← `chain_mass_ge_56` ← `DW7.D56_rank8_anyk` | **proved** |
| Height balance: the XBal model of G with owned registers satisfies Flow, and W ≥ 0 | `hF`, `hW` | named (W ≥ 0 ⟺ A ≥ D + Σc); #7761: kernel, W = 0 |
| X = 2D + W ≥ 112 | `XBal.Model.X_ge`, `xbal_tied`, `excess_ge_112` | **proved** |
| P-1S': each bank paid ≥ dh^s (paid := SPEC invoice latD^s) | `bankPrice_le_specInvoice` | **proved** |
| P-CALLER': Σ paid − Σ helper credit ≤ cdat T − cdat P | `hcaller_of_valid` from `hV : Valid` | reduced to **Valid** (κ is a crossing of the SPEC invoice: caller paid + natives ≤ root targets + helper credit), named |
| Caller block T/P = #7761's (`hT`, `hP`) | `consts7761` (lists decide-checked) | T/P = the SPEC caller block of #7761: Python-checked |
| Exact certificate F(1 − t) < 0 on [kbar, 1] | `BankBannerCert`, `BankBannerBud` | **proved** (kernel) |
| P-NOCHAN: the word is realisable as a banked graph | outside Lean | named; **not checkable from data** |

## #7761: every premise except Valid is a kernel term
`Bridge7761.kappa7761_lt_banner_head (κ) (hκ0) (hκ1) (hV : Valid (caller7761 hO7761) …) : κ < 2381707/250000000`
(Bridge7761T4) = `BankBannerHead.bank_kappa_lt_banner_head` applied to these kernel terms (data = packed numerals from
the generators in `lean/tools/bridgegen/`; 5746 banks, 1262 fields, 1099 charts):
- Net + BankedGraph: `Recipe7761` with all side conditions (`sc_fld7761`/`sc_ref7761`/`sc_out7761`), `hO7761`
  (the expanded bank forms reproduce O7761; Bridge7761PG via digit-uniqueness packing, P0 general lemmas), `Net7761`,
  `Con7761` (Contract, 14 + 14 rows), `minors7761`, `nest7761`, `climbA7761`/`card_Mn7761`/`main8_7761`, `G7761`.
- HSContract `HS7761` (`hsupp7761`, `piF_inj`, `hi_h7761`/`lo_h7761`/`nz_*`); ComputesS `computes7761` (c = 1 on 96
  ports, 1/2 on 8, `cdist`); `hin7761`, `hout7761`; `hcov7761`/`hcov7761G` (uses `nest7761`, `nDesc`).
- ChainTie `τ7761 : ChainTie (G7761 hO7761) (Fin 8)` (T1–T3: carried vectors read off the packed bank forms, fresh
  supports, β ≠ 0, injective steps; chain facts `chain0`–`chain7`, `pos_*`).
- Height balance `gflow7761`, `gW7761` (W = 0); also `flow7761`, `D7761` (56), `A7761`, `climb7761`, `X7761` (112).
- Alternatives: `kappa7761_lt_banner_hO` (reads D = 56 off the data via `descMass7761`/`xd7761`, no chain tie) and
  `kappa7761_lt_banner` (same, hO as a hypothesis).

**Valid is satisfiable (Python only).** Valid is paid ≤ credit at s = 1 − κ. With paid = Σ|ΔH|^s over the moves
(= Σ latD^s, `nest7761`) and credit = Σ_fields climb^s − 400·8^s (= Σ over non-mains, `main8`), plus #7761's caller
block, our exact Decimal model (70 digits) of #7761's invoice has F(1 − κ) > 0 at κ = 1e-6 and its root at
.0038206983256546…, which is #7761's published κ .00382069832557. So Valid holds on (0, .0038206983] and the #7761
instance is not vacuous; this evidence is Python, not Lean (the script is not included).

**Still outside Lean:** Valid (the SPEC crossing, which defines κ); T/P = the SPEC caller block of #7761 (`consts7761`
decide-checks the lists; their SPEC origin is Python); the packed data = the posted #7761 graph (generator only); and
P-NOCHAN.

## The #7761 graph and the generators (`lean/tools/bridgegen/`)
The graph is #7761's (Clear1nsight); it is not redistributed here. Identification: the final graph of #7761 has
canonical sha256 `c6387f5a887f3ef2e79782cf2d7d167aeae5e6cd1e92d577e4c6e610ed360f84` (the `graph_sha256` in #7761's
`research/p104-mixed-batch-boundary/evidence/application.json`). To rebuild it from #7761's posted files
(PR head `d5219594c9b0e80c002a75e79b85766256496b07`, `git fetch origin pull/7761/head`):
```
D=research/p104-mixed-batch-boundary/pr7756        # in a checkout of #7761's head
python3 lean/tools/bridgegen/apply.py $D/data/BASE-GRAPH.json.gz $D/data/BASE-INTERFACE.json $D/EDITS.json final7761.json.gz
# prints: public 1262 moves 5746 forms 7008 / sha256 c6387f5a887f3ef2e79782cf2d7d167aeae5e6cd1e92d577e4c6e610ed360f84
```
`apply.py` is our own transliteration of the edit application (data only). Then, in a scratch COPY of `lean/Nov15`:
```
export BRIDGE_OUT=/path/to/copy/of/Nov15 BRIDGE_GRAPH=final7761.json.gz BRIDGE_IFACE=$D/data/BASE-INTERFACE.json
cd lean/tools/bridgegen   # recipe.json / pq*.json / pb.json are written here
python3 gen.py --d123 --d45 && python3 gen4.py && python3 gen6.py && python3 gen6.py --recipe && python3 gen7.py \
  && python3 genP.py pd pq ps pb pc po
diff -r /path/to/copy/of/Nov15 ../../Nov15
```
On our run every generated file came out byte-identical, except `Bridge7761S1D.lean`, which carries one
hand-added line `import Mathlib.Data.Rat.Defs`. The generators check their own data in exact `Fraction`s.

## Ladder (each a kernel theorem on the same invoice)
| κ bound | Theorem | Extra premises beyond BankedGraph + P-1S' + P-CALLER' (both discharged/reduced to Valid in the `_spec`/`_head` forms) |
|---|---|---|
| .01994 / .019933 | `BankFit.bank_kappa_lt_flag` (`BankPrem.bank_kappa_lt_flag_spec`) / `_flag_tight` | none (flag rows) |
| .019187 (root .0191868719) | `BankFitHS.bank_kappa_lt_hs` | HSContract (height-stop) |
| **.009526828** (root .0095268277) | `BankBannerHead.bank_kappa_lt_banner_head` (`BankMed…tiedS_loc`) | HSContract, ≤ 8 chains, ComputesS, hin/hout/hcov, Flow + W ≥ 0 |

Non-vacuity of the structures: `BankFitB.nonvacuous` (BankedGraph) and `BankFitD.nonvacuous_hs` (+ HSContract), toy
graphs over ℚ with the real flag data; for the banner premise set, #7761 supplies every premise except Valid
(`kappa7761_lt_banner_head`). Supporting forms: `bank_kappa_lt_banner_tiedS` (Mediated as a premise),
`bank_kappa_lt_banner_tied` (c = 1), and `BankBanner.bank_kappa_lt_banner` / `BankPrem.bank_kappa_lt_banner_spec`
(D ≥ 56, X ≥ 2D as bare premises).

## Theorem W (descent shapes reduced to chain rows, each D ≥ 56 with ≤ 8 pieces)
`zlayout_mass_ge_56` (β = 0 splits), `zig_mass_ge_56` (zigzag chains, F3 support condition), `branch_mass_ge_56`
(fresh-free trunk), `merge_mass_ge_56` (gather-free tail), plus `_rank8` variants (any piece count, stacked rank ≤ 8).
These widen the chain lemma. The headline itself is stated for pure chains (`ChainTie`).

## Finding: a V-rooted chain design cannot gain (kernel-checked for ≤ 8 pure chains)
A pure relay chain of any drops, including a V-rooted chain (9 → 0), collapses on odd pairs to one rank-1 decoder row
with rowPrice ≤ drop (`ChainRow.RelayChain.chain_row`, `pairing_rank_le_drop`, `ChainLayout.mass_le`). clique8 forces
≥ 8 rows (`chains_ge_8`), so ≤ 8 pure chains give D ≥ 56 (`chain_mass_ge_56`): kernel. That merged E8 blocks are not
chain-realisable at any length is paper + exact Python (all 28 pairs, every gauge), not Lean. #7761's 8 chains are
exactly the 8-row optimum (drop 7 each).

## Not covered
- the banner theorem needs ≤ 8 PURE relay chains (`ChainTie`). Zigzag / branch / merge / β = 0-split shapes have only
  the D ≥ 56 lemmas (Theorem W), not a banner theorem. Zigzag + split combinations in one chain, and fresh-content
  trunks in mixed DAGs, have neither;
- Valid (the SPEC crossing, which defines κ) stays a hypothesis; T/P = the SPEC caller block is Python only; the
  packed data = the posted #7761 graph rests on the generators;
- ≥ 9 chains with stacked rank ≥ 9 (the decoder core; no decoder wall is assumed);
- other callers (the certificate is #7761's 2048-call caller block);
- W < 0 (the banner theorem needs W ≥ 0; on paper W ≥ −4 still gives κ < .01, not in Lean);
- words not realisable as banked graphs (P-NOCHAN).

## Excluded on audit
`BankBanner.bank_kappa_lt_banner_full` and `chain_desc_ge_56` (module BankBannerChain): audited as restating the
premise (free layout tied by one number). The module is not in the package, and `check.sh` and `verify.py` enforce
this. The closure contains BankFlagA, whose `cross_nested`/`d_le_one` are vacuous. No headline cites them: the flag
cut goes through `BankWireA.cross_nested_lt`. `R1_bank`, `word_snf`, `BarrierB0` and `netToDec8` are not headlines.

## Open next questions
- Discharge Valid's satisfiability in Lean: a kernel certificate that #7761's invoice F(1 − κ) is positive at some
  small κ, so the #7761 instance is non-vacuous in the kernel, not only in Python.
- A banner theorem (not only D ≥ 56) for zigzag, branch, merge and β = 0-split descent shapes.
- ≥ 9 chains with stacked rank ≥ 9 (the decoder core).

## Files
`lean/Nov15/` (213 modules, the import closure of `lean/All.lean`, in `lean/build-order.txt` order),
`lean/Check.lean` (axiom audit), `lean/check.sh`, `lean/tools/build.sh` (sequential guarded build),
`lean/tools/closure.sh` (how build-order.txt was computed), `lean/tools/bridgegen/` (graph rebuild + data generators),
`CHECK-axioms.txt`, `verify.py`, `MANIFEST.sha256`, TASK/SOURCES/VERIFY.json, LICENSE, NOTICE.md.
