# One-accumulator factors for the complete-minor family

The serial accumulator construction applies to every union of complete
centre minors. It gives lower scalar costs for the dyadic forty-port
case, and gives exact rational implementations for the other nonsingular
cases. It also implements the original-content matrix and its inverse
at a common full frame. All factors use one existing owned C0 array and
no new native child.

The exact algebra admits every minor count k from zero through fourteen,
except k=13 for the ordinary-block inverse and k=1 for the content inverse.
The k=1 limitation is a real rational kernel. The odd-prime failures at
other sizes concern the dyadic coefficient ring and disappear on an exact
odd grid. This statement concerns these scalar factors and their stated
cuts. It is not a complete supplier theorem.

## Actual source and general identities

The checker pins the actual new-core R matrix with the same SHA256 as
`A8-ODD-GRID.md`. It verifies the full partition of its 112 columns into
fourteen eight-port minors. Every minor A_j satisfies

    R_Aj R_Aj^T = 4 I_8.

Each row has four signed unit entries in each minor. These finite facts
give the following identities for any union S of k such minors, not only
the initial unions used in the literal table. Put U equal to its complement,
K=R^T/4, d=k-13, and E=diag(-I_S,I_U). Then

    R_U K_U = (14-k) I_8,
    R E K = (14-2k) I_8,
    H_k = I_U-K_U R_U.

For k different from thirteen,

    H_k^-1 = I_U + K_U R_U/d.                         (1)

After the selected raw exchange and this ordinary inverse, the fused
upper correction makes the borrowed-Y response `diag(Q_S^-1,-I_U)`.
The original-X response, with its explicit input Q_S kept in place, is

    A_k = E + K R/d.                                 (2)

For k different from one and thirteen,

    A_k^-1 = E + E K R E/(k-1).                       (3)

To prove (3), factor (2) as `E(I+E K R/d)`. The inner rank-eight update
has Schur factor `d+R E K=(1-k)I`. Its inverse is
`I+E K R/(k-1)`. Multiplication on the right by E gives (3).
No Q operator has moved through a scalar matrix in this derivation.

At k=1, `A_k E K=0`, and `E A_k` is a rank-104 projector. Selected Y
retains the missing eight original channels in the full two-bank word.
At k=13, U is one complete minor and H_k is exactly zero on all eight
ordinary fields. No coefficient-field extension inverts that block. A
different controller can still preserve additional information elsewhere;
this result does not exclude such a change.

At k=0, H_0=J, A_0=J^-1, and A_0^-1=J. The ordinary inverse uses
division by thirteen. There is no selected exchange. At k=14, U is empty,
the ordinary factor is the identity, A_14=-J, and its inverse is -J^-1.
These endpoints help separate a borrowed-block condition from a
restriction on the required computation.

## The shared accumulator word

Use one initial CLEAR of C0 and one CLEAR after each of the eight rows.
This is nine CLEARs. C0 stays at the common frame between rows. The final
CLEAR permits its return to the inherited empty-frame private convention.
No nonzero value is relabelled. The initial CLEAR removes an arbitrary
owned C0 input. Other private and borrowed fields are not erased.

To apply H_k or its inverse, query the signed ordinary row r_i=R_i|_U
into C0. Scale it by -1/4 for H_k, or by `1/(4d)` for the inverse, and
scatter it through r_i^T. Put a negative sign in the unit ADDs instead of
using a negative SCALE. For the fused inverse and upper correction, query
the same ordinary row, but scatter through the full row R_i^T.

To apply A_k, first apply E to the data. For each full row R_i, query
`R_i E` from the current data, scale by `1/(4d)`, and scatter through
R_i^T. To apply A_k^-1, first apply E, query R_i, scale by `1/(4(k-1))`,
and scatter through `E R_i^T`.

The ordinary rows are orthogonal. The full-row content words have weighted
orthogonality `R_i E R_j^T=0` when i differs from j. Therefore, in each
word, a complete later query equals its query on the input to that word
after the initial E, if present. Distinct rank-one terms have zero cross
product. Their product is precisely (1), (2), or (3).

Write the absolute scalar denominator as `2^t o`, with o odd. Implement
the scale by `2^-t`, followed by one exact division by o if o>1. For all
these factors, o belongs to `{1,3,5,7,9,11,13}`. A partial query can have
one factor of o from earlier rows. The complete query has none, by
orthogonality. It is divided only when complete. Every prefix therefore
has odd denominator dividing o relative to the module input. For o=9,
this means at most two factors of three, not one.

All query and scatter coefficients are signed units. The largest new
binary height is five. Each row has at most 56 terms and each scaled
rank-one coefficient has absolute value at most 1/4. A data prefix has
row 1-norm at most `1+8*56/4=113`. A partial query has row 1-norm at most
`56*113=6328`. Scalar arithmetic temporaries are bounded by 12656 times
the maximum input field magnitude, which is less than `2^14` times that
bound. This conservative guard holds for every union of minors. The
receipt gives sharper exact prefix norms for each initial union tested.

H_k acts on ordinary input Y at I. The inverse, fused upper, and content
factors act on completed X at FULL. A controller must supply those cuts
and the existing owned C0. The factors contain no native transition.

## Exact costs

Let `t=v_2(4|k-13|)` and `u=v_2(4|k-1|)`. For k below fourteen and
different from thirteen, the scalar costs are

    H_k:                         7218 - 512k,
    H_k^-1:                      7186 - 512k + 16t,
    H_k^-1 with upper correction: 7186 - 256k + 16t,
    A_k:                         7186 + 16k + 16t.

For k different from one and thirteen, the content inverse costs

    A_k^-1:                      7186 + 16k + 16u.

The last two formulas also hold at k=14. At that size, the three ordinary
factors are empty and cost zero. They do not allocate or use C0.
The factors that have o>1 add sixteen real division-by-o scans. Those
scans are separate from the old primitive totals.

For example, the forty-port case now costs 4,658 for H, 4,706 for its
inverse, and 5,986 for the fused inverse. The content matrix costs 7,346
and its inverse costs 7,330. All are dyadic. The earlier frozen pivot
factor had the benefit of using no private array; these lower costs use
the C0 array already present in the actual core. The choice of interface
therefore matters.

The following local sums include the 164514-scalar clean core, all selected
physical exchanges, and the 14-scalar cleanup of C1 through C7. Each row
has native mass 5073. The table is a scalar assembly calculation. A
literal native transfer and full controller are additional checks.

| k | Selected fields | Balanced F | Fused B | B odd divisor | Content inverse: old cost and odd divisor |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 171746 | 171746 | 13 | 7218; none |
| 1 | 8 | 171650 | 171730 | 3 | Does not exist |
| 2 | 16 | 171554 | 171650 | 11 | 7250; none |
| 3 | 24 | 171458 | 171618 | 5 | 7282; none |
| 4 | 32 | 171362 | 171554 | 9 | 7282; 3 |
| 5 | 40 | 171266 | 171554 | none | 7330; none |
| 6 | 48 | 171170 | 171458 | 7 | 7314; 5 |
| 7 | 56 | 171074 | 171426 | 3 | 7346; 3 |
| 8 | 64 | 170978 | 171362 | 5 | 7346; 7 |
| 9 | 72 | 170882 | 171346 | none | 7410; none |
| 10 | 80 | 170786 | 171266 | 3 | 7378; 9 |
| 11 | 88 | 170690 | 171234 | none | 7410; 5 |
| 12 | 96 | 170594 | 171170 | none | 7410; 11 |
| 13 | 104 | Inadmissible balanced map | Singular H | — | — |
| 14 | 112 | 170352 | 167440 | none | 7442; 13 |

Every nontrivial odd-divisor entry adds sixteen real scans for that factor.
The content inverse is not included in the B total. It acts on the whole
completed X bank. The controller must decide whether and where it is
needed. A smaller number in this table does not establish a smaller full
supplier moment. In particular, more selected ports can change the
required line-code conversions and owner schedule.

## A common exact grid for a fixed family mix

The prior common-grid theorem in `A8-ODD-GRID.md` applies with the odd
denominators actually used by the controller. It requires Gaussian-dyadic
endpoints for every completed recursive child and for the final outer
return. A local rational factor can occur inside those exact words.
It cannot remain as an unaccounted rational recursive endpoint.

A uniform choice for every factor in this family is

    L = lcm(3,5,7,9,11,13) = 45045 = 3^2*5*7*11*13.

If M bounds the number of factors with odd division in a finite parent,
and D bounds live recursive depth, use root grid `2^-P L^-K`, where
`K=M(D+1)`. Each factor adds at most one L. Completed children add none.
Scale every root numeric stream by L^K, including arbitrary dirty
helpers; unscale every final numeric stream after the proved dyadic
endpoint. The additional width is at most 16K bits.

Six fixed-prime multiplication scans implement multiplication by L; six
division scans implement its inverse. Thus both root conversions together
need at most `48 N K (w_g+1)` arithmetic-head steps, plus retained linear
descriptor and counter work. Here N counts all real numeric records.
Each local real /o scan uses at most `4(w_g+1)` arithmetic-head steps.
The finite carry is in `{0,...,o-1}`. The general signed invariant is
`o Q_unsigned=N_unsigned+2^w c_final`, with exact signed condition
`c_final=o s_Q-s_N`.

For a fixed family and the retained 73/48 child bound, these costs add
O(log d) width and O(V log d) outer work. The local scan cost is O(V).
An actual controller should use its smaller necessary L: k=1 needs three,
k=0 needs thirteen, and k=5 or k=9 needs no odd grid for either unit.
The complete controller must still calculate its binary guard, all
finite node work, and its supplier moment. No old precision constant is
copied by this argument.

## Verification and credit

Run one process:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/odd-grid-a8-20261017/check_minor_factors.py --out /tmp/MINOR-FACTORS-REPLAY.json
```

Expected status: `PASS_ALL_COMPLETE_MINOR_SCALAR_FACTORS`.

The checker verifies each actual minor Gram matrix and its four unit
entries per row. It then checks the literal words for the first k minors
at every k. There are 69 factors, of which 66 are nonempty and three are
the k=14 ordinary identities. Every nonempty factor checks all 113 formal
columns, including arbitrary owned C0. Every prefix checks its
denominator and row norm. Both inverse orders are checked where an
inverse exists. Wrong scatter signs fail the endpoint or the stated
divisibility invariant. All six odd-divisor scans are checked on every
signed numerator at widths one through ten.

The executable does not enumerate all 16384 subsets of minors. The theorem
for arbitrary unions follows from the verified individual Gram identities
and the proof above. The sharper prefix norms in the receipt apply to
the literal first-k packets. The uniform bound 6328 applies to all unions.
The executable does not replay the complete native words or a controller.

The actual minor partition and Schur formulas come from
`../../native-escape-20261017/RAW-MINOR-SUBSETS.md`. The first five minors
build on the prior protected five-minor logger. The weighted content unit
and full-frame implementation also build on the new-core-transfer lane.
The bridge-access and new-core-transfer lanes independently found that
seven adjacent zero CLEAR pairs can be merged; that change gives the
nine-CLEAR schedule used here. The exact odd-grid method and its earlier
campaign application are credited in `A8-ODD-GRID.md`.

OpenAI Codex assisted this work. This is a producer packet and requires
independent review. No PR, push, publication commit, maintainer selection,
or complete kappa improvement is claimed.
