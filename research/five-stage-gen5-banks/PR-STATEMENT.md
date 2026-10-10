# Extreme-meet frame retiming on target-compressed gen5 five-stage completed banks

**κ = 186031848117737/(2.5·10^17) = 7.44127392470948e-4**, conditional, with the bit supplier binding: **+6.70 × 10⁻⁹ (+0.0009 %)** over updated PR #287 (7.44120696397042e-4).

## Summary of the Construction

This package builds directly on DreamingOfClouds' `five-stage-gen5-banks` (#285) with three chained post-parity transformations:

| Stage | PR Origin | Gates / Groups | Local Paid Calls | Exponent $\kappa$ |
| :--- | :--- | :---: | :---: | :---: |
| **Base Word** | #285 (DreamingOfClouds) | — | 476,464 | $7.42785663 \times 10^{-4}$ |
| **1. Concave Descent** | #244 / #287 (Rohan Arun) | 904 ADD gates | 474,744 | $7.43528852 \times 10^{-4}$ |
| **2. Target Prefix** | #268 (eumemic) / #287 (Rohan Arun) | 220 square groups | 473,599 | $7.44120696 \times 10^{-4}$ |
| **3. Extreme-Meet** | #289 (This package) | 87 meet gates | **471,480** | **7.44127392 \times 10^{-4}** |

### 1. Concave-Descent Retiming (`descent_transform.py`)
Reassigns 904 ADD gate frames using local descent on the concave paid-rank objective $\sum r \ln(120/r)$. Each unborrowed source-pair mix executes at its rank-22 common delivery frame (PR244) plus 24 internal gates. Local paid histogram delta:
$$\{1: -1760, 2: +880, 6: +24, 7: -48, 8: +24, 20: -880, 21: +1760, 22: -880\}$$
Eliminates 880 local recursive calls at invariant rank mass 411,356.

### 2. Target-Prefix Compression (`target_transform.py`)
In each of 220 squares of four targets, rank-20 entrance helpers are shared: each dependent target's frame-20 prefix response is the $\mathbb{F}_2$ sum of its three square-mates. Its 1,100 reads are omitted; it receives $t \mathrel{-}= p_j$ at the cut zero frame and $t \mathrel{+}= p_j$ at the square's common nondegenerate 21-dimensional frame at close (1,320 setup/restore additions; 575,052 weighted ADDs). Frame transition $\text{ZERO} \to (20) \to (1) \to 21$ becomes $\text{ZERO} \to (21) \to 21$. Histogram delta:
$$\{1: -221, 2: -8, 17: -1, 18: -7, 20: -212, 21: +220\}$$

### 3. Extreme-Meet Frame Retiming (`extreme_transform.py`)
Extends the word by identifying 87 mutually role-disjoint, target-stream-disjoint ADD gates whose operands admit exact common nondegenerate meet frames ($F_{\text{meet}} \subseteq F_{\text{old}}$ with $F_{\text{meet}} \subseteq F_{\text{next},a}, F_{\text{next},b}$):
- **24 gates** retimed from dimension $12 \to 14$
- **63 gates** retimed from dimension $18 \to 19$
- **Zero role collisions:** All 174 operand roles are distinct.
- **Zero target interference:** All operations strictly disjoint from target streams ($r < 1760$ or $r \ge 3520$).
- **Concave gain:** $\Delta \Phi = \sum r \ln(120/r) = \mathbf{+10.924353}$ at invariant rank mass $2,746,720$.
- **Paid recursive calls:** Reduced from $473,599 \to \mathbf{471,480}$ (total five-stage records: 670,267).
- Verified byte-identical scalar/COPY projections, nested chains, and integer source spans across all 19,406 formal variables.

## Lineage and Contributor Chain Credit

Apache-2.0 applies. All original headers, licenses, notices, and AI-assistance disclosures are preserved across the lineage:

| Scope | PRs | Key Contributors | Description |
| :--- | :--- | :--- | :--- |
| **Framework** | #109 | Douglas Colkitt | Community framework maintenance, project coordination, and integration audits. |
| **Paired-Cube** | #144 | icekylinx | Paired-coordinate and shared-core framework with configurable local channels. |
| **Recycling & Gauges** | #146, #147, #150, #151 | Thomas Marchand (Th0rgal), William Porter (hpst3r), DaysSky, SovereignSteak | Min-cut gauge subsets, terminal accumulator elimination, delayed dirty reads, and physical register recycling. |
| **Carrier & Stopping** | #124, #148, #158, #166 | James Chang (jamesyc), Rohan Gupta (gupt1156), Abhinav Ramachandran (geckods) | Compensated birth-read reuse, carrier closure, tighter stopping parameters, and atom tolls. |
| **Bit Word & Packaging** | #168, #210, #268 | eumemic | Annealed signed modules, physical bit word, target-prefix compression, and source527 verification package. |
| **Complex Supplier** | #181, #193, #200 | Chafik Boukhalfa (chafreaky), Avi Eisenberg (ikeboy) | Shared-edge complex supplier and physical-word proof classes. |
| **Completed Banks** | #186, #197 | Evan McKinney (evmckinney9), Dugongue | Completed entrance bank methodology, coordinated frames, and conflict-free schedules. |
| **Five-Stage Layout** | #234 | Henry Grant (hcg890), Jacob Sussman | Five-stage architecture, stage-private width-120 banks, and gcert/1 export. |
| **gen4 & gen5 Words** | #276, #285 | DreamingOfClouds | Arc-aware per-cube circuit and exact compile-cost annealed modules (debt 164 & 11). |
| **Descent & Target PR287** | #211, #237, #244, #287 | Rohan Arun (rohanarun) | Width-120 application, 904-gate concave descent retiming, and 220 target-prefix squares. |
| **Extreme-Meet Retiming** | #289 (This PR) | Rohan Gupta (gupt1156) | 87 extreme-meet retimings on gen5 post-target word; Google DeepMind Antigravity assistance. |

Everything below is the gen5 package's own description.

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
