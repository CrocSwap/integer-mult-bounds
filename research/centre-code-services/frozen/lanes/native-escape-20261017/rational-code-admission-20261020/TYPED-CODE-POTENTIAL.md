# Rational boundary codes with a bounded odd height

The exact common-grid method does not require every completed child
matrix to be dyadic in its physical coordinates. A child can return a
rational boundary code if its complete typed endpoint is proved and the
caller uses that exact type. Codes that match across completed calls
cancel algebraically. Their odd height is then a boundary cost, rather
than a cost for every completed sibling.

This theorem concerns exact arithmetic and complete operator identities.
It does not grant a physical code change, a native source read, or a
helper lease. It does not show that the current supplier's codes match.
The actual caller must prove those identities on every physical role.

## Whole-state types

Use R0=Z[i,1/2]. At a cut, let u contain all semantic values. This
includes computational data, arbitrary borrowed data, and any live
numeric work values. A type is an invertible rational linear operator
C. The stored physical state is C u.

A completed typed operation from C_in to C_out has physical matrix

```text
M = C_out A C_in^-1,
```

where A is its required semantic endpoint. The identity must hold on
every input column. In particular, it must hold on arbitrary borrowed
columns. Restoring a borrowed value, applying its required native
endpoint, and returning it in a changed code are different contracts.
The caller must use the contract that was actually proved.

Suppose a sequence has types C_0,...,C_m and dyadic semantic matrices
A_1,...,A_m. Then

```text
M_m ... M_1 C_0 = C_m A_m ... A_1.
```

All adjacent C_j^-1 C_j products cancel in their stated order. No
commutation is used. Thus an input C_0 u with dyadic u has a final odd
denominator bounded only by C_m. The number of completed operations
does not occur in that bound.

This is not true for a list of unrelated rational matrices. Repeating
a map with centre eigenvalue -1/5 can produce denominator 5^m. A
caller cannot declare matching types after the fact to avoid that
denominator: each semantic A_j must still have its proved dyadic
endpoint.

## A finite codebook for the actual clique response

Let E be the actual signed 112-port response in `CLIQUE-CODE-GRID.md`.
Let Gamma_s be the exact portwise current-stage route. Define

```text
E_s = Gamma_s^-1 E Gamma_s.
```

The finite stage labels s are part of the supplier word. A useful
candidate codebook consists of I, E_s, and E_s^-1 on each declared data
bank, with identity on all unrelated roles. It also permits declared
dyadic unit frame operators on the left and right of those codes.
These frame operators and their inverses add no odd denominator.
Their implementation and binary precision costs remain separate.

For this codebook, every code and its inverse has odd height at most
one at five and at seven, and zero at all other odd primes. This follows
from the actual inverse formula, not only from its determinant. The
codes can depend on tensor width through the exact routes and native
frames. The same height bound holds at every width.

Every entry in a physical bank needs a declared type. It is not valid
to call only its eight centre coordinates encoded while leaving an
unproved action on the other coordinates. A code on borrowed helpers
also needs its full arbitrary-input endpoint. Identity on an untouched
helper is a proved special case.

This codebook excludes the inverse of the 104-port ordinary complement
of the selected-eight split, which requires 31. Adding that inverse requires an enlarged
codebook, its exact prefix bound, and a factor 31 in the grid.

The modular syndrome criterion in `CLIQUE-CODE-GRID.md` is a direct
way to check one class of matching transitions. It tests all physical
input columns, including helper columns. The mere fact that two codes
both use divisor 35 does not prove a matching transition.

## Recursive prefix theorem

For an odd prime p, let h_p(X) be the largest exponent of p in any
denominator of a matrix or vector X. Take h_p(X)=0 when all denominators
are prime to p. The elementary bounds are

```text
h_p(X+Y) <= max(h_p(X),h_p(Y)),
h_p(XY) <= h_p(X)+h_p(Y).
```

Assume a recursive implementation has the following proved data.

0. The root has dyadic semantic input and identity physical type. An
   optional initial code has a proved and charged encoding word whose
   complete prefixes satisfy the same local bounds.
1. Each completed child has a whole-state typed endpoint
   C_out A C_in^-1, with A Gaussian dyadic on every role.
2. All caller and child interfaces use the same actual code. A copy,
   permutation, split, or merge has its full declared operator and
   preserves that matching relation.
3. At each local cut, after completed children are replaced by their
   exact typed endpoints, the state is C_cut B_cut u, where u is the
   semantic input of this node. There is a uniform bound
   h_p(C_cut)<=c_p and h_p(B_cut)<=ell_p.
4. At every child entry, the decoded semantic input is D_child u with
   h_p(D_child)<=ell_p. This is a separate check. It prevents an
   unpriced inverse code at a nested entry.
5. All stored internal prefixes of local arithmetic modules satisfy
   the same bound after their current code is included. There is a
   fixed finite local word and a uniform maximum recursive depth D.

The code, prefix, and child-entry bounds concern exact matrices. A
sample of numerical inputs does not establish them.

Then every stored state on a live chain has odd height at most

```text
K_p = (D+1) ell_p + c_p
```

relative to the dyadic semantic root input.

To prove this, a child semantic input has height at most ell_p more
than its parent's semantic input. Induction down the live chain
therefore gives at most D ell_p at a node's semantic entrance. A
stored local state adds at most ell_p for B_cut and c_p for C_cut.
This gives the displayed bound. Completed siblings add no term:
their matching codes cancel, and their semantic endpoint A is
dyadic. Local rational factors between siblings are already counted
in B_cut.

If a convenient local analysis starts from physical rather than
semantic inputs, one can use the more conservative bounds obtained
by adding the code and inverse-code heights when forming B_cut and
D_child. For the five/seven codebook this adds at most two local
levels per prime to a naive physical-prefix estimate. This is a
finite bound, but it is not permission to omit the actual prefix
calculation.

The theorem applies to recursive calls with varying types. It also
applies to several data banks, provided the type is defined on their
complete direct sum. If a code mixes banks, a one-bank child entry
must prove its decoded-input relation explicitly. A code on a large
state does not automatically restrict to a legal type on one field.

## Common exact grid and the outer endpoint

Choose a fixed finite odd prime set containing every denominator in
the codebook and local words. Let

```text
S = product_p p^K_p.
```

Pad the binary grid as required by the full exact guard. At the outer
entrance multiply every physical numeric numerator by S, including all
arbitrary borrowed values. Use one common record format thereafter.
The height theorem makes every local fixed-odd division exact on this
grid. All native children remain exact; no new rounding is inserted.

At the final outer cut, the theorem by itself gives only the declared
code C_final A_total. If that physical endpoint is Gaussian dyadic,
all numerators can be unscaled exactly. If the required endpoint is
A_total rather than C_final A_total, the caller must also implement and
price removal of C_final. A bounded rational output code cannot be
silently treated as the required raw output.

The final semantic proof must include each borrowed role's stipulated
endpoint. The exact unscaling restores its original numeric encoding
only after that proof. Neither a height bound nor a finite codebook
establishes borrowed restoration by itself.

For the five/seven codebook, take K_5 and K_7 from the theorem. The
outer arithmetic-head cost and width are

```text
cost <= 8 N (K_5+K_7)(w_g+1),
extra width <= 3(K_5+K_7).
```

These counts include both conversions and all real numeric records.
Descriptor work is separate and linear. Equal exponents can use
one direct 35 scan per level, with the smaller cost stated in
`CLIQUE-CODE-GRID.md`. Since the codebook is fixed and D=O(log d)
under the retained contraction bound, this layer uses O(log d)
extra bits and O(V log d) outer work.

This is an extension of the retained odd-grid proof. The old condition
that completed children are physically Gaussian dyadic is the special
case C_in=C_out=I. The new proof uses exact matching code types to
replace that condition. It leaves source access, phases, maps,
storage, finite precision, and the final native endpoint to their
own implementation proofs.

## Exact checks and a decisive mismatch

The companion checker constructs the actual 112-port code and inverse.
It also uses sixteen-dimensional typed fixtures with a six-block,
an eight-block, and two arbitrary spectator roles. Ninety-six
completed rational children have changing types in {I,E,E^-1} and
dyadic semantic shears. Exact matrix composition agrees with the
telescoping identity after every child. Odd heights remain at most
one at both five and seven. The spectator rows remain identity.

The mismatch control repeats E^-1 eight times without the required
type transition. It has odd height eight at both primes. This shows
why the matching premise is material. The finite fixtures check the
formula and the counterexample; the argument above proves the
all-depth statement under its hypotheses.

The current clique-response codebook is a construction candidate.
The controller has not yet supplied all of the whole-state typed
identities and child-entry relations in the theorem. No complete
supplier, new exponent, or kappa value is claimed.

The work uses the retained exact-grid method, the actual cyclic pair
coordinates, and the coordinating agent's clique response. OpenAI Codex
assisted the proof and checks. No publication is authorized. Before any
future PR description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
