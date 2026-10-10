κ = 7.65146115390441e-4

# Concave-descent frame retiming on the p = 10 paired-cube word

**Conditional κ = 765146115390441/10¹⁸ = 7.65146115390441 × 10⁻⁴**, +0.120% over PR #315's p = 10 word
(7.64230861320245 × 10⁻⁴). The bit supplier binds (bit root 7.65732 × 10⁻⁴ against the centre-sharing complex
supplier's 7.72714 × 10⁻⁴).

This package is DreamingOfClouds' PR #315 package with one added transcript stage after `parity_transform.py`:
the concave-descent frame retiming of PR #287 (`descent_transform.py`, shape-generalized from h = 24 to the paired-cube
shape h = 20, m = 100, h copied centres of rank h − 2 with 3v/h scatter reads each) with a frozen
`descent-selection.json`. The p = 10 word has no frame retiming; local descent on the concave paid-rank objective
Σ r·ln(m/r) finds PR244's pattern again at this size: each of the 480 unborrowed source-pair mixes runs at its
rank-18 common delivery frame, so per pair the paid children of ranks 1, 1, 16, 18 become 17, 17, 2 — local paid
histogram delta {1: −960, 2: +480, 16: −480, 17: +960, 18: −480}, 480 local recursive calls disappear at unchanged
rank mass 181,050 (five-stage calls 248,360 → 245,960, rank mass 1,204,960 unchanged). No new frames are needed.
The transform rebuilds every MOVE from the retimed gate needs and independently checks the byte-identical scalar/COPY
projection, nested chains, fixed source/dirty/target endpoints, unchanged COPY lifetimes, nondegenerate endpoint
bases, both reflected annihilator ledgers and the exact integer source span of every non-target operand inside its
new frame; `raw_ledger.rebind_descent` recounts the five-stage profile. All changed counts (bank patterns,
banks per stage, literal stock 663,030 → 660,630, banked calls, unique bases 12,884 → 13,364, κ) are re-pinned in
`word-pins.json` by the package's own `discovery/repin.py`, and `verify.py` runs strict.

```sh
python3 -m pip install -r research/p10-descent/requirements.txt    # sympy==1.14.0
python3 -B research/p10-descent/verify.py --output /tmp/p10-descent-verification     # about 4 minutes, no network
```

Everything below is PR #315's own description (kept as `README-PR315.md`, `PROOF-PR315.md`). Prepared by Rohan Arun
with Anthropic Claude assistance; Apache-2.0; see `NOTICE.md`.

---

κ = 7.64230861320245e-4

# A p = 10 bit word in the five-stage completed banks

A conditional finite construction with **κ = 152846172264049/(2·10¹⁷) ≈ 7.64230861320245 × 10⁻⁴**.

This package ports #285's gen5 five-stage package to a smaller cube: the paired-cube bit word is generated at
**p = 10** (h = 20 coordinates, v = 960 sources) instead of p = 12 (h = 24, v = 1,760). The five-stage width
becomes m = 5h = 100, and the stage-private completed banks become 100-coordinate banks. Every later stage keeps
#285's logic, with its p = 12 literals replaced by cube-size formulas or by values pinned in `word-pins.json`.

The bit word comes from eumemic's PR168 generator, as in gen5, with three p = 10 data files:

- the pair module `pm_p10.json` (273 additions), annealed for p = 10;
- the all-but-one module `qmod_p10.json` (24 additions);
- the cube-local recipe trees of a pair-aware local design search, `local_design_p10.json`. The design was
  found by a search on the p = 12 word and is reused unchanged: it is cube-local, so it does not depend on p.

The physical layer follows PR200's rules, as in gen5. The compensated reuse recipients are the rank h − 3 = 17
gauges.

**Complex supplier of this variant, and the bit binds.** The complex program is a centre-sharing complex word
built with PR #304's recipe on three query modules and a patched graph builder (local research, not published;
see `inputs/complex/centre-mw/NOTICE`). Its coarse saving is b = 7.72714351296671e-4, certified with the 10⁻¹⁶
bad-class fallback like the bit side; the inherited no-fallback convention gives 7.72714354722691e-4. The bit's
certified coarse saving, 7.64815357e-4, is below the complex leaf cap (1 − β)·b. The bit therefore binds, and the
assembly path is #285's: the bit is fed at its certified root. (With PR #304's complex supplier,
7.6358781017907e-4, the bit root would exceed the cap. `math_check.py` also handles that complex-bound case, but
this package does not exercise it.)

The complex program itself is checked in every run by Jacob Sussman's reference checker `gx.check1` with the
exact scalar identity, and by his `gxcore` mirror of the two Lean checks. No Lean check of the program is pinned
here.

**Lean (run locally; not pinned here).** With Jacob Sussman's wht-power-saving-lean at f010392c (Lean v4.34.1,
Mathlib d13f23b) and his unchanged generator `tools/gx/regen_check.py`, the exact gcert pinned here (sha256
bb0499ab342aee3594904fc1cd72b9ff496cdb315d0840f4cdd5ba64ef794d34) was compiled to Lean and kernel-checked:
`OAI.PowerSaving.WHT.wht_main_block_B2Gcc27x`, the Walsh–Hadamard corollary at exponent 1 − 7727140/10¹⁰.
`tools/Compare.lean` passed against a challenge file that differs from Sussman's ChallengeB2Gp193x only in the
exponent and names; the axioms are propext, Classical.choice and Quot.sound. The official comparator and a clean
build from nothing were not run. This covers only the complex program's Walsh–Hadamard saving, not the bit word,
the bootstrap, the κ assembly or the retained integer-multiplication interfaces. Because the bit binds, κ is
unchanged if b is replaced by the Lean exponent.

| one invocation | gen5 (#285), p = 12, m = 120 | this package, p = 10, m = 100 |
| --- | ---: | ---: |
| virtual auxiliary roles | 17,292 | **9,120** |
| compensated reuse pairs | 1,406 | 890 |
| independent dirty registers R | 15,886 | **8,230** |
| formal F₂ columns 2v + R | 19,406 | 10,150 |
| independent entrances (ranks) | 2,554 (17, 18, 20, 21) | 1,270 (16, 17) |
| banks per stage | 164,934 | 86,526 |
| literal stock, 60 replicas | 1,247,070 | 663,030 |
| normalized stock / deficit | 249,414 / 52,800 | 132,606 / 24,480 |
| bit coarse saving (certified root) | 7.43337804075788e-4 | **7.64815357146385e-4** |
| complex coarse saving | 7.47454944651775e-4 (PR193, no fallback) | 7.72714351296671e-4 (centre-sharing, with fallback) |
| binding side | bit | **bit** |
| κ | 7.42785663120535e-4 | **7.64230861320245e-4** |

Run with Python 3.12 or newer (tested on 3.12 and 3.14), sympy 1.14.0 and assertions enabled:

```sh
python3 -m pip install -r requirements.txt
python3 -B verify.py --output /tmp/p10-five-stage-verification
```

The output directory must be new and outside this immutable package. Verification takes about three to five
minutes, uses no network and runs no producer. It performs these checks:

- the PR168-v4 checker on the virtual word, with its five mutation controls;
- PR200's physical-word proof as PR200 ran it: frames, handoffs, the physical row and all-column replays, with
  4 adverse controls;
- the retained source527 scalar program on all 10,150 formal F₂ columns, both integer decoder signs and 11
  corruptions;
- the physical event emitter, parity fusion and five-stage global lowering;
- exact h = 20/m = 100 geometry, including two actual rank-16 entrance bases and one actual rank-17 basis;
- exact determinants for 12,884 bases;
- 163 bank charts and all 2,469,000 bank assignments;
- the centre-sharing complex program: `gx.check1` with the exact scalar identity and the `gxcore` mirror, with a
  flipped-sign control;
- the complex supplier (labels, scalars, splice and finite guard), and both rational moment engines on the bit
  and complex profiles, each with the fallback;
- the assembly (bit-bound here) with all 47 outer inequalities, and the finite bill.

`bitword/producer/regenerate.py` rebuilds the five pinned bit-word files from the generator and the two
physical-layer producers, and checks them byte for byte. This is provenance only, not part of the proof.
`discovery/REPIN.md` describes how to re-pin the package mechanically for a new module file.

The result is conditional on the retained all-size compiler, common weighted chart, restored rows, selectors,
tape routing, prime supply, precision/recovery, complex symbolic correctness and analytic reduction. The included
finite checks do not replace those hypotheses. See:

- `PROOF.md` for the verification chain and what changed from p = 12;
- `BANK-PROOF.md` for the banks;
- `bitword/README.md` for the bit word;
- `NOTICE.md` for attribution.
