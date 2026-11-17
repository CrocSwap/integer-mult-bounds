# Exact determinant images for square-zero local tensors

This contribution was produced by Nick Petalas. Apache-2.0.

Scoped written algebraic proof with exact finite corroboration. Let K=F_q
and let A=K plus J be a commutative unital local K-algebra with residue K,
J squared zero, and d=dim_K J>=2. Put n=d+1 and g=gcd(n,q-1). For its
multiplication tensor in A* tensor A* tensor A, with the ordinary covariant
three-factor action, the exact stabilizer determinant image is

```text
Delta = {(u,v,w) in (K*)^3 : uw and vw are nth powers in K*}.
```

Equivalently, `(uw)^((q-1)/g)=(vw)^((q-1)/g)=1`. Its order is
`(q-1)^3/g^2`, and its general-linear orbit splits into exactly `g^2`
special-linear orbits. Every allowed determinant triple has an explicit
attaining stabilizer, with arbitrary radical coordinates in its two units.

At q=5 and n=4 the image is `{(c,c,c^-1):c in F5*}` and there are 16
special-linear orbits. A product-one condition alone gives the wrong image.
[PROOF.md](PROOF.md) proves the statements over every finite field and all
d>=2, including characteristic two and extension fields.

## What this adds

Ali Romman's [PR #5540](https://github.com/CrocSwap/integer-mult-bounds/pull/5540)
reconstructs commutative multiplication from tensors over prime fields. It
leaves recovered-algebra comparison and determinant-character interfaces
open. This supplies the exact character subgroup for its non-Gorenstein
square-zero local class. The reconstruction theorem is cited, not audited.

The etale, Frobenius-truncated and equal-cutoff rectangular determinant
packages concern different algebra classes. No scientific executable,
inventory, count or new theorem from those packages is a step of this proof.
Unital isotopy normalization, cyclicity of finite-field unit groups and the
normal-subgroup orbit argument are classical. The contribution is this exact
assembly, its two equations, constructive witnesses and bounded verifier.
Global literature priority is unclaimed.

This changes the formal-interface-lemma card to an algebraic side result.
It does not meet that card's proof-assistant gate or discharge a selected
supplier assumption. The canonical base is
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8, selected
#7000 with conditional kappa .00363005817. The baseline binding check passed.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19541747)
and SOURCES.json record the source interface and provenance.

## Exact finite evidence

The new verifier uses only its own arithmetic and Python's standard library.
It writes no files and emits a generated JSON receipt with SHA256 hashes of
all seven package files. Checks remain active under optimized Python.

- All 42 contexts with q in {2,3,4,5,7,8,11} and n=3,...,8. Every allowed
  determinant triple has a literal full tensor-action witness: 5,448 total.
  All 4,506 excluded triples reject. Independently enumerated cosets of the
  attained subgroup give the claimed special-linear orbit count.
- Complete raw automorphism domains of 512, 65,536 and 19,683 matrices at
  (q,n)=(2,3),(2,4),(3,3), accepting 6, 168 and 48 automorphisms. These tests
  check invertibility, the unit and every basis product directly.
- A separate complete GL3(F2)^2 domain contains 28,224 input-map pairs.
  The unit forces the only possible output map; exactly 96 pairs give
  invertible autotopisms. Their full covariant tensor action also passes.
- All 833 elements of seven specified small algebras check the literal
  multiplication determinant; 680 are units. Field checks cover 2,410
  triples. Fifteen controls reject changed tensor factors, the wrong input
  action convention, omitted subgroup restrictions and invalid domains.

The exhaustive claims apply only to these named finite domains. The
all-field and all-dimension conclusions rely on the written proof.

## Reproduce

From the repository root with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/squarezero-tensor-characters/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/squarezero-tensor-characters/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/squarezero-tensor-characters
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/squarezero-tensor-characters --check-source-history --check-modes
```

Another machine may substitute its CPython 3.12 path. The direct marker is
`PASS_SQUAREZERO_TENSOR_CHARACTERS`; registered replay also returns
`PASS_REGISTERED_RESEARCH_PACKAGE`. The direct commands need no Git or
predecessor files. Provenance checks require the recorded repository history.

## Limits and engineering

There is no arbitrary-tensor recognizer, supplied-table radical extractor or
special-linear transporter implementation here. The witness builder accepts
canonical multiplication charts on the bounded field/dimension domain of
the verifier. The proof gives the image on the promised general-linear
orbit; the group-theoretic orbit count does not supply an algorithm to find
that chart. Nonsplit residue fields, higher radical products and semilinear
equivalence are outside the result.

The code has no recursion or external processes. Matrix loops have dimension
at most eight, field loops have order at most eleven, exponentiation has at
most 64 steps, and raw matrix enumeration rejects domains larger than 70,000.
Each function is below 60 physical lines. Explicit ValueError checks cover
all mathematical verification conditions, including optimized execution.
Internal matrix helpers receive only constructed bounded fixtures.

Power-of-Ten rule 3 has a bounded managed-runtime deviation: Python allocates
matrix rows, integers and sets during verification. The largest determinant
ambient group has 1,000 triples. Cosets partition that group; at most 1,000
triples persist across the distinct stored cosets, with one further transient
coset of at most 1,000 entries. The full GL3(F2) list stores 168 matrices;
larger raw domains stream one matrix at a time. The lifetime ends at each
finite check. No external input can enlarge these fixtures. A future general
API must set its own resource contract. Rule 9's exception is the fixed list
of local rejection callbacks; none escapes its immediate check. Warning-strict
normal/optimized execution and AST compilation provide the available Python
diagnostics; no claim of exhaustive static analysis is made.

There is no physical coefficient preparation, native program, dirty-state
restoration tariff, precision/tape implementation, complete paid supplier,
new kappa or selected-frontier change. No selected cold replay, Lean or Docker
run is needed for this isolated algebraic statement. Independent human and
formal proof-kernel review are unclaimed.

## Open next questions

1. Build a bounded supplied-table extractor for this exact class, then compose
   it with #5540's recovered-table interface and an explicit special-linear
   transporter. Begin with the radical and scalar-residue checks. No such
   program is supplied here.
2. Determine the determinant image for square-zero local algebras with a
   nonsplit residue field. Start with the determinant of the induced
   semilinear radical map; the present scalar-residue calculation does not
   justify dropping that contribution.
3. Find a named native producer/consumer that uses one of these equivalences,
   then charge coefficient preparation, movement, precision and restoration.
   An abstract special-linear orbit count supplies none of those costs.

Credit Ali Romman for #5540 and its retained apoursh, Nick Petalas, David Ganz
and tensor/algebra reconstruction lineage. Classical algebra and finite-field
facts retain their usual credit. Predecessor source files are unchanged.
