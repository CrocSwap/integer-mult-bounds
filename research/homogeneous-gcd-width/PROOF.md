# Exact cancellation in a homogeneous chronological compiler

This scoped written proof was produced by Nick Petalas. It specializes
codyw912's PR4638 arbitrary-height forest and Mihir Srivastava's PR4507
chronological batching policy. Their validity and native contracts are cited
premises. No predecessor result is re-audited here.

## Hypotheses

Fix integers m>=2 and W,P>=1. A raw unit has W distinguishable productive
positions, all of rank m, and P distinguishable chronological paid positions,
all of rank 1. Use precisely the arbitrary-height forest in PR4638. At
ambient integer rank n>=m its cutoff is C=floor(n/m), and its height G(n)
is any specified nonnegative finite integer. Different ranks may have
different heights. Set B_j=1 for 0<=j<m.

The W targets are separate arbitrary inputs. No productive role is silently
identified with another. Separate paid paths and positions retain separate
chronological cuts. The interpretation as a physical supplier requires the
predecessor's native, whole-job, ownership and closure hypotheses. This proof
does not construct a native unit with this symbolic inventory.

For every n>=m define

```text
H(n) = floor(log_m n),
k(n) = min(G(n)+1,H(n)),
d(n) = G(n)+1-k(n),
s(n) = m^k(n),
S(n) = P^d(n) W^k(n).
```

All logarithms here define integer floors by power comparison. Since
floor(log_m floor(n/m))=H(n)-1, the first present depth of the forest is
d(n). In particular 1<=k(n)<=H(n), m<=s(n)<=n, and n-s(n)<n.

## Lemma 1. The complete source and cut lists

At depth d a class is indexed by a distinguishable paid path of length d.
There are P^d such classes. A unit is indexed by an ordered target word of
length G-d. All these words have column m^(G-d), independently of their
letters. Consequently either the entire class is present or it is empty.
It is present exactly when m^(G-d)<=C, which is equivalent to d>=d(n).

For a nonleaf present parent, its W^(G-d) paid outputs at one position
match the child's target demands bijectively. Split a parent word into its
first letter and remaining word. Both have the same column/rank contract,
and the child is present whenever its parent is. Thus no present class has
an unmatched nonleaf exit. This is matching within one actual paid cut,
with no pooling between paths or positions.

If d(n)=0, the root demands W^(G+1) source jobs of rank m^(G+1).
If d(n)>0, the classes through depth d(n)-1 are empty. At the first present
depth d(n), each of the P^d(n) classes demands W^(G-d(n)+1) fresh source
jobs, all of rank m^(G-d(n)+1). No later class needs a fresh source because
its present parent supplies it. These two cases give the same source list

```text
one rank s(n), with total multiplicity S(n).
```

Every depth-G class contains the single empty target word. Each of its P
paid positions therefore exits with one rank-one job. The complete exit
list has P^(G+1) separate cuts, each (rank 1, multiplicity 1). Its length
is an algebraic count; a general-height forest is not emitted by this proof.
There are no boundary exits. This also proves nonemptiness, including when
the root class is empty.

As a consistency identity, its unit-column mass V is

```text
V = sum_(d=d(n)..G) P^d (Wm)^(G-d),
S(n) s(n) - P^(G+1) = (Wm-P) V.
```

This is a telescoping finite geometric sum, valid also at Wm=P. No positive
surplus or favorable moment is assumed merely to count the forest.

## Theorem 2. Exact least-LCM width at every height

The source complement is one upfront batch
(n-s(n),S(n)). All the separate exits use B_1=1 and impose no replication
constraint. Applying the cited local batching lemma gives

```text
a_n = B_(n-s(n)) / gcd(B_(n-s(n)),S(n)),
B_n = S(n) a_n = lcm(S(n),B_(n-s(n))).                 (1)
```

This is the recursively least library under that fixed common-replication
policy. Local minimality is inherited from PR4507; no optimality over other
policies or physical programs is claimed.

Starting at n_0=n, set n_(i+1)=n_i-s(n_i) until n_t<m. Each step decreases
the rank by at least m, so t<=floor(n/m). Repeated application of (1) gives
the exact closed expression

```text
B_n = lcm_(0<=i<t) [P^d(n_i) W^k(n_i)].              (2)
```

The empty LCM is 1. This expression retains the actual gcd cancellations;
replacing the LCM by multiplication or by numerical maximum is invalid.

## Corollary 3. Exact default width

For the default height G(n)=floor(log_m floor(n/m))=H(n)-1,
one has d(n)=0, s(n)=m^H(n), S(n)=W^H(n). Along the decreasing chain every
later H is at most the initial H. Every later source total therefore divides
the first. Equation (2) proves, for all n>=m,

```text
B_n = W^floor(log_m n).                              (3)
```

At n=m^h, this is exactly W^h, so its polynomial order cannot be reduced
when W>1. P affects exits and cost, but not this default productive width.

For comparison define the specific gcd-free recurrence
U_j=1 for j<m and U_n=S(n) U_(n-s(n)). Writing n=sum a_j m^j in base m
gives U_n=W^(sum_(j>=1) j a_j), because each subtraction removes one largest
power. At n=m^(h+1)-1 its exponent is (m-1)h(h+1)/2. Hence retaining gcd
cancellation changes this particular upper construction from worst-shell
exp(Theta((log n)^2)) to polynomial width when W>1. This comparator is
defined here; it is not alleged to be a predecessor's optimal width.

## Corollary 4. Polynomial adaptive widths, including empty roots

Put G_*(N)=max_(m<=j<=N) G(j), with N>=m. Every source in the chain for
any n<=N divides W^H(N) P^G_*(N), since k(j)<=H(N) and d(j)<=G(j).
This remains true when W and P have shared prime factors. Thus

```text
B_n divides W^H(N) P^G_*(N),  m<=n<=N.               (4)
```

In particular, fix M>=2 and integer g>=1 and use the predecessor's height
G(n)=g floor(log_M floor(n/m)). This is monotone, so (4) at N=n gives

```text
B_n divides W^floor(log_m n) P^(g floor(log_M floor(n/m))),
B_n <= n^(log_m W + g log_M P).                     (5)
```

This proves polynomial width even when m^g<M, where the general adaptive
envelope in PR4638 has a subexponential factor. Equation (5) need not be
sharp. No lower bound or universal polynomial width theorem for mixed rank
alphabets follows. The hypothesis that every paid rank is one is essential
to the cut reduction used above.

## Scope and attribution

The new results are the exact homogeneous source/cut reduction, chain-LCM
solution, default closed form and polynomial adaptive divisor. The question
comes from PR4638's request to retain actual gcd savings. PR5962's independent
prime-coordinate projection and PR6086's shell counting retain a different
mechanism and are not audited or extended here. This proof does not tighten
their generic semigroup estimates.

Credit Jacob Alan Sussman's integer compiler; zxv's PR4436/4483 chronological
forest; Mihir Srivastava's PR4507 local gcd/LCM policy; codyw912's PR4638
arbitrary-height transfer and width question; and Cinna Davis and Ryanson
Jonathan for the retained native/flow lineage. LCM arithmetic, positional
notation and finite geometric sums are classical. No literature-wide
priority is claimed for those tools.

This is a conditional mathematical specialization. It supplies no physical
native inventory, storage/tape cost, numerical precision, stock constant,
outer consumer, new kappa or complete multiplication theorem. In particular,
polynomial productive width does not bound the cost of generating every
smaller program. The five selected framework assumptions remain.
Independent human and formal proof-kernel review are unclaimed.
