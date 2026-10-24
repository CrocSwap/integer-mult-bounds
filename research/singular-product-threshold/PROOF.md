# Singular rank-one product threshold

Let K be a field and R=K^k for a positive finite k. Scalars embed diagonally
in R. Use two roles. Paid factors are I+u y^T, where u belongs to R^2 and y
belongs to K^2. Common GL_2(K) maps are free anywhere. A target is an ordered
tuple M=(M_1,...,M_k) of 2-by-2 matrices over K. All M_i in the main theorem
have rank exactly one. Cost means the least number of paid factors.

## Cited criterion and the changed target contract

Nick Petalas's #4276, Theorem B, states that cost(M)<=2 exactly when common
G,H in GL_2(K) make N=GMH satisfy N12 in the right ideal N11 R. This criterion
allows singular targets. We cite it as a predecessor theorem, rather than
claiming or auditing it. Free maps can be collected at one endpoint by
#4243's normal form, following Wentao Li's #4099/#2513 alphabet.

For R=K^k, right-ideal membership is componentwise. Write t for the first
column of H and phi for the first row of G. The other column of H completes
t to a basis. In component i the ideal condition is equivalent to

```text
phi M_i t != 0, or phi M_i = 0.
```

Indeed a nonzero pivot generates the entire field. A zero pivot requires
the other entry of the row to be zero, which means the entire row is zero.
Conversely every nonzero t and phi extend to suitable H and G. Thus the
displayed condition must hold for every i with the SAME t and phi.

ToikY's #4334 studies invertible components, for which a zero row is
impossible, and proves the sharp threshold q+1. The present theorem changes
every component to a nonzero rank-one matrix. The zero-row alternative is
essential, so applying the invertible common-unit-pivot test would be wrong.
Nick Petalas's #4601 leaves singular local-product targets open.

## Theorem 1: exact kernel/image criterion

For each line T in K^2, let S_T be the span of the image lines im(M_i) for
those i with ker(M_i)=T. The span of an empty collection is zero. Then

```text
cost(M)<=2  iff  some T has dim(S_T)<=1.
```

Proof. Fix a nonzero t spanning T. If t is not in ker(M_i), then M_i t is a
nonzero vector spanning im(M_i). Every phi either evaluates nontrivially on
this vector or kills the entire image. Both satisfy the cited criterion.
If ker(M_i)=T, then M_i t=0. The criterion requires phi to kill im(M_i).
Therefore a common nonzero phi exists exactly when it kills S_T, which is
equivalent to dim(S_T)<=1 in a two-dimensional space. Taking all T proves
both directions.

## Lemma 2: three factors suffice

In fact every target in M_2(K^k), without any rank assumption, has cost at
most three. It is enough to factor each component with the common ordered
right vectors e1,e2,e1. Left-vector entries can vary by component, so the
following per-component choices assemble into three paid R-valued factors.

For M_i=[[a,b],[c,d]] with b=0 use

```text
[[a,0],[c,1]] [[1,0],[0,d]] I = M_i.
```

For b!=0 put l=(d-1)/b, f=c-l*a, and e=a-b*f. Then use

```text
F1=[[1,0],[l,1]], F2=[[1,b],[0,1]], F3=[[e,0],[f,1]].
F1 F2 F3 = [[e+b*f,b],[l*(e+b*f)+f,l*b+1]] = M_i.
```

Every displayed factor is I+u e_j^T for its stated right vector. The
identity may use e1 and a zero left vector. These are algebraic product
orders, so column-vector execution applies F3 first. No free endpoint is
needed. The construction extends the invertible-only upper-word scope in
#4334 to this pure-field product domain. It does not apply to general local
algebras, where a nonzero b may fail to be invertible.

## Theorem 3: sharp finite-field threshold

Let K=F_q. Among tuples with all component matrices nonzero and rank one,

```text
k < 2(q+1): every target has cost <=2;
k >= 2(q+1): some target has exact cost 3;
every target has cost <=3.
```

Proof. There are q+1 possible kernel lines. If cost(M)>2, Theorem 1 says
that every S_T has dimension two. Each such span needs at least two
component matrices with kernel T and distinct image lines. A component has
only one kernel, so k>=2(q+1).

For sharpness, for each T choose a nonzero row r_T with kernel T. Include
both e1*r_T and e2*r_T as component matrices. They have rank one, share
kernel T and have different image lines. Now every S_T=K^2. Theorem 1
excludes two factors, while Lemma 2 gives three. For larger k repeat any
component. Repetition preserves the obstruction and the three-factor word.
This proves all assertions.

Over an infinite K, a finite tuple omits some possible kernel line T.
Then S_T=0, and every such rank-one tuple costs at most two. This is a
direct case of Theorem 1, not a finite-field enumeration claim.

## Binary finite certificate

Over F2 there are nine nonzero rank-one matrices. Literal zero-, one- and
two-factor images are enumerated with all common free endpoints and all
right-vector lines. Allowing arbitrary left vectors includes singular paid
factors. Projective representatives suffice because a nonzero rescaling of
y can be absorbed in u. A free map anywhere can be collected at the right
endpoint by the cited normal form.

For fixed common right-vector lines and endpoint, every component may
choose its left vectors independently. Thus a tuple belongs to this chart
exactly when every component belongs to its local image. Membership depends
only on its support among the nine matrices. Comparing all 2^9 support
sets with Theorem 1 is an exhaustive comparison for tuples of ANY length
over this binary rank-one alphabet, without enumerating infinitely many
tuples. There are 64 support sets outside the two-factor image, with minimum
size six. A finite recurrence enumerates ordered-tuple multiplicities,
starting with the empty support and adding one of nine entries at each
step. It covers every tuple through length six exactly once.

At length six the resulting exact cost histogram is

```text
cost 0: 0; cost 1: 567; cost 2: 511434; cost 3: 19440.
total: 531441 = 9^6.
```

The 19,440 count also follows from the threshold criterion. Assign the six
ordered positions in pairs to the three kernel lines, in 6!/(2!)^3=90 ways.
For each kernel the ordered pair has 3*2=6 different image-line choices,
and over F2 each kernel/image pair specifies one matrix. Thus the count is
90*6^3=19440. The verifier checks the literal chart census independently of
this arithmetic count.

## Scope and credit

The quantified result is a scoped algebraic proof, with a separate finite
certificate over the stated binary domain and finite word checks over five
fields. It is not a complete multiplication theorem. Native preparation,
access, routing, restoration, precision, stock and complete supplier costs
are unknown. Local radical lifts, matrix-algebra blocks, mixed-rank lower
thresholds and more than two roles are outside scope. No supplier admission
or new kappa is claimed. Independent human and formal proof-kernel review
are unclaimed.

This package was produced by Nick Petalas. The exact low-factor criterion
and common-free normal form are credited above to Nick Petalas, the
invertible-product predecessor and open gap to ToikY, and the alphabet and
column bound to Wentao Li following #2513. Projective-line counting and
elementary matrix multiplication are classical. Apache-2.0.
