# An actual TWOSIDE profile excluded by A3 shortening

Let K be any characteristic-zero field. Use the P112 root-evaluation code C
and binary support weight in the retained PR3234 theorem. Suppose eleven
collectively independent pieces span T, with

```
dim(T intersect C) >= 7,
binary weights bounded by 2,3,6,6,6,6,6,7,7,7,7.
```

These hypotheses are impossible. This is the literal historical TWOSIDE
`(b,t)=(7,4)` profile `2,3,6^5,7^4`, with weights understood as upper bounds.
The conclusion is a local profile exclusion. Applying it inside the full
decoder reduction retains that reduction's other obligations.

## The inherited theorem and geometry

PR3234 at `bd90899d5a45806288f7f3c9f177172a0ef5fa59` proves the following
statement over K, uniformly over orthogonal eight-root punctures. If
`a_1,...,a_k,q_0,...,q_3` are collectively independent, their span has
code intersection dimension at most two whenever the union of the a-supports
has cardinality at most 29 and every q has binary support rank at most six.
Its exact proof is retained byte for byte in `vendor/A3-PROOF.md`.

That theorem uses the P112 capacities `g(2)=2`, `g(3)=4`, `g(6)=20`,
minimum nonzero code support 53, and classification of support below 70 as a
root direction. Its finite geometry and standard Weyl-chamber dependency
are inherited here. This package checks the application, and does not replay
or independently establish PR3234's theorem or its finite geometry.

## Deletion preserves three code dimensions

Remove the four pieces whose weight bounds are seven. Their coefficients
define a linear map `pi:T -> K^4`, because all eleven pieces are a basis
of T. Its kernel T' is exactly the span of the seven retained pieces.
For D=`T intersect C`, rank-nullity gives

```
dim(T' intersect C) = dim ker(pi restricted to D)
                    >= dim D - 4 >= 3.
```

No deleted piece is required to lie in C. This argument permits arbitrary
supports, values and correlations of those pieces. The seven retained pieces
are still collectively independent.

## Bind every A3 hypothesis

Order the retained weights as `2,3,6,6,6,6,6`. Designate the first three
pieces as a_1,a_2,a_3 and the last four as q_0,...,q_3. The common small
support S therefore satisfies

```
|S| <= g(2)+g(3)+g(6) = 2+4+20 = 26 <= 29.
```

All four q-pieces have binary rank at most six. Independence and the exact
root code are unchanged by taking a subset of the original basis. Thus the
inherited theorem gives `dim(T' intersect C)<=2`, contradicting the deletion
lower bound three.

For clarity, the quotient and root-edge inequalities inside that theorem
also hold directly for this caller: `26+20=46<53`, and
`26+20+20=66<70`. PR3221's earlier unrestricted support22 theorem does not
apply to the bound 26. PR3227's special six-flat-plus-four theorem is not
invoked. No common cover or overlap among the small supports is assumed.

## Historical profile binding and limits

DreamingOfClouds/PR3154 at `708f0ad8928c383de8294aea3c126e9461d2066d`
supplies the original TWOSIDE filters. The profile has eleven pieces,
code-dimension parameter seven, allowance four, and sigma sum
`sum(w-2)=41<42`. It survives the original size/deletion and BK/BK7 filters.
The two local implementations reproduce all 154 historical survivors of
that cell, agree on the complete enumerated domain, and contain this profile.
The original two implementations and recorded count are retained for inspection.

This does not establish that 153 unresolved profiles remain. Other public
proofs already exclude members of the same historical list. We claim only
this literal implication, not a complete reconciliation of those proofs,
full C5, `C(P112)>=64`, a supplier, a new kappa or a selected-frontier change.

Credit DreamingOfClouds for the profile reduction, Nick Petalas for PR3234
and the deletion-based predecessor applications, and the retained E8/P112
lineage including joaqcoo's decoder model. New work is Apache-2.0.
