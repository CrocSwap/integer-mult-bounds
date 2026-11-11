# Conditional κ = 0.003643180671645 from a temporal split at chart 120

This source-bound candidate improves the complete signed P104 invoice over
[#7140](https://github.com/CrocSwap/integer-mult-bounds/pull/7140) by
**0.000000221652614**, from κ=.003642959019031 to **κ=.003643180671645**.
All three direct CPython 3.14.7 checks passed. Final registered isolated Python
3.12.16 replay passed all three commands and matched every frozen receipt field. No admission or selected-frontier change is claimed.

Two values collected at different times in frame 120 isolate helper input
1449. Two explicitly initialized owned buffers let pivot 648 retire there while
a fresh arbitrary public input continues its old program. Six later injections
restore the complete output direction. One paid path changes from rank seven
to ranks four and three, funding a productive split from rank nine to five and
four. This is another instance of **Ali Romman's causal-history owned-buffer
mechanism**; [PROOF.md](PROOF.md) states its exact chronology and identity.
ToikY's earlier chart-120 lead is credited through the predecessor chain.

| Count | Source | Candidate |
|---|---:|---:|
|Native public fields|1493|1494|
|Native independent helpers|1093|1094|
|Owned labels|53|55|
|Owned lifetimes|56|58|
|Peak simultaneous owned fields|44|44|
|Native instructions|74627|74655|
|Complete paid positions|110417|110434|
|Complete productive fields|22325|22342|
|Rank surplus|1424|1424|
|Empty credit|0|0|

The exact per-native changes are ΔP={3:+1,4:+1,7:−1} and
ΔT={4:+1,5:+1,9:−1}. Every added scalar, owned lifetime and compiler service is
charged in the application checks. The candidate has 21 more ADDs, two SCALEs,
one MOVE, two INITs and two CLEARs. The fresh minimal grid remains **1125/F25**.
The two directed price engines bracket the emitted invoice's crossing in

```
(0.0036431806716457592014331762194701,
 0.0036431806716457592014331762194702).
```

This is an invoice-specific ceiling, not an optimum over temporal programs.
The retained BIT cap .00376669 leaves .000123509328355 headroom above the claim.
The original one-path search stopped at its first positive after 715 of 7,667
individually affordable paths; it does not exclude the unvisited domain.

## Exact inputs and reproduction

`INPUTS.json` authenticates the complete 30-file #7140 package at
`a95783a8c861248a759136d4285ea725499cf231`, including every nested source and
notice. `REUSE.json` binds six byte-identical implementation files to that
source. All three registered commands check this reuse before computation.

Source native SHA256:
`81f9b2e0a170aa3ab0cd4bb1056c834ebe0b98eaf37abe5986c6e53abd1257ea`.
Candidate native SHA256:
`c38b79279f665d46d795501de6645a8a16d9324c22199fa615313b6abfdc3e2f`.
The signed 17-stage caller from Rohan Arun's #7113 remains byte-identical,
SHA256 `255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc`.

```sh
git fetch --no-tags https://github.com/CrocSwap/integer-mult-bounds.git main
python3.12 -B scripts/research_package.py --package research/p104-temporal-chart120-split
```

The hook checks the exact timed coefficient certificate, complete native and
complete caller application. It reconstructs the source, all observation times
and paths, arbitrary-input forward/adjoint, lifecycle census, grids/envelopes,
phase, physical ownership, all 3,038 paid/helper maps and 104 main boundaries,
ordinary and finite-tape work, both price engines and 54 strict plus four
functional outer conditions. Every frozen receipt field must match.
[VALIDATION.md](VALIDATION.md) records the actual completed commands and limits;
[APPLICATION.md](APPLICATION.md) records full-cost substitutions.

## Scope and credit

The five inherited assumptions remain `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape`, `analytic_recovery`. Independent human/formal
review, maintainer admission and compiled top-level execution remain open.
Finite verification is distinct from each of those obligations.

Credit **Ali Romman** for causal-history buffers and helper bases;
**Jerry Chen/CubeJerry** for contact-free retiming, temporal coefficient and
native/caller/precision/compiler methods; **Matarener** for complete kernels;
**Rohan Arun** for input/output recharting and the shortened signed caller;
**Cinna Davis/1337isnot1337**, **Dugongue**, **ToikY**, **DreamingOfClouds**,
**Douglas Colkitt/#7000 reviewers** and every retained nested source author.
The dillona #7130 split and independent 666fd composition artifact are fully
retained. Prepared for dillona with substantial OpenAI Codex assistance;
no subagents. Apache-2.0.


## Concurrent work

The 00:21 UTC overlap refresh found Rohan Arun's draft
[#7142](https://github.com/CrocSwap/integer-mult-bounds/pull/7142), exact head
`d446d891ab4c25b3a7df002ae3a9d140b492bfab`, with provisional κ=.003643216822476
on the same #7140 source. Its endpoint-funded change is distinct, with native
ΔT={2:+1,7:+1,8:−1}, ΔP={1:+1}; its full verification was still pending.
This package improves #7140 and supplies a separate temporal instance. It does
not claim to beat #7142, validate that draft, or establish composability.
A future composition must reconstruct and reprice the complete combined word.

## Open next questions

- Independently replay the exact causal certificate and complete application,
  especially the additional owned lifetimes and precision/cost adapters.
- After refreshing upstream and overlap, test a distinct source-bound temporal
  domain on the successor. This first-positive search establishes no ceiling.

[Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19520521).
