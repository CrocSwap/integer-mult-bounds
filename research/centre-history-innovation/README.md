# Native F2 innovation after the complete earlier centre history

I construct input differences for which **all 80 earlier centre fields vanish**,
across all cover owners, while the eight queries at one F2 owner range over
the full payload space. A decoder that receives only those earlier transcripts
cannot recover the F2 query. I prove this for the selected calls 0..10 under the
repository's retained native common-frame and cover-view hypotheses.

The new scope includes coupled variation of original sources and targets and
the complete ten-call observation history. I use predecessor kernel/route and
native endpoint results; I do not claim their general linear algebra as new.
I leave the selected frontier and eight H8 children per call unchanged.

## Observation contract

Fix an admitted finite-dimensional complex payload space M, with d=dim(M)>0,
including any admitted tensor depth and spectator factors. Let G be the
selected orthogonal cover group. Original port fields at different physical
owners in G vary independently. Use the unchanged selected schedule and local
words. Let H record the eight pre-transport centre fields at each call 0..9,
at every owner, in their native carrier coordinates. Retaining their transported
versions as well adds no information on the witnesses below, since both vanish.
Let Q observe the eight pre-transport fields of call 10 at common owner I.

**Conditional theorem.** Under the native common-frame and full-space local-view
contracts in the pinned sources,

\[
Q(\ker H)=M^8,\qquad \dim Q(\ker H)=8d.
\]

Thus even a nonlinear decoder of H alone fails on this input domain. A decoder
that also receives a linear fresh observation E with complex codomain dimension
m needs m>=8d to recover this one owner's query for arbitrary inputs. The decoder
may mix owners, payload coordinates and earlier calls. It may not obtain other
source-dependent data without including that data in E.

I assert an information bound at one future owner. I infer no rank for the
complete future cover field, recursive-child count, transport tariff or physical
runtime from 8d. You may obtain fresh data, change the queries or seek
a weaker terminal-only obligation; you must specify and price that interface.

## Proof

### 1. Retained native coordinates and exact scalar rows

Write C_a for the translation root with Fourier multiplier
i^parity(a.u), tau_b for translation, and P_g for the coordinate permutation
at cover owner g. I use the native common-frame factorization

\[
\operatorname{diag}(L_{\rm final})(S\otimes I_M)
\operatorname{diag}(L_{\rm initial}^{-1})
\]

from the [whole-payload observation proof](../centre-native-observation-dimension/PROOF.md)
and [selected native lift](../selected-centre-native-lift/README.md). Their authors
check local recipes, conversions and labels. Their global full-space view
contract remains an explicit premise here. I authenticate their text and the
hosting/geometry inputs; I do not rebuild their native compiler or run Lean.

DLamdata uses the following gauges for port normal q in the
[native terminal factorization](../centre-native-terminal-factor/README.md):

\[
X_{-1}=C_q,\quad Y_{-1}=I,\quad
X_s=\prod_{i=0}^{8+8s}C_{e_i},\quad Y_s=X_sC_q^{-1}.
\]

At physical owner g, set G_Xs(g)=P_g X_s P_g^-1 and likewise for Y.
For normalized input(u,v), its complete native endpoints are

\[
F_s:(u,v)\mapsto(u,v+u),\qquad
B_s:(u,v)\mapsto(u-v,v),
\]

with the corresponding entrance/exit gauges. Helpers have diagonal complete
endpoint blocks; they receive no source or target variation. I rederive both
704-row scalar endpoints from the two full 24,767-event programs. I use their
retained native conjugation theorem to interpret the zero blocks.

Let R be the forward eight-by-112 source block. The actual forward cuts have
zero target coefficients. The backward cuts have only target coefficients,
with matrix R/4. I derive both from literal programs and check all 16 cuts by
a separate reverse-adjoint calculation. The established identities are

\[
RR^T=56I_8,\qquad \|R_{\cdot p}\|^2=4.
\]

For J=(0,1,2,3,4,5,6,12), the established minor P=R[:,J] has det(P)=32.
I recheck these finite premises rather than assume a new source matrix.

### 2. A coupled input makes the complete prior history zero

For p in J, define

\[
w^p=56e_p-R^TR e_p.
\]

Then Rw^p=0 and w_p^p=52. I verify these identities for all 112
ports; each vector has 53 nonzero integer entries. For this witness, choose
one arbitrary payload phi_p in M and one old physical owner g_p=rho_2(p).
Initialize differences only in the original X0/Y0 families at g_p:

\[
D_j(g_p)=w_j^p C_{g_pq_j}\phi_p,\qquad
T_j(g_p)=-w_j^p\phi_p.
\]

Set other ordinary and private differences to zero. These are differences
between two executions. Both executions may share arbitrary fixed helper dirt.
The theorem permits targets to vary along with sources.

At F0, all ports use route I. After the common owner identification, the
normalized source and target inputs are w_j^p phi_p and -w_j^p phi_p, up to
the same invertible owner coordinate change. Therefore Rw^p=0 makes all eight
F0 fields zero. The complete endpoint leaves

\[
X_j(g_p)=G_{X0}(g_p)w_j^p\phi_p,\qquad Y_j(g_p)=0.
\]

I locate F0, B1 and F2 at local times 0,4,10 and global event
indices 0,4,18. In the 19-event prefix, I check 11 local sweeps, four idle sweeps
and four bridges. Calls 1..3 and 5..9 use no family 0..111 as data or
helpers. They therefore see zero differences. B1 reads only the zero targets
at its centre cuts, and its complete endpoint leaves the same normalized X
with gauge G_X1. The idle sweeps concern pair 1. Each bridge reads X1 and Y0
in the updates X0+=X1 and Y1-=Y0; both inputs have zero difference. The other
replicas also have zero difference. No intervening operation spreads the live X0.

Consequently all eight centre fields at each of calls 0..9 vanish at every
owner, including the full B1 transcript. Invertible centre transports also
map these zero fields to zero.

### 3. F2 separates the owner routes

The actual stage 2 routes rho_2(j) are 112 distinct orthogonal involutions.
At common owner I, data port j reads physical owner rho_2(j). The witness
at g_p therefore contributes only through j=p, with normalized value 52phi_p.

For arbitrary payloads, the entrance phases matter. Define
E_2=product(i=9..24) C_ei. I use this stage 2 identity from the retained gauge theorem:

\[
\tau_{\rho_2(p)a_{X,p}}\,\rho_2(p)(X_1)=C_{q_p}E_2.
\]

The source adapter removes C_qp. The raw centre field in channel k is

\[
Q_k=52R_{kp}\,T_{415+k}E_2\phi_p.
\]

Here T_415+k denotes the canonical carrier-frame operator, as in the native lift.
The carrier/exterior factor is invertible and independent of p. I check all
four entry/exit identities for 112 ports and stages 0..2 by exact Fourier phase
polynomials modulo 4. For port 0 the routed stage 2 entrance translation is 917515;
the completed-X shift 917508 belongs to a different boundary.

Superpose the eight witnesses at their distinct old owners. Let W:M^8->inputs
denote this embedding. Then HW=0 and

\[
QW=\operatorname{diag}(T_{415},\ldots,T_{422})
       (I_8\otimes E_2)(52P\otimes I_M).
\]

Since det(52P)=52^8*32=1710711313006592, QW is invertible. This proves the
stated image and dimension. Any decoder of H alone gives the same output
on zero and W(phi), although Q distinguishes them. If the decoder also uses
linear E, then EW must be injective: a nonzero vector in its kernel would
give the same H,E observations and a different Q. Hence m>=8d.

For a small constant-payload counterexample, use the credited kernel
e0-e1-e6-e7 at owner rho_2(0), with opposite target values. F2 channel 0
has normalized value 1 while all 80 prior fields remain zero. The eight-vector
construction strengthens that collision to the full one-owner dimension.

## Evidence, limits and reuse

Run from the repository root with Python 3.12 and the standard library:

```sh
python3.12 scripts/research_package.py --package research/centre-history-innovation --check-only
python3.12 scripts/research_package.py --package research/centre-history-innovation
```

I authenticate the selected archive and four exact members, then
check both complete scalar endpoints, 16 reverse-derived cuts, all 112 kernel
vectors, the 19-event chronology, distinct routes and 1,344 native phase
identities. I compare a digest of the complete deterministic JSON result;
`verify.py --emit` prints the matrix, witness vectors and schedule receipt.
Checks use exceptions and remain active with -O. The registered launcher
isolates bytecode caches. No predecessor Python code executes in this package.

I ran the registered replay and metadata check on CPython 3.12.13, macOS arm64.
The three premise mutations failed at their intended checks. I ran no full
selected-supplier replay; this package leaves its word, invoice and frontier
unchanged. The new proof retains the native assumptions listed above.

I test controls that collapse the owner routes, change the original target
coefficient, allow a fresh source-coordinate read, and omit or misroute entrance phases.
I also mutate a helper owner to touch live X0, reverse the bridge's read side,
and corrupt a stage 2 entrance shift. Each mutation triggers its expected rejection.
The forward/backward common-frame theorem and full-space cover admission remain
inherited assumptions. Finite scalar/phase checks do not prove that compiler
contract, a full multiplication theorem or a new exponent.

The proof works over complex vector spaces. Scaling a constant witness yields
a bounded dyadic counterexample, but I supply no unchanged fixed-grid or
fixed-width realization of the arbitrary-payload right inverse. I do not charge
information dimensions as recursive calls. A mutable eight-slot cache with fresh
reads has a different interface; I have not ruled it out.

## Predecessors and overlap

- David Charbonneau (`dcharb78`), [PR3147](https://github.com/CrocSwap/integer-mult-bounds/pull/3147),
  head `5cbc48b18cb05327a8dacab3f626412d3bc5e924`: chronological circle proposal
  and source-only cancellation. I use its question, not its assigned cost profile.
- Nick Petalas, [PR3151](https://github.com/CrocSwap/integer-mult-bounds/pull/3151),
  head `ff21ddd5f801eccabb14fa88b76724a8d55c1e26`: scalar full-input rank 16,
  target-only collision and late-bridge audit. I do not repeat those results.
- Aaron Wang/navinor, [PR2391](https://github.com/CrocSwap/integer-mult-bounds/pull/2391),
  head `5efcbb6058d27aa8b988db8f18c7b678166b2783`: native quarter-query kernel
  witness and owner-route distinction. ywz65, [PR2461](https://github.com/CrocSwap/integer-mult-bounds/pull/2461),
  head `4c674beb8c752c4c2352e4591638807d23215c49`: kernel-vector family and
  locality-dependent information floors. Those contracts fix old target
  differences and observe an earlier pair of calls.
- DLamdata, [native terminal factorization](../centre-native-terminal-factor/README.md),
  source head `f122d255c4cdb0714c079d8e91b76bd7a34da23e`: complete native endpoint
  gauges, phase identities and the 19-event prefix; following ywz65's PR2564
  source-only terminal quotient. I vary original targets and demand the internal
  F2 query, so I do not contradict that fixed-dirt terminal factorization.
- Ali Romman, [native source codes](../native-source-codes/source_data.py):
  the existing RR^T=56I source identity. commdata2338/PR2048, ywz65's whole-payload
  observation proof, Sagar Thakrar/PR2199 and exact-recipe audits, Adam Gall/PR1918,
  DreamingOfClouds, icekylinx, Rohan Arun, Jeremy Kothe and Hao Yan retain credit
  for the common-frame, geometry, selected construction and compiler lineage.

I checked live PR bodies and Discussion text with complete pagination at
16:14–16:15 UTC on October 17, 2026: 309 open PRs and 1,974 Discussion records.
I also checked the named source packages and exact heads. Coverage excludes
unpublished work and arbitrary diffs; I make no novelty claim from a missing hit.
At 16:30 UTC I refreshed main, both pending source heads and Discussion 3149.
I found unchanged sources and no replies to my scoped claim.
I coordinate in [Discussion3149](https://github.com/CrocSwap/integer-mult-bounds/discussions/3149#discussioncomment-19000929).

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance in
research, proofs, code and prose, including source-analysis subagents.
Apache-2.0. I claim no independent human or formal-kernel verification.

## Open next questions

Can a paid fresh-data update produce the missing F2 query within a favorable
complete invoice? Start with explicit physical source reads, frames and return
obligations, and test the eight witnesses. Acquisition, restoration, precision
and hosting costs remain unresolved. Prior-transcript recombination alone
cannot pass this test.

Can a terminal-only consumer avoid reconstructing this internal query? State
the complete varying-source-and-target output map, then evaluate these inputs.
The present theorem does not answer that changed contract. I stop this audit
at the information boundary; [TASK.json](TASK.json) records the expansion decision.
