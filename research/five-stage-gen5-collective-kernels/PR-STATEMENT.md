# Compatible gen5 retiming and collective kernels

Conditional κ = **0.000744719882668682**, from the exact composition of 65
kernel-disjoint PR289 retimings with all 450 PR290 kernel entries.
See [COMPOSITION-PROOF.md](COMPOSITION-PROOF.md) for the selection, accounting,
reproducibility repair, credits, and unchanged conditional scope.

The original PR290 description below is retained as historical context; its
κ = 0.000744714499357628 is the parent baseline.

---

# Concave-descent frame retiming and target-prefix compression on the gen5 five-stage completed banks

**κ = 372060348198521/(5·10^17) = 7.44120696397042e-4**, conditional, with the bit supplier binding: +1.34 × 10⁻⁶ (+0.180 %) over the gen5 package below (7.42785663120535e-4).

This package is DreamingOfClouds' `five-stage-gen5-banks` with two added stages after `parity_transform.py`: `descent_transform.py` (frozen `descent-selection.json`) and then `target_transform.py` (eumemic's PR268 exact F₂ target-prefix compression, unchanged apart from the stream count; frozen `target-selection.json`). In each of 220 squares of four targets, every rank-20 entrance helper is read by exactly two of the four, so the dependent target's frame-20 prefix response is the F₂ sum of its three square-mates'; its 1,100 frame-20 reads are omitted, it receives `t −= p_j` at the zero frame at the cut and `t += p_j` at the square's common nondegenerate 21-dimensional frame at the close (1,320 setup/restore additions; 575,052 weighted ADDs), so ZERO →(20)→(1)→ 21 becomes ZERO →(21)→ 21 (histogram delta {1: −221, 2: −8, 17: −1, 18: −7, 20: −212, 21: +220}). The target transform recomputes every literal prefix dependency from the actual word, rebuilds every MOVE, checks nesting, endpoints, COPY lifetimes, nondegenerate bases and both all-column replays with an omitted-setup control, and rebinds the raw ledger. The retiming stage: The gen5 word had no frame retiming; local descent on the concave paid-rank objective Σ r·ln(120/r) reassigns 904 ADD frames: each unborrowed source-pair mix runs at its rank-22 common delivery frame exactly as PR244 did for source527 (per pair the paid children of ranks 1, 1, 20, 22 become 21, 21, 2) plus 24 further internal gates; local paid histogram delta {1: −1760, 2: +880, 6: +24, 7: −48, 8: +24, 20: −880, 21: +1760, 22: −880}, so 880 local recursive calls disappear at unchanged rank mass 411,356. The transform rebuilds every MOVE from the retimed gate needs and independently checks the byte-identical scalar/COPY projection, nested chains, fixed source/dirty/target endpoints, unchanged COPY lifetimes, nondegenerate endpoint bases, both reflected annihilator ledgers, and the exact integer source span of every non-target operand inside its new frame; `raw_ledger.rebind_descent` recounts the five-stage profile (474,744 calls after the retiming, 473,599 after the squares; rank mass 2,746,720) and `bank_check`/`verify.py` require the new counts and κ. `prime_check` retains the determinant obligation for producer frames the retiming removes (PR244's rule). Banks, entrances, charts, the scalar word and all endpoints are unchanged.

Prepared by Rohan Arun with Anthropic Claude assistance; Apache-2.0. Everything below is the gen5 package's own description.

---

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
