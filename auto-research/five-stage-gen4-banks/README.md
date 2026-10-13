# Concave-descent frame retiming on the gen4 five-stage completed banks

**κ = 90446448750933/(1.25·10^17) = 7.23571590007464e-4**, conditional, with the bit supplier binding: +7.02 × 10⁻⁷ (+0.097 %) over the gen4 package below (7.22869827347495e-4).

This package is DreamingOfClouds' `five-stage-gen4-banks` with one added stage, `descent_transform.py` (frozen selection `descent-selection.json`), run after `parity_transform.py`. The gen4 word had no frame retiming; local descent on the concave paid-rank objective Σ r·ln(120/r) reassigns 880 ADD frames, running each unborrowed source-pair mix at its rank-22 common delivery frame exactly as PR244 did for source527: per pair the paid children of ranks 1, 1, 20, 22 become 21, 21, 2 (local paid histogram delta {1: −1760, 2: +880, 20: −880, 21: +1760, 22: −880}), so 880 local recursive calls disappear at unchanged rank mass 425,742. The transform rebuilds every MOVE from the retimed gate needs and independently checks the byte-identical scalar/COPY projection, nested chains, fixed source/dirty/target endpoints, unchanged COPY lifetimes, nondegenerate endpoint bases, both reflected annihilator ledgers, and the exact integer source span of every non-target operand inside its new frame; `raw_ledger.rebind_descent` recounts the five-stage profile (483,146 calls, rank mass 2,809,600) and `bank_check`/`verify.py` require the new counts and κ. Banks, entrances, charts, the scalar word and all endpoints are unchanged.

Prepared by Rohan Arun with Anthropic Claude assistance; Apache-2.0. Everything below is the gen4 package's own description.

---

κ = 7.22869827347495e-4

# gen4 bit word in the five-stage completed banks

A conditional finite construction with **κ = 144573965469499/(2·10¹⁷) ≈ 7.22869827347495 × 10⁻⁴**.

The package keeps PR234's five-stage layout, the completed width-120 entrance banks and the whole
verification chain of eumemic's source527 package. Only the bit helper changes. It is a new paired-cube
bit word, **gen4**, with three changes to PR168's generator:

- a different per-cube local circuit;
- a pair module whose extra root is the copied centre;
- a re-annealed all-but-one module.

Its virtual word needs 17,904 auxiliary roles, against 18,908 for PR200's word. After 1,494
compensated reuse pairs and descended operation frames, the physical helper has **16,410** independent
dirty registers, against source527's 16,587, which needed 527 source loans and 34 terminal sinks. The bit
supplier still binds.

| one invocation, m = 120 | source527 (current package) | gen4 (this package) |
| --- | ---: | ---: |
| virtual auxiliary roles | 18,908 (PR200 word) | 17,904 |
| compensated reuse pairs | 1,760 | 1,494 |
| source loans / terminal sinks | 527 / 34 | 0 / 0 |
| independent dirty registers R | 16,587 | 16,410 |
| independent entrances (ranks) | 2,279 (12, 13, 18, 20) | 2,466 (20, 21) |
| literal stock, 60 replicas | 1,304,935 | 1,283,035 |
| normalized stock / deficit | 260,987 / 52,800 | 256,607 / 52,800 |
| bit coarse saving | 7.10573897320284e-4 | 7.23392746398452e-4 |
| κ | 7.10069340338651e-4 | **7.22869827347495e-4** |

Run with Python 3.11+ and assertions enabled:

```sh
python3 -m pip install -r requirements.txt
python3 -B verify.py --output /tmp/gen4-five-stage-verification
```

The output directory must be new and outside this immutable package. Verification takes about five
minutes, uses no network and runs no producer. It performs these checks:

- the PR168-v4 checker on the virtual word, with its five mutation controls;
- PR200's physical-word proof, exactly as PR200 ran it: frames, handoffs, the physical row and all-column replays, with 4 adverse controls;
- the retained source527 scalar program on all 19,930 formal F₂ columns, both integer decoder signs and 11 corruptions;
- the physical event emitter, parity fusion and five-stage global lowering, with exact h=24/m=120 geometry;
- exact determinants for 26,249 bases;
- 370 bank charts and all 4,923,000 bank assignments;
- the retained complex supplier, both rational moment engines, the 47 outer inequalities and the finite bill.

`gen4bit/producer/regenerate.py` rebuilds the five pinned bit-word files from the generator and the two
physical-layer producers, and checks them byte for byte. This is provenance only, not part of the proof.

The result is conditional on the retained all-size compiler, common weighted chart, restored rows,
selectors, tape routing, prime supply, precision/recovery, complex symbolic correctness and analytic
reduction. The included finite checks do not replace those hypotheses. See `PROOF.md` for the
verification chain, `BANK-PROOF.md` for the banks, `gen4bit/README.md` for the bit word and `NOTICE.md`
for attribution.
