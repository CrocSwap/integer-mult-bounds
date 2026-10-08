# Exact parameter refinement of pinned PR60

The unchanged PR60 construction supports the freshly certified numerical
witness

    kappa = 59556416720821 / 1250000000000000000

This exceeds PR60's published `4764513337/10^14` and the scoped ceiling
computed using its old bit saving. The new backoff is explicitly `h=10^-18`.
This is a small parameter refinement, not a new compiler, scalar graph,
matrix tensor rank, practical speedup or unconditional theorem.

Fresh verification covers the rational moment, all 47 strict assembly
inequalities, seven margins, and the eventual-bound arithmetic. The source
certificate and arithmetic modules are hash-checked before evaluation.
The unchanged PR60 graph, words, dirty bases, CPP/CRT profiles and data sweep
are **inherited from its reported validation and were not rerun here**. Its
announcement states that focused verification passed while the full upstream
repository verification was running. Separate Lean artifacts have their
explicit arithmetic scope; this Python checker does not compile those files.

Python 3.11+ standard library and Git suffice:

```sh
git clone https://github.com/chafreaky/integer-mult-bounds.git upstream
git -C upstream checkout --detach e7a492dd8bee4e6f574ced784a62af2ce735edc4
python3 verify_refinement.py --upstream upstream
```

The external pinned checkout is required. No dependency download or inherited
physical construction replay occurs. `arithmetic.json` supplies exact values
and source hashes; `arithmetic-verification.json` records the executed result.

At the fine grid, a next-point upper enclosure above one shows that this
enclosure does not certify that point. It does not exclude actual feasibility
or prove global optimality. The compared predecessor is
[PR60](https://github.com/CrocSwap/integer-mult-bounds/pull/60), Chafik
Boukhalfa's retired-slot priority refinement of the PR58 composition. Eumemic's
joint frame compiler, Rohan Gupta's dual-suffix layout, Avi Eisenberg's producer
framework, and every retained contributor and license remain credited.
