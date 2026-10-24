# Independent review of the signed clique code and typed grid

Status: the independent exact checks pass. The conditional type theorem
has no unresolved local proof finding. See `FREEZE.json` for the checked
source bytes and this review's hashes.

The reviewed claim is a scalar code on 112 fields in one proved common
frame. The recursive grid result is conditional on the stated whole-state
types, child-entry relations, and prefix bounds. Neither claim supplies a
native inverse response, a helper lease, a new controller, or a complete
supplier cost.

## Independent source construction

Let A be the actual direct sum of 24 signed pair matrices. On the other
64 coordinates, A is identity. The pair matrices have entries in
{1,-1} and satisfy A_e A_e^T=2I.

For each of the eight six-mode groups, let d_g be its actual signed
indicator, and set w_g=A^T d_g. For each of the eight small cliques, let
w_g be its unsigned indicator. Then

```text
w_g^T w_h = 0                         when g differs from h,
w_g^T w_g = 12                        for a six-mode group,
w_g^T w_g = 8                         for a small clique.
```

Thus the source matrices must be

```text
E     = I - sum_large w_g w_g^T/2 - sum_small w_g w_g^T,
E^-1  = I - sum_large w_g w_g^T/10 - sum_small w_g w_g^T/7.
```

This construction uses signed source rows. It does not import a producer
module or form the expected endpoint from the emitted word. The review
checker compares these matrices with both endpoint matrices in the
frozen native extension. It does not
replay the native extension.

The 16 nonzero orthogonal vectors prove rank(E-I)=16. The eigenvalues
are 1 with multiplicity 96, -5 with multiplicity 8, and -7 with
multiplicity 8. Hence det(E)=35^8. The same decomposition proves both
inverse orders and the stated quadratic inverse polynomial.

## Literal scalar word

For an unsigned group of size k, put m=k-1. Write a_i for the original
nonpivot values and p_0 for the original pivot. The forward word first
sets each nonpivot to a_i-p_0. Its middle steps set the pivot to
-sum_i a_i. The final additions give a_i-sum_j a_j-p_0. These are
exactly the coordinates of (I-11^T)x.

For the inverse word, the pivot before its odd division is
sum_i a_i-(k-2)p_0. Division by -m sets it to
p_0-(sum_i a_i+p_0)/m. The last loop adds the same correction to each
nonpivot. This proves I-11^T/m. Sign conjugation proves the signed
version.

The independent checker reads the final literal event list. It first
accumulates each output covector in reverse event order. It then checks
all forward prefixes with a separate row update. Both runs include all
112 data columns and two arbitrary spectator columns. Each event must
read and write only the 112 data fields. This address check, rather than
the choice of two spectator examples, proves that every untouched role
is unchanged.

Each direction has 574 complex events: 384 unit ADDs, 126 signs,
48 binary scales, and 16 odd operations. The scalar count is 3,420 old
real units, with 32 real odd scans charged separately. The forward odd
operations multiply; the inverse odd operations divide.

The exact maximum stored row sum is 20 forward and 18 inverse.
The sum of the two unit-ADD operand row norms has the same respective
maximum. The binary denominator height is one in each direction.
The inverse odd height is one at five and one at seven; the forward
odd height is zero.

## Exact division and stored values

The review checks each required division on the common integer grid
with scale 70. It separately starts the inverse on 4E and checks every
division without an odd root factor. The latter computation must return
4I. Four is a binary scale, so it does not change the valid-code claim.

For a positive odd divisor d, low-to-high division has the invariant

```text
d Q_low = N_low + 2^j c_j,
0 <= c_j < d.
```

The next quotient bit is (b-c_j) mod2. At the end of a signed w-bit
word, exactness is equivalent to c_w=d*s_Q-s_N. The quotient cannot
overflow on an exact division. For multiplication, the corresponding
invariant is d N_low=Q_low+2^j c_j. The final test is
c_w=d*s_N-s_Q. It detects signed overflow.

The retained A8 scan proof gives the explicit arithmetic-head bound
4(w+1). It charges the move to the low end, the arithmetic traversal,
delimiters, and the return. A fixed d needs only finite carry control
and sign flags. The input record is overwritten. There is no remainder
stream. Descriptor and record-counter work remains a separate charge.
The review checks division and multiplication for all signed inputs of
widths 1 through 12 and d in {5,7,35,2145}.
All 65,520 division and multiplication cases pass.

The factor 64 is a local scalar-word guard. It is not a binary precision
bound for a complete recursive supplier. A root scale must apply to
all physical numeric records, including arbitrary borrowed records.
Addresses, tags, and descriptors are not numeric payloads.

## Code image and Gaussian coefficients

In a signed block, the inverse has its only possible odd denominator in
the signed sum divided by k-1. This proves the two syndrome conditions:
eight rows modulo five and eight rows modulo seven. A is a dyadic unit,
so the conditions transfer to the physical coordinates.

The source matrices are real. Their rank calculations over F_5 and F_7
extend to Gaussian coefficients. In particular, R0/5R0 is not a field:
it is F_5[i], which has two factors. The claim does not need it to be a
field. The syndrome map has an explicit right inverse after the dyadic
pair basis is applied. It is therefore surjective over R0/pR0. The
kernel-factor criterion L_t M=S_p L_s follows over that ring. The
Chinese remainder argument for the two coprime integer moduli is valid.

The criterion concerns the complete operator, including helper columns
that a middle map reads. It does not certify a map from only its action
on data columns.

## Recursive type theorem

Let u_0 be the dyadic whole-state root input. After j recursive edges,
write the decoded semantic input as

```text
u_j = D_j ... D_1 u_0.
```

The separate child-entry hypothesis gives h_p(u_j)<=j*ell_p.
A stored local state has the form C_cut B_cut u_j. It therefore has
height at most j*ell_p+c_p+ell_p. With j<=D this is
(D+1)ell_p+c_p.

This proof requires the child-entry bound in addition to a bound on
the child's physical input. Decoding that input can add height.
It also requires the internal arithmetic prefixes, not only the
visible caller cuts.

For completed calls, exact matching types cancel in their given order:

```text
(C_m A_m C_(m-1)^-1) ... (C_1 A_1 C_0^-1) C_0
    = C_m A_m ... A_1.
```

No factors are commuted. Each A_j must be dyadic on every input
column. A borrowed row with an unproved rational action can invalidate
the bound even when all data columns pass. An unrelated list of
rational physical matrices does not satisfy this premise merely
because its entries have the same odd prime support.

The independent fixture uses noncommuting rational codes and semantic
shears. It reads two arbitrary helper inputs and keeps their endpoint
rows equal to identity. It compares all columns after every completed
call. A separate unmatched repetition has height eight and supplies a
negative control. This finite check supports the algebra. The induction
above is the proof for arbitrary depth under the hypotheses.

## Review findings and limits

The root representation needed an explicit entry condition. The producer
added identity physical type at the root, or a separately proved and
charged initial encoding whose prefixes satisfy the same bounds.
This condition is necessary before multiplying raw dyadic numerators
by the common odd factor.

The exact four-pass scan constant needed its specific source. The
producer added the pinned A8 scan proof and the general signed carry
formulas. The retained stream text alone states a linear bound; it
does not state this constant.

The older `RESPONSE-PROGRAM.json` supplies the mode signs and the
certified clique sets. Its own response is a different operator. The
new endpoint differs in 1,154 forward entries and 1,704 inverse entries.
Its chosen small-group partition also differs. The reviewed equality
is with `odd16-normal-v2/EXTENSION-PROGRAM.json.gz`, as the producer
states. It is not an equality with the older response endpoint.

The prime-31 exclusion is necessary for the ordinary complement of
the selected-eight split. The source `ordinary_inverse` is 104 by 104
and has reduced denominators {7,31,62}. In contrast, `selected_inverse`
is 8 by 8 and is integral. `selected_inverse_block`, the selected
block of the full inverse, has denominators {5,10}. These are three
different matrices. The full E^-1 code does not introduce 31.

The outer endpoint condition is separate from the height theorem.
A final rational code cannot be discarded. Exact unscaling restores
the original record format only when the complete required physical
endpoint is dyadic on all roles. If the caller needs the uncoded
semantic output, it must also implement and price code removal.

This review does not establish current-stage access, old retired-bank
access, phases, helper restoration in a native supplier, storage for a
new caller, or a complete kappa calculation. It does not repeat the
640-column native replay. The common-frame scalar result does not
depend on any such replay being repeated here.

## Reproduction

The review checker uses only the Python standard library. It imports
no producer module. Run each command with a new output directory:

```text
python3 -I -B check_review.py --out review-normal
python3 -I -O -B check_review.py --out review-optimized
```

Both runs returned:

```text
PASS_INDEPENDENT_SIGNED_CLIQUE_CODE_REVIEW
```

The two `CHECKS.json` files are byte-identical. The canonical review
receipt is `CHECKS.json` beside this proof. The source manifest records
the producer proof and checker bytes in addition to the exact source
and literal-word pins checked by the review program.

No PR, commit, push, or publication is authorized. Before any future PR
description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
