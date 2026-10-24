# First-pivot Schur state weights from sector incidence

**Scoped binary counting proof; no new kappa.** Prepared by JoyboyBrian with substantial OpenAI Codex (gpt-6-astra) assistance. Apache-2.0.

For the commuting-idempotent sector profile (1,1,1,2), [PROOF.md](PROOF.md) derives the seven first-pivot split multiplicities **(1,3,126,18,3,3,18)** from vector/covector incidence. It fills the input-count gap explicitly left by Sagar Thakrar's complementary-plane continuation rule. Neither all 496 splits nor GL4 is enumerated. The existing seven-state census, downstream transitions and centralizers remain credited predecessor results.

The binary scalar-pivot formula applies to arbitrary nonnegative sector dimensions: partition each sector's vector/covector pair into Z/A/B/N/C incidence types, multiply their exact sizes, and add compatible tuples reaching the same residual class. General residual classification is not solved. For this fixed profile, h=0 yields four classes with weights 1,3,3,3; h=1 gives 27 incidence tuples of weight six, grouped as 21,3,3. The proof supplies sufficient image/kernel and rank-one normal forms, rather than assuming that rank fingerprints classify arbitrary projector pairs.

| Published state | Split weight | Header multiplicity per coordinate pair | Credited full-guard contribution |
|---:|---:|---:|---:|
| 1 | 1 | 36 | 3600 |
| 2 | 3 | 12 | 5616 |
| 3 | 126 | 126 | 46116 |
| 4 | 18 | 18 | 14688 |
| 5 | 3 | 12 | 5616 |
| 6 | 3 | 12 | 3240 |
| 7 | 18 | 18 | 14688 |

Each split has 20160 full-header completions. The middle column additionally uses the credited centralizers; the final column composes the new input weights with the credited continuation table and sums to 93564. The numerical continuation counts are a retained premise, not an independently rerun result. No physical header selection, odd-field normalizer, supplier admission or selected-frontier change follows.

## Verification and source boundaries

```sh
python3.12 -B scripts/research_package.py --package research/schur-split-incidence
python3.12 -B scripts/check_research_commit.py --package research/schur-split-incidence --check-source-history
```

Standalone Git-free replay is `python3.12 -I -B verify.py` or `python3.12 -I -O -B verify.py` from this package. Only the Python standard library is used. All checks use explicit failures under optimization. The verifier checks 31 canonical sector tuples against direct Schur maps and actual invertible intertwiners to the seven supplied representatives. Intertwiners are found in the linear solution space of SK=KS0 and TK=KT0, rather than by enumerating GL4. Thirty sector profiles in dimensions two and three compare weighted incidence with direct small split counts, including empty sectors. Five controls reject omitted completion fibres, orbit sizes substituted for incidence, unweighted sector types, omission of the six C realizations, and confusing all splits with admitted splits. RESULT.json fixes the output.

Tests protect the sector-incidence partition and state mapping. The credible regressions are a missing multiplicity, reversed ordered state, or invalid zero-sector handling. Earlier census/continuation packages do not test this new derivation. The checks call the verifier's mathematical boundary directly; no production exports or flags are introduced.

[RETAINED.json](RETAINED.json) authenticates the exact original README bytes from thakrarsagar/integer-mult-bounds commit `93bebe5e1ad3dd17a97ae79f27e1a35edd3630aa`, path `research/cbc3b1759ddd5fe5c461c509fecfae56/README.md`, and identifies its Apache-2.0 license and author. The retained calibration JSON is explicitly a small transcription, not an original file. It is compared only after deriving the input weights; it is never a filter defining the incidence classes. Base-main predecessor README/RESULT bytes are provenance-pinned in SOURCES.json. The remote successor is carried as actual package bytes, so standalone replay does not need a shared Git object or network. Its continuation proof/table is credited rather than reimplemented.

Local checks completed on macOS with Python 3.12; both registered modes pass in under one second each. No heavy historical suite, GL4 census, Lean, Docker, production build or selected cold replay was run. Independent human/proof-kernel acceptance and general residual classification remain open.

## Scope and attribution

Canonical base `4c0a359d88f22f05189d51f48387750b801a45d4`, priority revision 7. This changes the formal-interface card to the precise algebraic handoff already claimed at [Discussion4653](https://github.com/CrocSwap/integer-mult-bounds/discussions/4653#discussioncomment-19140794). The root coordinator checked the active overlap/claims; coverage and exclusions are retained in TASK.json. The family decision is narrow: finish this missing input law without another profile census or construction round.

Credit: Mihir Srivastava #4689 (`3a72fbad148294aa9ca7f900a48dbb10e64232be`) supplies the seven-state table and calibration; ssafwann #4678 (`af9cf805c501e4e9e947c98c0b97b2281b6b6e97`) and #4671 supply sector equations, factor counts and completion arguments; Sagar Thakrar supplies the complementary-plane successor and explicit first-pivot handoff; Nick Petalas #4915/#4597 and earlier scalar/header papers supply centralizer and Schur lineage. MatShep #4762, codyw912 #4735, Ryanson Jonathan, lee-phys, Cinna Davis and the normalizer lineage retain their predecessor credit. The retained successor preserves its own full credit and AI-assistance disclosure. The new claim is the input-incidence derivation, not the published seven-state count, downstream law, or centralizer calculation.

## Open next questions

Can the scalar sector-incidence formula be paired with a sufficient residual invariant for larger sector profiles? Start with a symbolic image/kernel decomposition for one changed profile; stop if its state classifier is unspecified rather than running another census. Higher-rank pivots require relative factorization data beyond the five scalar incidence types. Production use separately requires an actual header cover and complete selection, restoration, storage, stock and dispatch costs. These obligations are unknown, not zero.
