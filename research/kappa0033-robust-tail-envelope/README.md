# Conditional integer-profile envelope for the 8/9 moment tails

One strict mixed budget implies `alpha<1−rho` and `gamma,delta<.97` for every
honest integer profile `P=P0+A`, `T=T0−L` in [MODEL.json](MODEL.json), at
`C=330007/100000000`, `rho=10^−9`, `c=8,b=9,u=1/5,v=1024`. Consequently
`alpha^1024+2gamma^1024+2delta^1024<1`. The quantified argument is in
[PROOF.md](PROOF.md); the executable checks exact finite certificates and domain
countercontrols, rather than enumerating all future A,L.

All 240 H25 targets remain **hypothetical**. The theorem assumes

```
A_t+(1−rho)L_t < R0 <43,
R0=(1−rho)(T0)_t−(P0)_t,  t=1−C.
```

A has finite nonnegative integer multiplicities at positive integer ranks;
L is a subhistogram of T0. There are no new targets, paid deletions or signed
netting. Every addition and loss must enter the one mixed account. Separate
loose bounds `A_t<43`, `L_t<44` cannot replace that inequality. Eight later H1
jobs spend8 from the same allowance; they do not create another43 allowance.

## Result and exact certificates

The fixed P0/T0 are public PR5418's explicit model. Its R0<43 result motivates
the conditional upper premise; this package neither recomputes a price nor proves
that any future physical ledger fits that budget. No Powers, pricing, native,
receiver or physical-word implementation is included or executed.

The proof uses finite binomial certificates and coarse bounds:

| Bound | Exact rational certificate |
|---|---|
| Baseline target moment | `(T0)_t>1024320/65` |
| Baseline paid higher numerator | `(P0)_(t+u)/8^u<301423/20` |
| Additional paid numerator | `A_(t+u)/8^u<129` |
| Remaining target denominator | `T_t>1021460/65` |
| Gamma | `<19760195/20429200<97/100`, cross-product margin5612900 |
| Delta | `<828360/1021460<97/100`, cross-product margin16245620 |

Integer multiplicity supplies `r<1849<8·3^5` for every added rank. This is a
scalar tail estimate, **not an ambient or geometry certificate**. The proof also
checks `(100/97)^32>2` and the exact reserve gap
`1/(1+1024rho)+4/2^32<1`. It evaluates no fractional powers or transcendental
functions and performs no compiler search.

Meaningful countercontrols reject fractional additions, negative/netted counts,
losses beyond T0, new targets, paid deletions, dropping the mixed hypothesis,
ambient overclaims, earned-target overclaims and changed parameters. The valid
integer ledger A=42H1,L=H4 illustrates why the two separate loose quotas do not
suffice: its mixed consumption is greater than43. It is a logical countercontrol,
not a claimed viable physical ledger.

## Source and reproduction

Canonical package base is `1a3ced60b2f7a46bc70280a04f2eeb8ca027c700`, whose
selected κ is `.003027288235` under the same five assumptions. This package
changes no selected record or source algorithm.

The public profile model is retained exactly from [PR5418](https://github.com/CrocSwap/integer-mult-bounds/pull/5418),
commit `fe4c345778554ec5c02368b1ddf2f6918eeb0df5`, with a portable raw
commit/tree/blob proof. That public side commit is not represented as canonical
ancestry. All needed bytes are package-local; Git-free replay does not need its
Git object or complete history. Canonical provenance has separate origin proofs.
The local peer lemma and root audit are credit references by SHA256 only in
[LOCAL-CREDIT-REFERENCES.json](LOCAL-CREDIT-REFERENCES.json), with no private body.

The wrapper authenticates [INTEGRITY.json](INTEGRITY.json), raw Git origins and
public-model equality, checks byte/origin mutations, then runs only the small
integer verifier. All acceptance predicates are explicit in normal and optimized
Python. A private bytecode-cache namespace, preserved fresh raw receipts and
complete pre/post hashes close the source-custody boundary. The frozen request
and final handoff record actual execution separately from expected mathematics.

```sh
python3 -B scripts/research_package.py --package research/kappa0033-robust-tail-envelope
python3 -B scripts/check_research_commit.py --package research/kappa0033-robust-tail-envelope --check-source-history
```

Git-free direct command is `/usr/bin/python3 -I -B research/kappa0033-robust-tail-envelope/verify.py`;
add `-O` for optimized mode. `--integrity-only` authenticates without running the
integer verifier. No third-party dependencies are needed. Actual normal/O,
readonly/empty-PATH, export and declared-source-history outcomes are recorded in
the final operational handoff; no unexecuted command is presented as a pass.
Source custody uses named public Git objects, not a claim that the full canonical
corpus or history was materialized locally.

## Open next questions and limits

A future caller must earn the retained independent canonical targets and bind
its actual complete gross A,L ledger to the single strict budget. Source
endpoints, arbitrary owned/restoration columns, ambient geometry, adapters,
ordinary movement/instruction costs, norm/error envelopes, semantic constants,
stock, fixed tapes, chronological splitting/completion and full compiler/outer
application remain separate. Unknown work remains unknown. The rank estimate
alone certifies none of those joins.

[TASK.json](TASK.json) records structured questions, relevance, first steps and
blockers. This lemma does not establish a physical supplier, funded κ, complete
compiler/outer theorem, unconditional multiplication, human approval or formal
kernel proof. The goal of an achieved conditional κ>=.0033 remains open.

## Credit

Peer precision owns the robust-tail extension; root supplied the elementary
baseline derivation and independent written audit. Public PR5418 supplies the
explicit profile model. Retain the construction/resource owners, Dillon,
Ali Romman, Cao Yifan/native/Clifford, Cinna Davis, zxv, Jacob Alan Sussman,
Dugongue, Chris R / Clear1nsight and all native/helper/compiler/precision/analytic
and recovery notices. New exact finite certificates, source custody and publication
packaging by **Chris R / Clear1nsight, with substantial OpenAI Codex assistance**;
Apache-2.0. No construction priority or independent human approval is claimed.
