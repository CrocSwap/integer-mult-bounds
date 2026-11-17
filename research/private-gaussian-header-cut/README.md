# Gaussian private routing retains the nonlinear copy floor

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration. No new kappa.

A localized header can remain private while preserving the Gaussian nonlinear
copy floor, provided its adaptive payloads stay inside its reader set and their
encoders can compute the header from their declared original inputs. This
answers a restricted private-reader part of ywz65's
[PR2641](https://github.com/CrocSwap/integer-mult-bounds/pull/2641) open question.
The new result is the private schedule simulation and joint source/reader cut.
The predecessor's geometry and public-header theorem are cited, not audited.

For M=h(X_A), delivered only to R, let c=c(R,A) be its pairing price,
L its expected prefix-code length and eta the retained weighted-clique
incidence meeting both A and R. With total independent uniform demand B,

```text
E[total charge] >= (2/3)B + cL - eta H(M)
               >= (2/3)B + (c-eta)L
               >= (2/3)B.
```

Equal b-bit demands retain expected and worst-case charge at least 40b.
[PROOF.md](PROOF.md) gives the full contract and proof. Every header-dependent
payload has readers inside R and declared sources containing A. Its encoder
computes the header locally. Outside R, both payload schedule and encoding
remain independent of the header. All additional routing, timing and absence
signals are excluded. Payloads may be nonlinear and prefix-coded, and their
number, order and supports may change within the private reader region.

The cited Gaussian support inequality gives eta<=c. The source certificate
already supplies a rank-one pair with eta=c=1. A parity header on its six
source bits attains the joint conditional-entropy term. Thus this argument
establishes no positive private-header surcharge. It does not produce an
attaining complete 40b code or rule out a stronger lower bound.

## Evidence and reproduction

From the repository root, CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/private-gaussian-header-cut/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/private-gaussian-header-cut/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/private-gaussian-header-cut
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/private-gaussian-header-cut --check-source-history
```

Another CPython 3.12 executable may replace the displayed local path. Direct
replay prints `PASS_PRIVATE_GAUSSIAN_HEADER_CUT` in a generated JSON receipt
bound to all six package files by SHA256. It writes nothing into the checkout.
The registered runner additionally prints `PASS_REGISTERED_RESEARCH_PACKAGE`.

The new finite checks cover:

- All 316 choices of nonempty declared source support and Boolean header table
  on three bits, crossed with all seven nonempty private-reader sets. The
  2,212 resulting protocols pass 53,088 literal receiver checks and 15,484
  exact cut inequalities, comprising 11,332 joint cuts and 4,152 other cuts.
  Receivers have no side information in this generic finite model. The check
  uses integer products of conditional fiber sizes, with no floating entropy.
- Three private protocols on six active Gaussian source ports. Their headers
  are parity, a nonlinear Boolean function and a ternary prefix code. Only
  two active recipients see the header. All 64 inputs per protocol pass
  384 receiver checks and 63 cut checks. Their exact charges are 7, 7 and
  29/4. The Gaussian support-pair price is a cited premise; this is not a
  geometry census or an optimality claim for these codes.
- Seven rejected mutations: three invalid prefix codes, an adaptive payload
  escaping R, an encoder lacking A, a branch-dependent fixed schedule and
  an actual missing-demand payload. A separate two-input witness shows an
  outsider learning one bit from the presence of an empty message despite
  zero payload bits. It explains the visibility boundary.

These finite protocols corroborate the new simulation lemma. The quantified
statement rests on the written proof and retained geometric premises.
No predecessor executable, scientific replay or flat-pair census runs.

## Scope and credit

Base canonical main is `e54523517d0f03e58352e647c403a5af3e525a57`, priority
revision 8, selected #7000 unchanged. The `complex-new-helper-inventory` card
is explicitly changed to this observation-interface side obstruction. Its
binding-only selected baseline passed. [Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19592129).
[SOURCES.json](SOURCES.json) records immutable provenance. None is a live
scientific input to the standalone verifier.

Credit ywz65 #2641 for the public-header proof and localized/private-header
question; Sagar Thakrar #738 for the Gaussian geometry, weighted support
inequality and rank-one pair; ToikY #888, Alexander Templeton #785, Michael
Fischler #814 and Jerry Chen #912 for the transcript and paid-header lineage.
Joel Pulikkan, Douglas Colkitt and DreamingOfClouds retain their prior credit.
Nick Petalas #4897 concerns public readers and a strict localized-source
surcharge. Its theorem and construction are background, not steps in this
private-schedule proof. Entropy and prefix coding are classical. Global
literature priority is unclaimed.

The result excludes arbitrary private encoder knowledge, schedule leakage,
interactive relays, correlated demands and changed physical bit prices.
No strict surcharge, complete Gaussian communication optimum, physical
supplier, helper restoration, native/tape/precision/stock bill or selected
multiplication theorem is supplied. No selected cold replay, Lean or Docker
run is claimed. All five selected framework assumptions remain. Independent
human and formal proof-kernel review are unclaimed.

The family decision is narrow and finish. A new observer interface is now
bounded, but no new construction campaign follows from a favorable local code.

## Open next questions

1. Can the sufficient A-subset-S encoder condition be replaced by an explicit
   factorization h(X_A)=g(X_S)? First specify each branch's actual knowledge
   and routing. This could reduce declared source prices, but the full
   simulation contract remains to be proved.
2. Can private routing attain 40b, or must a stronger argument impose a
   surcharge? First produce a complete code on the cited F,G pair. The parity
   witness here attains only the entropy comparison, not a full copy optimum.

## Engineering constraints

The verifier has no scientific imports, recursion, subprocesses, network or
external runtime inputs. Loops range over the fixed corpus, at most six
bits, 64 assignments, 63 cuts and three payload targets in the exhaustive
corpus. Functions stay below 60 physical lines. Explicit checks remain active
under optimized Python. Warning-strict execution and in-memory compilation
are the applicable diagnostics; no external static analyzer is claimed.

Power of Ten rule 3 requires a managed-runtime deviation: Python allocates
integers, tuples, counters and JSON while running. Live scientific collections
are bounded by the fixed six-bit domain, and exact entropy products have at
most 64 fiber factors of size at most 64. There is no growing cache or shared
mutable resource. If a future public API enlarges this domain, it must retain
explicit input, collection and arithmetic-size limits. Files are read only
for the generated source-hash receipt, with a per-file size cap.
