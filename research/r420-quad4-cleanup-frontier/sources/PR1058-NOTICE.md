# Attribution and assistance

New work prepared for **Chris Barber (@cbarber1)** with substantial
**OpenAI Codex assistance** in circuit factoring, proof analysis, code,
verification, documentation and packaging. The separate search implementations
are AI-written computational cross-checks; no independent human peer review is
claimed. Licensed under the repository's Apache-2.0 license.

The construction, E8 word, selected bound and inherited interfaces belong to
their predecessors. In particular:

- **eumemic**, PR543 (`2065fe4f72a914d907f1046603f5a36f17018535`), supplies
  the R420 word, phase-A quad architecture, native verifier and H1–H5 argument;
  the contribution discloses substantial Anthropic Claude assistance. PR493
  supplies the carrier skeleton and six-register quad realization lineage.
- **Dylan Crow / utcorvusvolat-dotcom**, PR370, supplies the bitE8 format,
  record exporter and independent-checker lineage, with disclosed Anthropic
  Claude assistance. The exporter is used unchanged.
- **Zhihao Chen / jacklightChen**, PR425, supplies the interleaved scalar
  interface lineage; **icekylinx** supplies the mutable-source carryover
  argument. These remain inherited conditional interfaces.
- **DreamingOfClouds**, PR503/510, supplies the dead-register totals and
  nine-stage pricing work; **DaysSky**, **chafreaky**, **Zhihao Chen** and the
  authors credited in the pinned predecessor notices supply hosting,
  accounting, prefix and cohort work. **Jacob Sussman** introduced the E8 unit.
- The selected #626/#543 context retains **Chafik Boukhalfa**, **Jeremy Kothe**,
  **eumemic**, and all cumulative credits in `CONTRIBUTORS.md` and the pinned
  maintainer review.

Related concurrent work was checked for overlap and is not a code dependency:
PR670 by yongjae321 (phase-B block 3), PR674 by x0hu (phase-B block 5), PR661 by
yuj1r0 (fixed-order phase-B frame minimum), and PR686 by Mikhail R. Gadelha
(frame-zero sharing), each with its disclosed assistance. Their results are
neither reattributed here nor asserted to compose with this replacement.

PR691 by **@mtpsl** independently preserves the integer map and improves the
reverse envelope of R420 phase-A quad 13. PR823 by **Hao Yan / @FanPUYen**
resynthesizes historical R480 quad 1. Both appeared during this work and are
credited as related independent contributions; neither implementation was
imported, and neither claims the exhaustive monotone minimum supplied here.

The later publication refresh credits **Ross Richardson**, PR925, **@woklerx**,
PR1002/986, and **Hanson Sun / @bbMisk**, PR1027, for related exact positive-transfer
minima and guarded boundaries. PR925/1002/1027 use the same inverse-subtraction
DAG and independent BFS approach. This package claims a different target and
witness, not a new search technique; no code from those packages is imported.
**Yuzhou Wang / @yzhouwang**, PR789, supplies a related restricted phase-B
schedule minimum. **Gareth Davidson / @bitplane**, PR904/952, and **Ross
Richardson**, PR936, supply broader resynthesis of the later R439 word.
Their savings and native verification are not claimed as part of this package.

All predecessor source files and notices remain unchanged. `SOURCES.json`
records the exact files consumed or cited by this package.
