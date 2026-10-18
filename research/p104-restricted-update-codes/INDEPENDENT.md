# Independent mathematical check

This is an internal AI-assisted independent derivation and implementation, not
human review or a formal-kernel proof. It reads no executable primary or
predecessor implementation. The pinned PR3059 source texts and scientific model
were read; its code was not imported. The literal P104 word and inherited
prefix-parity mechanism retain credit to Tekalign/PR3025/3033 and Nick
Petalas/PR3035/3037. PR3059 is the source of the changed pointwise-versus-mutable
question, not an accepted theorem about a changed construction.

## Contract and exact minimal code

The source coordinates are signed **integers**, arranged as the real and
imaginary coordinates of Gaussian integers. The word does not here accept
arbitrary real-valued source entries. Let X=Z^d, let H be any additive subgroup
of X, and let D:X -> A be any function. A code consists of C:X -> S, a decoder
f with D=f C, and, for every h in H, a deterministic code-only update T_h with
C(x+h)=T_h(C(x)). The code includes every persistent input-dependent state used
by these updates. There is no assumption that C or T_h is linear.

Define Sigma_H(x)(h)=D(x+h). If C(x)=C(y), applying T_h and f proves
Sigma_H(x)(h)=Sigma_H(y)(h) for every h. Hence every admissible code partition
refines the signature partition. Conversely, signatures themselves form a code:
f reads the coordinate h=0, while

    (T_k sigma)(h) = sigma(h+k).

This is well defined on reached signatures, has inverse T_-k, and satisfies
T_k T_l=T_(k+l). Thus signature equality is exactly the coarsest admissible
partition and its number of classes is the exact minimum number of reached
states. This proof is valid even if the minimum is infinite. Finite capacity
requires a separate finiteness premise.

For a finite quotient G=X/P by a subgroup P of global periods of D, signatures
need only be indexed by the image of H in G, equivalently H/(H intersection P).
The quotient need not use the *maximal* period subgroup. A sufficient period
subgroup gives the same set of full signatures, possibly with duplicate
representatives. For H=X, signature equality is equivalence modulo the maximal
period group. For a proper H it need not be a group congruence; unequal fibers
already occur in the exact examples below. Calling those classes lattice cosets
or assigning them a quotient-group addition would be unsupported.

On a finite quotient, repeated positive steps generate the same cyclic group
as positive and negative steps. A bounded number of future updates gives a
different contract. These distinctions matter when applying the result to an
actual caller.

## Independent literal and linear construction

The executable `independent.py` stores Gaussian pairs and evaluates the literal
word as d=a-b, s=b+floor(d/2), e=i d, B=s-floor(e/2), A=B+e, with componentwise
Euclidean floors. In contrast, its ideal matrix uses no stage evaluator. After
k stages on the low address bits, the coefficient from address b to a is zero
unless their untouched high bits agree. Otherwise, if h is the Hamming distance
of the processed address bits, it is

    (1+i)^(k-h) (1-i)^h / 2^k.

Each address path is unique. Expanding complex multiplication gives the real
integer numerator matrix. The checker subtracts this matrix applied to x from
2^r times the independently evaluated literal word to obtain D_r.

The signed pair identity is D_1=(q-p,p-q,q-p,p-q), where p and q are the
real and imaginary input-difference parities. It is checked on all 7^4=2,401
signed local inputs. It also proves the sufficient prefix-lattice periodicity:
if all ideal translated pair-input differences at all prefixes are even Gaussian
integers, the pair correction is unchanged, so induction carries the ideal
translation through the literal word. The same induction establishes a scalar
period q0=2^(floor(r/2)+1). Indeed, the coefficient before stage k+1 is a
Gaussian unit times (1+i)^k/2^k, and multiplying by q0 has (1+i)-valuation
2(floor(r/2)+1)-k >= 2 for k <= r-1. It is therefore an even Gaussian integer.
This is an all-positive-rank written periodicity argument, not an all-rank
state-count theorem.

## Independent finite quotient at rank three

For each k=0,...,r-1, each pair (a,b) of the next address stage, and each real
component c, define the rational character

    chi_(k,a,b,c)(x) = ((U_k x)_(a,c)-(U_k x)_(b,c))/2 mod Z.

Their joint kernel is exactly the sufficient prefix-parity lattice Gamma:
vanishing means every difference at the next ideal prefix is even; by induction
all those ideal prefixes are integral. The preceding pair argument proves that
Gamma consists of global periods of D. This claim does not invoke or reprove
maximality of Gamma.

For r<=3 the checker constructs every character coefficient from the closed
matrix above and checks its denominator divides q=2,4,4 respectively. Characters
are thus represented exactly by residue vectors modulo q. It enumerates their
image by adjoining the characters of the standard coordinate vectors. If K is
the subgroup already listed and v is the next generator, let m be the first
positive integer with m v in K. Then K, v+K, ..., (m-1)v+K are disjoint and
exhaust K+<v>. The algorithm materializes exactly these cosets and retains an
integer representative for each character. Induction over all coordinates
proves complete and duplicate-free coverage of X/Gamma. It uses no predecessor
index-two lattice basis, HNF, determinant oracle or primary inverse basis.

At rank three the extension orders are

    4,4,2,2,2,2,2,1,4,2,2,1,2,2,1,1,

whose product is 32,768. D is evaluated once on each representative. Adding
s e_j to a character gives the exact finite translation action. For every
coordinate j and s=1,2,4, all q/gcd(q,s) defect values along that orbit form
the signature. The checker also checks closure under both rotations of every
reached signature set, establishing its abstract forward/inverse permutation.

## Complete finite results

| r | independently covered domain | step 1 states | step 2 states | step 4 states |
|---|---|---:|---:|---:|
| 1 | all 2^4=16 low-bit inputs | 4 | 3 | 3 |
| 2 | all 4^8=65,536 low-bit inputs | 56 | 33 | 25 |
| 3 | all 32,768 joint-character classes | 27,392 | 21,144 | 10,225 |

Each count holds for every one of the d=4,8,16 real coordinates separately.
The scalar-period and character-kernel proofs extend these finite counts to all
signed integer inputs at the stated ranks. Ranks one and two are exhaustive
raw-box censuses independent of a lattice reduction. Rank three is an exhaustive
independently constructed finite quotient, with the written completeness proof;
it is not a raw-box enumeration.

The exact minimum fixed bit capacities for steps (1,2,4) are (2,2,2), (6,6,5),
and (15,15,14) respectively. In particular 33, rather than 32, rules out a
five-bit step-2 code at rank two. Neither unit nor double coordinate steps
retain the pointwise one-bit saving at ranks two and three. No rank-seven
census or all-rank lower bound follows.

The receipt also includes all per-coordinate signature/fiber hashes and fiber
histograms. For example the rank-three step-1 classes, on the 32,768-character
quotient, have sizes 1,2,4 with multiplicities 22,528,4,608,256. Their unequal
sizes provide a concrete warning against quotient-group language.

## Controls, reproduction and limits

The checker uses explicit exceptions, so checks remain active under optimized
Python. Besides the complete censuses and inverse-rotation checks, controls
cover 2,401 signed pair cases and 21 signed scalar-period fixtures across ranks
one through three. It rejects a reversed literal rotation sign, an incorrect
rank-two scalar period 2, and the attempted use of equal pointwise defects as
unit-update code states. The pointwise collision is x=0, y=(0,0,1,1), with
D_1(x)=D_1(y)=0 but D_1(x+e_0) != D_1(y+e_0).

Run, without producing checkout output files:

    python3 -B independent.py --rank3

Raw-box and rank-three JSON receipts were saved in the owning external run
directory as `independent-result.json` and `independent-rank3-result.json`.
The latter includes the former plus the rank-three census. A separate
receipt comparison checks all 84 coordinate/step contracts against the primary
RESULT.json, including every fiber histogram after the exact raw-box-to-lattice
multipliers 4 and 1,024 (and multiplier 1 at rank three). The comparison passes.
No code file imports an executable predecessor or primary model.

The general signature proof and scalar periodicity argument are written proofs.
The displayed counts and controls are exact finite computations under those
premises. No formal-kernel proof is supplied. An arbitrary state permutation can
be extended to unused binary labels, but this proves neither a cheap circuit nor
an encoder, decoder, dirty-work restoration, physical memory bound or favorable
recursive moment. Those paid obligations and the actual caller's translation set
remain unresolved. The main theorem's assumptions and proof in `PROOF.md` were
reviewed; no material mathematical defect was found.

Ross Richardson, with OpenAI Codex assistance. Apache-2.0.
