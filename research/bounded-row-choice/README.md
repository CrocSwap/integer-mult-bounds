# Exact bounded-current-row choice at the stopped-cover boundary

PR2097 demonstrates why unrestricted current-row-dependent edge choice can
destroy a fixed-edge bad-class average even with identity routing and exact
row restoration. This package supplies an exact finite-choice boundary:
selecting among M fixed linear-minor candidates in GL_m(F_q), m>=2, has maximal
bad fraction

    (q^(m-2)*(1+M*(q-1))-1)/(q^m-1)  for 1<=M<=q+1,
    1                              for M>=q+1.

A projective pencil attains it. The standard hyperplane-union argument is
written for all finite-field orders, dimensions and budgets in `PROOF.md`.
This is the specified linear-minor family, not all selected bad varieties.

For arbitrary M candidate bad sets, the usual union bound gives min(1,M*beta).
Applied conditionally to the SAME inherited selected eligible-prime/edge bound,
at most seven fixed-width current-field bits preserve the numerical 10^-16
per-edge allowance: 2^7*2^19/q<2^-54<10^-16 for q>2^80. Eight bits merely fail
this sufficient worst-q guard; no impossibility or selected failure is claimed.
Every relevant current-field choice must factor through the declared full
transcript. Selector/preparation/routing costs and changed weights remain paid.

No actual selected adaptive compiler or transcript certificate is supplied.
The stock coefficient, selected word, supplier and kappa are unchanged. This
quantifies a changed counting hypothesis explicitly left open by the source;
it does not deduce uniform conditioning from endpoint restoration.

## Reproduction

```
python3 scripts/research_package.py --package research/bounded-row-choice
```

The exact verifier checks 6,806 complete candidate-subset cases, projective
pencil attainment through q=11 and dimension 7, and 23,150 executed selector
inputs. Literal GL2 matrix enumeration independently checks equal first-row
completion counts. A separate generic finite-set census checks the union-bound
step. Eight controls delimit the hypotheses, and the typed complete receipt is
required. Normal checks write nothing; `--write NEW_PATH` refuses overwriting.

PR2097's authentication/selected-fact functions and original GL2 witness are
executed unchanged after authentication. Only their package/root paths are
rebound to this package's exact source manifest. The new union, pencil, matrix
and selector engines do not call its witness implementation. Selected facts
are inherited source bindings, not a new independent full supplier replay.
Git-free optimized replay and live source/snapshot/typed-receipt corruptions
are included. No Lean, native supplier, hosted CI or human review is claimed.

## Open next questions

1. Emit and price an actual selected caller's complete current-field transcript,
   including routes, guards, coefficients and stopping. Prove every candidate
   edge separately satisfies the same conditional-domain and eligible-prime
   bound. The missing compiler/dependency certificate blocks adoption.
2. Characterize intersections of a concrete family of actual higher-rank bad
   minors. A sharper family-specific bound could admit more choices, but the
   exact one-linear-minor formula cannot be presumed for those varieties.

## Credit and scope

Adam Gall's PR2097 supplies the fresh-fiber theorem, source bindings and
unrestricted GL2 kernel-selection counterexample, with the retained
three-stage-cover, eumemic source527, Rohan Arun PR185/387/1094, Jeremy Kothe
PR1087 and PR589 contributor lineage. These are unchanged and credited.
Finite hyperplane-union counting and the probabilistic union bound are standard.
The new resource application, proof organization and independent checks are by
ywz65 with substantial OpenAI Codex assistance; Apache-2.0.

Base: current main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority 4.
Selection seed `299ee5a2ebfe16c1bcb5ef0c7868a470`; the first baseline passed.
The stock-envelope card was changed to its fresh-field counting interface,
because numerical reserve followups were already covered. Exact source pins,
current predecessor heads, overlap coverage and limitations are in TASK.json
and SNAPSHOTS.json. Metadata absence is not a novelty certificate.
