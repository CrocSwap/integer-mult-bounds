# Deferred readouts on the cyclic-strip complex network

Conditional κ = 469537/5000000000 = **9.39074 × 10^-5** — **+9.39% over PR #110** (429239/5·10^9)
and +9.47% over the cyclic-strips witness (1715630240171/2·10^16).

PR #110 showed that, under PR #104's one-child-per-residual rule, deferred readouts pay on both stopped
networks; its binding side was the complex network built on PR #104's unchanged h = 24 DAG (44,918 roles).
This witness runs **exactly PR #110's deferral pipeline** (maximum carrier matching under the inherited
adjacency, explicit role compile, lifted binary frames, deferred readouts, replay with arbitrary scratch,
exact F2 frame checks) on a smaller complex DAG:

- PairedTriple strips use **cyclic interval strips** (PR #62's construction), and pair stars use the
  **dual-suffix** identity of PR #108 (from PR #55), with PR #104's coordinate order — `cyclic_producer.py`,
  identical to `research/cyclic-strips-both-axes/producer.py` on the PR #108→cyclic-strips branch.

| h = 24 complex network | PR #110 | this |
|---|---:|---:|
| matched carriers | 8,966 | 37,802 |
| roles R | 44,918 | **38,506** |
| deferred roles | 8,893 | 5,887 |
| complex saving (binding) | 214657/2.5·10^9 = 8.58628e-5 | **939253/10^10 = 9.39253e-5** |
| κ | 8.58478e-5 | **9.39074e-5** |

The bit side is PR #110's unchanged one-child profile of Swapnil Jain's round-seven deferred word
(`bit-profile.json`, stopped saving 1.24019e-4), so the complex side still binds.

## Reproduce

```sh
python3 research/deferred-cyclic/complex_deferred.py      # ~2 min; writes complex-profile.json
python3 research/deferred-cyclic/bit_round7.py DIR        # optional; as in PR #110 (Swapnil's two files)
python3 research/deferred-cyclic/certificate.py           # exact moments, next-grid rejections, 47 constraints, kappa
```

`certificate.py` rejects the next grid point of the coarse bit saving, the complex saving and κ, checks
all 47 strict constraints and seven margins, and requires κ above PR #110 and the cyclic-strips witness.
Scope, assumptions and the stated-but-not-machine-checked steps are exactly those of PR #110 (see PROOF.md);
the only new input is the complex DAG, whose scalar supports, centers, rational scatter and frame nesting
are asserted by its producer and re-checked by the deferral pipeline.

Credit: Avi Eisenberg (PR #110 deferral on stopped networks, PR #62 interval strips), Swapnil Jain (deferred
readouts, round-seven word), icekylinx (PR #104), the PR #55 dual-suffix authors, PR #107–#109, and all
predecessors credited in PR #104's NOTICE/SOURCES. Composition by Rohan Arun with Anthropic Claude assistance.


### Expanded scalar-work charge (PR114 accounting correction)

The initial inherited PR110 certificate counted the original addition DAG when forming its scalar guard. Deferred readouts expand into additional operations, so that charge was insufficiently justified. Following eumemic's PR114, the certificate now conservatively charges the literal expanded forward, inverse and reflected words. A local row has at most c+R mixer operations, R leaf copies, and R+q readouts with at most h center and v direct coefficients each. The bound 8(c+2R+(R+q)v(h+1)+h²+h+1), applied to both sets of v rows plus the data term, covers these operations and copies. It raises G from 2,019,773,888 to 76,407,506,746,560. Precision constants and eventual cutoffs increase; the physical profiles, strict savings and κ=9.39074e-5 are unchanged. All 47 inequalities, seven margins and next-grid exclusions are recertified with the enlarged guard. Credit: eumemic, PR114 commit51cd8934128be37830981ca391d3d6fd28b0fce8, OpenAI Codex assistance.

The already-running full suite tests the preceding fingerprint-repaired head. Its receipt must identify that head and a separate corrected-certificate replay; it must not represent the old certificate as including this correction.
