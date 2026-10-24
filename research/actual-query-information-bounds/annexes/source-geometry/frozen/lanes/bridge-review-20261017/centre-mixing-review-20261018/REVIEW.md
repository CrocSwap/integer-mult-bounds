# Independent review of the centre-matrix restriction

The all-cut result passes independent review for the stated fixed-source
class. The physical support proof is valid. It does not need independence
of formal warp words. The exact equations constrain all 64 entries of the
centre matrix. Their kernel is `A=c I8`.

The source inventory is complete for its declared equal-frame one-way
insertion grammar. A separate interval method gives the same 4,276
products. The exact 63-row determinant is `-2^71`. No claim about a new
supplier, total native-child lower bound, precision bound, or complete
kappa improvement follows from this result.

## Inputs and reproduction

The reviewed producer packets are:

- `oblique-native-20261017/interior-cut/ALL-CUT-SUPPORT.md`, its inventory,
  and `FRAME-SUPPORT.json`;
- `coherent-port/centre-mixing-20261018/MIXING.md`, `SUPPORT.json`, and
  their checkers;
- the actual clean core with decompressed SHA256
  `a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa`;
- the logical monomial definition in
  `new-native-recipes-20261017/sources/bw_adapters.py`.

The review receipt pins the producer files. The freeze file pins this
review and both checkers. The reviewer imported no producer code in the
independent checker. Run from the workspace root:

```text
python3 -I -B -O work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/centre-mixing-review-20261018/check_review.py
python3 -I -B work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/centre-mixing-review-20261018/replay_producers.py
```

The first command must print `PASS_INDEPENDENT_NATIVE_CENTRE_REVIEW` and
the determinant `-2361183241434822606848`. The second repeats the producer
checks. It redirects only their declared output writes into the review
directory and requires byte equality with the frozen outputs. It must
print `ALL_PRODUCER_OUTPUTS_BYTE_EQUAL`.

## Independent derivation

Let `q_s` be the actual odd binary label of source port `s`. Put the
computational-basis vector `|q_s>` in that source. Put zero in every
other source and in every Y, helper, and owned input. This is a legal
test input to an operation required to work for arbitrary borrowed state.

At a canonical cut, write `F` for a field's current binary subspace.
The logical content has support in `F` under the following conditions:

1. Its initial support is in its initial frame.
2. Every scalar ADD has equal source and target frames. A SCALE cannot
   change support. A CLEAR gives zero support in its declared new frame.
3. A native climb has nested frames `F_old` contained in `F_new`. Its
   logical content is unchanged; only its physical representation changes.
4. A logical monomial has an address map that sends `F_old` into `F_new`.

These conditions preserve the support statement by induction. They do
not require one-way scalar gates, an unchanged Y tail, or independent
operator words. Arbitrary complex phases on the supported addresses do
not change the argument.

For the actual current core, all 3,507 climbs are strict inclusions with
the declared rank difference. Each of the 240 signed warp occurrences
has address map `G` or `G^-1` and sends its old frame onto its new frame.
The source definition is `perm(G)` followed by a diagonal phase. Thus it
has no affine translation. Both providers have the required properties,
although their actual `G` matrices differ.

The initial X frame contains `q_s`. The final canonical Y frame at port
`t` is contained in `q_t`-perp. Therefore, if `q_t dot q_s=1`, the final
Y content has zero coefficient at `q_s`. Equivalently, every retained
response operator in the declared class satisfies

```text
<q_s | E_ts | q_s> = 0  when q_t dot q_s = 1.
```

This is a computational-basis statement, not a Fourier-character
statement. It remains true when different warp words have the same
physical operator or when sums of warp operators cancel. For a positive
tensor depth, use `(q_s,0,...,0)` as the input label. The address maps
fix zero in each other tensor factor. Thus the same witness works at
every tensor depth at least one. No claim at tensor depth zero is needed.

For the fixed-source producer class, the independent checker also
verifies the support statement directly at every source interval. It
uses actual signed binary matrices in the correct operator order. It
checks the frame containment for each reverse Y-tail interval. Thus the
proof does not rest only on the general induction.

## Complete cut and adapter audit

The independent checker first replays all 640 formal input columns. It
checks every scalar frame, all native changes, the full clean-J endpoint,
all 408 arbitrary helper outputs, the owned outputs, and all 91 private
zero-buffer lifetimes. It then builds maximal constant intervals for
each source row and frame. A separate reverse pass builds constant
intervals for each remaining Y-tail column and frame. It joins the two
interval lists by overlap at the same frame.

For each provider this gives 8,957 source intervals, 1,054 target
intervals, and 7,838 nonempty interval intersections. Their product set
is exactly the supplied set of 4,276 products. This method covers each
of the 23,389 literal cuts, including the initial and final cuts, without
using the producer's change-event enumeration. The producer replay
separately reproduces its 267,854 pair visits and its compressed payload
byte for byte. The two visit counts measure different enumerations.

The independent support pass checks 11,438 distinct source/frame terms,
including 1,880 terms with a nonempty warp word. It checks 1,030 distinct
target/frame pairs. These counts cover all source and tail intervals,
not only the product representatives.

Adapter events require care. A physical view change must not be ignored
when a new scalar read is admitted. The current replay finds 317 helper
view changes with an X-dependent branch. Every one is a `new_to_old`
adapter at FULL. No X-dependent helper branch passes through a proper-
frame residual wrapper. No Y frame is FULL. These FULL helper branches
therefore cannot give an extra one-way X-to-Y response through an
equal-frame scalar read. The fixed source branches at proper helper
wrappers are zero. The owned fields carry no X branch, and each private
Z field has frame FULL. These facts justify the omitted source types in
the supplied inventory for this obstruction.

The result does not treat access inside an atomic wrapper as an ordinary
cut. It does not identify two physical views merely because a stale
canonical frame number is equal. Source and target must have the same
actual canonical view at an admitted scalar gate. Before the entry
adapters the X fields do not match Y's zero frame. After the exit
adapters only FULL sources can have an X branch in a changed view, and
they do not match a Y field. This covers the fixed one-way class without
assuming that exit adapters act as identities on physical arrays.

There is a useful wider, explicit class. Keep the exterior prefix,
entry adapters, exit adapters, and exterior suffix fixed. Between the
last entry adapter and the first exit adapter, allow any scalar edits
that keep all current native frame changes and that satisfy the four
support conditions above. This includes changes to the source and Y
scalar subwords and Y-to-source feedback. The support induction still
holds. In the current event indexing this canonical section starts at
cut 7502 and ends at cut 17249. The resulting circuit must still meet
its endpoint and restoration contract. This wider statement does not
cover arbitrary edits through the physical wrapper boundaries.

## Full centre matrix and its consequence

Let `R` be the actual eight-row integer matrix and `K=R^T/4`. Consider
any constant scalar 8-by-8 matrix `A`. Suppose the retained response and
the centre response give a clean diagonal map:

```text
E + K A R = diag(d_0,...,d_111) tensor I.
```

Here `E` can initially be a sum of actual operator words. Apply the
matrix-entry functional from the support proof to each off-diagonal
pair with `q_t dot q_s=1`. Its value on `E_ts` is zero. Its value on the
payload identity is one. Hence

```text
R[:,t]^T A R[:,s] = 0.
```

There are 6,608 such pairs. They are equations on all 64 entries of `A`;
no symmetry or diagonal form is imposed. The supplied 63 pairs with the
column for `A[7,7]` removed have determinant `-2^71`. The independent
checker computes this by rational Gaussian elimination, rather than
the producer's integer Bareiss elimination. It also checks directly that
`I8` satisfies every one of the 6,608 equations. Thus the exact kernel
over the rationals or Gaussian rationals is `span(I8)`. Since the minor
is a power of two, the same linear-equation conclusion holds over any
commutative coefficient ring in which two is a unit.

There is also an analytic proof using two actual orthogonal port bases.
Their overlap graph is connected, and every nonzero overlap is a dyadic
unit. A matrix diagonal in both bases must then be scalar. The separate
`TWO-BASES.md` gives the general criterion and the 16-port witness.
`TWO-BASES.json` gives its exact overlap matrix and a spanning tree. This
explains the rank-63 result without using a large elimination.

Each column of `R` has squared norm four. Each port label is odd. The
same support witness at `s=t` therefore gives `d_s=c` when `A=cI8`.
Consequently every nonzero clean diagonal response in this family has
the form

```text
A = c I8,  d_0 = ... = d_111 = c,  E = c (I-KR) tensor I.
```

Over the rational or Gaussian rational field, a nonzero `cI8` has rank
eight. A factorization through seven scalar centre channels has rank at
most seven. It cannot give the required nonzero diagonal response.
Allowing odd denominators does not alter this obstruction.

The negative example `A=I8-ones(8,8)/8` has rank seven and has a nonzero
`KAR` diagonal at every port. It nevertheless fails 2,534 forbidden-pair
equations. This checks the distinction between a diagonal test and the
full centre-matrix condition. Duplicating a certificate row makes the
independently computed determinant zero.

## Limits and one checker qualification

The physical support proof and the integer minor establish a theorem
for the stated circuit class. The event inventory establishes that the
current native words meet its hypotheses. A finite inventory by itself
would not prove the theorem for changed native paths.

The result does not exclude an invertible off-diagonal retained response,
a port matching with orthogonal source and target labels, a changed
centre query or scatter space, a native inverse hop, a new address map
that fails the support condition, a mixed-view physical operation, or
operator-valued centre entries. Each escape needs its own access,
restoration, and complete cost analysis. In particular, this result is
not a lower bound of eight new native children for every possible
encoding.

One producer detail must not be generalized without a correction.
The source histories are stored with the outermost operator first.
Generic composition must therefore apply their linear maps in reverse
list order. The frozen `check_support.py` applies them in list order.
Every X history in its consumed inventory has length zero or one, so
the current checked result is unchanged. The independent checker uses
reverse order and confirms this length bound for all relevant source
intervals. A future packet with longer X histories must change that
loop. This is not a material finding against the frozen result.

No frozen producer file was edited. No PR, push, commit, or publication
was made. The user continues to require explicit permission before a
PR. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
The work builds on the current core, the oblique-native cut inventory,
the coherent-port centre certificate, and the prior native frame work.
OpenAI Codex assisted this independent review.
