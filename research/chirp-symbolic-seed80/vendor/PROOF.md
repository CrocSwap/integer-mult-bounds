# Exact streamed chirp phases and the scalar cost row

## Changed cost, unchanged numerical map

The retained chirp array, in the original padded tensor order, is

```
a(j) = exp(-pi*i*sum_i s_i*j_i^2/t_i),
E(j) = -sum_i s_i*j_i^2*(r/t_i) mod 2r,
a(j) = exp(2*pi*i*E(j)/(2r)).
```

Here r=2^ell, t_i is r or r/2, t_i>=2, and 0<s_i<t_i. The application
has odd prime s_i, but this phase generator needs only these integer bounds.
There are T=product(t_i) entries, p-bit coefficient precision, and
`d*ell=O(p)` in the original padded box. The source's chirp paragraph
charges each of the d index calculations as if it needed a full p-bit
multiply, giving `O(T*d*p^(1+delta))`. The phase is already fused into one
exponential per entry; we do not claim to discover that fusion.

We supply both a width-sensitive bound and an exact additive stream. Either
gives complete chirp generation in `O(T*p^(1+delta)+poly(p))` for every
retained fixed delta>0. Twist products, coefficientwise scalar products and
format adapters already fit this bound. Polynomial-ring products on O(rp)-bit
packed records are a separate cost and are **not** included in this change.
Thus this **scalar cost row** has normalized
exponent delta and saving `1-delta`, instead of `1-epsilon-delta`.

Every generated residue E is the original exact residue. Call the same
retained disk-grid exponential routine with the same E, denominator 2r and
precision p. Its output and error guarantee are unchanged. There is no new
transcendental approximation, normalization, phase convention or input order.

## Direct width-sensitive computation

An index j_i and source s_i each have at most ell bits. The square has at
most 2ell bits, its product with s_i at most 3ell bits, and multiplication
by r/t_i is a shift by zero or one bit. Reduce every term modulo 2r before
adding it to the running residue. Only O(ell)-bit arithmetic is required
for each term, including the modular accumulator.

Using the already retained unconditional multiplier on these short integers
costs `O(ell*log(2ell))` per term. Descriptors s_i,t_i and coordinates j_i
are serialized as O(ell)-bit fields, not padded to p bits individually.
One scan through all d fields costs O(d*ell). Consequently the phase cost
per coefficient is

```
O(d*ell*log(2ell)) = O(p*log(2p)).
```

Coordinate extraction and resetting those short fields are also charged to
the O(d*ell) scan. The one precision-p exponential then costs
`O(max(p,log(2r))^(1+delta)) = O(p^(1+delta))`, using the unchanged cited
scalar interface in the source. The descriptor scan no longer contributes
a factor d to that cost. No improved multiplier is called on its own input
size; these control records and coefficient products are strictly short.

## An additive generator with an explicit tape schedule

Put Q=2r and `A_i=-s_i*(r/t_i) mod Q`. For each axis store its radix,
current index j_i, value `v_i=A_i*j_i^2 mod Q`, and forward difference
`Delta_i=A_i*(2j_i+1) mod Q`, together with A_i. Keep the global residue
`E=sum_i v_i mod Q` on a separate work tape. Initially j_i=v_i=E=0 and
Delta_i=A_i.

Emit E, then advance the last axis, carrying left in lexicographic order.
At an axis whose index is not last:

```
E       <- E + Delta_i       mod Q
v_i     <- v_i + Delta_i     mod Q
Delta_i <- Delta_i + 2*A_i   mod Q
j_i     <- j_i + 1
```

At a wrapped axis:

```
E       <- E - v_i           mod Q
j_i,v_i <- 0,0
Delta_i <- A_i
```

Then carry to its left neighbor. When every axis wraps, stop; no full-width
remaining-output counter is required. The identities
`(j+1)^2-j^2=2j+1` and `2(j+1)+1=(2j+1)+2` prove the invariant at every
ordinary increment. Subtraction of the old v_i proves it across every
carry, including simultaneous carries. Thus the emitted sequence is exactly
the original E(j), and the final complete rollover restores E=0 and all
initial axis states. There is no precomputed table of T phases.

Store the d axis records consecutively on one tape, fastest axis last.
Each record has O(ell) bits; each visit scans a fixed number of its fields.
The carry head only walks to adjacent records and then returns across the
records just visited. The global E tape uses O(ell) bits and is restored to
its starting head position after each update. The coefficient and phase
output tapes advance sequentially. The retained exponential subroutine uses
its fixed work tapes between visits; the axis tape can remain parked.
This is a fixed tape count, with O(d*ell)=O(p) persistent phase state.

Over a complete T-entry stream, the exact number of axis visits is

```
V_axis = sum_i T / product_(j>i) t_j < 2T,
```

because all radices are at least two. Returning the head adds at most the
same number of record traversals. Modular arithmetic costs O(ell) per
visit, so phase generation costs `O(T*ell+d*ell)` bit operations. Reading
the source descriptors and forming A_i use only shifts and modular
negations on O(ell)-bit words. Intermediate signed sums fit a constant
multiple of ell bits. The precision-p exponential and coefficient output
dominate this cost. Verifier statistics and materialized coordinate tuples
are not required by the generator or this tape schedule.

## Numerical and operator interfaces

The scalar routine already returns a disk-grid approximation with error
less than `2*2^-p`. We pass the same exact integer residue and denominator,
so no new precision loss is introduced. Retain the original exact dyadic
endpoint products and their component truncations. The chirp convolution
identity and its error proof therefore apply without a change.

For every pair of tensor addresses j,k, periodicity of the even t_i gives

```
E(j-k mod t) - E(j) - E(k)
  = 2*sum_i s_i*j_i*k_i*(r/t_i)  mod 2r.
```

This checks the coefficient identity underlying the retained permuted
Fourier transform, including wrapped differences and the sign of the phase.
Conjugation uses the same generated array as before. The FFT layouts from
#475 are internal to the convolution; the chirp interface remains in the
original tensor order. No source or frequency permutation has been dropped.

The executable generator is an exact reference implementation and the finite
checks test its residues, carries, widths, period and operator exponents.
They do not execute the cited high-precision exponential or a full multiplier.
Equality of its exact inputs is the transfer argument for that unchanged
routine. Nor is the Python runtime a measurement of the fixed-tape bound.

## Remaining barriers

Only `scalar_work` improves from `1-epsilon-delta` to `1-delta`.
The Gaussian arithmetic margin is still
`min(1-epsilon-delta,r-delta)`, so it was already no larger than the old
scalar margin. Changing this row alone cannot improve the current minimum.
The source-bound arithmetic control verifies this fact with #472's exact
parameters and leaves every other constraint intact. It is not a new finite
supplier invoice or a higher-kappa certificate.

Together with #475, this removes reserved-axis, exceptional top-bit and
scalar-chirp costs from the list of independent bottlenecks. Gaussian line
application, normalization `epsilon+r<1`, and the separate small-field
exposure condition remain, as does the separate polynomial-product dimension
margin. Those require actual constructions or tighter
justified bounds of their own. Kappa=1 is not established.

Prepared by chafreaky with OpenAI Codex assistance. The chirp formula,
permuted Fourier identity, scalar exponential interface and asymptotic size
bands are retained from the source-pinned integer-mult-bounds manuscript and
its credited authors. Exact quadratic differences are elementary; no claim
of literature priority is made. Apache-2.0.
