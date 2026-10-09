This builds on #104 (`948ce1510df750f4c18b96bdaef436a86f8bf834`) and the exact #113 cyclic-strip producer (`0eee4d507092a96bde88de703f07574ba17401a8`).

Under those interfaces,

$$
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=\frac{942802139}{10^{13}}=0.0000942802139.
$$

The saving is **54.4687% above $2^{-14}$**.

## Construction

**Bit network (23,23).** Apply #104's common-basis, opposite-bank stopped compiler to every proper projector of Swapnil Jain's frozen round-seven word, pinned at `741e7aa078392553815df7926ee17ac5e25a8c38`. Every nonzero projector residual is one reversed child of its full rank. The strict coarse saving is `15513/125000000`; stopping at atom exponent `1/1000`, with ordinary leaf saving `384599/10^10`, gives ordinary bit saving `1240183559/10^13`.

**Complex network (24,24).** Keep #113's producer and legal matching: 68,188 additions, 8,120 roots, 37,802 matched links and 38,506 physical auxiliary roles. Reconstruct the invertible matched scalar word `L`, signed rational scatter `J`, and exact complete adjoint `C=JL`.

A 32,488-event closure computes the 24 retained centers first, preserving every role's full access order, including read/read dependencies. Checks cover **209,340 accesses**, retained-center boundaries and 8,096 ordinary root reads. Selected scratch is untouched by the closure and injection.

Select **9,356 nondegenerate partial subframes** (3,309 distinct frames), each contained in its first owner and every target hyperplane receiving its adjoint coefficient. Target readouts follow actual nested chains. All residuals are nondegenerate; alternating cases use the retained inverse-Gram/Gauss interface.

For dimension d inside an owner of rank b, the first child changes from b to b-d, and the exterior from m-h to m-h+d. Source and sink phases change together: in stage one use `+q_sigma` and `q_F+q_sigma`; in stage two use `-q_sigma` and `q_F-q_sigma`. The completed operator remains `q_F`. Target-front chain replacements preserve rank mass. The strict complex saving is **`5893637/62500000000 = 0.000094298192`**.

| Complete paid inventory | Bit | Complex |
|---|---:|---:|
| m / auxiliary roles | 529 / 28,866 | 576 / 38,506 |
| W | 108,516,254 | 164,065,440 |
| Recursive rank sum | 57,403,754,177 | 94,499,831,360 |
| Positive bins / maximum child | 46 / 528 | 40 / 572 |
| Rank-one copied-output children | 3,136,441 | 4,096,576 |

The complete adjoint has **11,678,073 nonzero coefficients per invocation**, with numerator magnitude at most 42 over denominator 42. Charge 16 scalar operations per term and retain the predecessor allowance:

`G = 2019773888 + 2*2024*11678073*16 = 758385205952`.

Recompute the denominator-21 exact grid, literal precision guard, completed-child height induction and `C1=1` contract. Halving factors 367, 100 and 9 give row coefficient 12,961; **p^27000** supplies degree gap `13989/25 > 0`. All copies, scalar work and wrappers are paid. With `beta=10^-6` and `eta=10^-8`, all 47 assembly constraints and seven margins are strict.

## Contribution sources and prior PRs

| Source | Contributor and retained role |
|---|---|
| Original manuscript/framework | OpenAI, Douglas Colkitt, David Harvey and Joris van der Hoeven: multiplication reduction and analytic context. |
| Round-seven witness | Swapnil Jain: frozen bit word, lifted frames and deferred readouts. |
| #104 | icekylinx: stopped compiler, rational centers, odd grid, precision/row bridge and semantic assembly, retaining the #10/#18/#24/#32/#36 lineage. |
| #108/#111/#113 | Rohan Arun: dual-suffix pair stars and cyclic-strip composition; exact producer bytes and Anthropic Claude disclosure preserved. |
| #62/#110 | Avi Eisenberg: cyclic intervals and independently developed deferred-readout pipeline. |
| #55 | Rohan Gupta / gupt1156: dual-suffix identity credited by the producer. |
| Retained #104 notices | Zhihao Chen, Aurel Prosz, RaD/hipotures, Dominik Scholz, Bortlesboat, dleen, eumemic and other predecessors; Baker-Harman-Pintz prime packing. |

## Proof and attribution

`PROOF.md` gives the physical schedule, paired endpoint gauges, stopped bit recurrence, exact grid and all-size transfer dependencies. `MANIFEST.json` and `SWAPNIL_SOURCE.json` bind sources and inputs; `NOTICE` and imported headers preserve Apache-2.0 and source-specific attribution.

New work used **OpenAI Codex and twenty GPT-6-sol agents at medium reasoning effort**, with independent audits. `EXPERIMENTS.md` records more than twelve tested directions and rejection of a scalar-valid schedule with unpaid frame descents.

This is a **conditional research bound**. Analytic, prime, ordered-affine streaming, restored-row, exact-recovery and fixed-tape interfaces, constructive setup and eventual thresholds remain premises. Bit stage-two reversal and complex complement/time-reversal remain written dependencies. Finite Lean arithmetic does **not** formally verify the complete multiplication theorem.

## Validation

- Rebuilt the pinned complex producer, C++ matcher and physical role word, and all 102 pinned bit-source files.
- Checked every selected owner/residual/target chain and every physical access/root boundary; independently audited alternating frames and phase identities.
- Exact signed-rational dirty-scratch replay restores scratch and gives the required side map. Selected roles' full adjoint supports and frame ranks are cross-bound to the assembly.
- Recomputed complete paid histograms and strict rational moment gaps above `1.1417e-10` (bit) and `1.5791e-13` (complex), G, precision, rows, all 47 constraints and seven margins. Controls reject omitted copies, wrong sinks, degenerate frames and illegal selections.
- **Lean 4.34.1** checks both finite moments and signed assembly. `bit_grid`, `cx_grid` and `signed_assembly` print **empty axiom lists**; analytic enclosure interpretations and all-size transfers remain external.
- Focused package/source checks, staged diff checks and the **complete inherited `make verify` pass**, covering all eleven groups, isolated regressions and historical patch checks.

## Reproduction

```sh
make -C research/partial-complex-stopped verify
make -C research/partial-complex-stopped verify-sources \
  SWAPNIL_SOURCE=/path/to/pinned/round7 PR104_SOURCE=/path/to/pinned/pr104
cd research/partial-complex-stopped/kernel
python3 generate.py
lean KernelNew.lean
```

The README supplies pinned checkouts; CI repeats source and kernel checks.
