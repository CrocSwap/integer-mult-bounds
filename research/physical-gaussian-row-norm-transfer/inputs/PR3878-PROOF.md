# Complete physical Gaussian expansion tile

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
I give a scoped implementation argument under the retained word, interval and
analytic source premises. The finite checks support the listed interfaces;
they do not establish a complete integer-multiplication theorem or independent
human review.

## 1. Quantified boundary and sources

I use the original global integers `s,t`, with `1<t/s<2`, integer `p>100`,
integer `2<=alpha<sqrt(p)`, and **exactly** `u=alpha²`. For a periodic complex
input `x_j`, `x_(j+s)=x_j`, `|x_j|<=1`, define

```text
(Sx/2)_v = (1/(2alpha)) sum_(j in Z)
           exp(-pi*(j-(s/t)*v)^2/u) x_j.
```

I implement one increasing target interval `[v0,v0+L)` from a supplied
increasing unwrapped source halo and its zero-padded capacity. The caller must
provide the periodic values at those original global indices. The consumer
checks framing, disk bounds and zero padding; it cannot establish periodicity
from one finite borrowed halo. A caller must use the matching coefficient
producer. A syntactically valid arbitrary factor page does not establish the
Gaussian coefficient premise.

I retain the source07 definition, rad20 blocked evaluator and microbox/bulk
contracts. Hanson Sun's PR1243 identifies the missing exponential generation,
normalized block and final-grid accounting. I retain Artus Krohn-Grimberghe's
PR371 correction: a fine-grid enclosure and a later target-grid truncation
have separate errors. The older combined S/E lemma assumes
`alpha^-2<=t/s-1`. I do not import that restriction or the complete combined
lemma. The expansion argument below uses only `1<t/s<2` and the stated
integer-alpha domain. PR3851 supplies the actual common physical cohort,
certified exponentials, exact signed prefix convolution and PR3787 word engine.
The nested sources retain their numerical and all-size review obligations.

## 2. Short stencil and factorization

Put `kappa=s/t`, `b=alpha*ceil(sqrt(p))`. Split the target interval into blocks
of length `1<=m<=b`, clipping its last block. For a block starting at `v0`, put

```text
j0 = floor(kappa*v0),  gamma = j0-kappa*v0 in (-1,0],
hlo = -b-1,  hhi = ceil(kappa*(m-1)-gamma)+b+1,
n = hhi-hlo+1,  nc = n+m-1.
```

The source window is `[j0+hlo,j0+hhi+1)`. Since `hhi<=b+m+1`,
`n<=2b+m+3`. For `p>100`, `b²/u<5p/4`, `b<p+sqrt(p)`, hence
`n<4p` and `nc<5p`. I use the exact identity

```text
U_h = ((1-kappa)*h²+2gamma*h+gamma²)/u,
V_z = ((kappa²-kappa)*z²-2gamma*kappa*z)/u,
K_d = kappa*d²/u,
U_h+V_z+K_(h-z) = (j0+h-kappa*(v0+z))²/u.
```

Because `b>=22`, `|h|<=2b+1`, `0<=z<b` and `|h-z|<=2b+1`, the following
loose bounds hold:

```text
|U_h| <= (2b+2)²/u < 20p,
|V_z| <= (b+1)²/u < 3p,
0<=K_(h-z) <= (2b+1)²/u < 12p.
```

No step uses a lower bound on `u*(t/s-1)`. With `sigma=4096p`, define

```text
A_h = 2^-sigma exp(-pi*U_h),
B_z = 2^-sigma exp(-pi*V_z),
k_d = exp(-pi*K_d),  c=1/(2alpha).
```

I use `pi<4` and `e<4` to obtain `A_h,B_z,k_d<=1`. The producer obtains
directed P-grid factors through the retained exponential owner; it checks
the upper enclosure endpoint is at most one. It uses exact unit factors
when the argument and scale vanish. It reuses `k_d=k_-d` through a fixed
owned tape and restores that tape's head after each scan. This reflection
changes setup work only.

Store source factor `A_(hlo+i)` at position `i` and kernel `k_(-hhi+r)` at
position `r`. Coefficient `n-1+z` of the ordinary convolution contains
kernel index `n-1+z-i`, which lies in `[0,nc)`, and its difference is
`h-z`. Thus the prefix convolution of length `nc` includes the complete
requested result. The consumer pads the weighted source from `n` to `nc`,
then discards the first `n-1` output positions and keeps exactly `m`.

## 3. Fine-grid arithmetic and final extraction

Put `P=32768p`, `eta=2^-P`. The producer returns nonnegative factors at most
one with absolute error below `4eta`. It returns
`c_hat=floor(2^P/(2alpha))/2^P`, so `0<c_hat<=1/4` and its error is below
`eta`. Work components use `W=P+ceilLog2(n+1)+3` bits. Their intermediate
magnitudes remain at most `n`, which fits this signed width. The exact
Kronecker child supplies its own packed-word carry guards.

For each real or imaginary component, the consumer performs, in order:

1. Exact promotion of the p-grid source; A multiplication and truncation at P.
2. Exact signed prefix convolution followed by one P-grid truncation.
3. B multiplication and P-grid truncation.
4. `c_hat` multiplication and P-grid truncation.
5. Truncation by `P-p-2sigma` numerator bits, which combines scale restoration
   and the final target-grid extraction.

For one component, compare each stage to its exact normalized counterpart.
The first-stage error is below `5eta`, and its magnitude is at most one.
The convolution error is below `(9n+1)eta`: charge `5eta` for each weighted
source, `4eta` for each kernel and one final truncation. The B stage adds
at most `4n eta+eta`, giving `(13n+2)eta`. The c stage gives at most
`((13n+2)/4+n+1)eta`, hence below `16(n+1)eta`. After scale restoration,
the complex internal error is below

```text
32(n+1)*2^(2sigma-P).
```

The header requires
`P>=2sigma+p+ceilLog2(32(n+1))+12`. The production values satisfy it with
room to spare. Thus internal complex error is below `2^(-p-12)`.

Every omitted source index lies beyond distance `b` from the target center.
A monotone integral estimate bounds the two normalized tails by

```text
(1/alpha + alpha/(2*pi*b))*exp(-pi*b²/u)
  < exp(-pi*p) < 2^(-3p) < 2^(-p-12).
```

I charge final component truncations separately, with complex error below
`sqrt(2)*2^-p`. For the complete tile, use the maximum over its disjoint
target blocks, rather than summing over the number of blocks. The result is

```text
||returned-Sx/2||_infinity
  < (sqrt(2)+2^-11)*2^-p < p²*2^-p.
```

The shifted Gaussian sum is at most `1+alpha`, by its maximum plus its
integral. Hence the exact S/2 operator norm is at most
`1/2+1/(2alpha)<=3/4`. Before final truncation, the computed norm is below
`3/4+2^(-p-11)<1`; component truncation toward zero cannot increase it.
The consumer also checks its returned disk-grid values.

Reduced-radius fixtures exercise the complete implementation and rounding
order. They do not satisfy this production tail proof. Their independent
reference reports bound the **maximum component error**, not complex modulus.

## 4. Production halo and complete stream

The production wrapper retains the paired compression domain:

```text
A=4096p³, L=2^ceilLog2(p^8), t dyadic,
u>=ceilLog2(8p), u*d<=p,
1/(4d)<(t-s)/s<1/(2d-1),
w=ceil(sqrt(ceil(16p/u)))+2, d>4w+2,
L>=64dA, s>2(L+2A+2w).
```

For tile `k`, I use target core `[kL,(k+1)L)` and target halo
`[kL-A,(k+1)L+A)`. I invoke the retained `ProductionPlan` on that halo and
the source core `[floor(kappa*kL),floor(kappa*(k+1)L))`. For target endpoint
`v`, its source-window endpoint is

```text
ceil(s*(2v-1)/(2t)),
```

because `q_j=floor(t*j/s+1/2)` belongs to an integer target interval exactly
between those two ceilings. I retain the principal complement, locality
margin and paired precision checks. Both positive and negative lifts use
this same endpoint convention.

The entire expansion stencil is
`[floor(kappa*kL)-b-1, ceil(kappa*((k+1)L-1))+b+2)`.
Each side has clearance greater than `kappa*(A+1/2)-b-3>A/2-b-3>0`
inside the source halo. The ratio and `L>=64dA` bounds imply source count
at most L, including endpoint discrepancies. The implementation checks
that inequality and pads the supplied source halo to capacity L.

For consecutive short blocks, their source left and right endpoints are
nondecreasing. Since `kappa<1` and each target step is at most b, the next
source window overlaps the previous one. The consumer validates the entire
capacity once, then scans it once in increasing order. It copies the first
window; for each next block it copies the retained suffix from one short
bank into the other and appends only newly reached source records. Equal
left endpoints and equal right endpoints are legal. It skips the remaining
source tail and padding once. It checks the complete ordered page catalogue,
common axis/precision, target positions and clipped final block.

## 5. Complete cost and ownership

For a block, count two input norm products, two A products per source record,
two B products, two c products and two output norm products per target record,
plus eight packed products for the two signed convolutions. The exact
FftWord call count is `4n+6m+8`. The tile adds `2*input_capacity` products
for its initial validation. These calls use the actual shared word owner.

With the retained `O(q log²(q+2))` q-bit word contract, the eight packed
products have q=`O(bp)` and cost `O(bp log²(p+2))`; the scalar products,
packing, cropping, carries and head restoration fit the same block bound.
Across all blocks, `sum n_i=O(L+b)`. Copying overlap banks and streaming
coefficient pages also costs `O((L+b)p)`. The complete online bounds are

```text
time  O((input_capacity+L+b)*p*log²(p+2)),
space O((L+b)*p),
prepared catalogue O((L+b)*p).
```

For production capacity L, these give `O(Lp log²p)` time and `O(Lp)`
space. The output itself has L records. Metadata operations and fixed
scratch restoration fit these bounds. A caller must retain the complete
catalogue and reuse it across incoming payload lines.

The producer uses exact rational metadata, directed exponentials and
sequential page copies. For fixed global parameters it performs a
polynomial number of operations on polynomial-length values in t,p.
Reflection scans add at most `O(b²p)` work per block. I charge total setup
time and scratch as **polynomial(t,p)**, separately from the per-line bill.
Only an enclosing tensor schedule with the required spectator stock may
absorb that term. This package does not implement that schedule.

Under the retained bulk scaling `d=p^.997`, the complete expansion
arithmetic contributes `p^(.997+delta)` per data volume for each fixed
`delta>0`. At `delta=.0001`, `.9971<.99827619697`, the authenticated full
Fourier power. This comparison covers expansion arithmetic only. A full
caller must also pay its global permutations, short mixed-radix moves,
periodic halo copies, page access and compression.

Each public owner reserves a fixed number of physical tapes before a call.
Inside a call it seals physical constructors, borrows canonical parameters,
suspends its scope around actual child owners and consumes protected child
returns. It restores borrowed values/heads and empties owned scratch on
success or failure. For paired reads, it opens the first value's ownership
scope before reading the second. The short-imaginary-input control exercises
that failure boundary. The checker disables decoded host dimensions during
the complete calls; host fractions and arrays belong only to reference tests.

## 6. Remaining joins

I leave the selected frontier unchanged. A complete transform still needs
the physical global coordinate gathers/scatters, short mixed-radix moves,
periodic halo routing, catalogue reuse and source-core assembly. A gather
that preserves canonical coarse-field order can move Theta(p) coordinates;
the caller must account for its full support, rather than pricing only the
selected low bits.

PR3763 must receive the complete natural target tensor: D source lengths,
D-1 flags and one final contiguous axis. Microbox coarse indices cannot
become independent chirp row batches. Count the actual D scalar axes in
`gamma=sum_i(2u_i+ceilLog2(32p)+1)`; rad20 uses D=d-1. Keep fine normalization
within each endpoint and apply the final global restoration once. The
retained outer norm at most 1/2 leaves room for expansion error before the
chirp's .6 bound. The CRT entrance/return and both final integer-recovery S
factors remain separate obligations. Reviewers must also assess the
inherited numerical recovery, supplier and source-correspondence premises.
