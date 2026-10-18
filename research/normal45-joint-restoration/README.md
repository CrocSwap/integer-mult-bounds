# Independent joint-restoration check of PR2942

Both finite providers pass the complete 632-input free-operator replay,
including all 86 restored dirty helpers, compensation, literal inverse cleanup
and private-zero return in forward and inverse-transpose orientations. A
separate column/covector derivation checks all four paired steps and their
ordered composition. No construction defect was found in this scope.

The exact source is [PR2942](https://github.com/CrocSwap/integer-mult-bounds/pull/2942)
at `a027b0f6fdb0ab2b42ba10fc31b53960166bf2bf`, based on PR2917's 82-endpoint
words. Its four 9-to-8 extractions share terminal overhead and charge four
more private buffers. This audit tests their simultaneous algebraic premise;
it does not independently admit the source's complete cost or kappa claim.
An archival merge is not scientific endorsement.

One exact control passes the **complete forward** clean-buffer replay but
fails inverse-transpose private-zero return: omitting the first cleanup gate
leaves coefficient `-1` from original input2 in private register969. The valid
source contains that gate and passes both. The [proof](PROOF.md) explains the
general block-matrix reason and the precise clean-buffer premise.

## Evidence and limits

| Check | Covered domain |
|---|---|
| Integer/dyadic free-group replay | Both parent/final providers; 632 independent original inputs; both orientations |
| Delivery and cleanup | 82 inherited and 86 final dirty-helper row/column endpoints; 4,992 final cleanup gates; all private zero slots |
| Separate paired-block oracle | Four ordered steps per provider, compensation product and prior endpoint preservation; [independent derivation](INDEPENDENT.md) |
| Failure controls | Stale compensation, terminal order, cleanup omissions, operator inversion and private-zero premise; additional independent composition controls |

No predecessor Python module is imported or executed. The eight data inputs
are bound to their original author Git blobs and SHA256 hashes in
[SOURCES.json](SOURCES.json). Every original input, including dirty helpers and
targets, is arbitrary; the 86 **private** slots must start zero.

This is finite exact symbolic evidence plus written proofs, with separate AI
verification. Native phases, physical frames/owners, storage, precision,
complete recursive/outer invoices and all-size hypotheses remain unverified
here. No new supplier, formal-kernel proof, independent human review or kappa
improvement is claimed. [TASK.json](TASK.json) records the scoped assignment.

## Reproduce

From the repository root, with standard-library Python 3.12:

```sh
python3 scripts/research_package.py --package research/normal45-joint-restoration --check-only
python3.12 scripts/research_package.py --package research/normal45-joint-restoration
python3.12 -I -O -B research/normal45-joint-restoration/verify.py
python3.12 -I -O -B research/normal45-joint-restoration/independent.py
```

Both direct commands emit deterministic JSON and require only this package
plus the eight declared sibling data inputs. They work in a matching Git-free
export. The registered metadata check additionally resolves historical Git
provenance. Neither command writes files.

## Open next questions

Independently review the pinned source's native and complete physical/outer
release pipeline. Those costs decide whether the checked joint algebra yields
its proposed recursive gain. Begin with PR2942's `reproduce.py` at the exact
source commit and retain its inherited all-size hypotheses. This audit does
not reserve or repeat the separate active terminal-gate retiming work.

## Credit

Marius-Paul Dumitrean/PR2942 supplies the four-extraction mechanism and literal
words; Mason Hale/PR2917 the parent; Jeremy Diviney/PR2908 the paired method;
Jeremy Kothe/PR2894/2833 the supplier and cleanup lineage. Retain Yiyang Lu,
Dugongue, Tekalign, icekylinx and the original native/geometry authors' credit.
PR2932's predecessor frame-ledger audit is complementary. New independently
implemented check by Ross Richardson with substantial OpenAI Codex assistance,
including a separate mathematical specialist. Apache-2.0.
