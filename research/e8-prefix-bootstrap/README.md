# Finite bootstrap on the PR390 prefix-restoration supplier

Conditional **kappa = 0.001000220224856110** (`100022022485611/10^17`), exceeding PR390 by `983291/(5*10^17)` = 1.966582e-12. This is a small finite-bootstrap and arithmetic refinement. The target-prefix rewrites, dirty preconditioning, early helper restoration, heterogeneous endpoint banks and bit construction are entirely PR390's contribution.

Run `python -B research/e8-prefix-bootstrap/verify.py /fresh/output`. Install the unchanged `research/e8-prefix-restoration/requirements.txt` and provide C++17 plus Boost headers as PR390 requires. The verifier checks every upstream byte, reruns all twelve PR390 stages, then derives this witness. The upstream package is retained unchanged in this branch; no network or saved PASS receipts are used by verification.

Two exact independent moment engines enclose the same complex paid root between 0.001001221667017025386926 and 0.001001221667017025386927, retaining the entire positive 10^-16 fallback. Six fixed ordinary-bootstrap levels with beta=eta=10^-18 produce the witness. All 47 strict outer constraints, six invalid-parameter/cutoff controls, and the next-grid ceiling are checked. The expected profile is an assertion against the freshly emitted physical profile, not a substitute for that emission.

This reuses our PR387 fixed-depth argument from the reviewed PR185 mechanism. The prior review covered three levels; the six-level conditional extension is stated in PROOF.md. All PR390 interfaces remain assumptions. No new circuit, unconditional theorem, complete Lean proof or runtime speedup is claimed.
