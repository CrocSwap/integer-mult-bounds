# Exact modulus admission for the inherited carry-count grade

This is a scoped audit of Chafik Boukhalfa's
[PR524](https://github.com/CrocSwap/integer-mult-bounds/pull/524),
head `9161fb1ff1c71bd8255e32d57ab5164aa8109376`.
It keeps the original grade recurrence and characterizes exactly which
positive moduli are safe for a specified box. The inherited choice `T=D`
is correct. Nothing here changes the selected multiplication bound.

## 1. Fixed model and statement

Let `D>=1`, let every `n_i` be a positive integer, and set

```
N = product n_i,  P_0 = 1,  P_(i+1) = n_i P_i,
I(a) = sum a_i P_i,                 0 <= a_i < n_i.
```

For an arbitrary positive integer `T`, retain PR524's weights:

```
w_0 = 1 (mod T),
w_(i+1) = n_i w_i - 1 (mod T),
g(a) = sum w_i a_i (mod T).
```

Call `T` **sound** if, for every pair `a,b` with `I(a)+I(b)<N`, and the
unique box coordinate `c` with `I(c)=I(a)+I(b)`, grade agreement
`g(a)+g(b)=g(c) (mod T)` holds exactly when `a+b=c` componentwise.
This quantifies over every coefficient array, not just a signed example
whose wrong terms might happen to cancel.

Let `j_0 < ... < j_(m-1)` be the indices of the **active** axes (`n_i>1`).
For `m>=2`, write `d_r = j_(r+1)-j_r` for the positive consecutive gaps.
Define the finite set

```
C = {sum_(r in S) d_r : S is a subset of {0,...,m-2}}.
```

For `m=0` or `m=1`, define `C={0}`.

**Theorem.** The attainable internal carry counts are exactly `C`.
Consequently `T` is sound if and only if no positive element of `C` is
divisible by `T`.

This is an all-shape integer argument. The accompanying exhaustive replay
is independent finite evidence, not a formal proof of this theorem or of
integer multiplication.

## 2. Necessity: every carry count is a gap subset sum

Ordinary mixed-radix addition gives

```
a_i+b_i+e_(i-1) = c_i+n_i e_i,
e_(-1)=0, e_(D-1)=0, e_i in {0,1}.
```

The last equality follows from the below-`N` restriction. The binary
carry bound also holds at radix one: at an active axis the sum is at most
`2(n_i-1)+1 < 2n_i`, and at a singleton axis it is just the incoming carry.

At a singleton axis all three digits are zero, so `e_i=e_(i-1)`.
Leading singleton axes therefore have carry zero. After the final active
axis a carry could never disappear, so that axis also has outgoing carry
zero. Between active axes `j_r` and `j_(r+1)`, the carry is the constant
bit `q_r=e_(j_r)` for exactly `d_r` internal positions. Thus

```
sum_(i=0)^(D-2) e_i = sum_(r=0)^(m-2) d_r q_r.
```

## 3. Sufficiency: every subset is realizable

Choose the bits `q_r` arbitrarily, and choose final outgoing carry zero.
For each active axis of radix `n>=2`, every incoming/outgoing pair `(u,v)`
has valid input and output digits. One uniform choice is

```
v=0:  (a,b,c)=(0,0,u),
v=1:  (a,b,c)=(n-1,1,u).
```

Both satisfy `a+b+u=c+nv`, and `0<=a,b,c<n`. At singleton axes use zero
digits and propagate the carry. These transitions compose with initial
and final carry zero. The resulting inputs lie in the box, their encoded
sum is below `N`, and their internal carry count is the specified subset
sum. The construction also covers `m=0,1`, where only count zero occurs.

## 4. Grade agreement and concrete false positives

Multiplying the digit equations by `w_i` and summing gives the original
PR524 telescoping identity, now modulo arbitrary `T`:

```
g(a)+g(b)-g(c) = sum_(i=0)^(D-2) e_i (mod T).
```

An internal carry exists if and only if the componentwise sum leaves the
box: the first carry must start at an active axis with `a_i+b_i>=n_i`.
Together with sections 2 and 3 this proves the criterion.

For any positive attainable count divisible by `T`, put one unit
coefficient at the constructed `a` and one at `b`, all others zero. The
true box-truncated convolution is identically zero, but the grade filter
places a unit at `c`. This is a concrete counterexample to that modulus,
not a failed search or a cancellation-sensitive numerical test.

## 5. Sharp consequences and limits

* If all axes are active, all gaps are one, so `C={0,...,D-1}`. A modulus
  is sound exactly when `T>=D`. Thus the original generic choice is sharp
  in this unchanged recurrence; a uniformly smaller modulus fails.
* With zero or one active axis, every positive modulus is sound. Leading
  and trailing singleton axes do not affect the carry-count set.
* For `m>=1`, any sound modulus has `T>=m`. Indeed, the `m` prefix
  positions `0,j_1-j_0,...,j_(m-1)-j_0` must have distinct residues: a
  repeated residue yields a positive contiguous gap sum divisible by `T`.
  Also the least sound modulus is at most `j_(m-1)-j_0+1`.
  Distinct prefix residues are necessary but not sufficient: gaps
  `(2,3,2)` have distinct prefixes modulo four, but the noncontiguous
  subset `2+2` still gives an alias.
* With exactly two active axes separated by gap `d`, soundness is
  precisely `T` does **not** divide `d`. For `d=lcm(1,...,K)`, every
  modulus through `K` fails despite only two active axes. There is no
  upper bound on the least sound modulus depending only on the active
  axis count, for the inherited recurrence.
* Soundness is not monotone in `T` below the safe upper bound. Shape
  `(2,1,1,2)` has `C={0,3}`: `T=2` is sound, `T=3` is not. Shape
  `(2,1,2,1,1,2)` has `C={0,2,3,5}`: `T=4` is sound, `T=5` is not.

Singleton compaction or a different recurrence is outside the fixed
model. Removing singleton axes recovers a safe modulus equal to the
number of remaining axes (or one for the all-singleton box). Therefore
the preceding negative statements are not lower bounds for unrestricted
convolution layouts, coordinate changes, or algorithms.

## 6. Complete representation cost and remaining obligations

The audit adapter keeps `X=2N-1`, the slot map `J(a)=I(a)+X*g(a)`, and
both possible grade-sum output slots from PR524. Its signed decomposition
uses **four** nonnegative integer products, including both cross terms.
For input magnitude bounds `A,B`, each nonnegative product coefficient
is at most `N*A*B`. Choose `b>=1` with `2^b>N*A*B`; then coefficient
carries cannot corrupt extraction. A zero operand gives a zero product.

The largest input slot is at most `(N-1)+(2N-1)(T-1)`. A full product
therefore needs at most

```
2(N-1) + 2(2N-1)(T-1) + 1 < 4TN
```

slots. This is only a representation bound. A smaller admitted modulus
can reduce this bound for a particular fixed layout; the least modulus
is not claimed to minimize actual occupied slots over all encodings.
Packing, extraction, permutation and the four integer multiplications
remain paid operations. No faster runtime, new recursive supplier,
Gaussian table certification, weighted tensor solve, or exponent saving
is inferred. PR489's phase-cell, tile, tensor-boundary, tape and all-size
obligations remain outside this audit.

## Attribution

The mixed-radix carry identity, signed four-product packing, index padding,
and coefficient bounds are Chafik Boukhalfa's PR524 work, building on his
PR489 experiment and the rank-filtered convolution literature cited there.
This note adds the exact attainable-count characterization, modulus
admission criterion and its scoped counterexamples. No broader originality
claim is made. Prepared for Ross Richardson with substantial OpenAI Codex
assistance, including the proof, implementations and adversarial review.
Apache-2.0; predecessor source and notices are unchanged.
