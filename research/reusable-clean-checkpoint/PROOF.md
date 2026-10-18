# One reusable clean array: contract and exact tree minimum

## Interface

Fix an abelian payload group and ordered, deterministic, zero-preserving
target-additive leaf increments f_j. A signed leaf updates t by +/-f_j(s),
leaves s unchanged, and reads immutable parameters. The negative leaf is an
exact inverse. Initial arrays, including all ancestor sources and targets,
are distinct. The one clean scratch array is initially zero; every other
scratch array is arbitrary. The interpreter is an indexed-RAM reference,
not a fixed-tape compiler. Its supplied matrices are immutable in execution.

At a binary node let B be the left subtree increment and A the right subtree
increment. A dirty connector z starts at z0. The forward sequence is

```
z += B(s)
t += A(z)
z -= B(s)
t -= A(z)
```

Each child restores its entire scratch pool before the next child begins.
Hence B sees identical source, scratch and immutable parameters on its paired
calls, and z returns to z0. The increment is A(z0+B(s))-A(z0), independent
of initial t. It is zero-preserving if A and B are zero-preserving. The
increment may depend on deeper dirty scratch for nonlinear leaves.

If z is the clean array, z0=0 and the last call can be omitted, because
A(0)=0. The three-call node restores z to zero. While z is live its children
receive only dirty scratch; they may not borrow z or any ancestor role.
If instead the parent reserves a dirty connector, the clean array remains
available to each child. It is zero again after each child, so sequential
subtrees reuse it without provisioning another clean array. These induction
steps prove restoration, target independence, zero preservation and exact
inversion (reverse the full instruction sequence, negate signs).

For linear leaves, A(z0+B(s))-A(z0)=A(B(s)). Thus every admissible tree
implements the original ordered matrix product. No commutation is used.
For nonlinear rounded leaves the tree may change the increment. Restoration
remains exact on the fixed grid, provided leaf inversion, target independence
and zero preservation hold; no equality of rounded outputs across trees or
scratch-independence of nonlinear increments is asserted.

## Exact minimum in the defined class

Let D(I,s) be the minimum signed-leaf charge for an interval I with s dirty
arrays. Let C(I,s) use s-1 dirty arrays and one reusable clean array. Both
are restricted to ordered binary trees with reserved connectors that remain
unavailable to descendants for the full node invocation. Leaf prices t_j
are positive integers bounding either sign at one common precision.

For a singleton both values are t_j. A nonleaf with insufficient resources
has value infinity. At every nonempty contiguous split I=L followed by R:

```
D(I,s) = min [2 D(L,s-1) + 2 D(R,s-1)]
C(I,s) = min {
    2 D(L,s-1) + D(R,s-1),             clean connector
    2 C(L,s-1) + 2 C(R,s-1)           dirty connector, s >= 2
}
```

Every admissible tree has exactly one such root choice and split. Conversely
each finite entry composes legal children under the reserved-connector rule.
Induction on |I| proves the minimum over this class. It is not a minimum over
all reversible programs, higher-arity trees, or alternative lifetime rules.
A factor count larger than 2^s is impossible because every binary leaf path
has at most s reserved connectors. In C a path with no clean reservation may
use only s-1 dirty connectors. The independent census instead computes these
path constraints and the product of edge multiplicities on decorated trees.

For t=(1,3,1,1), s=2, a clean-root tree must split 2+2 and costs
2*(2*1+2*3)+(2*1+2*1)=20. A dirty root with two clean children costs
2*(2*1+3)+2*(2*1+1)=16. Each child returns the same clean array to zero.
The node constraints force these shapes at cap two, so 16 is the class minimum.
The actual word has factor multiplicities (4,2,4,2); charging each invocation
at the given prices gives 16. The root-only word has (4,4,2,2), giving 20.
Both contain twelve invocations. With unit prices these two shapes tie.

There are extra internal dispatches: the reusable word executes one dirty
node and four clean nodes; the root-only word executes one clean node and
three dirty nodes. Both execute twelve leaves. If those equal-sized node
dispatches cost g_D and g_C, respectively, and leaf dispatch costs g_L,
the complete local charges (excluding identical preparation/routing) are
16+g_D+4g_C+12g_L versus 20+3g_D+g_C+12g_L. The saving survives exactly
when 3g_C-2g_D<4. For equal internal price g this is g<4. Unequal routing
or preparation must also be included; no wall-time improvement is asserted.

## Complete work, memory and precision accounting

The displayed D/C formulas optimize only one specified signed-leaf bill.
Each t_j must include preparation internal to a leaf, source/target scans,
coefficient/phase access, arithmetic, and restoration. External parameter
preparation is charged separately. If sign prices differ use their maximum,
or a sign-aware extension; the current optimizer does not claim that optimum.

For a fixed tree let R(t)=t_j+g_leaf at a leaf. At a dirty node,
R=2 R(left)+2 R(right)+g_dirty; at a clean node,
R=2 R(left)+R(right)+g_clean. These g terms pay dispatch, descriptor and
alias checks, controller work and any per-invocation parameter scans. Exact
signed word costs can replace upper prices when measured. The complete charge is

```
factor/phase preparation + clean provisioning + clean admission scan
+ R(tree) + routing/access work not already charged + optimization cost.
```

No child connector is cleared by erasing borrowed information. Provisioning
requires a real clean length-L array (L writes when that operation is allowed),
and admission scans L values. Data scratch is exactly s arrays of L words,
one initially zero, apart from source and target. This work may need s+2
payload arrays plus scalar arithmetic workspace and immutable descriptions.
Magnitude bits as well as fractional bits count toward each word's storage.

The interval optimization has O(n^2 s) cached entries and O(n) split choices
per entry, hence O(n^3 s) arithmetic comparisons (with integer bit costs).
The reference stores literal tree tuples; this is offline preparation, not a
free runtime oracle. A descriptor implementation can use child references.
The emitter materializes N instructions, O(N) memory and time; the interpreter
uses that representation. A streaming compiler could avoid the materialized
word, but is not supplied here. Array admission and instructions are validated
before mutation. Matrix dimensions and the leaf contract remain caller
obligations; failures of a supplied leaf are not transactional.

Conditionally inherit a per-leaf ideal norm bound K and local error
a*u*(B+1), u=2^-w, for both signs. Put G=2+K, assume a*u<=1, and bound all
initial array norms by D0. After j leaves M_j+1 <= G^j(D0+1). Comparing the
complete word to its ideal linear word yields
e_(j+1) <= (1+K)e_j + a*u*G^j(D0+1), hence
e_N <= N*a*(D0+1)*u*G^(N-1).
For requested error 2^(-p-1), one sufficient common precision is

```
w >= p+1+ceil(log2(N*a*(D0+1)))+(N-1)*ceil(log2(G)),
```

together with inherited stability conditions. Preparation must separately
meet its scaled error budget. This is a conditional pathwise estimate; the
package does not prove PR628's leaf accuracy or improve its precision order.
The weighted gain uses the SAME twelve calls and does not imply lower N.

The local weighted fixture does not supply actual cheaper factors, a new
hosted operator or a complete supplier moment. PR673's direct all-role
adapter obstruction remains applicable: its favorable unit-leaf bill already
fails. No new kappa, analytic transfer or complete multiplication proof follows.
