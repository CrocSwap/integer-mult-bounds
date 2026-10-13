# Executed validation and scope

Executed on 2026-10-13 with Windows / CPython 3.14, at exact base
`2921874911956718fcaaaf9396fe8267b3cfa9f0`.

| Check | Result |
| --- | --- |
| `python research/r439-target-retune-seed14/search.py` | Complete deterministic census and decoded candidate match retained artifacts |
| `python research/r439-target-retune-seed14/verify.py --write-receipt` | PASS independent source reconstruction, census, full bills, both dirty-state directions, owning checker/exporter and 14 negative controls; initial receipt recording |
| `python -I -O -B research/r439-target-retune-seed14/verify.py` | PASS complete receipt comparison under isolated optimized execution |
| `python -B scripts/verify_selected_result.py` | PASS unchanged selected record and exact kappa `1661960547713947/1000000000000000000` |
| `make verify` | Unavailable: Windows reports `make` is not recognized |
| `git diff --cached --check` | PASS for the thirteen new package files |

The 14 negative controls reject omission of preparation or restoration,
omission of the middle row transformation, transposed target direction,
using the donor before helper mixing, unpaid basis gates, each of the
two genuine nine-stage overruns, strict guard equality, removal or
corruption of a source pin, floating-point seed identity, duplicate JSON
keys and nonfinite JSON. A cancelling target pair is a positive control:
it preserves arbitrary dirt but costs two ADDs.

The independent verifier imports no search or predecessor compensation
implementation. It uses set supports to reconstruct the fixed matrices
and literal elementary ADD/COPY/ERASE instructions to compute both positive
bounds. The builder uses packed supports and grouped additions. Both
depend on the same pinned source data. The retained owning geometry
checker and exporter provide additional existing-code checks; they are
not presented as independently written components of this contribution.

The exported non-ADD record sequences are exactly equal, with 2,911 MOVEs,
nine COPYs and nine ERASEs. The candidate emits 11,780 ADDs in 14,709 total
records and has unchanged paid rank mass 5,129. All 661 symbolic inputs
(including targets and helper dirt) are checked for both complete-word
directions and both D directions. No clean-register premise is used.

The source checker continues to report false exactly for original H2 and
literal `K_equals_D`; the semantic boundary is verified separately. The
strict 104-bit local and 192-bit nine-stage prefix inequalities pass with
unchanged F/B, and the exact stage formula/charge are source-bound.
No native multistage check, changed whole-hosted supplier, full invoice,
outer assembly, hosted CI or all-size theorem is claimed. The selected
pointer and all predecessor files remain unchanged. The finite minimum
only covers the one-insertion class stated in PROOF.md.
