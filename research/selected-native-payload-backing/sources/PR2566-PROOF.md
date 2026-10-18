# Charged binary digit and atom permutations

This audit concerns the unchanged `bitstream.py` and `cardinality.py` from
Jose Manuel's PR2501 at `52a995b9d7f3e008c252770a5f47fde67a7cb37a`.
It does not reprove that package's selected residual normal form or extend its
leaf interface to a recursive child. The Counter lemma is credited to ywz65's
PR2473 at `677baf4c92e876530c9637db191e5fd92f62624f`; the present calculation
includes the new digit buckets, cardinalities, atom passes and address signs.

## Domain, units, and endpoint

Fix an odd prime q, w>=1, M=q^w, and positive spectator extents U,G,S.
The atom-swap input is the complete stream

    [U] x [M] x [G] x [M] x [S],  V=U*M^2*G*S.

The sign input is `[U] x [M] x [S]`, with V=U*M*S. Extents entering the
public macros use their own canonical binary encoding with one high zero
margin, as required by the retained source. Natural's private extents are
canonical with no redundant high zero. Modulus words have exactly
L=bitlength(M)+1 bits. q is a compiled finite label, not an unbounded decoded
runtime word. The source enforces the prime-power modulus path; primality and
oddness are inherited mathematical premises, not inferred from that check.

An atom swap sends `(u,x,g,y,s)` to `(u,y,g,x,s)`. Sign sends `(u,x,s)` to
`(u,-x mod M,s)`. All payload bits are opaque. These are exact permutations
of the complete stream, including unequal prefix, gap, and suffix extents.
The borrowed source and all input words return byte-for-byte with heads at
their entry position; the result is a separate owned output. Private temporary
payload, counters, cardinalities and numerical words are erased at success.
Caller disposal of the output, exceptions, and surrounding layout construction
are outside this successful-call contract.

The exact bill below counts the source Tape/Word meter's reads, writes, and
unit head moves separately. Input-word traffic, blank tests and head returns
are included. Fixture construction and the audit's inspection are excluded.
The meter does not charge Python object allocation, bytearray bookkeeping,
integer audit arithmetic or literal transition-table execution. Fixed tape
headers and finite control can be implemented with the stated reused lanes;
they add a constant depending on q to the asymptotic bound. We do not identify
these metered operations with elapsed Python time.

## Countdown and suffix costs

Let b=bitlength(N), s(N)=popcount(N), N>0, and let its input word have k>=b
bits. PR2473 gives the Counter's own lifetime traffic

    (7N-2s(N)+2k+11, 2N-s(N)+3k+4, 6N-2s(N)+4k+14).

Reading/restoring its input adds `(3k+3,0,2k+4)`. Write their sum as

    F(N,k)=(7N-2s(N)+5k+14, 2N-s(N)+3k+4,
            6N-2s(N)+6k+18),     F(N)=F(N,b).

The old source used k>=2. The same formula holds at the newly used canonical
one-bit word N=1,k=1: initialization, its one decrement and close give the
same expression by direct code accounting. This extension is also checked.
The general derivation uses sum_{j=1}^N v2(j)=N-s(N); power-of-two decrements
shorten the counter, and the final zero is represented and erased explicitly.
Thus F(N)<=(24N,8N,28N), coordinatewise, for every positive N.

The fixed one-bit-suffix recognizer has no writes. On a canonical Natural word
its exact traffic H(S) is

    S even:                 (2,0,2)
    S=1 or S=3 mod 4:        (6,0,6)
    S>1 and S=1 mod 4:       (7,0,8).

It reads no whole numerical value. `copy_bits` performs that test on every
invocation, then constructs a suffix Counter only when S>1. Set

    B(S)=H(S)+1_{S>1} F(S).

Consequently B(S)<=(28S,8S,32S). The exceptional S=1 branch is part of the
bill; pretending every copy builds a Counter gives a different exact result.

## Exact digit bills

For digit swap let V=U*q^2*G*S and Q=q^2. There are Q sequential buckets,
each with U*G*S bits. Counting their split, rewind, merge, blank checks and
erasure, together with the borrowed source and returned output, gives

    payload(U,G,S,q)=(10V+5Q+3, 3V, 10V+6Q+4).

For example, a B-bit bucket costs `(6B+5,2B,6B+6)`. The source costs
`(2V+2,0,2V+2)` and output `(2V+1,V,2V+2)`. This includes every return scan.
There are two outer U countdowns, 2Uq middle G countdowns, and 2Uq^2G suffix
copies. Therefore the exact complete digit-swap bill is

    D=(10V+5q^2+3,3V,10V+6q^2+4)
       +2F(U)+2Uq F(G)+2Uq^2G B(S).                    (1)

For digit complement V=U*q*S. There are q buckets and no middle countdown:

    E=(10V+5q+3,3V,10V+6q+4)+2F(U)+2Uq B(S).          (2)

These formulas depend only on the extents, not payload values or samples.
For q>=3, both are coordinatewise at most `(93V,27V,106V)`.
For (1), substitute the F/B bounds and use U<=V/9,
UqG<=V/3, q^2<=V and V>=9. The resulting coefficients are at most
92+2/3, 26+1/9, and 105+1/3 respectively. Equation (2) gives the smaller
coefficients 88, 24+1/3, and 100. No finite experiment is needed for these
inequalities.

## Whole atom and sign, including preparation

The kth atom digit pass (k=0,...,w-1) uses

    U_k=U*q^k,  G_k=G*q^(w-1),  S_k=S*q^(w-1-k).

Their volume remains V. Splitting into q^2 digit buckets and merging bucket
(b,a) for output digits (a,b) exchanges exactly the kth radix digits; the
unchanged middle includes all intervening digits and the spectator gap.
The w exchanges commute on distinct digit positions and perform the whole
atom interchange. Earlier intermediate outputs are erased after the next
pass. Erasing a V-bit tape from its returned head costs

    C(V)=(2V+3,V,2V+4).

Thus the atom's exact digit-and-intermediate subtotal is
`sum_k D(q,U_k,G_k,S_k)+(w-1)C(V)`; it deliberately excludes, rather than
forgets, the separate preparation charged next.

Sign complements the w digits, obtaining M-1-x, then rotates the atom by one
to obtain -x modulo M. Its digit pass k uses U*q^k and S*q^(w-1-k).
The final rotation splits into M-1 and 1 blocks and merges in reverse order.
It uses two outer countdowns, 2U countdowns of each block count, and at most
2UM suffix countdowns, plus four suffix recognizer tests per U. The original
margin-bearing suffix word is used here, so its F has k=bitlength(S)+1.
The leading and unit block words use k=L, including the padded unit word;
that O(L) work is not treated as a one-bit numeral. The same payload-bucket
calculation applies with two buckets. Using L<=M, k_S<=2S and k_U<=2U,
the complete rotation, except binary subtraction of M-1, is less than
`(400V,400V,400V)`. The sign erases all w intermediate V-bit tapes.

Here is an explicit conservative accounting of preparation. Put
B=bitlength(q)+1 and K=k_U+k_G+k_S+2wB+2. Reading the retained loops gives:

* A Natural construction/normalization/close, positive-extent check, or one
  fixed-q multiply/divide costs at most 100(K+B+1) of each metered operation.
  Every loop scans its binary word or deletes a high zero; multiply extends
  by at most B bits. Input extent reads are included.
* A word-bank copy/free/compare/subtract, or a zero test, costs at most
  100(L+1) of each operation. `Unsigned.divmod` makes exactly L iterations,
  each performing at most one shift, compare and subtract, with paired
  allocations/erasures. Including its startup and return, its charge is at
  most 1000(L+1)^2 per operation. The fixed literal q fits these same words.
* Atom makes three `radix_power` traversals of w divisions, and at most
  4w+9 Natural lifecycle/check/update operations. A bound on all its
  preparation is

      1000(w+3)(k_U+k_G+k_S+2wB+B+3)
        +3000(w+1)(L+1)^2.                            (3)

  Sign uses two radix traversals and fewer Natural operations; its extra
  subtraction and rotation fit the same bound plus 400V. Its absent G may
  be set to 1 for this upper bound.

These are source-loop upper bounds, not a fitted regression. In particular
no constant-time arithmetic on w, M or the spectator values is presumed.
For positive X, bitlength(X)+1<=2X. Put H=UGS for atom and H=US for
sign (with its absent G set to 1). Then k_U+k_G+k_S<=6H,
w+3<=4w, and L+1<=(B+2)w. Thus (3) is at most

    24000*w*H + 12000*(B+1)*w^2 + 6000*(B+2)^2*w^3.

The cubic term requires w^2<=q^w=M: this holds for w=1,2 at q=3,
and the successive ratio (1+1/w)^2<=9/4<3 for w>=2 proves the rest;
larger q only strengthens it. Both primitives have V>=H*M. Dividing the
last display by w*V and using H>=1, w<=M and w^2<=M therefore gives

    preparation/(w*V) <= 24000 + 12000*(B+1) + 6000*(B+2)^2.

Digit passes, intermediate clears and the sign rotation together add less
than 512*w*V per operation. The sum is below 1,000,000*(B+3)^2*w*V.
Consequently, for each of reads, writes and moves,

    total <= C_q * w * V,    C_q=1,000,000*(B+3)^2.    (4)

The deliberately loose constant is explicit and independent of w,U,G,S,
payload and recursion depth. q is fixed; this is not a uniform constant in
an unbounded machine alphabet. The complete source primitive is bounded,
not just its payload stream loop. A whole residual or caller may invoke
many such primitives and has additional coefficients and layout obligations.

## Live capacity and a fixed tape-role realization

During one digit pass all buckets together hold V bits; its output holds at
most V. At later passes the incoming owned intermediate holds another V,
while the original borrowed input is preserved separately. Thus at most 3V
additional payload bits are live, including the eventual result. At return
only the V-bit result remains. Rotation obeys the same bound. q^2 bucket
headers and tape delimiters are additional constant-size administrative state.

Allocation in the Python reference can be lowered to a fixed set of tape
roles: q^2 bucket lanes, two alternating intermediate/output lanes, three
Natural cardinality lanes and three nested Counter lanes suffice for atom
(q^2+8 owned lanes). A Counter is closed before its nesting role is reused;
all buckets are erased before the next digit. Sign uses no more lanes than
this bound. These lanes need variable finite tape length, not a bound on the
numerical extents. Six extra L-bit numerical word slots suffice during the
radix division, in addition to the preserved modulus and unit. Input extents
have their own separate borrowed word tapes. The reused-lane schedule charges
each erase; it does not treat retained allocation capacity as erased payload.

This is a concrete role-allocation consequence of the source lifetimes, not
an executed full FinTM2 compiler or a bound on Python heap overhead. Raw-prefix
directories, child continuation stacks, family hosting, numerical coefficient
pages and the complete selected supplier remain outside the audited primitive.

## Validation and limits

The independent oracle uses integer formulas (1)-(2), not a shadow copy of the
source loops. Instrumentation registers source Tape objects and sums all Tape
and Arena meters; it does not change runtime branch decisions. All retained
bytes are authenticated before any import. Binary index bit planes reconstruct
the origin of every output bit in the finite complete macro cases; this is
stronger than a random payload check. The permutation is calculated directly
from the whole-atom index map, independently of digit buckets.

Finite cases corroborate source accounting, but the all-size results are the
written identities, loop bounds and lifetime argument above. This does not
claim a new residual identity, better tariff, global supplier, exponent,
formal-kernel verification or physical runtime measurement.
