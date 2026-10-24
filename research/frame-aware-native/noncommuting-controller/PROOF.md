# A sufficient noncommuting-stage construction for the p16 controller

## Theorem (universal in the stage operators)

Let V be a vector space over a field of characteristic 0. Let Q be an invertible linear operator on V. For each thick stage s in

`T = [0, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 32]`,

let D_s be an arbitrary linear endomorphism of V such that Q D_s = D_s Q. No equality D_s D_t = D_t D_s is assumed, and D_s need not be invertible for this algebraic statement.

Form the 32-port word W specified by the 154 physical events in the authenticated `CONTROLLER.json` from #4470. A forward local call is `(D_s ⊕ D_s) [[1,0],[Q^−1,1]]`; a backward local call is `(D_s ⊕ D_s) [[1,−Q],[0,1]]`. A query-only event applies the indicated shear without D_s. An idle event on ascending stage list `[s_1,…,s_k]` applies `D_{s_k} … D_{s_1}` on both ports. ADD and SIGNED_SWAP act literally as recorded.

Then the explicit rational scalar matrices L and R in `FREE-CERTIFICATE.json` are invertible, admit dyadic scalar programs, and satisfy

`L W R = diag(Q^{ε_i} D_{w_i[0]} … D_{w_i[-1]})`,

where `(ε_i,w_i)` is the corresponding entry of that certificate's `diagonal` list. There are 16 exponents −1 and 16 exponents +1. The two longest stage words are

`G = [32, 31, 29, 27, 25, 23, 21, 19, 17, 15, 13, 11, 9, 7, 5, 3, 1, 0]`.

Every remaining stage word is one of the 15 nonempty paid idle words; each occurs with both central exponents. Each paid word is a contiguous prefix or suffix of G in its actual operator order.

This is a theorem for this fixed p16 word and arbitrary admissible V, Q and D_s. It is not a theorem for every controller size p.

## Proof

Work first in the algebra A = Q⟨d_s : s in T⟩[q,q^−1], where q is central and the d_s are freely noncommuting letters. The canonical basis elements are pairs `(e,w)`, representing q^e times the ordered free word w. Distinct words are not identified, even when they use the same multiset of stages.

Initialize W as the identity matrix. The literal interpreter applies each of the authenticated 154 events by exact row operations. Left multiplication of an entry by q^e d_w prepends w to its existing free word and adds e to its central exponent. Rational coefficients are exact `Fraction` values; zero coefficients alone are removed. Thus every interpreter update is exactly the declared operation in Mat_32(A). No sorting of stage words or commuting of stage letters is performed.

Multiply this computed W by the two displayed scalar matrices, using rational arithmetic. The verifier checks every coefficient of every ordered word in all 1,024 matrix entries: off-diagonal entries are zero and each diagonal entry is precisely the declared single monomial with coefficient 1. This is a finite exact certificate for the asserted identity in Mat_32(A), rather than evaluation at a finite list of numerical operators.

The verifier also reduces each scalar boundary to the identity by Gaussian row operations. Every used scale and its inverse is dyadic, and every ADD coefficient is dyadic. Reversing these operations explicitly constructs L and R; replay gives the original matrices. The left and right boundaries use 90 and 59 synthesized scalar operations respectively. This establishes their invertibility and a legal constant scalar realization. These counts describe the emitted SWAP/ADD/SCALE operations; they are not an updated complete paid recursive invoice.

Finally send q to Q and each d_s to D_s. The assumptions that Q is invertible and central relative to the D_s give a well-defined algebra homomorphism A → End(V). Entrywise application to the exact identity proves the theorem. No pairwise commutation of the D_s is needed. ∎

## What this permits, and what it does not yet establish

The theorem is a sufficient operator construction for any proposed native stage family satisfying the local-call contract and central-Q commutation. It permits research on noncommuting stage geometries; the older commutative Laurent representation alone did not establish that extension.

A concrete multiplication construction must still implement its proposed D_s, local native tables, helpers and scalar boundaries on the actual fields, and pay the Fourier rank and absolute-phase corrections of every ordered idle product and main endpoint. Conjugating a Clifford operator is not assumed free. No unchanged rank invoice is inherited merely from this operator identity, and no new κ follows from the identity alone.

For a rank tariff satisfying subadditivity, preserving the maximal rank of G forces every contiguous idle subword to retain maximal additive rank. Therefore simply making those same contiguous idles cheaper while keeping G maximal cannot supply a gain. The new positive result is the broader sufficient algebraic identity; this observation is only a caution about one application.

## Reproduction and controls

Run `python3 -I -O -B verify.py`. Python's standard library suffices. The source bytes are authenticated before parsing, no repository code is imported, and no assert statement is used as an acceptance check. The verifier separately rejects a reversed query orientation and an idle whose stage order is reversed. Reversing the idle would be invisible in a commutative monomial representation; its rejection confirms that actual chronology is being checked.

The script has been run on Python 3.12.10 on Windows. No Linux execution or formal-kernel verification is claimed. The exact free-algebra certificate is independent of platform arithmetic and uses no platform-specific module.

## Attribution

The p16 word, retained native contracts and query-thinning construction are predecessor work, retained from Cinna Davis / 1337isnot1337's #4470 at commit b9a13c1673e0e9697de410de16e8bbf3207a7363 and its credited lineage. #4516 by Ryanson Jonathan independently replayed the commutative p16 controller and motivates retaining literal chronology checks. The underlying supplier and invoice work credits zxv, Jacob Alan Sussman, Cinna Davis, and the scalar, Clifford, geometry and outer-ledger contributors already named in those sources. No native word, supplier profile or κ improvement is attributed to this extension.

The new contribution is the exact free-associative certificate, separately written word interpreter, universal substitution argument and dyadic boundary synthesis for noncommuting stages. Prepared for Dugongue with substantial OpenAI assistance. Apache-2.0.
