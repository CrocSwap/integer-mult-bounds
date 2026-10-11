# R715 bit supplier with PR #458's paid complex kernel: κ = 641739651875561/(5·10¹⁷) ≈ 1.283479·10⁻³

Conditional **κ = 641739651875561/(5·10¹⁷) ≈ 1.283479303751122·10⁻³**, bit-bound, **+0.711% over PR #460**
(1.274415506145115·10⁻³) and +0.741% over PR #458. Whole-residual hosting on both sides: no cross-family residual split
and no cross-copy hosting lemma (see PR #451's obstruction). No new complex lemma: the complex supplier is PR #458's, unchanged.

| side | supplier | endpoint |
| --- | --- | ---: |
| bit (binds) | R715 word, eleven stages, PR #442 whole-residual hosting, target mixing (`research/e8-r715-eleven-stage-whole`) | c = 642564369945714399381/(5·10²³) ≈ 1.285129·10⁻³ |
| complex | PR #458 paid residual adapters (`research/e8-complex-adapted-kernel`, unchanged) | b = 1297203880559577927527/10²⁴ ≈ 1.297204·10⁻³ |

## Reproduce
```sh
python -m pip install -r research/e8-r740-replica32/parent436/requirements.txt
python -B research/e8-r715-paid-complex/verify.py /absolute/new/output
```
Runs PR #458's full wrapper and the R715 package's full wrapper from scratch, then `compose.py`: both exact rational moments
(two engines) for both suppliers, six bootstrap levels, all 47 strict outer inequalities, next-grid and parameter controls.
`python -B research/e8-r715-paid-complex/compose.py /abs/screen.json` is a screen against PR #458's pinned report.

## The bit word (research/e8-r715-eleven-stage-whole)
- **Carrier lower bound, met.** The 63 lines of E7 form a spherical 4-design, so no two hyperplanes contain them; hence every
  source needs ≥ 3 registers (≥ 2 carriers, 240 in all) and every target ≥ 2 helpers reaching its hyperplane. PR #370's word
  spends 272 carriers; frame-pair D4 sums reach 240 (R 740 → 724 after PR #443's reuse).
- **Eleven cancelling re-expressions** inside frames: R 724 → 715.
- **Kernel rebuild** (PR #443's replica kernel, deterministic search) and **target mixing generalised to chained receivers**.
- Checks: hierarchy legality, regeneration, PR #370's independent all-column checker and mutants, the relaxed checker on the
  kernel and mixed words, C++ cohort legality and formal columns (five and eleven stages), mixing mutants, Gram, eleven-stage
  template/hosting audits and assembly.

## Composition
`compose.py` follows PR #460's `assemble.py`, with the R715 side's own contracts: halving depth 3, two-level coefficient
charged 576 bits (used in the bootstrap cutoffs), row coefficient 28,416 (> PR #458's 20,161, so the row allowance is 28,416).
Both suppliers' published expected fields are rechecked against the fresh outputs.

## Review points
PR #450's Lemma M (bit target mixing, here with chained receivers); the R715 hierarchy (frame-pair sums and cancelling
re-expressions, independently validated); PR #458's paid adapters (inherited). Conditional like all parents; no
unconditional theorem or Lean proof is claimed.
