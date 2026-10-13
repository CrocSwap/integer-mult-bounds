# Balanced dirty commutators: prefix bounds and quartic precision

This audits the conservative per-leaf growth estimate in PR628's
`DIRTY-PROOF.md`, pinned and retained under `vendor/pr628/`. Its old bound is
valid. We give a smaller sufficient execution budget for its **unchanged
balanced binary dispatcher and unchanged rounded leaves**. No minimum
precision, physical implementation or new multiplication exponent is claimed.

## 1. Ideal prefixes, including their inverses

Let `A_1,...,A_n` be arbitrary composable linear maps on a common normed
space, with operator norms at most `K >= 0`. Use the maximum norm on the
joint source, target and borrowed arrays. Assume distinct ancestor and child
arrays, with one reserved connector per recursion depth, as in PR628. All
initial arrays may contain arbitrary data. No factor commutativity is used.

Set `C=1+K`. A complete m-factor ideal child is a shear with multiplier
`A_(j+m-1)...A_j`, and restores its source and deeper scratch. Its norm and
its inverse's norm are at most `1+K^m <= C^m`. This uses the ordinary ideal
commutator identity, not an assumption about rounded linearity.

Define

```text
E(1) = 1,
a = floor(n/2), b = ceil(n/2),
E(n) = n + max(a + E(b), b + E(a)).
```

**Prefix lemma.** Every ideal primitive prefix `P_j` of either sign of the
balanced word satisfies

```text
||P_j|| <= B,   ||P_j^-1|| <= B,   B = C^E(n).
```

The empty prefix is included. At a binary node write U for the left child's
source-to-connector shear and V for the right child's connector-to-target
shear. The positive chronological word is `U,V,U^-1,V^-1`; the negative word
is `V,U,V^-1,U^-1`. A prefix consists of completed children and a prefix
inside the next child. The largest completed-child degree before an active
b-child is `2a+b=n+a`, and before an active a-child is `a+2b=n+b`, allowing
both signs. Induction and submultiplicativity give the stated recurrence.
For the inverse of that prefix, reverse and invert the completed factors
and the active child prefix. The same product of norm bounds applies. We
do not infer an inverse-prefix bound merely from a forward-prefix norm.

Inductively **`E(n) <= 4n-3`**: the two bounds become `2a+5b-3` and
`5a+2b-3`, both at most `4(a+b)-3`, since the balanced positive sizes satisfy
`a <= 2b` and `b <= 2a`. For powers of two the exact recurrence is
`E(n)=3n-2`. The recurrence is a sufficient majorant, not the exact maximum
norm or a lower bound on required precision.

Every ideal propagator between two primitive boundaries consequently has
norm at most **`B^2`**, since it is `P_j P_i^-1`. This is where the inverse
prefix bound is needed. A small final product alone would not control the
intermediate dirty computation.

## 2. Rounded execution with arbitrary initial dirt

Suppose each executed leaf is a deterministic signed shear that restores its
source exactly, computes its increment independently of its target, and
approximates its ideal linear map with error at most

```text
a u (||source||+1),   u=2^-w,   a>0.
```

Here `a` denotes the error constant, no longer the left subtree size. Let
`D` bound the norm of **all** initial arrays. Let N be the actual complete
leaf count, including inverse and restoration calls. PR663 gives, equivalently
to the elementary recursion `N(n)=2N(floor(n/2))+2N(ceil(n/2))`,

```text
N(n) = 3 q n - 2 q^2,   q=2^floor(log2 n).
```

Let M be the maximum actual joint norm over all leaf boundaries. Inserting
the actual leaf errors into the ideal linear recurrence is exact even though
each error depends nonlinearly on the current source. Variation of constants
and the prefix lemma give

```text
M <= B D + delta (M+1),   delta = N B^2 a u.
```

If `delta <= 1/2`, then

```text
M <= 2 B D + 1,
execution error <= 2 N B^2 a u (B D+1).
```

The last error is for the whole joint state against the exact ideal word;
it therefore also bounds the target error. Exact source and dirty restoration
still follow from the predecessor's deterministic shear/inverse identity,
with immutable nonaliased phase/factor data. This proof neither assumes a
rounded child is linear nor claims its output is independent of dirt.

For any desired execution accuracy `2^-t`, `t>=0`, it suffices to use

```text
w >= t + ceil(log2(2 N B^2 a (B D+1))).
```

This also implies `delta<=1/2`. Retain the input grid and every separate
leaf-admission condition. All bounds are independent of cyclic length L.

## 3. The inherited prime-power inverse and the complete bill

For PR628's n=r-1 prepared factors, the inherited leaf lemma has
`K=r/beta`, `a=13(r+1)/beta^3`, and requires `u<=beta^2/2`. Its root-gap
budget supplies `beta >= 2^-g` with `g=O(r^3)`. If `D<=2^d`, set

```text
A = 3g + ceil(log2(13(r+1))),
H = g + ceil(log2(r+1)),
w = max(A, 2g+1, p+3+ceil(log2 N)+A+d+3 E(n) H).
```

Indeed `a<=2^A`, `B<=2^(E H)` and `BD+1<=2^(EH+d+1)`, so the execution
error is at most `2^(-p-1)`. The smallness and leaf closure conditions hold.
If initial inputs have a finer dyadic grid, replace w by the maximum of w
and their fractional precision; an array cannot be silently coarsened.

Keep PR628's **unchanged coefficient/phase preparation** at target
`p+1+d`. Its perturbation bound for the original source contributes at most
`2^(-p-1)`, hence the total error is at most `2^-p`. Initial dirty data
enters the execution budget D; it does not enter the ideal operator's
coefficient perturbation. No unimplemented preparation algorithm is supplied
by this audit.

Since `E(n)=O(r)` and `N=O(r^2)`, this proves the alternative sufficient guard

```text
w = O(p + d + r^4),
```

instead of the old `O(p+d+r^5)` growth bound. Integer magnitude bits at leaf
boundaries are `O(d+E log(1+K))=O(d+r^4)`. The inherited causal passes and
closure scalars add `O(log(beta^-1)+log r)` magnitude bits inside a leaf.
The bound is on complete word size after also retaining any finer input grid.

All **N leaf calls remain paid**: each retains validation/access, causal,
output and undo passes. With inherited fixed-precision arithmetic and
preparation, the local neighboring-layout bill becomes

```text
soft-O((L r^2 + r^3) (p + d + r^4)),
```

plus charged phase access and the predecessor's arbitrary-stride routing.
Borrowed storage remains `ceil(log2 n)` length-L arrays, arbitrary initially,
with `O(L log r)` words; scalar arithmetic, indexing and factor descriptors
retain the predecessor's charges. No clean length-L array, free copy, or
discarded restoration call is introduced. The rational reference code is
not an implementation or benchmark of the asymptotic bit-cost algorithm.

This improves one local precision upper bound. It supplies no admitted
common-label/Clifford or reversible-bit word, physical owner layout,
complete-transform recurrence or multiplication reduction. The selected
supplier and κ are unchanged. PR862's cubic guard uses owned widened words
with reserved zero bits; its storage contract differs from this dirty-array
result. General multiway or optimized unequal trees are outside this proof.

Credit Chafik Boukhalfa / chafreaky for PR628, 0xkilgore for PR663's exact
count and nonlinear restoration audit, androolloyd for PR673's multiway and
phase-alias work, and the original sources retained in the vendor notice.
The perturbation argument is a standard variation-of-constants estimate;
no literature-priority claim is made. Written for Gareth Davidson (@bitplane)
with substantial OpenAI Codex assistance; Apache-2.0. Finite evidence below
supports this handwritten argument, not formal verification of the full
multiplication theorem.
