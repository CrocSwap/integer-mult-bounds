# Integral transfer of the chain-nested root caller

## 1. Statement
Let C be the complex chain-nested root caller (`chainroot.build([1]*9,[1]*9)`). (a) C has integer ADD coefficients and only unit SCALE factors; its root and handoff bases are unimodular over Z. (b) Specialising q²=1 turns every ordinary normalisation into the identity, so the caller identity is an identity of integer matrices over R=Z[q,D1..D18]/(q²−1). (c) Reducing mod 2 gives a characteristic-two caller B (ADD odd → XOR, even → nothing, SCALE ±1 → identity) that computes the same endpoint with q reduced mod 2. (d) On the retained BIT native word B has the invoice priced in `verify.py` and an ordinary BIT saving 0.00385248 is admitted.

## 2. Integrality of the chain (a)
Left site i has x_i = A + f_i + 2 Σ_{j<i} f_j and w_i = A + 2 Σ_{j<i} f_j, so x_i − w_i = f_i; with the unit vectors f_j (j<i) and the remaining coordinate vectors, the basis matrix has determinant ±1 over Z. Right site m uses x = −A + h_m + 2 Σ_{l>m} h_l, w = A − 2 Σ_{l>m} h_l, with x + w = h_m, again determinant ±1. The coefficient 2 in x is only an entry of an integral unimodular matrix: its reduction mod 2 is still invertible, and the identity is established over Z before reducing. The three thin query pairs (x,y) have integral primitive vectors with y·x=0 and a ±1 entry in each; their completions use ±1 pivots only. A construction that lets power-of-two pivots through (`dyadic=True`) produces SCALE 2, 1/2 and ADD 1/2; it is not integral and `verify.py` rejects it (control `dyadic_basis_not_integral`). Every pivot of the integral build is ±1, checked by `verify.py` on all 1237 events.

## 3. Normalisations and reduction (b), (c)
The ordinary normalisation at a role is (1+σq²)/2 on the old row plus (1−σq²)/2 times the q²-shifted row, in Z[i] terms; at q²=1 the sum is the old row. Hence after specialisation only integer ADD, SWAP, ±1 SCALE, QUERY/LOCAL (adding the q-shifted row, q^{-1}=q) and IDLE (monomial shift) remain. R is a free Z-module on monomials, so equal integer coefficients of the Z-identity reduce mod 2; the F2 replay in `verify.py` recomputes the reduced identity directly, and the integer replay recomputes the Z-identity.

## 4. Invoice and crossing (d)
Targets and paid jobs are 18 times the native histograms of the retained audit, plus 111 paid rank-1 jobs per thin QUERY, 111 paid jobs of rank 7·|stages| per merged idle, and 111 productive fields of rank q + 7·|stages| per role (diagonal). The crossing of Σ(T_r−P_r) r^{1−κ} is bracketed by the retained interval engine and a Decimal engine; the rank-mass surplus is positive (753). Finite admission, ordinary work, owned bank and the wrapper envelope follow the #6726 procedure with the new tested saving 0.0038525.

## 5. Scope
This is a dependency bound for the BIT native word under the five framework assumptions of #6726. The overall κ of a complex construction must stay below the BIT saving; this package does not assert one.
