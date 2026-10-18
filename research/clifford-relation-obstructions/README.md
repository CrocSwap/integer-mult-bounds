# Exact exclusions for 33 fixed Clifford register words

**Scoped negative result; no new primitive or kappa claim.** For each of the
33 words in `certificates.json.gz`, no choice of three invertible complex
3-by-3 scalar mixing blocks achieves the specified full-rank coset endpoint
with eight paid calls. This is a statement in a formal projective Clifford
group algebra. It does not exclude arbitrary three-block words or solve the
general m=3, W=3, s=8 register problem left open in [PR #288](https://github.com/CrocSwap/integer-mult-bounds/pull/288).

The contribution is a self-contained support/rank/torus checker, explicit
fixed-word inputs, exact refutation traces and a written explanation of the
necessary conditions. Every runtime dependency is in this directory or the
Python standard library. No author-local directory, solver installation,
network access or historical research checkout is needed.

## Reproduce

From the repository root, with Python 3.10 or later:

```sh
python -B -S research/clifford-relation-obstructions/verify.py
```

Expected final JSON contains:

```json
{
  "status": "PASS_FIXED_CLIFFORD_WORD_EXCLUSIONS",
  "counts": {
    "excluded_templates": 33,
    "exact_torus_refutations": 78,
    "noncommuting_relations": 32
  }
}
```

The actual output has additional control counts. The command replays saved
witnesses; it does not rerun the bounded discovery search. It writes no files.
`-O` and `-OO` are explicitly rejected because the checker uses assertions.
`MANIFEST.json` pins source bytes and the decompressed certificate payload;
gzip container bytes are not used to decide mathematical equality.

## Domain and method

There are three streams of formal group-algebra elements, and each target
column must be supported in one left monomial coset of Fourier rank three.
Every unary operation and scalar-block location is fixed by the input word.
Each scalar block ranges over all GL(3,C), including matrices with zero
entries. [PROOF.md](PROOF.md) defines the operators, endpoint and model limits.

For 32 words, the generator prescribed

    U = (I,Q,T), V = (I,P,Q), T = Q^-1 P Q,

so that PQ = QT and Q is also repeated. P and Q do not commute. P and T each
have one paid gate; Q has one or two, with 16 words of each kind. Free
monomial decorations and outside gates vary, keeping the total at eight.
The other word is a commuting-diamond case from the preceding local search.
All 33 literal words are included; no equivalence-class uniqueness is claimed.

The support relaxation encodes nonzero entries, a necessary determinant
matching, selected endpoint frames and the fact that a single nonzero term
cannot cancel. Invertibility gives stronger row, column and rank constraints
for partial-permutation middle-product classes. When a Boolean support survives,
binomial torus equations and exact Laurent determinant identities can refute
it. Only that exact support/frame assignment is then forbidden. The final
Boolean proof closes the fixed word. Twenty-nine words close without an
arithmetic cut; four require the 78 saved torus refutations.

The recorded discovery seed was 521031. The conjugation generator accepted
16 words of each Q cost after 22 and 39 proposals respectively; a 112-gate
representation cap also applied. The final fixed-word search had a 55-second
overall budget, four seconds per word and at most 192 support assignments per
word; it completed all 33 exclusions. These are post-selection research inputs,
not an exhaustive domain or a statistical sample. The seed records provenance;
the literal inputs, rather than a seeded search rerun, define this certificate.

## Validation and independence

The checker compares direct trajectory enumeration with sequential polynomial
propagation. It reconstructs rank clauses from unary products and compares
them with the monomial-based encoding. It replays literal Boolean proof trees,
unimodular integer operations and a direct Leibniz expansion of determinant
products. No SAT or arithmetic solver is trusted for a negative conclusion.

Controls include 33 exact dense skeleton checks, 150 Pauli conjugation
identities, seven paid-gate square identities, four known nine-call solutions,
recovery of their scalar matrices, and an eight-call rejection. A second
eight-call control deliberately survives the Boolean relaxation while its
concrete scalar word fails: Boolean feasibility is not a construction.
Corrupt integer traces, Boolean proofs and learned clauses, missing final
refutations and an unsupported complex-torsion exclusion are rejected.

The two path/rank encodings share the tableau/coset core. The dense Gaussian
matrix implementation independently checks that core on the finite corpus;
it does not establish an all-size representation theorem. The methods were
implemented and checked with substantial AI assistance, not independent human
peer review. There is no Lean proof or novelty claim for the general support,
rank, torus or determinant techniques. See `VALIDATION.json` for the measured
local checks and [NOTICE.md](NOTICE.md) for attribution.

The selected frontier, all supplier sources and `upstream/` are unchanged.
This standalone contribution does not replay or strengthen their compiler,
physical, recursive, precision/tape or analytic assumptions. No bit primitive,
complete exponent invoice or practical multiplication speedup is supplied.
