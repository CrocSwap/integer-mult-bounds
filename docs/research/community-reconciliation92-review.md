# Completion of the frozen 100-PR reconciliation

This review finishes the **92 carry-forwards** after #2/#3/#4/#8/#9/#12/#90/#183.
The final live reconciliation records **99 of the original 100 resolved**, with **91 PRs
closed in this completion** and #122 still open for its missing parent artifacts.
See the [final snapshot](../../research/community-reconciliation92-audit/FINAL-100-SNAPSHOT.json)
and [closure receipts](../../research/community-reconciliation92-audit/CLOSURE-RECEIPTS.json).
It incorporates historical construction, proof, verification and tooling contributions;
it does **not** change the selected conditional frontier, establish the full multiplication
theorem, or turn an author's saved receipt into a fresh maintainer replay.

The selected record remains `certificates/selected-result.json`:
κ = 836330098538459 / 500000000000000000 = 0.001672660197076918.

## Dispositions and reproducibility

The [machine-readable decisions](../../research/community-reconciliation92-audit/DISPOSITIONS.json)
separate source review, execution, publication and actual GitHub closure. **#122 stays open**
for missing complete parent circuit/profile inputs. Its useful terminal-elision argument
and attribution are preserved while that reproducibility obligation remains unresolved.
The other 91 are reconciled as historical contributions, with the qualifications below.

All 92 complete original trees are retained through a separate
[source-retention tag](https://github.com/CrocSwap/integer-mult-bounds/tree/archive/pr-reconciliation100-20261013).
That tag joins the original heads solely for Git object retention. It is **not merged into
main's ancestry**, and its existence does not approve all claims or automatically resolve
ancestor PRs. This avoids another duplicate half-gigabyte source bundle.
[Source inventories](../../research/community-reconciliation92-audit/SOURCES.json.gz) bind Git
commit/tree/blob IDs, SHA-256 file digests, original comparison bases, attribution and complete
diff coverage. Current-main exact-blob reuse is recorded separately.

To obtain one original runnable tree:

```sh
python3 research/community-reconciliation92-audit/replay.py --pr 70 --fetch --destination /tmp/pr70-review
```

Use [EXECUTION.json](../../research/community-reconciliation92-audit/EXECUTION.json) for recorded
commands and [CI-EVIDENCE.json.gz](../../research/community-reconciliation92-audit/CI-EVIDENCE.json.gz)
for exact-head historical CI. Local temporary paths in receipts must be replaced by the recreated
checkout and pinned baseline locations. The replay command materializes source; it does not run
science implicitly. `verify.py --git-blobs` authenticates sources and review integrity, not mathematics.

## What was checked and what remains conditional

Fresh focused checks cover the early source/stage chain, with all 303 tests at #15 and additional
own drivers for #22/#27/#34/#35/#41. #70/#75 have fresh native full-word and small Lean project builds;
#77/#81/#102/#110/#128/#138/#146 have dedicated replays. #162/#178/#182/#185/#187/#189 have fresh
full package replays. #83 combines fresh arithmetic/negative checks with its exact-head full Linux
menu run. Other historical variants use specifically identified prior integration and exact-head CI
coverage, not a claim that every old verifier was rerun locally.

Failures are preserved. #41's first command named a nonexistent driver, then both correct drivers
passed. #110 initially lacked its external input argument, then passed with exact pinned inputs;
its red historical CI was a stale inherited Makefile hash. #138's documented command failed sibling imports/data lookup; a fresh exact certificate passed after
staging its unchanged, SHA-pinned sibling inputs (see the retained repair138 runner). #188 stopped before mathematics at a
macOS RLIMIT_AS call; the exact-head Linux full-word and assembly job passed. Draft proof obligations
in #68/#110 and inherited analytic/compiler assumptions remain qualified. **#145's paired-lockstep
claim was retracted; only its valid unpaired witness and the failure lesson are retained.** Generic
`formal(matrix)` CI is not evidence for newly added Lean packages; #91/#141 formal scope is stated below.

PR #154 is actively adapted as an opt-in `make verify-parallel JOBS=2` runner. It rejects invalid job
counts and unsafe groups, preserves tracked ignored files and deletions, isolates mutable checkouts,
and propagates failures. Six adversarial tests cover these properties. Its historical frame optimizer
is retained separately; it does not replace the currently pinned compiler.

## Per-contribution review and credit

Each row links the original PR and preserves its author. Predecessor/coauthor acknowledgments in
all original notices, proof notes and PR bodies are retained in the full source record. Ordering is
by PR number, not a ranking of importance.

| PR / contributor | Contribution | Review scope and limitations |
|---|---|---|
| [#5](https://github.com/CrocSwap/integer-mult-bounds/pull/5) — eumemic (@eumemic) | Chirped Gaussian correlations and the potential estimate for correction powers remove the historical epsilon<1/5 bottleneck. | Nine fresh tests cover identities and negative parameter controls. Historical analytic proof remains conditional; subsequent input-error corrections in the current chain take precedence. |
| [#6](https://github.com/CrocSwap/integer-mult-bounds/pull/6) — eumemic (@eumemic) | Aligned global pair groups and the h(h-1) center accounting refine the paired network. | Fresh tests, certificate generation and patch application; complete historical proof retained. Not merely a duplicate of #2. |
| [#7](https://github.com/CrocSwap/integer-mult-bounds/pull/7) — Zhihao Chen (@jacklightChen) | Ternary five-subset bit construction and paired complex motif at h=28. | Fresh tests and native full-size producer replay; no claim of an optimal family or practical speedup. |
| [#13](https://github.com/CrocSwap/integer-mult-bounds/pull/13) — eumemic (@eumemic) | Source-frame relocation and a third complex child class preserve rank mass while improving the block distribution. | Focused source-frame tests; all endpoint identity obligations retained. Reuses the previously reviewed integration chain rather than rerunning every historical compiler. |
| [#14](https://github.com/CrocSwap/integer-mult-bounds/pull/14) — rohanarun (@rohanarun) | Common rational bases create larger data corners. | Fresh witness replay. The written finite-polynomial argument, not random numeric samples, supplies existence of the simultaneous basis. |
| [#15](https://github.com/CrocSwap/integer-mult-bounds/pull/15) — eumemic (@eumemic) | Rectangular streaming and four-star resynthesis at h=30, including the complex residual inventory. | All 303 tests replayed. Auxiliary searches are bounded experiments, not optimality theorems; full native production for every alternative was not rerun. |
| [#16](https://github.com/CrocSwap/integer-mult-bounds/pull/16) — Zhihao Chen (@jacklightChen) | Nested source bases and all-residual guards. | Five focused integration tests; preserves the nested basis compatibility and full residual accounting. |
| [#17](https://github.com/CrocSwap/integer-mult-bounds/pull/17) — rohanarun (@rohanarun) | Compatible source boundaries improve the nested stream. | Fresh nested-stream tests; entrance work is not counted twice. |
| [#19](https://github.com/CrocSwap/integer-mult-bounds/pull/19) — rohanarun (@rohanarun) | Partial-swap ternary construction removes a legacy outer shear. | Focused tests include nonsymmetric controls; source archive retains all alternative experiments with their stated scope. |
| [#21](https://github.com/CrocSwap/integer-mult-bounds/pull/21) — Zhihao Chen (@jacklightChen) | Translated second-stage partial swaps and corrected complex phase gauge. | Fresh translated-partial tests; phase and coefficient accounting remain part of the contract. |
| [#22](https://github.com/CrocSwap/integer-mult-bounds/pull/22) — Dominik Scholz (@DominikScholz) | Exact parameter refinement of the unchanged translated-partial construction. | Fresh own driver and negative controls; grid rejection is only for its sufficient rational envelope, not a universal ceiling. |
| [#23](https://github.com/CrocSwap/integer-mult-bounds/pull/23) — Zhihao Chen (@jacklightChen) | Semantic bulk accounting with C1=1 and a fully charged literal bound. | Fresh semantic-bulk tests. Retains RaD's bulk/routing/phase attribution and inherited analytic assumptions. |
| [#25](https://github.com/CrocSwap/integer-mult-bounds/pull/25) — rohanarun (@rohanarun) | A5 Schur blocks preserve rank mass with a different child distribution. | Fresh semantic tests; finite-interface and analytic assumptions remain explicit. |
| [#27](https://github.com/CrocSwap/integer-mult-bounds/pull/27) — Dominik Scholz (@DominikScholz) | Compose the endpoint bit supplier with the semantic bulk reduction. | Fresh own certificate and negative controls; compatible bit/complex/row stocks are charged together. |
| [#28](https://github.com/CrocSwap/integer-mult-bounds/pull/28) — rohanarun (@rohanarun) | Rectangular semantic basis and its downstream assembly. | Focused rectangular-semantic tests; the complete historical dependency snapshot is preserved. |
| [#29](https://github.com/CrocSwap/integer-mult-bounds/pull/29) — Zhihao Chen (@jacklightChen) | Two-stage construction with separate compatible interfaces. | Focused two-stage tests and previously reviewed downstream integration; no new current frontier. |
| [#31](https://github.com/CrocSwap/integer-mult-bounds/pull/31) — rohanarun (@rohanarun) | Ordered 51/45 corner blocks and their rank-cut argument. | Focused corner tests; preserves the actual order rather than treating dimensions as interchangeable. |
| [#33](https://github.com/CrocSwap/integer-mult-bounds/pull/33) — Dominik Scholz (@DominikScholz) | Smaller 47/45 dimensions with regenerated rank identities. | Focused dimension tests; retained certificate and native sources remain separately reproducible. |
| [#34](https://github.com/CrocSwap/integer-mult-bounds/pull/34) — James Chang (@jamesyc) | Reversed 45/47 construction and balanced layout. | Fresh pinned scientific checker via portable reproduce.py, plus inherited tests. Not just removal of an assembly constraint. |
| [#35](https://github.com/CrocSwap/integer-mult-bounds/pull/35) — Dominik Scholz (@DominikScholz) | Fixed I+J basis and a conservative 43-dimensional block. | Fresh own verifier and negative controls; no unsupported 37-dimensional claim. |
| [#38](https://github.com/CrocSwap/integer-mult-bounds/pull/38) — Dominik Scholz (@DominikScholz) | Copied fixed-basis rank-one cleanup. | Fresh complete certificate driver; every paid center copy and data endpoint remains in the ledger. |
| [#40](https://github.com/CrocSwap/integer-mult-bounds/pull/40) — rohanarun (@rohanarun) | Both fixed axes reversed, with the full pair I+J source geometry. | Focused tests and later integration evidence; source-frame compatibility is retained. |
| [#41](https://github.com/CrocSwap/integer-mult-bounds/pull/41) — Andrzej Marszałek (@hipotures) | RaD association and alternating producer arithmetic with exact composition. | Both own arithmetic drivers replayed. Arithmetic does not by itself certify a changed producer; later #42 replay provides separate integration evidence for the alternating construction. Preserve this distinction. |
| [#42](https://github.com/CrocSwap/integer-mult-bounds/pull/42) — rohanarun (@rohanarun) | Combine RaD's alternating producers with fixed reversed geometry. | Focused tests; previously reviewed full profiles supply construction evidence. Credits both contributions. |
| [#44](https://github.com/CrocSwap/integer-mult-bounds/pull/44) — rohanarun (@rohanarun) | Search for improved compatible matchings. | Focused matching and fixed-basis tests. Floating-point optimization chooses candidates; it is not a proof of global optimality. |
| [#47](https://github.com/CrocSwap/integer-mult-bounds/pull/47) — rohanarun (@rohanarun) | Climb producer choices with portable source vectors. | Focused producer tests; bounded search, not a globally optimal construction. |
| [#63](https://github.com/CrocSwap/integer-mult-bounds/pull/63) — Dominik Scholz (@DominikScholz) | Rank-first choices among eligible clearing controls. | Exact-head CI evidence and source review; eligibility and literal paid work remain mandatory. |
| [#65](https://github.com/CrocSwap/integer-mult-bounds/pull/65) — rohanarun (@rohanarun) | Region ordering subject to the dependency DAG. | Exact-head CI evidence; rank ties alone do not authorize an invalid schedule. |
| [#66](https://github.com/CrocSwap/integer-mult-bounds/pull/66) — chafreaky (@chafreaky) | Joint split/dual source combinations with restored import state. | Exact-head CI evidence; retains the independent word checker and complete profile rather than assuming additive gains. |
| [#67](https://github.com/CrocSwap/integer-mult-bounds/pull/67) — rohanarun (@rohanarun) | Optimize actual profile cost with stable candidate evaluation. | Exact-head CI evidence; heuristic objective does not certify global optimality. |
| [#68](https://github.com/CrocSwap/integer-mult-bounds/pull/68) — Dominik Scholz (@DominikScholz) | Cost-aware live frames F subset E subset G and a global-anchor negative argument. | Exact-head evidence for the main construction. Supplemental cost-live-both proof is explicitly a draft with replay outstanding; preserved as research, not an accepted extra bound. |
| [#70](https://github.com/CrocSwap/integer-mult-bounds/pull/70) — Alejandro Zarzuelo Urdiales (@alejandrozu) | Profile-aware carry exchange and standalone finite Lean endpoints. | Fresh native full-word ordinary/dirty checks and Frozen62Research Lean build. Formal scope is the finite arithmetic interface, not the multiplication theorem. |
| [#71](https://github.com/CrocSwap/integer-mult-bounds/pull/71) — chafreaky (@chafreaky) | Anchored splits with strict contraction and dirty-state obligations. | Retains the earlier fresh physical replay and 23 tests; exact-head CI supplements rather than replaces that scoped review. |
| [#75](https://github.com/CrocSwap/integer-mult-bounds/pull/75) — Alejandro Zarzuelo Urdiales (@alejandrozu) | Kernel-zero toggles with excluded target and live-frame bounds. | Fresh native full-word checks and CurrentRecordMath Lean build. No full analytic formalization claim. |
| [#77](https://github.com/CrocSwap/integer-mult-bounds/pull/77) — huxint (@huxint) | Balanced splitting, carry cycles and coordinate flags. | Fresh rebuild and tests of the dedicated package; complete W and finite bridge are charged. |
| [#78](https://github.com/CrocSwap/integer-mult-bounds/pull/78) — rohanarun (@rohanarun) | Relabel by permutations commuting with I+J. | Exact-head CI evidence; internal profiles are recomputed, while the full Cartesian data invariant is preserved. |
| [#79](https://github.com/CrocSwap/integer-mult-bounds/pull/79) — chafreaky (@chafreaky) | Balanced row/column partitions and legal carry choices. | Exact-head CI evidence; complete future unit basis required, gains are not simply added. |
| [#80](https://github.com/CrocSwap/integer-mult-bounds/pull/80) — rohanarun (@rohanarun) | Select compatible axes with the correct stock and bridge. | Earlier full physical replay and stale-width correction retained; exact-head CI evidence included. |
| [#81](https://github.com/CrocSwap/integer-mult-bounds/pull/81) — Dominik Scholz (@DominikScholz) | Bounded column-carry variants of the same construction. | Fresh dense audit and selected-word validation against an exact #71 baseline; portable regenerated evidence distinguished from the original claim. |
| [#82](https://github.com/CrocSwap/integer-mult-bounds/pull/82) — rohanarun (@rohanarun) | Compose before compiling and use coordinate cost oracles. | Exact-head CI evidence; oracle scores remain candidate-selection heuristics. |
| [#83](https://github.com/CrocSwap/integer-mult-bounds/pull/83) — Joseph Demarest (@JosephDemarest) | Shared work functional for an adaptive depth menu. | Fresh arithmetic, independent checks and tests; exact-head full Linux menu CI retained. Scoped 64-profile family, not a universal algorithmic lower bound. |
| [#84](https://github.com/CrocSwap/integer-mult-bounds/pull/84) — chafreaky (@chafreaky) | Retired/pending indices, atomic two-cycle changes and contracting multisplits. | Exact-head CI evidence; serial lifecycle and ordering obligations reviewed. |
| [#85](https://github.com/CrocSwap/integer-mult-bounds/pull/85) — rohanarun (@rohanarun) | Coordinate relabeling in dimensions three and four. | Exact-head CI profile evidence; no automatic gain from relabeling without recompilation. |
| [#86](https://github.com/CrocSwap/integer-mult-bounds/pull/86) — rohanarun (@rohanarun) | Coordinate oracle and short carry cycles. | Exact-head CI evidence; independence and partition conditions retained. |
| [#87](https://github.com/CrocSwap/integer-mult-bounds/pull/87) — gupt1156 (@gupt1156) | Congruent [4,4,1] splitting. | Exact-head CI evidence; scoped finite improvement, not optimality. |
| [#88](https://github.com/CrocSwap/integer-mult-bounds/pull/88) — chafreaky (@chafreaky) | Whole-construction selection from a bounded portfolio. | Exact-head CI evidence; 51,525-candidate search scope retained, not a global ceiling. |
| [#89](https://github.com/CrocSwap/integer-mult-bounds/pull/89) — rohanarun (@rohanarun) | Null-circuit Gaussian relations preserve XOR action. | Exact-head CI evidence includes physical validation; scalar cancellation alone is insufficient. |
| [#91](https://github.com/CrocSwap/integer-mult-bounds/pull/91) — chafreaky (@chafreaky) | Aligned frames plus rational Lean endpoint arithmetic. | Finite numerical/physical CI and saved Lean source/axiom evidence retained. Generic formal(matrix) CI does not establish the new Lean module; no fresh full kernel rebuild claimed here. |
| [#92](https://github.com/CrocSwap/integer-mult-bounds/pull/92) — maxime-fleury (@maxime-fleury) | Dependency-valid region ordering and saved-word resynthesis. | Exact-head CI evidence; actual DAG compatibility retained. |
| [#93](https://github.com/CrocSwap/integer-mult-bounds/pull/93) — rohanarun (@rohanarun) | Adjacent coordinate flags and complete profile reassembly. | Exact-head CI evidence; historical variant retained independently of the selected record. |
| [#94](https://github.com/CrocSwap/integer-mult-bounds/pull/94) — maxime-fleury (@maxime-fleury) | Adjacent-flag improvement with inherited formal artifacts. | Exact-head CI evidence. The older #91 Lean package is not a formal proof of this newer kappa. |
| [#95](https://github.com/CrocSwap/integer-mult-bounds/pull/95) — rohanarun (@rohanarun) | Further adjacent-flag selection and full composition. | Exact-head CI evidence; inherited analytic interfaces remain assumptions. |
| [#97](https://github.com/CrocSwap/integer-mult-bounds/pull/97) — Zhihao Chen (@jacklightChen) | Stable commuting fans and reflected event ledgers. | Exact-head CI plus the separately retained verifier-hardening patch. Signed complex endpoint correction and Gaussian phase remain explicit. |
| [#98](https://github.com/CrocSwap/integer-mult-bounds/pull/98) — rohanarun (@rohanarun) | Coordinate pricing with the baseline legal engine. | Exact-head CI evidence. The long-cycle search accepted zero candidates; retained as a scoped negative experiment. |
| [#100](https://github.com/CrocSwap/integer-mult-bounds/pull/100) — rohanarun (@rohanarun) | Prefix refinement and a separate balanced physical layout experiment. | Exact-head CI evidence; original source and log-regeneration provenance remain separate from later experiments. |
| [#102](https://github.com/CrocSwap/integer-mult-bounds/pull/102) — SovereignSteak (@SovereignSteak) | Monotone moment follow-up with an exact fixed grid. | Fresh dedicated verifier; arithmetic-only improvement, no new physical circuit. |
| [#103](https://github.com/CrocSwap/integer-mult-bounds/pull/103) — rohanarun (@rohanarun) | Saturated frames and nondegenerate backward extension. | Exact-head CI evidence includes target-edge accounting; zero-rank mass changes are explicitly charged. |
| [#106](https://github.com/CrocSwap/integer-mult-bounds/pull/106) — Thomas Marchand (@Th0rgal) | Contiguous pair exchanges and minimum-cost circuits. | Exact-head CI evidence; role increases and offsets are included in complete W, not silently canceled by heuristic scores. |
| [#107](https://github.com/CrocSwap/integer-mult-bounds/pull/107) — rohanarun (@rohanarun) | Reverse-pair leaves on disjoint supports. | Exact-head CI evidence; legal matching and unchanged coefficient denominator retained. |
| [#108](https://github.com/CrocSwap/integer-mult-bounds/pull/108) — rohanarun (@rohanarun) | Dual suffixes trade more additions for fewer roles. | Exact-head CI evidence; both literal pieces remain paid. |
| [#109](https://github.com/CrocSwap/integer-mult-bounds/pull/109) — rohanarun (@rohanarun) | Matching selection with independently audited binary frames. | Exact-head CI evidence. Float matching is only a proposal mechanism; actual eligibility and histogram nonnegativity are checked separately. |
| [#110](https://github.com/CrocSwap/integer-mult-bounds/pull/110) — Avi Eisenberg (@ikeboy) | Deferred complex stages plus stopped-depth bit accounting. | Fresh complex, supplied-input bit and assembly arithmetic retained. Original full complex stage-2 proof obligation is not discharged by randomized modular tests. Historical conditional research only; stale Makefile-pin CI failure and corrected local invocation recorded. |
| [#111](https://github.com/CrocSwap/integer-mult-bounds/pull/111) — rohanarun (@rohanarun) | Cyclic strips on both axes and positive matchings. | Exact-head CI evidence; actual matchings and envelope bounds are distinct checks. |
| [#113](https://github.com/CrocSwap/integer-mult-bounds/pull/113) — rohanarun (@rohanarun) | Refinement of deferred/stopped accounting. | Exact-head CI evidence. Early copied PROOF sections describe an older checkpoint; current certificate and README control its historical claim. |
| [#114](https://github.com/CrocSwap/integer-mult-bounds/pull/114) — eumemic (@eumemic) | Completed-core sharing with full pre-exterior accounting. | Exact-head CI evidence; current head differs from obsolete PR-body narrative. No silent zeroing of auxiliary input. |
| [#116](https://github.com/CrocSwap/integer-mult-bounds/pull/116) — rohanarun (@rohanarun) | Cube-deferred construction with reflection and coefficient obligations. | Exact-head CI evidence; finite checks retain stated reflection/analytic dependencies. |
| [#117](https://github.com/CrocSwap/integer-mult-bounds/pull/117) — eumemic (@eumemic) | Replayed complex producer and stopped bit supplier. | Exact-head CI evidence retains 91,770 additions and 28,705 complex roles; full composition rather than isolated savings. |
| [#118](https://github.com/CrocSwap/integer-mult-bounds/pull/118) — rohanarun (@rohanarun) | Repair the 55/42 coefficient by splitting it into 1+13/42. | Exact-head CI evidence; both scalar additions are charged. This is not a free precision improvement. |
| [#121](https://github.com/CrocSwap/integer-mult-bounds/pull/121) — Thomas Marchand (@Th0rgal) | Staggered prefix/suffix pairs with compatible supports. | Exact-head CI evidence; joint and complex-only snapshots remain distinct. |
| [#122](https://github.com/CrocSwap/integer-mult-bounds/pull/122) — SovereignSteak (@SovereignSteak) | Terminal elision cancels initial dirty terms and redirects actual chronological reads. | BLOCKED: full pinned parent word and parent profile absent from the original tree and all 92 source inventories. Delta file and modular receipt do not replace that parent. Preserve scoped proof and credit; keep PR open for reproducible full replay. |
| [#123](https://github.com/CrocSwap/integer-mult-bounds/pull/123) — rohanarun (@rohanarun) | Seed-1 tie-order search with independent frame validation. | Exact-head CI evidence; retains the unit-split coefficient repair and bounded heuristic scope. |
| [#124](https://github.com/CrocSwap/integer-mult-bounds/pull/124) — James Chang (@jamesyc) | Reuse at a legal birth cut with exact dirty-state compensation. | Exact-head CI evidence; inverse chronology and feasible moment majorization retained, no reset assumed. |
| [#125](https://github.com/CrocSwap/integer-mult-bounds/pull/125) — Joel Pulikkan (@GamingPuzzled) | Shrink to the minimal nondegenerate span inside a successor frame. | Exact-head CI evidence; recomputed profile and fixed target-frame boundaries required. |
| [#128](https://github.com/CrocSwap/integer-mult-bounds/pull/128) — Andrey Mas (@an664) | Completed-core sharing with separate dirty-restored cores. | Fresh dedicated full replay; signed phase and physical scratch allocation matter. No identification of independent dirty inputs. |
| [#129](https://github.com/CrocSwap/integer-mult-bounds/pull/129) — eumemic (@eumemic) | Rational 9I-J sunflower geometry and source gauge. | Exact-head CI evidence; 161 groups and the complete tail are paid. |
| [#131](https://github.com/CrocSwap/integer-mult-bounds/pull/131) — eumemic (@eumemic) | Three-stage cover with general Clifford phases. | Exact-head CI evidence for finite construction; uniform phase/compiler contracts remain assumptions, not consequences of geometry alone. |
| [#133](https://github.com/CrocSwap/integer-mult-bounds/pull/133) — Thomas Marchand (@Th0rgal) | Radical complements, phase-aware roles, lazy deferral and plateau pricing. | Exact-head CI evidence; whole-profile accounting, not additive local savings. |
| [#137](https://github.com/CrocSwap/integer-mult-bounds/pull/137) — eumemic (@eumemic) | Pad to 72 with local copies and sequential banks. | Exact-head CI evidence; unpaired sequential banks, rank-zero adapters, scalar costs and rare-class factor are retained. |
| [#138](https://github.com/CrocSwap/integer-mult-bounds/pull/138) — Abhinav Ramachandran (@geckods) | Tighten beta/backoff on the frozen #137 construction. | Fresh exact certificate after repairing the invocation layout with byte-identical pinned sibling inputs. The original command failed imports/data lookup; no mathematical source was changed. Parameter-only contribution, not a new finite network. |
| [#141](https://github.com/CrocSwap/integer-mult-bounds/pull/141) — chafreaky (@chafreaky) | Shrunk-birth terminal elision with exact adjoint and redirects. | Exact-head physical CI evidence and source-linked saved 240-theorem arithmetic evidence. No fresh Lean kernel rebuild or analytic formalization claimed. |
| [#142](https://github.com/CrocSwap/integer-mult-bounds/pull/142) — eumemic (@eumemic) | Restrict to 22 and replay new supports and coefficients. | Exact-head CI evidence; old geometry is not assumed unchanged. |
| [#143](https://github.com/CrocSwap/integer-mult-bounds/pull/143) — eumemic (@eumemic) | Late compensation before birth and target deadlines. | Exact-head CI evidence; donor finish, disjointness and complete chronology are checked. |
| [#145](https://github.com/CrocSwap/integer-mult-bounds/pull/145) — Thomas Marchand (@Th0rgal) | Valid unpaired supplier plus a retracted paired-lockstep attempt. | Only unpaired kappa=0.000337546392004 retained as a conditional historical witness. Paired kappa=0.00036855 was retracted; preserve the counterexample and warning, never promote it. |
| [#146](https://github.com/CrocSwap/integer-mult-bounds/pull/146) — Thomas Marchand (@Th0rgal) | Exact min-cut producer over a fixed candidate subset. | Fresh producer replay plus later #147/#150/#151 integration provenance. Exactness applies to the specified 2^11565 subset, not every producer or topology. |
| [#154](https://github.com/CrocSwap/integer-mult-bounds/pull/154) — eumemic (@eumemic) | Isolated parallel verification runner and frame-equivalence work. | Adapted runner integrated actively, with positive-job validation and correct tracked/ignored-file snapshots; six new adversarial tests. Historical optimizer retained separately with existing 12,000-case equivalence evidence; no blanket runtime benchmark claimed. |
| [#162](https://github.com/CrocSwap/integer-mult-bounds/pull/162) — DaysSky (@DaysSky) | Expanded legal carrier relation with full backward containment. | Fresh full replay; acyclic relation and all 48 arcs paid. |
| [#178](https://github.com/CrocSwap/integer-mult-bounds/pull/178) — rohanarun (@rohanarun) | Retiming operation frames with fixed endpoints and schedule. | Fresh full replay with CRT and dirty-state checks; no free endpoint change. |
| [#182](https://github.com/CrocSwap/integer-mult-bounds/pull/182) — chafreaky (@chafreaky) | Shared edges and terminal-data accounting in the actual word. | Fresh full replay; independent construction evidence retained. |
| [#185](https://github.com/CrocSwap/integer-mult-bounds/pull/185) — rohanarun (@rohanarun) | Finite three-level ordinary-leaf bootstrap. | Fresh verifier; exactly three levels, not a new infinite fixed-point theorem. |
| [#187](https://github.com/CrocSwap/integer-mult-bounds/pull/187) — rohanarun (@rohanarun) | Source-assisted injection before original sources mix. | Fresh --full replay; conservative Gram ancestry, donor complements and full global word paid. |
| [#188](https://github.com/CrocSwap/integer-mult-bounds/pull/188) — huxint (@huxint) | Terminal accumulator executed on every required column. | Exact-head Linux full-word/CRT/assembly CI passed. Local macOS stopped at RLIMIT_AS setup; record that portability failure, not a mathematical failure or fresh Linux replay. |
| [#189](https://github.com/CrocSwap/integer-mult-bounds/pull/189) — chafreaky (@chafreaky) | Facetwin bit locals combined with shared-edge complex supplier. | Fresh full replay of both suppliers and composition; complete conditional interfaces retained. |

## Open next questions

- #122: supply the full parent `round15/refined-replayed/word.json.gz` with SHA-256
  `be7e7c6c4530bf84190c3ceedfbf782547176e221aa660f1256e306dd3f86a76`, and parent profile
  `e671b71d1f64dfeaaa756f3c1c63365d3df908abce7ad65f0868b909767d902f`, or an exact pinned
  regeneration procedure. Then run the full terminal-word and majorization checks. Its existing
  focused CI checks inherited cube/cyclic packages, not the terminal-elision delta.
- Later improvements should start from the selected result and current autoresearch task catalogue,
  not the obsolete numerical headlines in these preserved snapshots.
