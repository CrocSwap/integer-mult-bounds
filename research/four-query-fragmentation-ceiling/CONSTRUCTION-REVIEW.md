# Independent inspection of the four-query module and reverse oracle

Independent reviewer, for Jerry Chen / @CubeJerry, with substantial OpenAI Codex assistance.
2026-11-06. Apache-2.0. Review within the same AI-assisted session; not external
human acceptance. This is verification evidence for the integrated construction.

## Verdict

No mathematical counterexample, missing paid transform, or contract error was
found in the literal atomic-supplier construction, its reverse-functional
oracle, the Gaussian normalization, or the stated local signed invoice. The
four-query attainment is valid in the inherited scalar, positive-formal-body,
atomic-native contract. It is not a complete physical supplier admission or a
new multiplication bound. I did not independently audit the companion global
grammar ceiling in this review.

## Literal word and all inputs

After N_L(B,A), write the pair as A=L A0, B=L(B0+S A0).
The first sign/query gives A=S L B0. The following ADDs give
A=L((S-1)B0-S A0), B=S L B0. The second query gives
A=S L(B0-A0), and the final sign/ADD gives A=S L A0. Thus both
old auxiliary inputs retire exactly, with no cross term. The independently
encoded shorter signed-query word in reverse_check.py has the same
endpoint: its lower negative query gives B=-S L A0; its upper query gives
A=S L B0; swap/sign then give S L A0,S L B0.

The main pair is separately L-scaled and then transformed by N_R, giving
LR(X+S Y), LR Y. E,F are independent arbitrary inputs, untouched until their
paid R idles. No coordinate is presumed zero or erased. As an additional
structural check, the endpoint determinant is L^4 R^4, matching two rank-two
native bodies and the four rank-one idles.

The reverse oracle's native pullback is correct: a forward map
(d,s)->(D(d+S s),D s) sends output covector coefficients (u,v) backwards to
(u D,(v+u S)D). It must multiply by D rather than its inverse, as implemented.
The ADD/QUERY, sign and swap pullbacks have the corresponding correct source
and target conventions. One unit output row is pulled back for each of the
six outputs, and full six-coordinate polynomial rows are compared, so all
36 arbitrary-input coefficients are covered; this is not sampled testing.
The forward verifier's destination/source update order is consistent with
this convention and its integer literal word matches the displayed proof.

## Exact q^4 normalization

Let alpha=(1+i)/2 and beta=(1-i)/2. Then alpha*beta=1/2,
alpha^2+beta^2=0, and alpha^2-beta^2=i. For
lambda=alpha+beta q^2 and q^4=1, lambda^2=q^2 and
lambda*(beta+alpha q^2)=1. Hence S=lambda q^-1 has S^2=1.

The pinned source uses QUERY(d,s,-1) with -1 as the q exponent, not a
negative scalar coefficient. Its LAMBDA(d,-1), QUERY, LAMBDA(d,+1)
sandwich gives exactly d+S s. The analogous LOCAL sandwich gives
(D(d+S s),D s), since the body commutes with the ordinary lambda factor.
The Gaussian coefficient routine, q-exponent reduction, and substitution
S=alpha q^3+beta q in the forward checker implement these identities with
the correct absolute signs. Applying lambda^-1 only to the two SL outputs
gives q^-1 L; the fresh R outputs need no such phase normalizer.

There are 21 events in the expanded normalized word and 23 after those two
final auxiliary normalizers. The integrated result now states this explicitly.
The integer formal S-word specializes in every characteristic; the displayed
Gaussian half-coefficient normalization is a characteristic-zero complex
normalization, not a characteristic-two implementation claim.

## Precise inherited four-query lower bound

At L=R=1, normalize the endpoint by its S=1 value. The header is
I+(S-1)K with K=E_XY+P_AB, of rank three. The general rank factorization
K=U T V gives at least three rank-one central queries. For exactly three,
#6764's HEADER-SATURATION theorem applies to D=R: the final R projector is
P_R=diag(1,1,0,0,1,1), it commutes with K, and its restriction to the
S-target quotient span(A,B) has rank zero. The retained R-native query is
atomic and supported on its rank-two R body. Positive formal body degree
is saturated at rank four. The theorem would require rank two on that
quotient, a contradiction. Thus the minimum is at least four, and the
literal construction attains it.

The conditions matter: retain the R-coupled native call, S- and D-independent
invertible ordinary controls in the normalized scalar contract, positive
unit-exponent body projectors, and the formal independent body identity.
A generic circuit with no R-native query, body-dependent controls, changed
header/target contract, or only a quotient identity D^4=1 is not excluded by
this argument alone. Fixed q^2-character sectors make lambda an ordinary
constant; the physical/Fourier admission remains separate. These are the
explicit source-relative boundaries, not a universal physical query optimum.

## Local accounting

The native child calls and their inherited internal helper targets are held
fixed by the arbitrary-input supplier interface. The new productive entries
are 2H(a+1)+2H(b), with paid idles 2H(a)+2H(b) and two thin queries.
The fresh R targets therefore cancel their paid R idles only after both are
included. Relative to the old 2H(a+b+1) targets, 2H(a+b) idles and one thin
query, the exact change is

    2[i(a)-i(a+b)]-1.

The new node excess is 2i(a)-2<0 for 0<kappa<1 and a>0. The additional
thin query is fully charged; the ordinary signs, ADDs, wrapper phases and
final normalizers are not a proved complete compiler/tape budget. The proof
correctly leaves that and new field allocation/physical phase admission
outside its local claim.

## Execution corroboration

After inspecting the formulas and code, I ran the independent reverse oracle.
It passed all 36 coefficients and its eight stated rejection controls, with
endpoint SHA256
1ff1d3adaa7e0b9b91b9679036b95422d44be399a70dafa1d68c883665929d82.
This run corroborates the inspection; it is not the sole basis of the review.

## Reviewed file pins

- `reverse_check.py`: `296d72aeb360f351f7842b1ed7a1ae74151d744132afa4d1808f2e1892cc3352`
- Original author proof before integration cross-reference edits: `0a775e1bed40b60cd96846887df7c81e5a9e6a955bcac54ca961b7f3867c9045`
- `construct.py`: `9fb33c8902a2ef8c603c342cc9c32da8d0aad3108df85bf536d77194a6513296`
- `frozen/THREE-QUERY-OBSTRUCTION.md`: `717f3aa49c7124a413021f022ad7ed5b984399e5d1ef61fa1343a2ae0acbb031`
