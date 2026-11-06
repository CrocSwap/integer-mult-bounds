# The exact six-orbit chain relaxation

## 1. Finite matrices and cited interpretation

Let V have basis e_x for x in F_2^4. Write X_w e_x=e_(x+w) and
C_w=((1+i)I+(1-i)X_w)/2. There are 35 two-dimensional linear subspaces, or
planes, of F_2^4. For each D choose its lexicographically first triple T_D
of distinct points with difference plane D. Define

```text
v_D = sum_(z in F_2^4) X_z e_(T_D[0]) wedge X_z e_(T_D[1]) wedge X_z e_(T_D[2]).
```

These vectors have disjoint supports and coefficient one at their reference
triples. Let M_w be the matrix of the exterior action of 2C_w on their span,
read by reference coefficients, and set K=M_1 M_2 M_4 M_8. The integer scaling
does not affect rank. `model.py` expands the eight wedge choices and sixteen
translations using Gaussian integers. Its matrix entries are real.

Sussman's PR #6706 supplies the width-three necessary-condition interpretation.
The other shift-character blocks have the same rectangular ranks after its
cited scalar and diagonal changes of basis. Free steps without address maps
preserve plane blocks. Bit permutations act on these blocks by permuting
planes. The finite calculation takes these premises as given. It does not
audit the representation or turn a passing condition into a construction.

## 2. The six blocks

Order planes lexicographically by their sorted elements. Order their S_4 orbits
by smallest plane index. The orbit sizes are 6,12,4,4,3,6. Their nonzero-vector
weight multisets are respectively

```text
(1,1,2), (1,2,3), (1,3,4), (2,2,2), (2,2,4), (2,3,3).
```

Every invariant union of plane blocks is a union of these orbits. Encode a
union by its six-bit mask. For masks b subset a define

```text
c(a,b) = rank M_1[planes(b), planes(a)^c]
d(a,b) = rank K[planes(b), planes(a)^c].
```

Ranks are over Q, equivalently C for these integer matrices. A bit permutation
conjugates any single-bit direction to 1 and preserves each orbit union, so
all single-bit directions have the same cut ranks. It preserves the target
because it permutes its four commuting factors. There are 3^6=729 nested mask
pairs. The certificate lists every rank.

## 3. Complete optimization

For s calls and U_s subset ... subset U_0, the six-piece inequality is

```text
sum_(t=1..s) c(U_(t-1),U_t) >= W d(U_0,U_s).
```

Fix a starting mask a. Put F_0(a,a)=0 and F_0(a,b)=infinity otherwise. Then

```text
F_(t+1)(a,b) = min_(b subset v subset a) [F_t(a,v)+c(v,b)].
```

Induction proves this is exactly the minimum over all length-t shrinking
chains from a to b. The preceding mask of the last step is one of these v,
and every listed v supplies a legal last step. Zero-demand pairs impose no
restriction because all costs are nonnegative. Therefore every inequality
passes exactly when

```text
W <= R_s = min_(b subset a, d(a,b)>0) F_s(a,b)/d(a,b).
```

## 4. Certificate and consequence

The regenerated table gives R_5=19/10, R_6=23/10 and R_7=27/10.
For s=6 or 7 an attaining chain has U_0=44 and U_t=36 for every t>=1.
Here d(44,36)=10, c(44,36)=3 and c(36,36)=4. Its ratios are respectively
(3+5*4)/10 and (3+6*4)/10. The dynamic program certifies every other chain's
ratio is at least this value.

An enumeration with different coverage logic checks the minimum without
using dynamic-program entries. Each orbit bit chooses its first absent
boundary, or remains present throughout. Including absence at U_0 gives
s+2 choices per bit, in bijection with all shrinking chains. The loops cover
8^6=262,144 six-call chains and 9^6=531,441 seven-call chains. Respectively
64,430 and 108,338 have positive demand. Their exact minima agree with R_s.
These are all chains, not all physical programs.

Since 2<23/10 and 2<27/10, both schedules pass every stated inequality for
W=2. Five calls fail for W=2, and seven fail for W=3. In particular this
six-piece rank-chain search cannot settle the two-array seven-call problem
by rejecting every schedule.

## 5. Limits

The result concerns these necessary inequalities on unions of six plane orbits.
It asserts no schedule realization, optimality against other invariants, or
limitation of every network cut. Additional information constraints can reject
the schedules. Native operations, precision, dirty restoration, stock, complete
supplier costs and outer use remain open. No new kappa follows.
