# Exact mixed Q8 tariff with arbitrary restored dirty workspace

For any finite number of roles in the formal `F2[Q8]` register model, a
diagonal target containing `t` copies of `z=-1`, `s_i` copies of `i`, `s_j`
copies of `j`, and any number of restored identity roles needs exactly

    2t + s_i + s_j

paid rank-one calls from the alphabet `{i,j}`. If their positive per-call
prices are `alpha,beta`, its exact minimum bill is

    alpha*s_i + beta*s_j + 2t*min(alpha,beta).

Every initial role is arbitrary dirty data. Free mixing is scalar `GL_r(F2)`;
there are no clean helpers, free address operations, COPY, erasure, or
higher-rank paid calls. The result is a written all-size formal obstruction,
with finite exact corroboration. It is not a native supplier or a new kappa.

## What this adds

Cinna Davis's [PR #2248](https://github.com/CrocSwap/integer-mult-bounds/pull/2248)
proved the three-role minima five for two central targets and one generator,
and six for three central targets. Its explicit handoff asks whether arbitrary
dirty workspace can improve the mixed five-call minimum. This proof answers
no, and settles all multiplicities in the stated target alphabet at once.
The all-register one-central/two-generator value four was already proved by
Cinna Davis in [PR #2047](https://github.com/CrocSwap/integer-mult-bounds/pull/2047);
it is credited, not presented as a new case.

The method is the [support-rank proof](PROOF.md): full group-algebra endpoint
coefficients force both the span of paid image vectors and the span of paid
row vectors to have dimension at least `w=t+s_i+s_j`. A first-order quotient
separately gives `X_i Y_i=P_i` and `X_j Y_j=P_j`. Sylvester's inequality then
forces `2w <= n_i+n_j+s_i+s_j`. Direct coordinate calls attain the bound,
including the weighted formula. The full endpoint is essential: the
first-order quotient alone sends the nontrivial central target to identity.

This closes a specific workspace-only route. It does not rule out other Q8
target profiles, different priced alphabets, or different native mechanisms.
For example, allowing `z` itself as a unit-cost call immediately invalidates
the two-call central tariff. No claim is made for signed noncentral targets,
`k`, inverse-label pricing, or the alphabet in PR #2318.

## Exact checks and reproducibility

Run from the repository root with standard-library Python 3.12:

```sh
python3.12 -I -O -B research/q8-mixed-uniform-tariff/verify.py
python3.12 -I -O -B research/q8-mixed-uniform-tariff/test_verify.py
python3.12 -B scripts/research_package.py --package research/q8-mixed-uniform-tariff
```

`RESULT.json` is the typed canonical receipt. `--out NEW_PATH` regenerates a
receipt without replacing an existing file. The verifier authenticates the
context and retained predecessor texts before computation; its standalone
replay also works in a Git-free export containing those declared inputs.
The generic metadata launcher additionally checks Git provenance.

The exact replay reports `PASS_Q8_MIXED_UNIFORM_TARIFF` and checks:

- All 512 Q8 associativity triples and its first-order quotient map.
- 1,023 attaining fixtures: every target word of width zero through four,
  one restored dirty extra, and each price pair `(1,1),(2,5),(5,2)`.
- 24 further words with identity spurs mixing active and restored dirty
  coordinates, across 4, 6 and 9 roles. These have four extra calls.
- All 39,448 input columns of those 1,047 fixtures twice: eight-coefficient
  formal matrices and an independent faithful binary regular representation
  constructed from integer quaternion multiplication, without primary imports.
- Support and first-order identities for 448 non-diagonal word prefixes, and
  all 270,759 pairs of binary matrices `X,Y` for role counts 1 through 3 and
  inner dimensions zero through 3 in the Sylvester inequality.
- Six semantic controls: one-call central underpricing, loss of the central
  target in the quotient, dirty-helper leakage, deletion of a paid call,
  an expanded-alphabet counterexample, and an inadmissible nilpotent projector.

The tests additionally force the independent replay to reject real word
deletion, wrong label, dirty leakage and a more expensive construction falsely
claimed optimal. Source drift/missing source, incomplete fixtures, typed receipt
changes and overwrite protection are tested. These finite checks corroborate
the written proof; they are not an exhaustive search over arbitrary words or a
machine verification of its universal quantifiers.

The native selected cold replay was not run: no selected source, supplier,
hosting, precision, or transfer contract is changed. Local registered execution
uses CPython 3.12.7 and passed all three failure-control test groups. An
independent agent reviewed the proof and implementation and replayed the
complete verifier under optimized CPython 3.12.14 with no blocking finding.
No predecessor search or complete predecessor certificate
is rerun; the retained README texts bind attribution and the exact handoff.

## Sources and selection

`TASK.json` records the original `bit-new-register-model` card, revision 4,
seed `fa61e23a5706a4c7c23c8182a2176f7e`, successful first baseline command,
and the refined obstruction scope. Main was
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` at selection.
The coordinated live overlap cache covered 768 open PRs at 15:00:19 UTC and
1,232 Discussion records at 15:03:35 UTC on 2026-10-15 with complete pagination.
This covers bodies/comments and local package notes, not every diff or every
closed historical PR. It is not a novelty guarantee. The initially considered
one-central all-register scope was discarded on finding PR #2047.
At the 15:27 UTC pre-submission checkpoint, canonical main and all five
related PR heads (#1573/#2047/#2248/#2303/#2318) were unchanged. A bounded
100-most-recently-updated PR-body check found no new same-scope item; it does
not claim a complete new Discussion refresh.

`SOURCES.json` pins exact SHA-256 and Git blobs for retained context and these
three predecessor texts, which are preserved verbatim under `inputs/`:

| PR | Exact head | Role |
|---|---|---|
| #2248 | `835bd7b1877f56d6d9f4eecd7d1ee32f31593e1e` | Finite 5/6 floors and arbitrary-workspace handoff |
| #2047 | `46bce88fab2baa5392a2b27168babc7b6e2915cb` | Existing one-central all-register result |
| #1573 | `0b8c5a69297c794f2de22c04494c83e41300ae36` | Related all-register rank-nullity method for D8/UT3 |

## Open next questions

- **Native realization:** Can one specified Q8 address action improve a complete
  supplier bill? First implement and price one native eight-address action,
  including restoration and chronological hosting. This matters because the
  formal tariff has no admitted native cost. The missing contract is the blocker.
- **Other target classes:** What sharp bound covers `k` and signed noncentral
  targets? First derive their actual first-order coefficient ranks and a
  matching construction, reconciling PR #1925 and PR #2318 before selecting
  new work. Their overlapping first-order support lies outside this theorem.

## Credit and license

Credit Cinna Davis / `1337isnot1337` for PRs #1925, #2047 and #2248 and their
exact Q8 results and handoff; Aaron Wang for the Q8 central-pair model in
PR #1822; `steph4n-gh` for PR #1573's all-register D8/UT3 rank-nullity method;
and Tuafo's retained `bit-identical-three-targets-dirty` proof for the scalar
image-span restriction. The register-model lineage includes eumemic (PR #288),
Ali Romman (PR #468), Gareth Davidson / bitplane (PR #1333), and woklerx
(PR #1443). Sylvester's inequality is standard; no broader literature-priority
claim is made. Prepared by ywz65 with substantial OpenAI Codex assistance in
derivation, implementation and independent agent review. No independent human
review is claimed. New work and retained repository sources are Apache-2.0.
