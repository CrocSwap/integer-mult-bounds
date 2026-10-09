# Five-level finite bootstrap on the PR211 cascade-frame supplier

## Result

Starting from open PR211's exact conditional exponent `683847872495777/10^18`, this follow-up adds two fixed stopped-leaf levels and obtains

```text
kappa = 683847872497761/10^18
      = 0.000683847872497761.
```

The exact gain over PR211 is `1984/10^18`. The fifth level adds the last `10^-18` grid step over the four-level version. The bit supplier still binds. The regenerated certificate stores all 47 exact positive assembly margins, and the independent audit rejects the adjacent final grid point.

## Mechanism and inherited construction

The finite supplier and physical frames are PR211's frozen cascade-optimized PR200 bit word: 6,191 changed operation frames, the same terminal-modified word, 1,760 compensated aliases, completed banks, and PR193 complex supplier. We do not overwrite that layout with an older frame candidate. In an explicit comparison, PR211 already uses the same first-frame minimum joins at all 17 pairs found in our prior local search, while its second frames are smaller than that earlier candidate. The stronger cascade schedule is retained intact.

Let `c` be the newly priced packed bit saving and let `a_0` be the fully paid ordinary saving from the admitted PR200 word. Five fixed recurrences use

```text
a_j = (1-c)c + c a_(j-1),  j=1,2,3,4,5.
```

The exact rational verifier checks every recurrence, `a_(j-1) < a_j < c < 1-a_j`, the two-supplier paid moments, and the unchanged 47-constraint assembly with `eta=beta=10^-24` and weakening `10^-30`. The finite depth is five, independent of input size. For the fixed suppliers, the exact assembly ceiling at the unattained limit `a=c` has the same `10^-18` grid floor as the fifth level; since every finite `a_j<c` and the ceiling is increasing, no deeper fixed level can raise the reported grid value. The limiting value is only an upper-bound check, not an input supplier.

## Reproduction and validation

```sh
python -B research/cascade-frames-bit/verify.py \
  --complex-root .dependencies/pr193 \
  --bit-root .dependencies/pr200 \
  --full
```

The existing workflow checks out the pinned PR193 and PR200 sources, reruns the PR193 complex verifier, re-admits all PR200 frames and terminal columns, rebuilds banks, recomputes the exact certificate and independent moment audit, and compares the regenerated certificate byte for byte. The root Verify workflow also covers the repository Makefile matrix and formal jobs.

The local exact-arithmetic replay used PR211's frozen admitted physical record and the byte-pinned PR193 assembly/certificate. It produced five levels, 47 positive exact assembly margins, an independent moment audit PASS, and the exact limiting-grid upper bound. At Draft creation, this follow-up's GitHub Actions runs have not yet completed; the submitted branch reruns the complete frame/source verification.

## Conditions and limits

The conclusion remains conditional on the inherited all-width compiler, completed weighted/restored selector, routing, prime supply, precision/recovery, fixed analytic tape, and finite bridge hypotheses. PR211's cascade search is heuristic and does not prove a frame optimum. Finite verification does not prove the inherited all-size interfaces or the multiplication theorem unconditionally; this adds no Lean proof and makes no practical-speedup claim.

## Attribution

The cascade frame layout and its verification belong to PR211 (Rohan Arun, with Anthropic Claude assistance). The bit word/checkers are from PR200, banks from PR197, complex supplier from PR193, and finite-composition work from PR185/187/210; their licenses and source notices are retained. The fifth-level arithmetic extension and independent audit were prepared with substantial OpenAI Codex assistance. No inherited construction is claimed as new or exclusive work.
