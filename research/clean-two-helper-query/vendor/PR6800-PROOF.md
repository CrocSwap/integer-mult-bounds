# Restored dirty helpers do not increase square-zero query capacity

This contribution was produced by Nick Petalas. Apache-2.0.

## 1. Statement and credited premise

Let K be any field of characteristic two and let
R = K[Q]/(Q^2-1). The symbol Q is a formal central involution.
Fix n>0 target coordinates, h>=0 arbitrary dirty helper coordinates,
k>=3 available paid calls, and a nonnegative integer rank cap r.
Free gates are arbitrary constant matrices in GL_(n+h)(K).
A paid gate is I+Q N, where N is constant, N^2=0, and rank(N)<=r.
The complete required endpoint on every input is

```text
diag(Q I_n, I_h).
```

Thus every original helper value must return unchanged, without a promise
on its value or correlations with the target inputs.
Put m_k=2 floor((k-1)/2). The endpoint is possible with at most k calls iff

```text
n is even and n + ceil(n/m_k) <= k r.
```

Whenever feasible, its least total paid rank with at most k calls is
n+ceil(n/m_k).
Neither statement depends on h. Zero-rank calls may pad a shorter word.

The new part is necessity for arbitrary h. Josie Elliston's
[PR #6138](https://github.com/CrocSwap/integer-mult-bounds/pull/6138),
`research/four-block-query-capacity-audit/README.md`, finding 5, supplies
the workspace-free attaining construction. We use that theorem as a cited
premise and extend its words by the identity on h helpers. We do not replay
its computations or claim its construction. Its four-call theorem credits
Nick Petalas #6122, its simplex credits Cinna Davis, its Gram framework
credits Ali Romman #5617, and its source question credits Matarener #6114.

## 2. Normalize to a projection, keeping every helper

Set epsilon=Q+1, so epsilon^2=0 and R=K[epsilon]/(epsilon^2).
For square-zero N,

```text
I+Q N = (I+N)(I+epsilon N).
```

Move the constant factors and free gates to one side, conjugating the N's
by constant invertible matrices. Rank and square-zero are preserved.
The constant part of the required endpoint is I, so the complete endpoint
is equivalent to

```text
sum_(i=1)^k R_i = P,
R_i^2=0,
P=diag(I_n,0_h).
```

All products involving two epsilon terms vanish. Conversely, such a sum
implements I+epsilon P by preceding each paid I+Q R_i with the free I+R_i.
This equivalence keeps the whole arbitrary-input matrix, including both
off-diagonal helper blocks. It does not discard helper information.

Let r_i=rank(R_i) and S=sum r_i. Since a square-zero matrix has trace zero,
trace(P)=n times 1_K=0, so n must be even.

## 3. The projection Gram complement

Factor R_i=U_i V_i with U_i injective and V_i surjective through K^(r_i).
Then V_i U_i=0, since U_i(V_i U_i)V_i=R_i^2=0.
Concatenate the U_i horizontally into U and the V_i vertically into V.
Thus UV=P. Let

```text
X=VU on K^S,       Y=I_S+X,       d=S-n.
```

The call-diagonal blocks of X vanish, so Y_ii=I_(r_i).
Although P is a projection, X need not be one. Instead,

```text
X^3=V P^2 U=V P U=X^2,
Y^3=Y.
```

The fixed space of X has dimension n. Indeed, U and V restrict to inverse
maps between ker(I_S+X) and im(P). For Xv=v, P(Uv)=Uv and VUv=v.
For Pw=w, XVw=Vw and UVw=w. Therefore rank(Y)=S-n=d.

Take a full-rank factorization Y=A B through K^d. Since Y^3=Y,
injectivity of A and surjectivity of B give

```text
C=BA,             C^2=I_d.
```

In particular C is invertible. Partition A into call row blocks A_i
and B into matching column blocks B_i. The call-diagonal equations give

```text
A_i B_i=I_(r_i),
E_i=B_i A_i,      E_i^2=E_i,      rank(E_i)=r_i,
sum E_i=C.
```

Consequently r_i<=d. When h=0, the old argument can take C=I_d.
With dirty helpers, C can be a nonidentity involution I_d+Z with Z^2=0.
Invertibility, rather than identity, is the property needed below.

## 4. The rank bound for every call count

If k is odd, sum r_i<=k d immediately gives

```text
(k-1) S >= k n,
S >= n + ceil(n/(k-1)).
```

If k is even, characteristic two gives sum(I_d+E_i)=C.
Each I_d+E_i has rank d-r_i, while C has rank d. Rank subadditivity yields

```text
d <= sum(d-r_i) = k d-S,
(k-2) S >= (k-1) n,
S >= n + ceil(n/(k-2)).
```

Together these say S>=n+ceil(n/m_k). Since S<=k r, the stated uniform-cap
condition is necessary. The credited workspace-free construction proves
sufficiency and equality for total rank. This finishes the scoped theorem.

For example, four rank-two paid calls cannot twist six independent
coordinates even when any number of arbitrary dirty helpers may be mixed
into every call and must eventually return unchanged. The new conclusion
is the independence from the helper count, not the predecessor's
workspace-free numerical bound.

## 5. A genuine nilpotent defect and the clean-helper boundary

Write binary matrices as integer-coded rows, with the least significant
bit the first column. The four three-by-three matrices

```text
(0,6,6), (6,6,6), (0,5,0), (7,7,0)
```

are square-zero rank-one matrices with sum diag(1,1,0). Their stacked
X=VU is not idempotent, and the complement factor has C!=I but C^2=I.
The verifier reconstructs these facts without treating the coded rows as
a receipt. Thus replacing the predecessor's identity by a projection
requires the new argument in section 3.

Initialized clean helpers have a different contract. The two-by-two terms

```text
(2,0), (0,1), (3,3)
```

sum to I_2 and yield endpoint Q I_2. On (x,0) this twists one target and
returns the zero helper, despite n=1 being odd. On (x,y) it also twists y.
It therefore fails dirty restoration. The theorem does not cover a
zero-initialized helper promise, discarded outputs, nonlinear controls,
Q-dependent free gates, non-square-zero paid gates or approximate equality.

This is an abstract query-capacity obstruction. Native implementation,
physical basis-change costs, independent stage multipliers, storage,
precision, a complete supplier invoice and the five selected framework
assumptions remain outside the claim. No new kappa or complete
multiplication theorem follows. The all-field proof is written mathematics;
finite binary checks do not provide formal proof-kernel acceptance.
