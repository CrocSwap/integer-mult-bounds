# Premise narrowing for #7620 (what is now a kernel fact, what is still assumed)

Context: our #7623/#7630 κ is conditional on the premises of PR #7620 (SYLforge; the premise list builds on #7616). Nothing here is a κ claim, and no premise is discharged in full.
"Fact" means: kernel-checked in this package, for the stated model and extracted data (axioms within propext, Classical.choice, Quot.sound; see CHECK.txt).
Data are extracted by scripts that are not shipped; "extraction fidelity" is by reading in every case below. Each file's `.md` in `lean/Nov15/` has the model and hypotheses.

## 1. owned_erasure (files ClearCert, OwnedSkeleton, OwnedTree)
Clauses: E1 explicit INIT, erased, no overlapping reuse; E2 one bank per live unit (allocation); E3 field identity / chronology, flat and parent-child; E4 copy/read/erase linear in volume; E5 paid non-reversible erase is permitted; E6 dirty residuals counted via earlier ADD reads.

| item | status |
|---|---|
| Content half: every CLEAR erases a lossless row | FACT (`ClearCert.every_clear_lossless`: endpoint-exact, birth-free word with rows in U; no legality needed). The certificate checker is sound and complete for it (`checker_sound`, `checker_complete`). Two endpoint-exact words with the same owned events satisfy the erasure predicate together or not at all (`clearform`). |
| E1 on the real owned skeleton of #7630 (180 INIT, 180 CLEAR, 47 owned MOVE) | FACT (`OwnedSkeleton.sk_skel`, by `decide +kernel` on extracted data) |
| E2: 68 labels, peak live 50 ≤ 68, 17 calls x 68 = 1,156 banks, 180 lifetimes reuse the 68 labels | FACT (`peak_skel`, `bank_count`, `lifetimes_exceed_labels`) |
| E3 flat half (MOVE starts at current chart, properly nested; CLEAR at current chart) | FACT (`OwnedSkeleton`) |
| E3 tree half (a clear never acts on a descendant's live storage), every recursion depth and every call-site list | FACT under ATOMIC CALLS and unit-tagged banks (`OwnedTree.e3_tree`, `e3_tree_real` at the 6,250 real MOVE sites). It is implied by E1's "nothing live at the end" for the child (`execU_id`); it is not independent evidence. |
| Caller layer owns no storage; 17 sequential native calls | FACT on the extracted #7113 caller alphabet (`OwnedTreeCheck.caller_alphabet`, `caller_tree`) |
| E4, E5, E6 | ASSUMED. Cost/permission statements; not expressible in the row model. |
| Compiler admission of the retained allocation | ASSUMED |
| Atomic scheduling of child units; "child = same word" self-similarity | ASSUMED (execution-model facts from the contract text, not properties of the word). If "tree" meant a chart hierarchy instead of paid rounds, the flat word would violate the clause 251 times: a reviewer who reads it that way has a real objection. |
| Extraction fidelity (skeleton, call sites, certificates); replay of the 208,738-event word and of the 180 certificates | ASSUMED / not in the kernel |

## 2. Owned ascent (file OwnedAscent)
Reduced to ADMISSION.

| item | status |
|---|---|
| Rank cost of a chart change is direction-free (`rc_inv`, `back_cost`); price of a→b equals price of b→a if the compiled rank is |Δdim| (hypothesis) | FACT (in the abstract model) |
| Owned moves are charged like public ones; owned share never negative; an owned ascent costs ≥ 1 | FACT (`cost_split`, `ownedCost_nonneg`, `owned_ascent_charged`) |
| Owned registers earn no credit; ascent only adds to the invoice | FACT (`owned_no_credit`, `invoice_eq`) |
| Relaxed legality differs from strict only on owned ascents; every FloorEndToEnd floor proved on the relaxed class holds for strict words | FACT (`legal_diff`, `public_unchanged`, `AcceptedS.toAccepted`, `hOnce_strict`) |
| Floors that rest on "owned registers only descend" do NOT transfer to the relaxed class | FACT, as a scope statement with a witness (`strict_no_owned_asc`, `W1_*`) |
| Contract admits owned ascent on arbitrary content, factorwise at every width | ASSUMED. The contract text never mentions direction; an earlier P112 precedent supports, does not prove. |
| Compiled rank = |Δdim| for each chart pair | ASSUMED (Clifford compilation not formalised) |
| CLEAR at any frame | rests on premise 1 |

## 3. native_all_columns (files NativeColumns, CensusComplete, CensusData)
| item | status |
|---|---|
| For an exact-rows word, the word computes the matrix on every column, every tensor power (any K-module) | FACT (`all_columns_of_exact_rows`) |
| Exact final rows ⇔ correct on every unit column | FACT (`exact_rows_iff_columns`) |
| Subset tests are only evidence (`partial_columns_insufficient`); adjoint columns add nothing once forward is exact (`adjoint_iff_forward`); absolute phase needs its own test (`phase_visible`) | FACT |
| The #7630 checker's column test is exhaustive (512 of 512 forward and 512 adjoint exact columns per affected pair), not sampled | tool fact (code read; not re-run) |
| used(#7630) ⊆ used(#7623) ∪ census | FACT (`used_subset_base_or_census`, kernel, extracted data: census 981, #7623 census 964, used 3,024 and 3,021) |
| The census covers every pair #7630 uses | FALSE as stated: `used_not_subset_census` (2,143 of 3,024 used pairs are outside it). The census is a DELTA census. |
| Correct on the census and on #7623's used pairs ⇒ correct on all #7630 used pairs | FACT (`all_used_correct`, for any predicate) |
| Per-pair column checks pass on the 981 census pairs | ASSUMED (checker output) |
| Correctness of #7623's 3,021 used pairs (only 866 lie in the 964-pair census) | ASSUMED: inherited from #7623/#7620. This, not a code fact about #7630, is the real residue of "census completeness". |
| Operator realization (Pauli frame, complex phase, Fourier recipe on 512-dim states); compiler and precision halves; the checker itself | ASSUMED |

## Other premises
`compiler`, `precision_tape`, `analytic_recovery`: untouched.
