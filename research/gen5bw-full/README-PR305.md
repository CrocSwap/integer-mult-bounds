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
