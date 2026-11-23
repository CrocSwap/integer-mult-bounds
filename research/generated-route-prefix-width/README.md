# Structural all-prefix widths for the generated low/carry producer

Every forward/inverse prefix, including actual ordered-addition and signed-scale lowering, has a structural certificate (d,e): 2^d M is integral and the maximum column-sum norm is at most 2^e. A fixed denominator 2^d and d+e+9 signed work bits suffice. Tensor/guard copy counts do not inflate the certificate. Fixed-base tensor powers have O(log N) widths; arbitrary recipes receive no such claim. See author/PROOF.md and review/REVIEW.md.

```sh
python3 -B scripts/research_package.py --package research/generated-route-prefix-width
python3 -B scripts/check_research_commit.py --package research/generated-route-prefix-width --check-modes
```

Normal and optimized frozen author/independent checks write temporary receipts. Exact sources, metadata and committed-byte gates are included; earlier PR files remain unchanged.

## Open next questions

Bound d,e for the selected compact expression and join this producer to actual quotient/high-payload consumers, route movement and native owner return. Small endpoint matrices cannot justify small prefixes. No complete canonical assumption is removed and selected kappa is unchanged. The exact cocycle and column-denominator identities remain credited to #5841; the emitter and low producer retain their #8092 lineage. New content is the all-prefix grammar induction and fixed-denominator implementation. Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance and separate model-assisted review. Retained author NOTICE and LICENSE provide attribution. No human or proof-kernel acceptance is claimed.
