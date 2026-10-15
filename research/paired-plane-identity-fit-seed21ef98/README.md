# Exact scalar identity fit for the selected paired planes

**Finite local construction and favorable screen. No new κ or admitted supplier is claimed.**

## Construction

This package keeps the selected 112 labels and the fixed 56-edge zero-dot matching in
[`paired-plane-port-matching-seed6c563a/CERTIFICATE.json`](../paired-plane-port-matching-seed6c563a/CERTIFICATE.json).
For a matched pair (P=\{i,j\}), the selected labels obey

\[
q_i\cdot q_i=q_j\cdot q_j=1,\qquad q_i\cdot q_j=0.
\]

Let (e_i,e_j\) be the corresponding port-coordinate vectors. Use the rank-two
plane term with source and target columns (D_P=T_P=[e_i\ e_j]) and coefficient
matrix (I_2). Its scalar contribution is

\[
D_P I_2 T_P^T=e_i e_i^T+e_j e_j^T.
\]

The 56 pairs partition all ports, so summing the terms gives the exact scalar fit

\[
K=\sum_P D_P I_2 T_P^T=I_{112}.
\]

Thus every diagonal is one and every cross-entry is zero, including all
11,560 off-diagonal entries whose two plane ports are not orthogonal. This meets
the scalar plane endpoint conditions directly. It replaces PR1825's F2
incompatibility-matrix target; that binary identity remains valid as an F2
identity but is not used as the scalar endpoint here.

For each pair, the B14 support rectangle is the pair against itself. Its
restricted pairing matrix is exactly (B_0[P,P]=I_2), so its support charge is
2. The complete copy invoice is therefore (56\cdot2=112), compared with 126
for the published F2-derived support factors. The verifier computes all
12,544 scalar entries and recomputes each of the 56 restricted ranks.

The local plane correction is retained: with

\[
C_q=((1+i)I+(1-i)X_q)/2,\qquad C_E=C_{q_i}C_{q_j},
\]

the endpoint translation is (C_E^2=X_{q_i+q_j}). Exact Gaussian-dyadic
arithmetic checks this identity on all 512 computational basis states for each
of the 56 planes. By linearity, those checks cover every dirty local state.

## Cost screen and limits

Starting from the pinned selected complex profile
`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`, remove the eight rank-eight
centre terms and add 56 rank-two identity terms. The changed local profile is
`{1:2412, 2:474, 3:432, 4:142, 5:82}`, with mass 5,634 and centre charge 112.
For the two-unpaid-coordinate favorable model (`m=73`, `W=896/9`, nine stages,
idle rank cap 51), the pinned exact ceiling routine gives

\[
a_{\rm hi}=4078546959/10^{12}=0.004078546959,
\qquad a_{\rm hi}/(1+a_{\rm hi})
=4078546959/1004078546959.
\]

The published paired-plane profile has `a_hi=0.003447203501` at centre charge
126 under the same hypothetical law. Both are favorable local relaxations. The
larger ceiling is room in this changed complex-side model, not a new bound on
integer multiplication. The current selected κ remains outside this package's
claim, and the unchanged bit side can still bind.

The invoice includes all 56 local rank-two query terms and the exact support
pairing charge. It does not price native address/frame transitions, hosted
application frequency, full restoration, recursive precision, a bit-side
endpoint, or joint supplier assembly. Those are the open work required before
this can affect a selected result.

## Reproduction

The verifier uses only the Python standard library and authenticates its live
inputs against [`SOURCES.json`](SOURCES.json). It does not import the predecessor
verifier. From the repository root:

```sh
python3 -I -O -B research/paired-plane-identity-fit-seed21ef98/verify.py
python3 scripts/research_package.py --package research/paired-plane-identity-fit-seed21ef98 --check-only
python3.12 scripts/research_package.py --package research/paired-plane-identity-fit-seed21ef98
```

The scientific replay prints `PASS_PAIRED_PLANE_IDENTITY_SCALAR_FIT`, the exact
112-unit invoice, 224 dirty scalar columns, all 28,672 local endpoint basis checks,
the ceiling bracket, and four active negative controls. The generic launcher checks the declared
source pins and package metadata; it is a separate layer from the mathematical
checks.

## Provenance, overlap and attribution

Scientific base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. The package pins the
selected record, task catalogue, selected replay archive, PR1825 matching
certificate, and the ceiling/profile source files. Seed `21ef98da55990762165db57af28256e5`,
track `recursive-interfaces`, task `coverage-law-change`, priority revision 4.

The closest construction is merged PR1825 at head
`d16fb8936795ff101e4d2f63cfdc6a25066ebabf`, which supplies the fixed matching
and its plane endpoint translations. Merged PR1889 at head
`5f05652c7dc7f51555ddb59b716000199a72c0ff` identifies why its F2 coefficient
target does not supply this scalar fit. The live two-edge rematching claim in
[Discussion #1587, comment 18932774](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-18932774)
varies the matching and re-solves the F2 system. This result holds that matching
fixed and changes the scalar coefficient map. The current claim and handoff are
in [Discussion #1587, comment 18933097](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-18933097).
The final full refresh at 20:09–20:11 UTC covered 381 open PRs and 789
discussion/comment records with complete pagination and no warnings. Exact-term
search found no active scalar-identity claim. Search is not a novelty guarantee.

Credit the selected PR1094 lineage for the labels and selected source, and PR1825
for the matching and paired-plane endpoint. Prepared by Cinna Davis with
substantial OpenAI Codex assistance in mathematical scoping, source extraction,
proof derivation, exact verification and writing. No independent human or formal
proof-assistant review is claimed. Apache-2.0.

## Open next questions

Can the 56 identity-fit plane terms and their local corrections be routed through
the selected native complex supplier with every hosting, restoration, precision
and bit-side cost charged? It matters because the scalar endpoint and copy
invoice are necessary local conditions; only a complete native assembly and
compatible bit-side endpoint could improve the selected conditional bound. The
first step is to propagate every matched plane through the actual source and
target routes, count address/frame transitions and application frequency, and
derive a bit-side fit for the same 112 labels. The blocker is that no plane-aware
native child/host schedule, full restoration invoice, recursive precision
argument or matching bit-side decoder is included here.
