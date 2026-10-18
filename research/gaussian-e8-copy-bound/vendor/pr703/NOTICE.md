# Attribution, license and source status

Prepared by **Douglas R. Colkitt (@Mister-Meeseeks)**, with substantial
**OpenAI Codex** assistance in research selection, proof development,
implementation, checking and documentation. No human-only or independent
human review is claimed. New files are under the repository's
[Apache-2.0 license](../../LICENSE).

The ten-line quaternionic E8 model, orthogonality observation, symmetric
cost-ten result, exact asymmetric SAT formulation and open question come
from **Joel Pulikkan / GamingPuzzled's
[PR #620](https://github.com/CrocSwap/integer-mult-bounds/pull/620)**, prepared
with Claude Opus 5.5 assistance. This contribution supplies the weighted
transversal proof and a new standard-library exact implementation. It does
not claim to have discovered that geometry or the cost-ten upper bound.

The pairing-rank accounting is inherited from **DreamingOfClouds'
#446/#595** work as used by #620; the conditional deficit screen uses the
retained [format-limits-corrected](../format-limits-corrected/README.md)
accounting. The Hamilton multiplication law and E8 root coordinates are
standard. The implementation uses no copied predecessor routines.

The main-branch base is 66849e1475c930fd7732b1a0067ffee7e1e95f60.
The maintainer's retained #620 head was
419c7374c3bf5f2eee28f08b1e50c1d57934081c, with a **partial** review.
The current open head inspected for overlap was
e9cf03bbdf7094b5a83f6dbd1d74bfd77a05fb87. Its four relevant extension-ring
source files have the same Git blob IDs as the retained base files.
Its later README adds an E6 correction and unrelated unit/dispatch work;
the Hurwitz asymmetric case remains marked open. All consumed file bytes
and base Git blob IDs are pinned in [SOURCES.json](SOURCES.json).

The predecessor's hurwitz_exact.py docstring says costs below ten are
UNSAT. Its accompanying REPORT.md explicitly says that run **did not
finish**. We treat the case as open in that source and do not cite the
docstring as evidence of solver success. The new proof and exact replay
stand independently of any claimed SAT outcome.

Concurrent work checked for overlap includes Zhao Chi / vectorsss' #631
on star punctures, Sam Sung / the-missionary-company's #669 on asymmetric
hypercube stars, Shike Chen's #634 on coding/Lorentzian families, and
Scott Woolsey Biggart's #682 auditing Artus / artuskg's #647 tensor E8
profile. These contributions concern different objects and are not
dependencies. The selected #626/#543 construction and its full predecessor
lineage retain their existing credit and assumptions.

Before submission, metadata was refreshed through #700. Scott Woolsey
Biggart's newer #697 directly reads sources in the complex #647 supplier;
it does not address the quaternionic ten-line decoder considered here.
