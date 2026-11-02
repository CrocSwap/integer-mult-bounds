# An unbiased reversible lattice rotation

This contribution was produced by Nick Petalas. Apache-2.0.

Put

```text
B = [[3,-4],[4,3]],        A = B/5.
```

Thus A is multiplication by the unit complex number (3+4i)/5. The input and
output lattices are both Z^2. A seed is supplied uniformly from five states,
independently of the input. The seed is retained for inversion.

## The statement

There are five bijections F_s:Z^2 -> Z^2, for 0 <= s < 5, such that for every
x in Z^2:

1. F_s(x+5z)=F_s(x)+Bz for every integer z.
2. E_s F_s(x)=Ax.
3. If Ax is integral, F_s(x)=Ax for every seed. Otherwise
   E_s ||F_s(x)-Ax||_2^2=2/5.
4. For every individual seed and input, ||F_s(x)-Ax||_2^2 <= 4/5.

The expected squared error in item 3 is the smallest possible at each x
among all unbiased integer-valued random outputs, even without requiring
reversibility. In particular the worst-input expected squared error 2/5 is
optimal for the declared unbiased contract. The last item's deterministic
bound is an attained bound of this construction; no new optimum for a
single deterministic bijection is asserted.

The witness is TABLE.json. Its five tables each have 25 pairs. Row i=5r+t
corresponds to the residue (r,t), with 0 <= r,t < 5. Write o_s(r,t) for that
pair. Define, using coordinatewise Euclidean division,

```text
x = 5q + (r,t),             F_s(x) = Bq + o_s(r,t).
```

This is a definition on the entire unbounded lattice, including negative
inputs. No clipping, saturation, inward norm constraint or bounded entrance
domain is imposed.

## A finite certificate for each all-lattice bijection

For y=(u,v), define

```text
K(y) = (3u+4v mod 25, -4u+3v mod 25).
```

Two integer points y,y' have the same K exactly when y-y' belongs to BZ^2.
Indeed B^(-1)=[[3,4],[-4,3]]/25, so equality of the two residues is exactly
integrality of B^(-1)(y-y'). The group Z^2/BZ^2 has order |det B|=25. This
also follows by enumerating K on the 25-by-25 residue square, since 25Z^2
is contained in BZ^2.

For each seed, the 25 table outputs have distinct K values. This is one
finite exact certificate obligation. They consequently represent all 25
cosets. Given any y, there is exactly one row (r,t) with
K(o_s(r,t))=K(y). Its unique inverse is

```text
q = B^(-1)(y-o_s(r,t)),       x = 5q+(r,t).
```

The coset test proves that q is integral. Substitution proves both inverse
identities, hence bijectivity and surjectivity on the full lattice. The
covariance in item 1 follows directly from Euclidean division.

## Unbiasedness and the error

The checker verifies, for every one of the 25 rows,

```text
sum_s o_s(r,t) = B(r,t).
```

Taking the uniform average in the defining formula proves E F_s(x)=Ax for
all q as well as every residue. Errors are unchanged by x -> x+5z.

For each row and seed, both coordinates of o_s(r,t) lie between the floor
and ceiling of the corresponding coordinate of A(r,t). The checker verifies
that condition, the first moment above, and the exact sums of squared
residual numerators. Those sums are zero at five rows and 50 at the other
twenty rows. Since the residual numerators are 5o_s-B(r,t), the expected
squared error is 50/(5*25)=2/5 at the latter rows. The largest individual
squared residual numerator is 20, giving 20/25=4/5. The checker enumerates
all 125 row/seed entries; neither conclusion comes from a sampled input.

The optimality can also be derived without those squared-error sums. For
a scalar mean mu=k+f with k an integer and 0<=f<1, any integer-valued random
variable Y with finite second moment satisfies

```text
(Y-k)(Y-k-1) >= 0,
E (Y-mu)^2 >= f(1-f)       whenever E Y=mu.
```

Expansion and E(Y-k)=f prove the inequality. Equality holds exactly when
Y is supported on {k,k+1}, apart from the integral case where it is constant.
If the second moment is infinite, the lower bound still holds. Adding the
two coordinate inequalities gives the pointwise bound for Euclidean squared
error, without any independence assumption between coordinates.

Set a=(3r-4t) mod 5 and b=(4r+3t) mod 5. Then b=3a mod 5. When a=0 both
coordinates of A(r,t) are integral. Otherwise (a,b) is one of
(1,3),(2,1),(3,4),(4,2), and

```text
[a(5-a)+b(5-b)]/25 = 10/25 = 2/5.
```

Our unbiased nearest-cell outputs attain this lower bound in both
coordinates simultaneously. Requiring each seeded map to be a bijection
therefore costs no additional mean squared error for this rotation.

## How the witness is constructed

The retained constructor is an exact integer algorithm. For one input row,
let u,v be the two coordinate floors and let a,b be their fractional
numerators modulo five. In units of 1/5 put

```text
c = min(a,b)                  if a is 1 or 4,
c = max(0,a+b-5)              otherwise.

weight(u,  v  ) = 5-a-b+c,
weight(u+1,v  ) = a-c,
weight(u,  v+1) = b-c,
weight(u+1,v+1) = c.
```

These weights are nonnegative and give total weight five and the required
two coordinate means. Group the output points by K. The constructor checks
all 25 input and 25 output degrees equal five, obtaining a five-regular
bipartite multigraph. It extracts five perfect matchings and uses their
literal output points as the five tables. Matching existence is the standard
regular bipartite graph argument: a set of input vertices has 5|S| incident
edges, whose neighbors can receive at most 5|N(S)|, so Hall's inequality
holds. The implemented bounded augmentation routine constructs each matching;
removing it leaves a regular graph of one smaller degree.

This is dependent coordinate rounding. Independent stochastic rounding has
the same scalar means and minimum error but its output coset capacities
are not all one in this quotient. The checker rejects that control. Thus
unbiased scalar rounding by itself does not certify the reversible ensemble.
The independent checker of the table only needs coset coverage, means and
nearest-cell membership; it does not trust how the weights were discovered.
No optimizer or floating-point result is a mathematical premise.

## Scope

Multiplying the input and output lattices by h>0 multiplies the squared
error bounds by h^2. This follows by conjugating each map by scalar scaling.
It does not price changes of representation or precision.

The contract is for a fresh uniform seed independent of the current input.
An adversary who selects inputs after observing the seed can obtain a bias;
no adaptive seed-reuse or inverse-unbiasedness theorem is claimed. Exact
return requires the seed or an equivalent record. No seed sampler, entropy
recovery, physical instruction table, fixed-tape routing, bounded-word
implementation or reversible workspace bill is supplied. The rational phase
is not bound to a selected supplier root or caller. Those costs and the five
selected framework assumptions remain open. This is a scoped mathematical
construction with a finite exact certificate, not a complete multiplication
theorem or a new kappa.
