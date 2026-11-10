# Independent physical-contact and complete-invoice audit of #6726

**Result: PASS for the finite scope below. No new κ, scientific admission, or change to the selected frontier is claimed.** This package independently reconstructs the physical contacts and complete paid/productive invoice of [#6726](https://github.com/CrocSwap/integer-mult-bounds/pull/6726) at exact head `435bbe91fb28cb1d7a569ca70c6c4e9eb302d486`. The selected construction at the canonical base remains [#6030](https://github.com/CrocSwap/integer-mult-bounds/pull/6030), conditional κ = 0.003125804.

The standalone verifier imports only the Python standard library. It does not import the author's constructor, caller algebra, native replay, physical engine, or pricing routines. Source data and the comparison receipt are frozen with byte counts, SHA256 digests and Git blob identities. The author receipt is used only after the new implementation has reconstructed its results.

## What is independently checked

| Obligation | Checked result |
| --- | --- |
| Literal changed caller | 606 gates, 18 distinct chronological LOCAL stages, 15 QUERY gates, 12 IDLE and 6 IDLE_ONE gates, 100 ordinary λ gates |
| Physical route and phase | All 104 retained ports at all 18 stages; 7,488 forward/inverse contacts; exact absolute phases and fresh-body cross coefficient |
| Complete contact payload | Independent digest `79930ec6c09a8e4930556c925c354bb5431203eaf069d9373f056049c061289b`, equal to the frozen author receipt |
| Native chronological application | All 18,577 events, 771 arbitrary public-input endpoint rows, common-chart scalar gates, strict nested paid transitions, COPY into cleared owned storage |
| Native request inventory | 3,454 paid requests and 563 independently productive helper endpoints per LOCAL |
| Native owned state | 29 distinct reserved labels, 47 chronological lifetimes, peak 14 live fields, all cleared on return |
| Global independent allocation | 3,536 main fields and 18 × 563 = 10,134 distinct new native helper fields; 29 reserved native owned slots and one separate query scratch slot |
| Whole paid idles | 3,120 owner/port jobs, with every selected fresh axis charged exactly once in that job |
| Complete invoice | 13,670 productive fields, 66,852 paid requests, productive rank mass 178,840, paid rank mass 178,080, surplus 760 |
| Ordinary work | Independent conservative native bound 5,675,608 per call < 10⁷; complete retained envelope 535,415,008 < 10⁹, including all λ gates, helper normalizers, native adapters, and explicit input/output adapters for every scattered main, idle and query job |
| Chronology and retention | Actual final-word handoffs after gates **169 and 401**; fresh fields 32 and 33 untouched beforehand; retired fields 6 and 4 untouched afterward |

Both boundaries of every whole Gaussian job are explicitly charged. Full-carrier main and idle permutations are decomposed into individual two-axis exchanges; q normalization uses nine-axis maps. The retained 1,000-unit rate is applied separately to each elementary map, never to an arbitrary 153-axis map as a whole.

The first witness's `handoff_after: 166` describes the intermediate 33-field caller. The second retirement prepends its three-gate input basis, so this handoff occurs at 169 in the final 606-gate caller. The source construction is consistent; this distinction matters to a final-word audit.

The complete rank histograms, ordinary bounds, phase/ownership coverage and ten mutation results are in [RESULT.json](RESULT.json). [PROOF.md](PROOF.md) explains why the finite phase checks establish exact operator equalities on the 153-axis carrier, and identifies every retained implication.

## Relation to previous independent work

[#6733](https://github.com/CrocSwap/integer-mult-bounds/pull/6733), head `403b4ed85eea7f99b0c4b4afad22123363492c7a`, independently checked all 34-input scalar endpoints and the two retirement cuts, including the second absolute phase. Its stated exclusions include the physical/native action, complete invoice, stock and compiler. This package addresses the physical application, chronological native scalar/ownership ledger, distinct field allocation, ordinary cost bound and complete finite invoice. It does not repeat a full symbolic scalar-caller audit or imply that #6733's endpoint theorem alone supplies physical admission.

[#6716](https://github.com/CrocSwap/integer-mult-bounds/pull/6716) and [#6702](https://github.com/CrocSwap/integer-mult-bounds/pull/6702) retain the native supplier and preceding callers. Their unchanged native physical adapters remain explicit dependencies; a passing old-caller audit is not treated as a proof of the new caller's application.

## Reproduce

Python 3.11 or later, standard library only, from this directory:

```sh
python3 -I -B verify.py
```

The normal command authenticates all frozen scientific inputs, performs the independent checks and negative controls, and requires byte equality with the saved receipt. `--write` explicitly regenerates the local receipt and is not the normal verification command. No source archive or shared selected file is changed.

The checks use explicit exceptions, so optimized Python does not disable them:

```sh
python3 -I -O -B verify.py
```

The registered hook targets Python 3.12 and needs no third-party package. Validation records the actual local Python version and timings separately.

## Exact scope and retained assumptions

The parity-phase argument checks all Fourier frequencies of the finite 153-axis carrier by a degree-two identity, rather than sampling a few addresses. It does **not** establish the retained implementation at every positive column multiplicity. Tensor extension of the native primitive, helper whole-job adapters and source chart normalization still use the retained native contract. Ordinary λ polynomials act on the total central operator; their scalar coefficients are not moved inside tensor powers.

The independently replayed 771 public rows are the native supplier's scalar chart action, conditional on those physical primitives. Generic native paid maps and helper normalizers are not freshly regenerated as dense 512-column physical matrices. The changed caller's complete symbolic endpoint identity is a retained, exact-source dependency already addressed by #6733. The present audit verifies its physical interpretation and billed targets.

This package supplies an explicit finite disjoint field allocation and recounts every use of the retained ordinary route rates. It does not prove an all-size stopped-producer stock bound, exact tape implementation, rounded multiplier, analytic recovery, compiler strictification or outer-transfer inequalities. All five assumptions remain: `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, and `analytic_recovery`.

## Open next questions

1. Independently review the exact-source compiler and outer qualification for this invoice. First consume the full histograms in RESULT.json and inspect #6726's strictification and 54+4 outer inequalities. This is separate from the physical/contact audit and is needed for complete candidate application admission.
2. Close the retained native primitive/all-column implication for the actual source word. First audit a precise claimed tensor/whole-job adapter theorem against the pinned native frames and operator normalization; the finite carrier result alone does not discharge it.
3. Review the complete stopped-producer stock and physical precision/tape implementation at the candidate's actual compiler parameters. The finite disjoint allocation here supplies a concrete field census, while the uniform recurrence and machine realization remain additional obligations.

## Attribution and license

Independent audit by **Jerry Chen (@CubeJerry)** with substantial **OpenAI assistance**, Apache-2.0. The positive two-fragment construction is credited to **zxv** with OpenAI Codex assistance. Retain **thu-nmrc**, **Ali Romman**, **Cinna Davis**, **DreamingOfClouds**, **Jacob Alan Sussman**, **Cao Yifan**, and all source-specific predecessor credit. The frozen predecessor notice is preserved verbatim in `frozen/PREDECESSOR-NOTICE`; it records the detailed native, binary supplier, caller, retirement, pricing and compiler lineage, including #6545, #6348 and #6398.
