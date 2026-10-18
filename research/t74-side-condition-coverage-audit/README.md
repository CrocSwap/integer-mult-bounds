# Side-condition coverage audit of the pending T74 capped-fusion outer at PR #2044

**Status: adversarial audit and research note — no counterexample found. No new κ, no frontier change, and no
claim that the audited arguments are proved.**

The pending T74 family (#1673 → #1758 → #1786 → #1905/#1928 → #1992 → #2044) claims the conditional
κ = 0.0016797549561255445…, which is 0.43% above the selected record. Its final parameter point puts the group exponent
and the axis exponent within 10⁻³⁰⁰¹⁰ of 1: β = 1 − 6·10⁻³⁰⁰¹⁰ and ε = 1 − 2·10⁻³⁰⁰¹⁰. Many of the inherited
PR1673 notes were written at β ≈ 0.09 and ε ≈ 0.998.

This audit asks one question:

> Is every asymptotic side condition written into the 28 notes of the PR #2044 head either encoded as a ledger strict
> check and true at that final point, true there for an elementary reason, or explicitly superseded? Side conditions
> here are exponent inequalities and claims of the form "o(p)", "fits the record" and "eventually".

A condition that silently fails at the final point would invalidate the claimed κ, because the ledger only checks what it
encodes. Maintainer reviews of #1673, #1758, #1876 and #1928 leave these shared parameter-inequality interfaces open.

## Result

Four independent extractors read all 28 Markdown notes of `research/capped-fusion-t74-k554` at
`322949a53488d64023fedb89a6774927707e57ba`. They recorded 554 side conditions; 280 are distinct after
de-duplication. Each one was translated into the ledger's variables (d = p^ε, g = p^β, B = p^ξ, W ≈ p^½,
θ ≈ p⁻², halo p⁴⁸, core p¹²⁸). Each was then evaluated exactly at the #2044 final point, and also at the PR1786 and
PR1673 points as sanity controls.

| Classification | Count | Meaning |
|---|---:|---|
| COVERED | 262 | equals or is implied by named ledger strict checks (exact equality or a recorded identity) |
| AUTO_TRUE | 53 | true at the point for an elementary reason (constant inequality, polylog, structural) |
| OBSOLETE | 113 | explicitly superseded by a later note (file:line cited); many are false at the point, as intended |
| STALE_TEXT_ONLY | 64 | quotes an old numeric exponent or margin; the generic condition holds |
| NON_EXPONENT | 58 | a proof obligation not reducible to an exponent inequality (listed, not assessed) |
| FALSE_AT_POINT | 3 | a current statement that is false at the point, but **not load-bearing** |
| UNCOVERED_TRUE | 1 | true at the point but not tied to any ledger check |
| AMBIGUOUS | 0 | (one matcher item resolved as COVERED by two verifiers) |

**No load-bearing side condition is false at the final point.** Every condition the final chain needs is a ledger
check, implied by one, or elementary. Every condition that fails at the point is explicitly superseded. Examples are the
linear gauge guard, the `2β < 1` union-tag test, `β < 1 − ε`, the old g-factor union row, the union-density row and
`θ ≥ 1/(4d)`. Each of those held at PR1673's own point, which serves as a sanity control.

The smallest exponent margins are 10⁻³⁰⁰²², 10⁻³⁰⁰¹⁰, 2·10⁻³⁰⁰¹⁰, 4·10⁻³⁰⁰¹⁰ and 6·10⁻³⁰⁰¹⁰. These rows hold only
*eventually*, for astronomically large p. That suffices for an asymptotic exponent statement, but it is not a practical
cutoff.

### Text defects found (none changes κ)

1. **`outer/FINE-PADDING-COMPOSITION.md:37`.** The note says every non-main row exceeds κ by at least 10⁻³⁰⁰¹⁰. This is
   false: `global_coordinate_router_above_kappa` is 5.03·10⁻³⁰⁰¹¹, and several supplier checks are smaller still. What
   the proof needs is that every margin is positive, which the ledger checks. Both verifiers confirmed the statement
   is false.
2. **`outer/FINE-PADDING-COMPOSITION.md:38`.** The aside "ξ free in (1/2, ε); c = 1/2 gives ξ = 0.5" is false as
   written. With c = 3/32, ξ is pinned at ε(1+q) − c + s. With c = 1/2, ξ = 0.50168, and ξ = 0.5 would violate the
   boundary row and the strict cap. It describes an unused alternative boundary.
3. **`vendor/pr1673/capped-phase-fusion/HALO-THEOREM.md:205`.** "K₀² = o(p)" belongs to the theorem's §6
   instantiation, which assumes g = p^(1−ε−ζ), ε > 5/6 and L = O(p polylog p). At the final point it fails, since
   1 − 2(β+1−ε) = −1 + 8·10⁻³⁰⁰¹⁰. The theorem's own l.32/l.44 alternative, which pays the explicit metadata term
   O((gL/N)V K₀²/B), does hold: its exponent lies 2 + 2δ below the ledger's `microbox_face_corrections` row.
   **No final note records that branch choice.** Its only consumer at #2044 is `PHASE-LAYOUT-AUDIT.md` l.204–219.
4. **Uncovered constant.** The PR1786 umbrella exponent p¹⁰ (vendor `FINE-PRIME-PADDING.md`, polynomial norm bounds at
   θ ≈ p⁻²) holds with margin 7/2. No ledger check ties it to `THETA_POWER`; the ledger's only θ check is that the
   power is positive.
5. **Stale numbers.** `outer/FINE-PADDING-COMPOSITION.md:28` and `outer/UNION-SCHEDULE.md:121` quote
   ξ = 0.90792965…, which is PR1786's δ = 10⁻⁷ point. The pinned point is ξ = 0.90792975…. The other 62 STALE_TEXT_ONLY
   items are similar old margins and exponents.

### The two open review items

Both are resolved. Item 1 independently corroborates philippeVV's earlier reconciliation on #1897; see
"Relation to concurrent work" below. Details, file:line citations and the sweep table are in
[REVIEW-ITEMS.md](REVIEW-ITEMS.md), and `review_items.py` checks them exactly.

1. **The disabled `or True` assertion (`outer/check_gaugefree.py:23`; #1876/#1897).** The line checks the
   s = −δ/λ substitution against `δ² + δ²/λ − 2δ(1−λ)y`. The correct bracket is
   `(1−λ)x² − λ(1−λ)y² + δ² − δ²/λ + 2δ(1−λ)y`, which is #1876's supplemental identity. So the constant and the
   y-linear signs are both wrong, and the line would fail if it were made live. However:
   - **No live check depends on it.** The proof uses s = −δ(1−θ) for the broad block and s = −β₀/ρ for the narrow
     block, and both are checked by live assertions. The s = −δ/λ variant appears only in a parenthetical, and its
     linear coefficients are checked correctly by live line 25.
   - **Neither the ledger nor `run_outer.py` uses it.** `check_ledger.py` never uses the identity, and `run_outer.py`
     only runs the script.
   - **Lemmas 2.1 and 2.2 hold exactly**, as do the normalisation and the shrunk-shift coefficients.

   The #2044 head still ships the wrong line, and a second vacuous `or True` sits at `outer/struct_check.py:130`; the
   check it disables does not enter κ. The fix is to make line 23 a live assert with the correct bracket, or to
   delete it.
2. **"Confirm no other place charges g² per record" (GAUGEFREE-INTERIORS §7).** At the final point, no *active*
   step charges g² (or g·|F|) against one record:
   - **Superseded charges** cover every hit of the old per-axis U scan, the `1 − 2β` tag test, the full-key sort,
     g·a·d precision bits and the linear gauge. Each is superseded and rejected by a ledger control.
   - **Active charges** are per-visit tag work and header (1 − β = 6·10⁻³⁰¹⁰), membership (2·10⁻³⁰¹⁰), keys and the
     support router, and the halo g-fold passes (face-correction margin ≈ 77). All are ledger-encoded and true.
   - **One false option remains:** HALO-THEOREM's "K₀² = O(B)" option (defect 3 above). The package must use the
     explicit-metadata branch.

### Further observations

- **Offline precision at fine θ.** The offline term a/(4θ) = Θ(p² log p) is not o(p). The written argument handles it
  in PR1786 §3 (separate setup precision P_setup = Cp + 64p²L_p; `research/pr1786-fine-prime-transfer-audit` checked
  that section), but no ledger row encodes it. `global_gamma_power_slack` (1 − ε − r) is the θ ≈ 1/d version of a
  different bound.
- **Unused ζ.** ζ is stored in the ledger, but no ledger formula uses it.
- **Load-bearing removals.** The removals of `β < 1 − ε`, `g < √B` and union sparsity are load-bearing: all three
  conditions are false at the final point, so the stack depends on the arguments that removed them. These are
  SUPPLIER-SUPPORT §8, the gauge-free chirp guard and the per-visit union schedule.
- **Calling conventions that must hold.** The support-local supplier must be called globally. Charging V p^(1−a) per
  group would need a − (ε − β) > κ, which is false (−3.5·10⁻³⁰⁰¹⁰). Setup and online precision must likewise stay
  separate.

## Verification

- **Flagged items.** Every flagged item (FALSE_AT_POINT, UNCOVERED_TRUE, AMBIGUOUS) was checked by two independent
  agents. One tried to refute the flag; the other re-derived the condition from the argument it supports and evaluated
  it exactly.
- **Sampled re-check.** A seeded random sample (seed 72) of 28 non-flagged classifications (15 COVERED, 5 AUTO_TRUE,
  5 OBSOLETE, 3 STALE_TEXT_ONLY) was re-translated by a separate agent before it looked at the inventory. It agreed on
  27. The one disagreement mapped two structural premises (`h = O(p)`, `W = O(√p polylog p)`) to ε < 1. Those two
  items, pr1673a-58 and pr1673a-133, are now NON_EXPONENT, which does not change any truth value.
- **Verdict log.** All 38 verdicts are recorded in `INVENTORY.json`, under `verification_verdicts`.

## Reproduce

From the repository root, Python 3.10+ standard library only, about 30 s:

```sh
python3 -I -B research/t74-side-condition-coverage-audit/verify.py
python3 -I -B research/t74-side-condition-coverage-audit/review_items.py
```

Expected last line of `verify.py`:

```text
PASS_T74_SIDE_CONDITION_COVERAGE conditions=554 keys=133 covered=262 auto_true=53 obsolete=113 stale_text_only=64 non_exponent=58 false_at_point=3 uncovered_true=1 ambiguous=0 load_bearing_false=0 negative_controls=14 source_root=skipped
```

and for `review_items.py` (about 6 s):

```text
PASS_T74_REVIEW_ITEMS checks=88 mode=default item1_random_points=1500 seed=20441876 item2_records=18 active=11 superseded=6 false_option=1 cites=skipped ...
```

The verifier:

- rebuilds the exact #2044 final point from one pinned 30,000-digit rational (`complex_lower_pinned`) and the
  closed forms of `outer/check_ledger.py`, with SHA-256 fingerprints of 11 rebuilt rationals;
- evaluates all 133 condition keys at four points with an AST-whitelisted exact evaluator (no `eval`);
- checks every classification rule (for example, COVERED keys must hold at the point, OBSOLETE items must cite a
  superseding file:line, and FALSE_AT_POINT items must record `load_bearing: false` with true operative keys);
- recomputes 49 ledger strict checks and 7 rejecting-control rows from transcribed formulas;
- runs 14 negative controls: flipped classes, a corrupted β, undefined variables, forbidden AST nodes and others.

The audited sources live in the open PR, not on main. To re-check them, export that head into a new empty directory:

```sh
git fetch origin pull/2044/head
mkdir /new/empty/dir
git archive 322949a53488d64023fedb89a6774927707e57ba research/capped-fusion-t74-k554 | tar -x -C /new/empty/dir
python3 -I -B research/t74-side-condition-coverage-audit/verify.py --source-root /new/empty/dir
python3 -I -B research/t74-side-condition-coverage-audit/review_items.py --source-root /new/empty/dir
```

This re-hashes all 32 files in `SOURCES-T74.json` (blob id and SHA-256). It locates each of the 554 quotes within
±2 lines, checks the rebuilt parameters and the 49 checks against `LEDGER.json`, and runs two more source controls.

## Scope and limits

- **Checked:** the *written* side conditions and their exact truth at the final point. **Not checked:** the arguments
  themselves, including:
  - the accretive Toeplitz circuit theorem;
  - the SHALLOW-TOEPLITZ recursion;
  - the union-schedule correctness;
  - the locality/halo constructions;
  - the Trudgian prime step;
  - the all-size compiler, hosting and precision/tape interfaces;
  - the T74 supplier admission.

  The 58 NON_EXPONENT items list such obligations without assessing them.
- **Extraction coverage.** Extraction is exhaustive over the 28 notes, but it is a reading by language models,
  cross-checked by de-duplication, two verifiers per flag and a sample. A condition that no extractor recognised is not
  covered. Code-only assumptions in `check_*.py`, and the evidence archives under `vendor/pr1673/.../evidence/`, were
  not extracted.
- **Pinned head.** The result is pinned to the #2044 head. Later heads, and siblings such as #2161 and #2180 that
  change only ε-slack arithmetic, would need their final point re-substituted. `POINTS.json` makes this a small
  change.
- **Provenance of the inventory.** `INVENTORY.json` was produced in a local session from the extractor and matcher
  outputs, which are not retained. Every entry carries its file, line and verbatim quote so it can be re-checked
  against the pinned sources.

## Open next questions

1. **Record the HALO branch at the final point.** *Why it matters:* the stack relies on HALO-THEOREM's explicit
   metadata branch, but the only written instantiation (§6) assumes the obsolete PR1673 regime. *First step:* add a
   short note to the family's outer stating the K₀ instantiation, either as a ledger row or by citing
   `microbox_face_corrections`. *Blocked by:* author or maintainer action on the pending stack.
2. **Tie the p¹⁰ umbrella to `THETA_POWER`.** *Why it matters:* it is the only side condition found that is true but
   unchecked, and a future change to the θ power would not be caught. *First step:* a ledger strict check deriving
   the umbrella exponent from `THETA_POWER`. *Blocked by:* nothing.
3. **Extend coverage to code-only assumptions.** *Why it matters:* this audit reads prose only. *First step:* the
   same inventory method applied to the assertions in `outer/check_*.py` and `run_outer.py`. *Blocked by:* nothing; it
   is about the same size as this audit.

## Relation to concurrent work (philippeVV)

Philippe Van Velzen (philippeVV) published a closely related audit of the same #2044 head while this one was running.
It appears as PR comments and fork commits, which `scripts/find_overlap.py` does not index, so this audit's 00:30 UTC
overlap check missed it. That work has priority on the points below, and this package independently corroborates
them:

- **Broad-shift reconciliation** ([#1897 comment, 2026-10-14 19:40 UTC](https://github.com/CrocSwap/integer-mult-bounds/pull/1897);
  fork `philippeVV/integer-mult-bounds@a3c40a6f`, `research/t74-broad-shift-reconcile/`). It shows the disabled
  `or True` line is in a branch the proof does not use and corrects GAUGEFREE :31/:84 (the linear leftover is
  3b₀θB, not 2b₀θB). This package reaches the same conclusions by a different method: an exact Laurent certificate
  with no sympy (`review_items.py`).
- **Outer-layer audit and PR1673 fusion cost census** (#2044 comments, 2026-10-15 00:04–00:46 UTC; fork commits
  `e6bc8393`, `bc4ed55b`, `76af2562`, `d1e01310`):
  - an exact knockout showing the lift rests on PR1673's removal of the per-axis Vd row;
  - every PR1673 cost term evaluated at the #2044 point;
  - the same HALO `K₀² = O(B)` finding;
  - the support-local H-call and layout-contract follow-ups;
  - the CRLF, stage-E and self-authenticated cache issues.

This package does **not** repeat the knockout, the cost census, the H-call analysis or the release-path issues.
It adds:

- **Scope:** a machine-checkable inventory of *all* written side conditions in all 28 notes (554 items, 133
  exact keys), not only the PR1673 cost terms. It covers the outer, PR1758 and PR1786 notes as well, and maps each
  condition to the 62 ledger strict checks.
- **Exact re-check:** a registered standard-library verifier that re-evaluates every classification exactly at
  four points, with negative controls and source-pinned quotes.
- **Findings not in those comments:**
  - the false margin claim at `FINE-PADDING-COMPOSITION.md:37`;
  - the false aside at `FINE-PADDING-COMPOSITION.md:38`;
  - the PR1786 p¹⁰ umbrella that no ledger row ties to `THETA_POWER`;
  - the unused ζ;
  - the offline fine-θ precision term that no ledger row encodes;
  - the second vacuous `or True` at `outer/struct_check.py:130`;
  - the stale ξ digits;
  - the per-record g² sweep table.

## Credit and provenance

- **Audited work:**
  - Vlado Vojdanovski (PR1673, capped phase-cell fusion and its audits);
  - Jeremy Kothe and the PR1758/PR1839/PR2044 contributors (gauge-free interiors, union schedule, structured
    boundary, final ledger);
  - Chafik Boukhalfa (PR1786, fine-prime padding);
  - Rohan Arun and M6LI (PR1876, PR1897: the broad-shift identity and the discovery of the `or True` guard);
  - LeverRank (`sched_review.py`).
- **Overlap:** the nearest prior audit is `research/pr1786-fine-prime-transfer-audit`, which covers the fine-prime
  lemmas only and explicitly excludes the union schedule and layout. The concurrent philippeVV audit is described
  above.
- **Assignment and claim:** base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4. Sprint track 60–74
  (adversarial audit), OS assignment seed 72. No pinned coordination issue existed, so the claim was recorded locally.
- **AI assistance:** prepared for Sagar Thakrar with substantial AI assistance (Claude Code, Anthropic). Subagents did
  the extraction, ledger re-evaluation, matching, adversarial verification, sampled re-check and verifier
  construction. The main session checked GAUGEFREE Lemmas 2.1, 3.1–3.3 and Theorem 4.1(a)(b) by hand and reran every
  command. Apache-2.0.
