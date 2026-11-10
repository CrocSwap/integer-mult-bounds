# Rounded-backend delta for the actual shared P104 opening prefix

This is a source-specific audit of PR #6678's released rounded-backend question.
It preserves that predecessor's exact rational and exact h/2-grid theorem.
The quantization, compute/uncompute and covariance principles used below are
classical and have direct repository predecessors credited in README and NOTICE.

## Actual source and granted local interface

At PR #6678 head `1025aa5f742a760da526df56e354f618b95f2bf5`, its retained
PR #6621 source is the compressed word with Git blob
`3e8f74fc90d386eb7042fc6d741a84c41d73d8d6` and SHA256
`25b350a56ce11436fccf4c987da466cb002fa28dfc9b7e9d88e8b1b748b79df3`.
The first eighteen instructions add `r471 + r525/2 + 2*r704` separately to
`D=(119,169,191,193,204,206)`. All nine public roles enter frame3, whose native
label list is empty. Slot770 is owned, outside public roles0..769, and its first
source occurrence is `INIT770 frame737` at zero-based program index8448.
No suffix instruction is interpreted here.

Grant the same legal zero-owned INIT as PR #6678. Write the integer h-grid input as
`X=r471/h`, `Y=r525/h`, `Z=r704/h`, `D_j=r_Dj/h`. The replacement initializes
`t=0`, adds X,Y/2,2Z to t, adds t to each destination, subtracts2Z,Y/2,X from t,
then attempts zero-CLEAR. The three sources remain stable. The new local
program has12 ADDs plus INIT/CLEAR, compared with18 original ADDs. Its exact
arithmetic identity and lifetime ledger are PR #6678's result, not this audit's.

For the first backend, round the WHOLE UPDATED DESTINATION after EACH ADD to
nearest integer, ties to the even integer. This specifies a coarser h grid,
while the exact predecessor uses h/2 for odd Y. For the second backend, leave
integer updates exact and round each half-integer to its floor plus a fresh
independent fair UP bit. All tables for the new program stop before CLEAR;
CLEAR is permitted only if the retained owned value is exactly zero.

## Nearest-even parity law for every integer input

Even Y makes every update integral, so both programs agree and t restores.
Let odd `Y=2k+1`, where k is the mathematical floor Y/2, including negative Y.
Let

`xi=(X+k) mod2`, and `xi_j=(D_j+X+k) mod2`, both in{0,1}.

The old destination becomes `D_j+X+k+xi_j+2Z`. In the new program, nearest-even
preparation yields `t=X+k+xi+2Z`; its integer delivery gives
`D_j+X+k+xi+2Z`. Thus new minus old is `xi-xi_j`. It is zero for even D_j,
and is `2xi-1` for odd D_j. All changed coordinates have the same sign.
In physical units, the sharp difference bounds are h in the maximum norm and
sqrt(6)h in the Euclidean norm; all six odd destinations attain them.

For cleanup, subtracting2Z leaves `X+k+xi`. Subtracting Y/2 leaves the half
`X+xi-1/2`. Nearest-even rounding followed by subtraction of X leaves

`t_final = xi - ((X+xi) mod2)`.

This is zero for even X; for odd X it is `(-1)^k`. Multiplying by h restores
physical units. Hence the two rounded local words have equal public output
AND a legal new zero-CLEAR precisely when

- Y is even; or
- Y is odd, X is even, and every D_j is even.

The public-output equality and zero-CLEAR tests are separate obligations. For
example X=Y=1,Z=0,all D_j=0 gives the same public output in both programs, but
t_final=1 and CLEAR is inadmissible. Erasing that value would change the ABI.

The complete phase space is X mod2, Y mod4 and six destination parities:
2*4*64=512 classes. There are256 even-Y classes and2 additional legal-equivalent
odd-Y classes, totaling258. Nonzero owned residue occurs in128 classes;
public differences occur in252;126 have both failures. Public equality alone
holds in260, including2 classes with illegal CLEAR. Arbitrary integer Z and
larger/signed inputs satisfy the same laws because2Z is exact and the relevant
parities are those displayed. None of this refutes exact h/2 execution.

## Fresh stochastic law before CLEAR

Fix any odd Y and any integer X,Z,D. Let the six old half-rounding UP bits be
`eta_1,...,eta_6`, the new preparation UP bit be xi, and the new inverse UP bit
be zeta. Each bit is independent and fair. UP means floor+bit at the actual
whole updated half-value, including the negative half in uncomputation.
Writing E for error against the exact public target, in physical units:

`E_old,j = h*(eta_j-1/2)`,
`E_shared,j = h*(xi-1/2)`,
`t_final = h*(xi+zeta-1)`.

All means vanish. The six-dimensional public covariance matrices are

`Cov(E_old)=h^2*I_6/4`, and `Cov(E_shared)=h^2*1*1^T/4`.

The coordinate variances and total Euclidean mean-squared error,3h^2/2, agree.
For the sum of all six coordinates, variance changes from3h^2/2 to9h^2. For
the unit all-ones direction, it changes from h^2/4 to3h^2/2, a factor6. A
zero-sum receiver cancels the shared error. An actual downstream receiver and
its tolerance must therefore be checked; unchanged coordinate error or trace
does not establish unchanged receiver error.

The owned pre-CLEAR residue is -h,0,+h with probabilities1/4,1/2,1/4. Its
variance is h^2/2 and its covariance with each shared public error is h^2/4.
Half of the new traces cannot legally CLEAR. Consequently these covariance
formulas describe the public delivery stage before a potentially inadmissible
CLEAR; they are not a claim about a legal complete rounded caller. The old
six UP bits plus xi,zeta have256 equally likely joint assignments. The finite
receipt enumerates all of them at X=Y=1,Z=0,D=0; the displayed argument proves
the law for every odd Y and integer entrance. Even Y needs no half coins and
has zero rounding error and zero cleanup residue in this local model.

## Safe inverse choices and remaining costs

Complementing the forward UP choice for the inverse, `zeta=1-xi`, gives zero
residue. Reusing the SAME UP bit gives residue ±h instead. The convention is
UP at a negative half-value; it must not be confused with threshold/seed
conventions in prior stochastic inverse work.

More generally, let the actual rounded half-step increment during preparation
be `p=R(X+Y/2)-X`. After reversing2Z, subtracting that exact integer p and then
X restores zero. A caller may record p, retain a suitable random tape, or
recompute a deterministic p from stable X,Y. These options require explicit
source access, control, storage or recomputation contracts and their costs.
There is no universal one-bit-retention lower bound here. Restoring t alone
also does not repair the deterministic public-output differences already
delivered. A repaired backend/receiver theorem is a separate obligation.

## Evidence boundary and credit

The primary interpreter uses signed integer divmod and literal whole-sum
updates; the independent oracle uses its own Fraction interpreter and parity
and probability derivations. Complete finite tables corroborate, rather than
replace, the all-input argument. Exact h/2 execution on all 512 entrances is a
positive control. Signed/large translations, illegal CLEAR, wrong tie and
truncation rules, complemented versus same UP bits and recorded/recomputed
increments are separate controls. No Monte Carlo is used.

Nick Petalas's PR #6678 supplies the exact substitution, lifetime/resource ledger and
released question; DreamingOfClouds's PR #6621 supplies the actual prefix/recipients,
retaining Ali Romman, Rohan Arun, Erwan L. and the original NOTICE lineage.
Arham Tahir's PR #2665 supplies prior source-specific nonzero cleanup/strict-zero
boundary; ywz65's PR #2730 supplies the separate completed-native mixed-grid repair;
zxv's PR #6066 supplies complemented stochastic inversion and tape lifecycle;
Petalas's PR #5912 with ywz65's PR #2555 supplies whole-sum nearest-even history/tie
boundaries; Petalas's PRs #6134/#6573 and Ali Romman's PR #6540 supply covariance/error-price
and fixed-receiver correlation context. This contribution adds only the
actual #6678/6621 nine-input coarse-backend classification and its exact joint
outcome audit, not those general principles.

No complete native/suffix/caller replay, compiler allocation or lifetime price,
backend physical admission, legal whole-call stochastic distribution, new
multiplication theorem, kappa claim, frontier change, proof-kernel verification
or global novelty/optimality theorem is established.
