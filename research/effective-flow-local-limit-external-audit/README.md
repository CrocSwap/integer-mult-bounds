# External audit of the effective interval local limit

This source-bound audit finds no gap in **PR6713 LOCAL_LIMIT.md sections3–7**,
conditional on the six stated finite-law hypotheses and the classical
Beurling–Selberg approximation. Separately implemented exact-rational engines
certify those six hypotheses for every alpha in the retained bracket. The
local-limit theorem and effective-flow construction remain alephnan's work.
There is no new exponent, selected-frontier change or full-flow admission.

## Exact reviewed scope

For the nine ranks/counts in [CASES.json](CASES.json), put
`Pr(X=ln r)=P_r*r^alpha/sum_s(P_s*s^alpha)` and center at the **actual**
mean `mu=E[X]`. Both engines certify, throughout

    98981438244597/100000000000000 <= alpha
      <= 98981438244599/100000000000000,

that the masses at0,ln2,ln3 are at least1/4,1/8,1/16, respectively;
`2<=v=E[(X-mu)^2]<=3`; `E|X-mu|^3<=5`; and `|X-mu|<=3` on its support.
They neither locate the tilt nor prove its existence, uniqueness, bracket or
the equation `mu=ln5`. Numerical centering never substitutes that equation.

The written analytic review establishes the following conditional implication.
For a finite real law satisfying these six hypotheses, let S_n sum n independent
copies of X-mu, and let G_n be centered Gaussian with variance nv. For every
integer n>=1296, every real x, every b>=0 and every endpoint convention for an
interval I with endpoints x,x+b, define

    B_n=3/sqrt(n)+sqrt(n)*ln(n)*exp(-sqrt(n)/320),
    A_n=(1+4*B_n)/ln(n),  c_sigma=sqrt(v)*sqrt(2*pi).

Then

    sqrt(n)*|Pr(S_n in I)-Pr(G_n in I)| <= A_n+b*B_n,

and

    |sqrt(n)*Pr(S_n in I)-b*exp(-x^2/(2*n*v))/c_sigma|
      <= A_n+b*B_n+b^2/(4*sqrt(n)).

Empty intervals and the singleton{x} at b=0 are included. The endpoint passage
does not assume that the discrete sum has a density or discard boundary atoms.
The reviewed argument includes smoothing normalization, central frequencies,
the quantitative two-logarithm separation, integration and Gaussian replacement.
The universal n statement comes from written analysis, not a finite convolution.

The external premise is the classical interval majorant/minorant with angular
Fourier support[-T,T] and spatial L1 defect2*pi/T. The normalization is checked
against [Laura Shou, arXiv:2110.15301v3, Theorem4.1, printed page12](https://arxiv.org/pdf/2110.15301v3),
including the forward1/(2*pi) convention visible in equation4.8. Rescaling that
transform changes neither support nor the spatial defect. This audit uses that
classical theorem as a premise; it does not newly prove the approximation.

## Numerical evidence and replay

The primary uses an atanh log expansion and positive Taylor exponential bounds.
The oracle uses4096 decreasing-integral rectangles, termwise outward rounding
at10^-12, power-sandwich exponential bounds and centered-square variance sums.
Their independently sealed first computations give **different valid full
enclosures**, with all six H predicates true. No equality of the unlike full
certificates is asserted. Each retained certificate is checked against its own
complete canonical regeneration, including every numeric range and control.

Four actual-certificate replays cover both engines normally and under optimized
Python. Forty additional rejecting CLI checks exercise corrupted inputs,
manifests and certificates. These supplement the engines' four real changed-law
controls and four parser controls each; they are not finite tests of the all-n
analytic statement or of the complete source flow.

With standard-library Python3.12, the default commands are read-only:

```sh
python3 -I -B primary.py
python3 -I -O -B primary.py
python3 -I -B oracle.py
python3 -I -O -B oracle.py
```

[CERTIFICATE.json](CERTIFICATE.json) and [ORACLE.json](ORACLE.json) are the
separate complete certificates. FILES.json authenticates both programs,
shared metadata and six inert source inputs before arithmetic. `--certificate`
selects an actual certificate to verify; `--emit` explicitly writes one.
Source verifiers, source constructors and peer numerical code are never imported.

## Limits

Source [LOCAL_LIMIT.md](inputs/LOCAL_LIMIT.md) sections8–9, its symbolic huge
onset, kernel transfer, mixed-layer/leaf/complement/boundary accounting and
complete flow theorem remain outside this audit. So do tilt-root validation,
native/physical suppliers, complete invoices, ownership, precision/stock/tape,
compiler/outer applications and all five selected framework assumptions.
No n-fold convolution, enormous winning object or rounded multiplier is run.

## Open next questions

- Can sections8–9's symbolic onset and kernel transfer be independently bound
  to their actual flow caller? This matters because sections3–7 alone do not
  adopt those later claims. Start with the exact endpoint and normalization
  contracts; a separate source review, fresh overlap checkpoint and budget are
  required. This work is unreserved.
- Can the full mixed-layer/leaf/complement/boundary argument and a physical
  implementation satisfy their complete interfaces and bills? Start by listing
  the source caller's exact dependencies and paid/owned/precision obligations.
  Those unreviewed bindings block admission; the present scalar estimates do
  not fund them, and unknown costs are not zero.

## Credit

alephnan PR6713, exact head `cd666f05c4e9006025b634687cc493911c8371c8`,
supplies the effective interval estimate and complete-flow application with
substantial OpenAI Codex assistance. Credit the retained law/flow lineage:
zxv4436/4483; Ryanson Jonathan/pinterbanget4459/4467; DLamdata6118;
Nick Petalas6125/6128; CubeJerry6329; Cinna Davis/1337isnot1337;
Jacob Alan Sussman and the native/precision/analytic predecessors.
Beurling, Selberg and Vaaler retain the classical approximation credit;
Laura Shou supplies the inspected normalized statement.

External audit: ToikY with substantial OpenAI Codex and separate AI proof,
numeric and adversarial roles. Prior source-review exposure is disclosed in
SOURCE-PINS; no blind mathematical review, independent human acceptance or
proof-kernel certification is claimed. New material is Apache-2.0.
