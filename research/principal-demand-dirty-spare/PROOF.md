# A restored spare removes the principal-demand orbit obstruction

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract

Let R be any associative ring with identity, 1 != 0. It need not be finite,
commutative, a domain or a field. Three rows A0,A1,H and a disjoint source p
start with independent arbitrary values a0,a1,h,p in R^w, w >= 1. Every
coefficient acts by left multiplication. The required endpoint is

```text
(A0,A1,H,p) = (a0+x p, a1+y p, h, p).
```

A fixed, input-independent finite word may use only source insertions
P_i(beta): row i += beta p and row additions E_ij(c): row i += c row j,
i != j, with rows numbered 0,1,2 and H numbered 2. Every original dirt
column must return exactly. There is no clearing, observation, free basis
map, extra row, or input-dependent control. We count nonzero source
insertions. Row additions, coefficient preparation and physical use are
separate costs. The optional tariff below charges every gate in the word.

## Theorem

Put L=Rx+Ry, a left ideal. The minimum number of nonzero source insertions is

```text
0 if x=y=0;
1 if L is nonzero and principal;
2 if L is not principal.
```

The new assertion is sufficiency of principality over arbitrary rings after
adding one restored dirty spare. A one-insertion word uses at most eight
row additions, with its insertion at the spare. This bound need not be a
shortest word. Necessity and the two-insertion echo are credited to Ali
Romman #5310 and the retained ring-valued fanout lineage. Their finite-ring
sufficiency theorem does not assert this arbitrary-ring stabilization.

### Necessity

No insertion leaves the source column zero. If a word has exactly one
nonzero insertion beta at row i, let C be the invertible matrix product of
all later row additions. The final source column is

```text
lambda=(x,y,0)^T = C e_i beta.
```

Every coordinate is a left multiple of beta, so L is contained in R beta.
Applying C^-1 expresses beta as a left linear combination of x,y,0 and
gives the opposite containment. Thus L=R beta is principal. This proof
works with any finite number of restored dirty spectators, and it does
not use commutativity, finiteness, or a division operation. Invertibility
also shows that nonzero beta cannot produce zero demand.

### The eight-ADD construction

Suppose L=R beta is nonzero. Since x,y belong to R beta and beta belongs
to Rx+Ry, choose a,b,s,t in R satisfying

```text
x=a beta,       y=b beta,       beta=s x+t y.
```

These are witnesses, not free divisions. The theorem is existential when
only the ideal's principality is known. An implementation must supply the
witnesses and pay for their preparation. Define the four-ADD word R in
chronological order by

```text
E_20(s), E_21(t), E_02(-a), E_12(-b).
```

On the desired source column it performs

```text
(x,y,0) -> (x,y,sx) -> (x,y,beta)
          -> (0,y,beta) -> (0,0,beta).
```

Execute R, then P_2(beta), then the literal inverse of R:

| Step | Gate |
|---:|---|
| 1 | H += s A0 |
| 2 | H += t A1 |
| 3 | A0 -= a H |
| 4 | A1 -= b H |
| 5 | H += beta p |
| 6 | A1 += b H |
| 7 | A0 += a H |
| 8 | H -= t A1 |
| 9 | H -= s A0 |

On every original dirt column, steps 1-4 and 6-9 cancel exactly. The source
column after step 5 evolves under steps 6-9 as

```text
(0,0,beta) -> (0,b beta,beta)
            -> (a beta,b beta,beta)
            -> (a beta,b beta,beta-t b beta)
            -> (a beta,b beta,beta-t b beta-s a beta)
            = (x,y,0).
```

The additive group of a ring is commutative; no multiplicative coefficients
were commuted. In particular the order is s a and t b, not a s or b t.
This proves the endpoint for arbitrary dirt and every data width. Zero
coefficient gates may be deleted. The inverse reverses all nine gates and
negates their coefficients, and must be charged if used.

A useful stronger identity holds without any witness relation: the same
word has identity dirt block and source column

```text
(a beta, b beta, (1-s a-t b) beta)^T.
```

The verifier checks this full identity over the free associative integer
polynomial ring. It is a finite coefficient certificate, independently of
all finite-ring substitutions.

### At most two insertions

For any x,y, even without a spare, the chronological word

```text
A1 -= y A0;  A0 += p;  A1 += y A0;  A0 += (x-1) p
```

restores all dirt and produces increments (x p,y p). Delete zero calls.
If L is nonprincipal, x cannot equal 1, so both source coefficients are
nonzero. The necessity argument makes two insertions minimal. Zero demand
has the empty word. These observations complete the classification.

## Polynomial first example and complete declared gate price

For R=K[u,v] over any field K, take

```text
x=1+uv,  y=u^2,  beta=1,
a=1+uv, b=u^2, s=1-uv, t=v^2.
```

The witness identity is (1-uv)(1+uv)+v^2 u^2=1. Every coefficient of the
eight row additions is a nonzero polynomial over every field, including
characteristic two. The word therefore uses exactly eight nonzero row
additions and one nonzero source insertion, restores the arbitrary third
row, and realizes precisely the demand in Nick Petalas #5211.

That predecessor proves that the same demand with exactly two mutable
rows has no one-insertion word, using Cohn's cited classical theorem.
We use that obstruction as a cited premise and do not replay or reprove it.
The new constructive upper bound is independent of Cohn's theorem.

Let each row addition into row i cost c_i>0, independently of coefficient
and source row, and let insertion at the spare cost mu_2>0. The exact price
of the displayed polynomial word is

```text
mu_2 + 2 c_0 + 2 c_1 + 4 c_2.
```

This charges all preparation, dirty restoration and the insertion in this
abstract alphabet. At mu_0=100, mu_1=1000, mu_2=100 and c_0=c_1=c_2=1,
the displayed word costs 108. The predecessor's exact two-row tariff at
the matching two-row prices is 202. This is a comparison of two explicitly
different workspace contracts, not a new three-row optimum or a physical
cost claim. Inverse execution would cost another 108 under these stationary
prices. Coefficient preparation, storage, movement and actual native gates
are outside the declared abstract tariff and are not assigned zero cost.

## Relation to stabilized dual exchange

Nick Petalas #6280 gives a dyadic exchange for a genuine dual pair ab=1,
with three block shears and one sign SCALE. Its classical stabilized
completion mechanism is related precedent. The present word uses only
elementary row additions and requires merely (1-sa-tb) beta=0. The element
beta may be a zero divisor and sa+tb need not equal 1. Thus no dual pair or
unit beta is assumed. For example, in Z/4, beta=2, a=b=s=1, t=2 satisfies
the witness while sa+tb=3. The claim here is the exact ring-valued fanout
criterion, explicit eight-ADD word and Cohn application, not historical
priority for stabilization or elementary matrix algebra.

## Limits

The finite certificate establishes the stated polynomial identity. The
all-ring classification rests on the written algebraic proof. No shortest
ADD count, all-positive-price three-row tariff, native coefficient
implementation, physical spare lifetime, precision/tape cost, recursive
supplier admission, new kappa, or complete multiplication theorem follows.
All five selected framework assumptions remain. Independent human and
formal proof-kernel review are unclaimed.
