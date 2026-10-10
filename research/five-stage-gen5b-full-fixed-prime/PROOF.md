# Fixed-prime eight-level transfer on PR300 — proof outline

**Conditional κ = 749982571369270160072237 / 10²⁷ = 7.49982571369270160072237·10⁻⁴**, +4.10 × 10⁻¹² over
[PR #300](https://github.com/CrocSwap/integer-mult-bounds/pull/300)'s `187495641816757/(25·10¹⁶)` = 7.49982567267028·10⁻⁴.

This is the fixed-prime / eight-finite-level arithmetic transfer (Nespoli PR235, Arun PR243/PR261/PR265, sennemmi PR253;
package form jacklightChen PR293) applied to the actual literal costs of PR #300's `five-stage-gen5b-full` package,
whose complete 150-file tree is vendored unchanged under `source/` (commit `aea3dc9`, `upstream-files.json`). It is a
small arithmetic refinement at the same bit word and the same conditional interfaces: the retained prime q = 2¹²⁷ − 1
(Lucas–Lehmer residues in `prime-proof.json`, checked by `verify.py`), ρ = 3,456,000/q, the entire 32m² rank-one
fallback, two exact interval moment engines, eight finite acyclic ordinary levels, η = 10⁻²⁴, β = 10⁻⁹, all 47 strict
outer constraints and seven margins, with adjacent coarse/final 10⁻²⁷ points rejected. The bit side still binds below
#233's complex supplier (complex coarse 754736418878859/10¹⁸).

## Complete paid transfer (from `source/verify.py`'s fresh outputs)

* 60 physical replicas; literal stock 1,229,680 = 5·W with W = 245,936; literal children 28,973,400; literal rank
  mass 147,297,600; normalized m = 120, rank mass 29,459,520, deficit 52,800, max child 50.
* 910 charts, 4,627,800 bank assignments, normalizer bound 815, selector calls 905,935,487,400 =
  2·5·60·((1,229,680 − 1) + 15,426·120·815) < 2⁴⁰; q-power coefficient 90,408,185,853,299,401 < 2⁸⁰ < q, internal
  row coefficient 14,401; maximum determinant 118 bits, all remaining factors below 2⁸⁰.
* `prime_eight_port.py` asserts every one of these against the supplier's `certificate.json`, `finite.json`,
  `primes.json` and `banks.json`, rejects the old fallback density at the new rate, both adjacent coarse points, the
  adjacent final point at the eighth leaf and at the unattained coarse cap, four foreign fee vectors and a cyclic
  eighth level, then writes `certificate.json`, which `verify.py` compares key by key with the committed one.

## Verify

    python3 -m pip install -r research/five-stage-gen5b-full-fixed-prime/source/requirements.txt    # sympy 1.14.0
    python3 -B research/five-stage-gen5b-full-fixed-prime/verify.py --output /tmp/gen5b-full-fixed-prime-verification

Runs the complete vendored PR #300 verifier (about 7 minutes; all twelve stages fresh) and then the fixed-prime
transfer (under a second); prints `PASS complete gen5b-full fixed-prime eight-level reproduction` with κ.
`--check-package` checks hashes and syntax only. `validation/` holds the local supplier run that produced the
committed certificate (its κ `187495641816757/250000000000000000`).

## Scope

Conditional on exactly #300's retained interfaces (all-size compiler, weighted chart, restored rows, selectors,
routing, prime supply, precision/recovery, complex symbolic correctness, analytic reduction); no new coding mechanism,
no Lean build (the Lean sketch in `methods/Prime.lean` is PR293's, retained unchanged). Prepared by Rohan Arun with
Anthropic Claude assistance; Apache-2.0; see `NOTICE.md`.
