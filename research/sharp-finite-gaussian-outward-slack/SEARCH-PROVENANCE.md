# Bounded candidate search and proof provenance

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Operator: the exact Sylvester H4/2 fixture from #6619, transferred by explicit
signed permutations to #6509's ideal Gaussian pair. Uniform Euclidean error
cap:1. No random seed is used; candidate generation and order are deterministic.

The originating bounded search tested complete integer balls of radii 3, 4, 5
at the initial threshold sqrt(10)-3. Radii3 and 4 admitted full matchings;
radius 5 did not. It then generated all 39,681 error-one edges at radius 5,
ordered 130 distinct positive norm gaps with 128-bit rational enclosures,
and used eight threshold probes to locate sqrt(21)-sqrt(19). The resulting
full matching and strict-threshold Hall witness are the retained compressed
certificate. Its exact original byte hash and compressed byte hash are in
SOURCES.json. Replaying the optimizer is not a premise of the proof:
the certificate checker verifies the complete universe and both obligations.

The original search and separate direct checker are preserved on the labelled
session recovery branch; this package retains the exact candidate certificate,
two independent lower-bound methods, a full-vertex cross-check, and the
portable direct verifier. Radius 6 and larger radii, other error caps, other
operators, and global sufficiency were not covered by this originating search.
Subsequent research is separate and cannot retrospectively enlarge this claim.

The first symmetry preflight found that the supplied deficit-one witness has
trivial stabilizer and that balls, shells and parity-class unions alone did
not provide the desired compression. A new full-graph alternating cut and
independent orbit-capacity min cut instead found an invariant deficit 32.
The short two-exclusion witness is independently generated without the
original witness list. This is proof reduction for the same finite theorem,
not a larger-radius experiment or a global extrapolation.

Prepared for @CubeJerry with substantial OpenAI Astra/Sol/Luna assistance.
Credit #6619, #2589 and #6509 for the preceding question, finite-sphere
method and Gaussian pair construction. Exact scientific dependencies remain
pinned in SOURCES.json and the proof documents.
