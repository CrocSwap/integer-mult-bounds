# p104-banked-unified-banner: one kernel-checked κ banner for every caller of the per-call family × every unified descent layout

**Banner.** `BankUnify.bank_kappa_lt_unified` (Lean: `κ < 952721/100000000` = .00952721, certificate root
.009527209881) holds for

- **every caller** made of K > 0 calls of the fixed per-call block (targets 10 @ r9, 26 @ r17..65 step 8, 13 @ r129;
  paid 10 @ r1, 26 @ r8..56 step 8) plus a constant block (Tc, Pc) with cdat Tc ≤ cdat Pc on [0, 1]
  (`_fam` form; the sign form takes cdat T − cdat P ≤ K (cdat T1 − cdat P1) on [0, 1]). This covers #7761's 2048-call
  caller (constant 224 (9^s − 1 − 8^s) ≤ 0, `hTP7761`) and #7786's 48-call caller, which is exactly 48 × the per-call
  block with no constant (`consts7786`, decide-checked against `lean/tools/callergen/app7786-caller.json`);
- × **every banked graph** (per call) carrying a **unified descent layout** `ULayout` with ≤ 8 pieces:
  zigzag groups (a_j ⊇ b_j, b_j ≤ a_{j+1}, β ≠ 0; pure chains are the case a_{j+1} = b_j), trunks feeding any group
  step (deposits inside the W hull, `dep`, and re-ascent condition `reasc`), tails branching at any step (`ureasc`),
  free zero-relay chains (arbitrary β, no trunk/tail), and silent descents. Every field is a statement about G's banks,
  charts and bank forms; gathers are read off G (`BankMed.last_descent_split`).

OTI is handled per component: a component of trunks (W side) or tails (U side) is discharged by FOLD-disjointness or by
the Hall condition (both facts about G, proved), otherwise its OTI is the named hypothesis `OTIComp` for that component
only (`DischW`/`DischU`). `bank_kappa_lt_unified_disjoint` is hypothesis-free on OTI: every trunk feeds ≤ 1 group and
every tail is fed by ≤ 1 group. The other premises are named in the signature: `HSContract`, `ComputesS`, `hin`/`hout`,
Flow + W ≥ 0 (height balance), the caller sign condition, and `Valid` (κ is a crossing of the SPEC invoice, the
definition of κ).

Every listed theorem's axioms are within `[propext, Classical.choice, Quot.sound]`. There is no `sorry`,
`native_decide`, `axiom` or `extern`; finite facts use `decide +kernel`. No κ claim.

**Non-vacuity.** `Bridge7761.kappa7761_lt_unified` (8 chains entered as groups, via `ofGLayout ∘ ofChainTieG`) and
`kappa7761_lt_unified_W1` (8 free chains, via `ofDescentLayout ∘ ofChainTie`) instantiate
`bank_kappa_lt_unified_disjoint` on #7761's final graph and caller; their only hypotheses are 0 < κ < 1 and `Valid`.
These instances exercise **only pure chains** (Tr = Tu = Empty). **The trunk, zigzag and mid-chain-tail branches have
no G-level instance and may be vacuous.** Their layout-level consistency is shown only by an abstract model in F2^9 (a
7-dim head, a zigzag, a trunk depositing into a later step, a mid-chain tail) that satisfies every `ULayout` field not
involving G; no concrete banked graph with such branches is known (a `BankedGraph` needs 400 mains climbing 8, the flag
contract and nonzero minors).

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

## Build and check
```
cd research/p104-banked-unified-banner/lean
lake exe cache get   # Mathlib oleans (rev pinned in lakefile.toml / lake-manifest.json); toolchain v4.33.0-rc1
./check.sh           # builds build-order.txt (one lean at a time, RSS guard), then #print axioms on all of Check.lean
python3 -I -B ../verify.py   # static checks only (no Lean)
```
`CHECK-axioms.txt` is the `#print axioms` output of `Check.lean` (163 names) for these sources; `logs-clean.txt` is
the clean rebuild (no oleans present; `make -j6` over the import graph, `lake env lean` per module, Mathlib cache
reused). `verify.py` checks the file pins, token bans outside comments, the module set and import order, that every
`Check.lean` name is declared, the unified headline and #7761 witness signatures, that `_disjoint` takes no OTI
hypothesis, that the #7786 caller data equals `consts7786`, and regenerates `Nov15/BankCallerGenCert.lean`
byte-identical with `lean/tools/callergen/gen_callergencert.py`.

## Headline and supporting theorems
| Theorem | Statement |
|---|---|
| `BankUnify.bank_kappa_lt_unified` | sign-form caller × `ULayout` (≤ 8 pieces) × per-component `DischW`/`DischU` ⟹ κ < .00952721 |
| `BankUnify.bank_kappa_lt_unified_fam` | same, caller T = K·T1 ++ Tc, P = K·P1 ++ Pc, cdat Tc ≤ cdat Pc |
| `BankUnify.bank_kappa_lt_unified_disjoint` | same, no OTI hypothesis (disjoint feeding on both sides) |
| `BankUnify.ULayout.mass_ge_56_disch` / `_disjoint` | descent mass D ≥ 56 for the layout |
| `BankUnify.ULayout.core` | folding gives an 8-row decoder; per group dim(W hull) ≥ 8, dim(U hull) ≤ 1; D ≥ 56 + E_W + E_U |
| `BankUnify.UPre.carried_mul` | piece collapse along a zigzag (chain-row identity generalised) |
| `BankUnify.ofDescentLayout` / `ofGLayout` | the earlier descent layouts (five Theorem-W shapes) and Theorem-G layouts are `ULayout`s |
| `BankCallerGen.cert_gen` | exact certificate at .00952721 for every caller of the family, any K > 0 |
| `BankCallerGen.consts7786` | #7786's caller lists = 48 × the per-call block (`famT 48 []`, `famP 48 []`) |
| `ThmG.decouple`, `fold_W`/`fold_U`, `otiComp_disjoint`/`otiComp_hall` | Theorem G arithmetic, FOLD both sides, component OTI discharges |
| `ThmG.big_mass_floor_G` / `BankBig.bank_kappa_lt_big` | the two special cases (Theorem-G layouts; five-shape descent layouts) |
| `Bridge7761.kappa7761_lt_unified` / `_W1` | #7761 instances (pure chains), only `Valid` remains |

`ChainRow.*` (Theorem W, D ≥ 56 rows), `BankMed`, `BankPrem`, `XBal`, `BankFit*`, the decoder facts (`DFR`, `DW6`,
`DW7`) and the full #7761 data closure (`Bridge7761*`) are included, so the package is self-contained; their
headlines from #7783 are in `Check.lean` too.

## Premises (per call i < K)
| Premise | Lean form | Status |
|---|---|---|
| Banked scalar graph over ℚ (P-LOC, P-ACYC, P-LIN, minors, contract, nest, climb, 400 mains) | `BankedGraph` | named; #7761: kernel |
| Height-stop contract | `HSContract` | named; #7761: kernel |
| Descents fit a unified layout with ≤ 8 pieces (injective on banks; every non-layout descent silent) | `ULayout`, `pieces ≤ 8` | named; #7761: kernel (pure chains) |
| G's outputs realise the live P104 pattern up to nonzero scalars | `ComputesS` | named; #7761: kernel |
| Port locality | `hin`, `hout` | named; #7761: kernel |
| OTI per component | `DischW`/`DischU` (FOLD-disjoint ∨ Hall ∨ `OTIComp`) | FOLD, Hall **proved**; `OTIComp` named; none in `_disjoint` |
| Height balance: Flow and W ≥ 0 | `hF`, `hW` | named; #7761: kernel, W = 0 |
| Caller sign condition / family form | `hTP` / `hT`, `hP`, `hsign` | named; #7761 (`hTP7761`) and #7786 (`consts7786`) lists: kernel |
| P-CALLER' | from `hV : Valid` | reduced to **Valid**, named |
| Mediation, D ≥ 56, X = 2D + W ≥ 112, P-1S', exact certificate | | **proved** for the whole class |

Outside Lean: Valid; that the T/P lists are the SPEC caller blocks of #7761 / #7786 (data: generators and the
`caller` object of #7786's `evidence/application.json`, sha256 `88486d49…`); that the packed #7761 data is the posted
graph (generators in `lean/tools/bridgegen/`, graph sha256 `c6387f5a…`, not redistributed); P-NOCHAN. #7786's graph is
not used: this package does not show that #7786's native lies in the class.

## Scope relative to the paper statement
The layout is narrower than the paper's Theorem G: `reasc`/`ureasc` exclude a deposit outside the chart of an earlier
gatherable step, and `silent` requires every trunk bank to be non-gatherable or zero on the inputs (the paper only asks
"gather-free"). Trunks into free zero-relay chains are not covered (enter such chains as pure groups instead), and
gathered trunks are excluded (no bypass). A layout that leaves real mass out only weakens the bound: every layout
mass term is a sub-sum of `descMass G`.

## Data and generators
**#7786 caller** (`lean/tools/callergen/`): `app7786-caller.json` is the `caller` object of #7786's
`evidence/application.json` (file sha256 `88486d49f2ba1fc0e6c9f4a7402c82e91c44026cf90cd1387d1e5c45cf5e88d3`), copied
verbatim. The certificate module is regenerated byte-identical by
```
cd lean/tools/callergen
python3 gen_callergencert.py 112 952721/100000000 9527 BankCallerGenCert 1000000 HS BankCallerGenCert app7786-caller.json > out.lean
cmp out.lean ../../Nov15/BankCallerGenCert.lean
```
(`verify.py` runs this). `BankCallerGen.T48_eq`/`P48_eq`/`consts7786` then show by `decide` that these lists are
48 × the per-call block.

**#7761 graph** (`lean/tools/bridgegen/`, unchanged from #7783): the graph is #7761's (Clear1nsight) and is not
redistributed. Identification: canonical sha256 `c6387f5a887f3ef2e79782cf2d7d167aeae5e6cd1e92d577e4c6e610ed360f84`
(the `graph_sha256` in #7761's `research/p104-mixed-batch-boundary/evidence/application.json`). To rebuild it from
#7761's posted files (PR head `d5219594c9b0e80c002a75e79b85766256496b07`, `git fetch origin pull/7761/head`):
```
D=research/p104-mixed-batch-boundary/pr7756        # in a checkout of #7761's head
python3 lean/tools/bridgegen/apply.py $D/data/BASE-GRAPH.json.gz $D/data/BASE-INTERFACE.json $D/EDITS.json final7761.json.gz
# prints: public 1262 moves 5746 forms 7008 / sha256 c6387f5a887f3ef2e79782cf2d7d167aeae5e6cd1e92d577e4c6e610ed360f84
export BRIDGE_OUT=/path/to/copy/of/Nov15 BRIDGE_GRAPH=final7761.json.gz BRIDGE_IFACE=$D/data/BASE-INTERFACE.json
cd lean/tools/bridgegen   # recipe.json / pq*.json / pb.json are written here
python3 gen.py --d123 --d45 && python3 gen4.py && python3 gen6.py && python3 gen6.py --recipe && python3 gen7.py \
  && python3 genP.py pd pq ps pb pc po
diff -r /path/to/copy/of/Nov15 ../../Nov15
```
On the #7783 run every generated file came out byte-identical, except `Bridge7761S1D.lean`, which carries one
hand-added line `import Mathlib.Data.Rat.Defs` (generators and these modules are unchanged here; not rerun).

**Excluded module.** `BankBannerChain` (`bank_kappa_lt_banner_full`, `chain_desc_ge_56`) is not in the package, as in
#7783; `check.sh` and `verify.py` enforce this.

## Not covered
- ≥ 9 groups / stacked rank ≥ 9 (the decoder core); no decoder wall is assumed.
- General OTI: a component that is neither FOLD-disjoint nor Hall keeps `OTIComp` as a hypothesis. Outside this
  package an exhaustive search finds no violation for 3 heads fed by 2 drop-1 trunks; open are partial feeds of 4 heads
  by 3 trunks, m ≥ 4, multi-trunk components with drop ≥ 2, and 6-dim heads.
- Trunk, zigzag and mid-chain-tail branches: proved, but with no G-level instance (may be vacuous, see above).
- Valid stays a hypothesis (satisfiable for #7761 in Python, as in #7783); W < 0; other per-call blocks; words not
  realisable as banked graphs (P-NOCHAN).

## Open next questions
- A banked graph inhabiting the trunk, zigzag or mid-chain-tail branches of `ULayout` (G-level non-vacuity).
- OTI for every component, so that `OTIComp` can be dropped (minimal open shape: m + 1 heads fed by m drop-1 trunks
  with pairwise shared 6-dim subspaces).
- ≥ 9 groups with stacked rank ≥ 9 (the decoder core).
- A kernel certificate that Valid is satisfiable for #7761 (F(1 − κ) > 0 at small κ).

## Relation to #7783
This package extends #7783 (`research/p104-banked-banner`, κ < .009526828 for ≤ 8 pure chains on #7761's invoice),
which is unchanged. It is self-contained: the 213 modules of #7783 are included byte-identical, plus 8 new modules
(`BankBigA/B`, `ThmGA/B`, `BankCallerGen`, `BankCallerGenCert`, `BankUnifyA/B`). For #7761's own caller the #7783
constant .009526828 stays the sharper one; the unified banner trades it for .00952721 over the whole caller family and
the wider layout class.

## Files
`lean/Nov15/` (221 modules, the import closure of `lean/All.lean`, in `lean/build-order.txt` order), `lean/Check.lean`
(axiom audit), `lean/check.sh`, `lean/tools/build.sh` (sequential guarded build), `lean/tools/closure.sh` (how
build-order.txt was computed), `lean/tools/bridgegen/` (#7761 graph rebuild + data generators, as in #7783),
`lean/tools/callergen/` (caller certificate generator + #7786 caller data), `CHECK-axioms.txt`, `logs-clean.txt`,
`verify.py`, `MANIFEST.sha256`, TASK/SOURCES/VERIFY.json, LICENSE, NOTICE.md. Source comments are not part of any
statement.
