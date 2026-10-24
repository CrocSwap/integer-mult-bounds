# Overlap: packed RAM corollary, original source and classical simulation

## What the original manuscript states

The retained OpenAI manuscript is pinned at openai/math commit adc7f1241b42e322a6451854ab7e4b4c146bf78a. Its introduction states the multiplication result on a single fixed finite-alphabet, fixed-tape-count TM, with the exact fixed-width MSB-first product. Its history section distinguishes storage-modification machines and Groff's RAM result with excluded preprocessing; its exact-DFT discussion uses unbounded exact complex scalars and explicitly separates bit complexity. No packed bounded-word multiplication corollary appears in those inspected passages.

The current upstream path history returned only its initial commit. Four inspected source files match the pinned upstream manifest exactly. Their hashes and public original URLs are in OVERLAP-SOURCES.json.

Relevant originals:
- Introduction, lines 13–29: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026/build/sections/00-introduction.tex
- History, lines 28–34 and 141–164: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026/build/sections/01-history.tex
- Fixed-tape model, Section 2: https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026/build/sections/02-streams.tex

## The classical simulation precedent

Hopcroft, Paul and Valiant's *On Time versus Space and Related Problems* (FOCS 1975), Section 4, Theorem 5, gives a logarithmic RAM simulation speedup using precomputed bounded TM blocks. It explicitly assumes t(n)>=n log n and explains that its RAM needs n operations to examine the input. Corollary 3 applies this to multiplication, obtaining O(n log log n) from the then-available TM algorithm, while keeping numbers O(log n) bits long.

Primary source: https://www-wjp.cs.uni-saarland.de/publikationen/HPV75.pdf , printed page 63 (PDF page 7). SHA-256: 4700da81799d5e8794d37c2fdcc43eb06c3ec252ed9b878ce56805df5f88e57c.

Therefore the generic Four-Russians TM simulation is classical. The original theorem's stated t>=n log n hypothesis cannot simply be ignored when applying it to t=n(log n)^(1-kappa). A complete present proof must supply its packed-I/O variant, charge its preprocessing and establish bounded words and addresses.

## What is different in the present application

The proposed constructive variant uses Theta(log n)-step local windows and pays uniform sublinear table generation. With packed binary input/output and explicit codecs, its cost is
$$
O\left(\frac{T(n)+n}{\log(n+2)}
+n^\epsilon\operatorname{polylog}(n)\right)
$$
for a chosen fixed epsilon<1. At a fixed 0<kappa<1, substitution of the *complete conditional* TM theorem gives
$$
O\left(\frac{n}{(\log(n+2))^\kappa}\right).
$$

This is an explicit conditional consequence of the existing TM claim plus a classical simulation technique. It is not a new TM kappa, not evidence that the original finite/analytic premises hold unconditionally, and not a claim that generic logarithmic batching was invented here. The original TM theorem already implicitly supplies this direction once the correct packed-I/O transfer is proved. The useful artifact is the complete model/ABI/paid-setup specialization and executable bounded-window implementation.

For ordinary packed binary rather than already alphabet-coded fields, include bit-spreading and compression. Two small codec tables suffice: map a raw r-bit chunk to its r fixed-width symbol codes, and map r valid symbol codes to raw bits. Enumerate all table keys and generate each result with O(r) elementary bit operations during paid setup. The raw-key table has 2^r entries and the coded-key table 2^(c*r), both dominated by the local transition table's 2^(s+k*c*(2r+1)) entries. Each runtime physical block contains only a constant number of such chunks. Thus the codec does not reintroduce O(n) bitwise I/O.

## Repository overlap checked

The current open listing through #4539 was read. The GitHub title/body search RAM returned 19 PRs; word-RAM returned #4538, #956 and #514; log-RAM returned none. Tabulation and Hopcroft searches found unrelated census/matching work. Search results and their exact coverage are recorded in OVERLAP-SOURCES.json.

Actual selected predecessors were inspected:
- #4538 is the preceding finite compiler/packed-access/native-kernel package. It asserts constant-overhead correctness transfer, explicitly claims no new complexity record, and leaves the packed whole backend as future work.
- #956's actual proof uses exact scalar/index RAM, with unrestricted scalar heights. It is not a bounded-word integer-multiplication consequence.
- #647's actual provider proof similarly uses exact complex cells; retain its separately credited companion cyclic-DFT result, which is a different model and task.
- #514's body records research drawing on Word RAM/TM machinery but explicitly says those machine-derived alternatives did not produce its numerical improvement.

This is bounded source inspection and PR title/body search, not an exhaustive search of all historical code/comments or the mathematical literature. No absence-of-overlap or worldwide priority claim follows.

Credit the entire pinned multiplication antecedent and its authors, Hopcroft–Paul–Valiant and the Four-Russians method, the existing Problem 1.8 RAM/IMP implementation, and #4538's concrete finite-machine and packing work. The declared best conditional TM parameter remains #4535's 0.003020165 until an actual new native profile is supplied and verified.
