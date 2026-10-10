# five-stage-gen5b-banks

**Conditional κ = 373354860481239 / (5·10¹⁷) = 7.46709720962478·10⁻⁴** (+0.348% over PR #287's 7.44120696397042·10⁻⁴;
+0.525% over PR #285's gen5 word). Bit coarse 7.47268·10⁻⁴, complex coarse 7.54736·10⁻⁴: the bit side binds.

A third structural change to the paired-cube bit word (gen5b). PR #285's generator is run byte for byte with PR #285's
compile-cost-annealed pair module and two new pieces of module data:

* **an alternative per-cube local design** (28 additions, 12 carrier arcs, debt 16): an exact CP-SAT model over all
  15¹² recipe-tree choices of the generator's own arc rule (`discovery/cpsat_local.py`, `local_model.py`, which
  reproduces the compiler's 29/13/16 on all 220 cubes) proves debt 16 optimal in this class, so #276/#285's design is
  optimal too; the alternative optimum admits 1,726 compensated reuse pairs instead of 1,406;
* **a debt-10 all-but-one module** (35 additions, 25 arcs) found by a symmetric CP-SAT model at the trivial lower bound
  (outputs can never be donors, so 10 is a floor; `discovery/cpsat_abo_sym.py`, frame-exact on all 132 instances by
  `module_model.py`), against #285's annealed debt 11.

PR #285 notes that a debt-10 module of cyclic-interval form costs the word 4.5% by cutting roles into small rank steps;
this one does not: with #285's pair module the word's descent cost falls 910,000.8 → 907,245.3 (−0.30%), and with the
alternative local design to 905,892.5 (−0.45%).

| one invocation, m = 120 | gen5 (#285) | gen5b (this package) |
| --- | ---: | ---: |
| virtual auxiliary roles | 17,292 | **17,160** |
| compensated reuse pairs | 1,406 | 1,726 |
| independent dirty registers R | 15,886 | **15,434** |
| independent entrances (ranks) | 2,554 (17, 18, 20, 21) | 2,234 (20 × 2,182, 21 × 34, 18 × 16, 17 × 2) |
| literal stock (60 replicas) | 1,247,070 | **1,236,750** |
| κ (with #287's descent and target squares) | 7.44120696397042·10⁻⁴ (#287) | **7.46709720962478·10⁻⁴** |

On top of the word, the package carries PR #287's two stages re-derived on gen5b (`discovery/descent_search.py` and
`target_search.py` implement their stated rules; on #285's word they reproduce #287's 904 gates and 220 squares exactly;
on gen5b they find 904 gates and 220 squares, committed as `descent-selection.json`, `target-selection.json`), and PR
#233's complex word (gcert/1 certificate of PR #256, Lean-checked in jacobalansussman/wht-power-saving-lean#2) as complex
supplier, which keeps the bit gain from being capped: #193's supplier (7.47455·10⁻⁴) would sit only 0.025% above this
bit side.

**Checks.** The word passes the two retained checkers (PR168-v4: 5 mutation controls rejected; PR200 word classes: formal
identity, 4 adverse controls rejected) and `gen5bit/producer/regenerate.py` reproduces the five pinned bit files byte for
byte. `verify.py` runs all nine stages fresh (virtual, raw, bit with descent and targets, scalar, primes, banks, complex,
math, finite) with nine omitted-stage controls. Every literal of #287's package that the new word changes was recomputed
and re-pinned (word sizes, entrance histogram, path census, parity counts, scalar events and hash, bank patterns and
counts, charts, selector calls, κ); no check is dropped.

Conditional, finite construction under the retained public all-size hypotheses of the source527 lineage (no Lean
certificate for the bit side). #285 and #287 are open PRs; their generator, pair module and stage code are reused
unchanged.

## Verify

    python -m pip install -r research/five-stage-gen5b-banks/requirements.txt    # sympy 1.14.0
    python3 -B research/five-stage-gen5b-banks/verify.py --output /tmp/gen5b-verification          # about 4 minutes; not under -I
    python3 -B research/five-stage-gen5b-banks/gen5bit/producer/regenerate.py --work /tmp/gen5b-regeneration

The workflow `.github/workflows/five-stage-gen5b-banks.yml` runs both on Ubuntu.

## Files

#287's package with: `gen5bit/producer/data` (the local design, all-but-one module and frozen arcs) and the five pinned
bit files regenerated; `descent-selection.json`, `target-selection.json` re-derived; the PR #233 complex certificate and
`inputs/complex/source-pins.json`; re-pinned `bank_check.py`, `bank_template.py`, `code/global_lowering.py`,
`code/physical527.py`, `code/complex_*.py`, `finite_check.py`, `math_check.py`, `parity_transform.py`,
`portable_complex.py`, `prepare.py`, `raw_ledger.py`, `scalar_check.py`, `virtual_check.py`, `verify.py`;
`discovery/` (the CP-SAT models, the exact compile models, the descent and target searches, the re-pinning tools; not run
by the verifier); `README.md`, `NOTICE.md` (this package's), `README-PR287.md` (#287's, unchanged).
