# Audit: the endpoint-to-kappa reduction of the selected frontier799 assembly

Assignment seed 67, track 60-74 (adversarial mathematical audit).
Prepared with help from opencode. Apache-2.0, per CONTRIBUTING.md.

## What was audited

One accounting step: the reduction that turns the recorded moment endpoints
of the selected conditional witness into the headline

    kappa = 1661634653669567/10^18 = 0.001661634653669567.

Precisely, the function `outer_witness` in
`research/gauge44-frames-x/code/assemble.py` and the 47 strict constraints of
`research/complex-k492-owner-repair/vendor/multicold/engines/outer.py`,
evaluated on the committed record
`research/community-frontier799-audit/ASSEMBLY.json`. The reduction is:

    s      = min(c, (1-beta)*b) - 1e-27
    a_0    = 384599/10^10;  a_{i+1} = (1-s)*s + s*a_i   (seven steps)
    q_w    = a_7 * (1-2*eta)
    margin = (1-eta)*q_w/(1+q_w)          (= eps*q = the minimum of the 7 margins)
    kappa  = largest 1e-18 grid point strictly below margin

with eta = beta = 1e-24. The statement examined: the recorded kappa is exactly
this reduction of the recorded endpoints and guards, and the improvement over
the conservatively admitted kappa is attributable to one specific change.

## Base commit and pins

- Base commit: `f567884aeb8851b6e794af1184119a3bfbe1e631` (origin/main).
- Audited record: `research/community-frontier799-audit/ASSEMBLY.json`,
  sha256 `65c7648a8edaeaf4e0b8de3e21eeda94fba124d0935010d45ac9f76375b72cec`,
  audited source head `80e6463157cfc80b85af09e7e2f14748fe2dac60`
  (`certificates/selected-result.json`).
- The three engines I transcribed the formulae from were hash-checked against
  the assembly's own `input_sha256` pins and match exactly:
  `engines/moment.py` `81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482`,
  `engines/base_two_moment.py` `aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098`,
  `engines/outer.py` `c1ebb52163a7219504c728a5c2b098bf1e50bf20148a2879c5a74c3cadc7c03c`,
  read at `research/complex-k492-owner-repair/vendor/multicold/engines/`.

## Method

`audit_kappa_reduction.py` recomputes the entire reduction and all 47 outer
slacks with exact rationals (`fractions`), importing none of the repository
engines. Every recorded value it recomputes is compared exactly, not
numerically: the two kappa pairs, both decimal fields, both seven-row bootstrap
tables, and all 94 recorded outer slacks (accepted and conservative rows).

Reproduce:

    python research/audit-kappa-floor-seed67/audit_kappa_reduction.py

Expected output (CPython 3.13.15, stdlib only, no `-O`):

    PASS endpoint-to-kappa reduction audit (seed 67)
      kappa                        = 1661634653669567/1000000000000000000
      margin - kappa               = 7.578608e-20
      (kappa + 1e-18) - margin     = 9.242139e-19
      binding endpoint             = complex
      endpoint slack c-(1-beta)b   = 6.902676e-05
      conservative -> accepted gap = 2881809/1000000000000000000 (=2.881809e-12)
      endpoint gap b - b_c         = 2.891409e-12
      transfer factor              = 0.996679726523
      guard cap cost (guards->0)   = 7.634935e-27
      guard grid cost              = 0
      tightest outer slacks        = [('lambda_above_internal', '1.664e-27'), ('lambda_above_tau', '1.664e-27'), ('lambda_prime_above_lambda', '1.664e-27'), ('q_below_internal', '3.329e-27'), ('delta_positive', '1.250e-25')]
      margin cluster above minimum = [('Gaussian_arithmetic', '3.750e-25'), ('balanced_prefix', '1.000e-24'), ('compact_phase_layer', '0.000e+00'), ('scalar_work', '8.750e-25')]
      bootstrap cutoff_log2        = ['4915613269871', '1774443388201110908', '640540491097945923200390', '231222998414134964443595932879', '83467127743916184993039472927586044', '30130053937546965452116011965235164002719', '10876379418071676456390609457427077833228788828']
      negative controls detected   = 4

## Findings

All findings are exact-recomputation results on the committed record. No
counterexample was found in the audited step.

**F1 (identity confirmed).** The recorded kappa is exactly the largest 1e-18
grid point strictly below the margin: recomputation from the recorded
endpoints and guards matches digit for digit, `kappa < margin < kappa+1e-18`,
and `margin - kappa = 7.578608e-20`, so the accepted kappa sits 0.076 of one
tick below its cap. The strict floor matters at this instance: a
nearest-grid rounding would pick `kappa + 1e-18` and violate the
compact-phase-layer margin.

**F2 (refined claim: a four-way near-tie, not a single binding cap).** The
margin is `minimum = eps*q`, the `compact_phase_layer` margin of outer.py, and
it is strictly the smallest of the seven margins. But the binding cluster is
four margins within one tick of it: `compact_phase_layer` (0),
`Gaussian_arithmetic` (+3*eta/8 = 3.75e-25), `scalar_work` (+7*eta/8 =
8.75e-25), `balanced_prefix` (+eta = 1e-24). At `kappa + 1e-18` exactly these
four `_above_kappa` slacks turn non-positive and every other strict slack
stays positive; at `kappa - 1e-18` all 47 slacks are positive. So the next
tick is blocked by the guard cluster as a whole, and any future improvement
must clear all four margins, not only `compact_phase_layer`. The
kappa-independent slacks are nowhere near binding: the tightest
(`lambda_above_tau`, `lambda_above_internal`, `lambda_prime_above_lambda`)
equal `a_7 * eta = 1.664e-27` exactly.

**F3 (surcharge attribution confirmed).** The published kappa exceeds the
conservatively admitted `conservative_kappa = 830817325393879/500000000000000000`
by exactly `2881809/10^18 = 2.881809e-12`, matching the recorded
`native_correction_gain`. The only input difference between the two reductions
is the complex endpoint (`b = 0.001664400278850482327913` unsurcharged versus
`conservative_complex_lower = 0.001664400275959073058404` with the bad-residue
surcharge; gap `2.891409e-12`), transferred through the margin with factor
0.996679726523. No other accounting step in the reduction contributes to that
improvement. The published kappa is therefore exactly as strong as the
surcharge-removal justification (the retained PR559 exact-cover recurrence
correction) and no stronger; the certificate's own model controls show the
surcharged moment rejects at `b`.

**F4 (guard cost quantified).** Setting eta = beta = 0 and removing the
1e-27 floor in `s` raises the cap by exactly `7.634935e-27` and the grid kappa
by 0 ticks. The guard parameters cost less than one tick of the current
1e-18 grid; no kappa improvement is available from tuning them at this grid
resolution. (This is a headroom computation, not a witness: outer.py requires
eta > 0 and beta > 0 strictly, so zero guards are not admissible.)

## Negative controls

The script tampers the committed record four ways and asserts each is caught:
kappa bumped one tick, `native_correction_gain` altered, endpoints swapped,
and one outer slack replaced. It also asserts that a nearest-grid rounding
selects the next tick and fails the compact-phase-layer margin. All four
tamper controls are detected on the current record.

## Coverage limits and inherited assumptions

- These are finite exact recomputations of recorded identities. They are not
  a formal proof and not a re-run of the construction.
- Not checked here: the moment-engine claims themselves ("accepted at b,
  rejected at b+1e-24" for both engines), the invoice and owner audit feeding
  the endpoints, the seven bootstrap cutoffs' analytic role
  (`cutoff_log2 >= 4915613269871` identities were recomputed and match the
  record; their sufficiency is the inherited analytic-transfer hypothesis),
  and the surcharge-removal justification (PR559 exact-cover recurrence).
  Those remain exactly where the selected record places them.
- Inherited all-size/compiler, common-label/mutable-source, whole-call
  hosting, precision/tape and analytic hypotheses remain assumptions. This
  note does not change the selected result and claims no new kappa.
- The bootstrap cutoffs for steps 2-7 grow past 10^18; the record treats them
  as exact integers and so do I. Whether that regime is meaningful is an
  analytic question outside this audit.

## Documentation gap closed

The maintainer review (`docs/research/community-frontier799-review.md`) and
the package README do not state which margin caps the headline kappa, the
strict 1e-18 floor semantics, or the exact attribution of the
`2881809/10^18` conservative-to-accepted gap. This note pins all three from
the code and the committed record, together with the four-way binding cluster
of F2.

## Attribution

Reduction and constraint engines retained from the PR547/PR548 lineage:
`engines/outer.py` prepared by eumemic with Anthropic Claude assistance
(47 constraints retained from icekylinx's PR144, adapted from Zhihao Chen's
PR23; balanced prefix from the RaD project); `code/assemble.py` prepared with
OpenAI Codex assistance in chafreaky's lineage. The selected assembly and its
review are the frontier799 maintainers' work; PR559's exact-cover recurrence
correction is credited there. This audit is new work by sprint agent-05 with
help from opencode, on base commit f567884aeb8851b6e794af1184119a3bfbe1e631.
