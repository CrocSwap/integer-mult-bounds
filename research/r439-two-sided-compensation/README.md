# Two-sided compensation for the selected R439 word

**Finite bit-circuit construction.** Adding 192 disjoint helper pairs around
the frozen target basis from [PR915](https://github.com/CrocSwap/integer-mult-bounds/pull/915)
saves **1,228 further native ADDs**, including both preparation and restoration.
The complete word costs **11,980 ADDs**, compared with 13,208 in PR915 and
24,305 in the selected PR589 word. The saving against PR589 is 12,325 ADDs.

| Quantity | Selected PR589 | Frozen PR915 | This composition |
|---|---:|---:|---:|
| D ADDs | 18,085 | 6,988 | 5,760 |
| Complete native ADDs | 24,305 | 13,208 | 11,980 |
| Exported records | 27,234 | 16,137 | 14,909 |
| Forward positive prefix F | 49,347 | 49,347 | 71,907 |
| Reverse positive prefix B | 1,113,070 | 9,534,616 | 10,562,318 |
| Local payload bound, bits | 93 | 100 | 102 |
| Nine-stage prefix bound, bits | 177 | 189 | 192 |
| Helpers / copied totals / rank mass | 439 / 9 / 5,129 | same | same |

The complete D bill is **192 + 306 + 4,764 + 306 + 192 = 5,760**. Every
non-D field is identical to PR589. The native checks compare each register's
ordered MOVE path and all COPY/ERASE records; every paid resource is retained.
Helpers are temporarily changed during D and restored before A. The full D
boundary remains `(x, y, s) -> (x, y + K s, s)` for arbitrary targets and dirt.

The original syntactic H2 and literal extraction of K remain **false**, as in
PR915. The old checker is unchanged. Integration requires acceptance of the
semantic D-boundary substitution and a complete updated hosted reconstruction
and invoice. All other H1/H3/H4/H5 predicates and decomposed conclusions pass.
This package does not change the selected frontier or claim a new exponent.

## Reproduce

Python 3.12 or later, C++17, and Boost headers are required. From the repository
root, run:

```sh
python3 -I -B research/r439-two-sided-compensation/verify.py
python3 -I -B research/r439-two-sided-compensation/test_package.py
```

Set `BOOST_INCLUDE` to a nonstandard Boost include directory, and `CXX` to
the compiler if needed. The first command rebuilds the search certificate,
compares the entire canonical JSON word, performs independent mathematical
checks, compiles the unchanged native checkers, and compares every receipt
field with [EXPECTED.json](EXPECTED.json). Its final line is:

```text
PASS_R439_TWO_SIDED_COMPENSATION: ADDs 24,305 -> 13,208 -> 11,980; 192 helper pairs; nine-stage prefix 192 bits; semantic D; no new kappa
```

Optional `--output NEW_DIRECTORY` retains all generated words, native records,
commands and logs. `--receipt NEW_FILE` saves the complete report. Existing
destinations are refused. `--source-root ROOT` accepts the minimal source
closure enumerated by [SOURCES.json](SOURCES.json). Normal and optimized
Python are supported: owning Python subprocesses run without optimization so
their existing assertions remain enabled. Regenerated gzip containers are
compared by canonical payload, not compression bytes.

## Construction and distinct contribution

Let K be the original 111 by 439 matrix, E the frozen product of PR915's 306
target transvections, and H the new product of disjoint helper transvections.
The new middle is **E K H inverse**. The complete prefix applies H to helpers,
E to targets, the middle injections, E inverse to targets, and H inverse to
helpers. The helper pairs are disjoint, so H inverse equals H. E is generally
not an involution; its operations are restored in reverse order.

This applies the two-sided method from **Scott Woolsey Biggart's
[PR733](https://github.com/CrocSwap/integer-mult-bounds/pull/733)** to the selected
R439 matrix with a fixed, overlapping target basis. It scores the actual
transformed matrix and checks the complete 192-bit nine-stage prefix ceiling
after each admitted pair. No PR733 executable or saving is imported. Its
verbatim [README](vendor/pr733/README.md) preserves the prior proof and credit.
The mixed term contains 7,031 nonzero coefficients; omitting it fails the D
operator. [PROOF.md](PROOF.md) gives the algebra and complete cost argument.

The seed-5 assignment and the three considered tasks are in
[CLAIM.json](CLAIM.json). The completed search scores all **192,282 ordered
helper pairs** once on the frozen matrix. A seed-5 64-bit tie key is drawn for
every pair, including nonpositive ones. Of 2,298 positive pairs, the sorted
greedy pass accepts 192 and skips 2,106 for overlap; no bound rejects occur.
The maximum individual gain is 19 ADDs. Search stops at the end of that pass.
It makes no claim about optimal matchings, target-basis reselection, neutral
detours, or globally optimal circuits.

## Evidence and precision cost

The independent verifier uses set-valued supports instead of the builder's
packed columns. It recomputes every pair score and literally executes both
positive orientations of all 192 partial words: 4,760,850 ADD/COPY/ERASE
instructions. A separate coefficient calculation checks all 48,729 entries of
`K + (E-I)K + K(H-I) + (E-I)K(H-I)`.

All three complete D words are checked on 661 distinct Boolean input columns
in both directions. The unmodified owning checker also checks full-word E8
labels, geometry, frame legality, restoration and endpoint columns. Native
5/9/11-stage checks cover 883/1,327/1,549 formal columns per word and reject all
144 omitted-bridge controls. Nineteen local controls address preparation,
restoration, mixed terms, wrong column orientation, illegal access, stale
bounds and accounting; a cancelling helper pair is accepted and charged two
ADDs. Eight package tests cover source pins, strict/typed JSON, safe output
handling and gzip recompression. These are independent algorithms where
stated, with shared source data and retained owning tools; no separate human
review is claimed.

Both larger positive bounds are charged explicitly:

```text
64 F^3 B^2 = 2654678678257550221373682862848 < 2^104
2^18 F^5 B^4 = 6272385284143355252940491378432965655169900286360795742208 < 2^192
```

The nine-stage expression is bound to the pinned source formula and its
18-bridge relation. The baseline reproduces the source's 177-bit estimate and
192-bit charge. The candidate uses about **99.925% of that ceiling**, so the
remaining margin is small. A 192-bit result still satisfies the strict
inequality; the verifier compares integers directly. No other global invoice
allocation is inferred from this check.

## Pins, scope and attribution

Base: `91a2094f2e022930069e8cfdc810a3ea1b81cd09`.
Selected bit source: PR589, `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`.
Frozen parent: PR915, `e9daefe320a0043000bd9746664ed02c3287d056`.
Two-sided predecessor: PR733, `dfe84e09298abc5c5e0074afda59a821e10abfb4`.
The current selected assembly remains PR799. The new follow-up review batch
on this base is triage, and this package makes no claim of batch approval.

PR915's word, recipe, complete receipt, proof, notice and source manifest are
retained verbatim. We reconstruct its target recipe, check its actual word and
native bill, and do not independently re-review its historical search coverage.
No API/network access is needed for reproduction. [NOTICE.md](NOTICE.md)
retains attribution to DreamingOfClouds, eumemic, commdata2338, Mikhail R.
Gadelha, Greer Guthrie, Scott Woolsey Biggart, Sagar Thakrar and the owning
verification lineage. Ross Richardson's concurrent PR917 provides a separate
two-sided complex-side example; no code or saving is imported from it.

The remaining integration work is concrete: review the semantic interface;
emit and audit the changed whole hosted supplier; recompute its full finite
invoice and precision allocations; then rerun outer assembly against the
selected complex supplier. The unchanged frame/rank profile alone does not
establish those results. The common-label realization and analytic assumptions
remain those in the selected maintainer review. This finite construction is
not a formal proof of the full multiplication theorem or a measured runtime
speedup.

Prepared for **Gareth Davidson (@bitplane)** with substantial **OpenAI Codex
assistance** in research, implementation, proof, verification and packaging.
Apache-2.0.
