# CK grid-preserving single-scratch coefficient circuits

Finite complex-supplier construction and scoped optimality certificate; **no
new kappa**. This supplies a CK companion to Philipp / @mightyOil's JP8 search
in [PR882](https://github.com/CrocSwap/integer-mult-bounds/pull/882). It covers
all 103 magnitudes in the historical PR626 CK streams, including numerators
through 512 and denominators through 64, rather than reopening the JP8 domain.

| Complete CK scalar projection | PR696 copy/unit | Best four PR837 Horner choices | This construction |
| --- | ---: | ---: | ---: |
| Forward | 169,618 | 168,488 | 168,308 |
| Backward / inverse-transpose | 169,634 | 168,504 | 168,324 |

The saving is **1,310 real-component primitives per orientation against
PR696**, or **180 net against the complete four-Horner comparator**. At the
individual occurrences that strictly beat every Horner choice the saving is
234; other occurrences cost 54 more than that comparator, giving the stated
net 180. All original magnitude envelopes and coefficient grids are retained.
These are finite instruction counts, not measured runtime improvements.

Run offline with standard-library Python 3.11+:

```sh
python3 -B -I research/ck-grid-synthesis-seed24/verify.py
python3 -B -I research/ck-grid-synthesis-seed24/independent.py
python3 -B -I research/ck-grid-synthesis-seed24/test_package.py
```

Main expected marker:

```text
PASS_CK_GRID_SYNTHESIS magnitudes=103 programs=2 columns=725 savings=1310,1310 no_new_kappa
```

The default verifier writes nothing and compares its complete deterministic
receipt to [EXPECTED.json](EXPECTED.json). `--write-certificate` explicitly
regenerates that receipt after all checks. [CENSUS.json.gz](CENSUS.json.gz)
contains every graph distance and chosen preparation witness; equality is on
decoded JSON, not gzip packaging. [SOURCES.json](SOURCES.json) binds the seven
consumed inputs by payload SHA256 and records their immutable Git blobs.

For `q = +/-a/D`, preparation starts with one paid `COPY W <- S`, stays on
the grid `D^-1 Z` with `|W/S| <= a`, and ends at either signed coefficient
`+/-a/D`. Every source ADD/SUB, DOUBLE, HALF, NEGATE, COPY or CLEAR costs one.
One signed target accumulation and one final CLEAR complete the map
`(T,S,W) -> (T+qS,S,0)`, including arbitrary initial work. The accepted unit
macro costs two and is kept separately. Every primitive uses the original
macro frame; source, helper count, paid children and event boundaries stay
fixed. No additional source access, frame change, copy, restoration or child
is hidden in these counts. Only a strictly shorter complete word replaces
the PR696 word.

The complete finite search comprises 16,251 vertices and 96,929 labelled
edges, with no depth cap, sampled coefficients or unresolved search nodes.
A separately written synchronous Bellman implementation checks every label,
edge inequality and shortest witness. This is independent AI implementation,
not independent human review. The primitive replay checks all 725 formal
input columns in both complete scalar programs: 224 data, 492 arbitrary dirty
helpers, eight dirty private centers and dirty coefficient work. Helpers are
restored and private cells erased. Nine graph controls, six macro controls
and focused whole-word/source/certificate tests check meaningful failures.
The [proof](PROOF.md) states exactly which minimum and prefix claims follow.

Exact base: `ba82555c64e1879e4b7decce28186f208fcb8262`. OS assignment seed
**24**, complex-supplier track. The local [claim](CLAIM.json) records candidate
selection, stopping rule and timing. The old clone reported a truncated pack,
so this sprint used a fresh shallow clone and isolated `codex/complex-seed24`
branch. Orientation exceeded the intended first 20 percent; implementation
then stayed bounded and the final quarter was reserved for verification and
handoff.

At this base the actual selected result is **PR1042**, conditional kappa
`1672188119205421/10^18 = 0.001672188119205421`, with reviewed source head
`7e8ef087c02a77038a28a337a7ee3a77039cac0d`. The selected record, manifest,
assembly, batch1047 review, mutable-leaver/slot construction and T16 owner
package were read. This contribution deliberately concerns historical CK,
not transport to that newly selected word. The paid profile is unchanged,
so no exponent improvement follows.

PR723/734/787 already cover forward signed-digit recoding; PR837 supplies the
four-Horner comparator and PR866 explains the fractional-grid obligation.
PR722/739/769/811 reuse work across macros and are not composed here.
[PR1036](https://github.com/CrocSwap/integer-mult-bounds/pull/1036), by Hanson
Sun / @bbMisk, obtains larger CK savings in a distinct source/target mutation
class. Its two-register exclusion does not settle this single-scratch class;
we claim no stronger unrestricted circuit result. PR999 permits multiple
target accumulations and is also distinct. No pending implementation is a
code dependency, and no savings from these packages are added together.

Credit Sagar Thakrar / @thakrarsagar's PR696 copy/unit lowering (also used in
the verifier adaptation), Gareth Davidson / @bitplane's PR837 comparator,
Philipp / @mightyOil's PR882 graph method and grid proof, Chris Pagolu's PR734,
Hanson Sun's PR1036, and the retained icekylinx / Jeremy Kothe / Chafik
Boukhalfa / DreamingOfClouds / Rohan Arun / eumemic construction lineage.
Prepared for **Eva Ayala / @ToikY with substantial OpenAI Codex assistance**
in selection, implementation, proof, verification and separate AI review.
Apache-2.0; no elementary shift/add synthesis priority is claimed.

Production/native phase admission, complete global invoice and owner replay,
transport to PR1042 and all-size compiler/realization/hosting/precision/tape/
analytic obligations remain separate. Full repository, supplier cold replay,
Lean and hosted CI passes are not claimed. `upstream/`, the production emitter
and selected frontier are unchanged.
