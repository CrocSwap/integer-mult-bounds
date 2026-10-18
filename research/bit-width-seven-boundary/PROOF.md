# Two necessary conditions for a BIT helper endpoint

This proof concerns a finite frame word over F2. A frame is a rational
subspace of Q^8. A register can move only to a frame that contains its
current frame. Every scalar operation is linear, invertible, and acts on registers
at one common frame. ADD gates and register permutations satisfy this rule.
The suffix can use any number of these operations and any rational frames.
It can use extra dirty registers if it restores them. It has no new COPY,
descent, reset of a nonzero register, or other operation outside this model.

The selected prefix fixes the scalar state and frame of every register at
the cut. Write the scalar state as w = M u. The vector u contains all source,
target and dirty-helper inputs. M is invertible: each prefix scalar gate,
including each scatter addition, is an invertible transvection over F2.
At completion, source x_i must contain x_i, target y_i must contain y_i+x_i,
and helper h must contain its original input s_h. No other final register
can contain s_h. Extra dirty registers must also return their own inputs.

Let F_r be the frame of register r at the cut. Suppose helper h ends in U.
Its frame at the cut must satisfy F_h <= U.

## 1. Restoration condition

Let a be the unique row such that s_h = sum_r a_r w_r. Every register on a
dependency path into a final register at U has a frame contained in U.
This follows from common-frame operations and monotone frame changes.
Thus the final value of h can depend only on boundary registers r with
F_r <= U, and on fresh inputs independent of u.

The boundary coordinates w_r are independent because M is invertible. If
a_r = 1, changing w_r alone changes s_h. Therefore each such r is required:

    span(F_h, {F_r : a_r = 1}) <= U.                 (R)

This argument also permits nonlinear operations on the available inputs.
No nonlinear method can compute a parity without every essential input.
We use only its consequence for the reversible linear frame-word class.

The selected word has no target-to-z edge, where z consists of sources and
helpers. Its z boundary matrix is invertible. Consequently, the restoration
row a uses only z registers. The derivation obtains a by reversing the z
gates. The checker obtains it by Gaussian elimination of the actual boundary
matrix. It does not read or import the derivation program.

## 2. Erasure condition

Fix U. Call a register high when its frame is not contained in U. Let S be
the F2 span of the current scalar rows of all high registers.

A frame change cannot make a high register low. A low-to-high frame change
adds one row to S. A common-frame scalar operation either acts entirely on
low registers, or entirely on high registers. In the second case it is an
invertible change of basis of the affected high rows. Thus S never loses
a vector throughout the suffix.

The final helper h is low. Every final high register has zero coefficient
of s_h, because every other register has its required final value. Hence
every vector in the final S has zero coefficient of s_h. The same must hold
for the initial S. If M[r,h] = 1, register r therefore cannot be high:

    span({F_r : M[r,h] = 1}) <= U.                  (E)

This condition uses the complete dirty column. A small restoration row
alone does not suffice. Extra restored dirty registers do not weaken (E).
They begin with independent inputs and end with zero coefficient of s_h.

Combining (R), (E), and the frame already held by h gives the lower bound

    dim U >= dim span(F_h,
                      {F_r : a_r = 1},
                      {F_r : M[r,h] = 1}).

There is no frame-catalogue restriction in this statement. A rank-eight
join excludes every proper subspace of Q^8, including an unlisted frame.
The bound remains necessary if several helpers receive smaller endpoints
at once. Each final output other than h still has zero s_h coefficient.

## 3. Application to the selected PR589 word

The input is the exact tuned R439 word in SOURCES.json. The certificate uses
original register identifiers, including sources 0..110, targets 111..221,
and helpers 222..660. The input has 661 independent dirty-input coordinates.

Immediately after D, A and the retained-total scatter, the joint bound has
rank eight for 433 helpers. It has rank seven for exactly these six:

| Helper | Necessary terminal hyperplane, in the selected catalogue |
|---|---:|
| 465 | 512 |
| 466 | 514 |
| 468 | 513 |
| 469 | 517 |
| 470 | 513 |
| 476 | 514 |

For a rank-seven row, the certificate contains seven independent vectors
and a nonzero integer normal that annihilates every required frame. These
six rows pass a necessary condition only. The proof supplies no suffix,
caller window, or paid construction for them.

At the cut after the selected B, condition (R) alone has rank eight for all
439 helpers. Thus no replacement cleanup C in this class can reduce even
one selected helper to width seven. H4 is not used: C need not be the literal
reverse, need not use full-frame gates, and can have any finite length.
Allowing target reads, new restored dirty work, or different gate order does
not change the lower bound.

Each rank-eight certificate lists eight line vectors, their boundary donor
registers, and a nonzero integer determinant. The checker verifies that each
line is in the stated register's current frame and that the register belongs
to the required row or column. It checks the determinant by fraction-free
integer elimination. It checks all 439 helpers at both cuts. This is an exact
finite certificate, not a formalization of the full multiplication theorem.

## 4. Rank-one entrance with a semantic compensation prefix

Keep the raw A/scatter/B entry state z and the zero frame of each target.
Require D to provide all dirty-target compensation before A. A later cleanup
does not supply missing target compensation in this entrance class. This is
a separate restriction from the endpoint classes in sections 1 and 2.
The raw target map is y -> y + x + K s. The required compensation prefix is
therefore y -> y + K s, regardless of its particular gate list. It can use
an arbitrary common-frame circuit, provided that it returns z to the same
raw entry state and leaves the targets at frame zero.

Every column of K in this word is nonzero. The certificate records the
complete list of target rows for every helper. The checker verifies these
lists and the complete dirty endpoint of D/A/scatter/B/C.

If helper h starts in a nonzero frame E, no target ending the prefix at
frame zero can depend on its independent input s_h. This is the dependency
argument in (R), applied to the compensation prefix. Yet a nonzero entry
K[t,h] requires precisely that dependence. The contradiction excludes a
rank-one entrance in this prefix class for every selected helper.

This is a semantic condition. It does not merely enforce the old H2 syntax.
It does not apply to a changed helper basis at the raw entry, a changed A
or scatter, compensation moved after A, or a new
recursive interface. Those mechanisms remain outside the result.

## 5. A paid bridge that does not help

One constructive attempt preserves the selected later source use by adding
a new dirty bridge. Consider a helper whose last raw frame has rank seven,
such as 469. Let the new bridge read a source at rank one, deliver that value
at rank seven, and restore at the full frame. Its paid path is 0 -> 1 -> 7 -> 8.
This path costs children of ranks 1, 6 and 1. Permit every other new operation
for free in this lower-cost model.

Put the bridge's width-eight residual in the old helper's hosted slot. Put
the converted width-seven helper in a formerly idle rank-seven slot. The old
helper loses its final rank-one child. Including the consumed idle child,
the change per local call is exactly

    Delta n_1 = +1, Delta n_6 = +1, Delta n_7 = -1.

Rank mass is unchanged. The number of children grows by one. For 0 < a < 1,
the bit moment weight is g_a(r) = 64^a r^(1-a). Strict concavity gives
g_a(1) + g_a(6) > g_a(7). The inherited surcharge also grows with the child
count. This optimistic complete profile is worse than the selected profile.
Additional source access, compensation or restoration work cannot rescue
this specific wrapper at unchanged live stock and precision allowances.
This excludes that wrapper,
not every method that uses an extra helper.

## Scope

The selected endpoints have start rank zero, so terminal rank eight means
residual width eight. The after-scatter result excludes 433 individual
conversions when the prefix is fixed. It does not exclude changes to that
prefix, to the retained copies, to helper coordinates, or to the frame
transport interface. The six survivors are not an existence theorem.

The argument uses the selected finite scalar/frame model. Its all-size
compiler, common-label and mutable-source realization, physical hosting,
precision/tape and analytic transfer assumptions remain inherited. No full
native supplier, new exponent, practical speedup, or universal BIT lower
bound is asserted.

Prepared for Ali Romman, with substantial OpenAI Codex assistance.
New material is Apache-2.0.
