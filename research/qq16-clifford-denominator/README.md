# Odd-denominator QQ16 obstruction with normalized Clifford coefficients

The complete-input obstruction in [PR2546](https://github.com/CrocSwap/integer-mult-bounds/pull/2546)
still holds when exact decoding may use normalized Clifford gates. The previous
result covered Gaussian-dyadic coefficients and explicitly excluded `1/sqrt(2)`.
This note closes that coefficient-ring gap. It does not construct a controller,
change the selected frontier or claim a new kappa.

## Coefficient-ring lemma

Put `zeta = exp(pi*i/4)` and `A = Z[zeta,1/2]`. Equivalently,
`A = Z[i,1/sqrt(2)]`. Its elements have unique expressions
`a0 + a1*zeta + a2*zeta^2 + a3*zeta^3`, with dyadic rational `aj`, because
`zeta^4 = -1` and `X^4+1` is the minimal polynomial of zeta over Q.
In particular `i=zeta^2` and `1/sqrt(2)=(zeta-zeta^3)/2`.

For every odd prime p there is a unital homomorphism

```text
A -> B_p = F_p[t]/(t^4+1),
zeta -> t,   1/2 -> 2^(-1).
```

The quotient is nonzero: division by the monic degree-four polynomial gives
unique representatives of degree less than four, so `1 != 0`. It need not be a
field. Thus `pA` is proper. Every finite matrix with entries in A preserves the
coordinatewise ideal pA, as do permutations, finite sums, products, tensor
products, conjugates and adjoints of such matrices. Complex conjugation sends
`zeta` to `-zeta^3` and preserves A.

Consequently, an integer square matrix is invertible over A if and only if its
determinant is a signed power of two. Sufficiency is the adjugate formula. For
necessity, a zero determinant is impossible for an inverse. If a nonzero integer
determinant has an odd prime divisor p, reduction of a putative inverse would
give `0 * det(inverse) = 1` in the nonzero ring B_p, a contradiction.
This is a statement about integer matrices of every finite size, not just the
specific eight-column minor below. Adjoining exact Clifford coefficients does
not enlarge the admissible unread-minor class.

Normalized H, S and T have entries in A:

```text
H = (1/sqrt(2)) [[1,1],[1,-1]],
S = diag(1,i),    T = diag(1,zeta).
```

T is included as a larger allowed alphabet, not described as a Clifford gate.
Pauli gates, controlled permutations, inverse gates, dyadic scalar ADD/SCALE
operations and arbitrary finite tensor depths also stay in A. No uniform depth
bound is needed for this algebraic statement. This is not an audit of every
primitive or recursive oracle that a prospective physical supplier might use.
An oracle with an odd-denominator coefficient must not be admitted by assumption.

## The fixed QQ16 observation contract

Use the actual `R`, selected sets A/T and ordinary set U96 from the unchanged
[QQ16 packet](../joint-query/README.md). The letter A denotes the coefficient
ring above or the selected port set according to context. The observation
contract is PR2443's fixed two-cut contract, as distinguished from other QQ16
interfaces:

- After complete F0, retain `x1_A/T`, `y1_A/T` and read `x1_(U\H)`.
- Immediately after B1, retain `y2_A` and `C=x2_U`.
- Make no intervening modification and grant no extra original-input read.

The original unread set `H0=[1,2,3,4,5,6,8,12]` has determinant -32 and passes
the ring-invertibility test. The alternative ordered unread set and input are
credited to PR2546:

```text
Hbad = [1,25,3,4,5,6,8,12],
z = [1,2,1,1,1,1,3,-2],
R_Hbad z = 10 e_1,      det(R_Hbad) = -80.
```

Here e_1 is the second centre coordinate. Let `P_A=R_A^T/4`, `q=10e_1`, and set
all owner/payload coordinates constant. Initialize

```text
x_U=iota_Hbad z,   x_A=-P_A q,   x_T=0,
y_U=0,            y_A= P_A q,   y_T=0.
```

Every cover permutation fixes these constant arrays. The actual conserved F0
equations give zero forward query, `x1_U=y1_U=iota_Hbad z`, and zero selected
outputs. The B1 future logger gives `y2_A=P_A q`; its ordinary target
subtraction gives `C=0`. Thus every observation is zero except

```text
y2_A = [5/2,-5/2,0,5/2,0,0,-5/2,0].
```

All observation entries lie in `5A`, but the required original ordinary
coordinate `x_1` equals 1. Reduction in B_5 annihilates every observation but
not the requested output. Therefore no finite A-linear decoder can recover
all original inputs from this observation contract. This includes normalized
Clifford processing of arbitrary finite owner/payload arrays, even when it
creates nonconstant arrays from the constant input. The proof uses entrywise
ideal preservation, not preservation of the constant-array subspace.

Fixed affine constants and arbitrary initial dirty workspace do not help an
exact affine circuit: compare this input and the zero input using identical
workspace and constants. Their observation difference lies in `5A`, whereas
the required output difference is 1. The difference follows the same A-linear
part. The schedule and coefficients must be data-independent. Adaptive or
nonlinear division and data-dependent branching are outside this theorem.
A fixed output frame and its inverse with entries in A do not help either:
applying the inverse would give a forbidden logical decoder.

This is not information loss over Q. The rational inverse exists and contains
`1/10`; explicitly allowing that coefficient defeats the ideal argument. Nor
does this witness exclude selected-input-only recovery. Its original selected
inputs are already dyadically determined by `y2_A`. New observations, a changed
first pair, odd-denominator operations and nonlinear decoding remain outside
scope. Approximation followed by rounding is nonlinear and is not ruled out.
Native execution, physical access/retention, hosting, precision, all-size
admission and a favorable complete supplier budget remain unproved.

## Reproduce and evidence

Python 3.12, standard library only:

```sh
python3.12 -Werror -I -B scripts/research_package.py --package research/qq16-clifford-denominator
python3.12 -Werror -I -O -B research/qq16-clifford-denominator/verify.py
```

The new checker imports no PR2546 executable. It independently reconstructs R,
checks both selected Gram identities, inverts both minors, and replays F0 and
the B1 observation rows on the displayed arbitrary-input family. It implements
exact four-coordinate cyclotomic arithmetic and a separate modular polynomial
remainder implementation for B_3 and B_5. It checks generator relations,
normalized H/S/T/inverses, tensor examples and the actual observation residues.
Meaningful controls include an admitted `1/5`, a perturbed witness, a missing H
normalization and a deliberately collapsed quotient. `RESULT.json` is a complete
read-only replay receipt; `--emit` prints a recomputed receipt without modifying
files. Entrypoint tests cover optimized execution, source/receipt corruption,
Git-free export and failure controls. These finite checks accompany the written
all-size ring argument; they are not a formal-kernel proof or human review.
The predecessor's 107889-set census is not repeated or claimed as new evidence.

Local validation passed on Linux x86_64 / WSL2 with CPython 3.12.15:
registered normal/optimized replay, all six behavioral test groups, package
metadata/source pins, and all 65 repository research-workflow tests. A separate
CPython 3.13.5 optimized replay also passed. Ruff 0.17.1 passed with
`--select E,F,I,UP,B,SIM --line-length 100`; `git diff --check` passed.
Hosted CI and the selected cold replay were not run for this local result.

## Engineering limits

The checker uses matrices of size eight, four-term ring elements, and tensor
examples through three qubits. Source bounds are 1 MB compressed and 11 MB
decompressed. Every loop has a finite bound from these fixed domains. Functions
remain under 60 physical lines. Validation uses explicit exceptions and remains
active with `-O`. Replay has no network access, imports of predecessor code or
writes. Python's required dynamic allocation is a rule-3 managed-runtime
deviation; these fixed dimensions and bounded source reads constrain live state.
Tests and warning-enabled replay plus Ruff check the interpreted code. There
is no pointer/preprocessor analogue requiring a further deviation. Broader
input domains require new explicit limits and resource checks.

## Open next questions

Can an unread set with an odd determinant factor be recovered with a priced
operation outside A? First specify its representation and an exact division
contract on arbitrary valid observations, then price access, retention,
restoration and precision. Ring invertibility alone neither provides nor prices
such an operation. This is blocked by the missing physical implementation, not
by the rational inverse. [TASK.json](TASK.json) records the structured handoff.

## Sources and credit

The exact baseline is main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority
revision 4, reconfirmed unchanged at 2026-10-15 16:22:07 UTC. Submission overlap
fully paginated 812 open PRs and 1276 Discussion records at 16:22 / 16:24 UTC,
with no warnings. The targeted ring-extension search found the predecessor and
this claim, not an existing extension. Metadata search is not a novelty proof.
[SOURCES.json](SOURCES.json) binds runtime inputs and the inspected
pending predecessor. Nick Petalas's PR2546 at
`3aff4ccbfaa1005e5093e95535e4d99aa3813e54` supplies the explicit odd-prime witness
and the Gaussian-dyadic boundary. starship-s's PR2443 at
`545c05e17243c962b112b91e7f84b4c1a41de7b8` supplies the arbitrary-input two-cut
decoder and observation contract. Gareth Davidson's PR2432 at
`cbede349fc764aa38379aa533befe3215916cfcd` supplies the unread-column criterion.
thakrarsagar's PR2470 supplies the separate retention census. Ali Romman and the
retained QQ16/native contributors supply the conserved maps, actual matrix,
selected sections and cover semantics. Their unchanged
[notice](../joint-query/NOTICE.md) retains the earlier geometry/compiler/supplier
lineage. No predecessor package is copied or modified. New material is
Apache-2.0. Evidence is author-checked, not independent human review.
