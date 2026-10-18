# Masked root-star assembly has exact copy cost 64

**Scoped theorem; no new kappa or physical supplier.** The nine cheap atoms
left open by [PR1226](https://github.com/CrocSwap/integer-mult-bounds/pull/1226)
cannot be assembled into a masked P112 decoder. Its lower bound `784/13`
improves to **64**, attained by the existing coordinate decoder. The result
covers arbitrary finite term counts and arbitrary real or complex
coefficients when both actual supports of each paid term equal an
untrimmed root star `C(alpha)` or its self-trimmed version `N(alpha)`.
Arbitrary cost-zero correction terms are allowed.

The missing constraint is simultaneous frame coverage. Each live
orthogonal eight-frame needs eight rank-one contributions. Nine cost-seven
terms would have to miss pairwise disjoint collections of frames. Choosing
one live normal from each then gives nine pairwise nonorthogonal E8 lines,
which is impossible by a short integer-parity argument. Eight paid terms
cannot use a cost-seven atom at all; ten already cost at least 70.

[PROOF.md](PROOF.md) gives the full argument, including an explicit split
by term count and the sharp coordinate construction. This does not rely on
pending eight-term rigidity results, assume root-linear coefficients, or
search a bounded coefficient alphabet. It closes PR1226's stated support
family, rather than extending the conclusion to general masked decoders.

## Reproduce and inspect

Python 3.10 or newer, standard library only, from the repository root:

```sh
python3 -I -B research/masked-root-star-assembly/verify.py
python3 -I -B research/masked-root-star-assembly/independent.py
python3 -I -B research/masked-root-star-assembly/test_package.py
```

The primary checker rebuilds all 57,600 ordered support-pair ranks,
the 1,260 live frames, every live orthogonal-pair extension, and the
complete nonorthogonality clique census. It checks the exact cost-seven
classification and missed frames, then the full coordinate decoder.
Its deterministic receipt is [CERTIFICATE.json](CERTIFICATE.json).

The separate checker imports neither the primary checker nor a predecessor.
It uses a different root order, dense F2 elimination, set-based frame
enumeration and an explicit eight-dimensional quadratic space over F2
to rule out nine odd roots without the primary clique census. Its receipt
is [INDEPENDENT.json](INDEPENDENT.json). Both commands reject changed
receipts and work with `-O`; the controls test failed mathematical premises,
including why pairwise symplectic products without the quadratic condition
would be insufficient. [VALIDATION.md](VALIDATION.md) records the actual
runs and limitations.

The package opts into the repository's bounded replay hook:

```sh
python3 scripts/research_package.py --package research/masked-root-star-assembly --check-only
python3.12 scripts/research_package.py --package research/masked-root-star-assembly
```

The mathematical checkers need only this directory and no network.
The metadata command additionally resolves historical provenance using Git.
The pinned selected record is orientation, not a mutable mathematical input.

## Scope and relationship to other work

The exact support condition matters: further trims, arbitrary subsets,
unions of stars, other punctures and general non-star supports remain
outside the theorem. No new physical word, owner map, hosted invoice,
or supplier cold replay is supplied. All-size/compiler, realization,
hosting, precision/tape, analytic and bit-interface obligations are
unchanged. A finite certificate and this written scoped proof are not
formal verification of the complete multiplication theorem.

The base is current main `49b3157d1d89adcef16df8be98445451672be5ba`, whose
reviewed conditional saving is `0.001672660197076918`. The task selector
chose `complex-masked-decoder`; [TASK.json](TASK.json) records the refinement,
nonce, bounded stopping rule and coordination limitation. Source commits,
Git blobs and hashes are in [SOURCES.json](SOURCES.json).

PR1226 is the immediate predecessor: it defines the support family,
computes the correct averaged bound and identifies this assembly gap.
We recompute its finite premises and add the joint-miss obstruction.
PR1212 and PR1213 concern eight-term masked rigidity; PR1191 assumes
one factor is root-linear; PR1180 and PR1224 concern all-pairs
overcomplete identities. None of these pending results is a proof
dependency. See [OVERLAP.json](OVERLAP.json) for the checked heads and
coverage limitations.

## Open next questions

Can deeper trims or non-star supports achieve a masked P112 decoder
below 64? They can escape the live-normal witness used here. A feasible
first step is to exhibit one such support pair, compute its exact pairing
rank and missed-frame set, and test joint frame-rank feasibility before
coefficient synthesis. The remaining blockers are exact decoder
coefficients and a complete bill for centre reads, frame travel and dirty
restoration. The structured version is in [TASK.json](TASK.json).

## Credit

Aaron Wang / Navinor (PR1226) supplies the immediate support family,
census and assembly question. DreamingOfClouds (PR717/595) supplies the
masked decoder and label-cost model. Joel Pulikkan / GamingPuzzled
(PR620) and the retained lineage supply the coordinate construction.
themilkman216 (PR968) and woklerx (PR1077) supply the eight-term
all-pairs context. The independently recomputed finite facts and
known sharp example retain their attribution.

Prepared for David Arias (@DavidAriasC), with substantial OpenAI Codex
assistance in research, mathematics, both implementations, testing,
review and writing. Separate AI implementations and review are not
independent human review. New material is Apache-2.0; no predecessor
source files are copied or modified.
