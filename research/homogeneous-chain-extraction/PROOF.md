# Exact two-call capacity of homogeneous query chains

This is a conditional operator theorem, not a physical supplier. The three-field
case is already in Cinna Davis's PR4698. The new result is the all-odd-length
construction, a new attaining even-length construction, explicit linear-size
boundaries, and a matching two-call bound
with arbitrary restored dirty workspace in the restricted ring below.

## Model and statement

Work over A = Z[q]/(q^4-1), with p=q^2, and let B=Z[p]/(p^2-1).
For the upper bound scalars may extend to any characteristic-zero field K,
and free boundaries may be arbitrary invertible matrices over K[p]/(p^2-1).
Thus the bound includes more scalar mixing than the construction needs.
It does **not** include arbitrary physical address maps, independently selected
column operations, or arbitrary Pauli operators beyond this global p. A physical
substitution must satisfy Q^T=Q and Q^4=I; transpose fixes the formal q.

Let n=2m+1 >= 3, and let J be the n-by-n upper shift. The two paid
offers are U=I+qJ and its **actual** raw inverse transpose

    U^-T = (I+qJ^T)^-1 = sum_{d=0}^{n-1} (-q J^T)^d.

There are invertible B-valued boundaries L,E,D,R with

    L U E D U^-T D R = diag(q I_(n-1), 1).

They use 5m-2 scalar ADDs, m field swaps, and 3m signed-p field scales.
ADD coefficients are only ±1 or ±p. These counts include **all** boundaries;
there are no zero-only inputs. The last input is arbitrary and is restored.
An ADD with coefficient p is implemented by p-conjugating its source, adding,
and restoring the source, so no q query is implicit in a boundary. The counts
are field macros, not a physical tape/runtime invoice.

In this model any two calls to U or its inverse/transpose/raw-dual orientations,
with arbitrary free boundaries and any number of restored dirty fields, can
produce at most n-1 independent q jobs. The number of such jobs must be even.
Consequently n-1 is optimal for every odd n. For even n we prove only the
upper bound n-2, attained by the separate even construction below. The exact
capacity for every n>=2 is therefore 2 floor((n-1)/2).

## Odd-chain constructive factorization

Index fields 0,...,2m. Define D=diag(1,p,1,p,...,1) and E=I-p(J^T)^2.
Both have explicitly invertible B-valued circuits. Conjugation gives

    D U^-T D = (I+q^-1 J^T)^-1.

Since (I-a)(I+a)=I-a^2 for a=q^-1 J^T, multiplication by E gives

    E D U^-T D = I-q^-1 J^T.

This removes every long-root term, including odd powers beyond the quadratic
term of the three-field predecessor; E itself has only p entries. Therefore

    U E D U^-T D = E_(2m,2m) + q T,   T=J-pJ^T.

The identity follows from JJ^T=diag(1,...,1,0). All operations are in A.

Let u_(2k)=p^(m-k), u_(2k+1)=0. Then Tu=0 and u_(2m)=1.
Take R to have columns e_0,...,e_(2m-1),u. It adds
p^(m-k) times the arbitrary spectator to field 2k, for 0<=k<m.
The first 2m inputs are unchanged otherwise. These are m reversible ADDs.

Let W have columns T e_0,...,T e_(2m-1),e_(2m). Then

    (E_(2m,2m)+qT) R = W diag(q I_(2m),1).

The following explicit circuit is W^-1, so L=W^-1 and no determinant
assumption or division is being hidden. On output vector y:

1. For k=1,...,m-1, add p y_(2k-2) to y_(2k), in that order.
2. For k=m-2,...,0, add p y_(2k+3) to y_(2k+1), in that order.
3. Multiply every odd field by -p.
4. Add p y_(2m-2) to the last field y_(2m).
5. Swap each adjacent pair (0,1),(2,3),...,(2m-2,2m-1).

For a vector Wz, the even-field prefix sums recover each z_(2k+1).
The odd-field suffix sums, followed by -p, recover each z_(2k).
The last ADD restores z_(2m), including its arbitrary initial value.
This proves the circuit identity on every independent input column.

E is emitted by adding -p times field i-2 to field i in descending order
i=2m,...,2, using n-2 ADDs. L uses n-2 ADDs, m signed-p scales and m swaps.
The two D boundaries use 2m p scales. With the m ADDs of R, the full inventory
is (m+2(n-2), m, 3m) = (5m-2, m, 3m).

## Even-chain construction

Let n=2m>=4, gamma=p^(m-1), and E=I-p(J^T)^2. This time no D
conjugation is needed: E U^-T=I-qJ^T. Define a weighted cyclic permutation M by

    (Mx)_i = p^i x_(i+1) for 0<=i<n-1,
    (Mx)_(n-1) = gamma x_0.

All its weights are 1 or p, so it is invertible by field permutation and
monomial maps. The special wrap weight gamma is essential; simply extending
p^i to the last row fails when n is 2 modulo 4. Direct multiplication gives

    U M E U^-T = F + q O,
    F = E_(n-2,n-1) + gamma E_(n-1,0),
    (Ox)_i = p^i (-x_i+p x_(i+2)) for 0<=i<n-2,
    (Ox)_(n-2) = gamma x_0-x_(n-2),
    (Ox)_(n-1) = 0.

Define u_(2k)=p^k, u_(2k+1)=0, and v_(2k)=0,
v_(2k+1)=p^(m-1-k). Then Ou=Ov=0, u_0=v_(n-1)=1,
Fu=gamma e_(n-1), and Fv=e_(n-2).
Take R with columns e_1,...,e_(n-2),u,v. It is an invertible source
permutation followed by n-2 ADDs from the two arbitrary spectator fields.
For the other n-2 columns F e_i=0. Consequently

    (F+qO) R = W diag(q I_(n-2),I_2),
    W = [O e_1,...,O e_(n-2),gamma e_(n-1),e_(n-2)].

Here is an explicit reversible W^-1 circuit. Prefix-accumulate the even output
fields y_0,y_2,...,y_(n-4), adding p times the previous accumulated even field.
Suffix-accumulate the odd output fields y_1,y_3,...,y_(n-3), adding p times
the next accumulated odd field. Add p y_(n-4) to y_(n-2) to restore the odd
spectator. Multiply each of the first n-2 fields by p on even indices and -p
on odd indices, and multiply the last field by gamma. Swap every adjacent
pair, including the last pair. The query fields become their original order;
the last pair becomes the two restored spectators in their original order.

Thus with L=W^-1,

    L U M E U^-T R = diag(q I_(n-2),I_2).

The emitted circuit realizes the source permutation with n-2 swaps, M's
cyclic shift with n-1 swaps, and the final order with m swaps. For
eta=(m-1) mod 2 its full boundary inventory is

    ADDs = 3n-7, swaps = 5m-3, signed-p scales = 3m-3+2 eta.

There are n-2 ADDs each in R and E, and n-3 in L. M uses m-1+eta
p scales and L uses n-2+eta. Identity scales are omitted. For n=2,
conjugating U by the field swap S gives U^T, so S U S U^-T=I:
two swaps suffice, attaining the capacity zero. No clean spectator is assumed.

## Two-call upper bound with restored dirty workspace

Let N=n+s include arbitrary dirty workspace, and pad J by a zero s-by-s block.
Every oracle orientation reduces to I+epsilon q J_i, with J_i=J or J^T and
epsilon=±1, up to invertible B-valued factors. For inverses use

    (I+qJ_i)^-1 = (I-qJ_i)(I-pJ_i^2)^-1.

The second factor is free and invertible because J_i is nilpotent.
It can be absorbed into adjacent free boundaries. Thus an arbitrary two-call
word has the form A_0 (I+epsilon q J_1) B_0 (I+delta q J_2) C_0,
with A_0,B_0,C_0 invertible over K[p]/(p^2-1).

Specialize p=1 but retain both q=1 and q=-1. Invertible free boundaries
remain invertible at this component of K[p]/(p^2-1). The even coefficient is

    A_0 (B_0 + epsilon delta J_1 B_0 J_2) C_0.

Its rank is at least N-rank(J_1) = N-(n-1), by the rank inequality for
an invertible matrix plus a rank-at-most-(n-1) perturbation. The desired
diag(q I_r,I_(N-r)) has even coefficient rank N-r. Therefore r<=n-1.
This proof includes every workspace field and its arbitrary input. If a free
boundary or output permutation is absorbed into the desired endpoint, the
same rank conclusion holds.

Every padded oracle orientation has determinant 1 at both q=1 and q=-1,
because its shift is nilpotent. Every free boundary has the same determinant
at these two points, since p=1 at both. The endpoint determinant ratio is
(-1)^r. Characteristic zero gives r even. The same statements hold for any
mixture of q and q^-1 jobs, since q^-1=q at these points. For odd n our circuit
attains r=n-1; for even n the resulting upper bound is r<=n-2, also attained above.

This is a formal homogeneous-ring restriction. For the standard Gaussian
C with eigenvalues 1,i, C^tensor(f) represents all four q eigenvalues only
when f>=3. The construction holds at **every** positive width by substitution.
The ring lower bound applies to a faithful representation, and consequently
to any uniform family satisfying this restricted model at those larger widths.
It is not a lower bound for every isolated small width or for all physical
monomial/scalar circuits. For example at f=1, C=((1+i)/2)I+((1-i)/2)P
is itself a unit of the scalar/P ring, so no such two-call bound follows there.

## Conditional complete ledger and a direct-synthesis stop

Suppose two provider calls have a common commuting transverse rank-b Gaussian
on every chain field, using disjoint transverse axes, and the actual raw dual
admits its true Pauli normalization. Suppose each call has autonomous helper
target moment H_t and a **complete** paid moment P_t, with t=1-C. Then this
controller has moment surplus

    2 H_t + r(2b+1)^t + (n-r)(2b)^t - 2 P_t,
    r = 2 floor((n-1)/2).

Every provider charge and both orientations must be present in P_t. For
E=P_1-H_1-nb, the rank surplus at C=0 is r-2E.
In particular a positive rank surplus requires E<r/2 (E<m for odd n). This necessary threshold
is not sufficient for a positive moment at a chosen C, much less for compiler,
BIT and outer funding. A raw-dual orientation with different helpers needs its
own target and paid terms instead of a symmetric factor of two.

Directly synthesizing U by its n-1 unary q shears does not meet the allowance.
Even favorably granting transverse cost exactly n b^t per invocation, its
paid moment is n b^t+(n-1), before any further costs. For b>=1 and 0<=t<=1,
subadditivity yields (2b)^t<=2b^t and (2b+1)^t<=2b^t+1, so the complete
surplus is at most r-2(n-1), which is -(n-1) for odd n and -n for even n.
At b=0 and t>0 the same expression is exact.
Thus direct acquisition of each chain edge loses for every useful saving.
Already-paid native observations or a changed joint provider would be needed.
Their physical acquisition and restoration costs are **unknown** here.
