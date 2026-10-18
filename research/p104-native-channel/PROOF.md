# Finite native realization and its boundary

## 1. Physical labels

Reconstruct the 120 root lines from doubled integer E8 coordinates. Write
`B[i,j] = (<r_i,r_j>+1) mod 2`. Its rank is nine. Select nine independent
principal coordinates as recorded in `label_isometry`. The compressed labels
`l_i` do **not** use the ordinary dot product: their pairing matrix is `J`,
the inverse of the recorded nonsingular compressed Gram matrix.

Find a `J`-orthonormal basis `v_0,...,v_8` and set
`q(l)_a = l^t J v_a`. The independent checker reconstructs the roots and Gram
matrix without producer imports, checks the inverse and orthonormality, and
verifies every one of the 120^2 identities
`q(l_i) dot q(l_j) = B[i,j]`.
The map is a linear isometry on the whole nine-dimensional binary space, so
it applies to every intermediate frame, including labels outside the 120 roots.
Each root label is odd because `B[i,i]=1`.

This is a concrete finite choice of physical labels. It is not an all-size
admission proof for an extended label alphabet.

## 2. Complete primitive identities

Use the retained canonical chart `Gamma_W` for a binary frame `W`. A literal
transport from `A` to `B` is `Gamma_B Gamma_A^-1`. Every transport is nested.
The exact compiler emits a Gaussian monomial, one positive child of rank
`|dim B-dim A|`, and another Gaussian monomial. No rank is inferred merely
from scalar event counts. There are 740 distinct recipes and 1410 paid uses;
the checker binds every use to its literal source-witness event and rank.

The independent interpreter imports no Clifford compiler. It compares signed
Pauli conjugations and an exact Gaussian state column. Equal signed Pauli
actions determine a Clifford up to scalar phase; equality on the nonzero state
column fixes that phase. Thus this checks the complete operator, not only its
unsigned symplectic matrix. In addition, all 512 Gaussian columns of each of
the eight rank-seven private drops are compared directly: 4096 columns total.

Let `C_q = ((1+i)I+(1-i)X_q)/2` and `F9 = product_a C_ea`.
For each source root the intrinsic input chart is `C_q`; its recorded adapter
is `Gamma_<q> C_q^-1`. For each target the intrinsic output chart is
`F9 C_q^-1`; its adapter is `F9 C_q^-1 Gamma_(q-perp)^-1`.
All 208 operators independently check as rank-zero Gaussian monomials,
including their phases. The final source and dirty-helper full charts are
already `F9`. Monomial endpoints add no positive child to this finite invoice.

## 3. Full channel induction

For each live register maintain a rational row `a_r` over the 280 independent
logical inputs. Its physical value is `Gamma_(W_r) a_r z`.
The entry adapters establish this invariant for the 104 intrinsic source
inputs. All other inputs start in the zero frame.

- A verified native transport changes only `W_r`, retaining `a_r`.
- A literal scalar addition is allowed only in a common physical chart; it
  changes `a_r` by the stated exact rational row addition.
- Owned private initialization creates the zero row, copying requires that
  zero row and the same chart, and discard requires the prescribed owned
  private register and chart. These are the inherited private-copy semantics,
  not a claim that a live copy was reversibly uncomputed to zero.

Inducting through every event proves the complete physical composition. The
checker reconstructs the expected ordinary Gram matrix directly from root
coordinates. At the end each source and each of the 72 dirty helper rows is
its original logical input; each target row is
`y_t + sum_s <r_t,r_s> x_s/2`.
Every endpoint frame also matches. Applying the target exit adapters gives
the stated intrinsic output charts. This covers arbitrary address functions,
not only scalar samples: the rows are identities of operators under the
verified common-chart invariant.

The source witness is hash-pinned to PR1972. None of its gather, dirty
compensation, delivery or query-cleanup algorithms is newly claimed here.
The new step proves that its abstract chart cancellations have this particular
exact native realization.

## 4. Accounting and controls

The independent occurrence recount gives
`{1:1074,2:58,3:86,4:104,5:48,6:24,7:8,8:8}`.
Rank mass is `2368`; the monotone boundary coverage is
`104*8 + 104*8 + 72*9 = 2312`, leaving eight rank-seven private descents.
There are 2624 scalar additions and eight each of private initialization,
copy and discard, for 4058 total events. No additional rank-zero endpoint
child is inserted.

Five actual faults reject: change a native recipe's global phase; remove a
transport recipe; corrupt a physical root image; set the first initial-query
compensation coefficient to zero; set the last query-cleanup coefficient to
zero. The last two preserve every transport index and are rejected by the
complete endpoint induction, not merely by an event-index mismatch.

## 5. Unresolved supplier obligations

This channel implements `G/2`, not `I`. A compatible `I-G/2` correction must
be integrated and priced. The 72 dirty width-nine roles are a local inventory,
not a chronological global owner map. The finite native identities do not
establish recursive precision, arbitrary-size lifting, all global residual
children or an improved recursive moment. No new kappa follows from this
certificate alone.
