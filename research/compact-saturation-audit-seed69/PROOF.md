# Saturated digits: exact agreement and the maximal invariant guard

This is a scoped mathematical audit of Douglas Colkitt's unchanged
earlier-source compact-control word. It extends Hanson Sun / bbMisk's PR1219
nonsaturated-digit criterion. The retained construction and PR1219's guard
are correct. No new supplier, runtime bound or kappa is asserted.

## 1. Domain and the complete map

Let n,G,K,rho be integers with n>=1, G>=1, K>=G+1 and 0<=rho<K.
Put B=2^G, A=2^(K-1), R=2A.
After removing the unchanged low rho target bits, the target modulus is
Y=2^((n+1)K-rho)>=2R^n. All unprocessed upper target bits remain in this
modulus. The temporary modulus is B^n. All fields range over their complete
dirty domains. The n source bits z_i are arbitrary and unchanged.

Write the processed target digits as v_i=2g_i+a_i, with 0<=g_i<A and
a_i in {0,1}; write the temporary digits as 0<=t_i<B. Saturation t_i=B-1
is allowed. Define

```
pack(y) = sum_i bit_(iK)(y) B^i
mask(z) = sum_i z_i R^i
T(y,t)  = (y XOR mask(z), t).
```

The retained four rotations, with their four physical swaps, induce P:

```
y1 = y + 2 sum_i z_i t_i R^i                 (mod Y)
t1 = t + pack(y1)                           (mod B^n)
y2 = y1 + sum_i z_i (1-2 digit_i(t1)) R^i   (mod Y)
t2 = t1 - pack(y2 XOR mask(z))              (mod B^n).
```

Each swap sandwich restores the arbitrary back field; each modular update
has an offset independent of its target. Thus P is a permutation on the
complete rectangle, including exceptional addresses. Source and spectator
bits are preserved. The highest selected XOR is a separate retained step.

## 2. Exact agreement, including saturation

Compute the compact carries from the ORIGINAL target parities:

```
d_0 = 0
d_(i+1) = floor((t_i + a_i + d_i)/B).
```

Each d_i is zero or one. Then P(y,t)=T(y,t) **if and only if** both hold:

1. `g_i + z_i t_i < A` for every i<n-1;
2. `d_i=d_(i+1)=0` at every digit with z_i=1.

There is no restriction on the first target rotation's final outgoing carry,
nor on a final compact carry produced at a source-zero digit.

For necessity, let c_i be the carries of the first target rotation:

```
c_0=0,
c_(i+1)=floor((v_i+2 z_i t_i+c_i)/R).
```

Since B<=A and t_i<=B-1, induction gives c_i in {0,1}. The parity read by
the compact load is a'_i=(a_i+c_i) mod 2. If the target is correct, the final
unload is pack(y). Full temporary restoration therefore requires
`pack(y1)-pack(y)=0 mod B^n`. Both packed values lie in [0,B^n), so they are
equal as integers. Uniqueness of radix-B digits forces a'_i=a_i, hence
c_i=0 for every i<n. Induction through the target carry recurrence makes
this exactly condition 1; c_n is irrelevant.

Assuming condition 1, pack(y1)=pack(y). The loaded digits are

```
u_i = t_i+a_i+d_i-B d_(i+1).
```

Subtracting the intended target change gives

```
y2 - (y XOR mask(z)) = 2 sum_i z_i (B d_(i+1)-d_i) R^i (mod Y).   (1)
```

This identity also holds when the compact addition overflows its final
digit. The coefficients in (1), before the factor two, have magnitude at
most B. A largest nonzero term dominates every smaller term because
`B sum_(i<j) R^i < R^j`, using B<R-1. The whole sum has absolute value
less than `2B(R^n-1)/(R-1) < 2R^n <= Y`, so modular wraparound cannot
turn a nonzero sum into zero. Thus target correctness is equivalent to
`z_i(B d_(i+1)-d_i)=0` for every i. As B>=2, this is exactly condition 2.
With the target correct, the compact load and unload cancel. This proves
both directions of the complete-map criterion, not just target agreement.

## 3. Agreement alone is not an invariant repair guard

Let E={s:P(s)=T(s)}. The ideal map T is an involution. The unique largest
T-invariant subset of E is

```
H = E intersect T(E).                                      (2)
```

Indeed T(H)=H, and every T-invariant subset of E lies in this intersection.
This maximality is for this fixed P, T, complete rectangle and invariant
guard requirement. It is not a lower bound on every possible repair method.

There is a one-pass carry description of H. Keep condition 1 and require,
at every active source digit z_i=1,

```
d_i=0 and t_i<=B-2.                                        (3)
```

To prove necessity, agreement at both s and T(s) forces zero incoming and
outgoing compact carry at each active digit in both computations. Its
target bit takes both values, so t_i+1<B. To prove sufficiency, compare the
compact carry recurrences before and after T. At a source-zero digit the
parities are identical. At an active digit, (3) makes the incoming and
outgoing carries zero for either parity. Induction proves identical carry
states in both passes. Condition 1 is invariant because T preserves g,t,z.
Thus both addresses satisfy Section 2, proving (2)-(3).

PR1219's H0 prohibits every saturated temporary digit and retains condition
1. It has d_i=0 everywhere, so H0 is contained in H. The inclusion is strict:
for n=2,K=3,G=2,rho=2, the quotient state (y,t,z)=(0,3,2) is in H and P
maps it to (8,3). Its first temporary digit is saturated but inactive; the
load produces no carry into the active second digit. Changing y to 1
produces that carry, and P gives (121,3), instead of the intended (9,3).
Checking only whether active digits themselves are nonsaturated is unsound.

For the simpler n=1,K=3,G=2,rho=2 witness, with t=3,z=1, P sends y=0 to 1
correctly, then sends 1 to 8 instead of 0. Both temporaries are restored.
The output address (8,3,1) is itself in E, so using E at current addresses
would skip the required correction for the second call. PR1108 already
establishes the related one-digit cancellation obstruction; here it is a
control for the multi-digit invariant-set distinction.

Because P=T on H and T(H)=H, P(H)=H. Since P is a permutation, it also
preserves the complement. The retained current-address correction T P^-1
on that complement is therefore valid. This package checks every sorted
repair key and unique payload, not merely hole counts.

## 4. Exact all-n densities

Each processed digit has 4AB equiprobable choices (g,a,t,z). Use row vectors
indexed by incoming d=0,1, with columns indexed by outgoing d=0,1.
For interior digits i<n-1, define

```
M_E = [[2A(2B-1)-(B-1)^2,           A],
       [A(2B-3),                  3A]]

M_H = [[A(4B-3)-(B-1)(B-2),        A],
       [A(2B-3),                  3A]].
```

For the final digit, let N_E and N_H be these same matrices with the
subtracted polynomial in entry (0,0) removed. Then

```
Pr(E) = (1,0) M_E^(n-1) N_E (1,1)^T / (4AB)^n
Pr(H) = (1,0) M_H^(n-1) N_H (1,1)^T / (4AB)^n.              (4)
```

At a source-zero digit, the counts of (t,a) transitions are
`[[2B-1,1],[2B-3,3]]`; every g is allowed. Source-one digits are allowed
only in transition 0->0. For E, sum `(A-t)` twice for t<=B-2 and once for
t=B-1 (only a=0). This gives `(2B-1)A-(B-1)^2`. For H, both parities are
allowed for t<=B-2 only, giving `2A(B-1)-(B-1)(B-2)`. Add the source-zero
contribution to obtain the displayed matrices. At the last digit there is
no target carry guard, so replace each A-t by A. Final compact overflow is
summed over both columns, as required. Unused source, low target, upper
target and back-field choices cancel between numerator and denominator.

For n=1, (4) reduces to Pr(E)=1-1/(4B), Pr(H)=1-1/(2B), consistent with
the predecessor's one-digit law. For n=2,K=6,G=2, for every allowed rho:

| Set | Exact complete-rectangle fraction |
|---|---:|
| Original retained guard | 9/64 |
| PR1219 nonsaturated H0 | 567/1024 |
| Maximal invariant H | 1499/2048 |
| Complete-map agreement E (not invariant) | 6841/8192 |

The replay independently enumerates every transition for twelve (K,G) pairs,
and complete address permutations in six domains. Those finite tests support
the written all-n proof; they do not constitute a formal proof of it.

## 5. Cost, inherited assumptions and limits

The new predicate uses at most n<=L digit comparisons and carry updates on
O(L)-bit integers, which fit the retained O(L^3) per-record descriptor
allowance. No field is initialized for free. The raw word still
has all four swaps and four controlled rotations, including both source
reads and both temporary updates. Highest-selected-bit completion remains
O(V). For M records, payload width P, address width L and V=MP, retain

```
O(V + M L^3 + delta M L (P+L)),    delta = 1-Pr(H).
```

This includes predicate scans, extraction, inverse-address and destination
key work, sorting complete records and keys, reinsertion, rewinds and cleanup.
Because H contains H0, its exceptional fraction is no larger than PR1219's.
The source's assumptions G=4 ceil(log2 p)+6, n+1<=p, K/log p tending to
infinity, L=O(p), and superpolynomial payload therefore retain their O(V)
repair conclusion and existing `O(V*((f log p)^tau+1))` earlier-source cost.
This is a guard-envelope improvement, not a measured speedup. No recursive
profile or binding supplier changes, and no larger kappa follows.

The argument assumes the retained complete independent fields and legal
controlled-rotation/repair interfaces. Later-source composition, physical
tape realization, recursive reservations/hosting, precision and analytic
transfer are not reverified. The predicate is not installed in production.
Apache-2.0; substantial OpenAI Codex assistance; no proof-assistant or
independent human review is claimed.
