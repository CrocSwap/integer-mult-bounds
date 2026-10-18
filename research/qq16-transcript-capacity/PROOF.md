# Information required by the fixed QQ16 erasure family

Fix the conserved `F0/B_1_2` pair and ordinary tail from
[PR #1969](https://github.com/CrocSwap/integer-mult-bounds/pull/1969),
as retained in `research/joint-query`. Let `G` be a finite regular cover
containing the actual routes and let `N=|G|`.

**Claim.** Suppose an additional read-only rational-linear record, taken
from the original input, has rank at most `d` on the family below.
The dimension of original selected `(X_A,X_T)` values still invisible
after adding that record is at least

```text
max(0, ceil(88 N / 7) - d).                              (1)
```

Consequently the complete initial query `R2 X`, of rank at most `8N`
on this family, does not repair selected-input recovery. Every record
of at most twelve rational scalars per cover owner also fails.
Thirteen is a necessary integer width in this model, not a sufficient
width, exact minimum, native operation count or recursive rank bill.

The three-query rank method belongs to
[PR #2104](https://github.com/CrocSwap/integer-mult-bounds/pull/2104);
the erased-state injection belongs to the original QQ16 work.
The new step measures the **joint A/T defect** before choosing a
record. It allows selected-input reads and arbitrary rational mixing
across cover owners, answering the full-initial-`R2 X` handoff in
[discussion #2074](https://github.com/CrocSwap/integer-mult-bounds/discussions/2074#discussioncomment-18932289).
It also extends the specific scalar-mixer family in
[PR #2122](https://github.com/CrocSwap/integer-mult-bounds/pull/2122).
The predecessor calculations are not claimed as new here.

## 1. Observation and capacity contract

Use logical coordinates and the selected sets

```text
A = [0,7,20,27,36,46,57,111],
T = [21,37,47,76,81,87,92,110],
U = {0,...,111} minus (A union T).
```

The old observations are selected endpoints after `B_1_2` and their
later selected-only descendants, completed-X descendants at the retained
output endpoint, and the five forward-query histories. The first pair
and ordinary tail are unchanged. There is no separately saved copy of
F0's transient A output: it is generally nonzero on this family and
would be additional information. Reading the former-Y hole as a
completed-X output is also outside this contract.

Grant a record `L z + c + H` before F0, where z is the complete original
logical input, L is rational-linear, c is fixed and the arbitrary dirty
baseline H is common to the two compared executions. Grant exact reads,
indefinite retention and all physical costs for free. The record does
not change the first pair or ordinary schedule. The final decoder may
be nonlinear; the record encoder L is linear. Records at several cuts
are covered if their combined restriction to this family is linear of
rank at most d and they do not change its trajectory.

Capacity counts independent rational scalars **on this family**, not
field names. A q-coordinate field with one scalar per cover owner has
capacity at most qN. Encoding extra independent information in payload
modes or other storage must count the increased rank. The actual full
query `R2 X` preserves the payload-constant subspace and has at most
8N outputs there.

Use arbitrary cover values constant in every payload block. Actual
cover maps retain their regular owner action; their payload translations
act trivially on this subspace. Distinct owners are not identified.
The inherited invertible endpoint gauges in
[BRIDGE-REVIEW.md](../joint-query/evidence/BRIDGE-REVIEW.md) transport
indistinguishable logical inputs to physical inputs. They are not
presumed free to execute. This works at every positive tensor size
but supplies no recursive precision bound.

## 2. Rebound three-query premise

Write `B_s=R_s iota_U`, s=0,1,2. For each ordinary port p let r_p
be its column of R and g_(s,p) its owner route. Exact packet checks give

```text
|U|=96,                  r_p^T r_p=4,
sum_(p in U) r_p r_p^T=48 I_8,
R_A R_A^T=R_T R_T^T=4 I_8,
g_(s,p) g_(t,p)^-1 distinct over p in U, for each s<t<=2.
```

The verifier reads the literal alignment maps before the first source
sweep in F1 and F2, checking agreement with the current and future Y
alignments in `B_1_2`. Stage zero has the identity route. This checks
the frozen packet, with no pending PR executable dependency. It inherits
the reviewed packet-to-native binding rather than replaying all words.

For the regular right action `Q_g f(d)=f(dg)`, a nonidentity route has
trace zero and `tr(Q_1)=N`. Thus

```text
B_s B_s*=48 I_(8N),
tr(B_s B_t* B_t B_s*)=1536 N                       (s!=t).
```

Indeed, in `B_s B_t*` the coefficient at the distinct route indexed
by p is `r_p r_p^T`. The identity coefficient of its product with its
adjoint is `sum_p (r_p r_p^T)^2=192 I_8`.
For `S=[B0;B1;B2]` and `K=S* S`,

```text
tr(K)=1152 N,
tr(K^2)=3(18432)N+6(1536)N=64512 N,
rank(S)>=tr(K)^2/tr(K^2)=144 N/7.                         (2)
```

The inequality is Cauchy--Schwarz on K's nonzero eigenvalues; rational
and real ranks agree. This is PR #2104's calculation, rebound to main's
packet. Distinct abstract labels in a nonfaithful quotient would not
justify the regular-trace step; no such quotient is used.

## 3. The complete selected defect

Let `V=ker B1`. For h in V set only pair 0 nonzero and define W(h) by

```text
X_U=h,                           Y_U=0,
X_A=-P_(0,A)B0h-P_(2,A)B2h,       Y_A=-X_A,
X_T=P_(0,T)ell_(0,A)P_(2,A)B2h,   Y_T=-X_T.               (3)
```

Other pairs and helpers are zero, an admissible subspace of the
arbitrary-input contract. The selected sections and queries are
two-sided inverses on their selected spaces. Operator order matters.

The defect `J(h)=(X_A,X_T)` retains exactly `(B0h,B2h)`, since

```text
B0h=-ell_(0,A)X_A-ell_(0,T)X_T,
B2h=ell_(2,A)P_(0,A)ell_(0,T)X_T.                         (4)
```

Thus `ker J=ker[B0;B2]` on V. The rank identity for restriction to a
kernel and `B1 B1*=48I` imply

```text
dim J(V)=rank([B0;B1;B2])-rank(B1)
        =rank(S)-8N >= ceil(88N/7).                      (5)
```

Both selected blocks matter. An A defect can remain when B2h=0;
other directions carry a T defect. Counting only one block would not
give (5).

For every h in V, substitution in the ordered forward map gives
`f0=B0h+ell_(0,A)X_A+ell_(0,T)X_T=0`. After F0,

```text
X_U=Y_U=h,
X_A=P_(2,A)B2h,     Y_A=-P_(2,A)B2h,
X_T=Y_T=0.
```

At B1, `R2 Y=B2h-B2h=0`, so E2 makes `u_A=0`, with u_U=h,
u_T=0. Also a1=ell_(1,T)X=0 and b1=R1u=B1h=0. The conserved
B formulas leave only `Y_(0,U)=h`.

The retained tail follows the original
[selected witness](../joint-query/evidence/QQ16-SELECTED-WITNESS.md):
the first plus bridge creates -h in Y1; the first minus bridge removes
it before B3; every later active local source is zero. The terminal
leaves h only in the former-Y hole. Selected endpoints after B1,
completed-X descendants and all five forward queries are zero.
The executable replays this formal-h tail and checks every stored
state. This is an inherited schedule, not a new scheduling theorem.
Later homogeneous selected-only linear controls preserve zero.

## 4. Arbitrary records and the full R2 read

Restrict the record to (3): `C=L W|V`, of rank at most d. For linear
maps J and C on a finite-dimensional space,

```text
dim J(ker C) >= dim J(V)-rank(C).                         (6)
```

A complement of ker C has dimension rank(C); its J-image can add
at most that many dimensions to J(ker C). Equations (5)--(6) prove
(1). A positive bound supplies h with Ch=0 and J(h)!=0. The inputs
W(h) and zero agree on all observations, including the common dirty
baseline and offset, but need different selected outputs. No decoder
from these records can restore all inputs.

Rational nullspaces give rational h. Clearing denominators makes h
integral; the selected sections are dyadic. Further common scaling
gives dyadic logical inputs of arbitrarily small nonzero magnitude.
Their inherited physical pullbacks are admissible complex dyadic
inputs. No compact formula for h on the actual regular cover, bit-length
bound or recursive precision bound is asserted.

The full original R2 X on (3) is

```text
-ell_(2,A)P_(0,A)B0h
+ell_(2,T)P_(0,T)ell_(0,A)P_(2,A)B2h.                    (7)
```

It is not B2h. It can detect an earlier B2-only counterexample, but
still has at most 8N independent outputs. Hence at least ceil(32N/7)
selected-defect dimensions remain invisible. The operators in (7)
may mix owners; no scalar-mixer or commutation assumption is needed.

For q scalars per owner the residual is at least
`max(0,ceil((88/7-q)N))`. At q=12 it is ceil(4N/7)>0. At q=13
this lower bound is zero and supplies no obstruction or construction.

As a positive boundary control, the sixteen-coordinate record
`(B0 X_U,B2 X_U)` determines J on W(V) by (3). This establishes
recovery only on that family, not on all inputs or the full controller.

## 5. Verification and limits

The executable checks source pins, actual routes and Gram identities,
selected units, trace arithmetic and the retained formal-h tail. Exact
rational fixtures with noncommuting selected section matrices test
(3), (4), (7), both local maps and a concrete full-query invisible
direction. Separate rank calculations check (6), a dimension-sharp
example and a sufficient two-record control. These are failure-mode
tests; the quantified assertion follows from the written proof.

Thirteen through sixteen coordinates remain unresolved for the full
controller. Nonlinear encoders, changed trajectories or first pairs,
and uncounted independent payload storage are outside this theorem.
Native reads, endpoint access, chronological hosting, dirty workspace
restoration, recursive precision, supplier admission and a new
multiplication exponent remain open. No formal-kernel proof is claimed.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex
assistance. Apache-2.0. Predecessor credit is retained in the README.
