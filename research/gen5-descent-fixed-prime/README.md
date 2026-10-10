# Fixed-prime eight-level gen5 collective descent

Conditional **κ = 744728654228590183370616/10^27 = 0.000744728654228590183370616**.

The complete fixed-prime and eight-finite-level transfer is recomputed on the
actual current PR291 collective/descent supplier. Its exact gain over PR291's
744728650221677/10^18 is **4006913183370616/10^27**. This is a small arithmetic refinement,
not a crossing of 2^-10 or a new structural multiplication algorithm.

All 139 original Git blobs from PR291 at
77d92c521e442c802b6fb4717bd8d066971a4b82 are retained byte-for-byte, with notices,
licenses and original proof. No private research material is included.

```sh
python3 -m pip install -r research/gen5-descent-fixed-prime/source/requirements.txt
python3 -B research/gen5-descent-fixed-prime/verify.py --output /tmp/gen5-descent-prime-fresh
```

Python 3.11+, SymPy 1.14.0, assertions enabled. The output directory must not
already exist. This offline standalone reproduction recomputes Lucas–Lehmer,
runs all original supplier stages including both descents, and compares the
complete expected mathematical certificate. `--check-package` is only hash and
syntax preflight. Local execution used exact unchanged-input reuse and fresh
changed checks, not a redundant original full-driver run. See VALIDATION.md.

The all-size Clifford/tensor, weighted common-ancestor, exact named endpoints,
restored-row, local-ring fallback, routing, precision/recovery, complex symbolic
flow and analytic/fixed-tape interfaces remain conditional. No new Lean proof,
unconditional theorem, practical speedup or exclusive priority is claimed.

Sources: [PR291](https://github.com/CrocSwap/integer-mult-bounds/pull/291),
[PR290](https://github.com/CrocSwap/integer-mult-bounds/pull/290),
[PR287](https://github.com/CrocSwap/integer-mult-bounds/pull/287),
[PR235](https://github.com/CrocSwap/integer-mult-bounds/pull/235),
[PR243](https://github.com/CrocSwap/integer-mult-bounds/pull/243),
[PR253](https://github.com/CrocSwap/integer-mult-bounds/pull/253).
