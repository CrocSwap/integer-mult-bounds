# General-coset-bound addendum

Reviewed final Worker C proof SHA256
`1fad3fa92b26bcd290b179ee3b714c3d25017bc63fa2439124e2e10ddb2c374c`,
including the general edge/coset bound and its all-pool corollary. The preceding
independent review and finite checks remain applicable. Jerry Chen / @CubeJerry
with substantial OpenAI Codex assistance; Apache-2.0.

The extension is sound. If P has dimension r and contains exactly e matrix
units, those units are independent, so their span P0 has dimension e. Let E
be the coordinate span of all their endpoints. The zero coset's projectors
have image in E, and the complete edge fibers give E contained in V. Within
each nonzero coset, two independent images modulo E would force, by the
already reviewed quotient observation, a single-edge pattern whose endpoints
lie outside E. This contradicts the definition using **every** edge in P.
Thus each of the `2^(r-e)-1` nonzero cosets contributes at most one quotient
dimension, proving

`dim V <= dim E + 2^(r-e)-1 <= 2e + 2^(r-e)-1`.

The last expression is convex in e on `[0,r]`, so it is at most the larger
endpoint value, `max(2^r-1,2r)`. This also covers r=e=0. For r=3 it gives
the stated complete-pool table: e=0 at most seven; e=1 at most five; e=2
at most five; e=3 at most six total, with the separate graph theorem giving
constituents of dimension at most four in the last case.

The proof correctly limits the unique irreducible five-dimensional normal
form to the e=2 case. Neither sharpness in e=0/e=1 nor a rank-saving word
follows from the general bound. These are analytic consequences of the
arbitrary-width quotient observation, not extrapolations from finite tests.

The final wording explicitly defines E as the coordinate span of endpoints of
all e edges. This clarifies exactly the hypothesis used in this review; no
mathematical conclusion changes.
