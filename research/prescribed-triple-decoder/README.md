# Independent targetwise audit of PR #966

**Independent verification; no new kappa.** This package audits the exact
prescribed-triple certificate from [PR #966](https://github.com/CrocSwap/integer-mult-bounds/pull/966)
at `7eaf5665ac246310293fda06a3cf245fe72f6012`. It checks the identity of
every labelled target in the independent comparison, rather than comparing
only cost histograms. It also verifies the certificate's orbit multiplicities
by explicitly applying the matching automorphism group, without importing
the predecessor's first-occurrence canonicalization or verifier.

The result is a positive audit of a concurrent contribution. PR #966
published the same deletion theorem while this sprint was running, with
broader finite coverage than our initial experiment. We therefore changed
the deliverable to this independent certificate audit and credit that work.
The new evidence is a targetwise cross-check, an independent group-action
inventory and literal witness checks, with a histogram-preserving adverse
control. No new deletion theorem is claimed here.

## Reproduce

Python 3.9 or later, standard library only. From the repository root:

```sh
python3 -I research/prescribed-triple-decoder/audit.py
```

Expected final line:

```text
PASS PR966 targetwise audit: 46348 triples; 63 orbits; 59 witnesses; 2244 targetwise minima; 11 controls
```

The audit checks the committed [receipt](AUDIT.json) and all **46,348** labelled
target triples represented by the certificate at `p=2,...,6`, all **63**
matching orbits, and all **59** feasible orbit witnesses. At `p=3,4`, it
compares each of **2,244** labelled target budgets against **11,966**
independently enumerated rank-three cut-code subspaces. Run with `-O`
after `-I` to check optimized-mode failure detection. The replay is offline
and leaves the checkout unchanged. `--write` explicitly regenerates only
this package's deterministic audit receipt.

## What is checked

The port graph is `K_(2p)` with the `p` original matched edges removed.
For every certificate representative, `audit.py` explicitly permutes the
original pairs and flips their signs. The resulting set of labelled target
triples must have exactly the recorded multiplicity. Different orbit sets
must be disjoint and their union must equal all three-edge target sets.
This independently checks the geometric inventory instead of trusting
the predecessor's canonical keys or histogram totals.

For every feasible orbit, the audit checks deletion membership, uniqueness,
count and target exclusion. It evaluates each published decoder vertex set
as a literal symmetric difference of incidence-star supports; after removing
deleted coordinates its support must be exactly the corresponding retained
target singleton. Every retained non-target input stays unrestricted.

`independent_check.py` imports no predecessor or audit implementation. It
enumerates all RREF rank-three subspaces of the full binary cut code at
`p=3,4`, fixing the final vertex coefficient to zero to remove the constant
kernel. It computes an exact minimum for every labelled target triple,
including spaces with five through eight distinct vertex labels. The audit
compares each target individually to the expanded PR #966 certificate.

The published PR #966 replay at this pin compares deletion histograms
between its partition and independent engines. A histogram alone does not
identify which target receives which budget. Our adverse control exchanges
an ordinary and exceptional target's budgets, preserving the histogram,
and requires the targetwise comparison to reject the exchange. This is a
test of the additional comparison's failure detection, not a reported
counterexample to PR #966's theorem or its own primary checks.

At `p=2,5,6`, this audit verifies inventory and attaining witnesses. It does
not independently enumerate every cut subspace there. The unrestricted
optimality claim for those parameters remains with PR #966's written proof
and its own independent checks. This finite audit is not a formal proof of
the general deletion theorem or of integer multiplication.

## Provenance and sprint scope

Base: `007664306fff84fbb1c9a1b4053b69f439764034`. Seed **42**, drawn from OS
randomness at `2026-10-13T14:53:15.619448+00:00`, selected structural decoder
research. The initial three candidates were nonempty-star prescribed
triples, empty-allowed triangle targets, and prescribed targets in the
exceptional `k=4,q=2` cube. Seed modulo three selected the first. The
initial experiment completed all triples at `p=3,4,5`; refreshing overlap
then found concurrent PR #966, published at `15:07:03 UTC`. The one
evidence-driven pivot retained the exact same mathematical object and
added independent verification of that submission.

A local claim records the initial scope and final result. The open issue
search found #650 and #913, neither a sprint coordination issue. PR #669
was the only prescribed-triple submission found before selection. The
experiment has fixed exhaustive stopping domains, not a randomized search.

The exact source pins are in [SOURCES.json](SOURCES.json). The vendored
certificate is byte-identical to its Git blob, checked by SHA-256 on each
run; its retained attribution is in [vendor/NOTICE.md](vendor/NOTICE.md).
Sam Sung's [PR #669](https://github.com/CrocSwap/integer-mult-bounds/pull/669)
at `7d526020fc368ce4157cd436995c2f4fcf683318` supplies the signed-port model
and selectable versus prescribed distinction. PR #966 credits that work,
Joel Pulikkan / GamingPuzzled, icekylinx and eumemic. Their credit is retained.

The observation model is binary nonempty singleton stars at `k=2`, three
retained targets and unrestricted surviving non-target inputs. Empty-star
observations, higher `k`, other target counts and physical suppliers are
outside this audit. Source access, totals, helpers, frames, copies,
restoration, recursive children and assembly remain unpriced.

Current main selects conditional PR #890 at
`kappa=1661957774647029/10^18`. We inspected its source manifest, certificate
and review and checked selected-record integrity. Its unrelated cold
construction was not rerun. No existing file, selected record or `upstream/`
file is changed.

Contributor: Eva Ayala / ToikY, with substantial OpenAI Codex assistance,
including separate bounded workers for mathematical and implementation
checks. No independent human review is claimed. Apache-2.0, under the
repository's [license](../../LICENSE).
