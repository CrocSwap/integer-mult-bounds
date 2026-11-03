# The profile (0,1,3,3,m) is impossible when m is a power of two

Proof by Nick Petalas. Apache-2.0.

## Model

The model, target and notation are those of apoursh's PR6089
(`research/bit-positive-frame-use`, pinned in [SOURCES.json](SOURCES.json)). It
keeps Cinna Davis's PR2085/2112 endpoint. Here $A,B,P,Q$ are the four old 2×2
addresses, with $A+B=P+Q=I_2$. The added frame is $R=F/m$ for an old address $F$
and an integer $m\ge1$. Calls are $D_N(F)=I_w+([F]-1)N$ over the formal group
algebra $\mathbb F_2[\Lambda]$ with $N^2=N$ and $\operatorname{rank}N=1$. Free
$\operatorname{GL}_w(\mathbb F_2)$ mixing is allowed, the $w-4\ge0$ extra roles
are dirty workspace restored exactly, and the target is

$$T_w=\operatorname{diag}([A+P],[A+Q],[B+P],[B+Q],1,\ldots,1).$$

PR6089 proves that every exact word using $R$ has one of the multiplicity profiles
$(1,2,2,2,m)$, $(0,2,2,2,2m)$ or $(0,1,3,3,m)$, in order $(F,F^\perp,G,H,R)$. It
constructs the first two and excludes the third for $m=1$. PR6089 Section 3 gives
exact symmetries that reduce every $F$ to $F=A$. Under that reduction the third
profile is: no $A$ call, one $B$ call, three $P$ calls, three $Q$ calls and $m$
calls labelled $R=A/m$.

## Theorem

**If $m=2^k$ for an integer $k\ge0$, no exact word in this model has the profile
$(0,1,3,3,m)$, at any finite width $w\ge4$.**

The case $k=0$ is PR6089's $m=1$ exclusion; the argument below also covers it.
For $F\ne A$ the statement follows by PR6089's symmetries, which preserve counts.

## Proof

**Normal form.** As in PR6089 Section 1, conjugate every free binary matrix through
the later paid factors. A conjugated rank-one idempotent is still one, with the same
label. The word becomes a product of paid factors followed by one free matrix $G$.
Applying the augmentation $[F]\mapsto1$ turns every paid factor and the target into
the identity, so $G=I_w$. Thus

$$\prod_{i=1}^{L}D_{N_i}(F_i)=T_w$$

exactly, in word order, where the $N_i$ are rank-one idempotents in
$M_w(\mathbb F_2)$. Write $E_1,\ldots,E_m$ for the projectors of the $R$ calls in
word order, $N_B$ for the $B$ call, and $N_{Q,1},N_{Q,2},N_{Q,3}$ for the $Q$ calls.
Let $D_w=\operatorname{diag}(1,1,1,1,0,\ldots,0)$.

**The lattice.** $\Lambda=\mathbb ZR+\mathbb ZB+\mathbb ZP$ is free on $R,B,P$,
because $A=mR$ and $A,B,P$ are linearly independent. In this basis

$$A=mR,\qquad Q=A+B-P=mR+B-P.$$

Any additive map $\psi:\Lambda\to\mathbb Z$ therefore defines a ring homomorphism
$\mathbb F_2[\Lambda]\to\mathbb F_2[s]/(s^K)$, $[\lambda]\mapsto(1+s)^{\psi(\lambda)}$,
since $1+s$ is a unit. Applied entrywise, it sends $D_N(F)$ to
$I+((1+s)^{\psi(F)}-1)N$.

**Step 1: the $R$ character at order $m$.** Take $\psi_R(R)=1$ and
$\psi_R(B)=\psi_R(P)=0$, so $\psi_R(A)=\psi_R(Q)=m$, and truncate at $K=m+1$. Because
$m=2^k$, over $\mathbb F_2$

$$(1+s)^m=1+s^m,\qquad (1+s)^{2m}=1+s^{2m}\equiv1\pmod{s^{m+1}}.$$

The $B$ and $P$ calls map to $I$. An $R$ call maps to $I+sE_i$, and a $Q$ call maps
to $I+s^mN_{Q,j}$. Expand the product over subsets of calls. The $s^m$ coefficient
gets one term from each subset of total order $m$. These are the subset of all $m$
$R$ calls, contributing $E_1E_2\cdots E_m$ in word order, and each single $Q$ call.
Any subset containing a $Q$ call and another call has order at least $m+1$. The
target exponents have $\psi_R$ values $m,2m,0,m$ on the active roles and $0$ on the
workspace, so the image of $T_w$ is $I+s^m\operatorname{diag}(1,0,0,1,0,\ldots,0)$
modulo $s^{m+1}$. Comparing $s^m$ coefficients:

$$E_1E_2\cdots E_m+\sum_jN_{Q,j}=\operatorname{diag}(1,0,0,1,0,\ldots,0).\tag{1}$$

**Step 2: the $B$ character at first order.** Take $\chi_B(B)=1$ and
$\chi_B(R)=\chi_B(P)=0$, so $\chi_B(Q)=1$ and $\chi_B(A)=0$, and truncate at $K=2$.
Only the $B$ and $Q$ calls are nontrivial, each mapping to $I+sN$. The target values
are $0,1,1,2$, and $(1+s)^2\equiv1\pmod{s^2}$. Hence

$$N_B+\sum_jN_{Q,j}=\operatorname{diag}(0,1,1,0,0,\ldots,0).\tag{2}$$

This is the first-order character equation used in PR6089 Section 4.

**Step 3: rank.** Adding (1) and (2) gives

$$N_B+E_1E_2\cdots E_m=D_w.$$

The left side is a sum of a rank-one matrix and a product of rank-one matrices, so
its rank is at most $2$. The right side has rank $4$. This is a contradiction. ∎

## Why the argument stops at powers of two

For $m=2^k o$ with $o\ge3$ odd, the same two steps give

$$N_B=D_w+e_{2^k}(E_1,\ldots,E_m),$$

where $e_j$ is the sum of the ordered products of $j$ distinct $R$ projectors, taken
in word order. Lower orders also force $e_j(E)=0$ for $1\le j<2^k$. Once $o\ge3$,
$e_{2^k}(E)$ is no longer a single product and its rank can exceed $2$, so the rank step no longer closes.
For example, when $m=3$ the condition reads $E_1+E_2+E_3+N_B=D_w$, which the four
coordinate projectors satisfy. Neither realizability nor impossibility is proved for
such $m$.

## Scope

This is a scoped written proof in PR6089's formal model. It is not a native
supplier, a κ change or a multiplication theorem. It does not alter PR6089's sharp
minimum $m+7$ or its length spectrum $\{m+7,2m+6\}$. It sharpens the count-profile
classification. For $m$ a power of two, the attained profiles are exactly the two
subdivision profiles. Clean ancillas, discarded roles, address-dependent free
mixing, signed or multiple added frames, and changed endpoints are outside scope,
as in PR6089.
