# Chronological donor sharing, retiming and complete banking

**Conditional kappa = 711074913688782665281379/1000000000000000000000000000 = 0.000711074913688782665281379.**

This physically extends the 518-entrance PR259 construction to **545 entrances at nine cuts**, with total entrance rank 1371. It then composes PR263's 25 exact gate retimings and PR261/265's fixed-prime finite-level arithmetic. The previous delivered value was0.000711029386054035; PR265's public composition is0.000711032242134072007667807. This is a modest improvement over both, not a claim of a huge exponent jump or global optimality.

The added physical saving comes from pricing shared donors through their actual chronological nested-frame chains when choosing compatible kernels. Every selected basis, scalar gate, frame transition, bank block and inverse is checked. A 120-replica bank allocation removes the general modulo-three restriction on admissible entrance rank. This final rank 1371 happens to be divisible by three;120 replicas are a uniform implementation choice, not a separate exponent gain for this final witness. Their larger finite cost is fully charged.

## Reproduce

Requires Python 3.11+, SymPy 1.14.0, GNU-compatible C++17 and Boost headers:

```sh
python -m pip install -r requirements.txt
python verify.py --output ../kernel-descent120-replay
```

Use a new output directory outside the package. On Windows, --cxx and --boost-include select MinGW and the Boost-header parent. The default regenerates pinned upstream sources and executes eight native checkers plus the exact retiming stage. Allow several minutes: the Python retiming audit checks tens of thousands of rational frames. No network, credentials, Lean or GPU is required. New mathematical computation is C++; inherited source generation and retiming are Python.

The verifier checks 20,107 local formal columns forward and inverse,23,627 global columns, all selected prefix relations, chronological geometry and COPY lifetimes, exact charts, all 9,952,200 bank assignments, the final finite invoice, two rational moment engines, eight finite ordinary levels, 47 strict assembly inequalities and successor rejection. Saved expected receipts are compared only after executing the computations. Both input and output word hashes and the complete package manifest are pinned.

The retiming stage retains every upstream mathematical check; its only computational optimization caches exact canonical frame keys once rather than calculating them twice. Its output must match the unchanged upstream stage. --snapshots-only explicitly records weaker baseline provenance; it is not the default.

## Finite inventory

Literal stock: 2601390. Selector charge: 1882893202800. Full counted primitive coefficient: 187960919367543601 (58 bits), below 2^80. Payload bound: 98 bits, below 104. No gate or bank cost is excluded to obtain the stated exponent.

## Scope and credit

Retains the public all-size compiler, common weighted chart, restored rows, routing, prime supply, precision/recovery, complex correctness and analytic interfaces. This does not independently prove those interfaces, an unconditional multiplication theorem, a practical runtime gain or Lean certification. Higher public numbers labelled unbuilt targets are not silently treated as witnessed baselines.

Pinned baseline: PR249 at96495746c786d6d0339dbb38c7f553d4af3f88ed. Retiming: PR263 at87129308f762f86a9d8e9a60f5d6c8ef23ce1f6e. Arithmetic: PR261 atd2c63486d895860a65f25b80a51f4b2ec4f3c6ef; the same public retiming/arithmetic composition is PR265. See NOTICE.md for retained contributors, licenses and assistance disclosures. No personal byline, local machine paths or executable binaries are included.

See PROOF.md, REPLICATION-PROOF.md, FINITE-PROOF.md, COPY-PROOF.md and REVIEW.md. KERNEL-PROOF.md and BANK-PROOF.md preserve predecessor arguments; historical counts are superseded by the final receipts.
