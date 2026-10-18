# Exact selected coarse depth and the remaining stock implication

The two-level guard `73² > 2·48²` is already checked in Jeremy Kothe's frozen
PR1087 assembler and Rohan Arun's selected PR1094 invoice. It is predecessor
work. The new statements are exact integer depth thresholds, their sharp
logarithmic rate, and a better rational depth allowance.

## Quantified coarse contract

Let n be a nonnegative integer atom count. A coarse node is internal exactly
when `n >= m = 73`. Every paid coarse child has width `r*floor(n/73)` with r
in the complete selected histogram. Its maximum `R=48` occurs 4,866 times.
Conservative bad-residue children have rank at most one. Ordinary peeled
atoms, routing, adapters and high-part exchanges are separate completed calls.

These are explicit inherited floor-child, terminal and realization premises.
The generic finite-cover source identifies the good child as `rf` for `n=mf`
and bounds fallback widths by f. That historical source has different local
geometry; applying its width rule to the selected profile remains conditional
on the selected all-size lowering. This package does not prove that lowering.

Write `F(n)=48*floor(n/73)`. It is monotone and strictly below n at every
internal node. By induction in n, the complete tree's greatest number of
internal nodes on a coarse path is

```
D(n)=0                    if n<73,
D(n)=1+D(F(n))            otherwise.
```

Every child's depth is at most the rank-48 child's depth; the present rank-48
child attains the maximum. This includes the paid idle remainders, rather
than using just the local ADD profile.

## Exact thresholds and sharp rate

The smallest width b_d with `D(n)>=d` satisfies

```
b_1=73,
b_(d+1)=73*ceil(b_d/48).
```

Indeed `48*floor(n/73)>=b_d` iff `n>=73*ceil(b_d/48)`. This proves both
directions at every integer width. D(n) counts thresholds at most n. The
first thresholds are `73,146,292,511,803,1241,1898,2920`.

Put `a=73/48`. For d>=1,

```
73*a^(d-1) <= b_d <= (5329/25)*a^(d-1)-3504/25.
```

The lower bound uses `ceil(x)>=x`. The upper bound follows by solving
`b_(d+1)<=a*b_d+73` from b_1=73. Inverting these explicit bounds gives

```
lim_(n->infinity) D(n)/log2(n) = 1/log2(73/48).
```

No smaller logarithmic coefficient bounds this worst-path model with a fixed
additive constant. This is a depth statement, not a lower bound for other
suppliers, different terminal rules or multiplication.

## Rational allowance, with bounded optimality

Suppose positive integers p,q satisfy `73^p > 2^q*48^p`. A depth-d path,
d>0, has `n>=73*a^(d-1)` because its last internal node has width at least
73. For our domain q<=p, `73^p>2^q`, so

```
n^p >= 73^p*a^(p*(d-1)) > 2^(q*d).
```

For d=1 the last inequality follows directly from `73^p>2^q`; for d>=2
it also uses `a^p>2^q`. Thus, covering n<73 as well,

```
D(n) <= (p/q)*log2(max(2,n)).
```

Assignment seed 64 sets `1<=p<=64, 1<=q<=p`. All 2,080 pairs are checked
exactly; 1,227 pass. The smallest ratio in that domain is **43/26**.
A second implementation computes the largest q per p by integer division
and bit length. Both agree; RESULT.json records the strict integer witness.
No optimum over unrestricted p is claimed.

Finite replay compares forward recursion, inverse thresholds and an
all-child dynamic program. It covers every width 0..100,000, the first 64
threshold boundaries, and neighbors of `2^k` and `73*2^k` for 0<=k<=512.
These checks exercise the proof rather than replacing its quantified argument.

## Complete conditional parent-reserve formula

Fix q>1, 0<s<1, integer width e>=2 and positive integer atom width w.
Let C(w)>=1 be a per-level divisor actually sufficient for the selected parent
at atom width w, and S_leaf(e,w)>=1 any separately required inherited leaf
reserve. Under the fresh-role splitting and row-restoration contract,

```
S_parent(e,w) = C(w)^D(n) * S_leaf(e,w)
```

is sufficient. Both factors remain. Sequential residuals and the two-call
ordinary wrapper reuse restored rows. Completed inner ordinary calls borrow
internally from their supplied chunks, preserve outer spectators and restore
their row. Their internal stock remains in their completed contract; their
execution counts do not multiply the parent's external stock. This also does
not prove a numerical bound on either remaining factor.

If the full completed ordinary-leaf contract is available without an external
reserve, one may take S_leaf=1. A nontrivial S_leaf above is an explicitly
retained extra reserve, not a claim that completed leaves require one. Their
actual internal borrowing is still not measured by an external allowance.

For a parameter comparison at native stage 2 (`1+64%7`), the selected
assembler's s is source-bound in RESULT.json. This does not identify the
complex tree with the actual ordinary BIT bootstrap producer. For a complex
coarse construction using `w=ceil(e^s)` and body width at most e,
`n<=floor(e/w)<=e^(1-s)`. At this stage's widths e>=2,

```
log_q S_parent(e,w)
 <= (43/26)*(1-s)*log2(e)*log_q C(w) + log_q S_leaf(e,w).
```

For n>=2 use the depth bound and `log2 n <= (1-s)*log2 e`; for n=0 or 1
the coarse depth is zero. A further selected-domain proof of
`log_q C(w)<=A*w+B` and `log_q S_leaf(e,w)<=rho*w*(1+log2 e)`, with
A,B,rho>=0 and w>=1, would imply the sufficient envelope coefficient

```
sigma <= (43/26)*(1-s)*(A+B) + rho.
```

Actual A, B and rho are **not established here**. No comparison with cutoff
headroom discharges the full fit obligation. Neither historical m=120's
57,604 nor external 252 slack is substituted for these missing coefficients.

The frozen assembler and pinned PR589 record separately bind the BIT supplier
to m=64 and maximum child rank 42. Concurrent Adam Gall PR2084 makes the
ordinary BIT producer distinction explicit and proves a conditional GL64
parent envelope; PR2087 addresses its uniform time implication. Those are
separate provisional contributions, not dependencies or results claimed here.
The m=73 thresholds and 2,642-bit finite stock must not be identified with
that m=64 producer or its GL64 packet.

## Finite ledger comparison and its adoption boundary

The selected invoice has 14,826 physical families: 14,336 data/owner, 480
helpers, eight private centres and two coefficient-work families. Independently
multiplying its fixed Sp(72,2) order gives a 2,642-bit stock allowance B.
The selected assembler retains

```
2*B + 9909 + 252 + 1024 = 16469 < 20161.
```

If a parent divisor costs at most B bits per coarse level, the proven depth
allowance supplies `ceil(43*B/26)=4370` bits per `ceil(log2(max(2,n)))`.
Replacing only that modeled component gives

```
4370 + 9909 + 252 + 1024 = 15555,
```

a reduction of 914. Every other term stays charged, including 252 as
inherited external slack rather than an ordinary-leaf reserve estimate.
Whether the finite stock bounds uniform C(w), and whether the other ledger
terms permit this replacement, remain physical/compiler admission questions.
The second number is not an adopted complete row bound and is not substituted
into the selected receipt.

No gate, frame, copy, restoration, helper, source access or recursive child is
removed. The paid histogram and moments, retained 20,161 row cap and outer
constraints stay unchanged. The complex side still binds; there is no new κ.
