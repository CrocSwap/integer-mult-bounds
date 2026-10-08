# Contiguous data blocks at (47,45)

The conditional witness is **κ = 1638103206/10^14 = 1.638103206e-5**,
using bit saving `1638156876/10^14`, beta `1/20` and headroom `1e-12`.
It composes the freshly rebuilt (47,45) producers with Rohan Arun's PR31
rank-partition method. The data profile becomes **11 singletons +43+37+1933**.

The exact certificate contains 1,569 weight-independent zero-minor proofs,
checked via 3,138 integer ranks, and 91 nonzero ordered rational pivots in
the actual normalized projector family. The same-basis finite-product and
ordered-affine arguments are written in the proof. The bit moment gap
exceeds `1e-15` and final absorption gap exceeds `5.9e-15`. All 47 strict
constraints and seven margins pass. The complex leaf parameter must change:
beta=1/10 is rejected because its leaf saving is below the new bit saving.
Beta=1/20 leaves saving `17.1e-6`. Eventual cutoffs are recomputed, with the
inherited additional analytic and fixed-setup thresholds explicitly retained.

```sh
make two-stage-dimensions-producer
make two-stage-corners-47-regenerate
make two-stage-corners-47-check
make verify
```

The generator reconstructs the identity certificate; the independent auditor
checks it without trusting the search oracle. SOURCE.json pins and credits
PR31's original modules and records the dimension adaptations. The composed
verifier replays the previous dimension certificate and retains every PR29
source pin. `patches/two-stage-corners-47.patch` replaces the pinned PR29
manuscript with the composed proof; apply it independently of the earlier
dimension-only patch, with both new proof sources available. No PDF is made.

The inherited rank-one copy corrections, every physical role, coefficient
charge, semantic C1=1 and product row stock `p^47000` remain unchanged.
This is conditional research, not formal verification or a practical runtime
claim. Failure of the next moment grid point is failure of a sufficient
enclosure, not a proof of global optimality.

Credit Rohan Arun for PR31's identities, search/audit, moment, assembly and
cutoff modules; Zhihao Chen for PR29 and PR21/23; Aurel Prosz (Paureel) and
Swapnil Jain for the two-stage topology; icekylinx for the producer/basis;
RaD/hipotures and all preceding authors retained in NOTICE. Dominik Scholz,
with substantial Anthropic Claude Opus 5.5 and OpenAI GPT-6 Astra/Codex
assistance, contributes the dimension specialization, regenerated evidence,
parameter choice and composition. Original licenses and attribution remain.
