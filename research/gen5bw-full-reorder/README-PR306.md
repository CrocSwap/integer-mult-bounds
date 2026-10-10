κ = 7.51458925311258e-4

# Restart-packed kernels on weighted gen5b matching, with reordering

**Conditional κ = 375729462655629 / (5·10¹⁷) = 7.51458925311258·10⁻⁴** (+3.184·10⁻⁷, +0.0424% over this package's
base 7.51140529238897·10⁻⁴, PR #305, described below).

This revision appends PR #299's reordering stage (`reorder_transform.py`, unchanged; section 3 of
[LEVERS-PROOF.md](LEVERS-PROOF.md)) after the terminal sinks, in two rounds, each screened on the actual word:

| step | moves | local delta | φ-ledger | κ predicted = verified |
| --- | ---: | --- | ---: | ---: |
| base (#305: kernels, second descent, restorations, sinks) | — | — | — | 7.51140529238897·10⁻⁴ |
| **reorder** | 237 | {2:+237, 3:−217, 4:−25, 5:+5, 6:−20, 8:+20, 21:−212, 22:+212} | −495.07 | 7.51458164306940·10⁻⁴ |
| **reorder2** (screen re-run on the reordered word) | 2 | {2:+2, 3:−2, 4:−2, 5:+2} | −1.18 | 7.51458925311258·10⁻⁴ |

A moved addition y += c·h is executed, unchanged, next to a neighbouring incidence of one of its operands and in that
incidence's frame. No gate between the two positions reads y or writes h, so the scalar map is identical over the
integers (checked by an independent replay modulo 2⁶¹−1 with dirty inputs, besides the all-column F₂ replay with an
omission control and the exact source-span rule on every gate). Rank mass, registers, endpoints, entrances, copies,
stock and the deficit are unchanged. A fixed-point re-census after round 2 (reorder, restoration, sink, descent and
kernel screens on the final word) finds nothing worth 10⁻⁸; see LEVERS-PROOF.md.

`python -B verify.py --output DIR` now runs fourteen mandatory stages (adds `reorder`, `reorder2`) with fourteen
omitted-stage controls; changed literals are re-pinned in `expected/kernel-pins.json`. Everything below describes the base.

κ = 7.51140529238897e-4

# Restart-packed kernels on weighted gen5b matching

This package composes PR275's weighted gen5b matching with PR300's full restart-packed kernel selection and second descent. The exact conditional value is `751140529238897/10^18`, or κ ≈ 7.51140529238897 × 10⁻⁴. It is about 0.00863% above the pinned PR275 result, 7.51075693834608 × 10⁻⁴.

All 1,734 entries from PR300 map by their logical helper roles onto the weighted word: 920 twin pairs, 431 triples and 383 quadruples, adding entrance rank 2,196. All 87 second-descent retimings map uniquely by signed scalar occurrence and exact old-frame basis. Fresh endpoint screens then admit 440 early restorations and eight terminal sinks. No separate exponent gains are added.

The final word has 18,944 local registers, 15,424 independent dirty helpers, 721,422 weighted ADDs, and SHA-256 `9c8dd18e7df17e3e98c4a7054334280e24967190af9c028365270ed51d21fdd3`. Its literal stock is 1,229,665 at 60 replicas. The full scalar, chart, bank, prime, finite and exact-moment checks are mandatory.

```sh
python -m pip install -r requirements.txt
python -B verify.py --output /absolute/path/to/fresh-output
```

Use Python 3.11+, SymPy 1.14.0 and a new output directory outside the package. The verifier reconstructs all twelve stages, executes the retained mutation and omission controls, and checks every input hash before and after. Discovery pin-recording mode is rejected. No network is needed.

The weighted producer and its five virtual files are unchanged from PR275 and can independently be regenerated with `python -B gen5bit/producer/regenerate.py --work /absolute/path/to/fresh-regeneration`.

The all-size compiler, chart, restored-row, selector, routing, prime-supply, precision/recovery, complex-correctness and analytic interfaces remain inherited assumptions. This is a conditional finite construction, not an unconditional multiplication theorem, Lean certificate or practical benchmark. Original notices and licenses are retained; this composition was prepared with substantial OpenAI Codex assistance.
