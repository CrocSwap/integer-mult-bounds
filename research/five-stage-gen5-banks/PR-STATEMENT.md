κ = 7.42785663120535e-4

# gen5 bit word in the five-stage completed banks

A conditional finite construction with **κ = 148557132624107/(2·10¹⁷) ≈ 7.42785663120535 × 10⁻⁴**.

This package is #276's gen4 package with one change: a new bit word, **gen5**. gen5 keeps gen4's arc-aware
per-cube local circuit and replaces its two module circuits. Both new modules were annealed against the
exact one-instance compile cost.

| Module | gen4 | gen5 |
| --- | --- | --- |
| pair + copied centre | 448 additions, debt 184 | 463 additions, 299 arcs, debt 164 |
| all-but-one | 34 additions, 22 arcs, debt 12 | 32 additions, 21 arcs, debt 11 |

Every later stage is unchanged: PR234's five-stage layout, the stage-private width-120 completed banks and
the source527 verification chain (eumemic). The bit supplier still binds, 0.55% below the retained complex
supplier.

| one invocation, m = 120 | gen4 (#276) | gen5 (this package) |
| --- | ---: | ---: |
| virtual auxiliary roles | 17,904 | **17,292** |
| compensated reuse pairs | 1,494 | 1,406 |
| independent dirty registers R | 16,410 | **15,886** |
| independent entrances (ranks) | 2,466 (20, 21) | 2,554 (17, 18, 20, 21) |
| literal stock, 60 replicas | 1,283,035 | 1,247,070 |
| normalized stock / deficit | 256,607 / 52,800 | 249,414 / 52,800 |
| bit coarse saving | 7.23392746398452e-4 | **7.43337804075788e-4** |
| κ | 7.22869827347495e-4 | **7.42785663120535e-4** |

Run with Python 3.11+ and assertions enabled:

```sh
python3 -m pip install -r requirements.txt
python3 -B verify.py --output /tmp/gen5-five-stage-verification
```

The output directory must be new and outside this immutable package. Verification takes about five
minutes, uses no network and runs no producer. It performs these checks:

- the PR168-v4 checker on the virtual word, with its five mutation controls;
- PR200's physical-word proof, exactly as PR200 ran it: frames, handoffs, the physical row and all-column
  replays, with 4 adverse controls;
- the retained source527 scalar program on all 19,406 formal F₂ columns, both integer decoder signs and
  11 corruptions;
- the physical event emitter, parity fusion and five-stage global lowering;
- exact h=24/m=120 geometry, including one actual entrance basis of each rank 17, 18, 20 and 21;
- exact determinants for 25,802 bases;
- 411 bank charts and all 4,765,800 bank assignments;
- the retained complex supplier, both rational moment engines, the 47 outer inequalities and the finite
  bill.

`gen5bit/producer/regenerate.py` rebuilds the five pinned bit-word files from the generator and the two
physical-layer producers, and checks them byte for byte. This is provenance only, not part of the proof.

The result is conditional on the retained all-size compiler, common weighted chart, restored rows,
selectors, tape routing, prime supply, precision/recovery, complex symbolic correctness and analytic
reduction. The included finite checks do not replace those hypotheses. See `PROOF.md` for the
verification chain, `BANK-PROOF.md` for the banks, `gen5bit/README.md` for the bit word and `NOTICE.md`
for attribution.
