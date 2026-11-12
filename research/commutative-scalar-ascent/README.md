# Lift recovered prime-field tensors to extension-field algebras

This constructive proof and certificate adapter were produced by Nick Petalas.
Apache-2.0.

Let K/F be a finite field extension and t a K-bilinear square tensor. Then t
is K-isotopic to multiplication in a commutative associative unital K-algebra
if and only if its restriction to F is F-isotopic to multiplication in a
commutative associative unital F-algebra. The explicit certificate bridge is

```text
source unit e;  u=P e;  v=Q e
R_v(x)=t(x,v);  L_u(y)=t(u,y)
mu(x,y)=t(R_v^(-1)x,L_u^(-1)y)
K-certificate: table(mu), unit=t(u,v), U=R_v^(-1), V=L_u^(-1), W=I
```

The source maps P,Q,S can be arbitrary F-linear maps. They do not need to be
K-linear. Both displayed slices are invertible K-linear maps, and mu is the
required K-algebra product. [PROOF.md](PROOF.md) proves the quantified
statement and explains both necessary boundary restrictions.

Claim type: scoped constructive proof with exact finite corroboration.
The contribution is the explicit scalar-restriction certificate adapter and
its bounded implementation. It is not a new general recognition theorem.
No kappa, supplier admission or selected-frontier change is claimed.

## Before and after

Ali Romman's [#5540](https://github.com/CrocSwap/integer-mult-bounds/pull/5540)
recovers arbitrary commutative unital multiplication from prime-field tensors
and leaves an extension-field input layer open. The adapter consumes that
certificate shape and returns a K-table and K-linear factor maps without
implementing an extension-field nucleus decomposition. It handles products,
non-Gorenstein algebras and nonsplit residue fields under the same general
commutative contract.

Ali Romman's [#5637](https://github.com/CrocSwap/integer-mult-bounds/pull/5637)
already supplies a direct extension-field implementation for the local
characteristic-power truncated-polynomial class. Nick Petalas's older
[#6464](https://github.com/CrocSwap/integer-mult-bounds/pull/6464) already proves
general recognition over any supplied exact field. Those results are credited
premises/background, not replay targets or claimed new coverage. This package
uses neither predecessor implementation. It supplies the explicit restriction
bridge to the existing prime-field interface.

Restriction does not preserve every class label: Res(F4) is a field over F2,
whereas F2[x]/x^2 is not. The adapter must consume a general commutative
recovery certificate. Nor can an arbitrary F-bilinear tensor be passed off as
a K-bilinear input. The semilinear map x^2 y over F4 is a boundary witness.

## Reproduce

From the repository root, CPython 3.12 and the standard library suffice:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/commutative-scalar-ascent/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/commutative-scalar-ascent/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/commutative-scalar-ascent
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/commutative-scalar-ascent --check-source-history
```

Another CPython 3.12 path can replace the recorded interpreter. The direct
marker is `PASS_COMMUTATIVE_SCALAR_ASCENT`. The program emits a generated
receipt binding all eight package files by SHA256 and the complete ordered
fixture output by a deterministic digest. It writes nothing. Both registered
commands run the same checks with runtime requirements enabled under `-O`.

`ascent.py` exports `ascend(tensor, certificate, field)`. Tensor entries are
`t[i][j][k]`. The input certificate contains `table`, `U`, `V`, `W` in the
restricted prime-field coordinates, with each original K-coordinate expanded
into consecutive low-to-high polynomial coefficients. Its maps use columns
as basis images and satisfy `Res(t)(U a,V b)=W table(a,b)`. The adapter checks
the supplied certificate and returns the corresponding K-certificate plus
`unit`. Invalid certificates raise `ValueError`. It never invokes a recognizer.

## Evidence

Local normal and optimized replay passes 78 constructed certificates, 684
K-basis products, 75 non-K-linear recovery bases, 16,930 field-law triples,
ten rejecting controls and two boundary witnesses. Both registered checks
and the package metadata runner pass on CPython 3.12.15. Generated normal
and optimized reports agree exactly.

The verifier constructs its own tensors and source certificates. It exercises
F4, F8, F9 and F25, nilpotent and non-Gorenstein algebras, direct products,
nonsplit quadratic residue fields, and dual-number extensions of those
nonsplit fields. Three deterministic independent input/output presentations
are used for each algebra. Prime-field recovery bases are changed separately,
including bases that do not commute with multiplication by the field
coordinate. Returned tables and units are compared with the original
fixture's explicit output-space algebra, independently of the adapter's
slice formula.

It also checks every field-law triple in the four finite arithmetic domains.
Named controls reject singular maps, an invertible but wrong output map,
noncanonical entries, missing keys, unsupported fields, wrong dimensions,
nonassociative multiplication and noncommutative multiplication. Two explicit
boundary witnesses cover K-bilinearity and the class-recognizer restriction.
The emitted receipt enumerates all counts. These finite checks corroborate
the written proof; they are not a complete tensor census or a replay of
another contributor's numbers.

## Scope, limits and credit

This is a changed `formal-interface-lemma` scope at canonical main
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8. It is an
algebraic interface side result, with no proof-assistant acceptance. The
source-binding baseline command passed for selected #7000. No selected
scientific replay was run. Historical source text and the task card are
pinned as provenance in SOURCES.json, rather than imported at runtime.

The reference accepts the explicitly listed polynomial fields in algebra.py,
with q at most 25 and restricted dimension dn at most 12. These are executable
capacities, not bounds on the theorem. It consumes a certificate; it does not
implement a new end-to-end recognizer or classify the recovered K-algebra.
No special-linear label, automorphism count, rational bit-complexity bound or
runtime speedup is claimed. There is no native implementation, physical
coefficient preparation, dirty restoration program, paid caller, compiler
closure, precision/tape admission or complete multiplication theorem. All
five selected assumptions remain. Independent human and formal proof-kernel
review are unclaimed.

Credit Ali Romman for #5540's question and recovery interface, #5525 and
#5637; apoursh for #5502; Nick Petalas for #5252; and David Ganz and the
retained tensor/algebra lineage. Restriction of scalars, exact elimination
and unital isotope normalization are classical. No predecessor code is copied.
The new bridge, bounded reference, proof and fixture checks were produced by
Nick Petalas. The #6464 cyclic-module construction is background and is not
used as a step.

Live PR titles/bodies, recent handoffs, batch reservations, merged searches
and all-main README searches were checked before the
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19572847).
The cached search reports its own coverage limits, including omitted sparse
notes. Search absence does not prove novelty. Related open work is recorded
in the PR body; no competing result is audited here.

## Open next questions

1. Can a public caller connect an actual #5540 recovery certificate to this
   adapter with a general exact finite-field input contract? Start with one
   source-owned output certificate and its precise coordinate basis. This
   package supplies a bounded adapter and new fixtures, not that integration.
2. Which prescribed K-algebra class or determinant labels can be reconstructed
   from the restricted F-algebra together with its embedded scalar action?
   Start with one nonsplit local component. Ignoring that scalar action is
   invalid; no classification or special-linear label transfer is supplied.
3. Can one recovered K-table be used in an affordable native caller? First
   charge all coefficient maps, workspace, returns and restoration. No such
   physical cost contract is supplied by recognition or this bridge.

## Verifier engineering bounds

Every dimension is bounded by 12 and every supported field has at most 25
values. All loops range over those explicit finite domains or fixed fixture
lists. There is no recursion, subprocess, runtime code generation or write.
Functions remain below sixty physical lines. Internal arithmetic helpers trust
representations validated at the public tensor, matrix and certificate
boundaries. Runtime requirements use explicit exceptions and remain enabled
under optimization. Warning-strict normal/optimized execution and syntax
inspection provide diagnostics; no separate static analyzer is claimed.

Power of Ten rule 3 deviation: CPython allocates integers, lists and tuples
throughout exact arithmetic. Live tensors have at most 12^3 coefficients,
linear systems at most 12^2 rows and 13 columns, and field tables at most
25^2 entries. Fixtures execute sequentially. Revisit these bounds before
accepting larger dimensions or a production caller. Rules 8 and 9 retain
ordinary Python module loading from two fixed siblings and a fixed list of
negative-control lambdas; no arbitrary imported target or callback is accepted.
