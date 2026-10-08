## Conditional result

The RaD alternating complete-pair DAG construction gives the following exact conditional assembly bound for integer multiplication in the inherited fixed finite-alphabet multitape framework:

\[
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\boxed{\kappa=\frac{1008542031}{25\cdot10^{12}}
=4.034168124\times10^{-5}>2^{-15}}.
\]

This is **4.762607006% above the PR #37 value** \(\kappa=3.850771033\times10^{-5}\), comparing asymptotic exponent savings rather than practical runtimes.

### New contribution

We change the h23/h25 scalar computation DAGs by using alternating complete-pair addition-tree structures and independently recompute the retained-controller allocations, their full physical role counts and the resulting native child-width distributions.

- h23: **36,685 physical roles**.
- h25: **48,479 physical roles**.
- The resulting assembly uses the credited copied-center schedule and reversed data-corner geometry with all paid endpoint corrections.
- Exact rational certificates recompute the bit/complex characteristics, semantic precision and row-stock costs, **47 strict assembly conditions and seven final margins**.

An independently checked companion association construction also supports \(\kappa=3946432011/10^{14}=3.946432011\times10^{-5}\); it is included for independent comparison, not presented as the main result.

### Verification boundary

**Exact full conditional arithmetic for \(\kappa=4.034168124\times10^{-5}\) is certified.** The separately required independent full-size compiled producer/frame/dirty-state acceptance of this alternating construction was **not yet complete at the pinned checkpoint**. The portable arithmetic verifier does not replace that check. This is therefore a conditional research submission with an explicit outstanding finite proof obligation; it is not formal verification, an unconditional theorem or a claim of global optimality. Inherited common-rational-basis, fixed-tape, setup and eventual-constant conditions remain explicit.

### Reproduction

The self-contained standard-library arithmetic inputs and certificates are in `research/rad-left-producer/` in this PR. From the repository root, with Python 3.11+:

```bash
python3 research/rad-left-producer/code/exact_composition.py \
  --axes research/rad-left-producer/fixtures/axes-alternating23-alternating25.json \
  --phase research/rad-left-producer/fixtures/phase-pr36.json \
  --assembly research/rad-left-producer/code/adopted_pr37_balanced_assembly.py \
  --output /tmp/rad-alternating-composition.json
```

The original research source, full finite-check evidence, regeneration protocols, independent review notes and the exact checkpoint are preserved in [RaD commit 7e488e6b](https://github.com/hipotures/rad/tree/7e488e6b25dc1713c1f41baaf1cefbf677507cf3/research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008). The research campaign continues on its original deadline; later separately verified evidence can be added to this PR.

### Attribution

Foundational multiplication result and compact-control framework: **OpenAI** and **Douglas Colkitt**. **icekylinx** contributed the copied retained-center schedule, physical producers and compiler (PR #36 and predecessors). **James Chang (jamesyc)** contributed the reversed boundary geometry (PR #34); **Rohan Arun** contributed the copied reversed data profile and corresponding assembly (PR #37). **Zhihao Chen (jacklightChen)** and earlier RaD work (PR #20) contributed semantic, routing and bulk interfaces, with the preceding authors credited in the source lineage.

The separate RaD/hipotures contribution is the changed alternating h23/h25 DAG design, selected retained-controller allocations, independent research checks and recomputed exact conditional exponent. Applicable Apache-2.0 source notices and credits remain preserved. Developed with substantial Codex/OpenAI assistance.