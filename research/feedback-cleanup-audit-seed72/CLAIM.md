# Seed 72: projected-cleanup interface audit

Base: abdc6a7002abdbcd9e21bfc5e1a795784deacfdf. Audit PR543's scalar
interface with interleaved z-gates. Its H1 forbids targets feeding sources
or helpers, and H3 repeats that restriction for B. Investigate replacing
that target-exclusion premise in both places by the weaker condition that the raw word
has no z dependence on targets at its endpoint, while retaining H5.

The deliverable is an exact block-matrix criterion for literal projected
cleanup with target feedback, a smallest three-wire counterexample to
the proposed weakening if one exists, and a complete finite quotient
census rather than a length-limited search. A source-pinned replay of the
selected PR589 word remains a valid baseline. No defect in the stated
H1-H5 lemma, new supplier, precision claim or kappa is presumed.

Alternatives: T37 integrality/equality audit was rejected because PR992
and PR1000 already cover it; packed coefficient radix audit was deferred
because PR950 already binds its radix to the supplied coefficients.
Fresh Curiosity Bot H1/feedback and target-feedback searches precede this
claim. PR982 output borrowing and PR1057 recursive additive echoes have
different interfaces; overlap is documented in the completed package.

Prepared for @woklerx with substantial OpenAI Codex assistance; Apache-2.0.
