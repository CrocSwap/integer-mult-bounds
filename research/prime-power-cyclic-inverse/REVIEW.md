# Independent mathematical review

Verdict: PASS. This is a useful scoped analytic contribution worth submitting.
The review was performed with substantial OpenAI Codex assistance by a
separate agent. It is not maintainer acceptance or a formal proof in Lean.

The reviewer first derived the integral-nonunit and determinant arguments
without producer imports, then reviewed the final proof and both checkers.
The root argument covers roots outside Q(u). The prime-power reduction,
dyadic characteristic, paired embeddings, cofactor bounds, and Fourier
normalization are correct. The bound

    delta_r = (2r(r-1) (2^r-1)^((r-1)phi(r)-1))^-1

holds on the entire unit circle for every primitive prime-power root.
The induced infinity-norm bound is uniform in cyclic length, integer step,
and scalar phase. The finite-product and unit-diagonal-gauge corollaries
are correct. Radix two has its separate inverse bound two.

The independent SymPy engine checked nine cases: (3,1), (4,1), (5,2),
(7,1), (8,1), (8,3), (9,1), (11,1), and (11,4). All eight primary EXPECTED
determinants and full norms agree exactly with independent calculations.
All 36 polynomial cyclic inverse products at lengths 1,2,4,8 equal one.
The unit-root and missing-conjugation controls detect their intended faults.
Both public checkers use explicit checks that remain active under -O.
The written proof establishes the uniform claims; the finite checks test
the identities and arithmetic implementations within their stated scope.

The contribution replaces a length-dependent algebraic-norm estimate with
a circle and inverse bound having logarithm O(r^2 phi(r)). Fixed-radix
compactness and prior finite invertibility do not supply that growth bound.
This removes a conditioning question from the proposed cyclic route.
It supplies no paid preparation, rounding, restoration, operation count,
or tape program, and proves no complete growing-family precision guard.
No integer kappa, complex b, or BIT c improvement follows. This review
makes no claim of literature priority or exhaustive live-PR novelty.

Reviewed package SHA256 values:

    PROOF.md: 2b8056c88e66f692f407450fff0414d41bcd09db8597be22e274a6c3dc20eb9e
    verify.py: 40e5e18cbd98d39ba6d0bb036778ccacc077dff009099a54b9c8f441af5d6a56
    independent_verify.py: 515d60fbbb28c025251b5a2929231b4b6124dabe357b8526fdb93c1456c847ce
    EXPECTED.json: 2c4ab855129670053f4f39ee14269cc9b5bda015eab71d5a226dd0d395740ebd

README, NOTICE, and SOURCE were reviewed for scope and assistance disclosure.
External source and live-frontier checks remain separate author checks.
