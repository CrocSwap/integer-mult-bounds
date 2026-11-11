# Conditional κ = 0.003642959019031 from a causal-history buffer split

This source-bound candidate improves the complete signed P104 invoice over
[#7131](https://github.com/CrocSwap/integer-mult-bounds/pull/7131) by
**0.000000550522162**, from κ=.003642408496869 to **κ=.003642959019031**.
All three direct CPython 3.14.7 checks passed. Final registered isolated Python
3.12.16 replay passed all three commands and matched every frozen receipt field. No admission or selected-frontier change is claimed.

Seven values collected at different times in frame 237 isolate one helper
input after a boundary basis change. Two explicitly initialized owned buffers
permit that helper to retire at the intermediate frame while a fresh arbitrary
public input continues its old program. One later injection restores the full
output direction. One paid transport changes from rank six to ranks one and
five, funding a productive helper split from rank nine to ranks four and five.
This is an instance of **Ali Romman's causal-history owned-buffer mechanism**;
[PROOF.md](PROOF.md) states the exact source, chronology and identity.

| Count | Source | Candidate |
|---|---:|---:|
|Native public fields|1492|1493|
|Native independent helpers|1092|1093|
|Owned labels|51|53|
|Owned lifetimes|54|56|
|Peak simultaneous owned fields|43|44|
|Native instructions|74591|74627|
|Complete paid positions|110400|110417|
|Complete productive fields|22308|22325|
|Rank surplus|1424|1424|
|Empty credit|0|0|

The exact per-native changes are ΔP={1:+1,5:+1,6:−1} and
ΔT={4:+1,5:+1,9:−1}. Every added scalar, owned lifetime and compiler service is
charged in the application checks. The candidate has 27 more ADDs, four SCALEs,
one MOVE, two INITs and two CLEARs. The fresh minimal grid remains **1125/F25**.
The two directed price engines locate the emitted invoice's crossing in

```
(0.0036429590190313419414962272850934,
 0.0036429590190313419414962272850935).
```

This is an invoice-specific ceiling, not an optimum over temporal programs.
The retained BIT cap .00376669 leaves .000123730980969 headroom above the claim.
The original one-path search stopped at its first positive after 150 of 7,687
individually affordable paths; it does not exclude the unvisited domain.

## Exact inputs and reproduction

`INPUTS.json` authenticates the complete 37-file independent composition artifact
at `666fd749ec465de7238633a0c2fd5ee3081477e0`, with every nested source and notice.
The construction is the same canonical native as Rohan Arun's completed #7131
at `67a6544cf18b2d372fd1d0deee1863e9f6ca9fc5`. This package uses the fully retained
666fd artifact as its byte-exact predecessor; it does not claim to replay the
entire separate #7131 package.

Source native SHA256:
`9557c4682056ab7cc7cda89aa73865bef0e3948cc10b3c3061b0a944af05b96a`.
Candidate native SHA256:
`81f9b2e0a170aa3ab0cd4bb1056c834ebe0b98eaf37abe5986c6e53abd1257ea`.
The signed 17-stage caller from Rohan Arun's #7113 remains byte-identical,
SHA256 `255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc`.

```sh
git fetch --no-tags https://github.com/CrocSwap/integer-mult-bounds.git main
python3.12 -B scripts/research_package.py --package research/p104-causal-buffer-split
```

The hook checks the exact timed coefficient certificate, complete native and
complete caller application. It reconstructs the source, all observation times
and paths, arbitrary-input forward/adjoint, lifecycle census, grids/envelopes,
phase, physical ownership, all 3,039 paid/helper maps and 104 main boundaries,
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

## Open next questions

- Independently replay the exact causal certificate and complete application,
  especially the additional owned lifetimes and precision/cost adapters.
- After refreshing upstream and overlap, test a distinct source-bound temporal
  domain on the successor. This first-positive search establishes no ceiling.

[Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19520521).
